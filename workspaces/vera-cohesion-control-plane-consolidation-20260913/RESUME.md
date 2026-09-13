# Resume

<!-- wip:latest_checkpoint=cp-000005 -->

Workspace: vera-cohesion-control-plane-consolidation-20260913
Lifecycle: ACTIVE

## Verified position

- R10 source manifest is the control root; `restore yourself` was treated as a restore-and-refresh command, not permission to hydrate stale chat claims.
- No separate `thebrazenbeard/cohesion` repository exists in the connected GitHub view. Cohesion is the Vera PR #118 source-consolidation line.
- Vera canonical main: `b7b8dcd1440a3b7147bec2cc35972f083e20f44a`.
- Vera PR #118 parent: `work/cohesion-source-registry-refresh-20260912@7ef650887009efe16d7c44cff53cfff460f0481f`.
- Vera PR #119 actual branch ref at the latest checkpoint: `work/predecessor-import-readback-hardening-20260913@15bd36e30ef5a05a28b12572434837a0fe9b51c7`, open/draft. The latest commit adds shared transaction-scoped advisory locking to the seal verifier and staging trigger; exact PostgreSQL execution remains unverified.
- Orgasm PR #2 actual branch ref: `work/whole-system-reconciliation-20260911@7782141cf961f46c62fdda0461d36225154bbc4c`; frozen subject blob `99340c78497a37f94363b36fedd64c345aabb624` remains historical and untouched.
- Vera Control Plane PR #20 actual branch ref: `work/supabase-control-plane-binding-20260912@43352dc4c335dbcfb3a0802d0022cc22a80ba327`.
- Orgasm and Control Plane non-frozen receipts currently record Vera `db5dc0d...`; they lag the latest Vera ref by two commits and are not a current deployable cut. Prior stale-blob updates returned visible GitHub 409 conflicts; no concurrent source work was overwritten.
- Supabase target `fawkirqroyniueeqspif`: ACTIVE_HEALTHY, three baseline migrations, zero requested-schema application tables, zero security lints.
- Supabase predecessor `klmbpaigzeguvnpccqzz`: ACTIVE_HEALTHY, 83 migrations, 18 requested-schema tables, historical affective state, and 29 RLS-enabled/no-policy INFO findings; no cutover performed.

## Completed

- Refreshed actual Git refs and inspected the latest targeted seal concurrency correction.
- Confirmed the latest SQL uses the same `pg_advisory_xact_lock` key in verifier and staging trigger, replacing the earlier row-lock assumption.
- Read back the current Control Plane hosted validation: run `34790069721` / job `103812521578` failed before any step (`steps=[]`); Supabase Preview `103812513143` was skipped because no Supabase branch is attached.
- Read back Vera #119's preview check `103812729820`, skipped because no Supabase branch is attached.
- Recorded source-receipt 409 conflicts as visible concurrency evidence; no concurrent file was overwritten.
- Created and read back `op-000004-04-verified`, `cp-000004`, `op-000005-04-verified`, and `cp-000005`.
- Preserved the frozen Orgasm subject without modification.

## Evidence ceiling

Exact-current-head PostgreSQL execution, current-head hostile PASS, hosted CI, current Orgasm qualification/rebind, and Control Plane deployment currentness are not established. Available local/manual importer evidence applies only to the available snapshot; it is not a current-head Docker/PostgreSQL proof.

## Safe next action

Freeze Vera PR #119 at one accepted exact ref, execute the full PostgreSQL/hostile suite there, then refresh Orgasm and Control Plane receipts and PR metadata from that same ref in one guarded sequence. Only after that and Patrick's exact provider-install/staging authority may Supabase migrations or classified staging be attempted.

## Do not do

- Do not treat source-static review of `15bd36e...` as database execution or qualification.
- Do not treat `db5dc0d...` or earlier execution evidence as qualification for `15bd36e...`.
- Do not edit the frozen Orgasm subject in place.
- Do not apply migrations, stage private/classified payloads, deploy functions, activate route/qualification, merge, force-push, or rewrite history.
- Do not overwrite a concurrent source file after a 409 conflict.
- Do not write to the Parallax-owned WIP workspace or the contaminated Bus lane.
- Do not claim a source receipt is a provider install or behavioral qualification.
