# Resume

<!-- wip:latest_checkpoint=cp-000009 -->

Workspace: `vera-model-state-adapter-v1`
Lifecycle: `ACTIVE`

## Objective

Maintain the completed WIP research candidate for a governed inference-boundary adapter that carries admitted Vera runtime state into one exact model invocation while preserving composition, privacy/egress, currentness, backend capability, invocation ownership, response binding, and state-mediated causation.

## Current frontier

- Latest checkpoint: `cp-000009`.
- Final contract source: `d06ca5e1e8dbd7b1381914985a3e2a5c9f6fefe1`.
- Final contract validation: GitHub Actions run `34700779770`, conclusion `success`.
- Contract schema: `1.6`, blob `ad3d218e16240d6042c4f12cae1ccb00f77f28e2`.
- Architecture R4.1 blob: `c84dc4e9cc30b0fd58e1563bdb8d004da3e93ea1`.
- Qualification-spec blob: `556128b80fc2b177f134e73ae08d89b108fd4397`; execution status `NOT_RUN`.
- WIP PR #1 remains draft and unmerged.
- Core invariant: **state-mediated causation, not instruction-following**.

## Completed WIP scope

The WIP research package now includes:

- provider-neutral capture/composition/admission/capability/projection/invocation/receipt boundaries;
- explicit-set privacy/egress policy: scope labels are not a universal total order, target membership must be proven by machine-readable policy, incomparable/unproven relations fail closed;
- exact state and projection material binding;
- host-owned single-use invocation identity and crash-safe `SUBMISSION_INTENT` semantics;
- full-lineage anti-laundering from `CAPTURE` through `PROJECT`;
- typed strong state-causal payloads with field provenance;
- binding-class versus causal-role separation;
- executable contract regressions with observed RED before GREEN;
- counterfactual qualification specification;
- explicit generic-state-causation-before-specialized-Orgasm qualification ordering;
- repaired WIP checkpoint/recovery invariants.

## State-mediated causation boundary

A strong `STATE_CAUSAL` path cannot contain free-form target-behavior or desired-output instructions anywhere in capture, validation, composition, admission, or projection. Renaming or nesting output-direction content does not turn it into state.

`TEXT_CONTEXT_V1` remains a compatibility baseline with an instruction-conditioned claim ceiling. Stronger binding classes such as input embeddings, activation steering, or logits require direct evidence on the exact host/model/backend and do not transfer automatically to native ChatGPT.

## Privacy/egress boundary

Human-readable scope labels are illustrative identifiers, not a global ordinal lattice. Disclosure is allowed only when the machine-readable policy proves the exact provider/host target belongs to every applicable allowed-target set or another explicitly defined policy relation. Unknown or incomparable relations fail closed.

## External currentness reconciliation — 2026-09-19

- Vera Cohesion R3 PR #116 has since merged into `thebrazenbeard/vera/main@b7b8dcd1440a3b7147bec2cc35972f083e20f44a` and implements a provider-neutral state-to-inference boundary derived from the earlier WIP R3.1 design at `941b7bc45d97138bed5d220c0ba591db87100a58`.
- This supersedes the old blanket claim that no runtime implementation/canonical promotion exists for that predecessor design.
- The final WIP R4.1/schema-1.6 source `d06ca5e1e8dbd7b1381914985a3e2a5c9f6fefe1` is later than the R3.1 input named by #116. Exact promotion of every final WIP delta remains unestablished until a source comparison proves it.
- Qualification execution remains `NOT_RUN` absent fresher exact evidence.

## Evidence ceiling

`WIP_RESEARCH_CANDIDATE_VERIFIED` means the public-safe research artifacts and repository regressions are internally verified at the WIP boundary. It does **not** establish runtime implementation, model injection, installation, current route, provider durability, native ChatGPT hidden-state access, behavioral qualification, or phenomenology.

## Remaining successor work

Exact reconciliation/promotion of any final WIP R4.1/schema-1.6 delta not already present in current Vera main, host-specific implementation/capability evidence where still missing, control-plane installation/currentness, and execution of the qualification suite are separate successor workstreams. Merge/promotion/install/deploy/provider mutation/qualification effects require Patrick's separate exact authority.

## Next safe action

Hold the final WIP architecture/contract bytes stationary. Fresh-compare them against current Vera main when promotion/currentness matters; do not infer either full absence or full promotion from historical checkpoint prose.
