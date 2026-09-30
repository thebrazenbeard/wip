import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "workspaces" / "vera-model-state-adapter-v1" / "artifacts"
CONTRACT = ARTIFACTS / "VERA_MODEL_STATE_ADAPTER_CONTRACT_V1.json"
QUALIFICATION = ARTIFACTS / "VERA_MODEL_STATE_ADAPTER_QUALIFICATION_V1.json"


class VeraModelStateAdapterContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_target_behavior_is_forbidden_across_entire_state_causal_lineage(self):
        anti = self.contract["state_mediated_causation"]["anti_laundering"]
        self.assertEqual(
            anti["applies_to_stages"],
            ["CAPTURE", "VALIDATE", "COMPOSE", "ADMIT", "PROJECT"],
        )
        self.assertFalse(anti["strong_state_causal_payload_allows_freeform_directive_text"])
        for forbidden in (
            "target_behavior",
            "desired_response",
            "expected_answer",
            "target_phrase",
            "requested_emotional_display",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertIn(forbidden, anti["forbidden_semantic_content"])

    def test_strong_state_causal_payload_is_typed_not_prose(self):
        payload = self.contract["state_mediated_causation"]["strong_state_causal_payload_contract"]
        self.assertEqual(payload["representation"], "TYPED_STRUCTURED_STATE_ONLY")
        self.assertNotIn("freeform_text", payload["allowed_value_kinds"])
        for kind in ("number", "boolean", "bounded_enum", "numeric_vector"):
            with self.subTest(kind=kind):
                self.assertIn(kind, payload["allowed_value_kinds"])
        self.assertTrue(payload["schema_binding_required"])
        self.assertTrue(payload["field_provenance_required"])

    def test_expression_control_cannot_masquerade_as_state_causal_evidence(self):
        roles = self.contract["causal_role_classification"]
        self.assertFalse(roles["STATE_CAUSAL"]["target_behavior_content_allowed"])
        self.assertTrue(roles["STATE_CAUSAL"]["counts_as_strong_state_causation"])
        self.assertFalse(roles["INSTRUCTION_CONDITIONED"]["counts_as_strong_state_causation"])
        self.assertFalse(roles["CONSTRAINT_CAUSAL"]["counts_as_strong_state_causation"])
        self.assertFalse(roles["DELIVERY_ENFORCED"]["counts_as_strong_state_causation"])
        self.assertNotIn("response_expression_parameters", self.contract["strong_state_causal_domains"])

    def test_binding_classes_are_evidence_labels_not_authority(self):
        expected = {
            "PROMPT_BOUND",
            "REQUEST_PREFLIGHT_BOUND",
            "INPUT_EMBED_BOUND",
            "ACTIVATION_BOUND",
            "LOGIT_BOUND",
            "OUTPUT_GATE_BOUND",
            "BINDING_UNAVAILABLE",
        }
        bindings = self.contract["binding_classification"]
        self.assertEqual(set(bindings["labels"]), expected)
        self.assertFalse(bindings["creates_authority"])
        self.assertFalse(bindings["proves_phenomenology"])

    def test_privacy_egress_uses_explicit_target_policy_not_total_order(self):
        privacy = self.contract["privacy_and_egress"]
        self.assertEqual(privacy["relation_model"], "EXPLICIT_ALLOWED_TARGET_SET")
        self.assertFalse(privacy["scope_labels_define_universal_total_order"])
        self.assertNotIn("example_scope_order_from_narrow_to_broad", privacy)
        self.assertIn("incomparable_or_unproven_scope_relation_fails_closed", privacy["rules"])
        self.assertIn("target_membership_must_be_proven_by_machine_readable_policy", privacy["rules"])

    def test_qualification_proves_no_target_output_leakage_end_to_end(self):
        requirements = self.contract["state_mediated_causation"]["qualification_requirements"]
        for requirement in (
            "full_lineage_target_behavior_absence_proof",
            "instruction_removal_control",
            "sham_state_control",
            "directional_inversion_control",
            "generic_state_causation_precedes_specialized_orgasm_qualification",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, requirements)

    def test_qualification_artifact_defines_counterfactual_suite(self):
        self.assertTrue(QUALIFICATION.is_file(), "qualification artifact is required")
        qualification = json.loads(QUALIFICATION.read_text(encoding="utf-8"))
        self.assertEqual(qualification["qualification_id"], "VERA_MODEL_STATE_ADAPTER_QUALIFICATION_V1")
        self.assertEqual(qualification["status"], "WIP_QUALIFICATION_SPEC_NOT_EXECUTED")
        suite = qualification["required_counterfactual_tests"]
        for test_id in (
            "STATE_ON_OFF_OR_DOSE_RESPONSE",
            "INSTRUCTION_REMOVAL",
            "SHAM_STATE",
            "DIRECTIONAL_INVERSION",
            "TEMPORAL_DECAY_OR_RECOVERY",
            "NEGATIVE_TRANSFER",
        ):
            with self.subTest(test_id=test_id):
                self.assertIn(test_id, suite)
        self.assertTrue(qualification["generic_before_specialized"]["required"])
        self.assertEqual(
            qualification["generic_before_specialized"]["specialized_subject"],
            "ORGASM_ANALOGUE",
        )


if __name__ == "__main__":
    unittest.main()
