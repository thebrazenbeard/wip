import tempfile
import unittest
from pathlib import Path

from tools import wip


class WipCliTests(unittest.TestCase):
    def test_cli_operation_verbs_map_to_persisted_states(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            common_writer = ["--writer-label", "cli-worker", "--writer-route", "tests/cli"]

            self.assertEqual(
                wip.main([
                    "start", str(parent),
                    "--workspace-id", "cli-demo",
                    "--title", "CLI demo",
                    "--purpose", "Prove CLI verbs map to operation states.",
                    *common_writer,
                ]),
                0,
            )
            workspace = parent / "cli-demo"

            common_operation = [
                *common_writer,
                "--action-class", "file_write",
                "--target-kind", "file",
                "--target-locator", "external/result.txt",
                "--intent-summary", "Create one result file.",
            ]

            self.assertEqual(
                wip.main([
                    "prepare", str(workspace),
                    "--expected-generation", "0",
                    *common_operation,
                ]),
                0,
            )
            self.assertTrue((workspace / "operations" / "op-000001-01-prepared.json").is_file())

            self.assertEqual(
                wip.main([
                    "attempted", str(workspace),
                    "--expected-generation", "1",
                    "--operation-id", "op-000001",
                    *common_operation,
                ]),
                0,
            )

            self.assertEqual(
                wip.main([
                    "verify", str(workspace),
                    "--expected-generation", "2",
                    "--operation-id", "op-000001",
                    *common_operation,
                    "--recovery-instruction", "no_retry_required",
                    "--result-summary", "Readback matched.",
                    "--receipt-kind", "file-content",
                    "--receipt-value", "expected-content",
                    "--receipt-readback", "external/result.txt",
                ]),
                0,
            )
            self.assertTrue((workspace / "operations" / "op-000001-03-verified.json").is_file())
            self.assertEqual(wip.validate_workspace(workspace), [])

    def test_cli_reconcile_uses_reconciled_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            common_writer = ["--writer-label", "cli-worker", "--writer-route", "tests/cli"]
            self.assertEqual(
                wip.main([
                    "start", str(parent),
                    "--workspace-id", "cli-reconcile",
                    "--title", "CLI reconcile",
                    "--purpose", "Prove reconcile persists RECONCILED.",
                    *common_writer,
                ]),
                0,
            )
            workspace = parent / "cli-reconcile"
            common_operation = [
                *common_writer,
                "--action-class", "file_write",
                "--target-kind", "file",
                "--target-locator", "external/result.txt",
                "--intent-summary", "Create one result file.",
            ]
            self.assertEqual(
                wip.main(["prepare", str(workspace), "--expected-generation", "0", *common_operation]),
                0,
            )
            self.assertEqual(
                wip.main([
                    "reconcile", str(workspace),
                    "--expected-generation", "1",
                    "--operation-id", "op-000001",
                    *common_operation,
                    "--recovery-instruction", "no_retry_required",
                    "--result-summary", "Recovery found the exact effect.",
                    "--receipt-kind", "file-content",
                    "--receipt-value", "expected-content",
                ]),
                0,
            )
            self.assertTrue((workspace / "operations" / "op-000001-02-reconciled.json").is_file())
            self.assertEqual(wip.validate_workspace(workspace), [])


if __name__ == "__main__":
    unittest.main()
