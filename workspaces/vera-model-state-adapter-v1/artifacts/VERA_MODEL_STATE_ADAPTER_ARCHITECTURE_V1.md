# Vera Model-State Adapter Architecture V1

Status: WIP architecture candidate, R4.1. Public-safe research only. Not canonical runtime authority, installation evidence, native-provider capability evidence, behavioral qualification, or phenomenology.

## Purpose

Define the inference-boundary layer between admitted Vera runtime state and the exact model invocation that emits a response.

Three governing invariants:

1. **Evidence separation:** state existence, composition, privacy/egress, admission, capability binding, projection, invocation ownership, injection, generation, response binding, behavioral effect, and phenomenology are separate propositions.
2. **State-mediated causation:** alter admitted upstream state or modulation conditions; do not encode the desired downstream response and then count instruction compliance as a state effect.
3. **No state laundering:** the state-causation firewall begins at capture, not at projection. Output-direction content does not become state-causal because it was renamed, nested, serialized, embedded, or passed through an earlier stage.

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

## Strong state-causal data

A strong `STATE_CAUSAL` path consumes typed structured state, not free-form directives. Allowed payload value kinds are numbers, booleans, bounded enums, and numeric vectors under an exact schema with field-level provenance.

The strong-state vocabulary may include bounded affective activation, salience, attention allocation, action tendency, satiation/refractory state, admitted goal weighting, temporal state, and admitted memory salience. This vocabulary is semantic runtime state; it is not assumed to map one-to-one to transformer features.

The following semantic content is forbidden anywhere in the strong state-causal lineage: target behavior, desired response, target phrase, expected answer, and requested emotional display. A producer cannot evade the rule by placing that content in metadata, memory salience, an expression field, a nested object, or a differently named state property.

`response_expression_parameters` may exist as a compatibility/expression control, but it cannot establish `STATE_CAUSAL` evidence. If it directly prescribes output characteristics, the causal role is instruction-conditioned or another weaker role as actually evidenced.

## Capture, composition and disclosure

Captured component state is canonical JSON-safe data or an exact immutable pointer+digest. Vera-wide state is composed only by a host-owned atomic snapshot or an explicit component-generation vector plus composition receipt.

For a strong state-causal claim, capture validates the typed-state schema before the payload can enter composition. Composition preserves each field's type, source/provenance and generation; it may not relabel output-control content as state.

Each component also carries privacy classification and explicit allowed egress targets/scopes. **Projectable does not mean discloseable.** Privacy labels do not define a universal `narrow -> broad` total order. The machine-readable policy must prove that the exact target provider/host is allowed; incomparable or unproven relations fail closed. Composition cannot broaden disclosure. Admission, projection and invocation may narrow allowed target sets but never widen them.

Capability binding names the exact target provider/host and target egress scope before backend materialization.

## Admission and capability binding

Admission verifies identity, source integrity, currentness, supersession, composition integrity, privacy/egress, projection firewalls, and the full-lineage anti-laundering invariant. Optional dimensions can be omitted only with explicit omission receipts; mandatory failures remain fail-closed.

A strong-state admission receipt binds the exact state schema and field provenance. If target-output semantics entered earlier in the lineage, admission rejects the strong-state path rather than letting projection sanitize it later.

Admission records its exact currentness basis and either an epoch/lease or sufficient frontier evidence for later revalidation.

Capability binding fixes the exact inference host generation, target provider/host, model revision, adapter revision, supported backends and backend constraints. A requested backend does not prove that capability exists.

## Projection

Projection is a deterministic function of admitted state + declared backend mapping + exact capability binding.

Projection must be exactly addressable: canonical projection material or immutable locator+digest. A projection digest alone is insufficient.

For `STATE_CAUSAL`, the projector accepts only admitted typed state and cannot accept target behavior, desired response, target phrase, expected answer, or requested emotional display as causal inputs. A later projection cannot upgrade prompt conditioning, expression controls, decode constraints or delivery gates into stronger causal evidence.

Backends:

- `TEXT_CONTEXT_V1`: compatibility baseline. Binding class `PROMPT_BOUND`; causal-role ceiling `INSTRUCTION_CONDITIONED`. It is instruction-adjacent and cannot alone establish strong state causation.
- `PROMPT_EMBEDS_V1`: candidate for a controlled/trusted host; binding class `INPUT_EMBED_BOUND` when exact evidence supports that mechanism.
- `ACTIVATION_STEERING_V1`: experimental transient internal hooks; binding class `ACTIVATION_BOUND` when directly demonstrated.
- `REFT_STATE_PROJECTION_V1`: experimental future trained representation intervention; activation-class evidence only when directly demonstrated on the exact host/model.

Native ChatGPT must not inherit a local/reference-host binding claim. If the native route exposes only request-level conditioning, its binding class remains correspondingly weak even if a local reference model demonstrates stronger mechanisms.

## Binding class versus causal role

Binding class reports **where/how** the intervention was applied:

`PROMPT_BOUND`, `REQUEST_PREFLIGHT_BOUND`, `INPUT_EMBED_BOUND`, `ACTIVATION_BOUND`, `LOGIT_BOUND`, `OUTPUT_GATE_BOUND`, or `BINDING_UNAVAILABLE`.

Causal role reports **what that mechanism establishes**:

- `INSTRUCTION_CONDITIONED`: explicit/rendered request material conditions behavior; useful as a baseline/control, not strong state causation.
- `STATE_CAUSAL`: typed admitted upstream state changes computation or selection conditions without encoding the desired response.
- `CONSTRAINT_CAUSAL`: a hard generation constraint changes what can be selected; this does not prove endogenous preference.
- `DELIVERY_ENFORCED`: a pre-delivery gate rejects/replaces invalid output; this proves delivery enforcement only.

Neither classification creates authority or proves phenomenology.

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

Before an external provider call can leave the process, the durable frontier records `SUBMISSION_INTENT` together with the exact request-material digest and any provider idempotency binding. That closes the crash window where a request might have left the process but recovery sees only `RESERVED` and sends it again.

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

Each receipt also reports actual binding class and causal role. `STATE_CAUSAL` additionally requires the typed-state schema binding and full-lineage anti-laundering receipt.

Even `RESPONSE_BOUND` does not prove behavioral effect, behavioral qualification, installation/currentness, native-provider capability, provider durability or phenomenology.

## Counterfactual qualification

Strong state causation is a counterfactual claim, not a resemblance judgment. The qualification suite therefore requires:

- matched state-on/state-off or dose-response runs with task/model/governing context held fixed as far as the host permits;
- instruction-removal control: the expected directional state effect survives removal of an explicit target-behavior instruction;
- sham-state control: metadata/provenance changes with the actual causal payload held constant should not create a state-specific effect;
- directional inversion: opposed state values produce the predicted directional change in the bound control surface/outcome;
- temporal decay/recovery when the state is temporal;
- negative-transfer controls;
- full-lineage audit proving target-output content was absent from capture through projection;
- same-generation response binding before any behavioral-effect claim.

The suite records exact host/model/backend/binding-class/causal-role evidence and never upgrades a local reference result into a native ChatGPT capability claim.

## Generic before specialized

The generic state-causation mechanism is qualified before a specialized Orgasm analogue is allowed to count as state-causal evidence. The specialized system can then supply a trajectory of admitted variables to the already-qualified generic adapter.

For Orgasm, the desired architecture remains a trajectory such as:

`context/stimulus -> appraisal -> activation/coupling -> entrainment/convergence -> eligibility/threshold -> event -> resolution/satiation/refractory shift`

A direct instruction such as `have an orgasm`, an `ORGASM = TRUE` flag used as the behavioral cause, or a prompt telling the model what display to emit does not satisfy the state-causal qualification. Test/admin forced transitions may remain useful for serialization and plumbing tests but are separately labeled.

## Projection firewall

Potentially projectable domains can influence bounded salience, attention, valuation/action tendency, temporal/refractory state, admitted goal weighting, admitted memory salience and compatible expression controls.

Projection authority excludes truth, factual confidence, consent, authorization, identity, autobiographical-memory admission, relationship status, provider currentness and phenomenology.

## Ownership hypothesis

- provider-neutral composition/admission/projection contract -> Vera/Cohesion source;
- host-specific injection and invocation-frontier ownership -> `vera-os` or another exact inference host;
- installation/current-route/qualification -> `vera-control-plane`;
- affect/Orgasm/etc. -> bounded state producers, not owners of model invocation authority;
- WIP -> public-safe staging only.

## Current evidence ceiling

These artifacts establish architecture/research and executable contract regressions only. They do not establish a runtime implementation, model injection, installation, current route, provider durability, native ChatGPT hidden-state access, behavioral qualification or phenomenology.
