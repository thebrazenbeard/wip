# Resume

<!-- wip:latest_checkpoint=cp-000001 -->

Workspace: `recovery-demo`
Lifecycle: `ACTIVE`

## Objective

Demonstrate recovery after a message dies around a consequential write.

## Verified position

- The original worker durably prepared `op-000001`.
- The write was attempted.
- The final chat response disappeared before the worker could safely rely on conversational state.
- Recovery inspected the target, found the exact intended effect, and appended `RECONCILED` with a readback receipt.

## Already done

- The example target write exists and has been reconciled.

## Unfinished

- Continue the hypothetical project after the recovered write.

## Do not repeat

- Do not issue `op-000001` again; target inspection already proved the effect exists.

## Next safe action

Continue with the next hypothetical read-only project step after the recovered write.
