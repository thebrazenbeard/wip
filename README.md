# Work in Progress

WIP is a durable crash-recovery layer for long-running ChatGPT and agentic work.

The original idea is simple: Vera or any chat should be able to build something, keep its progress durably recorded, and pick the work back up if a response dies, a chat fills, a runtime changes, or a tool effect becomes ambiguous.

**Work In Progress. Work Is Persistent.**

> The message may die. The work doesn't have to.

## What WIP protects

WIP solves two different failure modes:

1. **Work-state loss** — the worker did useful reads/reasoning/tool work, but the final message failed and the next chat no longer knows exactly where to continue.
2. **Effect ambiguity** — an external write may have succeeded before the response failed, so blindly repeating it could duplicate or corrupt work.

Periodic checkpoints solve the first problem. A write-ahead operation journal solves the second.

## Default heartbeat

A worker using WIP checkpoints after every **5 substantive non-WIP tool calls**.

WIP bookkeeping calls do not count toward the five.

Checkpoint immediately instead of waiting for five after:

- a verified external write;
- a completed phase;
- a material blocker;
- a scope/authority change;
- a target branch/head/current-state change.

## Before a consequential write

For a non-idempotent external effect:

```text
PREPARED
   ↓
perform tool call
   ↓
ATTEMPTED
   ↓
read target back
   ↓
VERIFIED / FAILED / AMBIGUOUS
```

If the chat dies after `PREPARED` or `ATTEMPTED`, the replacement worker **inspects the target before retrying**.

If the intended effect already exists, it is adopted and reconciled rather than repeated.

That is the difference between:

> "I think the last chat probably did it."

and:

> "The operation was prepared, the response died, fresh inspection found the exact effect, so do not repeat it."

## Workspace layout

```text
workspaces/<workspace-id>/
├── WORKSPACE.json       immutable identity + checkpoint policy
├── HEAD.json            mutable machine recovery projection
├── RESUME.md            short human/chat continuation card
├── checkpoints/         append-only work-state checkpoints
├── operations/          append-only external-effect transitions
├── decisions/           optional append-only decision records
├── handoffs/            optional explicit worker handoffs
├── artifacts/           optional WIP-owned drafts/prototypes
└── exit/                promotion/shelving/supersession/abandonment
```

Repository support:

```text
protocol/       normative behavior
schemas/        machine-readable V1 contracts
templates/      valid starter records
integration/    portable ChatGPT/agent instructions
registry/       workspace discovery projection
tools/          validator and recovery inspector
tests/          executable invariants
examples/       recovery demonstrations
```

## The recovery surface

Historical records are append-only.

`HEAD.json` and `RESUME.md` are deliberately small projections of that history.

A replacement chat should normally need only:

1. `WORKSPACE.json`
2. `HEAD.json`
3. `RESUME.md`
4. the latest checkpoint
5. unresolved operation events
6. fresh reads of mutable external targets needed for the next action

It should not need to ingest an enormous previous conversation and hope the missing turn can be reconstructed.

## Checkpoints distinguish fact from thought

A checkpoint keeps these separate:

- `observed`
- `inferred`
- `completed`
- `unfinished`
- `next_action`
- `do_not_repeat`

That prevents a later recovery from slowly turning "we think X" into "X was verified."

## Concurrency

`HEAD.json.generation` is an optimistic-concurrency token.

If two workers resume the same workspace, a stale worker must refresh rather than overwrite a newer HEAD. On GitHub, the contents API blob SHA naturally serves as the compare-and-swap precondition.

## Lifecycle

Nonterminal:

- `ACTIVE`
- `PAUSED`

Terminal:

- `PROMOTED`
- `SHELVED`
- `SUPERSEDED`
- `ABANDONED`

There is intentionally no `DONE` state.

Successful work usually leaves WIP by **promotion** to its canonical home. WIP keeps the durable fossil record of how it got there; it does not compete with the promoted project for authority.

## Public-repository privacy rule

This repository is public. V1 accepts only `PUBLIC_SAFE` workspace content.

Do **not** put credentials, secrets, private messages, sensitive personal material, private-repository payloads, or restricted source text into WIP merely to improve recovery. Store an opaque reference/digest instead when continuity needs to point at a protected object.

## Use it from ChatGPT

The portable integration contract is in:

`integration/CHATGPT_INSTRUCTIONS.md`

In short:

```text
start/resume workspace
        ↓
work
        ↓
every 5 substantive tool calls → checkpoint
        ↓
consequential write → PREPARED before, verify after, checkpoint immediately
        ↓
message fails
        ↓
read WIP + inspect unresolved effects + refresh external reality
        ↓
continue
```

## Validate a checkout

No third-party Python dependencies are required.

```bash
python -m unittest discover -s tests -v
python tools/wip.py validate .
python tools/wip.py status examples/recovery-demo
```

The GitHub Actions workflow runs the same validation on repository changes.

## Example

`examples/recovery-demo/` shows a worker that durably recorded a write, lost the conversational completion state, then recovered by inspecting the target and discovering that the write had already landed.

The recovery worker reconciles the operation and explicitly records:

**do not repeat it.**

## Limits

WIP does not automatically intercept ChatGPT tool calls. The worker/chat/Project must actually carry the WIP integration instruction and perform the checkpoint writes.

WIP also does not grant authority. A checkpoint can say which repository head or assignment existed when it was written; a resumed worker still refreshes mutable target state and permission before acting.

## The point

Chats are containers for work. They should not be single points of failure for it.

Checkpoint the frontier. Record uncertain effects before they happen. Verify what actually landed. Resume from evidence instead of vibes.

Then if the UI decides to throw **Message failed to deliver** after forty minutes of useful work, pick the shit back up and keep going.
