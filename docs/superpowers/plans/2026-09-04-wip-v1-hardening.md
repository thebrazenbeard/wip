# WIP V1 Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden WIP V1 into a strict, ergonomic, crash-qualified recovery substrate while preserving the existing checkpoint/effect-journal architecture.

**Architecture:** Keep the repository's append-only historical records plus mutable projections. Make the published schemas executable through a focused standard-library validator, add local mutation primitives/CLI commands with expected-generation concurrency, close WIP-storage recursion explicitly, add storage-class policy, repair the effect state machine with `ABSENT`/`CONFLICT`, then qualify the whole path with end-to-end crash recovery tests.

**Tech Stack:** Python 3 standard library, JSON/Markdown, GitHub Actions, unittest.

**Spec:** `docs/superpowers/specs/2026-09-04-wip-v1-hardening-design.md`

## Global Constraints

- No third-party Python dependencies.
- Historical checkpoint and operation-event records remain append-only.
- WIP continuity never grants external authority.
- Public reference repository live workspace payloads remain `PUBLIC_SAFE` only.
- WIP's own persistence writes are a non-recursive storage primitive.
- Every projection-changing mutation after workspace creation requires an expected HEAD generation.
- Do not merge this hardening branch to `main` without separate merge authority.

---

### Task 1: Encode the hardening failures as tests

**Files:**
- Modify: `tests/test_wip.py`
- Create: `tests/test_wip_e2e.py`

**Interfaces:**
- Consumes: current `tools.wip.validate_workspace`, `validate_repository`, `inspect_workspace`.
- Produces: executable acceptance expectations for strict schema validation, cross-workspace identity, mutation APIs, stale-generation rejection, storage policy, and crash recovery.

- [ ] **Step 1: Add failing strict-validation tests**

Add tests that construct a valid temporary workspace, then prove validation rejects:

```python
workspace["unexpected"] = True
```

and an operation/checkpoint whose `workspace_id` is different from the containing `WORKSPACE.json`.

- [ ] **Step 2: Add failing mutation/concurrency tests**

Import the planned API:

```python
from tools.wip import (
    StaleGenerationError,
    append_checkpoint,
    append_operation_event,
    start_workspace,
)
```

Test that `start_workspace` creates generation 0, a checkpoint advances the generation exactly once, and a second mutation using the stale generation raises `StaleGenerationError` without changing the winning state.

- [ ] **Step 3: Add failing storage-policy test**

Create a repository policy fixture and a live workspace with `privacy_class="PRIVATE"` / `storage_profile="PRIVATE_GITHUB"` under a public root. Assert repository validation rejects it.

- [ ] **Step 4: Add failing end-to-end crash tests**

In `tests/test_wip_e2e.py`, model:

```text
start -> checkpoint -> PREPARED -> external effect lands -> death
-> inspect -> RECONCILED -> checkpoint -> validate
```

and:

```text
PREPARED -> no effect -> ABSENT -> ATTEMPTED -> effect lands
-> VERIFIED -> validate
```

Assert the first path does not execute the external effect twice and the second reuses the same operation id.

- [ ] **Step 5: Run tests and verify RED**

Run:

```bash
python -m unittest discover -s tests -v
```

Expected: failures/import errors for missing hardening behavior. Do not weaken tests to regain green.

- [ ] **Step 6: Commit tests-only RED state**

```bash
git add tests/test_wip.py tests/test_wip_e2e.py
git commit -m "test: define WIP hardening qualification"
```

### Task 2: Make JSON schemas executable contracts

**Files:**
- Modify: `tools/wip.py`
- Modify: `schemas/workspace.schema.json`
- Modify: `schemas/operation-event.schema.json`
- Create: `storage/REPOSITORY_POLICY.json`
- Create: `schemas/repository-policy.schema.json`

**Interfaces:**
- Produces: `validate_json_schema(instance, schema, path="$") -> list[str]`, `load_schema(root, name)`, strict record validation, repository storage-policy validation.

- [ ] **Step 1: Implement the focused schema validator**

Support the exact keywords enumerated by the hardening spec. Date-time validation should accept RFC3339 timestamps with `Z` or an explicit offset using standard-library parsing.

- [ ] **Step 2: Route all WIP records through schemas**

Before cross-record checks, validate:

```text
WORKSPACE.json -> workspace.schema.json
HEAD.json -> head.schema.json
checkpoints/*.json -> checkpoint.schema.json
operations/*.json -> operation-event.schema.json
storage/REPOSITORY_POLICY.json -> repository-policy.schema.json
```

- [ ] **Step 3: Add cross-record identity checks**

Require record body workspace ids to equal the containing workspace id, and filename ids to equal record-body ids.

- [ ] **Step 4: Add storage profile fields/policy**

Change workspace schema from hard-coded `PUBLIC_SAFE` to:

```json
"privacy_class": {"enum": ["PUBLIC_SAFE", "PRIVATE"]},
"storage_profile": {"enum": ["PUBLIC_GITHUB", "PRIVATE_GITHUB", "PRIVATE_PROVIDER"]}
```

and create a root policy that identifies this repository as `PUBLIC_REFERENCE` permitting only `PUBLIC_SAFE` + `PUBLIC_GITHUB` live payloads.

- [ ] **Step 5: Run strict-validation tests**

Run the targeted new validation tests and confirm they pass while end-to-end mutation tests remain red.

- [ ] **Step 6: Commit**

```bash
git add tools/wip.py schemas storage tests
git commit -m "feat: enforce WIP schemas and storage policy"
```

### Task 3: Repair the operation state machine

**Files:**
- Modify: `schemas/operation-event.schema.json`
- Modify: `protocol/EFFECT_PROTOCOL.md`
- Modify: `protocol/RECOVERY_PROTOCOL.md`
- Modify: `tools/wip.py`
- Modify: `templates/OPERATION_EVENT.json`

**Interfaces:**
- Produces: legal transition validation for `ABSENT` and `CONFLICT`; status classification of unresolved/retryable/conflicted/completed operations.

- [ ] **Step 1: Add states to schema**

Allowed states become:

```text
PREPARED ATTEMPTED VERIFIED FAILED AMBIGUOUS ABSENT RECONCILED CONFLICT
```

- [ ] **Step 2: Implement legal-transition table**

Use the transition graph from the hardening spec. Reject state skips that are not explicitly allowed and reject events after terminal states.

- [ ] **Step 3: Update inspection/status classification**

Return separate collections for:

```text
unresolved: PREPARED/ATTEMPTED/AMBIGUOUS
retryable_absent: ABSENT
conflicts: CONFLICT
completed: VERIFIED/FAILED/RECONCILED
```

- [ ] **Step 4: Rewrite effect/recovery docs to match executable semantics**

Document same-operation retry only from `ABSENT` after fresh authority/currentness checks.

- [ ] **Step 5: Run transition tests**

Confirm valid ABSENT retry passes and invalid terminal-state continuation fails.

- [ ] **Step 6: Commit**

```bash
git add schemas/operation-event.schema.json protocol tools/wip.py templates/OPERATION_EVENT.json tests
git commit -m "fix: close ambiguous-effect recovery state machine"
```

### Task 4: Add mutation primitives and CLI commands

**Files:**
- Modify: `tools/wip.py`
- Modify: `templates/WORKSPACE.json`
- Modify: `templates/HEAD.json`
- Modify: `templates/CHECKPOINT.json`
- Modify: `templates/RESUME.md`
- Modify: `integration/CHATGPT_INSTRUCTIONS.md`

**Interfaces:**
- Produces:
  - `start_workspace(...) -> Path`
  - `append_checkpoint(..., expected_generation: int, ...) -> dict`
  - `append_operation_event(..., expected_generation: int, ...) -> dict`
  - `render_resume(workspace_path) -> str`
  - `StaleGenerationError`
  - CLI subcommands in H2.

- [ ] **Step 1: Implement exclusive append helper**

Create append-only JSON using exclusive creation (`open(..., "x")`) so duplicate record paths fail instead of overwrite.

- [ ] **Step 2: Implement generation guard**

Read HEAD, compare exact current generation with caller's expected value, and raise `StaleGenerationError` before any mutation when they differ.

- [ ] **Step 3: Implement workspace creation**

Create directory structure, WORKSPACE, HEAD generation 0, RESUME, and optional registry entry using safe deterministic paths.

- [ ] **Step 4: Implement checkpoint mutation**

Generate next checkpoint id, append checkpoint, increment HEAD once, update latest checkpoint, rebuild RESUME, then validate the workspace.

- [ ] **Step 5: Implement operation-event mutation**

Generate/validate sequence, append event, increment HEAD once, update latest operation event, rebuild RESUME, then validate.

- [ ] **Step 6: Wire CLI commands**

Expose `start`, `checkpoint`, `prepare`, `attempted`, `verify`, `ambiguous`, `absent`, `reconcile`, `conflict`, and `resume` with explicit required arguments and non-zero exit on stale generation/invalid state.

- [ ] **Step 7: Run mutation/concurrency tests**

Verify stale writes fail before append and the winning generation remains intact.

- [ ] **Step 8: Commit**

```bash
git add tools/wip.py templates integration tests
git commit -m "feat: add WIP mutation and resume commands"
```

### Task 5: Close WIP-storage recursion in protocol and integration

**Files:**
- Modify: `protocol/WIP_PROTOCOL.md`
- Modify: `protocol/EFFECT_PROTOCOL.md`
- Modify: `integration/CHATGPT_INSTRUCTIONS.md`
- Modify: `README.md`

**Interfaces:**
- Produces: one unambiguous rule for WIP's own persistence writes versus external work effects.

- [ ] **Step 1: Document the persistence primitive**

State explicitly that WIP persistence does not journal itself recursively and instead uses deterministic paths, create-only append records, compare-and-swap projections, and read-after-ambiguous-result.

- [ ] **Step 2: Add remote-provider mapping**

Document GitHub create-only contents writes for append events and blob-SHA CAS for mutable projections. Keep adapters out of hardening scope.

- [ ] **Step 3: Update portable ChatGPT instructions**

Ensure agents do not attempt PREPARED-about-PREPARED recursion and know to inspect WIP storage after an ambiguous WIP write.

- [ ] **Step 4: Commit**

```bash
git add protocol integration/CHATGPT_INSTRUCTIONS.md README.md
git commit -m "docs: define non-recursive WIP persistence primitive"
```

### Task 6: Complete end-to-end qualification

**Files:**
- Modify: `tests/test_wip_e2e.py`
- Modify: `.github/workflows/validate.yml` only if test discovery does not already include the new suite.
- Modify: `README.md`

**Interfaces:**
- Consumes: all hardening APIs.
- Produces: executable evidence that WIP recovers landed/missing effects and rejects stale writers.

- [ ] **Step 1: Run full local suite**

```bash
python -m unittest discover -s tests -v
python tools/wip.py validate .
```

Expected: all tests PASS and repository validation says `OK`.

- [ ] **Step 2: Inspect failure-path assertions**

Confirm the effect-present test counts one external effect, the absent path reuses one operation id, and stale concurrency leaves winner state unchanged.

- [ ] **Step 3: Update README readiness language**

Describe what is now qualified and retain the limitation that native ChatGPT does not automatically intercept tool calls merely because the repository exists.

- [ ] **Step 4: Commit qualification changes**

```bash
git add tests .github/workflows/validate.yml README.md
git commit -m "test: qualify WIP crash and concurrency recovery"
```

- [ ] **Step 5: Verify branch CI from the final head**

Read the branch head, find the Actions run for that exact SHA, inspect its jobs/logs, and require fresh green evidence before claiming completion.

- [ ] **Step 6: Read back critical files from the final head**

Read back the hardening spec, `tools/wip.py`, operation schema, public storage policy, integration instructions, and tests. Compare them to the acceptance criteria.

- [ ] **Step 7: Stop before merge**

Leave `work/wip-hardening-v1-20260904` unmerged. Report exact branch head, verification evidence, remaining limitations, and whether the architecture now meets the mission-readiness bar.
