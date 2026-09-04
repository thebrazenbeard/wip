import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools import wip


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def make_workspace(root: Path, workspace_id: str = "demo-workspace") -> Path:
    workspace = root / workspace_id
    (workspace / "checkpoints").mkdir(parents=True)
    (workspace / "operations").mkdir()
    write_json(
        workspace / "WORKSPACE.json",
        {
            "schema_version": "1.0",
            "protocol_version": "1.0",
            "workspace_id": workspace_id,
            "title": "Hardening test workspace",
            "purpose": "Exercise strict WIP hardening invariants.",
            "created_at": "2026-09-04T15:00:00Z",
            "created_by": {"label": "test-worker", "route": "tests"},
            "privacy_class": "PUBLIC_SAFE",
            "storage_profile": "PUBLIC_GITHUB",
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
            "workspace_id": workspace_id,
            "generation": 1,
            "lifecycle": "ACTIVE",
            "latest_checkpoint": "cp-000001",
            "latest_operation_event": None,
            "updated_at": "2026-09-04T15:01:00Z",
        },
    )
    (workspace / "RESUME.md").write_text(
        "# Resume\n\n<!-- wip:latest_checkpoint=cp-000001 -->\n\n"
        "## Next safe action\n\nContinue hardening.\n",
        encoding="utf-8",
    )
    write_json(
        workspace / "checkpoints" / "cp-000001.json",
        {
            "schema_version": "1.0",
            "workspace_id": workspace_id,
            "checkpoint_id": "cp-000001",
            "parent_checkpoint_id": None,
            "created_at": "2026-09-04T15:01:00Z",
            "writer": {"label": "test-worker", "route": "tests"},
            "reason": "MANUAL",
            "tool_calls_since_previous": 0,
            "objective": "Exercise strict validation.",
            "observed": ["Workspace exists."],
            "inferred": [],
            "completed": ["Initial workspace created."],
            "unfinished": ["Run hardening tests."],
            "next_action": "Run hardening tests.",
            "do_not_repeat": [],
            "target_snapshots": [],
        },
    )
    return workspace


def prepared_event(workspace_id: str) -> dict:
    return {
        "schema_version": "1.0",
        "workspace_id": workspace_id,
        "operation_id": "op-000001",
        "sequence": 1,
        "state": "PREPARED",
        "created_at": "2026-09-04T15:02:00Z",
        "writer": {"label": "test-worker", "route": "tests"},
        "action_class": "file_write",
        "target": {"kind": "file", "locator": "external/result.txt"},
        "intent_summary": "Write the external result exactly once.",
        "recovery_instruction": "inspect_before_retry",
        "previous_event": None,
    }


class StrictValidationTests(unittest.TestCase):
    def test_workspace_schema_rejects_additional_property(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = make_workspace(Path(tmp))
            data = json.loads((workspace / "WORKSPACE.json").read_text(encoding="utf-8"))
            data["unexpected"] = True
            write_json(workspace / "WORKSPACE.json", data)
            errors = wip.validate_workspace(workspace)
            self.assertTrue(any("unexpected" in error or "additional" in error.lower() for error in errors), errors)

    def test_operation_workspace_id_must_match_container(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = make_workspace(Path(tmp))
            write_json(
                workspace / "operations" / "op-000001-01-prepared.json",
                prepared_event("foreign-workspace"),
            )
            errors = wip.validate_workspace(workspace)
            self.assertTrue(any("workspace_id" in error for error in errors), errors)

    def test_public_repository_rejects_private_live_workspace(self):
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            copied = Path(tmp) / "repo"
            shutil.copytree(repo_root, copied, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            workspace = make_workspace(copied / "workspaces", "private-demo")
            data = json.loads((workspace / "WORKSPACE.json").read_text(encoding="utf-8"))
            data["privacy_class"] = "PRIVATE"
            data["storage_profile"] = "PRIVATE_GITHUB"
            write_json(workspace / "WORKSPACE.json", data)
            errors = wip.validate_repository(copied)
            self.assertTrue(any("PRIVATE" in error or "storage" in error.lower() or "privacy" in error.lower() for error in errors), errors)


class MutationConcurrencyTests(unittest.TestCase):
    def test_mutation_api_exists(self):
        for name in ("start_workspace", "append_checkpoint", "append_operation_event", "StaleGenerationError"):
            self.assertTrue(hasattr(wip, name), f"tools.wip missing {name}")

    def test_stale_generation_cannot_overwrite_winner(self):
        required = ("start_workspace", "append_checkpoint", "StaleGenerationError")
        missing = [name for name in required if not hasattr(wip, name)]
        if missing:
            self.fail(f"missing mutation API: {missing}")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = wip.start_workspace(
                root,
                workspace_id="generation-demo",
                title="Generation demo",
                purpose="Prove stale writers lose.",
                writer_label="worker-a",
                writer_route="tests",
            )
            original = json.loads((workspace / "HEAD.json").read_text(encoding="utf-8"))
            self.assertEqual(original["generation"], 0)

            wip.append_checkpoint(
                workspace,
                expected_generation=0,
                writer_label="worker-b",
                writer_route="tests",
                reason="MANUAL",
                objective="Advance winner.",
                observed=["Both workers saw generation zero."],
                inferred=[],
                completed=["Worker B won the update."],
                unfinished=["Worker A must refresh."],
                next_action="Refresh HEAD.",
                do_not_repeat=[],
                target_snapshots=[],
                tool_calls_since_previous=1,
            )
            winning_head = json.loads((workspace / "HEAD.json").read_text(encoding="utf-8"))
            self.assertEqual(winning_head["generation"], 1)

            with self.assertRaises(wip.StaleGenerationError):
                wip.append_checkpoint(
                    workspace,
                    expected_generation=0,
                    writer_label="worker-a",
                    writer_route="tests",
                    reason="MANUAL",
                    objective="Attempt stale overwrite.",
                    observed=[],
                    inferred=[],
                    completed=[],
                    unfinished=["Refresh first."],
                    next_action="Refresh HEAD.",
                    do_not_repeat=[],
                    target_snapshots=[],
                    tool_calls_since_previous=1,
                )

            after = json.loads((workspace / "HEAD.json").read_text(encoding="utf-8"))
            self.assertEqual(after, winning_head)
            self.assertFalse((workspace / "checkpoints" / "cp-000002.json").exists())


if __name__ == "__main__":
    unittest.main()
