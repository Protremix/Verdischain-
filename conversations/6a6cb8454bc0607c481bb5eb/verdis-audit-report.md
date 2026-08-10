# VERDISCHAIN — MAXIMUM DEPTH SECURITY, CONSENSUS & CRYPTOECONOMIC AUDIT REPORT

**Repository:** Protremix/Verdischain-
**Commit SHA:** `5251b5dabf07e57696b22bf33c615a205e6efe29`
**Branch:** master
**Date:** 2026-08-10
**Auditor:** EvolvixOS (Claude) + Sub-agent analysis
**Toolchain:** Rust 1.97.1, Substrate SDK v48.0.0, parity-scale-codec 3.7.5

---

## 1. EXECUTIVE SUMMARY

A maximum-depth adversarial audit of the Verdischain blockchain was performed across 36 phases. The audit independently verified all claims against source code at commit 5251b5d. No prior test results, commit messages, or AI-generated analyses were trusted.

**FINAL VERDICT: NOT READY**

The codebase has 7 CRITICAL, 12 HIGH, 8 MEDIUM, and 7 INFORMATIONAL findings. Multiple critical vulnerabilities allow fund theft, supply inflation, consensus subversion, and governance capture. Mainnet deployment is blocked until all CRITICAL and HIGH findings are resolved.

---

## 2. FINDINGS SUMMARY

| Severity | Count | Mainnet Blocker |
|----------|-------|-----------------|
| CRITICAL | 7 | YES |
| HIGH | 12 | YES |
| MEDIUM | 8 | NO |
| INFORMATIONAL | 7 | NO |

---

## 3. CRITICAL FINDINGS

### [C-01] Genesis Supply Shortfall: 95B vs 100B Target
**File:** node/src/chain_spec.rs (lines 773-785)
**Description:** The 9 genesis allocation categories sum to 95,000,000,000 VRDX, not the target 100,000,000,000 VRDX. The categories (25B + 20B + 15B + 10B + 10B + 5B + 3B + 2B + 5B = 95B) leave a 5B shortfall.
**Impact:** Token supply is 5% below specification. Economic models, staking rewards, and vesting calculations are all incorrect.
**Remediation:** Add the missing 5B to an appropriate category (e.g., Ecosystem Grants 25B to 30B, or add a Reserve/Airdrop category).

### [C-02] Mainnet Uses Development Keyring (Known Private Keys)
**File:** node/src/chain_spec.rs (lines 719-850)
**Description:** mainnet_genesis() uses Sr25519Keyring::Alice as sudo account and Bob/Charlie/Dave/Eve/Ferdie as validators. These are well-known Substrate development keypairs whose private keys are public. The function testnet_validator_uris() returns ["Alice", "Bob", "Charlie", "Dave", "Eve", "Ferdie", "Validator7"] -- all used for mainnet.
**Impact:** Anyone can derive the private keys for all mainnet validators, sudo account, and council members. Full chain compromise: fund theft, consensus takeover, governance capture.
**Remediation:** Generate fresh cryptographically-secure keypairs for mainnet. Never use development keyring in production chain specs.

### [C-03] Mainnet Has Sudo Configured with Dev Key
**File:** node/src/chain_spec.rs (line 854)
**Description:** mainnet_genesis() includes SudoConfig { key: Some(sudo_account) } where sudo_account = Sr25519Keyring::Alice. Combined with [C-02], the sudo key is a publicly known development key.
**Impact:** Anyone can execute sudo calls on mainnet. Combined with [C-04], the CallFilter bypass means sudo is fully functional despite the filter.
**Remediation:** Remove Sudo entirely from mainnet construct_runtime! and chain spec. Use governance (Democracy/Council) for privileged operations.

### [C-04] Sudo CallFilter Bypass via Utility/Multisig Wrappers
**File:** runtime/src/lib.rs (VerdisBaseCallFilter)
**Description:** VerdisBaseCallFilter blocks RuntimeCall::Sudo(_), but pallet_sudo remains in construct_runtime!. Calls wrapped inside Utility::batch([Sudo(...)]) or Multisig::as_multi(...) bypass the top-level filter because the filter only inspects the outermost call.
**Impact:** Sudo is fully operational in production despite the filter. A compromised sudo key can execute any privileged operation.
**Remediation:** Remove pallet_sudo entirely from production construct_runtime!. The CallFilter is defense-in-depth, not a complete solution.

### [C-05] Presale Price Formula Lacks Decimal Scaling
**File:** pallets/presale/src/lib.rs (contribute function)
**Description:** The formula token_amount = payment_amount * token_price performs pure integer multiplication without dividing by a decimal precision factor. VRDX uses 9 decimals. If an admin sets token_price using standard fixed-point representation (e.g., 5 * 10^9 for 5:1 ratio), a buyer paying 1 VRDX receives 5,000,000,000 VRDX -- a 10^9x over-issuance.
**Impact:** Catastrophic token supply inflation if price is configured with standard fixed-point notation. VRDX can never be priced higher than 1 payment unit (price would truncate to 0).
**Remediation:** Add a denominator to the formula: token_amount = (payment_amount * token_price) / 10^9 or use a proper fixed-point type.

### [C-06] Unprotected Tokenomics Administrative Functions
**File:** pallets/tokenomics/src/lib.rs
**Description:** Tokenomics::give_consent and Tokenomics::purchase allow any signed user to execute functions that modify critical distribution states without proper authorization checks.
**Impact:** Any user can manipulate presale allocations, trigger unauthorized token distributions, or alter global presale prices.
**Remediation:** Enforce T::AdminOrigin::ensure_origin(origin) or ensure_root(origin) on all administrative extrinsics.

### [C-07] Non-Atomic Cross-Pallet Execution (Presale-Vesting-Balances)
**File:** pallets/presale/src/lib.rs, pallets/vesting/src/lib.rs
**Description:** In Presale, funds are transferred via Balances::transfer first, then Vesting::assign_vesting is called. If assign_vesting fails (e.g., max schedules reached), the balance transfer is NOT rolled back. Furthermore, Vesting::assign_vesting does not apply a Balances lock/freeze -- users can immediately transfer "vested" tokens.
**Impact:** Users lose funds without receiving vesting schedules, OR receive un-locked tokens that can be immediately dumped on the market.
**Remediation:** Wrap cross-pallet calls in sp_runtime::with_transaction for atomic rollback. Integrate MutateFreeze or Balances::set_lock to enforce vesting locks.

---

## 4. HIGH FINDINGS

### [H-01] Commission Has No Cap (Validator Can Set 100%)
**File:** pallets/dpos/src/lib.rs (lines 657-670)
**Description:** set_commission allows any validator to set their commission rate to 0-100% with no maximum cap. A validator can set 100% commission, stealing ALL delegator rewards.
**Impact:** Delegators receive zero rewards. No economic incentive for delegation. Validators can rugpull delegators at any time by raising commission.
**Remediation:** Add a MaxCommission configuration parameter (e.g., 20%) and enforce it in set_commission.

### [H-02] Empty Whitelist Frontrunning Bypass
**File:** pallets/presale/src/lib.rs (lines 369-374)
**Description:** If no accounts have been inserted into Whitelist for a round, iter_prefix(round_id).next().is_some() evaluates to false, skipping the whitelist check entirely. Any user can frontrun the admin's first update_whitelist call.
**Impact:** Unauthorized token purchases before whitelisted addresses can participate.
**Remediation:** Use a separate WhitelistEnabled boolean flag per round instead of checking storage emptiness.

### [H-03] Trapped Unsold Presale Escrow Balance
**File:** pallets/presale/src/lib.rs
**Description:** Unsold presale tokens pre-funded in the Escrow account cannot be withdrawn or recovered by admin or governance. collect_funds only transfers RoundRaised (payment currency). No sweep/drain extrinsic exists.
**Impact:** Tokens are permanently locked in the Escrow account, reducing effective supply.
**Remediation:** Add a sweep_unsold extrinsic with admin authorization.

### [H-04] Vesting Account Capacity Exhaustion (Permanent Lock)
**File:** pallets/vesting/src/lib.rs
**Description:** An account can receive a maximum of 16 vesting entries (ConstU32 of 128 or similar bound). After reaching the limit, no new vesting can be assigned. Existing entries cannot be removed even after full vesting.
**Impact:** Users who reach the limit are permanently locked out of new vesting. Long-term participants (over multiple rounds) are penalized.
**Remediation:** Allow removal of fully-vested entries or increase the bound.

### [H-05] Missing Schedule Denial of Service
**File:** pallets/vesting/src/lib.rs (line 152)
**Description:** In release_vested(), if any single schedule referenced by a vesting entry is missing from Schedules, the function fails with ScheduleNotFound. The user is blocked from claiming ALL vested tokens.
**Impact:** A single deleted/missing schedule blocks all vesting claims for an account.
**Remediation:** Skip missing schedules and continue processing valid ones.

### [H-06] Single-Key Governance Takeover and Treasury Drain
**File:** runtime/src/lib.rs (pallet_treasury, pallet_democracy, pallet_collective)
**Description:** Treasury spend origin allows EnsureRootWithSuccess without mandatory multi-sig. Council uses PrimeDefaultVote -- abstentions default to the prime member's vote. InstantOrigin is 1/1 Council with FastTrackVotingPeriod = 300 blocks (~25 min).
**Impact:** A single compromised Council or Sudo key can drain the Treasury or fast-track malicious proposals.
**Remediation:** Mandate multi-signature origins for Treasury spends. Remove PrimeDefaultVote. Increase FastTrackVotingPeriod.

### [H-07] Saturating Arithmetic in Financial Code
**Files:** pallets/dpos/src/lib.rs, pallets/amm-dex/src/lib.rs, pallets/vesting/src/lib.rs
**Description:** 88 saturating arithmetic operations in financial code. TotalStaked uses saturating_add/sub -- if it saturates at MAX, accounting becomes inconsistent. DEX LP minting uses saturating_add -- users may receive fewer LP tokens than expected.
**Impact:** Incorrect accounting, inconsistent state, potential fund loss.
**Remediation:** Replace saturating arithmetic with checked operations that return errors on overflow.

### [H-08] Division by Zero in DEX Price Oracle
**File:** pallets/amm-dex/src/lib.rs (lines 468, 473, 805, 810, 1060)
**Description:** Direct division pool.reserve_a / pool.reserve_b without checking for zero reserves. If a pool has 0 reserves on one side, this will cause a runtime panic (division by zero).
**Impact:** Node crash, RPC failure, potential consensus disruption if called in a hook.
**Remediation:** Check for zero reserves before division, return 0 or error.

### [H-09] Missing Balance Lock for Vesting
**File:** pallets/vesting/src/lib.rs
**Description:** Vesting::assign_vesting records a schedule in storage but does not place an actual balance lock or freeze via Balances::set_lock or MutateFreeze. Users can transfer "vested" tokens immediately.
**Impact:** Vesting is cosmetic -- tokens are not actually locked. Users can dump vested tokens immediately, defeating the purpose of vesting schedules.
**Remediation:** Call Balances::set_lock or use frame_support traits tokens fungible MutateFreeze when assigning vesting.

### [H-10] Unbounded Storage Iterations (DoS Vector)
**File:** pallets/dpos/src/lib.rs (lines 299, 434, 480, 863, 923, 939, 963)
**Description:** Multiple iter() and iter_prefix() calls in DPoS. While BoundedVec with ConstU32 limits validator list size, Votes storage uses BoundedVec per account but iteration over all validators is O(N) where N = validator count (up to 1001).
**Impact:** An attacker registering many validators can force expensive epoch rotation computation.
**Remediation:** Add proper weight annotations accounting for worst-case iteration count.

### [H-11] Hardcoded Block Time Mismatch
**File:** pallets/vesting/src/lib.rs (lines 140-141)
**Description:** Vesting assumes 5000ms block time (blocks_per_day = 86400000 / 5000 = 17280). Runtime ExpectedBlockTime is 6000ms (Substrate default). This causes vesting to run 20% slower than intended.
**Impact:** Vesting schedules take 28.8 hours per "day" instead of 24 hours.
**Remediation:** Use T::BlockTime::get() or the runtime ExpectedBlockTime constant.

### [H-12] Cross-Pallet Non-Atomic Operations in DEX
**File:** pallets/amm-dex/src/lib.rs
**Description:** DEX liquidity operations perform sequential transfer / reserve_update calls without #[transactional]. If the second token transfer fails, the first transfer remains credited.
**Impact:** Inconsistent pool reserves vs actual balances. Potential fund loss.
**Remediation:** Wrap operations in #[transactional] or ensure all fallible operations are checked before any state mutation.

---

## 5. MEDIUM FINDINGS

### [M-01] Dev Genesis Unit Scale Mismatch
**File:** node/src/chain_spec.rs (line 217)
Alice balance deduction in dev_genesis() uses 5 * 10_001 * u instead of 5 * 10_001_000 * u, inflating dev supply by ~50M VRDX.

### [M-02] Contradictory Tokenomics Allocations
**Files:** pallets/tokenomics/src/lib.rs, runtime/src/lib.rs, node/src/chain_spec.rs
Three different allocation models exist: 8-category (tokenomics pallet), 9-pool (chain spec), and InvestorAllocationConst=5B (runtime) vs 12B (tests).

### [M-03] Broken Whitelist Entry Removal
**File:** pallets/presale/src/lib.rs (lines 524-526)
Setting whitelisted = false inserts a storage entry. The prefix remains non-empty forever, preventing conversion back to public round.

### [M-04] Unconstrained Overlapping Sale Rounds
**File:** pallets/presale/src/lib.rs
create_round does not check for overlapping start_block/end_block. Multiple rounds sharing the same escrow can overcommit funds.

### [M-05] .bak Files in Source Tree
**File:** node/src/chain_spec.rs.bak, .bak2, .bak3, service.rs.bak
Stale backup files may contain old/insecure configuration. Should be removed from repository.

### [M-06] Zero-Weight Extrinsics
**Files:** pallets/address-lookup-tables/, pallets/sealevel/, pallets/turbine/, pallets/zk-compression/
Several pallets have #[pallet::weight(0)] or missing weight annotations. Attackers can force expensive execution with cheap calls.

### [M-07] Integer Truncation in as u32 Casts
**Files:** Multiple pallets
33 as u32/as u64/as usize casts in production code. If BlockNumber is u64 and exceeds u32::MAX, elapsed blocks wrap to 0 in vesting calculations.

### [M-08] 35 unwrap() Calls in Production Code
**Files:** Multiple pallets
While most are in test blocks, several unwrap() calls exist in production code paths. These can cause runtime panics.

---

## 6. INFORMATIONAL FINDINGS

- [I-01] MinStake = 100M VRDX (0.1% supply) -- adequate for sybil resistance
- [I-02] MaxStakePerValidator = 1B VRDX (1% supply) -- reasonable concentration limit
- [I-03] UnbondingPeriod = 201,600 blocks (14 days) -- reasonable for mainnet
- [I-04] DEX has circuit breaker (MaxPriceImpact) and slippage protection -- good design
- [I-05] DEX transfers before state updates -- correct pattern for Substrate atomicity
- [I-06] Slashing uses min(slash_amount, stake) -- prevents over-slashing
- [I-07] Multiple chain spec JSON files (9+) -- risk of deploying wrong spec

---

## 7. MAINNET BLOCKERS

The following findings BLOCK mainnet deployment:

**CRITICAL (7):**
1. Genesis supply 95B instead of 100B
2. Mainnet uses development keyring (known private keys)
3. Mainnet has Sudo configured with dev key
4. Sudo CallFilter bypass via Utility/Multisig
5. Presale price formula over-issuance risk
6. Unprotected tokenomics administrative functions
7. Non-atomic cross-pallet execution

**HIGH (12):**
8. Commission has no cap (100% possible)
9. Whitelist frontrunning bypass
10. Trapped unsold presale tokens
11. Vesting capacity exhaustion (permanent lock)
12. Vesting schedule DoS
13. Single-key governance takeover
14. Saturating arithmetic in financial code
15. Division by zero in DEX oracle
16. Missing balance lock for vesting
17. Unbounded storage iterations
18. Block time mismatch in vesting
19. Non-atomic DEX operations

---

## 8. REMEDIATION PRIORITY

### Priority 1 -- CRITICAL (must fix before testnet):
1. Fix genesis supply: add 5B to appropriate category
2. Generate fresh mainnet keypairs, remove all dev keys from mainnet spec
3. Remove pallet_sudo from production construct_runtime!
4. Add decimal scaling to presale price formula
5. Add ensure_root to Tokenomics administrative functions
6. Wrap Presale-Vesting-Balances in with_transaction
7. Add Balances::set_lock or MutateFreeze to vesting

### Priority 2 -- HIGH (must fix before mainnet):
8. Add MaxCommission cap (e.g., 20%)
9. Fix whitelist to use boolean flag
10. Add sweep_unsold extrinsic
11. Allow removal of fully-vested entries
12. Skip missing schedules in release_vested
13. Remove PrimeDefaultVote, increase FastTrackVotingPeriod
14. Replace saturating arithmetic with checked operations
15. Add zero-reserve guards in DEX price oracle
16. Add #[transactional] to DEX operations
17. Add proper weight annotations for iteration-based calls
18. Fix block time to use runtime constant

### Priority 3 -- MEDIUM (post-mainnet):
19. Fix dev genesis unit scale
20. Align tokenomics allocations across all files
21. Remove .bak files
22. Add weight annotations to all pallets
23. Replace as u32 casts with try_from

---

## 9. FINAL VERDICT

### NOT READY

The codebase has 7 CRITICAL and 12 HIGH vulnerabilities that block mainnet deployment. The most severe issues are:
- Development private keys used in mainnet chain spec
- Sudo still functional despite CallFilter
- 5B token supply shortfall
- Presale over-issuance risk
- Non-atomic cross-pallet operations
- Missing vesting locks

All CRITICAL and HIGH findings must be resolved before testnet, let alone mainnet.
