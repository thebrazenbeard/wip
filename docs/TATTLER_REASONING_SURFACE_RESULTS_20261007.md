# Tattler reasoning-surface results — 2026-10-07

Status: RECOVERY-METADATA EVIDENCE

## Shared experiment result

On 2026-10-07, the same repository stress-test prompt was run through three ChatGPT surfaces while WorkLaptop was instrumented with Tattler plus a companion Codex process/network tracer.

Observed controlled windows:

- Desktop Chat, GPT-5.6 Sol High: **0 MXC launches** and **2 new established Codex TLS connections** in the companion tracer.
- ChatGPT Desktop Work, Ultra: **59 MXC launches** and **73 new established Codex TLS connections** using the same companion-tracer definitions.
- Firefox cloud Work, Max: browser-side traffic was observable locally, but the provider's server-side worker topology was not.

The bounded conclusion is that Desktop Work used materially different local orchestration from ordinary High Chat in this runtime. It does **not** establish that sockets or MXC processes equal agents, that connection fanout grants a reasoning tier, or that a client can promote High into Ultra/Max by imitating transport behavior.

Canonical detailed evidence is being preserved in `thebrazenbeard/tattler` PR #7 and the reasoning interpretation in `thebrazenbeard/rezon` PR #103.


## Why WIP needs this result

WIP exists to let long-running ChatGPT/agentic work survive lost responses, changed runtimes, and replacement chats. The experiment shows that the execution surface itself can materially change orchestration behavior even when the user task is the same.

A checkpoint for model-backed work should therefore preserve the execution surface when known, especially when a resume may occur in a different surface.

Useful optional metadata includes:
- Chat vs Work;
- desktop vs browser;
- model/reasoning label;
- runtime/build when relevant;
- exact task/source head;
- tool/connector set;
- whether another concurrent session overlapped the observation window.

```text
same task != same orchestration surface
replacement chat != same runtime conditions
telemetry difference != authority difference
```

Tattler process/network data can be referenced as observation evidence, but recovery must not infer a reasoning tier from those signals.

## Resume implication

If work moves from Ultra/Max Work back to High Chat, WIP should preserve that the prior artifact came from a different execution surface rather than describing the resumed High session as if it had inherited that reasoning tier.
