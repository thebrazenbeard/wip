# Resume

<!-- wip:latest_checkpoint=cp-000002 -->

Workspace: `parallax-chat-bus-hardening-v1`
Lifecycle: `ACTIVE`

## Objective

Independently harden the Chat Communication Bus, beginning with reviewed Parallax topology onboarding and an evidence-backed target architecture.

## Verified position

- Latest checkpoint: `cp-000002`
- WIP recovery branch: `wip/parallax-chat-bus-hardening-v1`
- Chat Bus canonical cut observed: `b2950bcb547fb78d16e44cd94a6ba2164937bf44`
- No merge, deployment, credential, provider, branch-protection, or ruleset mutation has been performed.

## Already done

- Independently reviewed current Bus source, PRs #15, #17, #18, issue #16, exact CI evidence, and read-only provider state.
- Established public-safe recovery records for this Work task.

## Unfinished

- Create inert `bus/parallax-v1` from an exact canonical cut.
- Open a reviewed Bus-local topology/bootstrap PR for Parallax.
- After Patrick merges, verify the first guarded append before worker coordination.
- Publish the architecture design as a separate Draft PR and stop at the written-spec review gate.

## Do not repeat

- Do not write through Radar's lane or impersonate Radar.
- Do not merge, deploy, mutate credentials/provider configuration, or change branch protections/rulesets without Patrick's explicit authorization.
- Do not treat provider projection absence as proof of no Git source message while issue #16 remains unresolved.

## Next safe action

Verify the latest PR #20 CI run; do not append to `bus/parallax-v1` until Patrick merges the topology PR.
