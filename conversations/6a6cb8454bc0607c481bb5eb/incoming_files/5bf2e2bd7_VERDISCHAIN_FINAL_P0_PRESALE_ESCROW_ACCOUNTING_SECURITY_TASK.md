VERDISCHAIN — FINAL P0 PRESALE ESCROW & ACCOUNTING SECURITY TASK

Repository: Protremix/Verdischain-
Branch: master

IMPORTANT:
Work only from the current repository state.
Inspect the existing implementation before making changes.
Do not rewrite unrelated architecture.
Do not change tokenomics, consensus, or public APIs unless required by this task.

OBJECTIVE:
Make the Presale payment flow economically safe, deterministic, auditable,
and resistant to double collection and DoS.

==================================================
P0 — REPLACE USER RESERVE WITH PRESALE ESCROW
==================================================

Current problem:
Presale currently reserves payment directly from the buyer. User reserved
balance is a global account-level resource and must not be used as the
accounting source for a specific presale round.

Implement:

Buyer
  ↓
payment transfer
  ↓
Presale Escrow Account
  ↓
Round accounting

Use one deterministic escrow account derived from T::PalletId for receiving
presale payments and holding presale VRDX inventory.

==================================================
P0 — PAYMENT MUST BE TRANSFERRED TO ESCROW
==================================================

Replace the current payment reservation model.

Instead of Currency::reserve(buyer, payment), transfer payment explicitly:

buyer → presale escrow

The contribution must not be recorded unless the payment transfer succeeds.

==================================================
P0 — TRACK ROUND-LEVEL RAISED AMOUNT
==================================================

Add explicit per-round accounting:

RoundRaised<RoundId, Balance>

Every successful contribution must atomically update:

- RoundRaised[round_id]
- TotalRaised
- Round.sold
- Contributions[(round_id, account)]

Use checked arithmetic. Do not use saturating arithmetic for financial
accounting.

==================================================
P0 — REWRITE collect_funds()
==================================================

Remove the current model that iterates over contributors and unreserves
individual user balances.

collect_funds() must NOT:
- iterate over every contributor
- inspect user reserved balances
- unreserve user balances
- transfer funds from individual users

Instead:

Presale Escrow → beneficiary

Use the recorded round raised amount.

The collection operation must be O(1), or properly bounded.

==================================================
P0 — PREVENT DOUBLE COLLECTION
==================================================

Add explicit state such as:

funds_collected: bool

First collection: SUCCESS
Second collection: FAIL

Add FundsAlreadyCollected or equivalent.

The state update and transfer must be atomic.

==================================================
P0 — COLLECTION ONLY AFTER ROUND COMPLETION
==================================================

Do not treat inactive as completed.

collect_funds() must verify:

current_block >= round.end_block

unless there is an explicitly designed emergency settlement mechanism.

Required tests:
1. Active round cannot be collected.
2. Deactivated-but-not-ended round cannot be collected.
3. Ended round can be collected.
4. Already-collected round cannot be collected again.

==================================================
P0 — PRESALE TOKEN ESCROW ACCOUNTING
==================================================

Verify that:

escrow VRDX balance >= total unclaimed/locked presale allocation

A contribution must fail if the presale escrow lacks sufficient VRDX.

Payment and token allocation must fail atomically.

==================================================
P0 — ATOMIC TRANSACTION REQUIREMENT
==================================================

Successful contribution must atomically perform:

- payment transferred to escrow
- VRDX transferred to buyer
- vesting created
- round sold updated
- round raised updated
- global totals updated
- account contribution updated

On failure, none of the financial state changes may remain.

Test failures at:
- insufficient payment
- insufficient VRDX escrow
- vesting failure
- arithmetic overflow
- invalid round
- allocation exceeded
- account cap exceeded

==================================================
P0 — PRESALE PRICE FORMULA
==================================================

Audit round.token_price.

The current calculation is:

token_amount = payment_amount * token_price

Explicitly define whether token_price means:
A) tokens per payment unit
or
B) payment units per token

If fixed-point pricing is required, implement explicit precision with checked
multiplication/division.

Document and test the exact formula using real token decimals, including:
- minimum payment
- large payment
- rounding
- overflow
- maximum allocation

==================================================
P0 — PER-ROUND ACCOUNTING
==================================================

Keep contributions keyed by:

(round_id, account_id)

Verify independently:
- total purchased
- total paid
- per-account cap

A user's Round A contribution must not consume Round B's cap.

Add regression tests.

==================================================
P0 — PER-ROUND WHITELIST
==================================================

Keep whitelist per round.

Round A: Alice allowed
Round B: Bob allowed

Alice must not automatically be allowed in B.
Bob must not automatically be allowed in A.

A round with no whitelist entries may remain public.

Add regression tests.

==================================================
P0 — VESTING
==================================================

Every successful presale purchase must create exactly one valid vesting
allocation equal to the purchased token amount.

Required invariant:

purchased tokens = vested allocation

No duplicate vesting allocation.
No vesting allocation without successful payment.
No payment without successful token allocation.

==================================================
P0 — ECONOMIC INVARIANTS
==================================================

Add tests proving:

RoundSold <= RoundAllocation
TotalSold <= total presale allocation
RoundRaised contributes exactly once to TotalRaised
RoundSold contributes exactly once to TotalSold
Collected funds never exceed RoundRaised
Collected funds cannot be collected twice
UserPurchased <= per-round account cap
Presale escrow VRDX balance is sufficient for allocations

==================================================
P0 — WEIGHT / DOS PROTECTION
==================================================

collect_funds() must NOT perform an unbounded loop over contributors.

If any operation has variable complexity:
- use bounded iteration
- add a limit
- use pagination/cursor
- or redesign it to O(1)

Do not use a fixed low weight for an unbounded operation.

==================================================
P1 — GENESIS VALIDATION
==================================================

Reject:
- zero price
- zero allocation
- zero/invalid cap where prohibited
- invalid block range
- empty vesting label
- oversized labels
- allocation inconsistencies

Do not silently convert invalid financial configuration to defaults.

==================================================
P1 — DPOS REGRESSION CHECK
==================================================

Do not undo the existing genesis stake reservation fix.

Verify genesis validators:
- have sufficient genesis balance
- have stake reserved
- appear in TotalStaked
- cannot spend reserved stake
- can be correctly unregistered/slashed according to runtime rules

==================================================
P1 — PALLET ID / ESCROW CONSISTENCY
==================================================

Verify Presale PalletId consistency across:
- runtime configuration
- chain spec
- genesis funding
- tests
- escrow calculations

There must be exactly one canonical Presale escrow account.

Verify the Tokenomics PalletId is not accidentally used as Presale escrow.

==================================================
P1 — SECURITY TESTING
==================================================

Act as an attacker.

Test:
- double collection
- collection before round end
- collection after manual deactivation
- fake contributor reserves
- insufficient escrow
- double contribution
- replayed contribution
- whitelist bypass
- cap bypass
- allocation bypass
- overflow
- underflow
- rounding abuse
- vesting duplication
- unauthorized admin
- malicious beneficiary
- zero-value edge cases
- maximum-value edge cases

==================================================
REQUIRED COMMANDS
==================================================

Run, where supported:

cargo fmt --all -- --check
cargo check --all-features
cargo test --workspace
cargo test --workspace --all-features
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo build --release
cargo build --release -p verdis-runtime --no-default-features --target wasm32v1-none

Run all Presale, Vesting and DPoS tests.

If try-runtime is available, execute the actual try-runtime validation.

Never claim a command passed unless it was actually executed.
If execution is impossible, report NOT VERIFIED and explain why.

==================================================
FINAL AUDIT REPORT
==================================================

Return:
1. Current commit
2. Files changed
3. Security issues found
4. Security issues fixed
5. Presale architecture before
6. Presale architecture after
7. Payment flow
8. Token flow
9. Vesting flow
10. Collection flow
11. Tests added
12. Tests executed
13. Exact test results
14. CI results
15. Remaining risks
16. Mainnet blockers

Mark every item:
FIXED / VERIFIED / NOT VERIFIED / BLOCKED / REQUIRES REVIEW

==================================================
DEFINITION OF DONE
==================================================

Complete only when:
- presale payments are held by Presale escrow
- user reserved balances are no longer used for presale collection
- round-level raised accounting exists
- collect_funds() is O(1) or properly bounded
- double collection is impossible
- collection before round completion is impossible
- payment/token/vesting operations are atomic
- token pricing formula is explicitly defined and tested
- per-round caps remain independent
- per-round whitelist remains independent
- economic invariants have tests
- DPoS genesis reservation remains correct
- Presale PalletId is consistent
- available tests pass
- clippy passes
- formatting passes
- WASM build passes

FINAL STATUS:
TESTNET READY
or
REQUIRES FIXES

Never report MAINNET READY until production validator keys, genesis,
consensus, economic security, and independent security-audit requirements
are separately verified.
