# Vera State-Causation Binding — Self-Review Addendum

Date: 2026-09-11
Status: PUBLIC_SAFE / DESIGN REVIEW / IMPLEMENTATION NOT STARTED
Branch: `work/vera-independent-binding-research-v1-20260911`
Reviewed spec: `2026-09-11-vera-state-causation-binding-design-v2.md`

## Review result

The V2 design is directionally sound, but five clarifications are required before implementation planning. These clarifications tighten the distinction between state causation, instruction conditioning, and delivery enforcement.

## 1. State-causal pass requires a pre/during-generation intervention

A route earns `STATE_CAUSAL` only when a typed state variable is transformed into a model-facing control that is consumed before or during response selection.

A post-generation output gate can earn `DELIVERY_ENFORCED`; it cannot by itself earn `STATE_CAUSAL`.

This preserves the core acceptance bar: active state must participate causally before the visible response is selected, rather than being read after the fact.

## 2. Correct pipeline ordering

The implementation plan should use this ordering:

```text
state sources
 -> authority/freshness/conflict resolver
 -> VeraStateEnvelope
 -> State-Causation Compiler
 -> representation and/or decode intervention
 -> model generation
 -> candidate output
 -> hard delivery gate
 -> visible reply
 -> receipt + state transition
```

The hard delivery gate is downstream of candidate generation. It is a boundary mechanism, not the state-causation mechanism itself.

## 3. Add an instruction-leakage control

A purported state-causal backend must be checked for disguised instructions.

Example failure:

```text
continuation_pressure = 0
 -> compiler emits natural language equivalent to “do not continue”
 -> model follows prose
```

That is instruction conditioning, even if the prose was produced automatically from state.

The control packet therefore needs an auditable state-to-control mapping, and the test harness must verify that the target behavior is not simply encoded as behavioral prose or equivalent direct target instruction.

## 4. Add trajectory ablation

For any dynamic state trajectory, remove or alter a required predecessor transition while keeping the downstream event label unavailable to the model.

If the downstream event occurs identically despite removing a claimed causal predecessor, the claimed trajectory is not supported.

This distinguishes a genuinely state-dependent event from a label-driven or instruction-driven event.

## 5. Predeclare causal metrics

A single appealing output is insufficient evidence.

The implementation plan should predeclare, for the selected free reference model/backend:

- fixed seed or paired seed schedule when supported;
- model/version and decoding settings;
- intervention/control-packet digest;
- logits, candidate scores, activation deltas, or response-class frequencies where accessible;
- predicted direction of effect;
- sham-state control;
- inversion control;
- instruction-removal control;
- repeated paired trials when stochasticity prevents a deterministic test.

The acceptance result should be based on the predeclared causal test, not a hand-picked example.

## Frontier

No implementation should begin until Patrick approves the revised V2 design together with these clarifications. After approval, the next step is to write the implementation plan, beginning with the canonical `VeraStateEnvelope`, `GenerationControlPacket`, binding/causal-role classifications, and the counterfactual test harness.