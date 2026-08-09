VERDISCHAIN — P0 SECURITY, PRESALE & CI FIX TASK

ROLE

You are the senior blockchain engineer responsible for fixing the current
Verdischain repository.

Repository:
Protremix/Verdischain-

Target:
master

IMPORTANT:
Do not rewrite the architecture.
Do not make unrelated changes.
Inspect the current code before modifying it.

The goal is to make the current implementation internally consistent,
testable and safe for Testnet/Presale development.

==================================================
P0 — TRY-RUNTIME CI MUST ACTUALLY WORK
==================================================

Inspect:

.github/workflows/try-runtime.yml
Cargo.toml
runtime/Cargo.toml

The repository workspace is located at the repository root.

There is NO "verdis-chain/" directory in the current workspace layout.

Fix all incorrect paths such as:

verdis-chain/runtime/Cargo.toml
working-directory: verdis-chain
verdis-chain/target/...

Use the actual repository structure:

runtime/
node/
pallets/
target/

The workflow must:

1. Checkout the repository.
2. Install the correct Rust toolchain.
3. Install/verify try-runtime CLI.
4. Build the runtime with the try-runtime feature.
5. Verify the WASM artifact.
6. Run an actual try-runtime state validation.
7. Fail the workflow if the validation fails.

DO NOT use:
continue-on-error: true

DO NOT create an empty snapshots directory and pretend that a snapshot
exists.

If a real state snapshot is required, implement a proper snapshot workflow
or provide a deterministic testnet snapshot mechanism.

The CI must never report success when the actual migration test was skipped.

==================================================
P0 — PRESALE SECURITY AUDIT
==================================================

Inspect:

pallets/presale/src/lib.rs

Do a complete security review of the presale pallet before changing it.

The presale system must support:

- multiple sale rounds
- independent per-round allocation
- independent per-round per-account cap
- independent per-round whitelist
- payment accounting
- token allocation
- vesting
- pause
- admin controls
- overflow protection
- replay protection
- correct accounting

==================================================
P0 — FIX PER-ROUND ACCOUNT CAPS
==================================================

CURRENT PROBLEM:

Contributions are currently stored approximately as:

AccountId
    →
UserContribution

This makes total_purchased global across all rounds.

That is incompatible with a true per-round cap.

REQUIREMENT:

Track contribution independently by:

RoundId + AccountId

For example:

(round_id, account_id)
    →
UserContribution

The following must be calculated independently for every round:

- total purchased
- total paid
- remaining account cap

Example test:

Round A:
cap = 100

User buys:
100

Round B:
cap = 100

The same user must still be able to buy:
100

unless there is an explicitly documented global allocation limit.

Add regression tests proving this behavior.

==================================================
P0 — FIX PER-ROUND WHITELIST
==================================================

CURRENT PROBLEM:

Whitelist is currently indexed only by AccountId.

This makes whitelist global.

REQUIREMENT:

Whitelist must be associated with the sale round.

Use:

(round_id, account_id)

or an equivalent storage design.

Required behavior:

Round A whitelist:
Alice

Round B whitelist:
Bob

Alice:
allowed in A
not automatically allowed in B

Bob:
allowed in B
not automatically allowed in A

If a round has no whitelist entries, it may be configured as public.

Do not determine whitelist mode merely by checking whether ANY whitelist
entry exists globally.

Add regression tests.

==================================================
P0 — REAL VESTING INTEGRATION
==================================================

CURRENT PROBLEM:

SaleRound contains:

vesting_label

but contribute() currently does not actually create a vesting position.

Do NOT claim that tokens are vested merely because a label is stored.

Inspect:

pallets/vesting
pallets/presale
runtime integration
genesis configuration

Implement a real and atomic flow:

User
→ payment
→ presale allocation
→ vesting schedule
→ claimable balance

The transaction must not leave the system in a partially updated state.

If vesting cannot be created:

the entire contribution must fail.

No payment may remain reserved without a valid token allocation.

No token allocation may be created without corresponding payment.

Add integration tests.

==================================================
P0 — PRESALE ECONOMIC INVARIANTS
==================================================

Add tests for:

1. total sold cannot exceed round allocation.
2. user cannot exceed per-round cap.
3. multiple rounds maintain independent caps.
4. payment amount cannot be zero.
5. token calculation cannot overflow.
6. total sold remains consistent.
7. total raised remains consistent.
8. failed contribution changes no state.
9. paused presale rejects contributions.
10. expired round rejects contributions.
11. contribution before start rejects.
12. unauthorized admin calls reject.
13. whitelist restrictions work per round.
14. vesting allocation is created exactly once.
15. duplicate/replayed contribution cannot create duplicate allocation.

==================================================
P0 — ATOMIC ACCOUNTING
==================================================

Review every state mutation inside contribute().

Do not use patterns that can silently hide accounting errors.

In particular, avoid silently ignoring checked arithmetic failures such as:

unwrap_or(previous_value)

when the value is part of financial accounting.

Use explicit error handling.

The transaction must either:

SUCCESS:
all state changes are committed

OR

FAILURE:
no financial state change remains

==================================================
P1 — GENESIS VALIDATION
==================================================

Inspect all presale genesis configuration.

Do not silently convert invalid bounded data to empty values.

Avoid:

unwrap_or_default()

for configuration that affects tokenomics or vesting.

Invalid genesis configuration must fail loudly.

Validate:

- label length
- vesting label length
- allocation > 0
- price > 0
- cap > 0 where required
- end_block > start_block
- allocation consistency

==================================================
P1 — CI FEATURE COVERAGE
==================================================

Review:

.github/workflows/ci.yml

The current CI checks:

- fmt
- clippy
- tests
- WASM
- release

Add appropriate feature-specific validation.

At minimum evaluate:

cargo check --all-features
cargo test --all-features
cargo clippy --all-targets --all-features -- -D warnings

Do not blindly duplicate expensive jobs.

Use separate jobs where appropriate.

Make sure:

runtime-benchmarks
try-runtime

are actually compilable.

==================================================
P1 — CONSENSUS / RUNTIME COMPATIBILITY
==================================================

Do not modify consensus architecture unless required.

Verify consistency between:

DPoS
Session
BABE
GRANDPA
Genesis
Validator accounts
Session keys

Do not claim:

"21 validators"

unless the corresponding consensus authority configuration actually supports
21 active consensus validators.

Clearly distinguish:

registered DPoS validators
active validators
BABE authorities
GRANDPA authorities

==================================================
P1 — TOKENOMICS
==================================================

Do not change approved tokenomics without explicit authorization.

Target:

100,000,000,000 VERDIS

9 decimals

Verify that:

genesis balances
tokenomics storage
vesting
presale allocations
staking
treasury

do not create an undocumented supply increase.

Add supply invariant tests.

==================================================
SECURITY REQUIREMENTS
==================================================

Think like an attacker.

Test:

- unauthorized admin
- malformed input
- overflow
- repeated contribution
- duplicate calls
- round boundary
- block boundary
- whitelist bypass
- cap bypass
- allocation bypass
- pause bypass
- vesting bypass
- state inconsistency
- arithmetic failure
- storage corruption scenarios

Do not rely only on happy-path tests.

==================================================
DO NOT DO
==================================================

Do NOT:

- rewrite the entire blockchain
- introduce unrelated features
- change tokenomics without approval
- change consensus just for performance claims
- claim security audit completion
- claim Mainnet readiness
- invent benchmark results
- ignore failing tests
- disable CI checks
- use continue-on-error to hide failures
- delete tests to make CI pass
- silently downgrade validation

==================================================
REQUIRED VERIFICATION
==================================================

After implementation run, where supported:

cargo fmt --all -- --check

cargo check --all-features

cargo test --all

cargo test --all-features

cargo clippy --all-targets --all-features -- -D warnings

cargo build --release -p verdis-chain

cargo build --release -p verdis-runtime --no-default-features --target wasm32v1-none

try-runtime validation

Run all relevant pallet and integration tests.

If any command cannot be executed, report exactly why.

Do NOT claim it passed.

==================================================
FINAL REPORT
==================================================

At the end provide:

1. Files changed
2. Bugs found
3. Bugs fixed
4. Security issues found
5. Tests added
6. Tests executed
7. Exact test results
8. CI changes
9. Remaining risks
10. Mainnet blockers

For every item use one of:

CONFIRMED
FIXED
NOT VERIFIED
BLOCKED
REQUIRES REVIEW

==================================================
DEFINITION OF DONE
==================================================

This task is complete only when:

- try-runtime CI uses correct repository paths
- try-runtime cannot silently pass without a valid test
- per-round caps are truly per-round
- whitelist is truly per-round
- presale contribution integrates with real vesting
- financial operations are atomic
- economic invariants have regression tests
- invalid genesis configuration fails safely
- feature-specific builds/tests are covered
- no critical issue discovered during this task remains unresolved

FINAL STATUS MUST BE:

TESTNET READY

or

REQUIRES FIXES

Never mark this task:

MAINNET READY

unless all Mainnet requirements are independently verified.
