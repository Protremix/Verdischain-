# Verdis Chain Pre-Audit Internal Review
**Date:** August 10, 2026
**Reviewer:** EvolvixOS Agent
**Commits:** 0d360a5, e847d7a
**Status:** Fixes applied, 249 tests pass

## 1. DPoS Slashing — CRITICAL (FIXED)

### Issue: Silent Error Ignoring in do_slash and slash_validator
- **Severity:** CRITICAL
- **Description:** do_slash() and slash_validator() used `let _` to ignore unreserve and transfer errors. If unreserve failed (partial shortfall) or transfer failed, storage was still updated — creating accounting mismatches.
- **Fix:** Track unreserve return value (shortfall). Calculate actual_slash. Abort if transfer fails. Zero-amount slashes early-return.
- **Commit:** 0d360a5

### Issue: reward_block_producer ignores transfer errors
- **Severity:** HIGH
- **Description:** Silent transfer failure meant validator got blocks_produced++ without receiving funds.
- **Fix:** Check transfer result, abort on failure.
- **Commit:** 0d360a5

## 2. DEX Native Token Swap — CRITICAL (FIXED)

### Issue: Non-LP traders lose input tokens
- **Severity:** CRITICAL
- **Description:** Native token swap used reserve/unreserve on the trader own account. Non-LP traders had 0 reserved balance, so unreserve did nothing. Trader lost amount_in and received 0 output.
- **Fix:** Refactored add_liquidity, remove_liquidity, and swap to use Currency::transfer to/from DEX pool account (PalletId), matching the fungible token pool pattern.
- **Commit:** e847d7a

## 3. Remaining Issues (Not Yet Fixed)

### 3.1 Slashed Validators Permanently Removed — MEDIUM
- slashed=true, active=false with no recovery path.
- Recommendation: Add reactivate_validator with cooldown.

### 3.2 Delegators Not Slashed — MEDIUM
- Only validator stake slashed. Delegators face no consequences.
- Recommendation: Slash delegator stakes proportionally.

### 3.3 No Validator Commission — LOW
- Recommendation: Add commission field.

### 3.4 Green Score Not in Selection — LOW
- rotate_epoch sorts by total_votes only.
- Recommendation: Weight by green score.

### 3.5 Reward Pool Depletion — LOW
- No mechanism to replenish.
- Recommendation: Governance call to refill.

## 4. What's Working Well

- Automatic BABE/GRANDPA equivocation slashing (5%)
- 14-day unbonding period
- Session rotation tied to BABE epochs (500 blocks)
- DEX arithmetic uses checked_mul/checked_sub (no overflow)
- DEX circuit breaker and slippage protection
- Reward pool pre-funded (no inflation minting)

## 5. Economic Parameters

| Parameter | Value | Assessment |
|-----------|-------|------------|
| BlockReward | 342 VRDX | ~1.8B/year, 9% APR at 20B staked |
| MinStake | 10M VRDX | 0.01% — may be too low for sybil resistance |
| MaxStake | 1B VRDX | 1% — reasonable cap |
| MaxValidators | 100 | Good for expansion |
| ActiveValidatorCount | 7 | Mainnet target |
| UnbondingPeriod | 14 days | Industry standard |
| DEX Fee | 0.3% | Standard |

## 6. Next Steps

1. Fix remaining MEDIUM issues (3.1, 3.2)
2. Fund DEX pool account in genesis
3. Re-seed DEX pools on fresh chain
4. Re-genesis chain with updated binary
5. External security audit
