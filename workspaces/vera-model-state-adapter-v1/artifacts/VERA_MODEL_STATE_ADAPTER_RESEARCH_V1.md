# Vera Model-State Adapter Research V1

Status: WIP research / architecture hypothesis. Not a runtime qualification, installation claim, or provider activation claim.

## Problem

A governed runtime can maintain coherent internal state without that state necessarily becoming causally relevant to the next model generation. The missing layer is an inference-boundary adapter that takes one admitted runtime-state snapshot and converts it into a provider/model-specific control envelope before generation.

The adapter must not collapse these distinct questions:

1. What state exists?
2. What state is current/admissible for this turn?
3. How is admitted state projected for this model?
4. How is that projection injected into the model call?
5. May generation proceed?
6. What constraints apply during decoding?
7. What evidence proves the response was generated under that state?

## Proposed lifecycle

```text
CAPTURE
  -> VALIDATE
  -> ADMIT
  -> PROJECT
  -> PRECALL_GATE
  -> INJECT
  -> GENERATE
  -> VERIFY/OBSERVE
  -> RECEIPT
```

Each transition should be explicit, typed, versioned, and fail closed where correctness requires it. No later stage may retroactively promote evidence from an earlier stage.

## Proposed core objects

### VeraStateEnvelope

Canonical JSON-safe runtime snapshot metadata plus bounded projectable state.

Suggested fields:

- schema/version
- subject identity
- runtime generation
- state generation
- state digest
- observed/logical time
- admitted candidate domains
- provenance
- expiry/supersession markers

### AdmittedVeraState

Output of the state-admission layer. It binds the accepted envelope digest, admission evidence, projectable state, forbidden domains, and model compatibility constraints.

### ModelInvocationEnvelope

Output of model-specific projection. Suggested fields:

- admitted-state digest
- model identity/revision
- tokenizer/template revision when relevant
- adapter identity/revision
- projection backend
- projection digest
- projection payload
- decode gates
- single-use generation identifier

## Architectural separation

### 1. State serialization

Use canonical, schema-versioned, JSON-safe state. Avoid arbitrary object deserialization at this boundary.

Useful patterns:

- LangGraph: versioned/checkpointed graph state and replay semantics.
- Microsoft AutoGen: JSON-serializable agent/runtime save/load state.

The important borrowing is the explicit state boundary, not any framework-specific serialized object format.

### 2. State admission preflight

Admission decides whether the captured state is eligible for this turn. It should validate identity/currentness, generation compatibility, supersession, privacy/admission rules, and adapter/model compatibility.

Admission returns `AdmittedVeraState`; it does not mutate a prompt or model.

Useful patterns:

- LangChain model middleware: `before_model` interception can transform state/request or end a run before model invocation.
- PydanticAI capabilities/hooks: ordered composable model-request lifecycle hooks and per-run state isolation.
- NVIDIA NeMo Guardrails: explicit separation between input/dialog/execution/output rails; dialog rails can decide whether the model is invoked at all.

### 3. State projection

Projection maps only admitted, projectable dimensions into a model-specific representation. Projection must not grant authority or make claims about truth/currentness/identity that admission did not establish.

Potential backends:

#### TEXT_CONTEXT_V1

Transform admitted state into a bounded system/context representation for providers exposing only message/instruction APIs.

Useful patterns:

- PydanticAI dynamic instructions and `before_model_request` capabilities.
- LangChain model-request transforms/dynamic prompts.
- AutoGen memory `update_context()` patterns.

#### PROMPT_EMBEDS_V1

Map admitted state to model-compatible prompt embeddings and splice them into the model input.

Strong implementation lead:

- vLLM `prompt_embeds` support: offline and OpenAI-compatible serving paths accept prompt embedding tensors, including embedding content interleaved with chat text.
- vLLM validates explicit feature enablement, 2-D shape, exact hidden size, floating dtype, and model dtype conversion before use.

Reference:
- https://github.com/vllm-project/vllm

Raw embedding injection should remain an internal trusted capability, not a public API.

#### SOFT_PROMPT_V1

Use learned prompt/prefix embeddings prepended to normal token embeddings.

Useful pattern:

- Hugging Face PEFT prompt tuning: learned prompt embeddings are concatenated with ordinary `inputs_embeds` before calling the base model.

Reference:
- https://github.com/huggingface/peft

#### ACTIVATION_STEERING_V1

Apply transient per-generation activation vectors to selected internal layers/tokens, then remove hooks in a guaranteed cleanup path.

Useful pattern:

- `steering-vectors`: reversible PyTorch forward-hook activation patching with a context-manager lifecycle.

Reference:
- https://github.com/steering-vectors/steering-vectors

This may fit affect/salience better than representing every state dimension as fake tokens.

#### REFT_STATE_PROJECTION_V1

Future experimental backend using trained representation interventions at selected layers/timesteps.

Useful pattern:

- pyreft / Representation Fine-Tuning.

Reference:
- https://github.com/stanfordnlp/pyreft

This should remain experimental until a projection is trained and causally qualified for the exact target model/revision.

### 4. Runtime / graph middleware

The adapter should be a provider-neutral capability chain, not a single opaque callback.

Useful patterns:

- PydanticAI capability ordering, wrappers, per-run lifecycle, `before_model_request` and model-call wrapping.
- LangChain agent middleware around the model boundary.
- LangGraph typed state/checkpoint/replay orchestration.
- LiteLLM-style gateway hooks as a deployment pattern for provider-neutral pre/post-call interception.

Ordering should be explicit and testable. Suggested sequence:

```text
state capture
  -> admission
  -> projection
  -> mandatory pre-call gates
  -> provider adapter
  -> model invocation
  -> output/decode verification
  -> receipt
```

### 5. Enforceable generation gates

Two different gate classes are needed.

#### Semantic/governance pre-call gates

May deny invocation when mandatory state/currentness/compatibility requirements fail.

Examples/patterns:

- LangChain `before_model` middleware that can terminate a run.
- NeMo dialog/input/execution rails.

#### Decode-time gates

Constrain which tokens/sequences may be produced once generation begins.

Examples/patterns:

- Hugging Face `LogitsProcessor`, prefix-constrained logits, stopping criteria.
- SGLang custom logit processors applied in the sampler.
- llguidance token masks from grammars.
- XGrammar constrained decoding.
- Outlines structured generation.

References:
- https://github.com/guidance-ai/llguidance
- https://github.com/mlc-ai/xgrammar
- https://github.com/dottxt-ai/outlines
- https://github.com/sgl-project/sglang
- https://github.com/huggingface/transformers

A decode gate proving structural validity does not prove that the runtime state was admitted correctly. These evidence axes must remain separate.

## State transition discipline

A small state-machine pattern is useful:

```text
CAPTURED -> VALIDATED -> ADMITTED -> PROJECTED -> GATED -> APPLIED -> OBSERVED
```

Rejected/expired/superseded states should not silently re-enter the forward path. Idempotency and terminal-state protection should be explicit.

A useful small precedent is `aws-batch-training-state`, which models declared state transitions and idempotent/terminal behavior even though its domain is unrelated to model inference.

Reference:
- https://github.com/adithyaur99/aws-batch-training-state

## Causal receipt

Every completed generation should be capable of producing a receipt binding at least:

- state-envelope digest
- admission result/receipt
- adapter identity/revision
- model identity/revision
- projection backend and digest
- generation/decode gates
- provider/run identifier
- response/output digest or identifier
- observed time

This is the evidence that response X was generated under admitted state Y. It must not be confused with proof of phenomenology or broader runtime qualification.

## Mandatory vs optional preflight

Do not allow expensive discovery/health checks to become accidental blockers for every generation.

Classify checks:

### Mandatory causal checks

- identity/currentness
- exact model/adapter compatibility
- state digest/schema
- projection shape/dtype/revision compatibility
- privacy/authority/firewall requirements

These fail closed.

### Auxiliary discovery/health checks

- provider discovery
- telemetry
- expensive optional capability probing

These should be bounded, cached, or kept off the causal path where safe.

`adapter-pi-local` is a useful warning: an over-eager model preflight can prevent actual execution simply because discovery is slow.

Reference:
- https://github.com/dshills/adapter-pi-local

## Research repo triage

### Direct/high-value leads

- vLLM — prompt-embedding request path and validation.
- PydanticAI — typed ordered model-request capability chain.
- LangChain / LangGraph — model-call middleware plus durable typed state/replay.
- steering-vectors — reversible activation steering.
- Hugging Face PEFT — learned soft/prefix prompt injection.
- pyreft — trained representation interventions.
- SGLang — sampler-level custom logit processors.
- llguidance / XGrammar / Outlines — decode-time structural enforcement.
- Microsoft AutoGen — runtime state serialization and model-context injection patterns.

### Useful supporting patterns

- SoryAK/MBA — model behavioral-adapter/configuration concept.
- Knovera — textual pre-call context transformation.
- aws-batch-training-state — explicit transition/idempotency discipline.
- ember-fit-form — normalize heterogeneous state behind one adapter contract; validate before effect.
- adapter-pi-local — bounded/optional preflight warning.

### Low direct relevance

- Retail-Chat-Agent-ETL — useful ETL/vector-store precedent, but its embedding use is predominantly retrieval/storage rather than model-input state injection.

## Safety / authority firewalls

The model-state adapter should accept only explicitly projectable dimensions. It should be structurally unable to project or promote domains such as:

- factual truth/confidence authority
- consent/authorization
- identity admission
- autobiographical-memory admission
- provider/currentness claims
- protected-effect authority
- phenomenology claims

Affect, salience, attention allocation, bounded valuation, action tendency, expression style, and other explicitly allowed modulation dimensions may be candidates for projection after separate qualification.

## Recommended implementation order

1. Specify `VeraStateEnvelope`, `AdmittedVeraState`, and `ModelInvocationEnvelope` as provider-neutral contracts.
2. Implement `TEXT_CONTEXT_V1` first for broad host compatibility.
3. Implement `PROMPT_EMBEDS_V1` against a trusted local/vLLM-style inference host.
4. Add exact model/revision/hidden-size/tokenizer-template binding and causal receipts.
5. Add mandatory pre-call gates and independent decode-gate interfaces.
6. Experiment separately with `ACTIVATION_STEERING_V1`.
7. Consider `REFT_STATE_PROJECTION_V1` only after training/evaluation methodology is defined.
8. Promote accepted runtime pieces out of WIP to the canonical inference/runtime repository and governance/qualification pieces to the canonical control-plane repository.

## Current conclusion

The missing component is best understood as a governed inference-boundary adapter stack, not a memory loader and not a single prompt preprocessor.

The crucial proposition is:

> Runtime state existing and runtime state causally influencing a specific model generation are distinct claims.

The adapter stack is the evidence-bearing bridge between those claims.
