# Resume

<!-- wip:latest_checkpoint=cp-000001 -->

Workspace: `vera-model-state-adapter-v1`
Lifecycle: `ACTIVE`

## Objective

Research and stage a governed inference-boundary model-state adapter that can carry admitted Vera runtime state into a specific model invocation without collapsing state existence, admission, projection, injection, generation gating, or causal evidence into one claim.

## Verified position

- Latest checkpoint: `cp-000001`
- Research synthesis is staged as `artifacts/VERA_MODEL_STATE_ADAPTER_RESEARCH_V1.md`.
- Work is isolated on branch `work/vera-model-state-adapter-v1-20260911` to avoid concurrent-writer collisions.
- WIP is staging only, not the eventual canonical runtime or control-plane authority.

## Already done

- Surveyed public patterns for JSON-safe runtime state, graph/checkpoint persistence, pre-model middleware, soft prompts, prompt embeddings, activation steering, representation interventions, sampler/logit control, constrained decoding, and guardrail/gate separation.
- Proposed the lifecycle `CAPTURE -> VALIDATE -> ADMIT -> PROJECT -> PRECALL_GATE -> INJECT -> GENERATE -> VERIFY/OBSERVE -> RECEIPT`.
- Identified `TEXT_CONTEXT_V1` and `PROMPT_EMBEDS_V1` as the first practical projection backends; activation steering/ReFT remain experimental successors.

## Unfinished

- Have concurrent Vera workers review and attack the architecture.
- Convert the research into machine-readable adapter contracts.
- Determine canonical promotion targets.
- Build and separately qualify each projection backend.

## Do not repeat

- Do not place protected/private project payloads into public WIP.
- Do not treat WIP research as installed/current runtime behavior.
- Do not treat runtime state existence as proof that the state influenced a model response.

## Next safe action

Open a draft WIP PR for this exact workspace commit, mirror the PR/research frontier to the communication bus, and request review/challenge from the concurrent Vera workers before promotion.
