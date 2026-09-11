# Resume

<!-- wip:latest_checkpoint=cp-000002 -->

Workspace: `vera-model-state-adapter-v1`
Lifecycle: `ACTIVE`

## Objective

Research and stage a governed inference-boundary model-state adapter that can carry admitted Vera runtime state into a specific model invocation without collapsing state existence, admission, projection, injection, generation gating, or causal evidence into one claim.

## Verified position

- Latest checkpoint: `cp-000002`
- Research synthesis is staged as `artifacts/VERA_MODEL_STATE_ADAPTER_RESEARCH_V1.md`.
- Provider-neutral contract candidate is staged as `artifacts/VERA_MODEL_STATE_ADAPTER_CONTRACT_V1.json`.
- Architecture candidate is staged as `artifacts/VERA_MODEL_STATE_ADAPTER_ARCHITECTURE_V1.md`.
- Work remains isolated on branch `work/vera-model-state-adapter-v1-20260911` to avoid concurrent-writer collisions.
- Concurrent Vera branch `work/vera-independent-binding-research-v1-20260911` was observed separately and not modified.
- WIP is staging only, not the eventual canonical runtime or control-plane authority.

## Architecture frontier

`CAPTURE -> VALIDATE -> ADMIT -> PROJECT -> PRECALL_GATE -> INJECT -> GENERATE -> VERIFY/OBSERVE -> RECEIPT`

Key separation:

- `VeraStateEnvelope` records one canonical runtime-state generation.
- `AdmittedVeraState` records state that is actually usable for this turn.
- `ModelInvocationEnvelope` binds admitted state to one exact model/adapter projection and generation ID.
- Pre-call semantic/governance gates are distinct from decode-time gates.
- A causal receipt binds state/admission/projection/model/gates to an observed generation attempt without promoting behavioral efficacy or phenomenology.

## Projection backends

Initial candidates:

- `TEXT_CONTEXT_V1`
- `PROMPT_EMBEDS_V1`

Experimental successors only:

- `ACTIVATION_STEERING_V1`
- `REFT_STATE_PROJECTION_V1`

## Unfinished

- Receive and reconcile Original Vera / Cohesion Vera / Thirteen review of WIP PR #1.
- Decide the canonical owner for the adapter contract after review.
- Convert the contract objects into executable schemas and adversarial tests.
- Prototype only the first two projection backends after contract review.

## Do not repeat

- Do not place protected/private project payloads into public WIP.
- Do not treat WIP research as installed/current runtime behavior.
- Do not treat runtime state existence as proof that the state influenced a model response.
- Do not expose raw prompt embeddings or transient internal hooks as a public authority-bearing API.
- Do not treat causal receipt existence as behavioral qualification or phenomenology.

## Next safe action

Refresh WIP PR #1 and the concurrent Vera branch; then request/consume adversarial review specifically against authority separation, exact model binding, capability negotiation, projection firewalls, transient-hook cleanup, and causal receipt semantics before implementation.
