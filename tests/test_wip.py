import json
import tempfile
import unittest
from pathlib import Path

from tools.wip import inspect_workspace, validate_workspace


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def make_workspace(root: Path, *, lifecycle: str = "ACTIVE", head_checkpoint: str = "cp-000001", resume_checkpoint: str = "cp-000001") -> Path:
    workspace = root / "demo-workspace"
    (workspace / "checkpoints").mkdir(parents=True)
    (workspace / "operations").mkdir()

    write_json(
        workspace / "WORKSPACE.json",
        {
            "schema_version": "1.0",
            "protocol_version": "1.0",
            "workspace_id": "demo-workspace",
            "title": "Demo workspace",
            "purpose": "Exercise WIP recovery validation.",
            "created_at": "2026-09-04T14:00:00Z",
            "created_by": {"label": "test-worker", "route": "tests"},
            "privacy_class": "PUBLIC_SAFE",
            "checkpoint_policy": {
                "tool_call_interval": 5,
                "exclude_wip_bookkeeping": True,
                "immediate_after_verified_write": True,
            },
            "destination": {"type": "UNKNOWN"},
        },
    )

    write_json(
        workspace / "HEAD.json",
        {
            "schema_version": "1.0",
            "workspace_id": "demo-workspace",
            "generation": 1,
            "lifecycle": lifecycle,
            "latest_checkpoint": head_checkpoint,
            "latest_operation_event": None,
            "updated_at": "2026-09-04T14:05:00Z",
        },
    )

    (workspace / "RESUME.md").write_text(
        "# Resume\n\n"
        f"<!-- wip:latest_checkpoint={resume_checkpoint} -->\n\n"
        "## Next safe action\n\nContinue testing.\n",
        encoding="utf-8",
    )

    write_json(
        workspace / "checkpoints" / "cp-000001.json",
        {
            "schema_version": "1.0",
            "workspace_id": "demo-workspace",
            "checkpoint_id": "cp-000001",
            "parent_checkpoint_id": None,
            "created_at": "2026-09-04T14:05:00Z",
            "writer": {"label": "test-worker", "route": "tests"},
            "reason": "MANUAL",
            "tool_calls_since_previous": 0,
            "objective": "Exercise validation.",
            "observed": ["Workspace exists."],
            "inferred": [],
            "completed": ["Initial records written."],
            "unfinished": ["Run validation."],
            "next_action": "Run validation.",
            "do_not_repeat": ["Do not recreate cp-000001."],
            "target_snapshots": [],
        },
    )
    return workspace


def operation_event(workspace_id: str, operation_id: str, sequence: int, state: str, previous_event=None) -> dict:
    data = {
        "schema_version": "1.0",
        "workspace_id": workspace_id,
        "operation_id": operation_id,
        "sequence": sequence,
        "state": state,
        "created_at": "2026-09-04T14:06:00Z",
        "writer": {"label": "test-worker", "route": "tests"},
        "action_class": "github_write",
        "target": {"kind": "github-file", "locator": "owner/repo:path"},
        "intent_summary": "Create a file exactly once.",
        "recovery_instruction": "inspect_before_retry",
        "previous_event": previous_event,
    }
    if state in {"VERIFIED", "RECONCILED"}:
        data["result_summary"] = "Effect found on readback."
        data["effect_receipt"] = {"kind": "commit", "value": "abc123", "readback": "file exists"}
    return data


class WipValidationTests(unittest.TestCase):
    def test_valid_workspace_has_no_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = make_workspace(Path(tmp))
            self.assertEqual(validate_workspace(workspace), [])

    def test_head_must_point_to_existing_latest_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = make_workspace(Path(tmp), head_checkpoint="cp-000002")
            errors = validate_workspace(workspace)
            self.assertTrue(any("latest_checkpoint" in error for error in errors), errors)

    def test_resume_marker_must_match_head_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = make_workspace(Path(tmp), resume_checkpoint="cp-000002")
            errors = validate_workspace(workspace)
            self.assertTrue(any("RESUME" in error for error in errors), errors)

    def test_done_lifecycle_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = make_workspace(Path(tmp), lifecycle="DONE")
            errors = validate_workspace(workspace)
            self.assertTrue(any("lifecycle" in error for error in errors), errors)

    def test_prepared_operation_is_reported_unresolved(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = make_workspace(Path(tmp))
            write_json(
                workspace / "operations" / "op-000001-01-prepared.json",
                operation_event("demo-workspace", "op-000001", 1, "PREPARED"),
            )
            result = inspect_workspace(workspace)
            self.assertIn("op-000001", result["unresolved_operations"])

    def test_verified_operation_is_not_unresolved(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = make_workspace(Path(tmp))
            write_json(
                workspace / "operations" / "op-000001-01-prepared.json",
                operation_event("demo-workspace", "op-000001", 1, "PREPARED"),
            )
            write_json(
                workspace / "operations" / "op-000001-02-attempted.json",
                operation_event("demo-workspace", "op-000001", 2, "ATTEMPTED", "op-000001-01-prepared"),
            )
            write_json(
                workspace / "operations" / "op-000001-03-verified.json",
                operation_event("demo-workspace", "op-000001", 3, "VERIFIED", "op-000001-02-attempted"),
            )
            result = inspect_workspace(workspace)
            self.assertNotIn("op-000001", result["unresolved_operations"])

    def test_operation_sequence_gap_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = make_workspace(Path(tmp))
            write_json(
                workspace / "operations" / "op-000001-01-prepared.json",
                operation_event("demo-workspace", "op-000001", 1, "PREPARED"),
            )
            write_json(
                workspace / "operations" / "op-000001-03-verified.json",
                operation_event("demo-workspace", "op-000001", 3, "VERIFIED", "op-000001-01-prepared"),
            )
            errors = validate_workspace(workspace)
            self.assertTrue(any("sequence" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
