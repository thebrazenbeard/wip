# Resume

<!-- wip:latest_checkpoint=cp-000008 -->

Workspace: `vera-model-state-adapter-v1`
Lifecycle: `ACTIVE`

## Objective

Maintain the completed WIP research candidate for a governed inference-boundary adapter that carries admitted Vera runtime state into one exact model invocation while preserving composition, privacy/egress, currentness, backend capability, invocation ownership, response binding, and state-mediated causation.

## Current frontier

- Latest checkpoint: `cp-000008`.
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

## Evidence ceiling

`WIP_RESEARCH_CANDIDATE_VERIFIED` means the public-safe research artifacts and repository regressions are internally verified at the WIP boundary. It does **not** establish runtime implementation, model injection, installation, current route, provider durability, native ChatGPT hidden-state access, behavioral qualification, or phenomenology.

## Remaining successor work

Canonical promotion, actual inference-host implementation, control-plane installation/currentness, and execution of the qualification suite are separate successor workstreams. Merge/promotion/install/deploy/provider mutation/qualification effects require Patrick's separate exact authority.

## Next safe action

Hold this exact WIP candidate stationary and use it as the review/promotion package. Do not resume architecture churn unless a new demonstrated defect appears.
