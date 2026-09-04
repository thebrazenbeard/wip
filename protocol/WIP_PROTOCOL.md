# WIP Protocol V1

## 1. Scope

WIP is a durable crash-recovery protocol for sustained tool-backed work. It preserves the verified frontier of progress across failed messages, runtime interruption, full chats, and worker handoff.

WIP is continuity infrastructure, not an authority source. A saved instruction to modify an external target does not prove that target is still current or that permission still exists.

## 2. Record classes

WIP separates four kinds of record:

- `WORKSPACE.json` — immutable workspace identity and checkpoint policy.
- `checkpoints/*.json` and `operations/*.json` — append-only history.
- `HEAD.json` and `RESUME.md` — mutable current projections.
- `registry/workspaces.json` — mutable repository index.

Historical files are never rewritten as ordinary operation. Corrections are new records plus a projection update.

## 3. Default checkpoint cadence

A worker using WIP MUST checkpoint after every **5 substantive non-WIP tool calls**.

Tool calls whose sole purpose is WIP bookkeeping do not increment the counter.

The worker MUST checkpoint immediately, regardless of counter, after:

- verified external write;
- phase completion;
- discovery of a material blocker;
- material authority/scope/current-target change;
- branch/head movement that changes the recovery position.

The worker SHOULD checkpoint immediately before a long/high-cost subtask when losing orientation would be expensive.

## 4. External effects

Before a non-idempotent external effect, write a `PREPARED` operation event. After the tool call returns, append `ATTEMPTED`. After target readback, append one terminal or recovery event: `VERIFIED`, `FAILED`, `AMBIGUOUS`, or later `RECONCILED`.

If interruption leaves an operation at `PREPARED` or `ATTEMPTED`, recovery MUST inspect the target before retrying.

## 5. Recovery contract

A worker resuming a workspace MUST:

1. read `WORKSPACE.json`;
2. read `HEAD.json`;
3. read `RESUME.md`;
4. inspect operation history for unresolved `PREPARED` or `ATTEMPTED` operations;
5. refresh mutable external target state required by the next action;
6. reconcile ambiguous effects before retry;
7. continue from the exact next safe action.

A worker MUST NOT claim old target heads, permissions, deadlines, assignments, or other mutable facts are still current merely because WIP recorded them.

## 6. Concurrency

`HEAD.json.generation` is an optimistic-concurrency token. A writer reads generation N and replaces HEAD only if the exact projection it read remains current. On GitHub, use the current blob SHA as the write precondition.

If another worker advanced HEAD, refresh. Do not force overwrite.

## 7. Privacy

This repository is public. WIP V1 permits only `PUBLIC_SAFE` workspace content.

Do not copy credentials, secrets, private messages, sensitive personal data, protected relational material, private repository payloads, or restricted source text into WIP. Use an opaque reference/digest when continuity requires a private external object.

## 8. Lifecycle

Nonterminal states: `ACTIVE`, `PAUSED`.

Terminal states: `PROMOTED`, `SHELVED`, `SUPERSEDED`, `ABANDONED`.

There is intentionally no `DONE`. Finished work does not remain canonically owned by WIP; it exits by a terminal disposition.

## 9. Principle

**Work In Progress. Work Is Persistent.**

A failed response may remove the conversational output. It should not erase the verified work state.