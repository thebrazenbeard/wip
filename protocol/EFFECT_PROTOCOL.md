# External Effect Protocol V1

WIP uses a write-ahead operation journal for consequential/non-idempotent external effects.

## Operation identity

Each operation receives a stable id:

`op-000001`, `op-000002`, ...

Each state transition is a separate append-only file:

`op-000001-01-prepared.json`
`op-000001-02-attempted.json`
`op-000001-03-verified.json`

The operation id persists across recovery. Never mint a new operation id merely because the original chat died.

## States

- `PREPARED` — intent and target/preconditions were durably recorded before the external call.
- `ATTEMPTED` — the external tool call returned or there is direct evidence it was issued, but target verification is not yet complete.
- `VERIFIED` — target readback proves the intended effect exists.
- `FAILED` — the call/effect is known not to have succeeded and the failure is deterministic enough to record.
- `AMBIGUOUS` — outcome cannot be resolved at the time of the event.
- `RECONCILED` — a later recovery inspection resolved a previously incomplete/ambiguous operation.

## Required transitions

Normal path:

`PREPARED -> ATTEMPTED -> VERIFIED`

Known failure:

`PREPARED -> ATTEMPTED -> FAILED`

Interrupted/uncertain path:

`PREPARED -> ATTEMPTED -> AMBIGUOUS -> RECONCILED`

Recovery may also reconcile a lone `PREPARED` record after inspecting the target if the worker cannot prove whether the external call was ever issued.

## Prepare before effect

`PREPARED` records MUST identify:

- action class;
- target locator;
- expected precondition when known;
- intended effect summary;
- recovery instruction (`inspect_before_retry` for non-idempotent writes).

They MUST NOT contain credentials or sensitive payload bodies in this public repository.

## Verify after effect

A `VERIFIED` event MUST contain enough receipt material to distinguish the intended effect from a merely successful tool response: commit SHA, blob SHA, provider record id/digest, external object id, or equivalent target readback.

A tool response without target readback is not `VERIFIED` when readback is reasonably available.

## Recovery

For an operation whose latest state is `PREPARED`, `ATTEMPTED`, or `AMBIGUOUS`:

1. inspect the target;
2. if the exact intended effect exists, append `RECONCILED` with the receipt and do not repeat;
3. if it is absent, refresh authority/currentness and retry only if still authorized, reusing the operation id;
4. if target state diverges, record conflict in the reconciliation event and stop rather than overwrite.

WIP records continuity. It does not authorize the retry.