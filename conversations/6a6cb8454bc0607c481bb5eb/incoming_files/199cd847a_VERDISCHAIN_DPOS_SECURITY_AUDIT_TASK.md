TASK: FULL DPoS SECURITY AND CONSENSUS FIX — VERDISCHAIN

Repository:
https://github.com/Protremix/Verdischain-

You are responsible for implementing and validating a production-grade fix for the DPoS subsystem.

IMPORTANT:
Do NOT blindly rewrite the architecture.
Do NOT change tokenomics, consensus economics, validator count, or public APIs unless required to fix a verified bug.
Preserve the existing VerdisChain architecture and terminology.

PRIMARY FILE:
pallets/dpos/src/lib.rs

RELATED FILES TO INSPECT:
- node/src/chain_spec.rs
- runtime/src/lib.rs
- pallets/dpos/src/tests if present
- any runtime configuration implementing pallet_dpos::Config
- Session/BABE/GRANDPA integration

==================================================
PHASE 1 — DEEPLY AUDIT THE CURRENT IMPLEMENTATION
==================================================

Before modifying anything:

1. Read the complete DPoS pallet.
2. Read the complete chain_spec.rs.
3. Read the runtime configuration for DPoS.
4. Trace all storage:
   - Validators
   - ValidatorList
   - ActiveValidators
   - Votes
   - UnbondingQueue
   - TotalStaked
   - SlashingEvents
5. Trace all DPoS extrinsics.
6. Trace genesis initialization.
7. Trace SessionManager integration.
8. Trace epoch rotation.
9. Trace block reward distribution.
10. Trace slashing.
11. Trace validator registration/unregistration.
12. Trace delegation/unvoting/withdrawal.

Create a written audit before editing.

==================================================
PHASE 2 — FIX VERIFIED DPoS BUGS
==================================================

Implement and test the following.

1. VALIDATOR STAKE CAP

The current registration logic contains:

total_staked.saturating_add(stake) <= MaxStakePerValidator
    || stake <= MaxStakePerValidator

This is logically incorrect.

The validator's own stake must never exceed MaxStakePerValidator.

Fix the condition without incorrectly turning MaxStakePerValidator into a network-wide TotalStaked cap.

Also verify that delegated voting weight cannot exceed the intended per-validator maximum.

2. UNREGISTER WITH ACTIVE DELEGATIONS

A validator must NOT be removable while delegated votes still exist.

Current behavior can remove the validator while voter funds remain associated with it.

Choose a safe design consistent with the existing architecture.

Preferred behavior:

- reject unregister if total_votes > validator.stake
- return an explicit error
- preserve all delegated funds
- never orphan voter funds

Add a regression test.

3. MULTIPLE VOTES TO THE SAME VALIDATOR

Inspect the current Votes storage and vote/unvote behavior.

If multiple votes to the same validator are not intentionally supported, prevent duplicate vote records.

The current unvote logic removes one matching delegation while the storage design can potentially contain multiple records.

Make vote/unvote accounting deterministic.

Add tests.

4. VOTE STORAGE OVERFLOW

Never silently ignore BoundedVec::try_push failures.

Every bounded storage insertion must return an explicit error.

Apply this to:
- Votes
- UnbondingQueue
- ValidatorList
- ActiveValidators

Do not use:
.try_push(...).ok();
where failure could cause accounting/state inconsistencies.

5. UNBONDING QUEUE

Ensure:
- queue capacity is enforced
- overflow returns an error
- funds remain reserved until unlock
- funds cannot be withdrawn before unlock
- all matured requests can be withdrawn
- immature requests remain untouched

Add regression tests.

6. SLASHING ACCOUNTING

When validator stake is slashed, verify all related accounting remains internally consistent.

Check:
- validator.stake
- validator.total_votes
- TotalStaked
- reserved balance
- treasury balance
- validator active/slashed status

Do not allow accounting to become inconsistent.

IMPORTANT:
Do not accidentally slash delegated voter funds when the current economic design does not authorize that.

Document the chosen behavior.

7. GENESIS VALIDATOR STATE

Review GenesisConfig.

Verify that:
- validator_count matches the actual validator vector
- ValidatorList contains exactly the intended validators
- ActiveValidators contains only ActiveValidatorCount validators
- TotalStaked equals the sum of validator stakes
- validator stake is correctly reserved/locked if the runtime expects it to be reserved
- no duplicate validator accounts exist

Do not silently modify the intended validator set.

8. SESSION INTEGRATION

Review SessionManager::new_session.

Verify that the validator set returned to Session is exactly the intended active set.

Check consistency between:
DPoS ActiveValidators
Session keys
BABE authorities
GRANDPA authorities

Do not assume that having 21 Session keys means DPoS actually has 21 matching validators.

Detect and report mismatches.

9. EPOCH ROTATION

Review rotate_epoch().

Verify:
- only active and non-slashed validators are eligible
- ActiveValidatorCount is respected
- sorting is deterministic
- ties are deterministic
- state transition cannot produce an empty validator set when eligible validators exist
- Session receives the correct resulting set

Do not introduce nondeterministic ordering.

10. GREEN SCORE

The current green score is self-reported.

Do NOT pretend this is an externally verified environmental metric.

If green_score currently affects consensus or validator selection, determine whether that is intended.

If it is only metadata, keep it as metadata.

If it affects validator selection, clearly document the security/economic implications and do not invent an oracle.

Do not create a fake verification mechanism.

==================================================
PHASE 3 — TOKENOMICS / GENESIS CONSISTENCY
==================================================

Inspect the relationship between:
- runtime tokenomics constants
- Tokenomics GenesisConfig
- chain_spec balances
- DPoS validator stakes
- reward pool
- treasury
- liquidity pools

Find any contradictions.

In particular verify whether:

tokenomics: Default::default()

leaves tokenomics storage uninitialized while chain_spec already defines a 100B VRDX distribution.

Do NOT change the 100B supply or allocation without explicit authorization.

Instead:
1. identify the inconsistency
2. determine the intended source of truth
3. implement the safest minimal fix
4. add tests/assertions preventing future divergence

==================================================
PHASE 4 — SECURITY REVIEW
==================================================

Check for:
- unauthorized state changes
- root-only operations
- Sudo exposure
- integer overflow/underflow
- zero-value operations
- duplicate delegation
- orphaned funds
- reservation inconsistencies
- reward pool accounting
- validator removal attacks
- slashing inconsistencies
- deterministic consensus issues
- bounded storage failures
- genesis inconsistencies

Pay special attention to:
- saturating arithmetic
- reserve/unreserve
- transfer failures
- ExistenceRequirement
- BoundedVec
- StorageMap mutation
- SessionManager

Never ignore a Result where ignoring it can create an accounting inconsistency.

==================================================
PHASE 5 — TESTS
==================================================

Add regression tests for every fixed vulnerability.

At minimum test:
1. validator registration above maximum stake
2. validator registration at maximum stake
3. validator unregister with no delegation
4. validator unregister with delegation -> must fail
5. duplicate vote -> must fail if duplicate votes are disallowed
6. vote above validator cap -> must fail
7. zero vote -> must fail
8. unvote starts unbonding
9. withdrawal before unlock -> must fail
10. withdrawal after unlock -> succeeds
11. unbonding queue overflow
12. vote storage overflow
13. slashing updates accounting
14. genesis validator count
15. genesis active validator count
16. genesis TotalStaked
17. deterministic epoch rotation
18. Session active validator set

Use the existing testing framework and conventions.

==================================================
PHASE 6 — BUILD AND TEST
==================================================

Run:
cargo fmt --all -- --check
cargo check --workspace
cargo test --workspace

If the repository has specific runtime/node tests, run them too.

If compilation fails because of an unrelated existing problem:
- identify the exact failure
- do not hide it
- do not claim success
- distinguish pre-existing failures from failures introduced by your changes

Run targeted DPoS tests separately.

==================================================
PHASE 7 — FINAL VERIFICATION
==================================================

After implementing fixes:

Re-read every changed file.

Check every:
- Result
- ensure!
- try_push
- reserve
- unreserve
- transfer
- storage mutation
- arithmetic operation
- validator state transition

Look specifically for cases where a failed operation could leave storage inconsistent with balances.

Then run formatting and tests again.

==================================================
PHASE 8 — DELIVERABLE
==================================================

Provide a final report containing:

A. Files changed
B. Every bug found
C. Severity: CRITICAL / HIGH / MEDIUM / LOW
D. Exact fix applied
E. Tests added
F. Test commands executed
G. Exact test/build results
H. Any remaining issues
I. Any issues that require architectural/product decisions
J. Security status:
   - production ready
   - requires additional fixes
   - not safe for mainnet

IMPORTANT:
Never say "fixed" unless the code was actually changed and the relevant test passed.

Never say "tests pass" unless the tests were actually executed.

Never invent test results.

==================================================
GIT REQUIREMENT
==================================================

Work on a dedicated branch:

fix/dpos-security-audit

Make clean commits.

Suggested commits:
1. fix: harden dpos validator accounting
2. fix: prevent orphaned delegations
3. test: add dpos regression coverage
4. fix: align genesis and session validator state

Before finishing, show:
git diff --stat
git diff
git status

Do NOT force-push.
Do NOT rewrite unrelated history.
Do NOT modify unrelated files.
