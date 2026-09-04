# Workspace Lifecycle Protocol V1

WIP owns unfinished continuity, not permanent canonical artifacts.

## States

Nonterminal:

- `ACTIVE` — work is expected to continue.
- `PAUSED` — intentionally dormant but resumable.

Terminal:

- `PROMOTED` — work became canonical somewhere else.
- `SHELVED` — preserved for possible future use with no current continuation expectation.
- `SUPERSEDED` — another workspace/project replaced this one.
- `ABANDONED` — explicitly discontinued.

There is no `DONE` state.

## Why no DONE

Completion is ambiguous: a prototype can be complete as a prototype while still being unfinished as a product. WIP therefore records disposition rather than pretending to own an absolute notion of completion.

A successful project normally exits WIP via `PROMOTED` and records the canonical destination.

## Terminal record

A terminal workspace SHOULD create `exit/EXIT.json` containing:

- workspace id;
- terminal lifecycle;
- final checkpoint id;
- final WIP HEAD generation;
- destination locator and immutable identity when `PROMOTED` or `SUPERSEDED`;
- disposition summary;
- timestamp.

After terminal disposition, ordinary tool work MUST NOT continue under that workspace id. Reopening genuinely new work requires a new workspace or an explicit lifecycle-extension design added in a later protocol version.

## Registry

`registry/workspaces.json` is an index/projection for discovery. It may be updated as lifecycle changes, but it is not the historical authority for why the change occurred. The workspace's append-only checkpoint/operation history and terminal record preserve that lineage.