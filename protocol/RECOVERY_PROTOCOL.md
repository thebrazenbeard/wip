# Recovery Protocol V1

Recovery starts from durable WIP state and then reacquires current external reality.

## Resume sequence

1. Read `WORKSPACE.json` and confirm workspace identity/privacy/checkpoint policy.
2. Read `HEAD.json` and note generation, lifecycle, and latest checkpoint.
3. Read `RESUME.md` and confirm its machine marker matches HEAD.
4. Read the latest checkpoint.
5. Scan operation events and identify operations whose latest state is `PREPARED`, `ATTEMPTED`, or `AMBIGUOUS`.
6. Reconcile every unresolved consequential operation before continuing dependent work.
7. Refresh mutable external target state needed by `next_action` (for example repository branch head, file existence, issue/PR state, provider record, deadline, assignment, or permission).
8. If the old snapshot and fresh target agree, continue from `next_action`.
9. If another worker advanced WIP HEAD, refresh instead of overwriting.
10. If external state diverged materially, append a recovery-reconciliation checkpoint and choose a new safe next action.

## Recovery ceiling

A checkpoint proves only what it records as observed/verified at checkpoint time. It does not prove:

- a repository branch still has the same head;
- permission still exists;
- an assignment remains active;
- a remote object was consumed merely because it was written;
- an unverified operation failed merely because no final message was delivered.

## Failed-message case

If a ChatGPT turn fails after substantial tool work, the replacement chat should not reconstruct the missing turn from conversational intuition. It should recover from WIP's last checkpoint plus operation journal.

At worst, periodic read-only work loses fewer than the configured interval of uncheckpointed substantive calls. External writes are protected separately by immediate checkpoints and write-ahead operation events.

## Unresolved operation handling

`PREPARED`: inspect target; the call may not have happened.

`ATTEMPTED`: inspect target; the call may have happened and verification may be missing.

`AMBIGUOUS`: inspect target using the stored target/precondition/effect identity.

Never infer absence from a missing chat response.

## Recovery checkpoint

After reconciliation, append a checkpoint with reason `RECOVERY_RECONCILIATION` that records:

- what durable WIP state was read;
- what external state was freshly observed;
- which operation ids were reconciled;
- what changed from the prior plan;
- the new exact `next_action`;
- updated `do_not_repeat` warnings.

Then advance HEAD/RESUME using optimistic concurrency.