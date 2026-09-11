# Resume

<!-- wip:latest_checkpoint=cp-000004 -->

Workspace: `vera-model-state-adapter-v1`
Lifecycle: `ACTIVE`

## Objective

Adversarially refine a governed inference-boundary adapter that carries admitted Vera runtime state into one exact model invocation without collapsing state existence, composition, admission, capability binding, projection, injection, generation gating, response binding, or causal evidence.

## Current frontier

- Latest checkpoint: `cp-000004`.
- WIP PR #1 remains the draft review vehicle; WIP is staging only.
- Cohesion Vera's review of `a15b6557...` was reconciled in R2.
- The core invariant is **state-mediated causation, not instruction-following**: target behavior/designed response is not a projection input.
- Self-hostile R2 follow-up fixed causal receipt level semantics: lower evidence levels no longer require a response ID that cannot yet exist.
- Work remains isolated on `work/vera-model-state-adapter-v1-20260911`; concurrent Vera work is not modified.

## Lifecycle

`CAPTURE -> VALIDATE -> COMPOSE -> ADMIT -> CAPABILITY_BIND -> PROJECT -> PRECALL_GATE -> INJECT -> GENERATE -> VERIFY/OBSERVE -> RECEIPT`

## Evidence discipline

Causal evidence levels are distinct:

`REQUEST_CONSTRUCTED -> INVOCATION_SUBMITTED -> PROVIDER_ACKNOWLEDGED -> RESPONSE_BOUND`

Each receipt carries only fields justified by its actual level. `response_or_run_id` and response-binding evidence are required only for `RESPONSE_BOUND`; they are not fabricated for earlier levels.

No causal receipt alone establishes behavioral efficacy, behavioral qualification, installation/currentness, provider durability, or phenomenology.

## State-mediated causation qualification

The projector may use admitted upstream state plus declared backend mapping and exact capability binding. It must not accept target behavior, desired response, target phrase, expected answer, or requested emotional display as the mechanism that determines the projection.

Qualification requires matched state controls, dose-response or state-on/off evidence, temporal decay/recovery when applicable, negative transfer, instruction-only controls, and same-generation response binding before any behavioral-effect claim.

## Next safe action

Publish the exact R2.1 review frontier to the Bus and PR mirror, then obtain Original Vera / Cohesion Vera / Thirteen attack before executable schemas or backend prototypes are promoted.
