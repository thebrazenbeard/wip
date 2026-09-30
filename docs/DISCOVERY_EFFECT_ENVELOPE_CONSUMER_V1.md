# Discovery Effect Envelope Consumer — WIP V1

Status: **SOURCE EXPERIMENT / ONE-WAY INTERCHANGE ONLY**

Exact WIP source subject:

`main@12a7c23dbe0482fd7bfe63659e54526778efef1e`

WIP's operation journal already separates prepare, attempt, verification,
ambiguity, failure, and reconciliation. This adapter translates those native
states into Discovery's experimental neutral effect-attempt vocabulary without
changing WIP's recovery protocol.

Mapping:

- `PREPARED` → `PRE_EFFECT`
- `ATTEMPTED` → `POST_EFFECT_UNVERIFIED`
- `VERIFIED` → `POST_EFFECT_VERIFIED`
- `FAILED` → `TERMINAL_FAILURE`
- `AMBIGUOUS` → `OUTCOME_UNKNOWN`
- `RECONCILED` → `RECONCILED`

Native effect receipts/readback remain native evidence and are copied only as
neutral receipt values. The envelope never authorizes a retry or reconciliation.

The adapter imports no Discovery runtime package and WIP continues to operate
without Discovery.
