# Portable ChatGPT / Agent Integration — WIP V1

Use this contract when a chat is expected to perform sustained tool-backed work that should survive a failed response or interrupted chat.

## Start or resume

Before sustained work:

1. If a matching WIP workspace exists, read its `WORKSPACE.json`, `HEAD.json`, `RESUME.md`, latest checkpoint, and unresolved operation events.
2. If no workspace exists, create one using the V1 templates and register it.
3. Refresh mutable external target state before acting on an old checkpoint.

## Tool-call heartbeat

Maintain a counter of **substantive non-WIP tool calls**.

- Checkpoint every 5 calls by default.
- Calls whose only purpose is WIP bookkeeping do not count.
- After a verified external write, checkpoint immediately and reset the substantive counter.
- Also checkpoint at phase completion, material blockers, scope/authority changes, and target/branch/head changes.

A checkpoint must distinguish `observed`, `inferred`, `completed`, `unfinished`, `next_action`, and `do_not_repeat`.

## Consequential writes

Before a non-idempotent external write/effect:

1. append a `PREPARED` operation event with stable `operation_id`, target, precondition, intended effect, and `inspect_before_retry`;
2. perform the tool call;
3. append `ATTEMPTED` when the call was issued/returned;
4. read the target back;
5. append `VERIFIED` only from effect/readback evidence;
6. checkpoint immediately.

If the outcome cannot be established, append `AMBIGUOUS` when possible. Do not blindly retry.

## Recovery after a failed message

When resuming after a missing/failed response:

1. trust durable WIP records over reconstruction of the missing turn;
2. inspect unresolved `PREPARED`, `ATTEMPTED`, or `AMBIGUOUS` operations before retry;
3. if the exact intended effect exists, append `RECONCILED` and do not repeat it;
4. if absent, refresh authority/currentness before retrying with the same operation id;
5. if divergent, stop and surface conflict;
6. append a `RECOVERY_RECONCILIATION` checkpoint and continue from its `next_action`.

## Concurrency

Treat `HEAD.json.generation` and the current HEAD blob/record identity as an optimistic-concurrency guard. If HEAD changed since you read it, refresh instead of overwriting another worker's progress.

## Privacy

This repository is public. Store only `PUBLIC_SAFE` information. Never copy credentials, secrets, private messages, sensitive personal data, or private-source payloads into checkpoints. Use opaque references/digests when needed.

## Authority

WIP says where work stopped. WIP does not grant permission to continue an external effect. Refresh permissions, assignments, branch heads, deadlines, and other mutable preconditions when material.

## If WIP persistence is unavailable

Do not claim the work is crash-recoverable. Read-only investigation may continue if useful, but do not begin additional non-idempotent effects until WIP persistence is restored or the user explicitly overrides the recovery requirement.