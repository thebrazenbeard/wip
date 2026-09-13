# Resume

<!-- wip:latest_checkpoint=cp-000006 -->

Workspace: parallax-chat-bus-hardening-v1
Lifecycle: ACTIVE

## Verified position

- Chat Bus main: aeab0f04fc9b4bd7c2945c9a53011c53fac809b4
- Current main is diverged from Anchor-E/preflight source (ded270af1dbd51537bec92904e283da8d4183ff8); central reconciliation is not canonical.
- PRs #15, #17, #18, #20, #21, and #22 are merged; #17 and #22 retain historical failing-CI evidence.
- bus/parallax-v1 is contaminated at 6620e9d9cc6662da2872d37b98747edb8476b04b; first Parallax append is not verified.
- Supabase github-bus-ingest is ACTIVE v3 with verify_jwt=true and digest 0aaab7f376d1454efe76a757755918312eac35a8fde2f4c4ff7e63072a558fb7; provider Radar migrations lag source.
- WIP branch: wip/parallax-chat-bus-hardening-v1
- Connection matrix: operations/op-000005-03-verified.json
- No protected effect has been performed.

## Hostile priorities

- NOW: stop using contaminated Parallax lane; reconcile canonical source and provider control root; close Edge topology/provenance/body-limit gaps; make current-main CI and branch protection observable.
- NEXT: durable queue/ack/retry/expiry, one authoritative registry with lease renewal, strict heartbeat wiring, DLQ replay state machine, duplicate-lane ambiguity failure, fan-out-safe relay IDs.
- LATER: scale beyond Git mailboxes, event-sourced topology/leases, push-based discovery, richer thread/read receipts, executable Vera-mesh vertical slice.
- DO NOT DO: merge failing PRs, deploy or migrate Supabase, force-push/rewrite lanes, infer currentness from stale contracts or provider absence, or treat docs-only Vera-mesh as runtime evidence.

## Safe next action

Create a clean successor lane only from a freshly verified canonical cut after Patrick approves the source-reconciliation plan. Do not append to bus/parallax-v1 until contamination is resolved and the current guard/readback path is proven.
