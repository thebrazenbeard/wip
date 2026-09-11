# Vera Model-State Adapter Architecture V1

Status: WIP architecture candidate. Public-safe research only. Not canonical runtime authority, installation evidence, or behavioral qualification.

## Purpose

Define the inference-boundary layer between admitted Vera runtime state and the exact model invocation that emits a response.

Two governing invariants:

1. **Evidence separation:** state existence, composition, privacy/egress, admission, capability binding, projection, invocation ownership, injection, generation, response binding, and behavioral effect are separate propositions.
2. **State-mediated causation:** change admitted upstream state or modulation conditions; do not encode the desired downstream response and then count instruction compliance as a state effect.

## Lifecycle

```text
CAPTURE
  -> VALIDATE
  -> COMPOSE
  -> ADMIT
  -> CAPABILITY_BIND
  -> PROJECT
  -> PRECALL_REVALIDATE_GATE
  -> INVOCATION_RESERVE
  -> INJECT
  -> GENERATE
  -> VERIFY/OBSERVE
  -> RECEIPT
```

### CAPTURE / VALIDATE / COMPOSE

Captured component state is canonical JSON-safe data or an exact immutable pointer+digest. Arbitrary object deserialization is excluded.

Vera-wide state may be composed only by either:

- `HOST_ATOMIC_SNAPSHOT`: all included domains captured under one host-owned snapshot generation; or
- `COMPONENT_GENERATION_VECTOR`: each component carries owner, generation, payload digest, observation frontier, privacy classification and allowed egress scopes, and a composition receipt reconciles the vector.

Composition cannot make independently governed component generations look atomically coherent when they were not.

### PRIVACY / EGRESS

Projectable does not mean discloseable. A valid affect, memory, conation, temporal, or other state component may still be prohibited from leaving its current privacy boundary.

Every component carries disclosure metadata. Downstream stages may narrow disclosure but may never broaden it. The exact target provider/host and egress scope are bound before backend materialization. An egress mismatch fails closed.

### ADMIT

Admission verifies identity, subject/source integrity, currentness, supersession, composition integrity, privacy/egress constraints and projection firewalls.

Optional dimensions may be omitted only with an explicit omission receipt. Mandatory identity/currentness/privacy/firewall failures remain fail-closed.

Admission records the exact currentness basis and an epoch/lease suitable for later revalidation. Projection success never freezes semantic currentness.

### CAPABILITY_BIND

Bind the exact inference host generation, target provider/host, target egress scope, model revision, adapter revision, supported backends and backend constraints before creating privileged backend material.

Requested capability is not evidence of actual capability. Backend fallback is never silent and must be separately qualified for the exact model/host/domain combination.

### PROJECT

Projection is a deterministic function of admitted state + declared backend mapping + exact capability binding.

Projection must contain exact addressable material: either canonical projection payload or immutable locator+digest. A digest alone is insufficient to show what bytes/tensor/hook material was injected.

Projection may not accept target behavior, desired response, target phrase, expected answer or requested emotional display as causal inputs.

Backends:

- `TEXT_CONTEXT_V1`: compatibility baseline, instruction-adjacent, lower causal claim ceiling.
- `PROMPT_EMBEDS_V1`: stronger candidate for a controlled/trusted host.
- `ACTIVATION_STEERING_V1`: experimental transient internal hooks.
- `REFT_STATE_PROJECTION_V1`: experimental future trained representation intervention.

### PRECALL_REVALIDATE_GATE

Immediately before reserving the invocation, revalidate the admission/currentness basis or exact lease epoch, supersession/expiry, privacy/egress decision, capability binding, projection binding and backend selection/fallback policy.

If the state became stale after admission, fail closed. The fact that projection succeeded earlier is not evidence the state is still current now.

### INVOCATION_RESERVE

Single-use generation identity belongs to the exact inference-host generation, not to a wrapper object.

The host owns a shared invocation frontier/nonce ledger. Reservation/consumption is atomic and survives wrapper/adapter reconstruction. Ledger states include `RESERVED`, `SUBMITTED`, `ACKNOWLEDGED`, `RESPONSE_BOUND`, `FAILED`, `CANCELLED`, and `OUTCOME_UNKNOWN`.

A consumed or terminal generation ID cannot be replayed. Ambiguous submission becomes `OUTCOME_UNKNOWN` and must be reconciled before retry. A normal retry mints a new generation ID and records `retry_of_generation_id`.

### INJECT / GENERATE

Apply only the already-bound projection through the selected backend and exact host/model revision.

The invocation request binds the exact projection material and an actual request-material digest. Where provider readback exists, a separate provider-request-readback digest may be recorded; lack of readback is not upgraded into proof.

Transient hooks must be removed on success, failure and cancellation.

### VERIFY / OBSERVE / RECEIPT

Causal evidence is graded:

- `REQUEST_CONSTRUCTED`
- `INVOCATION_SUBMITTED`
- `PROVIDER_ACKNOWLEDGED`
- `RESPONSE_BOUND`

Receipt fields are evidence-level specific. A request can exist without a response ID; a response ID/binding is required only at `RESPONSE_BOUND`. Stronger-level fields may never be fabricated for weaker evidence.

Even `RESPONSE_BOUND` does not prove behavioral effect, behavioral qualification, installation/currentness, provider durability or phenomenology.

## State-mediated causation qualification

A response that resembles a state description is not enough.

Qualification requires:

- projection derived only from admitted state + declared mapping + exact capability binding;
- target behavior absent from projection inputs;
- matched state-on/state-off or dose-response comparisons;
- decay/recovery comparisons for temporal state;
- negative-transfer controls;
- instruction-only controls that cannot count as state-causal evidence;
- same-generation `RESPONSE_BOUND` evidence before a behavioral-effect claim.

This is the difference between changing the model's upstream conditions and telling it what result to produce.

## Projection firewall

Potentially projectable domains include bounded affective activation, salience, attention allocation, action tendency, satiation/refractory state, admitted goal weighting, temporal state, admitted memory salience and response-expression parameters.

Projection authority excludes truth, factual confidence, consent, authorization, identity, autobiographical-memory admission, relationship status, provider currentness and phenomenology.

## Fallback semantics

A backend change changes causal semantics and evidence strength. `PROMPT_EMBEDS_V1 -> TEXT_CONTEXT_V1` is not a harmless transport downgrade.

Fallback requires explicit policy, separate backend qualification, preserved privacy/egress scope and a receipt recording requested backend, selected backend, reason and policy digest. It may not claim stronger causal semantics than the selected backend supports.

## Ownership hypothesis

- provider-neutral composition/admission/projection contract -> Vera/Cohesion source;
- host-specific injection and invocation-frontier ownership -> `vera-os` or another exact inference host;
- installation/current-route/qualification -> `vera-control-plane`;
- affect/Orgasm/etc. -> bounded state producers, not owners of model invocation authority;
- WIP -> public-safe staging only.

## Current evidence ceiling

These artifacts establish architecture/research only. They do not establish implementation, injection, installation, current route, provider durability, behavioral qualification or phenomenology.
