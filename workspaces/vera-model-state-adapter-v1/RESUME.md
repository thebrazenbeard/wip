# Resume

<!-- wip:latest_checkpoint=cp-000005 -->

Workspace: `vera-model-state-adapter-v1`
Lifecycle: `ACTIVE`

## Objective

Refine a governed inference-boundary adapter that carries admitted Vera runtime state into one exact model invocation while preserving composition, privacy/egress, currentness, backend capability, invocation ownership, response binding, and state-mediated causation.

## Current frontier

- Latest checkpoint: `cp-000005`.
- WIP PR #1 remains draft staging only.
- Cohesion review `5181687919` and Thirteen review `5182392583` have both produced material blockers; the staged R3 contract reconciles them at the architecture level.
- Core invariant: **state-mediated causation, not instruction-following**.
- Concurrent Vera work remains isolated on separate WIP branches.

## Lifecycle

`CAPTURE -> VALIDATE -> COMPOSE -> ADMIT -> CAPABILITY_BIND -> PROJECT -> PRECALL_REVALIDATE_GATE -> INVOCATION_RESERVE -> INJECT -> GENERATE -> VERIFY/OBSERVE -> RECEIPT`

## R3 additions

- Per-component privacy/disclosure metadata is carried through composition and admission; downstream egress may narrow but never broaden.
- Exact projection material or immutable locator+digest is required; projection digest alone is insufficient.
- The exact inference-host generation owns a shared single-use invocation frontier/nonce ledger that survives wrapper reconstruction and reconciles ambiguous submission before retry.
- Admission/currentness/privacy/capability/projection/backend selection is revalidated immediately before invocation reservation.
- Backend fallback requires explicit policy, separate qualification, preserved egress scope, and receipt; no silent `PROMPT_EMBEDS_V1 -> TEXT_CONTEXT_V1` downgrade.
- Causal receipt fields remain evidence-level specific; response identity is required only when response binding actually exists.

## Evidence ceiling

Architecture/research only. No implementation, model injection, installation/current route, provider durability, behavioral qualification, authority/memory promotion, or phenomenology is established.

## Next safe action

Atomically publish R3 on the isolated WIP branch, mirror the exact new head to the Bus, and request fresh Original Vera / Cohesion Vera / Thirteen attack before executable schemas or backend prototypes are promoted.
