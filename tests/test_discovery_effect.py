import json
import unittest
from pathlib import Path

from tools.discovery_effect import operation_event_envelope


ROOT = Path(__file__).resolve().parents[1]
RECONCILED = (
    ROOT
    / "examples"
    / "recovery-demo"
    / "operations"
    / "op-000001-03-reconciled.json"
)


def base_event(state: str) -> dict:
    event = {
        "schema_version": "1.0",
        "workspace_id": "effect-envelope-test",
        "operation_id": "op-000001",
        "sequence": 1,
        "state": state,
        "created_at": "2026-09-20T00:00:00Z",
        "writer": {"label": "test", "route": "tests"},
        "action_class": "github_write",
        "target": {
            "kind": "github-file",
            "locator": "owner/repo:path",
            "expected_precondition": "head=abc",
        },
        "intent_summary": "write once",
        "recovery_instruction": "inspect_before_retry",
        "previous_event": None,
    }
    if state in {"VERIFIED", "RECONCILED"}:
        event["effect_receipt"] = {
            "kind": "commit",
            "value": "abc123",
            "readback": "file exists",
        }
        event["result_summary"] = "effect verified"
    return event


class DiscoveryEffectAdapterTests(unittest.TestCase):
    def test_native_states_map_to_existing_v0_phases(self):
        expected = {
            "PREPARED": "PRE_EFFECT",
            "ATTEMPTED": "POST_EFFECT_UNVERIFIED",
            "VERIFIED": "POST_EFFECT_VERIFIED",
            "FAILED": "TERMINAL_FAILURE",
            "AMBIGUOUS": "OUTCOME_UNKNOWN",
            "RECONCILED": "RECONCILED",
        }
        for state, phase in expected.items():
            event = base_event(state)
            envelope = operation_event_envelope(event)
            self.assertEqual(envelope["normalized_phase"], phase)
            self.assertEqual(envelope["source_state"], state)
            self.assertEqual(envelope["source_operation_id"], "op-000001")

    def test_repository_reconciled_example_exports_readback_receipt(self):
        event = json.loads(RECONCILED.read_text(encoding="utf-8"))
        envelope = operation_event_envelope(event)
        self.assertEqual(envelope["normalized_phase"], "RECONCILED")
        self.assertEqual(envelope["retry_disposition"], "DO_NOT_RETRY")
        self.assertIn(
            {
                "kind": "effect_readback",
                "value": "marker build-42 present",
            },
            envelope["receipts"],
        )

    def test_ambiguous_and_attempted_require_inspection_before_retry(self):
        for state in ("ATTEMPTED", "AMBIGUOUS"):
            envelope = operation_event_envelope(base_event(state))
            self.assertEqual(
                envelope["retry_disposition"],
                "INSPECT_BEFORE_RETRY",
            )

    def test_failed_event_does_not_gain_retry_authority_from_envelope(self):
        envelope = operation_event_envelope(base_event("FAILED"))
        self.assertEqual(envelope["normalized_phase"], "TERMINAL_FAILURE")
        self.assertEqual(envelope["retry_disposition"], "DOMAIN_DECIDES")

    def test_verified_requires_native_effect_receipt(self):
        event = base_event("VERIFIED")
        event.pop("effect_receipt")
        with self.assertRaisesRegex(ValueError, "requires effect_receipt"):
            operation_event_envelope(event)

    def test_adapter_is_observational_and_does_not_mutate_event(self):
        event = base_event("PREPARED")
        before = json.loads(json.dumps(event))
        operation_event_envelope(event)
        self.assertEqual(event, before)


if __name__ == "__main__":
    unittest.main()
