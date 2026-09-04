# External Effect Protocol V1

WIP uses a write-ahead operation journal for consequential/non-idempotent **external work effects**.

WIP's own journal/projection persistence is the non-recursive storage primitive described in `WIP_PROTOCOL.md`; do not create PREPARED records about writing PREPARED records.

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
- `ATTEMPTED` — the external tool call was issued/returned, but target verification is not yet complete.
- `VERIFIED` — ordinary target readback proves the intended effect exists.
- `FAILED` — the call/effect is deterministically known to have failed.
- `AMBIGUOUS` — outcome cannot yet be resolved.
- `ABSENT` — recovery inspection proves the intended effect did not land; same-operation retry may be considered after fresh authority/currentness checks.
- `RECONCILED` — recovery inspection proves the exact intended effect already exists; adopt it and do not repeat it.
- `CONFLICT` — recovery inspection finds divergent state; stop rather than overwrite.

## Legal transitions

Normal path:

`PREPARED -> ATTEMPTED -> VERIFIED`

Known failure:

`PREPARED -> ATTEMPTED -> FAILED`

Interrupted/uncertain path:

`PREPARED -> ATTEMPTED -> AMBIGUOUS`

Recovery from any unresolved state may resolve to evidence-backed `VERIFIED`, `ABSENT`, `RECONCILED`, `FAILED`, or `CONFLICT` where the transition table in the schema/tool permits it.

A confirmed-absent retry is explicitly:

`... -> ABSENT -> ATTEMPTED -> VERIFIED | FAILED | AMBIGUOUS | ABSENT | RECONCILED | CONFLICT`

The same `operation_id` is reused after `ABSENT`. `ABSENT` is not permission to retry; it is evidence that the previous effect did not land.

Terminal states are `VERIFIED`, `FAILED`, `RECONCILED`, and `CONFLICT`.

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

`RECONCILED` also requires effect/readback evidence because its meaning is “recovery found and adopted the already-landed intended effect.”

`ABSENT` and `CONFLICT` require a result summary describing what recovery inspection established.

## Recovery

For an operation whose latest state is `PREPARED`, `ATTEMPTED`, or `AMBIGUOUS`:

1. inspect the target;
2. if the exact intended effect exists and recovery is adopting it, append `RECONCILED` with the receipt and do not repeat;
3. if inspection proves the effect is absent, append `ABSENT`;
4. before retrying an `ABSENT` operation, refresh authority, current target state, and any material preconditions outside WIP;
5. if retry remains authorized, append `ATTEMPTED` under the **same operation id**, perform the call, then verify normally;
6. if target state diverges, append `CONFLICT` and stop rather than overwrite.

Never infer absence merely because the chat response failed or because no terminal operation event exists.

## WIP persistence failures

If the WIP journal write itself has an ambiguous provider result, do not recursively journal that write. Read the exact WIP path/projection first:

- exact expected record/projection present -> adopt/read back and continue;
- absent -> retry the WIP persistence operation only under its create/CAS precondition;
- divergent -> stop and reconcile WIP storage state.

WIP records continuity. It does not authorize an external retry.
