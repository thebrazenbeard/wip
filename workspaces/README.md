# Live WIP Workspaces

This directory contains actual recoverable workspaces using WIP V1.

Each workspace lives at:

```text
workspaces/<workspace-id>/
```

Start from the records in `../templates/` and follow `../protocol/WIP_PROTOCOL.md`.

A live workspace must contain at least:

```text
WORKSPACE.json
HEAD.json
RESUME.md
checkpoints/
operations/
```

`WORKSPACE.json` is immutable after creation. Checkpoints and operation events are append-only. `HEAD.json` and `RESUME.md` are mutable projections updated with optimistic concurrency.

Because this repository is public, live workspaces may contain only `PUBLIC_SAFE` material. Store opaque references to protected external objects instead of copying sensitive contents here.

When work becomes canonical elsewhere, give the workspace a terminal lifecycle disposition (`PROMOTED`, `SHELVED`, `SUPERSEDED`, or `ABANDONED`) rather than treating WIP as the permanent source of truth.
