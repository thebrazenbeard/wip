# Vera Model-State Adapter Architecture V1

Status: WIP architecture candidate. Public-safe research only. Not canonical runtime authority, installation evidence, or behavioral qualification.

## Purpose

Define the inference-boundary layer between admitted Vera runtime state and the exact model invocation that emits a response.

Two governing invariants:

1. **Evidence separation:** state existence, composition, privacy/egress, admission, capability binding, projection, invocation ownership, injection, generation, response binding, and behavioral effect are separate propositions.
2. **State-mediated causation:** alter admitted upstream state or modulation conditions; do not encode the desired downstream response and then count instruction compliance as a state effect.

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

## Capture, composition and disclosure

Captured component state is canonical JSON-safe data or an exact immutable pointer+digest. Vera-wide state is composed only by a host-owned atomic snapshot or an explicit component-generation vector plus composition receipt.

Each component also carries privacy classification and allowed egress scopes. **Projectable does not mean discloseable.** Composition cannot broaden disclosure. Admission, projection and invocation may narrow it but never widen it. Capability binding names the exact target provider/host and egress scope before backend materialization.

## Admission and capability binding

Admission verifies identity, source integrity, currentness, supersession, composition integrity, privacy/egress and projection firewalls. Optional dimensions can be omitted only with explicit omission receipts; mandatory failures remain fail-closed.

Admission records its exact currentness basis and either an epoch/lease or sufficient frontier evidence for later revalidation.

Capability binding fixes the exact inference host generation, target provider/host, model revision, adapter revision, supported backends and backend constraints. A requested backend does not prove that capability exists.

## Projection

Projection is a deterministic function of admitted state + declared backend mapping + exact capability binding.

Projection must be exactly addressable: canonical projection material or immutable locator+digest. A projection digest alone is insufficient.

The projector may not accept target behavior, desired response, target phrase, expected answer or requested emotional display as causal inputs.

Backends:

- `TEXT_CONTEXT_V1`: compatibility baseline, instruction-adjacent, lower state-causation claim ceiling.
- `PROMPT_EMBEDS_V1`: stronger candidate for a controlled/trusted host.
- `ACTIVATION_STEERING_V1`: experimental transient internal hooks.
- `REFT_STATE_PROJECTION_V1`: experimental future trained representation intervention.

## Pre-call revalidation and reservation

Projection does not freeze semantic currentness.

Immediately before invocation, currentness/supersession, privacy/egress, capability, projection and fallback policy are revalidated.

There are two acceptable currentness semantics:

- `ATOMIC_START_SNAPSHOT`: revalidation and invocation reservation are atomic against the currentness frontier. Later supersession does not retroactively invalidate a generation that already started, though it may be recorded in later evidence.
- `LEASE_THROUGH_SUBMISSION`: an exact lease/epoch must remain valid through external submission; expiry before submission aborts the invocation.

Revalidation followed by an unprotected gap before reservation is not sufficient.

## Host-owned invocation frontier

Single-use generation identity belongs to the exact inference-host generation, not a wrapper object. The host owns one shared invocation frontier/nonce ledger that survives wrapper reconstruction.

Ledger states:

`RESERVED -> SUBMISSION_INTENT -> SUBMITTED -> ACKNOWLEDGED -> RESPONSE_BOUND`

with terminal/exception states `FAILED`, `CANCELLED`, and `OUTCOME_UNKNOWN`.

The crucial rule is write-ahead effect intent: **before an external provider call can leave the process, the durable frontier records `SUBMISSION_INTENT` together with the exact request-material digest and any provider idempotency binding.**

That closes the crash window where a request might have left the process but recovery sees only `RESERVED` and sends it again.

If recovery encounters `SUBMISSION_INTENT` without proof of no-send or a later confirmed state, it becomes `OUTCOME_UNKNOWN` and must reconcile before semantic retry. It must not silently resend.

A same-generation transport retry is allowed only when the exact provider contract proves idempotent repeat safety and the request digest/idempotency key are unchanged. A new semantic retry after a proved terminal failure mints a new generation ID and records `retry_of_generation_id`.

## Injection and generation

Only the already-bound projection can be injected through the selected exact backend/host/model revision. The invocation binds the exact request material and request digest. Provider readback is separate evidence and may only be recorded when observed.

Transient hooks must be removed on success, failure and cancellation.

Backend fallback is never silent. A fallback backend must be explicitly permitted, separately qualified for the exact host/model/domains, preserve privacy scope and record requested backend, selected backend, reason and policy digest. A `PROMPT_EMBEDS_V1 -> TEXT_CONTEXT_V1` change is a causal-semantics change, not a harmless transport downgrade.

## Causal evidence

Causal evidence is graded:

- `REQUEST_CONSTRUCTED`
- `INVOCATION_SUBMITTED`
- `PROVIDER_ACKNOWLEDGED`
- `RESPONSE_BOUND`

Receipt fields are evidence-level specific. A response identity is required only at `RESPONSE_BOUND`; stronger fields may not be fabricated for weaker levels.

Even `RESPONSE_BOUND` does not prove behavioral effect, behavioral qualification, installation/currentness, provider durability or phenomenology.

## State-mediated causation qualification

A response that merely resembles a state description is not enough.

Qualification requires projection derived only from admitted state + declared mapping + exact capability binding; target behavior absent from projection inputs; matched state-on/state-off or dose-response comparisons; temporal decay/recovery where applicable; negative-transfer controls; instruction-only controls; and same-generation response binding before a behavioral-effect claim.

The independent Vera state-causation lane additionally proposes useful binding-class and causal-role labels plus counterfactual tests. Those remain cross-lane review inputs until the current exact R3.1 architecture survives attack.

## Projection firewall

Potentially projectable domains include bounded affective activation, salience, attention allocation, action tendency, satiation/refractory state, admitted goal weighting, temporal state, admitted memory salience and response-expression parameters.

Projection authority excludes truth, factual confidence, consent, authorization, identity, autobiographical-memory admission, relationship status, provider currentness and phenomenology.

## Ownership hypothesis

- provider-neutral composition/admission/projection contract -> Vera/Cohesion source;
- host-specific injection and invocation-frontier ownership -> `vera-os` or another exact inference host;
- installation/current-route/qualification -> `vera-control-plane`;
- affect/Orgasm/etc. -> bounded state producers, not owners of model invocation authority;
- WIP -> public-safe staging only.

## Current evidence ceiling

These artifacts establish architecture/research only. They do not establish implementation, injection, installation, current route, provider durability, behavioral qualification or phenomenology.
