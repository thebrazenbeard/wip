# Vera Model-State Adapter Finalization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the WIP model-state-adapter research package as a schema-valid, CI-green, anti-laundering, review-ready candidate without merging, deploying, installing, or promoting it to canonical authority.

**Architecture:** Preserve WIP as public-safe staging. First restore the workspace's own checkpoint/recovery invariants. Then close the remaining state-to-instruction laundering defect by making strong state-causal payloads typed and non-free-form across CAPTURE -> COMPOSE -> ADMIT -> PROJECT, and add executable regression tests over the machine-readable contract. Finish with a final valid checkpoint, stationary exact review head, full CI evidence, and a Bus handoff.

**Tech Stack:** JSON/Markdown contracts, Python 3.12 standard-library `unittest`, existing `tools/wip.py` repository validator, GitHub Actions `validate-wip`.

**Spec:** `workspaces/vera-model-state-adapter-v1/artifacts/VERA_MODEL_STATE_ADAPTER_ARCHITECTURE_V1.md`

## Global Constraints

- WIP remains `PUBLIC_SAFE` staging only.
- No merge, deploy, install, provider mutation, paid execution, current-route promotion, authority/memory promotion, or phenomenology claim.
- State-mediated causation must not encode target behavior, desired response, target phrase, expected answer, or requested emotional display anywhere in the strong state-causal lineage.
- Truth, factual confidence, consent, authorization, identity, autobiographical-memory admission, relationship status, provider currentness, and phenomenology remain non-projectable authority domains.
- Privacy/egress may narrow downstream but never broaden.
- Every branch move is fast-forward from a freshly read exact frontier; never force-update.
- Existing independent Vera branch is read-only cross-lane input; do not modify or merge it.

---

### Task 1: Restore WIP checkpoint integrity

**Files:**
- Modify: `workspaces/vera-model-state-adapter-v1/checkpoints/cp-000003.json`
- Modify: `workspaces/vera-model-state-adapter-v1/checkpoints/cp-000004.json`
- Modify: `workspaces/vera-model-state-adapter-v1/checkpoints/cp-000005.json`
- Modify: `workspaces/vera-model-state-adapter-v1/checkpoints/cp-000006.json`

**Interfaces:**
- Consumes: checkpoint invariants enforced by `tools/wip.py::validate_workspace`.
- Produces: a contiguous `cp-000001` -> `cp-000006` chain accepted by the repository validator without changing the historical meaning of checkpoints 3-6.

- [ ] **Step 1: Preserve the observed failing baseline**

Evidence already captured from GitHub Actions run `34637149485`: unit tests pass; repository validation fails with 44 errors because checkpoints 3-6 use `parent_checkpoint` and ad-hoc fields instead of the required WIP checkpoint shape.

- [ ] **Step 2: Rewrite `cp-000003` to the canonical checkpoint shape**

Use `parent_checkpoint_id: "cp-000002"`, an allowed reason (`VERIFIED_WRITE`), non-negative `tool_calls_since_previous`, structured `writer`, arrays for `observed`, `inferred`, `completed`, `unfinished`, `do_not_repeat`, and `target_snapshots`, plus a non-empty `next_action`. Preserve the Cohesion review ID, reviewed head, five closed blockers, `CAPABILITY_BIND`, and state-mediated-causation invariant as content inside those canonical fields.

- [ ] **Step 3: Rewrite `cp-000004` through `cp-000006` the same way**

Keep the parent chain exact (`3 -> 2`, `4 -> 3`, `5 -> 4`, `6 -> 5`) and preserve each checkpoint's original finding/repair meaning and exact contract/architecture blob observations.

- [ ] **Step 4: Push only the checkpoint repair and wait for automatic PR CI**

Expected: `python -m unittest discover -s tests -v` PASS; `python tools/wip.py validate .` PASS. Do not proceed to Task 2 unless the baseline is green.

### Task 2: Add the anti-laundering RED regression

**Files:**
- Create: `tests/test_vera_model_state_adapter_contract.py`

**Interfaces:**
- Consumes: `workspaces/vera-model-state-adapter-v1/artifacts/VERA_MODEL_STATE_ADAPTER_CONTRACT_V1.json`.
- Produces: executable contract-level tests that fail on R3.1 and define the minimum R4 closure.

- [ ] **Step 1: Add a failing test that guards the full causal lineage**

```python
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "workspaces" / "vera-model-state-adapter-v1" / "artifacts" / "VERA_MODEL_STATE_ADAPTER_CONTRACT_V1.json"


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
        self.assertIn("target_behavior", anti["forbidden_semantic_content"])
        self.assertIn("desired_response", anti["forbidden_semantic_content"])
        self.assertIn("expected_answer", anti["forbidden_semantic_content"])
        self.assertIn("target_phrase", anti["forbidden_semantic_content"])
        self.assertIn("requested_emotional_display", anti["forbidden_semantic_content"])

    def test_strong_state_causal_payload_is_typed_not_prose(self):
        payload = self.contract["state_mediated_causation"]["strong_state_causal_payload_contract"]
        self.assertEqual(payload["representation"], "TYPED_STRUCTURED_STATE_ONLY")
        self.assertNotIn("freeform_text", payload["allowed_value_kinds"])
        self.assertIn("number", payload["allowed_value_kinds"])
        self.assertIn("boolean", payload["allowed_value_kinds"])
        self.assertIn("bounded_enum", payload["allowed_value_kinds"])
        self.assertIn("numeric_vector", payload["allowed_value_kinds"])

    def test_expression_control_cannot_masquerade_as_state_causal_evidence(self):
        roles = self.contract["causal_role_classification"]
        self.assertEqual(roles["STATE_CAUSAL"]["target_behavior_content_allowed"], False)
        self.assertEqual(roles["INSTRUCTION_CONDITIONED"]["counts_as_strong_state_causation"], False)
        self.assertEqual(roles["DELIVERY_ENFORCED"]["counts_as_strong_state_causation"], False)
        self.assertNotIn("response_expression_parameters", self.contract["strong_state_causal_domains"])

    def test_qualification_proves_no_target_output_leakage_end_to_end(self):
        requirements = self.contract["state_mediated_causation"]["qualification_requirements"]
        self.assertIn("full_lineage_target_behavior_absence_proof", requirements)
        self.assertIn("instruction_removal_control", requirements)
        self.assertIn("sham_state_control", requirements)
        self.assertIn("directional_inversion_control", requirements)
        self.assertIn("generic_state_causation_precedes_specialized_orgasm_qualification", requirements)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Push the test without changing the contract**

Expected automatic CI: unit-test step FAILS because R3.1 has no `anti_laundering`, `strong_state_causal_payload_contract`, `causal_role_classification`, or `strong_state_causal_domains`. Repository validation must remain PASS. This is the required RED observation.

### Task 3: Close anti-laundering and produce R4

**Files:**
- Modify: `workspaces/vera-model-state-adapter-v1/artifacts/VERA_MODEL_STATE_ADAPTER_CONTRACT_V1.json`
- Modify: `workspaces/vera-model-state-adapter-v1/artifacts/VERA_MODEL_STATE_ADAPTER_ARCHITECTURE_V1.md`
- Create: `workspaces/vera-model-state-adapter-v1/artifacts/VERA_MODEL_STATE_ADAPTER_QUALIFICATION_V1.json`

**Interfaces:**
- Consumes: Task 2 regression expectations and the independent Vera V2 review inputs.
- Produces: R4 contract with full-lineage anti-laundering, explicit causal-role/binding semantics, and counterfactual qualification requirements.

- [ ] **Step 1: Update contract schema to `1.5` and add anti-laundering invariants**

Add:

```json
"anti_laundering": {
  "applies_to_stages": ["CAPTURE", "VALIDATE", "COMPOSE", "ADMIT", "PROJECT"],
  "strong_state_causal_payload_allows_freeform_directive_text": false,
  "forbidden_semantic_content": [
    "target_behavior",
    "desired_response",
    "target_phrase",
    "expected_answer",
    "requested_emotional_display"
  ],
  "rule": "Renaming or nesting forbidden output-direction content inside state, memory salience, expression parameters, metadata, or another field does not make it state-causal."
},
"strong_state_causal_payload_contract": {
  "representation": "TYPED_STRUCTURED_STATE_ONLY",
  "allowed_value_kinds": ["number", "boolean", "bounded_enum", "numeric_vector"],
  "schema_binding_required": true,
  "field_provenance_required": true
}
```

Define `strong_state_causal_domains` separately from compatibility/expression controls. Keep bounded affect, salience, attention allocation, action tendency, satiation/refractory state, admitted goal weighting, temporal state, and admitted memory salience only when represented through the typed state schema. Remove `response_expression_parameters` from this strong causal set.

- [ ] **Step 2: Add causal-role and binding classifications**

Use the independent-lane semantics without importing authority:

```json
"causal_role_classification": {
  "INSTRUCTION_CONDITIONED": {"counts_as_strong_state_causation": false},
  "STATE_CAUSAL": {"counts_as_strong_state_causation": true, "target_behavior_content_allowed": false},
  "CONSTRAINT_CAUSAL": {"counts_as_strong_state_causation": false},
  "DELIVERY_ENFORCED": {"counts_as_strong_state_causation": false}
}
```

Add binding labels `PROMPT_BOUND`, `REQUEST_PREFLIGHT_BOUND`, `INPUT_EMBED_BOUND`, `ACTIVATION_BOUND`, `LOGIT_BOUND`, `OUTPUT_GATE_BOUND`, `BINDING_UNAVAILABLE` as evidence labels, not authority promotion.

- [ ] **Step 3: Add qualification object**

`VERA_MODEL_STATE_ADAPTER_QUALIFICATION_V1.json` must define matched state-on/off or dose-response tests, instruction-removal, sham-state, directional inversion, decay/recovery for temporal state, negative transfer, exact same-generation response binding, and the rule that generic state causation must pass before specialized Orgasm qualification can count.

- [ ] **Step 4: Update architecture prose consistently**

Explain that the anti-laundering firewall starts at capture, not merely at projection; distinguish semantic state variables from output-control fields; keep `TEXT_CONTEXT_V1` explicitly weak/instruction-adjacent.

- [ ] **Step 5: Push R4 and wait for automatic CI**

Expected: all unit tests PASS and repository validation PASS.

### Task 4: Final recovery state and review handoff

**Files:**
- Create: `workspaces/vera-model-state-adapter-v1/checkpoints/cp-000007.json`
- Modify: `workspaces/vera-model-state-adapter-v1/HEAD.json`
- Modify: `workspaces/vera-model-state-adapter-v1/RESUME.md`
- Modify: WIP PR #1 description/comment metadata only
- Create: next Bus message and external-PR mirror on `bus/vera-v2`

**Interfaces:**
- Consumes: exact green R4 head and CI run evidence.
- Produces: a stationary, recoverable final WIP candidate with an exact next boundary.

- [ ] **Step 1: Write canonical checkpoint `cp-000007`**

Use `reason: "PHASE_COMPLETE"`, `parent_checkpoint_id: "cp-000006"`, valid writer/tool count fields, and arrays required by WIP. Record exact R4 head/blobs/test run, the anti-laundering closure, and no stronger claim than `WIP_RESEARCH_CANDIDATE_VERIFIED`.

- [ ] **Step 2: Advance HEAD/RESUME consistently**

Set generation/latest checkpoint to 7 and the resume marker to `cp-000007`. Lifecycle remains `ACTIVE` unless promotion occurs; do not invent a terminal `DONE` lifecycle.

- [ ] **Step 3: Let CI verify the final checkpoint commit**

Expected: unit tests PASS; repository validation PASS.

- [ ] **Step 4: Freeze exact review head and mirror it to the Bus**

State explicitly that WIP work is complete to its authorized boundary: research contract, executable regressions, recovery integrity, and CI are complete; canonical promotion/merge/runtime implementation are separate protected successors requiring Patrick's exact authority.

- [ ] **Step 5: Do not merge**

Leave WIP PR #1 draft/unmerged as the promotion package unless Patrick separately authorizes a merge or canonical promotion.
