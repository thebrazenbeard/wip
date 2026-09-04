# WIP V1 Hardening Design

## Status

This document hardens the existing WIP V1 architecture without replacing its core model. The V1 thesis remains: WIP is a durable crash-recovery layer for long-running agentic work, preserving the verified frontier so a failed message or interrupted runtime does not erase operational continuity.

## Goal

Move WIP from a sound protocol prototype to a trustworthy recovery substrate that agents can actually use repeatedly, including ambiguous external effects, stale concurrent writers, public/private storage separation, and full crash-resume qualification.

## Non-goals

This hardening does not build a daemon, background agent, native ChatGPT tool interceptor, database service, or distributed lock service. It does not make WIP authority-bearing. It does not merge private content into this public repository.

## Hardening requirements

### H1 — Schema-exact validation

The JSON schemas under `schemas/` must become executable contracts rather than documentation that is stricter than the validator.

The standard-library validator must support the subset of JSON Schema Draft 2020-12 used by WIP V1:

- `type`
- `required`
- `properties`
- `additionalProperties`
- `const`
- `enum`
- `pattern`
- `minLength` / `maxLength`
- `minimum` / `maximum`
- `items`
- `oneOf`
- `allOf`
- `if` / `then`
- `format: date-time`

All workspace records must be validated against their repository schemas before cross-record invariants are evaluated.

Cross-record validation must additionally enforce:

- checkpoint `workspace_id` equals the containing workspace identity;
- operation-event `workspace_id` equals the containing workspace identity;
- HEAD `workspace_id` equals the containing workspace identity;
- append-only record filename identifiers match record-body identifiers;
- HEAD pointers resolve to existing records;
- checkpoint parent linkage is monotonic and gap-free;
- operation event sequences are monotonic and state transitions are legal;
- the RESUME marker agrees with HEAD;
- registry entries agree with the workspace identity/path they expose.

A repository validation result of `OK` must therefore mean both schema-valid and cross-record coherent.

### H2 — First-class mutation commands

Repeated checkpointing is part of the reliability model, so hand-authoring JSON cannot remain the normal path.

`tools/wip.py` must support local-checkout mutation commands in addition to `validate` and `status`:

- `start`
- `checkpoint`
- `prepare`
- `attempted`
- `verify`
- `ambiguous`
- `absent`
- `reconcile`
- `conflict`
- `resume`

The implementation may expose reusable Python functions behind the CLI. Mutations must:

- refuse to overwrite append-only records;
- use deterministic identifiers and paths;
- require an expected HEAD generation for projection-changing writes after workspace creation;
- reject stale generations rather than silently overwrite another worker's projection;
- update HEAD and RESUME coherently;
- remain standard-library-only.

The CLI is a reference implementation for local checkouts. Remote provider adapters may use the same semantics without being implemented in V1 hardening.

### H3 — Close the persistence recursion

The V1 rule “write PREPARED before a consequential external effect” creates a recursion unless WIP's own storage mutation is explicitly treated as the persistence primitive.

WIP substrate writes do **not** recursively create operation events about themselves.

Instead, WIP persistence writes must use provider-native integrity controls:

- deterministic append-only record paths with create-only semantics;
- expected-generation / compare-and-swap semantics for mutable projections;
- read-after-ambiguous-result reconciliation before retry;
- no blind retry of an ambiguous WIP storage mutation.

For GitHub-backed WIP, append-only files map to create-only contents writes and projection changes map to blob-SHA compare-and-swap. For a local checkout, exclusive creation plus expected-generation checks is the reference behavior.

This exception is narrow: it applies only to persistence of WIP's own journal/projections. External work effects still use the operation journal.

### H4 — Storage-class abstraction and public-repository policy

The WIP protocol must support private recovery state without putting private payloads into this public reference repository.

Workspace identity gains two independent concepts:

- `privacy_class`: `PUBLIC_SAFE` or `PRIVATE`
- `storage_profile`: `PUBLIC_GITHUB`, `PRIVATE_GITHUB`, or `PRIVATE_PROVIDER`

The public `thebrazenbeard/wip` repository is a `PUBLIC_REFERENCE` storage root and may contain live workspaces only when:

- `privacy_class == PUBLIC_SAFE`, and
- `storage_profile == PUBLIC_GITHUB`.

Private workspaces use the same schemas and recovery semantics in a private provider. This public repository may hold a public-safe opaque locator/digest to such a workspace, but not the protected payload.

A repository policy file must make the root's allowed classes machine-readable, and repository validation must reject incompatible live workspace storage classes.

### H5 — Correct ambiguous-effect recovery semantics

Qualification exposed a V1 state-machine hole: V1 said that recovery may inspect an ambiguous effect, find it absent, and retry with the same operation identity, but the event model had no explicit resolved-absent state from which retry was legal.

The hardened state machine is:

- `PREPARED`
- `ATTEMPTED`
- `VERIFIED`
- `FAILED`
- `AMBIGUOUS`
- `ABSENT`
- `RECONCILED`
- `CONFLICT`

Legal transitions:

- `PREPARED -> ATTEMPTED | VERIFIED | FAILED | AMBIGUOUS | ABSENT | RECONCILED | CONFLICT`
- `ATTEMPTED -> VERIFIED | FAILED | AMBIGUOUS | ABSENT | RECONCILED | CONFLICT`
- `AMBIGUOUS -> VERIFIED | FAILED | ABSENT | RECONCILED | CONFLICT`
- `ABSENT -> ATTEMPTED`

Terminal states are `VERIFIED`, `FAILED`, `RECONCILED`, and `CONFLICT`.

Meanings:

- `ABSENT`: inspection proved the intended effect did not land; same-operation retry is permitted only after authority/currentness refresh outside WIP.
- `RECONCILED`: inspection proved the intended effect already exists and was safely adopted without repeating it.
- `CONFLICT`: inspection found divergent state; stop rather than overwrite.

`PREPARED`, `ATTEMPTED`, and `AMBIGUOUS` are unresolved. `ABSENT` is resolved-as-absent but retryable. `CONFLICT` is terminal but attention-requiring.

### H6 — End-to-end qualification

Unit tests are necessary but insufficient. The repository must include deterministic end-to-end tests covering the failure modes WIP exists to solve.

Required scenarios:

1. **Effect landed, message died**
   - start workspace;
   - checkpoint;
   - append PREPARED;
   - simulate external effect landing;
   - simulate runtime death before terminal operation event;
   - fresh recovery detects unresolved operation;
   - inspect external target;
   - append RECONCILED without duplicating effect;
   - checkpoint and advance projections;
   - full validation passes.

2. **Effect did not land**
   - append PREPARED/ATTEMPTED;
   - simulate missing target;
   - append ABSENT;
   - retry same operation identity after simulated authority refresh;
   - append ATTEMPTED then VERIFIED;
   - full validation passes.

3. **Concurrent stale writer**
   - workers A and B both observe generation N;
   - B advances to N+1;
   - A attempts mutation using expected generation N;
   - A is rejected and must refresh;
   - B's state remains intact.

4. **Schema drift rejection**
   - add an undeclared property or malformed record that the JSON Schema forbids;
   - repository validation must fail.

5. **Cross-workspace contamination rejection**
   - place a valid-looking operation/checkpoint with a foreign `workspace_id` in another workspace;
   - validation must fail.

6. **Public/private storage-policy rejection**
   - place a PRIVATE or non-public storage profile under this public root;
   - repository validation must fail without inspecting/copying any private payload.

## Projection and generation semantics

Every operation that changes HEAD increments `generation` exactly once. A mutation function receives the generation the caller observed. If the live generation differs, it fails with a stale-generation error before appending or replacing anything.

Workspace creation establishes generation 0. The first checkpoint or operation transition advances it to generation 1.

RESUME is rebuilt from authoritative workspace records after projection-changing mutations. It is not historical truth.

## Durable ordering

Checkpoint ids remain monotonic six-digit ids (`cp-000001`, ...).

Operation ids remain monotonic six-digit ids (`op-000001`, ...). Each operation transition is a separate immutable event using an event filename that carries operation id, sequence, and state. Reusing an operation id after `ABSENT` is required for the retry path; it does not create a second logical operation.

## Recovery status model

`status` / `resume` output distinguishes:

- unresolved operations: PREPARED / ATTEMPTED / AMBIGUOUS;
- retryable-absent operations: ABSENT;
- terminal conflicts: CONFLICT;
- completed operations: VERIFIED / FAILED / RECONCILED.

A fresh worker must reconcile unresolved operations before unrelated forward mutation of that workspace.

## Privacy and authority boundaries

WIP stores continuity evidence, not permission. Resume never auto-renews credentials, consent, merge authority, deployment authority, or mutable external-currentness claims.

Private storage support is architectural portability, not permission to exfiltrate data. A worker may persist only material permitted for the configured target storage class.

## Acceptance criterion

WIP V1 hardening is mission-ready only when:

- strict schema + cross-record validation passes;
- first-class mutation commands are exercised by tests;
- storage recursion is explicitly closed;
- public/private storage policy is enforced;
- effect-present, effect-absent, and stale-concurrency end-to-end scenarios all pass from a clean checkout;
- the final branch head has a fresh green CI run;
- no merge-to-main claim is made without separate merge authority.
