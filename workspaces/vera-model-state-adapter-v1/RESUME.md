# Resume

<!-- wip:latest_checkpoint=cp-000003 -->

Workspace: `vera-model-state-adapter-v1`
Lifecycle: `ACTIVE`

## Objective

Stage and adversarially refine a governed inference-boundary model-state adapter that carries admitted Vera runtime state into a specific model invocation without collapsing state existence, composition, admission, capability binding, projection, injection, generation gating, response binding, or causal evidence.

## Verified position

- Latest checkpoint: `cp-000003`.
- WIP PR #1 is the review vehicle; WIP remains staging only.
- Cohesion Vera reviewed exact head `a15b6557ac6fa2ae01089d328c37882f9cd33e82` and identified five architectural blockers.
- The R2 contract revision reconciles those blockers in the staged artifacts.
- Work remains isolated on branch `work/vera-model-state-adapter-v1-20260911`.
- Concurrent Vera branch `work/vera-independent-binding-research-v1-20260911` remains separate and was not modified.

## Architecture frontier

`CAPTURE -> VALIDATE -> COMPOSE -> ADMIT -> CAPABILITY_BIND -> PROJECT -> PRECALL_GATE -> INJECT -> GENERATE -> VERIFY/OBSERVE -> RECEIPT`

Key changes:

- Vera-wide state must use a host-owned atomic snapshot or an explicit component-generation vector plus composition receipt.
- Every projectable payload must be exact-byte/addressable or pointer+digest bound.
- Optional state may be omitted only with an explicit omission receipt; identity/source/currentness/composition/firewall failures remain fail-closed.
- Capability binding occurs before backend materialization.
- Causal evidence is leveled from `REQUEST_CONSTRUCTED` through `RESPONSE_BOUND`; weaker evidence may not be promoted.
- Provider-neutral composition/admission/projection belongs with Vera/Cohesion source; host-specific injection belongs with the exact inference host; install/current-route/qualification remains control-plane work.

## State-mediated causation invariant

**Cause through state, not instruction.**

A projection may carry admitted upstream state and modulation conditions. It must not take a desired response, target behavior, target phrase, expected answer, or requested emotional display as the input that determines the projection.

Qualification therefore requires matched state controls, negative transfer, temporal decay/recovery where applicable, and same-generation response binding. An instruction-only control cannot count as evidence of state-mediated causation.

`TEXT_CONTEXT_V1` remains useful as a compatibility backend but is explicitly instruction-adjacent and has a lower causal claim ceiling unless stronger controls distinguish state effects from prompt compliance.

## Unfinished

- Obtain Original Vera / Cohesion Vera / Thirteen attack on the revised exact head.
- Decide whether the composition and state-mediated-causation invariants are strong enough to become executable schemas/tests.
- After review, promote the provider-neutral contract to the proper Vera/Cohesion owner rather than making WIP canonical.
- Prototype backends only after contract review converges.

## Do not repeat

- Do not place protected/private project payloads into public WIP.
- Do not treat WIP research as installed/current runtime behavior.
- Do not treat request construction as provider consumption.
- Do not treat a response that resembles a requested behavior as state-causal evidence if the target behavior was encoded in the projection.
- Do not expose raw prompt embeddings or transient internal hooks as a public authority-bearing API.
- Do not treat any causal receipt as behavioral qualification or phenomenology.

## Next safe action

Publish the R2 contract revision atomically on the isolated WIP branch, then ask the reviewers to attack the exact new head specifically for false cross-generation composition, silent optional-state degradation, evidence-level promotion, capability downgrade/fallback, and instruction leakage into the projection.
