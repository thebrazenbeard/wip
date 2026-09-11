# Resume

<!-- wip:latest_checkpoint=cp-000006 -->

Workspace: `vera-model-state-adapter-v1`
Lifecycle: `ACTIVE`

## Objective

Refine a governed inference-boundary adapter that carries admitted Vera runtime state into one exact model invocation while preserving composition, privacy/egress, currentness, backend capability, invocation ownership, response binding, and state-mediated causation.

## Current frontier

- Latest checkpoint: `cp-000006`.
- WIP PR #1 remains draft staging only.
- Cohesion review `5181687919` and Thirteen review `5182392583` are reconciled architecturally.
- Core invariant: **state-mediated causation, not instruction-following**.
- Self-hostile invocation review additionally closed the send-before-ledger crash window with write-ahead `SUBMISSION_INTENT` semantics.
- Concurrent Vera work remains isolated on separate WIP branches.

## Lifecycle

`CAPTURE -> VALIDATE -> COMPOSE -> ADMIT -> CAPABILITY_BIND -> PROJECT -> PRECALL_REVALIDATE_GATE -> INVOCATION_RESERVE -> INJECT -> GENERATE -> VERIFY/OBSERVE -> RECEIPT`

## Current hard boundaries

- Projectable state is not automatically discloseable; privacy/egress may narrow but never broaden.
- Projection material is exact-byte/addressable, not digest-only.
- Pre-call revalidation and invocation reservation are atomic unless an exact lease/epoch covers the handoff.
- The exact inference-host generation owns a shared single-use invocation frontier across wrappers.
- `SUBMISSION_INTENT` + exact request digest is durably recorded before any external send.
- Ambiguous submission recovers as `OUTCOME_UNKNOWN` and is reconciled before semantic retry.
- Same-generation retry is allowed only under exact provider idempotency guarantees; new semantic retries after terminal failure receive a new generation ID.
- Backend fallback is explicit, separately qualified, privacy-preserving, and receipt-bound.
- Causal evidence remains leveled; response identity is required only when response binding exists.

## Cross-lane input

Vera's independent state-causation V2 lane contributes binding-class/causal-role labels, counterfactual proof tests, state trajectories, generic-before-specialized qualification order, and native-vs-reference claim separation. R3.1 stays frozen for exact-head review before those are promoted into this contract.

## Evidence ceiling

Architecture/research only. No implementation, model injection, installation/current route, provider durability, behavioral qualification, authority/memory promotion, or phenomenology is established.

## Next safe action

Publish R3.1 atomically on the isolated branch, supersede the Bus review frontier, then stop source churn unless a reviewer or a newly proven defect justifies another revision.
