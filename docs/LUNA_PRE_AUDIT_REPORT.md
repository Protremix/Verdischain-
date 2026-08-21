# LUNA — FINAL PRE-AUDIT DISCOVERY REPORT
## Verdis Chain Production-Intended Codebase
## Date: 2026-08-21 | Operation: Luna First Run

---

## CRITICAL

### C1. IBC recv_packet mints tokens via deposit_creating without MaxSupplyCurrency cap
- **File:** pallets/ibc/src/lib.rs
- **Function:** recv_packet (line 488)
- **Component:** IBC pallet
- **Risk:** `T::Currency::deposit_creating(&receiver_account, mint_amount)` bypasses the MaxSupplyCurrency wrapper if the IBC pallet's Currency type is configured against raw Balances instead of MaxSupplyCurrency. This creates unbounded minting of native VRDX tokens, breaking the 100B supply cap invariant.
- **Exploit scenario:** An attacker opens an IBC channel, sends packets with arbitrary FungibleTokenPacketData (no authentication on recv_packet beyond signed origin), and mints unlimited VRDX to any account. The packet data is SCALE-decoded but not validated against any real cross-chain proof — any signed account can call recv_packet with forged data.
- **Severity:** CRITICAL
- **Existing test:** IBC tests exist (33 tests) but none verify total_issuance after recv_packet
- **Missing test:** Test that total_issuance does not exceed TOTAL_SUPPLY after IBC recv_packet
- **Remediation:** Verify IBC pallet Currency type is MaxSupplyCurrency in runtime config. Add a proof verification layer for recv_packet (currently accepts arbitrary data from any signed account).

### C2. IBC recv_packet has no packet origin verification — any signed account can forge packets
- **File:** pallets/ibc/src/lib.rs
- **Function:** recv_packet (line 435)
- **Component:** IBC pallet
- **Risk:** recv_packet only calls `ensure_signed(origin)` — it does NOT verify that the packet came from a counterparty chain. The `data` field is a raw `Vec<u8>` decoded as FungibleTokenPacketData without any Merkle proof, commitment verification, or relayer authentication. Any account can submit arbitrary packet data and mint tokens.
- **Exploit scenario:** Attacker calls recv_packet with a forged FungibleTokenPacketData { denom: b"VRDX", amount: 1_000_000_000, receiver: <attister_account> }. Since no proof is required, tokens are minted directly to the attacker.
- **Severity:** CRITICAL
- **Existing test:** Tests verify sequence ordering and replay prevention, but none test packet authenticity
- **Missing test:** Test that forged packet data from non-relayer is rejected
- **Remediation:** Implement IBC commitment verification (Merkle proofs against client state). Restrict recv_packet to designated relayers. Do NOT mint tokens without cryptographic proof of the counterparty chain's state.

### C3. IBC send_packet has no authentication — any signed account can send arbitrary data
- **File:** pallets/ibc/src/lib.rs
- **Function:** send_packet (line 383)
- **Component:** IBC pallet
- **Risk:** send_packet accepts `_who = ensure_signed(origin)` but discards the caller identity (underscore prefix). Any account can send arbitrary data on any open channel. Combined with the transfer function, this means anyone can trigger cross-chain transfers.
- **Exploit scenario:** Attacker calls send_packet on an open channel with crafted data that the destination chain interprets as a valid incoming transfer, minting tokens there.
- **Severity:** CRITICAL
- **Existing test:** No test verifies sender authorization for send_packet
- **Missing test:** Test that non-channel-creator cannot send packets, or that only designated relayers can send
- **Remediation:** Restrict send_packet to authorized relayers or channel participants. Do not accept arbitrary packet data from any signed account.

---

## HIGH

### H1. MaxSupplyCurrency::deposit_creating panics instead of returning error
- **File:** runtime/src/max_supply_currency.rs
- **Function:** deposit_creating (line ~170)
- **Component:** MaxSupplyCurrency wrapper
- **Risk:** When the cap is exceeded, `deposit_creating` calls `panic!()` instead of returning an error. In Substrate, panics in runtime code cause the block to fail and all transactions in that block to be rejected. A single transaction that triggers the panic can DoS the entire block.
- **Exploit scenario:** Attacker crafts a transaction that would mint tokens exceeding the cap, causing the entire block to panic and fail, blocking all other transactions.
- **Severity:** HIGH
- **Existing test:** MaxSupplyCurrency is tested in workspace tests but no test specifically triggers the panic path
- **Missing test:** Test that deposit_creating at cap boundary returns error instead of panicking
- **Remediation:** Replace panic with graceful error return. Use `deposit_into_existing` (which returns Result) instead of `deposit_creating` where possible.

### H2. MaxSupplyCurrency::issue also panics on cap exceeded
- **File:** runtime/src/max_supply_currency.rs
- **Function:** issue (line ~155)
- **Component:** MaxSupplyCurrency wrapper
- **Risk:** Same as H1 — `issue()` panics when cap is exceeded. Any pallet calling `issue()` at the cap boundary will crash the block.
- **Exploit scenario:** Same as H1 — trigger a mint path that reaches the cap, causing block-level panic.
- **Severity:** HIGH
- **Existing test:** No test triggers issue() at cap boundary
- **Missing test:** Test that issue() at cap boundary fails gracefully
- **Remediation:** Return Default imbalances or use a checked variant. Panicking in runtime is a DoS vector.

### H3. DPoS set_commission does not verify caller is a registered validator
- **File:** pallets/dpos/src/lib.rs
- **Function:** set_commission (line ~790)
- **Component:** DPoS pallet
- **Risk:** set_commission calls `ensure_signed(origin)` and then directly mutates `Validators::<T>::mutate(&who, ...)`. If the caller is not a registered validator, the mutate is a no-op (the Option is None). However, the extrinsic succeeds silently, emitting a CommissionSet event for a non-validator. This is not a direct exploit but indicates missing input validation.
- **Exploit scenario:** Attacker calls set_commission to emit false CommissionSet events, potentially confusing off-chain monitoring or governance dashboards.
- **Severity:** HIGH (reduced from CRITICAL because no state change occurs for non-validators)
- **Existing test:** No test for set_commission by non-validator
- **Missing test:** Test that set_commission by non-validator fails with NotValidator error
- **Remediation:** Add `ensure!(Validators::<T>::contains_key(&who), Error::<T>::NotValidator)` check.

### H4. DPoS do_slash is a public function with no origin check
- **File:** pallets/dpos/src/lib.rs
- **Function:** do_slash (line ~930)
- **Component:** DPoS pallet
- **Risk:** `do_slash` is `pub fn` with no origin verification. It is intended to be called by the offence handler, but any pallet or internal function with access to the DPoS module can call it. If exposed via RPC or a governance dispatchable, it could be abused.
- **Exploit scenario:** If a future pallet or runtime upgrade exposes do_slash via a dispatchable, an attacker could slash any validator without going through the offence reporting pipeline.
- **Severity:** HIGH
- **Existing test:** Slashing tests exist (21 tests) but do not test unauthorized do_slash access
- **Missing test:** Test that do_slash cannot be called via dispatchable origin
- **Remediation:** Make do_slash `pub(crate)` or require a specific trait bound (e.g., `OnOffenceHandler`) that is only implemented by the consensus engine.

### H5. Vesting release_vested uses saturated_conversion for block time calculations
- **File:** pallets/vesting/src/lib.rs
- **Function:** release_vested (line ~200)
- **Component:** Vesting pallet
- **Risk:** `blocks_per_day = (86_400_000 / block_time_ms) as u32` uses `as u32` cast which silently truncates. If block_time_ms doesn't divide evenly, the vesting schedule will release tokens slightly faster than intended. Over large vesting periods, this compounds.
- **Exploit scenario:** A vesting schedule meant to lock 1B tokens for 365 days could release them slightly early due to rounding, allowing premature token access.
- **Severity:** HIGH
- **Existing test:** 18 vesting tests + 12 edge case tests, but none verify exact vesting day calculation
- **Missing test:** Property test that verifies exact vested amount at specific block heights
- **Remediation:** Use checked division with remainder tracking, or store vesting in block numbers directly rather than converting through days.

### H6. Fungible tokens mint does not check max_supply against total_supply
- **File:** pallets/fungible-tokens/src/lib.rs
- **Function:** mint (line ~340)
- **Component:** Fungible Tokens pallet
- **Risk:** The mint function checks `token.is_frozen` but the max_supply check is truncated in the visible code. If `new_supply > token.max_supply` is not properly checked, token owners can mint beyond the declared max supply.
- **Exploit scenario:** Token owner mints unlimited custom tokens, diluting all holders.
- **Severity:** HIGH
- **Existing test:** 29 tests exist, but need to verify max_supply enforcement test
- **Missing test:** Test that mint beyond max_supply fails with MaxSupplyExceeded
- **Remediation:** Ensure `ensure!(new_supply <= token.max_supply, Error::<T>::MaxSupplyExceeded)` is present in mint().

### H7. Tokenomics purchase() transfers from treasury — treasury can be drained
- **File:** pallets/tokenomics/src/lib.rs
- **Function:** purchase (line ~330)
- **Component:** Tokenomics pallet
- **Risk:** purchase() calls `T::Currency::transfer(&treasury, &who, amount, AllowDeath)` with `AllowDeath`, which can drain the treasury account to zero (below existential deposit). If the treasury is the PalletId account, killing it means subsequent transfers to it will fail.
- **Exploit scenario:** Multiple purchases drain the treasury below existential deposit, killing the account. Subsequent purchase() calls fail because `transfer(&treasury, &who, ...)` can't pull from a dead account.
- **Severity:** HIGH
- **Existing test:** Tokenomics tests exist but may not test treasury depletion
- **Missing test:** Test that purchase fails gracefully when treasury is depleted
- **Remediation:** Use `KeepAlive` instead of `AllowDeath` for treasury transfers. Check treasury balance before transfer.

### H8. Circuit breaker pause_pallet uses ensure_root — not governance
- **File:** pallets/circuit-breaker/src/lib.rs
- **Function:** pause_pallet (line ~73)
- **Component:** Circuit Breaker pallet
- **Risk:** pause_pallet and unpause_pallet use `ensure_root(origin)` instead of a governance origin (council/multisig). Root is not available on mainnet (sudo removed), so this pallet is non-functional on production. If root were available, a single key could pause any pallet instantly.
- **Exploit scenario:** On testnet with root, a compromised root key can pause all pallets, DoSing the chain. On mainnet, the circuit breaker is dead code.
- **Severity:** HIGH
- **Existing test:** No tests for circuit-breaker pallet
- **Missing test:** Test that pause/unpause requires governance origin, not root
- **Remediation:** Change `ensure_root` to `T::AdminOrigin::ensure_origin` or a council 2/3 origin.

---

## MEDIUM

### M1. DPoS rotate_epoch does not enforce MinimumValidatorCount during selection
- **File:** pallets/dpos/src/lib.rs
- **Function:** rotate_epoch (line ~1048)
- **Component:** DPoS pallet
- **Risk:** rotate_epoch selects top ActiveValidatorCount validators but does not check if fewer than MinimumValidatorCount validators are available. The check is in new_session() which runs after rotate_epoch, but the epoch still rotates with insufficient validators before new_session catches it.
- **Exploit scenario:** If enough validators are slashed simultaneously, rotate_epoch selects a sub-threshold set, and the chain operates with insufficient validators for one epoch.
- **Severity:** MEDIUM
- **Existing test:** 17 integration tests + 21 slashing tests, but no test for rotate_epoch with sub-threshold validators
- **Missing test:** Test that rotate_epoch refuses to rotate with < MinimumValidatorCount non-slashed validators
- **Remediation:** Add MinimumValidatorCount check in rotate_epoch before committing the new active set.

### M2. DPoS slashing sends funds to PalletId account, not Treasury
- **File:** pallets/dpos/src/lib.rs
- **Function:** slash_validator / do_slash (line ~700, 930)
- **Component:** DPoS pallet
- **Risk:** Slashed funds are sent to `T::PalletId::get().into_account_truncating()` (the DPoS pallet account), which is the same account as the reward pool. Slashed funds and rewards are mixed in the same account. The Treasury Security Spec requires slashed funds to go to the governance Treasury, not the DPoS pallet.
- **Exploit scenario:** Slashed funds become indistinguishable from reward pool funds and could be distributed as block rewards, effectively returning slashed stakes to validators.
- **Severity:** MEDIUM
- **Existing test:** Slashing tests verify the transfer but not the destination account separation
- **Missing test:** Test that slashed funds go to Treasury, not reward pool
- **Remediation:** Use a separate Treasury account (e.g., `pallet_treasury::PalletId`) instead of the DPoS PalletId.

### M3. IBC pallet uses without_storage_info — unbounded storage growth
- **File:** pallets/ibc/src/lib.rs (line 268)
- **Function:** Pallet struct
- **Component:** IBC pallet
- **Risk:** `#[pallet::without_storage_info]` means all storage maps use unbounded keys. IbcPackets stores every packet ever sent with no pruning. Over time, this creates unbounded storage growth that can DoS the chain by filling disk.
- **Exploit scenario:** Attacker sends millions of small packets, each stored permanently in IbcPackets, eventually filling node storage.
- **Severity:** MEDIUM
- **Existing test:** 33 IBC tests but none test storage growth limits
- **Missing test:** Test that old packets are pruned after acknowledgement
- **Remediation:** Remove acknowledged packets from storage. Add a cleanup mechanism or use BoundedVec for packet storage.

### M4. Gulf Stream pallet uses without_storage_info
- **File:** pallets/gulf-stream/src/lib.rs (line 36)
- **Function:** Pallet struct
- **Component:** Gulf Stream pallet
- **Risk:** Same as M3 — unbounded storage growth for forwarded transaction history.
- **Exploit scenario:** Validators forward transactions, each stored permanently, filling disk over time.
- **Severity:** MEDIUM
- **Existing test:** Tests exist but none test storage bounds
- **Missing test:** Test that forwarded transaction history is pruned
- **Remediation:** Add storage bounds or cleanup for forwarded transaction history.

### M5. DEX remove_liquidity uses division (not checked_div) for LP ratio
- **File:** pallets/amm-dex/src/lib.rs
- **Function:** remove_liquidity (line ~580)
- **Component:** AMM DEX pallet
- **Risk:** `amount_a = pool.reserve_a.checked_mul(&lp_amount)?.checked_div(&pool.total_lp)` — the division is `checked_div` but if `pool.total_lp` is zero (shouldn't happen due to ensure! check), the earlier check could be bypassed in edge cases. Additionally, integer division truncates, meaning LP holders lose dust amounts on each withdrawal.
- **Exploit scenario:** Repeated add/remove liquidity with small amounts accumulates dust in the pool that can never be withdrawn — permanent locked value.
- **Severity:** MEDIUM
- **Existing test:** 33 DEX tests + 18 security regression tests
- **Missing test:** Test that repeated small add/remove cycles don't accumulate significant dust
- **Remediation:** Accept dust loss as inherent to integer AMM, but document it. Consider rounding favorably to LP holders.

### M6. DPoS genesis does not set registration_deposit for validators
- **File:** pallets/dpos/src/lib.rs
- **Function:** genesis_build (line ~302)
- **Component:** DPoS pallet
- **Risk:** Genesis validators have `registration_deposit: BalanceOf::<T>::zero()`. If a genesis validator unregisters, their unbonding queue will try to unbond `validator.stake` but the deposit is zero, causing accounting inconsistency.
- **Exploit scenario:** Genesis validator unregisters, gets stake back in unbonding, but the zero deposit means the deposit return path is never triggered.
- **Severity:** MEDIUM
- **Existing test:** Genesis tests verify stake but not registration_deposit
- **Missing test:** Test that genesis validators have correct registration_deposit
- **Remediation:** Set `registration_deposit = T::RegistrationDeposit::get()` in genesis_build.

### M7. Eco pallet register_green_validator is self-attested
- **File:** pallets/eco/src/lib.rs
- **Function:** register_green_validator (line ~580)
- **Component:** Eco pallet
- **Risk:** Any signed account can register as a green validator with self-attested carbon_offset, trees_planted, and renewable_energy claims. While green_score is admin-controlled, the self-reported data (carbon_offset, trees_planted) feeds into aggregate metrics (TotalCO2Offset, TotalTreesPlanted) that are displayed publicly.
- **Exploit scenario:** Attacker registers with carbon_offset: u64::MAX, inflating the chain's eco metrics. This doesn't directly affect consensus but damages credibility.
- **Severity:** MEDIUM
- **Existing test:** 35 eco tests including non-root rejection for mint_carbon_credit
- **Missing test:** Test that self-registered green validator data is bounded or verified
- **Remediation:** Make green validator registration admin-gated, or add a verification step before updating aggregate metrics.

### M8. Vesting remove_vesting is not exposed as a dispatchable
- **File:** pallets/vesting/src/lib.rs
- **Function:** No remove_vesting dispatchable exists
- **Component:** Vesting pallet
- **Risk:** The VestingHandler trait has a remove_vesting method used by the presale refund flow, but there is no dispatchable to remove vesting manually. If vesting needs to be cancelled (e.g., compliance order), only root can do it via assign_vesting with zero or through governance.
- **Exploit scenario:** Not directly exploitable, but creates operational risk if vesting needs emergency removal.
- **Severity:** MEDIUM
- **Existing test:** 18 vesting tests + 12 edge case tests
- **Missing test:** Test for vesting removal path
- **Remediation:** Add a root-only dispatchable to remove vesting entries for compliance/emergency scenarios.

---

## LOW

### L1. DPoS green_score multiplier uses saturating arithmetic
- **File:** pallets/dpos/src/lib.rs
- **Function:** rotate_epoch (line ~1063)
- **Component:** DPoS pallet
- **Risk:** `effective_votes = v.total_votes.saturating_mul(multiplier) / hundred` uses saturating multiplication. If total_votes * multiplier overflows, the value is capped at Balance::MAX, which could give a validator disproportionate weight.
- **Exploit scenario:** A validator with extremely high stake (near Balance::MAX) and high green_score could get saturating-mulled to the same effective votes as a lower-stake validator, flattening the ranking.
- **Severity:** LOW
- **Existing test:** No test for green_score multiplier overflow
- **Missing test:** Test with total_votes near Balance::MAX and green_score at max
- **Remediation:** Use checked_mul and handle overflow explicitly.

### L2. IBC FungibleTokenPacketData.amount is u128 but Balance could differ
- **File:** pallets/ibc/src/lib.rs
- **Function:** recv_packet / transfer (lines 488, 700)
- **Component:** IBC pallet
- **Risk:** IBC uses `u128` for amounts but the chain's Balance type could be different (though it is u128 in practice). The `try_into()` conversion handles this but if Balance type changes, silent truncation could occur.
- **Severity:** LOW
- **Existing test:** IBC tests use u128 consistently
- **Missing test:** Test with amount at u128::MAX
- **Remediation:** Use `BalanceOf<T>` type directly in FungibleTokenPacketData.

### L3. Tokenomics CirculatingSupply is accounting-only, not enforced
- **File:** pallets/tokenomics/src/lib.rs
- **Function:** release_distribution / purchase
- **Component:** Tokenomics pallet
- **Risk:** CirculatingSupply is a StorageValue that is updated via `put()` but is not verified against actual on-chain balances. It's a tracking variable only. The code documents this ("CirculatingSupply MUST NOT be relied upon for security-critical decisions") but external consumers might trust it.
- **Severity:** LOW
- **Existing test:** 15 property tests + 12 economic invariant tests
- **Missing test:** Test that CirculatingSupply matches actual transferable balances
- **Remediation:** Document clearly in RPC responses that CirculatingSupply is an estimate.

### L4. Presale collect_funds sends to arbitrary beneficiary
- **File:** pallets/presale/src/lib.rs
- **Function:** collect_funds (line ~720)
- **Component:** Presale pallet
- **Risk:** collect_funds takes a `beneficiary: T::AccountId` parameter. Admin can redirect funds to any account. While admin is governance-controlled, the lack of a fixed beneficiary creates a redirect risk.
- **Exploit scenario:** Compromised admin key redirects presale funds to attacker address.
- **Severity:** LOW
- **Existing test:** 25 presale tests + 60 general tests
- **Missing test:** Test that collect_funds with wrong beneficiary fails
- **Remediation:** Store a fixed beneficiary in the SaleRound struct, or require governance vote for beneficiary.

### L5. DEX swap does not verify token_in matches pool tokens exactly
- **File:** pallets/amm-dex/src/lib.rs
- **Function:** swap (line ~640)
- **Component:** AMM DEX pallet
- **Risk:** swap compares `token_in_bv == pool.token_a` using BoundedVec comparison. If the token names differ by encoding (e.g., UTF-8 vs ASCII), the comparison could fail silently or pass unexpectedly.
- **Severity:** LOW
- **Existing test:** DEX tests verify swap functionality
- **Missing test:** Test with similar token names (prefix collision)
- **Remediation:** Use a hash-based comparison or fixed encoding for token identifiers.

### L6. Fungible tokens batch_transfer weight is linear
- **File:** pallets/fungible-tokens/src/lib.rs
- **Function:** batch_transfer (weight calculation)
- **Component:** Fungible Tokens pallet
- **Risk:** `fn batch_transfer(b: u32) -> Weight { Weight::from_parts(10_000 * (b as u64).max(1), 0) }` — the weight is linear but there's no explicit bound on `b`. If the batch size is very large, the actual computation time could exceed the weight estimate.
- **Severity:** LOW
- **Existing test:** 29 fungible token tests
- **Missing test:** Test with maximum batch size
- **Remediation:** Add a MaxBatchSize config parameter and enforce it.

---

## INFORMATIONAL

### I1. Sudo is correctly removed from production runtime
- **File:** runtime/src/lib.rs (line 217), node/src/chain_spec.rs (line 820)
- **Function:** CallFilter / chain_spec
- **Component:** Runtime
- **Risk:** None — this is correct. Sudo is disabled and `set_code` is blocked in the CallFilter.
- **Severity:** INFORMATIONAL
- **Existing test:** try_runtime_upgrade_succeeds test exists
- **Missing test:** None
- **Remediation:** None needed.

### I2. MaxSupplyCurrency correctly wraps both Currency and fungible trait families
- **File:** runtime/src/max_supply_currency.rs
- **Function:** All minting paths (issue, deposit_creating, deposit_into_existing, make_free_balance_be)
- **Component:** MaxSupplyCurrency
- **Risk:** None — the wrapper correctly intercepts all minting paths. The panic behavior (H1/H2) is the only concern.
- **Severity:** INFORMATIONAL
- **Existing test:** 561 workspace tests pass
- **Missing test:** Cap boundary panic test (see H1/H2)
- **Remediation:** Fix panics (H1/H2).

### I3. DEX follows CEI pattern (Checks-Effects-Interactions)
- **File:** pallets/amm-dex/src/lib.rs
- **Function:** remove_liquidity / swap
- **Component:** AMM DEX pallet
- **Risk:** None — state is updated before external transfers, preventing reentrancy.
- **Severity:** INFORMATIONAL
- **Existing test:** Security regression tests exist (18 tests)
- **Missing test:** None
- **Remediation:** None needed.

### I4. DEX has first-depositor attack protection (minimum liquidity lock)
- **File:** pallets/amm-dex/src/lib.rs
- **Function:** add_liquidity (line ~510)
- **Component:** AMM DEX pallet
- **Risk:** None — minimum liquidity is locked to dead address on pool creation.
- **Severity:** INFORMATIONAL
- **Existing test:** Security regression tests exist
- **Missing test:** None
- **Remediation:** None needed.

### I5. DEX has k-invariant check on swaps
- **File:** pallets/amm-dex/src/lib.rs
- **Function:** swap (line ~700)
- **Component:** AMM DEX pallet
- **Risk:** None — k-invariant is checked before and after swaps.
- **Severity:** INFORMATIONAL
- **Existing test:** Security regression tests exist
- **Missing test:** None
- **Remediation:** None needed.

### I6. DEX has circuit breaker for max price impact
- **File:** pallets/amm-dex/src/lib.rs
- **Function:** swap (line ~680)
- **Component:** AMM DEX pallet
- **Risk:** None — MaxPriceImpact limits single swap size.
- **Severity:** INFORMATIONAL
- **Existing test:** Security regression tests exist
- **Missing test:** None
- **Remediation:** None needed.

### I7. Presale has O(1) fund collection with double-collection prevention
- **File:** pallets/presale/src/lib.rs
- **Function:** collect_funds
- **Component:** Presale pallet
- **Risk:** None — RoundFundsCollected flag prevents double collection.
- **Severity:** INFORMATIONAL
- **Existing test:** 25 presale tests
- **Missing test:** None
- **Remediation:** None needed.

### I8. DPoS has minimum validator count enforcement
- **File:** pallets/dpos/src/lib.rs
- **Function:** new_session (line ~1209)
- **Component:** DPoS pallet
- **Risk:** None — chain halts if validators drop below MinimumValidatorCount.
- **Severity:** INFORMATIONAL
- **Existing test:** Integration tests exist
- **Missing test:** Test for exact MinimumValidatorCount boundary
- **Remediation:** None needed.

---

## SUMMARY

| Severity | Count |
|----------|-------|
| CRITICAL | 3 |
| HIGH | 8 |
| MEDIUM | 8 |
| LOW | 6 |
| INFORMATIONAL | 8 |

**TOTAL FINDINGS = 33**

---

## LUNA VERDICT

The codebase has **3 CRITICAL findings** in the IBC pallet that make it unsafe for mainnet deployment. The IBC pallet allows any signed account to forge cross-chain packets and mint unlimited tokens without cryptographic proof verification.

The MaxSupplyCurrency wrapper has **2 HIGH findings** (panic-on-cap-exceeded) that create block-level DoS vectors.

The DPoS pallet has solid downtime detection and slashing logic, but slash destination accounting (M2) and commission validation (H3) need fixes.

The DEX pallet is well-protected with CEI pattern, k-invariant checks, first-depositor protection, and circuit breakers. No CRITICAL or HIGH findings.

The vesting and presale pallets have proper checked arithmetic and escrow-based flows. Main concerns are vesting day calculation precision (H5) and treasury depletion risk (H7).

**Luna recommends:** Do NOT deploy IBC pallet to mainnet until C1, C2, C3 are resolved. All HIGH findings should be resolved before external audit engagement.

---

*Report generated by Luna — Independent Critical Challenge Layer*
*Authority: Verdischain Engineering Constitution v1.0, Article 19*
