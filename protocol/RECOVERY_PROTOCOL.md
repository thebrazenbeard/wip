# Recovery Protocol V1

Recovery starts from durable WIP state and then reacquires current external reality.

## Resume sequence

1. Read `WORKSPACE.json` and confirm workspace identity, storage/privacy class, and checkpoint policy.
2. Read `HEAD.json` and note generation, lifecycle, latest checkpoint, and latest operation event.
3. Read `RESUME.md` and confirm its machine marker matches HEAD.
4. Read the latest checkpoint.
5. Scan operation events and classify the latest state of every operation.
6. Reconcile every unresolved consequential operation before continuing dependent work.
7. Refresh mutable external target state needed by `next_action` (for example repository branch head, file existence, issue/PR state, provider record, deadline, assignment, or permission).
8. If the old snapshot and fresh target agree, continue from `next_action`.
9. If another worker advanced WIP HEAD, refresh instead of overwriting.
10. If external state diverged materially, record the appropriate operation `CONFLICT`/reconciliation outcome and append a recovery checkpoint with a new safe next action.

## Recovery ceiling

A checkpoint proves only what it records as observed/verified at checkpoint time. It does not prove:

- a repository branch still has the same head;
- permission still exists;
- an assignment remains active;
- a remote object was consumed merely because it was written;
- an unverified operation failed merely because no final message was delivered.

WIP preserves operational continuity. It never converts historical intent into current authority.

## Failed-message case

If a ChatGPT turn fails after substantial tool work, the replacement chat should not reconstruct the missing turn from conversational intuition. It should recover from WIP's last checkpoint plus operation journal.

At worst, periodic read-only work loses fewer than the configured interval of uncheckpointed substantive calls. External writes are protected separately by immediate checkpoints and write-ahead operation events.

## Operation-state handling

`PREPARED`: inspect target; the call may not have happened.

`ATTEMPTED`: inspect target; the call may have happened and verification may be missing.

`AMBIGUOUS`: inspect target using the stored target/precondition/effect identity.

`ABSENT`: prior inspection already proved the intended effect did not land. Before any retry, refresh external authority/currentness/preconditions. If retry is still permitted, continue the **same operation id** with a new `ATTEMPTED` event.

`RECONCILED`: recovery already found and adopted the exact intended effect. Do not repeat it.

`CONFLICT`: recovery found divergent state. Stop dependent mutation until the conflict is resolved by current authority/evidence.

Never infer absence from a missing chat response.

## WIP-storage ambiguity

WIP journal persistence itself is the non-recursive storage primitive. If a WIP write has an ambiguous provider result:

1. inspect the exact append path or mutable projection;
2. if the exact expected WIP state is present, read it back and continue;
3. if absent, retry only under the original create-only or compare-and-swap precondition;
4. if divergent, stop and reconcile WIP storage before continuing the workspace.

Do not create an operation event about the act of creating an operation event.

## Recovery checkpoint

After reconciliation, append a checkpoint with reason `RECOVERY_RECONCILIATION` that records:

- what durable WIP state was read;
- what external state was freshly observed;
- which operation ids were reconciled, confirmed absent, or conflicted;
- what changed from the prior plan;
- the new exact `next_action`;
- updated `do_not_repeat` warnings.

Then advance HEAD/RESUME using optimistic concurrency.

## Concurrency recovery

If a projection-changing mutation fails because the observed generation/blob is stale, that worker loses the race cleanly:

1. do not force the update;
2. read current HEAD/RESUME;
3. inspect the newly appended history;
4. decide whether the pending action is still needed;
5. continue only from the refreshed generation.

A stale-write rejection is a safety result, not a transient failure to blindly retry.
