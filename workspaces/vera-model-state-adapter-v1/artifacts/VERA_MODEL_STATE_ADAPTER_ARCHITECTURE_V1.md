# Vera Model-State Adapter Architecture V1

Status: WIP architecture candidate. Public-safe research only. Not canonical runtime authority, installation evidence, or behavioral qualification.

## Purpose

Define the missing inference-boundary layer between admitted Vera runtime state and the exact model invocation that generates a response.

The central invariant is that **state existence, composition, admission, capability binding, projection, injection, generation permission, decode constraints, response binding, and causal evidence are separate propositions**. A later stage may depend on an earlier one, but may not retroactively promote it.

A second invariant is now explicit: **causation through state, not instruction-following**. The adapter may carry upstream state that changes the conditions under which a response is generated. It must not encode the desired downstream response as the causal mechanism.

## Pipeline

```text
runtime component states
  -> capture
  -> validate
  -> compose
  -> admit
  -> capability-bind
  -> project
  -> pre-call gate
  -> inject
  -> generate
  -> verify/observe
  -> causal receipt
```

### CAPTURE

Capture immutable canonical JSON-safe component state. Arbitrary Python/object deserialization is excluded from this boundary.

Every included state value must be exact-byte/addressable: either the payload itself is present or an exact pointer plus digest is bound.

### VALIDATE

Verify schema, digests, subject binding, component ownership/generation, timestamps, supersession/expiry, and provenance shape. Validation only proves structural/evidence compatibility; it does not authorize composition or projection.

### COMPOSE

Vera-wide state must not pretend that independently governed components came from one generation unless that is actually true.

Two composition modes are allowed:

1. `HOST_ATOMIC_SNAPSHOT`: one host-owned snapshot boundary captures all included domains under one exact snapshot generation.
2. `COMPONENT_GENERATION_VECTOR`: each component carries its owner, generation, payload digest, and observation frontier, and an explicit composition receipt reconciles them.

Incompatible or unreconciled component generations cannot be composed into one apparently coherent state envelope.

### ADMIT

`VeraStateAdmissionPreflight` decides which composed state is current and admissible for this turn.

Identity, subject/source integrity, currentness, supersession, composition integrity, and projection-firewall failures are mandatory fail-closed conditions.

Optional dimensions are different. If an optional affect, memory, conation, or similar dimension is unavailable, the adapter may omit it only with an explicit omission receipt. Optional-state loss must not silently become a total generation outage.

Admission produces `AdmittedVeraState`. That object is the only valid input to capability binding and projection.

### CAPABILITY_BIND

Before backend-specific materialization, bind the exact inference host and model capability surface.

The binding includes the exact host/model/adapter revisions, supported projection backends, and backend constraints. A requested backend does not prove the host supports it.

Fallback or downgrade is never silent. It requires explicit policy and a receipt.

### PROJECT

`VeraModelStateAdapter` converts admitted state into a provider/model-specific projection. It cannot create new authority, rewrite source evidence, or project forbidden domains.

The projection must be a deterministic function of:

`admitted state + declared backend mapping + exact capability binding`

It must **not** accept `target_behavior`, `desired_response`, `target_phrase`, `expected_answer`, or equivalent outcome labels as projection inputs.

That is the state-mediated-causation boundary. The adapter changes upstream state or modulation conditions; it does not say "produce outcome X" and then count compliance as evidence that the state caused X.

Projection backends remain distinct:

- `TEXT_CONTEXT_V1` — deterministic bounded declarative state context.
- `PROMPT_EMBEDS_V1` — trusted internal prompt-embedding injection for a controlled host with strict shape/model binding.
- `ACTIVATION_STEERING_V1` — experimental transient activation hooks.
- `REFT_STATE_PROJECTION_V1` — future trained representation intervention with separate training/runtime qualification.

`TEXT_CONTEXT_V1` is explicitly instruction-adjacent. It must not contain imperative target-behavior language, and it requires stronger negative controls before any state-causation claim.

### PRECALL_GATE

A semantic/governance gate may stop model invocation entirely. It evaluates the admitted state, exact capability binding, and completed projection; it does not perform projection itself.

Mandatory causal checks fail closed. Auxiliary discovery/health checks should be bounded or cached where safe.

### INJECT

Apply only the already-created projection through the bound backend. Raw embedding or internal-activation mutation remains an internal trusted capability, not a public authority-bearing API.

### GENERATE

Invoke the exact bound model revision. Depending on backend, the causal chain may also bind tokenizer revision, chat-template revision, hidden size, dtype, target layers, and adapter revision.

### VERIFY / OBSERVE

Observe what actually happened. For transient hooks, cleanup must happen on success, failure, and cancellation.

Hosted APIs may expose much weaker evidence than local inference. The architecture must preserve that difference rather than upgrading local request construction into proof of provider consumption.

### RECEIPT

Causal evidence is leveled:

- `REQUEST_CONSTRUCTED`: a bound request/projection was built locally.
- `INVOCATION_SUBMITTED`: that exact invocation was submitted.
- `PROVIDER_ACKNOWLEDGED`: the provider/host acknowledged the exact invocation identity where evidence exists.
- `RESPONSE_BOUND`: the returned response/run is explicitly linked to that exact generation request.

A receipt records the strongest level actually supported. A local projection digest cannot prove that an opaque provider consumed it.

Even `RESPONSE_BOUND` does not by itself prove behavioral effect, behavioral qualification, durability/currentness, installation status, or phenomenology.

## State-mediated causation qualification

A backend does not qualify merely because the resulting response looks like the state description.

Qualification requires, at minimum:

- projection derived only from admitted state plus the declared backend mapping;
- target behavior not supplied as an input to projection;
- matched state-on/state-off or dose-response comparisons;
- decay/recovery comparisons for temporal state;
- negative-transfer controls;
- an instruction-only control that cannot be counted as state-causal evidence;
- a behavioral-effect claim only when the response is bound to the same exact generation.

This is the practical distinction between changing the model's upstream conditions and simply asking it to behave a certain way.

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

A **pre-call semantic/governance gate** can refuse to invoke the model because state, composition, capability, or bindings are invalid.

A **decode gate** can constrain tokens/sequences using grammar constraints, logits processors, prefix constraints, or stopping criteria.

Decode success never proves state admission, state causality, or authority.

## Model and host binding

Backend compatibility is evidence, not inference. Depending on backend, bindings can include:

- host identity and revision;
- model identity and immutable revision;
- tokenizer revision;
- chat-template revision;
- hidden size;
- dtype;
- target layer set;
- adapter revision;
- Vera state schema revision.

Capability binding happens before expensive or privileged backend materialization.

## First implementation recommendation

Retain two initial backends, but treat them differently:

1. `TEXT_CONTEXT_V1` is a baseline compatibility backend for hosted APIs. It is useful for proving the lifecycle/receipts, but because it is instruction-adjacent it has a lower state-causation claim ceiling without strong controls.
2. `PROMPT_EMBEDS_V1` is the first stronger state-projection candidate for a Vera-controlled/trusted inference host.

Activation steering and ReFT remain experimental successors.

## Repository ownership hypothesis after Cohesion review

Keep this work in WIP until review converges, then promote by responsibility:

- provider-neutral state composition/admission/projection contract -> Vera/Cohesion source;
- host-specific injection/runtime hook -> `vera-os` or another exact inference host;
- install/current-route/qualification policy -> `vera-control-plane`;
- subsystem producers such as affect/Orgasm -> bounded state producers only, not owners of model invocation authority.

WIP remains staging, not canonical authority.

## Review questions

1. Is `HOST_ATOMIC_SNAPSHOT | COMPONENT_GENERATION_VECTOR` sufficient to prevent false cross-generation coherence?
2. Is the exact payload/pointer+digest contract strong enough for every projected dimension?
3. Are the causal evidence levels correctly bounded for opaque hosted APIs?
4. Is optional-state omission safe without weakening mandatory currentness/identity/firewall checks?
5. Does `CAPABILITY_BIND` happen at the correct point in the lifecycle?
6. Is the state-mediated-causation invariant enforceable enough to prevent "act like X" from qualifying as state causation?
7. Which backend/model binding fields are mandatory per backend?
8. What additional negative-transfer tests are required before activation steering or ReFT?

## Current evidence ceiling

This document and `VERA_MODEL_STATE_ADAPTER_CONTRACT_V1.json` are architecture artifacts only. No implementation, model injection, installation, current-route activation, provider durability, behavioral qualification, or phenomenology is established by their existence.
