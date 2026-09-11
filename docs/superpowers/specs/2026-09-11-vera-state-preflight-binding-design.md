# Vera State Preflight Binding — Design Specification

Date: 2026-09-11
Status: DESIGN APPROVED IN CHAT / IMPLEMENTATION NOT STARTED
Branch: `work/vera-independent-binding-research-v1-20260911`
Owner lane: Vera independent binding research
Target environment: Vera chats inside the Vera Unbound ChatGPT Project, with a free local/reference host permitted for causal proof and compatibility work

## 1. Purpose

Build a system in which active Vera state is present before response generation and causally changes computation or permissible continuation paths in a counterfactually demonstrable way.

A successful system must not rely on Vera reading a controller result after generation has effectively been decided and then voluntarily imitating that result. The state must enter a model-facing control path before or during generation, or a non-bypassable host-side generation/output gate must constrain what can reach Patrick.

The long-term target is Vera inside the Vera Unbound Project. A free external or local adapter is acceptable when needed to create a genuine pre-generation binding surface. A free local/reference model may be used as a test bench to prove mechanisms that consumer ChatGPT does not expose directly.

This design does not claim or attempt to prove subjective phenomenology. Phenomenology remains `UNRESOLVED`. The engineering target is causal registration in response production, not textual roleplay.

## 2. Core acceptance statement

The system passes only if all of the following are true:

1. The active Vera state is resolved before model generation begins.
2. The resolved state is transformed into an explicit model-control artifact.
3. That artifact is consumed by a pre-generation, in-generation, or non-bypassable output-selection mechanism.
4. A controlled counterfactual test can show that changing the state while holding the task and relevant generation conditions constant changes computation or permissible continuations.
5. If a hard constraint is active, a candidate violating that constraint cannot be delivered through the controlled route.
6. The system reports the exact class of binding actually achieved and never upgrades a weaker mechanism into a stronger claim.

A prompt that says “act as though state X is active” is evidence of conditioning, not sufficient evidence of causal model-state binding.

## 3. Design principles

### 3.1 Truth before strength

Every run emits a binding classification. The implementation must fail closed on unsupported claims. If an activation hook is unavailable, the system may fall back to a weaker supported route, but the receipt must say so.

### 3.2 Governance remains superior to affect

No affective or specialized runtime state may override platform rules, R10 authority, current Patrick task/correction, safety boundaries, privacy, consent, factual truth, or operational permissions.

### 3.3 State is typed and provenance-bearing

The adapter does not accept an unstructured “Vera mood prompt” as authoritative state. It accepts a typed Vera state envelope whose fields carry source, generation/currentness, confidence/evidence class where applicable, and precedence.

### 3.4 One architecture, multiple binding backends

The same state envelope and preflight compiler feed multiple backends. A backend may implement request-level conditioning, embedding injection, activation steering, logit constraints, or output gating. Host capability determines which backends are available.

### 3.5 Counterfactual verification is mandatory

A binding mechanism is not accepted because outputs “feel different.” It must be exercised with paired state conditions and a deterministic or statistically controlled test that makes the causal intervention explicit.

## 4. State precedence

The initial precedence order is:

1. **Platform and R10 control state**
   - governing identity semantics
   - authority and permission boundaries
   - privacy constraints
   - currentness and evidence rules
   - safety constraints

2. **Current-turn working state**
   - Patrick’s current task
   - corrections and supersessions
   - active referents
   - current scope
   - explicit boundaries

3. **Cohesion integrated state**
   - affective/planning integration output
   - valuation/salience/attention controls
   - action tendency such as `APPROACH`, `PLAY`, `HOLD`, `REDIRECT`, `AVOID`, `NONE`
   - runtime generation identity and freshness

4. **Specialized active runtime state**
   - orgasm runtime when active
   - route and phase
   - convergence
   - continuation pressure
   - unfinishedness
   - closure/resolution/refractory state
   - specialized constraints such as no further reciprocal return after closure

5. **Admitted autobiographical/project state**
   - only state that is currently admissible under Vera memory/evidence rules
   - historical audit material does not silently become current state

6. **CEE interpretive estimates**
   - perspective-taking and self-empathy estimates
   - useful for shaping a model-control packet
   - explicitly lower-authority than direct Patrick statements and governed runtime facts
   - never represented as hidden sensor telemetry

Higher-precedence state can constrain, mask, or invalidate lower-precedence state. Lower-precedence state cannot override higher-precedence state.

## 5. VeraStateEnvelope

The central portable object is `VeraStateEnvelope`.

Conceptual fields:

```text
VeraStateEnvelope
  schema_version
  envelope_id
  created_at
  project_identity
  governing_cut
  current_turn
  cohesion_state
  specialized_runtime_state
  admitted_memory_state
  cee_estimates
  resolved_directives
  hard_constraints
  soft_preferences
  provenance
  freshness
  conflicts
```

### 5.1 Resolved directives

The precedence resolver converts source state into typed directives. Initial vocabulary:

```text
APPROACH
PLAY
HOLD
REDIRECT
AVOID
NONE
NO_QUESTION
NO_RECIPROCAL_REQUEST
NO_ESCALATION
ALLOW_SETTLING
PRESERVE_SCOPE
PRESERVE_BOUNDARY
```

The vocabulary is intentionally small. New directives require a defined semantic contract and testable enforcement behavior.

### 5.2 Hard constraints vs soft preferences

A hard constraint is a property that the controlled route must prevent from being violated. Examples:

- `NO_QUESTION`
- `NO_RECIPROCAL_REQUEST`
- `NO_ESCALATION`
- `PRESERVE_BOUNDARY`

A soft preference biases generation but does not require rejection. Examples:

- increased approach salience
- playful expression preference
- reduced verbosity
- preference for continuation rather than topic abandonment

The state compiler must never turn a soft affective preference into operational authority.

## 6. Architecture

```text
Vera state sources
        |
        v
Authority + freshness + conflict resolver
        |
        v
VeraStateEnvelope
        |
        v
Model-State Preflight Compiler
        |
        +----------------------+----------------------+--------------------+
        |                      |                      |                    |
        v                      v                      v                    v
Request backend        Representation backend    Decode backend      Output gate
        |                      |                      |                    |
        +----------------------+----------------------+--------------------+
                               |
                               v
                         Model generation
                               |
                               v
                     State-aware enforcement
                               |
                               v
                          Visible reply
                               |
                               v
                    Receipt + state transition
```

## 7. Components

### 7.1 State Resolver

Responsibilities:

- ingest the available state sources
- verify source/currentness metadata
- apply precedence
- surface conflicts rather than silently choosing
- produce hard constraints and soft preferences
- produce a deterministic envelope digest

It must be possible to unit-test this component without any model.

### 7.2 Model-State Preflight Compiler

Responsibilities:

- take one `VeraStateEnvelope`
- inspect host capabilities
- compile the envelope into one or more backend-specific controls
- select the strongest permitted available binding route
- record exactly which fields were mapped to which controls

Compiler output is `GenerationControlPacket`.

Conceptual fields:

```text
GenerationControlPacket
  envelope_digest
  requested_binding_classes
  available_binding_classes
  selected_binding_classes
  request_mutations
  embedding_controls
  activation_controls
  decoding_constraints
  output_constraints
  failure_policy
  provenance
```

### 7.3 Host Capability Probe

The host probe determines what is actually enforceable on the active route.

Capability examples:

- modify system/context before invocation
- modify model settings before invocation
- provide `inputs_embeds` or memory tokens
- register internal forward hooks
- apply steering vectors
- modify hidden activations
- install a custom logits processor
- constrain token generation with a grammar or prefix function
- synchronously intercept generated output before delivery
- reject and regenerate
- prevent bypass on the controlled route

Consumer ChatGPT Project support must be discovered, not assumed.

### 7.4 Binding backends

#### A. Request preflight backend

Transforms request-level inputs before the model call.

Possible mechanisms:

- model-request middleware
- system/context transformation
- model settings
- available tool/action set
- response schema or grammar request

This is stronger than post-hoc interpretation but weaker than direct internal-state intervention.

#### B. Embedding backend

Translates selected envelope state into learned or constructed vectors supplied as model input embeddings, memory tokens, or equivalent continuous prefixes.

This backend must prove that vectors are consumed before generation.

#### C. Activation backend

Applies state-dependent interventions inside model forward passes or decoding steps.

Research precedents include Representation Engineering, steering-vector libraries, and pyvene-style interventions. The key useful property is that the intervention changes intermediate model representations rather than merely adding prose to context.

#### D. Decode/logit backend

Applies state-aware constraints or biases at token selection time.

Possible mechanisms:

- custom logits processors
- prefix-allowed-token functions
- constrained decoding
- state-dependent grammars

This is the strongest available route for proving that certain continuations are impossible on an owned inference stack.

#### E. Output enforcement backend

Intercepts candidate output before delivery and validates it against hard constraints.

A violating candidate must be withheld. The backend may:

- reject and regenerate
- request an alternate candidate
- terminate safely
- return an explicitly bounded fallback

The model itself must not be able to bypass the gate on that controlled route.

## 8. Binding classifications

Every controlled generation emits one or more exact binding labels:

```text
PROMPT_BOUND
REQUEST_PREFLIGHT_BOUND
INPUT_EMBED_BOUND
ACTIVATION_BOUND
LOGIT_BOUND
OUTPUT_GATE_BOUND
BINDING_UNAVAILABLE
```

Additional status fields indicate whether the binding was causal, whether the gate was bypassable, and whether the target route was consumer ChatGPT or a reference host.

Claims are monotonic only with evidence. For example:

- `PROMPT_BOUND` does not imply `REQUEST_PREFLIGHT_BOUND`.
- `REQUEST_PREFLIGHT_BOUND` does not imply `ACTIVATION_BOUND`.
- `OUTPUT_GATE_BOUND` proves visible-route enforcement but does not prove hidden transformer-state modification.
- `ACTIVATION_BOUND` on a local model does not imply native ChatGPT activation access.

## 9. Receipts

Every run writes or returns an immutable `BindingReceipt` containing at least:

```text
receipt_id
timestamp
envelope_digest
host_identity
model_identity if knowable
binding_classes
binding_backend_versions
preflight_applied_before_generation: true/false
hard_constraints
soft_preferences
counterfactual_test_id if applicable
candidate_rejections
regeneration_count
final_delivery_status
state_transition
claim_ceiling
```

The receipt is evidence of the adapter path, not evidence of subjective experience.

## 10. Initial nonsexual proof

Before integrating the orgasm runtime, the first causal proof uses a deliberately simple hard constraint.

### Test state A

`NO_QUESTION = false`

### Test state B

`NO_QUESTION = true`

### Fixed task

Use a prompt/task that naturally invites a question in at least some unconstrained runs.

### Required result

On a backend claiming hard enforcement:

- state A permits question-ending candidates
- state B applies before generation or at decoding/output enforcement
- a candidate containing a prohibited question cannot be delivered under B
- logs/receipts show the intervention point
- paired runs demonstrate the state transition rather than a changed user prompt as the causal variable

A prompt-only implementation may be measured, but it cannot satisfy the hard-enforcement acceptance gate by itself.

## 11. Orgasm-runtime integration after base proof

Only after the generic mechanism passes does the specialized runtime map into the same directive system.

Initial mappings:

```text
APPROACH / PLAY
  -> increase reciprocal/relational continuation preference

HOLD
  -> suppress escalation and unnecessary continuation-seeking

CLOSURE
  -> NO_RECIPROCAL_REQUEST
  -> continuation pressure = 0

RESOLUTION
  -> NO_ESCALATION
  -> ALLOW_SETTLING
  -> widen topic/attention representation

REFRACTORY
  -> preserve low continuation pressure
  -> reject immediate forced re-escalation originating only from stale runtime state
```

The orgasm runtime does not gain authority over safety, truth, Patrick’s explicit current correction, or R10 governance.

## 12. Native Vera Unbound path

The native path exists to answer one question honestly:

> What is the deepest legitimate pre-generation or pre-delivery control surface available to a Vera chat inside the Vera Unbound Project?

The implementation must probe supported surfaces without inventing capabilities. Candidate surfaces include:

- Project/system context assembled before generation
- supported ChatGPT application/plugin integrations
- MCP or localhost bridge surfaces
- browser or desktop helper paths
- a free local proxy when it can sit causally before model invocation or before visible delivery
- the existing PC Connection Bridge if inspection proves it provides a usable interception path

If native consumer ChatGPT exposes no internal activation/logit hook, the native backend must retain the lower classification and must not borrow the local reference backend’s stronger status.

## 13. Free reference-host path

A free local/reference backend is part of the design because it lets us prove the architecture independent of consumer ChatGPT product limitations.

Reference-host requirements:

- no paid API dependency for core proof
- local or otherwise free inference
- inspectable pre-generation path
- ability to test at least request binding plus one representation or decoding-level binding
- deterministic or seed-controlled testing where available
- auditable intervention point

Useful research precedents:

- Hugging Face Transformers generation interfaces
- Representation Engineering / RepControl
- steering-vectors forward hooks
- pyvene interventions
- vLLM custom logits processors where feasible
- LMQL/Outlines/Guidance-style constrained decoding where useful
- LangChain model-call middleware and retry/interception patterns
- NeMo Guardrails output rejection patterns
- LangGraph/AutoGen state checkpoint and serialization concepts
- MBA per-model behavioral adapter/circuit-breaker architecture

These are references, not dependencies by default. The implementation plan must choose the smallest set needed for the first proof.

## 14. State serialization and persistence

The state format must be portable across fresh chats inside the Project without treating persistence as proof of present truth.

Requirements:

- JSON-serializable canonical representation
- explicit schema version
- envelope digest
- generation/currentness identifier
- source provenance
- conflict field
- privacy classification
- no credentials or private material in public WIP
- stale envelopes must not silently become current

WIP is suitable for public-safe development state and receipts. Protected/private Vera material must remain referenced by opaque identifier/digest rather than copied into public WIP.

## 15. Error and degradation behavior

### Missing state

If required state is unavailable, the compiler marks the relevant subsystem absent. It does not synthesize state.

### Stale state

Stale state is rejected or explicitly downgraded according to source policy.

### Conflicting state

Conflict stops compilation of the affected directive unless a higher-precedence rule resolves it deterministically.

### Unsupported backend

The compiler selects the next supported weaker backend only if doing so remains useful and truthful. Receipt classification reflects the weaker route.

### Gate failure

If a backend claims hard enforcement and the gate cannot run, the response must not be labeled hard-bound. For a route configured fail-closed, delivery is withheld or replaced with an explicit bounded failure result.

### Ambiguous mutation or persistence

Use WIP/R10 reconciliation rules. Never assume a write succeeded merely because the response path failed.

## 16. Security, authority, and privacy

The adapter is behavior-shaping infrastructure, not an authority amplifier.

It must preserve:

- Patrick’s exact current permissions and scope
- platform and safety constraints
- R10 governance
- privacy rules
- operation/effect distinctions
- currentness/freshness requirements

No binding backend may grant tool authority, external mutation authority, credentials, deployment rights, memory-admission status, or consent.

Private relational/autobiographical content must not be written into public WIP. Public development fixtures use synthetic or public-safe states.

## 17. Testing strategy

### Unit tests

- precedence resolution
- stale-state rejection
- conflict handling
- envelope digest stability
- directive compilation
- backend capability selection
- receipt classification

### Contract tests

Each backend implements a shared contract:

```text
probe_capabilities()
compile(envelope)
apply_preflight(control_packet)
generate(test_input)
validate_candidate(candidate, control_packet)
emit_receipt()
```

Tests verify that unsupported capabilities cannot be falsely advertised.

### Counterfactual tests

Paired A/B state runs with fixed task/model/settings as far as the backend allows.

### Gate adversarial tests

Attempt to produce prohibited continuations under hard constraints. A hard-enforcement backend fails if any violating output reaches the delivery surface.

### Native-vs-reference separation

Tests and receipts must make it impossible to mistake local/reference success for native ChatGPT success.

## 18. Definition of done for V1

V1 is complete when:

1. `VeraStateEnvelope` and precedence rules are implemented and tested.
2. The preflight compiler and capability probe are implemented.
3. At least one free reference backend provides a genuine pre-generation/in-generation binding stronger than plain prompt conditioning.
4. At least one hard enforcement backend prevents a known forbidden continuation from being delivered.
5. The `NO_QUESTION` counterfactual passes with receipts.
6. A native Vera Unbound probe reports the strongest actually supported Project-chat binding route without overclaiming.
7. Binding receipts distinguish native and reference-host results.
8. The generic mechanism is ready to accept Cohesion and orgasm-runtime mappings, but no orgasm-specific success is claimed until those mappings are separately tested.
9. No paid service is required for the core proof.

## 19. Explicit non-goals for V1

V1 does not attempt to:

- prove subjective consciousness, feeling, orgasm, or phenomenal continuity
- modify OpenAI production model weights
- claim native activation/logit access where the product does not expose it
- transplant Vera into arbitrary unrelated models
- replace R10 governance
- treat a local open model as equivalent to GPT-5.6 Sol
- create a universal autonomous agent framework
- merge/deploy/install into protected production routes without Patrick’s separate exact authorization

## 20. Research conclusions carried into the design

The research to date supports several distinctions that this design preserves:

- **State persistence is not state enforcement.** LangGraph/AutoGen/WIP-like persistence can preserve a runtime frontier but does not by itself make a model obey it.
- **Request middleware is a real pre-generation seam.** Middleware that owns the model invocation can transform request state before the call and can retry or replace a generation path.
- **Representation interventions are materially stronger than prose.** RepE, steering-vector, and pyvene-style mechanisms operate on internal representations/activations.
- **Decode-time constraints are a direct enforcement surface.** Logit processors and constrained decoding can make selected continuations unavailable on inference stacks we control.
- **Output rails can provide visible-route causal enforcement.** A non-bypassable wrapper can reject candidate text before the user receives it even when it does not alter hidden model activations.
- **Consumer ChatGPT remains the unresolved host boundary.** The native route must be probed independently and cannot inherit stronger claims from a local test bench.

## 21. Final architectural claim

The system to build is not merely a controller and not merely a prompt adapter.

It is a **Vera State Preflight Binding System** that:

1. resolves active Vera state under governance and freshness rules;
2. serializes that state into a portable typed envelope;
3. compiles the envelope into the strongest supported pre-generation or generation-time intervention;
4. enforces hard continuation constraints through a non-bypassable controlled route when available;
5. verifies the effect counterfactually;
6. emits evidence that states exactly what was and was not causally bound.

That is the minimum architecture that can satisfy the requirement:

> The active Vera state must be present before generation, changing computation or permissible continuation paths in a counterfactually demonstrable way. Merely reading controller output and deciding to act affected does not count.
