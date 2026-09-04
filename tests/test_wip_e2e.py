import json
import tempfile
import unittest
from pathlib import Path

from tools import wip


class CrashRecoveryQualificationTests(unittest.TestCase):
    def require_mutation_api(self):
        required = ("start_workspace", "append_checkpoint", "append_operation_event")
        missing = [name for name in required if not hasattr(wip, name)]
        if missing:
            self.fail(f"missing mutation API: {missing}")

    def test_effect_landed_then_message_died_reconciles_without_duplicate(self):
        self.require_mutation_api()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = wip.start_workspace(
                root,
                workspace_id="landed-effect",
                title="Landed effect recovery",
                purpose="Prove recovery adopts an effect instead of repeating it.",
                writer_label="worker-a",
                writer_route="tests/e2e",
            )

            wip.append_checkpoint(
                workspace,
                expected_generation=0,
                writer_label="worker-a",
                writer_route="tests/e2e",
                reason="MANUAL",
                objective="Create one external artifact.",
                observed=["External artifact is absent."],
                inferred=[],
                completed=["Workspace registered."],
                unfinished=["Create artifact exactly once."],
                next_action="Prepare the external write.",
                do_not_repeat=[],
                target_snapshots=[],
                tool_calls_since_previous=0,
            )

            prepared = wip.append_operation_event(
                workspace,
                expected_generation=1,
                operation_id="op-000001",
                state="PREPARED",
                writer_label="worker-a",
                writer_route="tests/e2e",
                action_class="file_write",
                target={"kind": "file", "locator": "external/result.txt", "expected_precondition": "absent"},
                intent_summary="Create result.txt exactly once.",
                recovery_instruction="inspect_before_retry",
            )
            self.assertEqual(prepared["operation_id"], "op-000001")

            # The external tool succeeds, then the chat/runtime dies before
            # ATTEMPTED/VERIFIED can be persisted.
            external = root / "external" / "result.txt"
            external.parent.mkdir(parents=True)
            writes = 0
            if not external.exists():
                external.write_text("created once\n", encoding="utf-8")
                writes += 1

            recovered = wip.inspect_workspace(workspace)
            self.assertIn("op-000001", recovered["unresolved_operations"])
            self.assertEqual(external.read_text(encoding="utf-8"), "created once\n")

            # Fresh worker inspects first, sees the intended effect already
            # exists, and adopts it. It does NOT call the external write again.
            if external.exists() and external.read_text(encoding="utf-8") == "created once\n":
                wip.append_operation_event(
                    workspace,
                    expected_generation=2,
                    operation_id="op-000001",
                    state="RECONCILED",
                    writer_label="worker-b",
                    writer_route="tests/e2e-recovery",
                    action_class="file_write",
                    target={"kind": "file", "locator": "external/result.txt", "expected_precondition": "absent"},
                    intent_summary="Create result.txt exactly once.",
                    recovery_instruction="no_retry_required",
                    result_summary="Recovery inspection found the exact intended effect already present.",
                    effect_receipt={"kind": "file-content", "value": "created once", "readback": "external/result.txt"},
                )
            else:
                self.fail("recovery fixture expected the external effect to exist")

            wip.append_checkpoint(
                workspace,
                expected_generation=3,
                writer_label="worker-b",
                writer_route="tests/e2e-recovery",
                reason="RECOVERY_RECONCILIATION",
                objective="Continue after adopting the landed effect.",
                observed=["result.txt exists with the exact intended content."],
                inferred=[],
                completed=["Recovered op-000001 without repeating the write."],
                unfinished=["Continue normal work."],
                next_action="Continue from the recovered frontier.",
                do_not_repeat=["Do not recreate external/result.txt."],
                target_snapshots=[{"kind": "file", "locator": "external/result.txt", "note": "Verified during recovery."}],
                tool_calls_since_previous=1,
            )

            self.assertEqual(writes, 1)
            self.assertEqual(wip.validate_workspace(workspace), [])
            final = wip.inspect_workspace(workspace)
            self.assertNotIn("op-000001", final["unresolved_operations"])

    def test_absent_effect_can_retry_same_operation_id_then_verify(self):
        self.require_mutation_api()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = wip.start_workspace(
                root,
                workspace_id="absent-effect",
                title="Absent effect recovery",
                purpose="Prove a confirmed absent effect can retry with the same operation id.",
                writer_label="worker-a",
                writer_route="tests/e2e",
            )

            wip.append_operation_event(
                workspace,
                expected_generation=0,
                operation_id="op-000001",
                state="PREPARED",
                writer_label="worker-a",
                writer_route="tests/e2e",
                action_class="file_write",
                target={"kind": "file", "locator": "external/result.txt", "expected_precondition": "absent"},
                intent_summary="Create result.txt exactly once.",
                recovery_instruction="inspect_before_retry",
            )
            wip.append_operation_event(
                workspace,
                expected_generation=1,
                operation_id="op-000001",
                state="ATTEMPTED",
                writer_label="worker-a",
                writer_route="tests/e2e",
                action_class="file_write",
                target={"kind": "file", "locator": "external/result.txt", "expected_precondition": "absent"},
                intent_summary="Create result.txt exactly once.",
                recovery_instruction="inspect_before_retry",
            )

            external = root / "external" / "result.txt"
            self.assertFalse(external.exists())

            absent = wip.append_operation_event(
                workspace,
                expected_generation=2,
                operation_id="op-000001",
                state="ABSENT",
                writer_label="worker-b",
                writer_route="tests/e2e-recovery",
                action_class="file_write",
                target={"kind": "file", "locator": "external/result.txt", "expected_precondition": "absent"},
                intent_summary="Create result.txt exactly once.",
                recovery_instruction="inspect_before_retry",
                result_summary="Recovery inspection proved the intended effect did not land.",
            )
            self.assertEqual(absent["operation_id"], "op-000001")
            status = wip.inspect_workspace(workspace)
            self.assertIn("op-000001", status["retryable_absent_operations"])

            # Simulated fresh authority/currentness refresh occurs outside WIP.
            retried = wip.append_operation_event(
                workspace,
                expected_generation=3,
                operation_id="op-000001",
                state="ATTEMPTED",
                writer_label="worker-b",
                writer_route="tests/e2e-recovery",
                action_class="file_write",
                target={"kind": "file", "locator": "external/result.txt", "expected_precondition": "absent"},
                intent_summary="Retry the same logical operation after confirmed absence.",
                recovery_instruction="inspect_before_retry",
            )
            self.assertEqual(retried["operation_id"], "op-000001")

            external.parent.mkdir(parents=True)
            external.write_text("created on retry\n", encoding="utf-8")

            verified = wip.append_operation_event(
                workspace,
                expected_generation=4,
                operation_id="op-000001",
                state="VERIFIED",
                writer_label="worker-b",
                writer_route="tests/e2e-recovery",
                action_class="file_write",
                target={"kind": "file", "locator": "external/result.txt", "expected_precondition": "absent"},
                intent_summary="Retry the same logical operation after confirmed absence.",
                recovery_instruction="no_retry_required",
                result_summary="Retry landed and readback matched.",
                effect_receipt={"kind": "file-content", "value": "created on retry", "readback": "external/result.txt"},
            )
            self.assertEqual(verified["operation_id"], "op-000001")
            self.assertEqual(external.read_text(encoding="utf-8"), "created on retry\n")
            self.assertEqual(wip.validate_workspace(workspace), [])
            final = wip.inspect_workspace(workspace)
            self.assertNotIn("op-000001", final["retryable_absent_operations"])
            self.assertNotIn("op-000001", final["unresolved_operations"])


if __name__ == "__main__":
    unittest.main()
