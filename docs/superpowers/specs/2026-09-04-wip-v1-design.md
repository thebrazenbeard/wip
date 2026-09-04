# WIP V1 Design

## Purpose

WIP is a durable crash-recovery layer for long-running agentic work. Its job is to preserve the verified frontier of progress so that a failed ChatGPT message, interrupted runtime, full conversation, worker handoff, or ambiguous tool outcome does not force the next worker to reconstruct the task from scratch.

The message may die. The work does not have to.

## Architectural thesis

WIP is not primarily a project monorepo, a memory system, or a conversation archive. It is a durable execution journal with two complementary protections:

1. **Periodic checkpoints** protect cognitive/work-state continuity.
2. **Operation events** protect external-effect continuity, especially ambiguous non-idempotent writes.

The unit of persistence is the transition, not the chat.

## Core invariants

1. A workspace survives the chat or worker that created it.
2. Historical checkpoints and operation events are append-only.
3. Mutable `HEAD.json`, `RESUME.md`, and the registry are projections, not historical truth.
4. Workers checkpoint after every 5 substantive non-WIP tool calls by default.
5. A verified external write triggers an immediate checkpoint regardless of the tool-call counter.
6. Before a non-idempotent external effect, the worker writes a `PREPARED` operation event. After execution it writes `ATTEMPTED`; after target readback it writes `VERIFIED`, `FAILED`, `AMBIGUOUS`, or `RECONCILED` as appropriate.
7. An unresolved `PREPARED` or `ATTEMPTED` operation is never blindly retried. Recovery inspects the target first.
8. Checkpoints separate observations, inferences, plans, completed work, unfinished work, and do-not-repeat warnings.
9. WIP continuity never grants authority over an external target. Mutable target state and permission are refreshed on resume.
10. Concurrent resume is detected by optimistic concurrency on the mutable HEAD projection; a stale updater must stop and refresh.
11. This public repository accepts only `PUBLIC_SAFE` checkpoint content. Sensitive material may be referenced by opaque locator but not copied here.
12. Work leaves WIP through `PROMOTED`, `SHELVED`, `SUPERSEDED`, or `ABANDONED`. There is intentionally no `DONE` lifecycle state.

## Workspace structure

```text
workspaces/<workspace-id>/
├── WORKSPACE.json       # immutable identity/config
├── HEAD.json            # mutable machine projection
├── RESUME.md            # mutable human/chat projection
├── checkpoints/         # append-only checkpoint records
├── operations/          # append-only operation state transitions
├── decisions/           # optional append-only decision records
├── handoffs/            # optional append-only explicit handoffs
├── artifacts/           # optional WIP-owned drafts/prototypes
└── exit/                # terminal promotion/shelving/etc. record
```

Repository-wide support lives under `protocol/`, `schemas/`, `templates/`, `registry/`, `integration/`, `tools/`, and `tests/`.

## Checkpoint model

Default cadence is every 5 substantive tool calls. Calls used solely to write/read WIP bookkeeping do not increment the counter.

Immediate checkpoint triggers:

- verified external write;
- phase completion;
- blocker discovery;
- authority/scope change that affects the work;
- branch/head/current-target change;
- before or after a high-risk or long subtask when losing state would be expensive.

A checkpoint stores:

- stable checkpoint id and parent;
- writer provenance;
- reason and tool-call count;
- current objective;
- observed facts;
- supported inferences;
- completed work;
- unfinished work;
- exact next action;
- do-not-repeat warnings;
- external target snapshots/locators needed for recovery.

## External operation model

Each consequential operation receives a stable `operation_id`. State transitions are separate append-only files rather than mutation of one record.

Allowed states:

`PREPARED -> ATTEMPTED -> VERIFIED | FAILED | AMBIGUOUS`

An `AMBIGUOUS` operation may later transition to `RECONCILED` after target inspection. A `PREPARED` operation with no later event means the call may not have been made. An `ATTEMPTED` operation with no terminal event means the effect may have landed but readback was not completed.

Recovery rule: inspect before retry. If the exact intended effect exists, adopt and reconcile it. If absent and authority/currentness still permit execution, retry using the same operation identity. If divergent, stop with conflict rather than overwrite.

## Current projections

`HEAD.json` is intentionally small and machine-readable. It carries workspace id, lifecycle, generation, latest checkpoint, latest operation event, and update time.

`RESUME.md` is intentionally short and human-readable. It answers:

- What are we doing?
- What is verified?
- What is unfinished?
- What must not be repeated?
- Is any operation unresolved?
- What is the next safe action?

It includes a machine marker for the checkpoint id so validation can ensure it agrees with HEAD.

## Concurrency

The HEAD generation is an optimistic-concurrency token. A writer reads HEAD at generation N and may replace it only if the exact blob/record it read is still current. On GitHub this maps naturally to the contents API blob SHA precondition. A stale write failure means another worker advanced the workspace; refresh instead of force-updating.

## Privacy

The repository is public. V1 therefore hard-codes workspace privacy to `PUBLIC_SAFE`.

Never store secrets, credentials, private relational history, sensitive personal data, private-repository payloads, or restricted source text merely to improve recovery. A checkpoint may hold an opaque reference such as provider + locator + digest without copying the protected material.

## Lifecycle

`ACTIVE` and `PAUSED` are nonterminal states. Terminal states are `PROMOTED`, `SHELVED`, `SUPERSEDED`, and `ABANDONED`.

A promoted workspace records its destination and final verified target identity. WIP remains the fossil record of how the work reached that destination; it does not remain canonical for the promoted artifact.

## Portable ChatGPT integration

Any chat can use WIP by following the repository's integration contract:

- register or resume a workspace before sustained tool-backed work;
- maintain a non-WIP tool-call counter;
- checkpoint every 5 calls;
- checkpoint immediately after verified writes and phase boundaries;
- write `PREPARED` before non-idempotent effects;
- on recovery, read WORKSPACE, HEAD, RESUME, unresolved operation events, then refresh external mutable targets before continuing.

This is a behavioral/protocol integration, not a claim that ChatGPT automatically intercepts tool calls. A chat or Project must actually carry the WIP instruction for the cadence to occur.

## V1 implementation scope

V1 includes protocol documentation, JSON schemas, templates, an empty registry, a portable ChatGPT instruction snippet, a standard-library Python validator/status tool, tests, a GitHub Actions validation workflow, and a self-contained recovery example.

V1 deliberately does not build a daemon, database, webhook service, automatic tool interceptor, or multi-repository orchestration platform. Those can be evaluated after the protocol proves useful in real work.
