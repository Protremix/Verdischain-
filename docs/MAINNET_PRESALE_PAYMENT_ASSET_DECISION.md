# VERDIS CHAIN — MAINNET PRESALE PAYMENT ASSET DECISION

**Date:** 2026-08-23  
**Author:** Arlo (Chief Engineer & Technical Security Authority)  
**Status:** PENDING OWNER APPROVAL  
**Constitution Reference:** Article 21 (Mainnet GO/NO-GO gates)

---

## 1. ARCHITECTURE ANALYSIS

### What `PaymentCurrency` Requires

The presale pallet's `Config` trait (pallets/presale/src/lib.rs:415) requires:

```rust
type PaymentCurrency: Currency<Self::AccountId, Balance = BalanceOf<Self>>;
```

This means `PaymentCurrency` must implement `frame_support::traits::Currency<AccountId>`.

### Types Implementing `Currency<AccountId>` in the Current Runtime

| Type | Implements `Currency` | In `construct_runtime!` | Available |
|---|---|---|---|
| `MaxSupplyCurrency` | ✅ (wraps `Balances`) | ✅ (via `Balances`) | ✅ YES |
| `pallet_balances::Pallet` | ✅ (native) | ✅ (Instance 1) | ✅ YES |
| `pallet_fungible_tokens::Pallet` | ❌ NO | ✅ (Instance 1) | ❌ NO |
| `pallet_assets::Pallet` | ✅ (via adapter) | ❌ COMMENTED OUT | ❌ NO |

### Types NOT Available

1. **`pallet_fungible_tokens`** — Has its own `TokenBalances` storage (DoubleMap: token_id → account → u128) and dispatchables (create/mint/burn/transfer), but does NOT implement the `Currency<AccountId>` trait. Would require a `Currency` adapter wrapper.

2. **`pallet_assets` (Substrate Assets)** — Config impl exists (runtime/src/lib.rs:1094) but is COMMENTED OUT in `construct_runtime!` (line 1516: `// Assets: pallet_assets = 40, // need compatible version`). NOT in the runtime. Would need enabling + a `Currency` adapter.

3. **Second `pallet_balances` instance** — Only one `Balances` instance exists (Instance 1, pallet index 4). Adding a second instance would require code changes.

4. **External tokens (ORML, stablecoins)** — No ORML, USDT, USDC, or any external token dependencies in `Cargo.toml`.

### Only Technically Available Option (No Code Changes)

**Native VRDX via `MaxSupplyCurrency`** — The ONLY type that:
- Implements `Currency<AccountId, Balance = BalanceOf<Runtime>>`
- Is active in `construct_runtime!`
- Requires zero code changes

---

## 2. MAINNET PAYMENT ASSET DETERMINATION

```
TESTNET PAYMENT ASSET  = VRDX (native, MaxSupplyCurrency)
MAINNET PAYMENT ASSET = VRDX (native, MaxSupplyCurrency)
```

### Why VRDX is the Only Option Without Code Changes

The current architecture has exactly ONE type implementing `Currency<AccountId>` that is active in the runtime: `MaxSupplyCurrency` (which wraps `pallet_balances`).

No other asset, token, or stablecoin is technically available as `PaymentCurrency` without:
- Writing a `Currency` adapter for `pallet_fungible_tokens`
- Enabling `pallet_assets` + writing an adapter
- Adding a second `pallet_balances` instance
- Adding external token dependencies (ORML, etc.)

All of these require code changes and additional security review.

### Economic Model: Bonus-Rate Presale

With `Currency = PaymentCurrency = MaxSupplyCurrency` (VRDX):

- **Buyer pays** VRDX → escrow receives VRDX (PaymentCurrency transfer)
- **Escrow distributes** VRDX → buyer receives bonus VRDX (Currency transfer)
- **Formula**: `token_amount = payment_amount × token_price / price_precision`
- **Example**: pay 100 VRDX at price=5, precision=1 → receive 500 VRDX (5× bonus)
- **Escrow pre-funding**: escrow must hold `total_allocation` VRDX before round starts

This is a **bonus-rate / early-bird** model, NOT a capital-raising model. Buyers are existing VRDX holders receiving bonus tokens. No external capital (USD, stablecoins) is raised.

---

## 3. FULL DOCUMENTATION (13 Points)

### 1. Exact Asset/Token
**VRDX** — Native Verdis Chain token, transferred via `MaxSupplyCurrency` (which wraps `pallet_balances`).

### 2. Decimals
**9** (9 decimals, as defined by `UNITS` constant in runtime/src/lib.rs). `Balance = u128`, `1 VRDX = 1,000,000,000` smallest units.

### 3. Asset Identifier
- **Pallet**: `pallet_balances` (Instance 1, pallet index 4)
- **Wrapper**: `MaxSupplyCurrency` (runtime/src/max_supply_currency.rs)
- **Type**: `type PaymentCurrency = MaxSupplyCurrency;` (runtime/src/lib.rs:888)
- **SS58 prefix**: 42 (standard Substrate)
- **No external asset ID** — native chain token

### 4. How the Presale Receives It
`contribute()` dispatchable (pallets/presale/src/lib.rs:644):
1. Buyer signs `contribute(round_id, payment_amount)`
2. `T::PaymentCurrency::transfer(who, escrow, payment_amount, ...)` — transfers VRDX from buyer to per-round escrow account
3. Escrow account: `PresalePalletId::get().into_sub_account_truncating(round_id)` — unique per round (in production with AccountId32)
4. `RoundRaised[round_id]` incremented by `payment_amount`
5. `TotalRaised` global counter incremented

### 5. How Refunds Are Made
`claim_refund()` dispatchable (pallets/presale/src/lib.rs:942):
1. User calls `claim_refund(round_id)` on a Failed or Cancelled round
2. `T::PaymentCurrency::transfer(escrow, who, refund_amount, ...)` — returns payment VRDX from escrow to buyer
3. `T::Currency::transfer(who, escrow, tokens_to_return, ...)` — returns bonus VRDX from buyer to escrow
4. Contribution record deleted (CEI pattern — state cleared first)
5. `RoundRaised[round_id]` and `TotalRaised` decremented

### 6. How Escrow Accounts Hold It
- Escrow = `PalletId(*b"verdisps")` + `round_id` sub-account
- Escrow holds BOTH: payment VRDX (from contributions) AND token allocation VRDX (pre-funded at genesis)
- Escrow balance = initial_allocation + total_payments − total_tokens_distributed
- Pre-funded via genesis config or admin transfer before round activation
- In production (AccountId32): each round gets a distinct escrow account

### 7. How Collection Transfers It
`collect_funds()` dispatchable (pallets/presale/src/lib.rs:855):
1. Admin (Council 2/3) calls `collect_funds(round_id, beneficiary)` on a Successful round
2. `T::PaymentCurrency::transfer(escrow, beneficiary, RoundRaised[round_id], ...)` — transfers ALL payment VRDX to beneficiary
3. `RoundFundsCollected[round_id]` set to `true` (prevents double collection)
4. Round status → `Closed`
5. Unsold token VRDX swept to Treasury via `T::Currency::transfer`

### 8. Who Controls the Payment Asset
- **Token issuer**: `pallet_tokenomics` (mints/burns VRDX, enforces 100B cap via `MaxSupplyCurrency`)
- **Escrow controller**: Presale pallet logic (no manual access — PalletId-derived account, no private key)
- **Collection authority**: Council 2/3 (`EnsureProportionAtLeast<_, Instance1, 2, 3>`)
- **Treasury**: `TreasuryAccount` (defined in runtime, currently PalletId `verdist0`, to be replaced with 3-of-5 multisig)
- **No single party** can unilaterally access escrow funds — all transfers are pallet-enforced

### 9. Whether Native or External
**NATIVE** — VRDX is the native chain token, minted by `pallet_tokenomics`, stored in `pallet_balances`, wrapped by `MaxSupplyCurrency`. No external dependency, no bridging, no oracle, no cross-chain interaction.

### 10. Required Runtime Configuration
**Current configuration is already correct for VRDX-as-payment:**
```rust
// runtime/src/lib.rs:885-897
impl pallet_presale::Config for Runtime {
    type Currency = MaxSupplyCurrency;           // VRDX token distribution
    type PaymentCurrency = MaxSupplyCurrency;    // VRDX payment collection
    type PalletId = PresalePalletId;
    type AdminOrigin = Council 2/3;
    type Vesting = PresaleVestingHandler;
    type WeightInfo = pallet_presale::SubstrateWeight<Runtime>;
    type Treasury = TreasuryAccount;
    type EnforceUniqueVestingLabels = ConstBool<true>;
}
```

**No configuration change needed** for VRDX-as-payment mainnet. The only change required is replacing `TreasuryAccount` PalletId with the 3-of-5 multisig address (already documented as a mainnet blocker).

### 11. Required Tests
**Already passing (261 presale tests, 734 workspace tests, 0 failures):**
- MASTER-9 (27 tests): escrow isolation, refund atomicity, double-refund/collection protection, supply cap enforcement, Luna adversarial
- Integration (20 tests): presale→vesting atomic flow
- All MASTER-1 through MASTER-8 regression tests

**No additional tests required** for VRDX-as-payment — all payment paths use `MaxSupplyCurrency` which is already fully tested.

**If a separate payment asset is later desired** (future phase):
- New `Currency` adapter implementation tests
- Cross-asset escrow balance verification
- Refund atomicity with separate Currency/PaymentCurrency
- Collection with separate asset
- These would require a new test suite and full audit

### 12. Security Implications

**VRDX-as-Payment (current architecture):**

| Aspect | Assessment |
|---|---|
| Custody risk | ✅ LOW — no external asset custody, everything native |
| Oracle risk | ✅ NONE — no price feeds needed |
| Bridge risk | ✅ NONE — no cross-chain interaction |
| Double-spend | ✅ BLOCKED — Substrate transaction atomicity + CEI pattern |
| Escrow isolation | ✅ VERIFIED — per-round RoundRaised tracking (MASTER-9 test 01) |
| Supply cap | ✅ ENFORCED — `MaxSupplyCurrency` hard cap at 100B (max_supply_currency.rs:44) |
| Admin key risk | ✅ MITIGATED — Council 2/3 multisig for collect_funds |
| Refund reentrancy | ✅ BLOCKED — CEI pattern, state cleared before transfers |

**Economic risk (VRDX-as-Payment):**

| Aspect | Assessment |
|---|---|
| Capital raising | ⚠️ NOT POSSIBLE — presale distributes VRDX, does not raise external capital |
| Price discovery | ⚠️ BONUS-RATE — price denominated in VRDX (not USD/stablecoin) |
| Circular dependency | ⚠️ PRESENT — buyers need VRDX to buy VRDX (early holders only) |
| Market dynamics | ⚠️ BONUS MODEL — rewards existing holders, does not attract new capital |

**No security vulnerability** is introduced by using VRDX as both Currency and PaymentCurrency. The separation in the trait (two separate type parameters) ensures all payment paths use `PaymentCurrency` and all token distribution paths use `Currency`, even though they resolve to the same underlying type. The economic model is a design decision, not a security issue.

### 13. Whether Separate Audit/Review Required

**For VRDX-as-Payment (no code change):**
- **Security audit**: NOT REQUIRED for the payment asset specifically — already covered by the existing presale audit (261 tests, MASTER-1 through MASTER-9)
- **Economic review**: RECOMMENDED — the bonus-rate model should be reviewed by an economist/tokenomics advisor to confirm it achieves the project's fundraising goals
- **External audit**: Still required per Constitution Article 21 (independent security audit of full runtime)

**For a separate payment asset (future, if desired):**
- **Security audit**: REQUIRED — new `Currency` adapter, new escrow interaction, new refund/collection paths
- **Full regression**: REQUIRED — all 261 presale tests + new cross-asset tests
- **Independent review**: REQUIRED — new code paths, new attack surfaces

---

## 4. DECISION SUMMARY

```
TESTNET PAYMENT ASSET          = VRDX (native, MaxSupplyCurrency)

MAINNET PAYMENT ASSET          = VRDX (native, MaxSupplyCurrency)
                                 (ONLY technically available option
                                  without code changes)

MAINNET CONFIGURATION REQUIRED = NO  (current config works as-is)

CODE CHANGE REQUIRED           = NO  (if using VRDX-as-payment)
                                    YES (if separate payment asset desired)

ADDITIONAL SECURITY REVIEW     = NO  (for VRDX-as-payment specifically)
                                 YES  (for any future separate asset)

PRESALE SECURITY STATUS        = PASS
  (261 presale tests, 27 MASTER-9 evidence tests,
   20 integration tests, 734 workspace tests, 0 failures,
   all Luna adversarial attacks BLOCKED)

MAINNET PRESALE STATUS         = READY (code-level)
                                 NOT READY (external gates:
                                   independent audit,
                                   key ceremony,
                                   legal entity,
                                   Treasury multisig replacement)
```

---

## 5. CRITICAL NOTE FOR ROJS

The current architecture supports a **bonus-rate presale** where buyers pay VRDX and receive bonus VRDX. This does NOT raise capital in USD, stablecoins, or any external asset.

If the goal is to raise capital in a non-VRDX asset (USDC, USDT, fiat-pegged token), this requires:
1. Enabling `pallet_assets` or writing a `Currency` adapter for `pallet_fungible_tokens`
2. New runtime configuration for `PaymentCurrency`
3. New test suite
4. Additional security audit
5. ~2-4 weeks engineering effort (estimate)

**Decision required from Rojs:**
- **Option A**: Accept VRDX-as-payment (bonus-rate model, no code change, mainnet-ready)
- **Option B**: Specify a separate payment asset (requires code change + audit + timeline)

No code will be modified until this decision is explicitly approved.
