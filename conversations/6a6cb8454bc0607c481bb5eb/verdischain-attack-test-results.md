# VERDISCHAIN — ATTACK TEST RESULTS SUPPLEMENT

**Date:** 2026-08-12  
**Supplement to:** verdischain-verification-report.md  

---

## SECTION 5: BALANCES AND TOKEN SYSTEM — PARTIALLY VERIFIED
- Standard FRAME Balances v50.0.0 (Parity-audited)
- Attack testing relies on FRAME pallet security guarantees
- Token: VRDX, 9 decimals, SS58 909

## SECTION 8: DPoS ATTACK TESTING — ✅ ALL PROTECTED

**Test Results:** 73 passed, 0 failed (64.80s)

| Attack Vector | Status | Code Evidence |
|---------------|--------|---------------|
| Double registration | ✅ PROTECTED | Lines 350-353: `Validators::contains_key` check |
| Unauthorized activation | ✅ PROTECTED | Lines 735-753: `who == validator` + `ValidatorNotFound` + `MinStake` |
| Stake inflation | ✅ PROTECTED | Lines 356-372, 444-463: `T::Currency::reserve` enforced |
| Reward duplication | ✅ PROTECTED | Lines 936-976: Rewards from pool, not minted. No user-callable claim |
| Slashing bypass | ✅ PROTECTED | Line 623: `ensure_root` for slash. Lines 659-660: `slashed=true, active=false`. Unbonding period enforced |
| Cartel scenario | ✅ PROTECTED | `MaxStakePerValidator` cap, `AlreadyVoted` check, deterministic sort |

## SECTION 12: PRESALE ATTACK TESTING — ✅ ALL PROTECTED

**Test Results:** 87 passed, 0 failed

| Attack Vector | Status | Code Evidence |
|---------------|--------|---------------|
| Double purchase | ✅ PROTECTED | Lines 487-495: Cumulative `Contributions` tracking |
| Cap bypass | ✅ PROTECTED | Lines 492-495 (per-account), 502-505 (phase total) |
| Overflow | ✅ PROTECTED | Lines 475-520: All `checked_mul/div/add` |
| Unauthorized activation | ✅ PROTECTED | Lines 413, 426: `T::AdminOrigin::ensure_origin` |
| Refund abuse | ✅ PROTECTED | Lines 725-735: Contribution removed before transfer |
| Premature vesting claim | ✅ PROTECTED | Vesting delegated to `pallet_vesting`, not in presale |

## SECTION 13: VESTING ATTACK TESTING — ✅ ALL PROTECTED

**Test Results:** 44 passed, 0 failed (0.06s)

| Attack Vector | Status | Code Evidence |
|---------------|--------|---------------|
| Premature claim (before cliff) | ✅ PROTECTED | Line 266: `if elapsed_days < schedule.cliff_days` skips release |
| Double claim | ✅ PROTECTED | Line 72: `released` field tracks claimed. Line 280: `releasable = total - released` |
| Overflow | ✅ PROTECTED | Lines 257-330: All `checked_sub/mul/add` |
| Unauthorized modification | ✅ PROTECTED | Lines 199, 238: `ensure_root` for add/assign. Line 246: `ensure_signed` for claim only |
| Invariant (allocated = claimed + remaining) | ✅ PROTECTED | Lines 335-342: `LockedBalances` tracking + zero cleanup |
| Zero cliff edge case | ✅ PROTECTED | Line 211: `cliff_days <= vesting_days`. Zero cliff = immediate vesting (test line 1139) |

## SECTION 14: DEX/AMM ATTACK TESTING — 6 PROTECTED, 2 VULNERABLE

**Test Results:** 35 passed, 0 failed (0.12s)

| Attack Vector | Status | Code Evidence |
|---------------|--------|---------------|
| AMM invariant (x*y=k) | ✅ PROTECTED | Lines 755-763: `ensure!(k_after >= k_before)` enforced |
| Slippage protection | ✅ PROTECTED | Lines 656, 713: `min_amount_out` enforced |
| Price manipulation | ✅ PROTECTED | Lines 702-711: `MaxPriceImpact` circuit breaker |
| LP overflow | ✅ PROTECTED | All `checked_mul/checked_add` |
| LP underflow | ✅ PROTECTED | All `checked_sub`, balance checks |
| Div-by-zero | ✅ PROTECTED | Zero checks before all divisions |
| **Reentrancy** | ⚠️ **VULNERABLE** | Lines 719-765: Transfers BEFORE state updates (CEI violation) |
| **Flash loan / oracle** | ⚠️ **VULNERABLE** | Lines 1147-1153: Spot price only, no TWAP |

### Finding 14.1 — Reentrancy (Medium-High)

**Description:** The `swap` and `swap_token` functions execute token transfers BEFORE updating storage state. The code comments say "Transfers FIRST (before state update for atomicity)" at line 719.

**Risk Assessment:** In Substrate's native execution model, reentrancy within a single pallet call is unlikely because:
- `T::Currency::transfer` (native balance) is a trusted operation
- However, `T::TokenHandler::transfer` (fungible tokens) could delegate to smart contract code
- If a malicious token contract is registered, it could reenter the AMM with stale reserves

**Fix:** Move storage updates before external transfers (CEI pattern):
1. Calculate new reserves
2. Update Pools storage
3. Execute transfers

### Finding 14.2 — No TWAP Oracle (Medium)

**Description:** The `pool_price` function returns instant spot price (`reserve_a / reserve_b`) without time-weighted averaging.

**Risk Assessment:** If external protocols (oracles, lending, liquidations) use `pool_price` as a price feed, an attacker can:
1. Swap to manipulate price (up to MaxPriceImpact limit)
2. Read manipulated price in same block
3. Swap back

**Fix:** Implement TWAP with cumulative price accumulators updated on each swap. Store `(price_cumulative, timestamp)` and compute average over time window.

## SECTION 19: KEY SECURITY — ✅ VERIFIED

| Check | Status | Evidence |
|-------|--------|----------|
| Private keys in source | ✅ NONE | grep across all .rs files: 0 matches |
| Mnemonics in source | ✅ NONE | grep: 0 matches |
| API keys/tokens in source | ✅ NONE | grep: 0 matches |
| .env files | ✅ NONE | No .env files found |
| Git history secrets | ✅ NONE | Deleted wallet.html had UI text only, no actual keys |
| Server-side custody | ✅ NONE | TX Relay v3: "No signing keys on server. Only pre-signed extrinsics accepted." |
| systemd service secrets | ✅ NONE | No SECRET/PRIVATE_KEY/MNEMONIC in service files |
| Faucet secrets | ✅ NONE | No secrets in faucet code |
| Mainnet placeholder keys | ⚠️ WARNING | `//MAINNET_VALIDATOR_1-21` must be replaced before mainnet |

## SUMMARY OF ALL ATTACK TESTS

| Pallet | Tests | Passed | Failed | Attack Vectors Protected | Vulnerable |
|--------|-------|--------|--------|-------------------------|------------|
| DPoS | 73 | 73 | 0 | 6/6 | 0 |
| Presale | 87 | 87 | 0 | 6/6 | 0 |
| Vesting | 44 | 44 | 0 | 6/6 | 0 |
| DEX/AMM | 35 | 35 | 0 | 6/8 | 2 (Reentrancy, No TWAP) |
| **TOTAL** | **239** | **239** | **0** | **24/26** | **2** |

### Combined test count (all pallets + runtime): 446 tests, 0 failures
