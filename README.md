> **License:** Source-visible, not open source. The original material is proprietary and permits limited private, noncommercial evaluation; redistribution, commercial use, and hosted products require written permission. See [LICENSE](LICENSE) and [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md). Third-party components retain their own terms.

# WIP — durable work-state and external-effect recovery

**A portable checkpoint protocol and Python validation toolkit for long-running AI-agent and tool-backed workflows.**

WIP (Work In Progress) lets an application or agent record what it verified, what remains unfinished, and which external operations may have happened before a crash or interrupted conversation. A later worker can inspect those records, reconcile uncertain effects against the real target, and resume from evidence.

WIP provides **record schemas, protocols, examples, a repository/workspace validator, and a read-only recovery inspector**. It does not automatically capture an agent's tool calls, create checkpoints for you, persist a chat session, or grant permission to execute an action. The host or worker must implement the integration contract and durably save the records.

## When to use it

- **Interrupted work:** preserve an observed/inferred/completed/unfinished frontier and a precise next action across failed messages, process restarts, or worker handoffs.
- **Non-idempotent effects:** write an operation intent before a consequential external call, then record its outcome only after target readback. On recovery, inspect before retrying.
- **Concurrent workers:** use a monotonically increasing HEAD generation and the storage provider's compare-and-swap precondition to avoid clobbering another worker's progress.

The reference protocol calls for a checkpoint every **five substantive non-WIP tool calls**, plus immediate checkpoints after a verified write, completed phase, material blocker, authority/scope change, or relevant target movement. This is an **integration obligation**, not a timer or enforcement feature in the validator.

## Try the validator

Requires Python 3.10 or newer; the shipped Python tools use only the standard library.

```bash
python3 -m unittest discover -s tests -v
python3 tools/wip.py validate .
python3 tools/wip.py status examples/recovery-demo
```

`validate` checks the repository or one WIP workspace for structural invariants such as checkpoint numbering, HEAD/RESUME agreement, and operation-event transitions. `status` prints a JSON recovery projection with lifecycle, generation, latest checkpoint, unresolved operation IDs, and validation errors. **Both commands inspect local records; neither creates, repairs, or publishes an external workspace.**

To start your own workflow, adapt the files in [templates/](templates/) and follow the [portable integration contract](integration/CHATGPT_INSTRUCTIONS.md). The project does not currently ship a `wip init` or automatic checkpoint-writing command.

## Record model

| Record | Purpose |
|---|---|
| `WORKSPACE.json` | Stable workspace identity, public-safe privacy class, checkpoint policy |
| `checkpoints/cp-*.json` | Append-only observed, inferred, completed, unfinished, next-action and do-not-repeat evidence |
| `operations/op-*.json` | Append-only prepared/attempted/verified/failed/ambiguous/reconciled external-effect transitions |
| `HEAD.json` | Mutable recovery projection with generation and current lifecycle |
| `RESUME.md` | Small human/agent continuation card aligned with HEAD |
| `registry/workspaces.json` | Repository-level discovery projection |

The [workspace schema](schemas/workspace.schema.json), [checkpoint schema](schemas/checkpoint.schema.json), [operation-event schema](schemas/operation-event.schema.json), and [HEAD schema](schemas/head.schema.json) document the V1 record contracts. [Protocol specifications](protocol/WIP_PROTOCOL.md) define the intended worker obligations.

Workspace lifecycle states are `ACTIVE`, `PAUSED`, `PROMOTED`, `SHELVED`, `SUPERSEDED`, and `ABANDONED`. There is deliberately no `DONE`: successful work should be promoted to its authoritative destination, leaving WIP as a recovery record.

## External-effect recovery

The [effect protocol](protocol/EFFECT_PROTOCOL.md) records `PREPARED` before a consequential call, `ATTEMPTED` when issued, and `VERIFIED` only after sufficient target readback. If the outcome cannot be established, the worker records `AMBIGUOUS` and inspects the target before any retry. A later `RECONCILED` record preserves the finding without duplicating the action.

The [recovery demonstration](examples/recovery-demo/RESUME.md) shows a completed external effect whose chat completion was lost: fresh readback found the intended result, so the operation was reconciled rather than repeated.

The separate [discovery-effect envelope adapter](tools/discovery_effect.py) translates an existing WIP operation event into a neutral observational envelope. Its output describes evidence and retry disposition; it is **not an authorization token**, a provider-authentication check, or permission to perform the effect.

## Integration boundaries and safety

- **Currentness and authority:** A checkpoint proves only what was observed at record time. Before executing or retrying an operation, the host must refresh permissions, assignment, target head, and other mutable preconditions. WIP does not supply immutable authority/provider bindings or a complete authorization service.
- **Storage durability:** The protocol describes append-only history and optimistic concurrency. Actual atomic writes, persistence, access control, and compare-and-swap enforcement are responsibilities of the chosen storage host.
- **Privacy:** This public repository's V1 validator accepts only `PUBLIC_SAFE` workspaces. Do not commit private chats, credentials, third-party restricted sources, or sensitive personal material; use opaque references or digests where appropriate.
- **Editor safety:** The tracked source is checked against automatic editor startup tasks and disguised launchers by [the editor-startup guard](tools/editor_startup_guard.py). A concealed historical launcher was removed from the active tree; Git history may still contain it. These checks do not scan a live workstation or establish that the removed launcher ever executed.

## Project map

- [Integration instructions](integration/CHATGPT_INSTRUCTIONS.md) — how a host/worker records and resumes work
- [Recovery protocol](protocol/RECOVERY_PROTOCOL.md) — inspection and reconciliation sequence
- [Templates](templates/) and [example workspace](examples/recovery-demo/WORKSPACE.json) — starting records and worked case
- [Validator and inspector](tools/wip.py) — executable checks and status projection
- [Workspace catalog](workspaces/README.md) — public-safe durable workspace conventions
- [Discovery-effect integration boundary](docs/DISCOVERY_EFFECT_ENVELOPE_CONSUMER_V1.md) — neutral evidence exchange

WIP's core promise is modest: **an interrupted message need not erase an accurately recorded work frontier**. Safe recovery still depends on correct host integration, durable storage, fresh target verification, and separately established authority.
