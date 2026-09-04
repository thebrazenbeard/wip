# WIP Protocol V1

## 1. Scope

WIP is a durable crash-recovery protocol for sustained tool-backed work. It preserves the verified frontier of progress across failed messages, runtime interruption, full chats, and worker handoff.

WIP is continuity infrastructure, not an authority source. A saved instruction to modify an external target does not prove that target is still current or that permission still exists.

## 2. Record classes

WIP separates four kinds of record:

- `WORKSPACE.json` — immutable workspace identity, storage class, and checkpoint policy.
- `checkpoints/*.json` and `operations/*.json` — append-only history.
- `HEAD.json` and `RESUME.md` — mutable current projections.
- `registry/workspaces.json` — mutable repository index.

Historical files are never rewritten as ordinary operation. Corrections are new records plus a projection update.

The JSON schemas under `schemas/` are executable contracts. Repository validation is not complete until both schema constraints and cross-record invariants pass.

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

Before a non-idempotent external effect, write a `PREPARED` operation event. After the tool call is issued/returns, append `ATTEMPTED` when possible. After target inspection, append the evidence-backed next state.

The hardened state model is:

- `PREPARED` — intent durably recorded before the call;
- `ATTEMPTED` — call was issued/returned but effect verification is incomplete;
- `AMBIGUOUS` — outcome still cannot be established;
- `ABSENT` — inspection proved the intended effect did not land; retry may be possible after fresh authority/currentness checks;
- `VERIFIED` — ordinary readback proved the intended effect exists;
- `RECONCILED` — recovery inspection proved a previously unresolved effect already exists and was adopted without repeating it;
- `FAILED` — deterministic failure is established;
- `CONFLICT` — divergent target state was found; stop rather than overwrite.

If interruption leaves an operation at `PREPARED`, `ATTEMPTED`, or `AMBIGUOUS`, recovery MUST inspect the target before retrying. `ABSENT` may transition back to `ATTEMPTED` using the same operation id only after the external authority/currentness preconditions are refreshed.

## 5. WIP persistence is the non-recursive primitive

The rule “write `PREPARED` before a consequential external effect” does **not** recursively apply to persistence of the WIP journal itself. Otherwise writing the PREPARED record would require another PREPARED record forever.

WIP's own persistence operations are the storage primitive and protect themselves with provider-native integrity controls:

- append-only journal paths are deterministic and create-only;
- mutable projections use compare-and-swap / expected-version semantics;
- an ambiguous WIP storage response is reconciled by reading the exact WIP target before retry;
- an ambiguous WIP storage mutation is never blindly repeated.

For GitHub-backed WIP, append-only records map to create-only contents writes and projection updates map to the current blob SHA as the compare-and-swap precondition. The local reference tool uses exclusive file creation for append records and expected `HEAD.json.generation` checks before projection-changing mutation.

This exception is narrow. It makes WIP persistence finite; it does not exempt external project effects from operation journaling.

## 6. Recovery contract

A worker resuming a workspace MUST:

1. read `WORKSPACE.json`;
2. read `HEAD.json`;
3. read `RESUME.md`;
4. inspect operation history for unresolved `PREPARED`, `ATTEMPTED`, or `AMBIGUOUS` operations, plus any `ABSENT` retryable operation or `CONFLICT`;
5. refresh mutable external target state required by the next action;
6. reconcile unresolved effects before retry;
7. continue from the exact next safe action.

A worker MUST NOT claim old target heads, permissions, deadlines, assignments, or other mutable facts are still current merely because WIP recorded them.

## 7. Concurrency

`HEAD.json.generation` is an optimistic-concurrency token. A writer reads generation N and replaces HEAD only if the exact projection it read remains current. On GitHub, the current blob SHA is the stronger write precondition and SHOULD be used together with generation.

If another worker advanced HEAD, refresh. Do not force overwrite.

A failed stale-generation update is successful conflict detection, not permission to retry with force.

## 8. Storage and privacy

Workspace storage semantics are explicit:

- `privacy_class`: `PUBLIC_SAFE` or `PRIVATE`;
- `storage_profile`: `PUBLIC_GITHUB`, `PRIVATE_GITHUB`, or `PRIVATE_PROVIDER`.

This repository is a public reference root. Its machine-readable `storage/REPOSITORY_POLICY.json` permits live workspace payloads only when `privacy_class=PUBLIC_SAFE` and `storage_profile=PUBLIC_GITHUB`.

Private workspaces use the same WIP record model in a private storage root/provider. A public WIP record may carry a public-safe opaque locator/digest to a protected object, but it MUST NOT copy protected payload content merely to improve recovery.

Do not copy credentials, secrets, private messages, sensitive personal data, protected relational material, private repository payloads, or restricted source text into this public repository.

## 9. Lifecycle

Nonterminal states: `ACTIVE`, `PAUSED`.

Terminal states: `PROMOTED`, `SHELVED`, `SUPERSEDED`, `ABANDONED`.

There is intentionally no `DONE`. Finished work does not remain canonically owned by WIP; it exits by a terminal disposition.

## 10. Principle

**Work In Progress. Work Is Persistent.**

A failed response may remove the conversational output. It should not erase the verified work state.
