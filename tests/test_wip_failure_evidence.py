import json
import tempfile
import unittest
from pathlib import Path

from tools import wip


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


class FailureEvidenceTests(unittest.TestCase):
    def test_failed_operation_requires_result_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = wip.start_workspace(
                Path(tmp),
                workspace_id="failed-evidence",
                title="Failed evidence",
                purpose="Prove deterministic failure cannot be a naked label.",
                writer_label="worker-a",
                writer_route="tests/failure-evidence",
            )
            wip.append_operation_event(
                workspace,
                expected_generation=0,
                operation_id="op-000001",
                state="PREPARED",
                writer_label="worker-a",
                writer_route="tests/failure-evidence",
                action_class="file_write",
                target={"kind": "file", "locator": "external/result.txt"},
                intent_summary="Create result.txt.",
                recovery_instruction="inspect_before_retry",
            )

            # Bypass the mutation API to construct the malformed historical
            # event that strict schema validation must reject.
            write_json(
                workspace / "operations" / "op-000001-02-failed.json",
                {
                    "schema_version": "1.0",
                    "workspace_id": "failed-evidence",
                    "operation_id": "op-000001",
                    "sequence": 2,
                    "state": "FAILED",
                    "created_at": "2026-09-04T16:50:00Z",
                    "writer": {"label": "worker-a", "route": "tests/failure-evidence"},
                    "action_class": "file_write",
                    "target": {"kind": "file", "locator": "external/result.txt"},
                    "intent_summary": "Create result.txt.",
                    "recovery_instruction": "no_retry_required",
                    "previous_event": "op-000001-01-prepared"
                },
            )

            # Advance the projections manually so the failure we observe is
            # specifically missing failure evidence, not stale HEAD.
            head = json.loads((workspace / "HEAD.json").read_text(encoding="utf-8"))
            head["generation"] = 2
            head["latest_operation_event"] = "op-000001-02-failed"
            head["updated_at"] = "2026-09-04T16:50:00Z"
            write_json(workspace / "HEAD.json", head)
            (workspace / "RESUME.md").write_text(wip.render_resume(workspace), encoding="utf-8")

            errors = wip.validate_workspace(workspace)
            self.assertTrue(any("result_summary" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
