#!/usr/bin/env python3
"""Validate WIP workspaces and inspect their recovery state.

The implementation intentionally uses only the Python standard library so any
worker with a normal Python 3 runtime can validate a checkout without installing
packages.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


CHECKPOINT_RE = re.compile(r"^cp-(\d{6})$")
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
OPERATION_STATES = {"PREPARED", "ATTEMPTED", "VERIFIED", "FAILED", "AMBIGUOUS", "RECONCILED"}
UNRESOLVED_STATES = {"PREPARED", "ATTEMPTED", "AMBIGUOUS"}
TERMINAL_OPERATION_STATES = {"VERIFIED", "FAILED", "RECONCILED"}

ALLOWED_TRANSITIONS = {
    "PREPARED": {"ATTEMPTED", "FAILED", "AMBIGUOUS", "RECONCILED"},
    "ATTEMPTED": {"VERIFIED", "FAILED", "AMBIGUOUS", "RECONCILED"},
    "AMBIGUOUS": {"RECONCILED"},
    "VERIFIED": set(),
    "FAILED": set(),
    "RECONCILED": set(),
}


class JsonLoadError(ValueError):
    pass


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


def _require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def _validate_writer(errors: list[str], writer: Any, where: str) -> None:
    _require(errors, isinstance(writer, dict), f"{where}.writer must be an object")
    if not isinstance(writer, dict):
        return
    _require(errors, isinstance(writer.get("label"), str) and bool(writer.get("label")), f"{where}.writer.label is required")
    _require(errors, isinstance(writer.get("route"), str) and bool(writer.get("route")), f"{where}.writer.route is required")


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


def _read_operation_groups(workspace: Path, errors: list[str]) -> dict[str, list[tuple[int, str, Path, dict[str, Any]]]]:
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

        sequence = int(seq_text)
        state = data.get("state")
        expected_slug = state.lower() if isinstance(state, str) else ""

        _require(errors, data.get("operation_id") == operation_id, f"{path.name}: operation_id does not match filename")
        _require(errors, data.get("sequence") == sequence, f"{path.name}: sequence does not match filename")
        _require(errors, state in OPERATION_STATES, f"{path.name}: invalid operation state {state!r}")
        if state in OPERATION_STATES:
            _require(errors, state_slug == expected_slug, f"{path.name}: state slug does not match state {state}")
        _validate_writer(errors, data.get("writer"), path.name)
        _require(errors, isinstance(data.get("workspace_id"), str), f"{path.name}: workspace_id is required")
        _require(errors, isinstance(data.get("action_class"), str) and bool(data.get("action_class")), f"{path.name}: action_class is required")
        target = data.get("target")
        _require(errors, isinstance(target, dict), f"{path.name}: target must be an object")
        if isinstance(target, dict):
            _require(errors, isinstance(target.get("kind"), str) and bool(target.get("kind")), f"{path.name}: target.kind is required")
            _require(errors, isinstance(target.get("locator"), str) and bool(target.get("locator")), f"{path.name}: target.locator is required")
        _require(errors, data.get("recovery_instruction") in {"inspect_before_retry", "no_retry_required"}, f"{path.name}: invalid recovery_instruction")
        if state in {"VERIFIED", "RECONCILED"}:
            receipt = data.get("effect_receipt")
            _require(errors, isinstance(receipt, dict), f"{path.name}: {state} requires effect_receipt")
            _require(errors, isinstance(data.get("result_summary"), str) and bool(data.get("result_summary")), f"{path.name}: {state} requires result_summary")

        groups.setdefault(operation_id, []).append((sequence, state if isinstance(state, str) else "", path, data))
    return groups


def validate_workspace(workspace: Path | str) -> list[str]:
    """Return invariant violations for one workspace directory."""

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
    if errors and any(error.startswith("missing required file") for error in errors):
        return errors

    try:
        identity = _load_json(workspace / "WORKSPACE.json")
        head = _load_json(workspace / "HEAD.json")
    except JsonLoadError as exc:
        errors.append(str(exc))
        return errors

    workspace_id = identity.get("workspace_id")
    _require(errors, identity.get("schema_version") == "1.0", "WORKSPACE.schema_version must be '1.0'")
    _require(errors, identity.get("protocol_version") == "1.0", "WORKSPACE.protocol_version must be '1.0'")
    _require(errors, isinstance(workspace_id, str) and bool(re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,63}", workspace_id or "")), "WORKSPACE.workspace_id is invalid")
    _require(errors, identity.get("privacy_class") == "PUBLIC_SAFE", "WORKSPACE.privacy_class must be PUBLIC_SAFE in this public repository")
    _validate_writer(errors, identity.get("created_by"), "WORKSPACE.created_by")

    policy = identity.get("checkpoint_policy")
    _require(errors, isinstance(policy, dict), "WORKSPACE.checkpoint_policy must be an object")
    if isinstance(policy, dict):
        interval = policy.get("tool_call_interval")
        _require(errors, isinstance(interval, int) and not isinstance(interval, bool) and 1 <= interval <= 50, "checkpoint_policy.tool_call_interval must be an integer from 1 to 50")
        _require(errors, policy.get("exclude_wip_bookkeeping") is True, "checkpoint_policy.exclude_wip_bookkeeping must be true")
        _require(errors, policy.get("immediate_after_verified_write") is True, "checkpoint_policy.immediate_after_verified_write must be true")

    _require(errors, head.get("schema_version") == "1.0", "HEAD.schema_version must be '1.0'")
    _require(errors, head.get("workspace_id") == workspace_id, "HEAD.workspace_id must match WORKSPACE.workspace_id")
    generation = head.get("generation")
    _require(errors, isinstance(generation, int) and not isinstance(generation, bool) and generation >= 0, "HEAD.generation must be a non-negative integer")
    lifecycle = head.get("lifecycle")
    _require(errors, lifecycle in LIFECYCLES, f"HEAD.lifecycle is invalid: {lifecycle!r}; DONE is intentionally unsupported")

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
        checkpoints.append((stem, path, data))

    checkpoints.sort(key=lambda item: item[0])
    previous_id: str | None = None
    for index, (checkpoint_id, path, data) in enumerate(checkpoints, start=1):
        expected_id = f"cp-{index:06d}"
        _require(errors, checkpoint_id == expected_id, f"checkpoint sequence gap: expected {expected_id}, found {checkpoint_id}")
        _require(errors, data.get("checkpoint_id") == checkpoint_id, f"{path.name}: checkpoint_id does not match filename")
        _require(errors, data.get("workspace_id") == workspace_id, f"{path.name}: workspace_id does not match WORKSPACE")
        _require(errors, data.get("parent_checkpoint_id") == previous_id, f"{path.name}: parent_checkpoint_id must be {previous_id!r}")
        _require(errors, data.get("reason") in CHECKPOINT_REASONS, f"{path.name}: invalid checkpoint reason")
        tool_count = data.get("tool_calls_since_previous")
        _require(errors, isinstance(tool_count, int) and not isinstance(tool_count, bool) and tool_count >= 0, f"{path.name}: tool_calls_since_previous must be non-negative integer")
        _validate_writer(errors, data.get("writer"), path.name)
        for key in ("observed", "inferred", "completed", "unfinished", "do_not_repeat", "target_snapshots"):
            _require(errors, isinstance(data.get(key), list), f"{path.name}: {key} must be an array")
        _require(errors, isinstance(data.get("next_action"), str) and bool(data.get("next_action")), f"{path.name}: next_action is required")
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

    groups = _read_operation_groups(workspace, errors)
    latest_event_stem: str | None = None
    for operation_id, events in groups.items():
        events.sort(key=lambda item: item[0])
        previous_event_stem: str | None = None
        previous_state: str | None = None
        for expected_sequence, (sequence, state, path, data) in enumerate(events, start=1):
            _require(errors, sequence == expected_sequence, f"{operation_id}: operation sequence gap; expected {expected_sequence}, found {sequence}")
            expected_previous = previous_event_stem
            _require(errors, data.get("previous_event") == expected_previous, f"{path.name}: previous_event must be {expected_previous!r}")
            if expected_sequence == 1:
                _require(errors, state == "PREPARED", f"{operation_id}: first operation event must be PREPARED")
            elif previous_state in ALLOWED_TRANSITIONS:
                _require(errors, state in ALLOWED_TRANSITIONS[previous_state], f"{operation_id}: invalid transition {previous_state} -> {state}")
            previous_event_stem = path.stem
            previous_state = state
        if events:
            candidate = events[-1][2].stem
            if latest_event_stem is None or candidate > latest_event_stem:
                latest_event_stem = candidate

    head_event = head.get("latest_operation_event")
    if head_event is not None:
        _require(errors, any(path.stem == head_event for path in _operation_files(workspace)), f"HEAD.latest_operation_event {head_event!r} does not exist")
    if latest_event_stem is not None:
        _require(errors, head_event == latest_event_stem, f"HEAD.latest_operation_event must equal latest operation event {latest_event_stem!r}")

    return errors


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
            "unresolved_operations": [],
            "errors": errors + [str(exc)],
        }

    operation_errors: list[str] = []
    groups = _read_operation_groups(workspace, operation_errors)
    unresolved: list[str] = []
    for operation_id, events in sorted(groups.items()):
        events.sort(key=lambda item: item[0])
        if events and events[-1][1] in UNRESOLVED_STATES:
            unresolved.append(operation_id)

    return {
        "workspace_id": identity.get("workspace_id"),
        "lifecycle": head.get("lifecycle"),
        "generation": head.get("generation"),
        "latest_checkpoint": head.get("latest_checkpoint"),
        "unresolved_operations": unresolved,
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


def validate_repository(root: Path | str) -> list[str]:
    root = Path(root)
    errors: list[str] = []

    for json_root in ("schemas", "templates", "registry"):
        directory = root / json_root
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*.json")):
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"{path}: invalid/unreadable JSON: {exc}")

    registry = root / "registry" / "workspaces.json"
    if registry.is_file():
        try:
            registry_data = _load_json(registry)
            _require(errors, registry_data.get("schema_version") == "1.0", "registry/workspaces.json schema_version must be '1.0'")
            _require(errors, isinstance(registry_data.get("workspaces"), list), "registry/workspaces.json workspaces must be an array")
        except JsonLoadError as exc:
            errors.append(str(exc))

    for workspace in _workspace_dirs(root):
        for error in validate_workspace(workspace):
            errors.append(f"{workspace}: {error}")
    return errors


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="WIP V1 validator and recovery inspector")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="validate a workspace or repository root")
    validate.add_argument("path", nargs="?", default=".", type=Path)

    status = sub.add_parser("status", help="print compact recovery status for a workspace")
    status.add_argument("workspace", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "validate":
        return _cmd_validate(args.path)
    if args.command == "status":
        return _cmd_status(args.workspace)
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    sys.exit(main())
