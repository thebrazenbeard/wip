# Vera Model-State Adapter Architecture V1

Status: WIP architecture candidate. Public-safe research only. Not canonical runtime authority, installation evidence, or behavioral qualification.

## Purpose

Define the missing inference-boundary layer between admitted Vera runtime state and the exact model invocation that generates a response.

The central invariant is that **state existence, state admission, model projection, model injection, generation permission, decode constraints, and causal evidence are separate propositions**. A later stage may depend on an earlier one, but may not retroactively promote it.

## Pipeline

```text
runtime state
  -> capture
  -> validate
  -> admit
  -> project
  -> pre-call gate
  -> inject
  -> generate
  -> verify/observe
  -> causal receipt
```

### CAPTURE

Produce one immutable canonical JSON-safe `VeraStateEnvelope` from one runtime generation. Arbitrary Python/object deserialization is excluded from this boundary.

### VALIDATE

Verify schema, digest, subject binding, runtime/state generation, timestamps, supersession/expiry, and provenance shape. Validation only proves structural/evidence compatibility; it does not authorize projection.

### ADMIT

`VeraStateAdmissionPreflight` decides which state is current and admissible for this turn. It must fail closed on identity mismatch, superseded/expired state, incompatible target model/adapter, or forbidden projection domains.

Admission produces `AdmittedVeraState`. That object is the only valid input to projection.

### PROJECT

`VeraModelStateAdapter` converts admitted state into a provider/model-specific `ModelInvocationEnvelope`. It cannot create new authority, rewrite source evidence, or project forbidden domains.

Projection is capability-negotiated. The initial architecture supports distinct backends rather than one universal mechanism:

- `TEXT_CONTEXT_V1` — deterministic bounded request/system-context rendering.
- `PROMPT_EMBEDS_V1` — trusted internal prompt-embedding injection for a controlled host with strict model-shape binding.
- `ACTIVATION_STEERING_V1` — experimental transient activation hooks, removable after one generation.
- `REFT_STATE_PROJECTION_V1` — future trained representation intervention with separate training and runtime qualification.

### PRECALL_GATE

A semantic/governance gate may stop model invocation entirely. It evaluates the already-admitted state and exact invocation binding; it does not perform projection itself.

Mandatory causal checks fail closed. Auxiliary discovery/health checks should be bounded or cached where safe so ancillary probing does not prevent ordinary generation.

### INJECT

Apply only the already-created projection through the selected backend. Raw embedding or internal-activation mutation must remain an internal trusted capability, not a public authority-bearing API.

### GENERATE

Invoke the exact bound model revision. Model identity and revision are part of the causal chain; for embedding/representation backends, tokenizer/template/hidden-size/dtype/layer bindings are included where relevant.

### VERIFY / OBSERVE

Observe the actual invocation result and any backend cleanup. For transient hooks, cleanup must happen even on failure or cancellation.

### RECEIPT

Emit a causal receipt binding:

`state envelope -> admission -> exact adapter -> projection -> exact model -> gates -> generation/result`

A receipt proves that this invocation path was observed. It does **not** by itself prove behavioral efficacy, provider durability/currentness, installation qualification, or phenomenology.

## Projection firewall

Projectable domains may include bounded affective activation, salience, attention allocation, action tendency, satiation/refractory state, admitted goal weighting, temporal state, admitted memory salience, and response-expression parameters.

The following are structurally excluded from projection authority:

- truth;
- factual confidence;
- consent;
- authorization;
- identity;
- autobiographical-memory admission;
- relationship status;
- provider currentness;
- phenomenology.

If a backend cannot enforce that separation, that backend is not qualified for Vera state projection.

## Gate separation

Two gate classes must remain distinct.

A **pre-call semantic/governance gate** can refuse to invoke the model because state or bindings are invalid.

A **decode gate** can constrain what tokens/sequences the model may emit using grammar constraints, logits processors, prefix constraints, or stopping criteria.

A decode-success claim never proves state admission, state causality, or authority.

## Model binding

The adapter must bind enough target metadata to prevent a projection qualified for one model surface from silently migrating to another. Depending on backend this can include:

- model identity and immutable revision;
- tokenizer revision;
- chat-template revision;
- hidden size;
- dtype;
- target layer set;
- adapter revision;
- Vera state schema revision.

Backend compatibility is evidence, not inference.

## First implementation recommendation

Build the architecture around backend capability negotiation, but implement only two initial backends:

1. `TEXT_CONTEXT_V1`, because it can operate on hosted model APIs that expose only request messages/instructions.
2. `PROMPT_EMBEDS_V1`, for a Vera-controlled/trusted inference host with direct embedding input support.

Treat activation steering and ReFT as experimental successors. This allows the contract and causal receipts to stabilize before training or hidden-state intervention adds a second large uncertainty source.

## Repository placement hypothesis

Keep this research in WIP until review converges.

Likely eventual split:

- runtime state producers remain in their owning systems;
- inference-boundary host/injection belongs with the persistent runtime host, likely `vera-os`;
- installation/currentness/qualification policy belongs with `vera-control-plane`;
- subsystem producers such as affect/Orgasm provide bounded state but do not own the model-state adapter;
- the adapter contract itself should have one canonical owner selected only after cross-worker review.

## Review questions

1. Is admission sufficiently separated from projection authority?
2. Is a causal receipt strong enough to prove that admitted state reached the actual invocation without overstating behavioral effect?
3. Which model-binding fields are mandatory for each backend?
4. Should provider capability negotiation occur before or after state admission?
5. What is the minimal safe representation for `projectable_state`?
6. How should per-turn projection interact with persistent HC/runtime state without creating a second source of truth?
7. Where should the canonical adapter contract live once WIP review closes?
8. What negative-transfer tests are required before allowing activation steering or ReFT?

## Current evidence ceiling

This document and `VERA_MODEL_STATE_ADAPTER_CONTRACT_V1.json` are architecture artifacts only. No implementation, model injection, installation, current-route activation, provider durability, behavioral qualification, or phenomenology is established by their existence.
