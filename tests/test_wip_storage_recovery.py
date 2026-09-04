import json
import tempfile
import unittest
from pathlib import Path

from tools import wip


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


class WipStorageRecoveryTests(unittest.TestCase):
    def test_orphan_checkpoint_can_repair_head_and_resume(self):
        self.assertTrue(hasattr(wip, "repair_projections"), "tools.wip missing repair_projections")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = wip.start_workspace(
                root,
                workspace_id="storage-crash",
                title="Storage crash recovery",
                purpose="Recover when append-only checkpoint landed before projection update.",
                writer_label="worker-a",
                writer_route="tests/storage-recovery",
            )

            # Simulate the persistence primitive succeeding at the append-only
            # step and the runtime dying before HEAD/RESUME can be replaced.
            write_json(
                workspace / "checkpoints" / "cp-000001.json",
                {
                    "schema_version": "1.0",
                    "workspace_id": "storage-crash",
                    "checkpoint_id": "cp-000001",
                    "parent_checkpoint_id": None,
                    "created_at": "2026-09-04T16:45:00Z",
                    "writer": {"label": "worker-a", "route": "tests/storage-recovery"},
                    "reason": "TOOL_INTERVAL",
                    "tool_calls_since_previous": 5,
                    "objective": "Preserve the frontier before the crash.",
                    "observed": ["Five substantive calls completed."],
                    "inferred": [],
                    "completed": ["Checkpoint body reached durable storage."],
                    "unfinished": ["Repair projections and continue."],
                    "next_action": "Repair HEAD and RESUME from append-only history.",
                    "do_not_repeat": ["Do not recreate cp-000001."],
                    "target_snapshots": [],
                },
            )

            before = wip.validate_workspace(workspace)
            self.assertTrue(any("latest_checkpoint" in error for error in before), before)

            repaired = wip.repair_projections(workspace, expected_generation=0)
            self.assertEqual(repaired["generation"], 1)
            self.assertEqual(repaired["latest_checkpoint"], "cp-000001")
            self.assertIsNone(repaired["latest_operation_event"])
            self.assertEqual(wip.validate_workspace(workspace), [])

            resume = (workspace / "RESUME.md").read_text(encoding="utf-8")
            self.assertIn("<!-- wip:latest_checkpoint=cp-000001 -->", resume)
            self.assertIn("Repair HEAD and RESUME from append-only history.", resume)

    def test_projection_repair_rejects_stale_generation(self):
        if not hasattr(wip, "repair_projections"):
            self.fail("tools.wip missing repair_projections")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = wip.start_workspace(
                root,
                workspace_id="repair-stale",
                title="Repair stale guard",
                purpose="Prove projection repair obeys optimistic concurrency.",
                writer_label="worker-a",
                writer_route="tests/storage-recovery",
            )
            with self.assertRaises(wip.StaleGenerationError):
                wip.repair_projections(workspace, expected_generation=9)


if __name__ == "__main__":
    unittest.main()
