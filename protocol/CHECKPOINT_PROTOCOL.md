# Checkpoint Protocol V1

A checkpoint is an append-only recovery record describing the verified frontier of a workspace at one moment.

## Identifier

Checkpoint IDs are zero-padded and monotonic within a workspace:

`cp-000001`, `cp-000002`, ...

Every checkpoint except the first carries `parent_checkpoint_id` equal to the prior checkpoint id. The first uses `null`.

## Required semantic separation

A checkpoint MUST keep these categories distinct:

- `observed` — directly read or verified facts.
- `inferred` — supported interpretation not directly verified.
- `completed` — work known to have completed.
- `unfinished` — work still open.
- `next_action` — one exact safe continuation action.
- `do_not_repeat` — operations/actions already known to have succeeded or that require inspection before repetition.

Model-generated reasoning must not be silently promoted from `inferred` to `observed` on later resumptions.

## Reasons

Allowed checkpoint reasons:

- `TOOL_INTERVAL`
- `VERIFIED_WRITE`
- `PHASE_COMPLETE`
- `BLOCKER`
- `SCOPE_CHANGE`
- `TARGET_MOVED`
- `PRE_RISKY_SUBTASK`
- `MANUAL`
- `RECOVERY_RECONCILIATION`

## Tool-call count

`tool_calls_since_previous` counts substantive non-WIP tool calls since the previous checkpoint. WIP bookkeeping calls are excluded.

The default periodic threshold is 5. Immediate trigger checkpoints may occur below 5 and reset the substantive counter to zero after the checkpoint is verified.

## Target snapshots

A checkpoint MAY record external targets needed for recovery, including repository/ref/head, file locator/digest, provider record id, or other opaque locator. Such a snapshot is historical recovery evidence only. Recovery refreshes mutable target state before continuing.

## Projection update order

For an ordinary checkpoint:

1. append the checkpoint record;
2. read it back/verify it when the transport supports readback;
3. update `HEAD.json` using optimistic concurrency;
4. update `RESUME.md` to the same checkpoint id;
5. update the registry if lifecycle/summary changed.

If the historical checkpoint write succeeds but projection update fails, recovery treats the checkpoint as durable history and repairs the projection after inspecting current HEAD. It must not recreate the checkpoint under the same id with different bytes.