#!/usr/bin/env python3
"""WIP V1 validation, mutation, and crash-recovery reference tooling.

The implementation intentionally uses only the Python standard library so a
normal Python 3 runtime can validate and operate a local WIP checkout without
installing packages.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECKPOINT_RE = re.compile(r"^cp-(\d{6})$")
OPERATION_ID_RE = re.compile(r"^op-(\d{6})$")
OPERATION_FILE_RE = re.compile(r"^(op-\d{6})-(\d{2})-([a-z]+)\.json$")
RESUME_RE = re.compile(r"<!--\s*wip:latest_checkpoint=(cp-\d{6}|null)\s*-->")

LIFECYCLES = {"ACTIVE", "PAUSED", "PROMOTED", "SHELVED", "SUPERSEDED", "ABANDONED"}
CHECKPOINT_REASONS = {
    "TOOL_INTERVAL",
    "VERIFIED_WRITE",
    "PHASE_COMPLETE",
    "BLOCKER",
    "SCOPE_CHANGE",
    "TARGET_MOVED",
    "PRE_RISKY_SUBTASK",
    "MANUAL",
    "RECOVERY_RECONCILIATION",
}
OPERATION_STATES = {
    "PREPARED",
    "ATTEMPTED",
    "VERIFIED",
    "FAILED",
    "AMBIGUOUS",
    "ABSENT",
    "RECONCILED",
    "CONFLICT",
}
UNRESOLVED_STATES = {"PREPARED", "ATTEMPTED", "AMBIGUOUS"}
RETRYABLE_ABSENT_STATES = {"ABSENT"}
CONFLICT_STATES = {"CONFLICT"}
TERMINAL_OPERATION_STATES = {"VERIFIED", "FAILED", "RECONCILED", "CONFLICT"}

ALLOWED_TRANSITIONS = {
    "PREPARED": {"ATTEMPTED", "VERIFIED", "FAILED", "AMBIGUOUS", "ABSENT", "RECONCILED", "CONFLICT"},
    "ATTEMPTED": {"VERIFIED", "FAILED", "AMBIGUOUS", "ABSENT", "RECONCILED", "CONFLICT"},
    "AMBIGUOUS": {"VERIFIED", "FAILED", "ABSENT", "RECONCILED", "CONFLICT"},
    "ABSENT": {"ATTEMPTED"},
    "VERIFIED": set(),
    "FAILED": set(),
    "RECONCILED": set(),
    "CONFLICT": set(),
}

CLI_OPERATION_STATES = {
    "prepare": "PREPARED",
    "attempted": "ATTEMPTED",
    "verify": "VERIFIED",
    "ambiguous": "AMBIGUOUS",
    "absent": "ABSENT",
    "reconcile": "RECONCILED",
    "conflict": "CONFLICT",
}

SCHEMA_FILES = {
    "workspace": "workspace.schema.json",
    "head": "head.schema.json",
    "checkpoint": "checkpoint.schema.json",
    "operation": "operation-event.schema.json",
    "repository_policy": "repository-policy.schema.json",
}


class JsonLoadError(ValueError):
    pass


class WipMutationError(RuntimeError):
    pass


class StaleGenerationError(WipMutationError):
    pass


def _module_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise JsonLoadError(f"cannot read {path}: {exc}") from exc
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise JsonLoadError(f"invalid JSON in {path}: {exc.msg} at line {exc.lineno} column {exc.colno}") from exc
    if not isinstance(value, dict):
        raise JsonLoadError(f"{path} must contain a JSON object")
    return value


def _write_json_exclusive(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=False)
            handle.write("\n")
    except FileExistsError as exc:
        raise WipMutationError(f"append-only record already exists: {path}") from exc


def _write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def _write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def _require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def _is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _matches_type(value: Any, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": _is_integer(value),
        "number": (isinstance(value, (int, float)) and not isinstance(value, bool)),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }.get(expected, True)


def _valid_datetime(value: str) -> bool:
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    except ValueError:
        return False
    return parsed.tzinfo is not None


def validate_json_schema(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Validate the JSON-Schema subset used by WIP V1.

    This is intentionally not a general-purpose JSON Schema implementation. It
    executes the exact Draft 2020-12 keywords used by this repository while
    keeping WIP's zero-third-party-dependency property.
    """

    errors: list[str] = []

    if "oneOf" in schema:
        matches = [not validate_json_schema(instance, option, path) for option in schema["oneOf"]]
        if sum(matches) != 1:
            errors.append(f"{path}: must match exactly one oneOf schema")
            return errors

    for subschema in schema.get("allOf", []):
        errors.extend(validate_json_schema(instance, subschema, path))

    if "if" in schema and not validate_json_schema(instance, schema["if"], path):
        if "then" in schema:
            errors.extend(validate_json_schema(instance, schema["then"], path))

    expected_type = schema.get("type")
    if isinstance(expected_type, str) and not _matches_type(instance, expected_type):
        errors.append(f"{path}: expected type {expected_type}")
        return errors

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: value must equal {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: value {instance!r} is not in allowed enum")

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{path}.{key}: required property is missing")

        properties = schema.get("properties", {})
        if isinstance(properties, dict):
            for key, value in instance.items():
                if key in properties:
                    errors.extend(validate_json_schema(value, properties[key], f"{path}.{key}"))
                elif schema.get("additionalProperties") is False:
                    errors.append(f"{path}.{key}: additional property is not allowed")

    if isinstance(instance, list) and isinstance(schema.get("items"), dict):
        for index, value in enumerate(instance):
            errors.extend(validate_json_schema(value, schema["items"], f"{path}[{index}]"))

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: string is shorter than minLength {schema['minLength']}")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(f"{path}: string is longer than maxLength {schema['maxLength']}")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errors.append(f"{path}: value does not match pattern {schema['pattern']!r}")
        if schema.get("format") == "date-time" and not _valid_datetime(instance):
            errors.append(f"{path}: value is not an offset-aware date-time")

    if _is_integer(instance) or (isinstance(instance, float) and not isinstance(instance, bool)):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: value is below minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: value is above maximum {schema['maximum']}")

    return errors


def _load_schema(name: str, schema_root: Path | None = None) -> dict[str, Any]:
    root = Path(schema_root) if schema_root is not None else _module_root()
    return _load_json(root / "schemas" / SCHEMA_FILES[name])


def _checkpoint_files(workspace: Path) -> list[Path]:
    directory = workspace / "checkpoints"
    if not directory.is_dir():
        return []
    return sorted(path for path in directory.glob("cp-*.json") if path.is_file())


def _operation_files(workspace: Path) -> list[Path]:
    directory = workspace / "operations"
    if not directory.is_dir():
        return []
    return sorted(path for path in directory.glob("op-*.json") if path.is_file())


def _read_operation_groups(
    workspace: Path,
    errors: list[str],
    *,
    workspace_id: str | None = None,
    operation_schema: dict[str, Any] | None = None,
) -> dict[str, list[tuple[int, str, Path, dict[str, Any]]]]:
    groups: dict[str, list[tuple[int, str, Path, dict[str, Any]]]] = {}
    for path in _operation_files(workspace):
        match = OPERATION_FILE_RE.match(path.name)
        if not match:
            errors.append(f"operation filename is invalid: {path.name}")
            continue
        operation_id, seq_text, state_slug = match.groups()
        try:
            data = _load_json(path)
        except JsonLoadError as exc:
            errors.append(str(exc))
            continue

        if operation_schema is not None:
            errors.extend(f"{path.name}: {error}" for error in validate_json_schema(data, operation_schema))

        sequence = int(seq_text)
        state = data.get("state")
        expected_slug = state.lower() if isinstance(state, str) else ""
        _require(errors, data.get("operation_id") == operation_id, f"{path.name}: operation_id does not match filename")
        _require(errors, data.get("sequence") == sequence, f"{path.name}: sequence does not match filename")
        _require(errors, state in OPERATION_STATES, f"{path.name}: invalid operation state {state!r}")
        if state in OPERATION_STATES:
            _require(errors, state_slug == expected_slug, f"{path.name}: state slug does not match state {state}")
        if workspace_id is not None:
            _require(errors, data.get("workspace_id") == workspace_id, f"{path.name}: workspace_id does not match WORKSPACE.workspace_id")

        groups.setdefault(operation_id, []).append((sequence, state if isinstance(state, str) else "", path, data))
    return groups


def validate_workspace(workspace: Path | str, *, schema_root: Path | None = None) -> list[str]:
    """Return schema and cross-record invariant violations for one workspace."""

    workspace = Path(workspace)
    errors: list[str] = []

    required = ["WORKSPACE.json", "HEAD.json", "RESUME.md"]
    for name in required:
        if not (workspace / name).is_file():
            errors.append(f"missing required file: {name}")
    if not (workspace / "checkpoints").is_dir():
        errors.append("missing required directory: checkpoints")
    if not (workspace / "operations").is_dir():
        errors.append("missing required directory: operations")
    if any(error.startswith("missing required file") for error in errors):
        return errors

    try:
        identity = _load_json(workspace / "WORKSPACE.json")
        head = _load_json(workspace / "HEAD.json")
        workspace_schema = _load_schema("workspace", schema_root)
        head_schema = _load_schema("head", schema_root)
        checkpoint_schema = _load_schema("checkpoint", schema_root)
        operation_schema = _load_schema("operation", schema_root)
    except JsonLoadError as exc:
        errors.append(str(exc))
        return errors

    errors.extend(f"WORKSPACE.json: {error}" for error in validate_json_schema(identity, workspace_schema))
    errors.extend(f"HEAD.json: {error}" for error in validate_json_schema(head, head_schema))

    workspace_id = identity.get("workspace_id") if isinstance(identity.get("workspace_id"), str) else None
    _require(errors, head.get("workspace_id") == workspace_id, "HEAD.workspace_id must match WORKSPACE.workspace_id")

    checkpoints: list[tuple[str, Path, dict[str, Any]]] = []
    for path in _checkpoint_files(workspace):
        stem = path.stem
        if not CHECKPOINT_RE.match(stem):
            errors.append(f"checkpoint filename is invalid: {path.name}")
            continue
        try:
            data = _load_json(path)
        except JsonLoadError as exc:
            errors.append(str(exc))
            continue
        errors.extend(f"{path.name}: {error}" for error in validate_json_schema(data, checkpoint_schema))
        checkpoints.append((stem, path, data))

    checkpoints.sort(key=lambda item: item[0])
    previous_id: str | None = None
    for index, (checkpoint_id, path, data) in enumerate(checkpoints, start=1):
        expected_id = f"cp-{index:06d}"
        _require(errors, checkpoint_id == expected_id, f"checkpoint sequence gap: expected {expected_id}, found {checkpoint_id}")
        _require(errors, data.get("checkpoint_id") == checkpoint_id, f"{path.name}: checkpoint_id does not match filename")
        _require(errors, data.get("workspace_id") == workspace_id, f"{path.name}: workspace_id does not match WORKSPACE.workspace_id")
        _require(errors, data.get("parent_checkpoint_id") == previous_id, f"{path.name}: parent_checkpoint_id must be {previous_id!r}")
        previous_id = checkpoint_id

    latest_checkpoint = checkpoints[-1][0] if checkpoints else None
    _require(errors, head.get("latest_checkpoint") == latest_checkpoint, f"HEAD.latest_checkpoint must equal latest checkpoint {latest_checkpoint!r}")

    try:
        resume = (workspace / "RESUME.md").read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"cannot read RESUME.md: {exc}")
        resume = ""
    marker = RESUME_RE.search(resume)
    _require(errors, marker is not None, "RESUME.md must contain <!-- wip:latest_checkpoint=... --> marker")
    if marker:
        resume_checkpoint = None if marker.group(1) == "null" else marker.group(1)
        _require(errors, resume_checkpoint == head.get("latest_checkpoint"), f"RESUME latest checkpoint {resume_checkpoint!r} does not match HEAD.latest_checkpoint {head.get('latest_checkpoint')!r}")

    groups = _read_operation_groups(
        workspace,
        errors,
        workspace_id=workspace_id,
        operation_schema=operation_schema,
    )
    latest_event_stem: str | None = None
    for operation_id, events in groups.items():
        events.sort(key=lambda item: item[0])
        previous_event_stem: str | None = None
        previous_state: str | None = None
        for expected_sequence, (sequence, state, path, data) in enumerate(events, start=1):
            _require(errors, sequence == expected_sequence, f"{operation_id}: operation sequence gap; expected {expected_sequence}, found {sequence}")
            _require(errors, data.get("previous_event") == previous_event_stem, f"{path.name}: previous_event must be {previous_event_stem!r}")
            if expected_sequence == 1:
                _require(errors, state == "PREPARED", f"{operation_id}: first operation event must be PREPARED")
            elif previous_state is not None:
                _require(errors, state in ALLOWED_TRANSITIONS.get(previous_state, set()), f"{operation_id}: invalid transition {previous_state} -> {state}")
            previous_event_stem = path.stem
            previous_state = state
        if events:
            candidate = events[-1][2].stem
            if latest_event_stem is None or candidate > latest_event_stem:
                latest_event_stem = candidate

    head_event = head.get("latest_operation_event")
    if head_event is not None:
        _require(errors, any(path.stem == head_event for path in _operation_files(workspace)), f"HEAD.latest_operation_event {head_event!r} does not exist")
    _require(errors, head_event == latest_event_stem, f"HEAD.latest_operation_event must equal latest operation event {latest_event_stem!r}")

    return errors


def _latest_operation_states(workspace: Path) -> dict[str, str]:
    operation_errors: list[str] = []
    groups = _read_operation_groups(workspace, operation_errors)
    states: dict[str, str] = {}
    for operation_id, events in sorted(groups.items()):
        events.sort(key=lambda item: item[0])
        if events:
            states[operation_id] = events[-1][1]
    return states


def inspect_workspace(workspace: Path | str) -> dict[str, Any]:
    """Return a compact recovery/status projection for one workspace."""

    workspace = Path(workspace)
    errors = validate_workspace(workspace)
    try:
        identity = _load_json(workspace / "WORKSPACE.json")
        head = _load_json(workspace / "HEAD.json")
    except JsonLoadError as exc:
        return {
            "workspace_id": None,
            "lifecycle": None,
            "generation": None,
            "latest_checkpoint": None,
            "latest_operation_event": None,
            "unresolved_operations": [],
            "retryable_absent_operations": [],
            "conflict_operations": [],
            "completed_operations": [],
            "errors": errors + [str(exc)],
        }

    states = _latest_operation_states(workspace)
    unresolved = sorted(operation_id for operation_id, state in states.items() if state in UNRESOLVED_STATES)
    retryable_absent = sorted(operation_id for operation_id, state in states.items() if state in RETRYABLE_ABSENT_STATES)
    conflicts = sorted(operation_id for operation_id, state in states.items() if state in CONFLICT_STATES)
    completed = sorted(operation_id for operation_id, state in states.items() if state in TERMINAL_OPERATION_STATES and state not in CONFLICT_STATES)

    return {
        "workspace_id": identity.get("workspace_id"),
        "lifecycle": head.get("lifecycle"),
        "generation": head.get("generation"),
        "latest_checkpoint": head.get("latest_checkpoint"),
        "latest_operation_event": head.get("latest_operation_event"),
        "unresolved_operations": unresolved,
        "retryable_absent_operations": retryable_absent,
        "conflict_operations": conflicts,
        "completed_operations": completed,
        "errors": errors,
    }


def _workspace_dirs(root: Path) -> list[Path]:
    if (root / "WORKSPACE.json").is_file():
        return [root]
    found: list[Path] = []
    for parent_name in ("workspaces", "examples"):
        parent = root / parent_name
        if not parent.is_dir():
            continue
        for candidate in sorted(parent.iterdir()):
            if candidate.is_dir() and (candidate / "WORKSPACE.json").is_file():
                found.append(candidate)
    return found


def _validate_repository_policy(root: Path, errors: list[str]) -> dict[str, Any] | None:
    policy_path = root / "storage" / "REPOSITORY_POLICY.json"
    if not policy_path.is_file():
        errors.append("missing required repository storage policy: storage/REPOSITORY_POLICY.json")
        return None
    try:
        policy = _load_json(policy_path)
        schema = _load_schema("repository_policy", root)
    except JsonLoadError as exc:
        errors.append(str(exc))
        return None
    errors.extend(f"storage/REPOSITORY_POLICY.json: {error}" for error in validate_json_schema(policy, schema))
    return policy


def validate_repository(root: Path | str) -> list[str]:
    root = Path(root)
    errors: list[str] = []

    for json_root in ("schemas", "templates", "registry", "storage"):
        directory = root / json_root
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*.json")):
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"{path}: invalid/unreadable JSON: {exc}")

    policy = _validate_repository_policy(root, errors)

    registry = root / "registry" / "workspaces.json"
    registry_entries: list[Any] = []
    if registry.is_file():
        try:
            registry_data = _load_json(registry)
            _require(errors, registry_data.get("schema_version") == "1.0", "registry/workspaces.json schema_version must be '1.0'")
            _require(errors, isinstance(registry_data.get("workspaces"), list), "registry/workspaces.json workspaces must be an array")
            if isinstance(registry_data.get("workspaces"), list):
                registry_entries = registry_data["workspaces"]
        except JsonLoadError as exc:
            errors.append(str(exc))

    allowed_privacy: set[str] = set()
    allowed_storage: set[str] = set()
    if isinstance(policy, dict):
        live_policy = policy.get("live_workspace_policy")
        if isinstance(live_policy, dict):
            allowed_privacy = set(live_policy.get("allowed_privacy_classes", []))
            allowed_storage = set(live_policy.get("allowed_storage_profiles", []))

    workspace_map: dict[str, Path] = {}
    for workspace in _workspace_dirs(root):
        for error in validate_workspace(workspace, schema_root=root):
            errors.append(f"{workspace}: {error}")
        try:
            identity = _load_json(workspace / "WORKSPACE.json")
        except JsonLoadError:
            continue
        workspace_id = identity.get("workspace_id")
        if isinstance(workspace_id, str):
            workspace_map[workspace_id] = workspace
        if allowed_privacy and identity.get("privacy_class") not in allowed_privacy:
            errors.append(f"{workspace}: privacy_class {identity.get('privacy_class')!r} is not allowed by repository storage policy")
        if allowed_storage and identity.get("storage_profile") not in allowed_storage:
            errors.append(f"{workspace}: storage_profile {identity.get('storage_profile')!r} is not allowed by repository storage policy")

    for index, entry in enumerate(registry_entries):
        if not isinstance(entry, dict):
            errors.append(f"registry/workspaces.json workspaces[{index}] must be an object")
            continue
        workspace_id = entry.get("workspace_id")
        path_value = entry.get("path")
        if isinstance(workspace_id, str) and isinstance(path_value, str) and workspace_id in workspace_map:
            expected = workspace_map[workspace_id]
            try:
                actual = (root / path_value).resolve()
                if actual != expected.resolve():
                    errors.append(f"registry entry {workspace_id!r} path does not match discovered workspace")
            except OSError:
                errors.append(f"registry entry {workspace_id!r} path cannot be resolved")

    return errors


def _mutation_guard(workspace: Path, expected_generation: int) -> dict[str, Any]:
    head = _load_json(workspace / "HEAD.json")
    actual = head.get("generation")
    if actual != expected_generation:
        raise StaleGenerationError(f"stale HEAD generation: expected {expected_generation}, current {actual}")
    errors = validate_workspace(workspace)
    if errors:
        raise WipMutationError("workspace is not mutation-ready: " + "; ".join(errors))
    return head


def _next_operation_id(workspace: Path) -> str:
    highest = 0
    for path in _operation_files(workspace):
        match = OPERATION_FILE_RE.match(path.name)
        if match:
            op_match = OPERATION_ID_RE.match(match.group(1))
            if op_match:
                highest = max(highest, int(op_match.group(1)))
    return f"op-{highest + 1:06d}"


def render_resume(workspace: Path | str) -> str:
    workspace = Path(workspace)
    identity = _load_json(workspace / "WORKSPACE.json")
    head = _load_json(workspace / "HEAD.json")
    checkpoint_id = head.get("latest_checkpoint")
    checkpoint: dict[str, Any] | None = None
    if isinstance(checkpoint_id, str):
        path = workspace / "checkpoints" / f"{checkpoint_id}.json"
        if path.is_file():
            checkpoint = _load_json(path)

    states = _latest_operation_states(workspace)
    unresolved = [operation_id for operation_id, state in states.items() if state in UNRESOLVED_STATES]
    retryable = [operation_id for operation_id, state in states.items() if state == "ABSENT"]
    conflicts = [operation_id for operation_id, state in states.items() if state == "CONFLICT"]

    marker = checkpoint_id if checkpoint_id is not None else "null"
    objective = checkpoint.get("objective") if checkpoint else identity.get("purpose", "No checkpoint yet.")
    unfinished = checkpoint.get("unfinished", []) if checkpoint else ["Create the first checkpoint."]
    do_not_repeat = checkpoint.get("do_not_repeat", []) if checkpoint else []
    next_action = checkpoint.get("next_action") if checkpoint else "Create the first checkpoint before sustained work."

    def bullets(items: list[Any], empty: str) -> str:
        if not items:
            return f"- {empty}"
        return "\n".join(f"- {item}" for item in items)

    operation_lines: list[str] = []
    operation_lines.extend(f"- {item}: unresolved; inspect before retry" for item in sorted(unresolved))
    operation_lines.extend(f"- {item}: effect confirmed absent; refresh authority/currentness before retry" for item in sorted(retryable))
    operation_lines.extend(f"- {item}: conflict; stop and reconcile divergent state" for item in sorted(conflicts))

    return (
        "# Resume\n\n"
        f"<!-- wip:latest_checkpoint={marker} -->\n\n"
        f"Workspace: `{identity.get('workspace_id')}`  \n"
        f"Lifecycle: `{head.get('lifecycle')}`  \n"
        f"Generation: `{head.get('generation')}`\n\n"
        "## Objective\n\n"
        f"{objective}\n\n"
        "## Unfinished\n\n"
        f"{bullets(unfinished, 'Nothing recorded.')}\n\n"
        "## Do not repeat\n\n"
        f"{bullets(do_not_repeat, 'No do-not-repeat warning recorded.')}\n\n"
        "## Operation recovery\n\n"
        f"{bullets(operation_lines, 'No unresolved, absent, or conflicted operations.')}\n\n"
        "## Next safe action\n\n"
        f"{next_action}\n"
    )


def repair_projections(workspace: Path | str, *, expected_generation: int) -> dict[str, Any]:
    """Rebuild HEAD/RESUME from append-only history after an interrupted WIP write.

    The candidate projections are first validated in a shadow workspace. Only
    valid append-only history can advance the live projections.
    """

    workspace = Path(workspace)
    head = _load_json(workspace / "HEAD.json")
    actual_generation = head.get("generation")
    if actual_generation != expected_generation:
        raise StaleGenerationError(
            f"stale HEAD generation: expected {expected_generation}, current {actual_generation}"
        )

    checkpoints = _checkpoint_files(workspace)
    latest_checkpoint = checkpoints[-1].stem if checkpoints else None
    operation_files = _operation_files(workspace)
    latest_operation_event = operation_files[-1].stem if operation_files else None

    candidate_head = dict(head)
    candidate_head["generation"] = expected_generation + 1
    candidate_head["latest_checkpoint"] = latest_checkpoint
    candidate_head["latest_operation_event"] = latest_operation_event
    candidate_head["updated_at"] = _utcnow()

    with tempfile.TemporaryDirectory() as tmp:
        shadow = Path(tmp) / "workspace"
        shadow.mkdir()
        shutil.copy2(workspace / "WORKSPACE.json", shadow / "WORKSPACE.json")
        for directory_name in ("checkpoints", "operations"):
            source = workspace / directory_name
            target = shadow / directory_name
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                target.mkdir()
        _write_json_atomic(shadow / "HEAD.json", candidate_head)
        candidate_resume = render_resume(shadow)
        _write_text_atomic(shadow / "RESUME.md", candidate_resume)
        errors = validate_workspace(shadow)
        if errors:
            raise WipMutationError(
                "append-only history cannot produce valid projections: " + "; ".join(errors)
            )

    _write_json_atomic(workspace / "HEAD.json", candidate_head)
    _write_text_atomic(workspace / "RESUME.md", candidate_resume)
    errors = validate_workspace(workspace)
    if errors:
        raise WipMutationError("projection repair left invalid workspace: " + "; ".join(errors))
    return candidate_head


def start_workspace(
    parent: Path | str,
    *,
    workspace_id: str,
    title: str,
    purpose: str,
    writer_label: str,
    writer_route: str,
    privacy_class: str = "PUBLIC_SAFE",
    storage_profile: str = "PUBLIC_GITHUB",
    destination: dict[str, Any] | None = None,
    tool_call_interval: int = 5,
) -> Path:
    parent = Path(parent)
    workspace = parent / workspace_id
    if workspace.exists():
        raise WipMutationError(f"workspace path already exists: {workspace}")
    (workspace / "checkpoints").mkdir(parents=True)
    (workspace / "operations").mkdir()
    for optional in ("decisions", "handoffs", "artifacts", "exit"):
        (workspace / optional).mkdir()

    identity = {
        "schema_version": "1.0",
        "protocol_version": "1.0",
        "workspace_id": workspace_id,
        "title": title,
        "purpose": purpose,
        "created_at": _utcnow(),
        "created_by": {"label": writer_label, "route": writer_route},
        "privacy_class": privacy_class,
        "storage_profile": storage_profile,
        "checkpoint_policy": {
            "tool_call_interval": tool_call_interval,
            "exclude_wip_bookkeeping": True,
            "immediate_after_verified_write": True,
        },
        "destination": destination or {"type": "UNKNOWN"},
    }
    head = {
        "schema_version": "1.0",
        "workspace_id": workspace_id,
        "generation": 0,
        "lifecycle": "ACTIVE",
        "latest_checkpoint": None,
        "latest_operation_event": None,
        "updated_at": _utcnow(),
    }
    _write_json_exclusive(workspace / "WORKSPACE.json", identity)
    _write_json_exclusive(workspace / "HEAD.json", head)
    _write_text_atomic(workspace / "RESUME.md", render_resume(workspace))
    errors = validate_workspace(workspace)
    if errors:
        raise WipMutationError("created workspace failed validation: " + "; ".join(errors))
    return workspace


def append_checkpoint(
    workspace: Path | str,
    *,
    expected_generation: int,
    writer_label: str,
    writer_route: str,
    reason: str,
    objective: str,
    observed: list[str],
    inferred: list[str],
    completed: list[str],
    unfinished: list[str],
    next_action: str,
    do_not_repeat: list[str],
    target_snapshots: list[dict[str, Any]],
    tool_calls_since_previous: int,
) -> dict[str, Any]:
    workspace = Path(workspace)
    head = _mutation_guard(workspace, expected_generation)
    checkpoint_files = _checkpoint_files(workspace)
    next_number = len(checkpoint_files) + 1
    checkpoint_id = f"cp-{next_number:06d}"
    parent_checkpoint_id = head.get("latest_checkpoint")
    identity = _load_json(workspace / "WORKSPACE.json")
    record = {
        "schema_version": "1.0",
        "workspace_id": identity["workspace_id"],
        "checkpoint_id": checkpoint_id,
        "parent_checkpoint_id": parent_checkpoint_id,
        "created_at": _utcnow(),
        "writer": {"label": writer_label, "route": writer_route},
        "reason": reason,
        "tool_calls_since_previous": tool_calls_since_previous,
        "objective": objective,
        "observed": observed,
        "inferred": inferred,
        "completed": completed,
        "unfinished": unfinished,
        "next_action": next_action,
        "do_not_repeat": do_not_repeat,
        "target_snapshots": target_snapshots,
    }
    schema_errors = validate_json_schema(record, _load_schema("checkpoint"))
    if schema_errors:
        raise WipMutationError("checkpoint record is invalid: " + "; ".join(schema_errors))

    _write_json_exclusive(workspace / "checkpoints" / f"{checkpoint_id}.json", record)
    head["generation"] = expected_generation + 1
    head["latest_checkpoint"] = checkpoint_id
    head["updated_at"] = _utcnow()
    _write_json_atomic(workspace / "HEAD.json", head)
    _write_text_atomic(workspace / "RESUME.md", render_resume(workspace))
    errors = validate_workspace(workspace)
    if errors:
        raise WipMutationError("checkpoint mutation left invalid workspace: " + "; ".join(errors))
    return record


def append_operation_event(
    workspace: Path | str,
    *,
    expected_generation: int,
    operation_id: str | None,
    state: str,
    writer_label: str,
    writer_route: str,
    action_class: str,
    target: dict[str, Any],
    intent_summary: str,
    recovery_instruction: str,
    result_summary: str | None = None,
    effect_receipt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    workspace = Path(workspace)
    head = _mutation_guard(workspace, expected_generation)
    state = state.upper()
    if state not in OPERATION_STATES:
        raise WipMutationError(f"invalid operation state: {state}")

    operation_id = operation_id or _next_operation_id(workspace)
    if OPERATION_ID_RE.fullmatch(operation_id) is None:
        raise WipMutationError(f"invalid operation id: {operation_id}")

    group_errors: list[str] = []
    groups = _read_operation_groups(workspace, group_errors)
    if group_errors:
        raise WipMutationError("cannot append operation event: " + "; ".join(group_errors))
    existing = sorted(groups.get(operation_id, []), key=lambda item: item[0])

    if not existing:
        if state != "PREPARED":
            raise WipMutationError("first event for an operation must be PREPARED")
        sequence = 1
        previous_event = None
    else:
        previous_state = existing[-1][1]
        if state not in ALLOWED_TRANSITIONS.get(previous_state, set()):
            raise WipMutationError(f"invalid operation transition {previous_state} -> {state}")
        sequence = existing[-1][0] + 1
        previous_event = existing[-1][2].stem

    identity = _load_json(workspace / "WORKSPACE.json")
    record: dict[str, Any] = {
        "schema_version": "1.0",
        "workspace_id": identity["workspace_id"],
        "operation_id": operation_id,
        "sequence": sequence,
        "state": state,
        "created_at": _utcnow(),
        "writer": {"label": writer_label, "route": writer_route},
        "action_class": action_class,
        "target": target,
        "intent_summary": intent_summary,
        "recovery_instruction": recovery_instruction,
        "previous_event": previous_event,
    }
    if result_summary is not None:
        record["result_summary"] = result_summary
    if effect_receipt is not None:
        record["effect_receipt"] = effect_receipt

    schema_errors = validate_json_schema(record, _load_schema("operation"))
    if schema_errors:
        raise WipMutationError("operation event is invalid: " + "; ".join(schema_errors))

    event_stem = f"{operation_id}-{sequence:02d}-{state.lower()}"
    _write_json_exclusive(workspace / "operations" / f"{event_stem}.json", record)
    head["generation"] = expected_generation + 1
    head["latest_operation_event"] = event_stem
    head["updated_at"] = _utcnow()
    _write_json_atomic(workspace / "HEAD.json", head)
    _write_text_atomic(workspace / "RESUME.md", render_resume(workspace))
    errors = validate_workspace(workspace)
    if errors:
        raise WipMutationError("operation mutation left invalid workspace: " + "; ".join(errors))
    return record


def _cmd_validate(path: Path) -> int:
    errors = validate_workspace(path) if (path / "WORKSPACE.json").is_file() else validate_repository(path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAIL: {len(errors)} validation error(s)")
        return 1
    print(f"OK: {path}")
    return 0


def _cmd_status(path: Path) -> int:
    print(json.dumps(inspect_workspace(path), indent=2, sort_keys=True))
    return 0


def _cmd_start(args: argparse.Namespace) -> int:
    workspace = start_workspace(
        args.parent,
        workspace_id=args.workspace_id,
        title=args.title,
        purpose=args.purpose,
        writer_label=args.writer_label,
        writer_route=args.writer_route,
        privacy_class=args.privacy_class,
        storage_profile=args.storage_profile,
    )
    print(workspace)
    return 0


def _cmd_checkpoint(args: argparse.Namespace) -> int:
    record = append_checkpoint(
        args.workspace,
        expected_generation=args.expected_generation,
        writer_label=args.writer_label,
        writer_route=args.writer_route,
        reason=args.reason,
        objective=args.objective,
        observed=args.observed or [],
        inferred=args.inferred or [],
        completed=args.completed or [],
        unfinished=args.unfinished or [],
        next_action=args.next_action,
        do_not_repeat=args.do_not_repeat or [],
        target_snapshots=[],
        tool_calls_since_previous=args.tool_calls_since_previous,
    )
    print(record["checkpoint_id"])
    return 0


def _cmd_operation(args: argparse.Namespace) -> int:
    target: dict[str, Any] = {"kind": args.target_kind, "locator": args.target_locator}
    if args.expected_precondition:
        target["expected_precondition"] = args.expected_precondition
    receipt = None
    if args.receipt_kind or args.receipt_value or args.receipt_readback:
        if not args.receipt_kind or not args.receipt_value:
            raise WipMutationError("receipt-kind and receipt-value must be supplied together")
        receipt = {"kind": args.receipt_kind, "value": args.receipt_value}
        if args.receipt_readback:
            receipt["readback"] = args.receipt_readback

    record = append_operation_event(
        args.workspace,
        expected_generation=args.expected_generation,
        operation_id=args.operation_id,
        state=CLI_OPERATION_STATES[args.command],
        writer_label=args.writer_label,
        writer_route=args.writer_route,
        action_class=args.action_class,
        target=target,
        intent_summary=args.intent_summary,
        recovery_instruction=args.recovery_instruction,
        result_summary=args.result_summary,
        effect_receipt=receipt,
    )
    print(f"{record['operation_id']}-{record['sequence']:02d}-{record['state'].lower()}")
    return 0


def _add_writer_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--writer-label", required=True)
    parser.add_argument("--writer-route", required=True)


def _add_operation_args(parser: argparse.ArgumentParser, *, operation_id_required: bool) -> None:
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--expected-generation", required=True, type=int)
    parser.add_argument("--operation-id", required=operation_id_required)
    _add_writer_args(parser)
    parser.add_argument("--action-class", required=True)
    parser.add_argument("--target-kind", required=True)
    parser.add_argument("--target-locator", required=True)
    parser.add_argument("--expected-precondition")
    parser.add_argument("--intent-summary", required=True)
    parser.add_argument("--recovery-instruction", choices=["inspect_before_retry", "no_retry_required"], default="inspect_before_retry")
    parser.add_argument("--result-summary")
    parser.add_argument("--receipt-kind")
    parser.add_argument("--receipt-value")
    parser.add_argument("--receipt-readback")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="WIP V1 validator, mutation tool, and recovery inspector")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="validate a workspace or repository root")
    validate.add_argument("path", nargs="?", default=".", type=Path)

    status = sub.add_parser("status", help="print compact recovery status for a workspace")
    status.add_argument("workspace", type=Path)

    resume = sub.add_parser("resume", help="render the current recovery card")
    resume.add_argument("workspace", type=Path)

    repair = sub.add_parser("repair", help="rebuild HEAD/RESUME from validated append-only history")
    repair.add_argument("workspace", type=Path)
    repair.add_argument("--expected-generation", required=True, type=int)

    start = sub.add_parser("start", help="create a new local WIP workspace")
    start.add_argument("parent", type=Path)
    start.add_argument("--workspace-id", required=True)
    start.add_argument("--title", required=True)
    start.add_argument("--purpose", required=True)
    _add_writer_args(start)
    start.add_argument("--privacy-class", choices=["PUBLIC_SAFE", "PRIVATE"], default="PUBLIC_SAFE")
    start.add_argument("--storage-profile", choices=["PUBLIC_GITHUB", "PRIVATE_GITHUB", "PRIVATE_PROVIDER"], default="PUBLIC_GITHUB")

    checkpoint = sub.add_parser("checkpoint", help="append a checkpoint and advance HEAD")
    checkpoint.add_argument("workspace", type=Path)
    checkpoint.add_argument("--expected-generation", required=True, type=int)
    _add_writer_args(checkpoint)
    checkpoint.add_argument("--reason", choices=sorted(CHECKPOINT_REASONS), default="MANUAL")
    checkpoint.add_argument("--objective", required=True)
    checkpoint.add_argument("--next-action", required=True)
    checkpoint.add_argument("--tool-calls-since-previous", type=int, default=0)
    for flag in ("observed", "inferred", "completed", "unfinished", "do-not-repeat"):
        checkpoint.add_argument(f"--{flag}", action="append")

    for command in ("prepare", "attempted", "verify", "ambiguous", "absent", "reconcile", "conflict"):
        operation = sub.add_parser(command, help=f"append a {CLI_OPERATION_STATES[command]} operation event")
        _add_operation_args(operation, operation_id_required=(command != "prepare"))

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "validate":
            return _cmd_validate(args.path)
        if args.command == "status":
            return _cmd_status(args.workspace)
        if args.command == "resume":
            print(render_resume(args.workspace), end="")
            return 0
        if args.command == "repair":
            print(json.dumps(repair_projections(args.workspace, expected_generation=args.expected_generation), indent=2, sort_keys=True))
            return 0
        if args.command == "start":
            return _cmd_start(args)
        if args.command == "checkpoint":
            return _cmd_checkpoint(args)
        if args.command in CLI_OPERATION_STATES:
            return _cmd_operation(args)
    except (JsonLoadError, WipMutationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    sys.exit(main())
