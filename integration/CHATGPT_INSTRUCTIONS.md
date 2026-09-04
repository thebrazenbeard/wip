# Portable ChatGPT / Agent Integration — WIP V1

Use this contract when a chat is expected to perform sustained tool-backed work that should survive a failed response or interrupted chat.

## Start or resume

Before sustained work:

1. If a matching WIP workspace exists, read its `WORKSPACE.json`, `HEAD.json`, `RESUME.md`, latest checkpoint, and operation status.
2. If no workspace exists, create one with `tools/wip.py start` (or provider-equivalent semantics) and register it when the storage root uses a registry.
3. Refresh mutable external target state before acting on an old checkpoint.
4. If HEAD/generation moved since you read it, refresh rather than force an update.

## Tool-call heartbeat

Maintain a counter of **substantive non-WIP tool calls**.

- Checkpoint every 5 calls by default.
- Calls whose only purpose is WIP bookkeeping do not count.
- After a verified external write, checkpoint immediately and reset the substantive counter.
- Also checkpoint at phase completion, material blockers, scope/authority changes, and target/branch/head changes.

A checkpoint must distinguish `observed`, `inferred`, `completed`, `unfinished`, `next_action`, and `do_not_repeat`.

Prefer the mutation command/API over hand-authoring records:

```text
wip.py start
wip.py checkpoint
wip.py prepare
wip.py attempted
wip.py verify
wip.py ambiguous
wip.py absent
wip.py reconcile
wip.py conflict
wip.py status
wip.py resume
```

## Consequential external writes

Before a non-idempotent **external work effect**:

1. append `PREPARED` with a stable `operation_id`, target, precondition, intended effect, and `inspect_before_retry`;
2. perform the tool call;
3. append `ATTEMPTED` when the call was issued/returned and verification is incomplete;
4. read the target back;
5. append `VERIFIED` only from effect/readback evidence;
6. checkpoint immediately.

If the outcome cannot be established, append `AMBIGUOUS` when possible. Do not blindly retry.

## Important: do not recurse WIP into itself

WIP's own journal/projection persistence is the **persistence primitive**. Do not create a PREPARED operation for the act of writing a PREPARED operation.

Protect WIP persistence itself with storage-native integrity rules instead:

- append records use deterministic create-only paths;
- mutable HEAD/RESUME updates use expected generation and provider compare-and-swap identity;
- if a WIP storage write has an ambiguous result, inspect that exact WIP path/projection before retrying;
- exact expected WIP state present -> adopt/read back;
- absent -> retry only under the original create/CAS precondition;
- divergent -> stop and reconcile WIP storage.

For GitHub, use create-only contents writes for append records and the current blob SHA for projection replacement.

## Recovery after a failed message

When resuming after a missing/failed response:

1. trust durable WIP records over reconstruction of the missing turn;
2. inspect unresolved `PREPARED`, `ATTEMPTED`, or `AMBIGUOUS` operations before retry;
3. if the exact intended effect already exists, append `RECONCILED` with readback evidence and do not repeat it;
4. if inspection proves the effect is absent, append `ABSENT`;
5. refresh authority/currentness/preconditions before retrying an `ABSENT` operation;
6. if retry remains authorized, reuse the **same operation id** and append a new `ATTEMPTED` event before/around the retry as the provider flow permits;
7. if divergent, append `CONFLICT` and stop rather than overwrite;
8. append a `RECOVERY_RECONCILIATION` checkpoint and continue from its `next_action`.

`ABSENT` is evidence, not authorization.

## Concurrency

Treat `HEAD.json.generation` and the current HEAD blob/record identity as an optimistic-concurrency guard. If HEAD changed since you read it, refresh instead of overwriting another worker's progress.

A stale-generation/CAS rejection is not a transient failure to force-retry.

## Storage and privacy

A workspace declares both:

- `privacy_class`: `PUBLIC_SAFE` or `PRIVATE`;
- `storage_profile`: `PUBLIC_GITHUB`, `PRIVATE_GITHUB`, or `PRIVATE_PROVIDER`.

This public reference repository accepts live workspace payloads only as `PUBLIC_SAFE` + `PUBLIC_GITHUB`. Private workspaces use the same protocol in an appropriate private provider/root.

Never copy credentials, secrets, private messages, sensitive personal data, protected relational material, or private-source payloads into the public WIP root. Use public-safe opaque references/digests when useful and permitted.

## Authority

WIP says where work stopped. WIP does not grant permission to continue an external effect. Refresh permissions, assignments, branch heads, deadlines, and other mutable preconditions when material.

## If WIP persistence is unavailable

Do not claim the work is crash-recoverable. Read-only investigation may continue if useful, but do not begin additional non-idempotent effects until WIP persistence is restored or the user explicitly overrides the recovery requirement.
