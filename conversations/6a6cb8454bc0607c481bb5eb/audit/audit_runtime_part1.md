# Verdis Chain Runtime v2.0 — Comprehensive Security & Correctness Review

---

## FINDING 1: Zeroed WASM PRNG — Deterministic "Randomness"

**Severity: CRITICAL**
**Location: Custom getrandom / WASM build target**

The custom `getrandom` handler fills every byte with `0x00`. Any code that calls `getrandom` inside WASM (including cryptographic key derivation, nonce generation, or anything that depends on `rand`) receives an all-zero buffer. An attacker who knows this can predict "random" outputs, forge nonces, and break any security property that relies on entropy inside the WASM runtime.

```rust
// BEFORE — silently returns all-zero bytes, breaking any consumer
#[cfg(target_arch = "wasm32")]
fn verdis_getrandom(dest: &mut [u8]) -> Result<(), getrandom::Error> {
    for byte in dest.iter_mut() {
        *byte = 0;
    }
    Ok(())
}

// AFTER — return the proper "unsupported" error so callers cannot
// silently consume zero-entropy data; all entropy-dependent paths
// must be replaced with deterministic, on-chain-safe alternatives
// (e.g. pallet_babe::RandomnessFromOneEpochAgo, which is already
// wired into pallet_contracts).
#[cfg(target_arch = "wasm32")]
fn verdis_getrandom(dest: &mut [u8]) -> Result<(), getrandom::Error> {
    // WASM runtimes must never use OS entropy.
    // Return the standard "unsupported" error code so any accidental
    // caller gets a hard failure instead of silent zeroes.
    Err(getrandom::Error::UNSUPPORTED)
}
```

---

## FINDING 2: Blanket `#[allow(...)]` Directives Suppress Critical Warnings

**Severity: CRITICAL**
**Location: Crate-level attributes**

`#![allow(unused_imports)]`, `#![allow(unused_variables)]`, and `#![allow(clippy::all)]` suppress Rust's entire warning machinery for the runtime crate. Real bugs — unused but security-relevant imports, shadowed variables in extrinsic handlers, integer truncation — are silently hidden. `#![allow(deprecated)]` additionally allows calling functions that have known soundness issues.

```rust
// BEFORE
#![allow(deprecated)]
#![allow(unused_imports)]
#![allow(clippy::all)]
#![allow(unused_variables)]

// AFTER — remove all blanket suppressions; fix each warning site individually
// (no replacement block — these four lines must be deleted entirely)
```

---

## FINDING 3: `VerdisBaseCallFilter` Is a No-op — Provides Zero Filtering

**Severity: CRITICAL**
**Location: `VerdisBaseCallFilter` / `frame_system::Config`**

The call filter unconditionally returns `true` for every call. The comment claims "sudo key check still applies", which is correct for `pallet_sudo` itself, but the filter is documented as a *base* filter that is evaluated *before* origin checks. Any pallet that should be disabled during an emergency, migration window, or maintenance mode cannot be disabled because the filter is hardcoded to allow everything. More concretely: if `pallet_sudo` is ever removed, or if a governance extrinsic is used to pause a pallet, this filter will never honour it.

```rust
// BEFORE — two arms, both return true; dead code, false security narrative
pub struct VerdisBaseCallFilter;
impl frame_support::traits::Contains<RuntimeCall> for VerdisBaseCallFilter {
    fn contains(call: &RuntimeCall) -> bool {
        match call {
            RuntimeCall::Sudo(_) => true,
            _ => true,
        }
    }
}

// AFTER — use a real pausable filter backed by storage, or at minimum
// use the safe frame_support default while the pause mechanism is built
pub struct VerdisBaseCallFilter;
impl frame_support::traits::Contains<RuntimeCall> for VerdisBaseCallFilter {
    fn contains(call: &RuntimeCall) -> bool {
        // Explicitly disallow calls that must never be made directly
        // through the base filter regardless of origin.
        // SafeMode / TxPause pallets should be wired here in production.
        match call {
            // Block recursive sudo wrapping — prevents privilege escalation
            // where a sudo'd call wraps another sudo call.
            RuntimeCall::Sudo(pallet_sudo::Call::sudo { call })
                if matches!(call.as_ref(), RuntimeCall::Sudo(_)) =>
            {
                false
            }
            _ => true,
        }
    }
}
```

---

## FINDING 4: `ExistentialDeposit` Set to `UNITS` (1 × 10⁹) — Too High, Breaks UX and Dust Logic

**Severity: HIGH**
**Location: `pallet_balances::Config` / `parameter_types!`**

`ExistentialDeposit = UNITS = 1_000_000_000` (1 VRDX). This means any account holding less than 1 full token is automatically reaped. Smart-contract escrow accounts, DEX pool accounts that temporarily drop below this threshold mid-swap, and presale vesting accounts that receive micro-distributions will all be silently wiped. Standard Substrate chains use a value several orders of magnitude smaller (e.g., Polkadot uses 10_000_000_000 planck = 1 DOT but planck is 10⁻¹⁰; here UNITS is already the smallest-unit multiplier making 1 VRDX the floor).

```rust
// BEFORE
pub const ExistentialDeposit: Balance = UNITS; // 1_000_000_000 — 1 full VRDX

// AFTER — set to 1/1000 of a VRDX (0.001 VRDX = 1_000_000 raw units)
// This prevents accidental account reaping while still providing
// dust protection.
pub const ExistentialDeposit: Balance = UNITS / 1_000; // 1_000_000 raw units
```

---

## FINDING 5: `CreateTokenDeposit` Type Mismatch — `u64` vs `Balance` (`u128`)

**Severity: HIGH**
**Location: `pallet_fungible_tokens::Config` / `parameter_types!`**

`CreateTokenDeposit` is declared as `u64` but `Balance` is `u128`. Depending on how `pallet_fungible_tokens` uses this constant (likely via `T::CreateTokenDeposit::get()` returning a `Balance`), the implicit coercion or compile-time type mismatch will either silently truncate large values or refuse to compile. The literal `100_000_000_000` fits in `u64` today but the type contract with the pallet is broken.

```rust
// BEFORE
pub const CreateTokenDeposit: u64 = 100_000_000_000; // wrong type

// AFTER — match the Balance type alias (u128)
pub const CreateTokenDeposit: Balance = 100 * UNITS; // 100 VRDX, correct type
```

---

## FINDING 6: `MinValidatorStake` Is 10% of Total Supply — Chain Cannot Bootstrap

**Severity: HIGH**
**Location: `pallet_dpos::Config` / `parameter_types!`**

`MinValidatorStake = 100_000_000 * UNITS` and `UNITS = 1_000_000_000`, so the minimum stake is `10^17` raw units = 100 million VRDX. `TOTAL_SUPPLY = 100_000_000_000 * UNITS` = 100 billion VRDX. The minimum per validator is therefore **0.1% of total supply**, but with 7 genesis validators the required locked stake is **700 million VRDX**, and `CIRCULATING_SUPPLY` is only 17 billion — so this is feasible at genesis but leaves virtually no headroom for new validators to join post-launch without a governance change. More critically, the comment says "0.1% supply" which is accurate but operationally dangerous: no exchange, institution, or community pool can realistically stake 100 million tokens per validator slot for a new chain.

```rust
// BEFORE
pub const MinValidatorStake: Balance = 100_000_000 * UNITS; // 100M VRDX — too high

// AFTER — 1M VRDX minimum (0.001% of supply), still provides meaningful
// sybil resistance while enabling validator set growth
pub const MinValidatorStake: Balance = 1_000_000 * UNITS; // 1M VRDX
```

---

## FINDING 7: `EpochDuration` / `EpochLength` Mismatch Between BABE and DPoS

**Severity: HIGH**
**Location: `pallet_babe::Config` and `pallet_dpos::Config`**

`pallet_babe::Config` sets `EpochDuration = ConstU64<500>` (in slots). `pallet_dpos::Config` sets `EpochLength: BlockNumber = 500` (in blocks). `pallet_session` uses `Period: BlockNumber = 500`. These three constants must be consistent. If BABE slots and blocks diverge (possible with missed slots), session rotation and DPoS epoch boundaries will drift, causing reward miscalculations and potential double-counting of validator rewards. Additionally, at 6-second blocks, 500 blocks = 50 minutes per epoch — very short for a production chain. Validator set changes and reward settlements every 50 minutes create high state-write pressure.

```rust
// BEFORE — 500 slots/blocks epoch (50 minutes) — too short for production
pub const EpochDuration: ConstU64<500>   // in pallet_babe
pub const EpochLength: BlockNumber = 500; // in pallet_dpos
pub const Period: BlockNumber = 500;      // in pallet_session

// AFTER — align all three to 4 hours (2400 blocks at 6s)
// This matches Polkadot's epoch length and reduces state churn.

// In pallet_babe::Config:
type EpochDuration = ConstU64<2_400>;

// In parameter_types! for DPoS:
pub const EpochLength: BlockNumber = 2_400;

// In parameter_types! for Session:
pub const Period: BlockNumber = 2_400;
```

---

## FINDING 8: `BlockReward` Arithmetic Is Inconsistent with Stated APR

**Severity: HIGH**
**Location: `pallet_dpos::Config` / `parameter_types!`**

The comment states "342 VRDX per block (1.8B annual, 6% APR at 30% stake)". Verification: 342 VRDX × 5,256,000 blocks/year (365 × 24 × 600) = **1,797,552,000 VRDX/year ≈ 1.8B** ✓. However, the APR claim of 6% assumes 30 billion VRDX staked (30% of 100B total supply). With only 7 validators at minimum 100M VRDX stake each, actual staked supply at genesis is ~700M VRDX, making the real APR **~257%** — hyperinflationary for early stakers and a massive incentive to dump. The reward schedule must be tied to actual staked supply, not a theoretical 30% assumption.

```rust
// BEFORE — flat 342 VRDX/block regardless of stake ratio
pub const BlockReward: Balance = 342 * UNITS;

// AFTER — reduce genesis reward to reflect realistic stake,
// or implement dynamic issuance in pallet_dpos.
// Interim fix: target 6% APR on minimum viable stake (700M VRDX genesis stake):
// Annual reward = 700_000_000 * 6% = 42_000_000 VRDX
// Per block = 42_000_000 / 5_256_000 = ~7.99 VRDX ≈ 8 VRDX
pub const BlockReward: Balance = 8 * UNITS; // genesis rate; increase via governance as stake grows
```

---

## FINDING 9: `MaxValidators` vs `ActiveValidatorCount` Semantic Gap

**Severity: HIGH**
**Location: `pallet_dpos::Config`**

`MaxValidators = 100` (registered) and `ValidatorCount = 7` (active). `MinimumValidatorCount = 4`. The constant `MinimumValidatorCount` is declared but **never passed to `pallet_dpos::Config`** — it exists in `parameter_types!` but there is no `type MinimumValidatorCount = MinimumValidatorCount;` in the impl block. If the pallet requires this bound to halt the chain below 4 active validators, the safety guarantee described in the comment is silently absent.

```rust
// BEFORE — MinimumValidatorCount declared but not wired
parameter_types! {
    pub const MinimumValidatorCount: u32 = 4;
    // ...
}
impl pallet_dpos::Config for Runtime {
    // MinimumValidatorCount is MISSING from this impl block
    type ActiveValidatorCount = ValidatorCount;
    // ...
}

// AFTER — wire it in (assuming pallet_dpos exposes this associated type)
impl pallet_dpos::Config for Runtime {
    type ActiveValidatorCount = ValidatorCount;
    type MinimumValidatorCount = MinimumValidatorCount; // ADD THIS LINE
    // ... rest unchanged
}
```

---

## FINDING 10: `SS58Prefix` Declared as `u16` — `frame_system` Requires `u16` but Value 909 Must Be Registered

**Severity: HIGH**
**Location: `parameter_types!` / `frame_system::Config`**

`SS58Prefix = 909` — this value is not registered in the canonical [SS58 registry](https://github.com/paritytech/ss58-registry). Using an unregistered prefix means wallets will display incorrect addresses, users will send funds to wrong chains, and exchanges cannot distinguish Verdis addresses from other chains using the same prefix. Additionally, `SS58Prefix` is typed as `u16` in the parameter block but `frame_system::Config::SS58Prefix` must implement `Get<u16>`. The u16 type is correct, but the unregistered value is an operational security risk.

```rust
// BEFORE
pub const SS58Prefix: u16 = 909; // unregistered

// AFTER — register the prefix in the SS58 registry first, then use it.
// As a placeholder, use a clearly test-only value during development,
// and gate production value behind a compile-time feature.
#[cfg(not(feature = "production"))]
pub const SS58Prefix: u16 = 42;   // generic Substrate testnet prefix
#[cfg(feature = "production")]
pub const SS58Prefix: u16 = 909;  // replace ONLY after SS58 registry PR is merged
```

---

## FINDING 11: `VerdisOffenceHandler` Calls Unexposed Internal Functions

**Severity: HIGH**
**Location: `VerdisOffenceHandler::on_offence`**

The handler calls `Dpos::validators(validator_id)` and `Dpos::do_slash(validator_id, slash_amount)`. `do_slash` is almost certainly a private or `pub(crate)` function inside `pallet_dpos`. Calling it from outside the pallet bypasses all internal invariant checks (e.g., minimum stake floor, unbonding period checks, re-entrancy guards). Even if it compiles (via `pub` visibility), the slash logic may leave the pallet in an inconsistent state (validator active with zero stake, reward counters not updated, etc.).

```rust
// BEFORE — calling internal pallet function from outside
fn on_offence(
    offenders: &[...],
    _slash_fraction: &[Perbill],
    _session: SessionIndex,
) -> Weight {
    for offender in offenders {
        let (validator_id, _full_id) = &offender.offender;
        if let Some(val) = Dpos::validators(validator_id) {
            let slash_amount: Balance = val.stake / 20u128;
            Dpos::do_slash(validator_id, slash_amount); // UNSAFE: internal API
        }
    }
    Weight::zero()
}

// AFTER — use the pallet's public slash dispatchable or a dedicated
// slash trait that pallet_dpos must implement for cross-pallet safety
fn on_offence(
    offenders: &[sp_staking::offence::OffenceDetails<
        AccountId,
        pallet_session::historical::IdentificationTuple<Runtime>,
    >],
    slash_fraction: &[sp_runtime::Perbill],
    session: sp_staking::SessionIndex,
) -> frame_support::weights::Weight {
    for (offender_details, fraction) in offenders.iter().zip(slash_fraction.iter()) {
        let (validator_id, _) = &offender_details.offender;
        // Use the public trait impl — pallet_dpos must impl sp_staking::OnSlash
        // or expose a safe SlashValidator trait.
        <pallet_dpos::Pallet<Runtime> as pallet_dpos::SlashValidator<AccountId, Balance>>::slash(
            validator_id,
            *fraction,
        );
    }
    <Runtime as frame_system::Config>::DbWeight::get().reads_writes(
        offenders.len() as u64,
        offenders.len() as u64,
    )
}
```

---

## FINDING 12: `pallet_contracts` `CallFilter = Everything` — Contracts Can Call Any Extrinsic

**Severity: HIGH**
**Location: `pallet_contracts::Config`**

`type CallFilter = Everything` allows WASM contracts to dispatch **any** `RuntimeCall`, including `Sudo`, `DPoS::slash`, `Eco::set_green_score`, and governance extrinsics. A malicious or buggy contract can trigger privileged operations if the contract's origin passes downstream checks. This should be a strict allowlist.

```rust
// BEFORE
type CallFilter = Everything; // contracts can call anything

// AFTER — restrict contracts to safe, unprivileged calls only
pub struct ContractCallFilter;
impl frame_support::traits::Contains<RuntimeCall> for ContractCallFilter {
    fn contains(call: &RuntimeCall) -> bool {
        matches!(
            call,
            RuntimeCall::Balances(_)
                | RuntimeCall::FungibleTokens(_)
                | RuntimeCall::AmmDex(_)
                | RuntimeCall::Utility(_)
        )
    }
}

// In pallet_contracts::Config:
type CallFilter = ContractCallFilter;
```

---

## FINDING 13: `UnsafeUnstableInterface = ConstBool<false>` — Verify This Is Intentional

**Severity: MEDIUM**
**Location: `pallet_contracts::Config`**

`ConstBool<false>` is correct for production. This is a **confirmatory note**: ensure this is never flipped to `true` in any deployment script or feature flag, as it enables unstable host functions that can break across runtime upgrades.

```rust
// CORRECT — document explicitly why false is required
type UnsafeUnstableInterface = ConstBool<false>; // MUST remain false in production;
                                                  // enabling breaks upgrade compatibility
```

No code change required, but add the comment.

---

## FINDING 14: `MaxStorageKeyLen` for Contracts Set to 128 — Below Substrate Default of 128 but Inconsistent with `pallet_storage`

**Severity: MEDIUM**
**Location: `pallet_contracts::Config`**

`MaxStorageKeyLen = 128` bytes is the Substrate default and is fine. However, `pallet_storage` also has a `MaxStorageRecords = 10_000` with no per-record size bound documented. If contract storage and chain storage share underlying keys, a contract could enumerate or shadow custom storage keys. Ensure storage key namespacing is enforced.

```rust
// BEFORE — no namespace isolation documented
pub const MaxStorageKeyLen: u32 = 128;

// AFTER — add a comment and ensure pallet_storage uses a distinct prefix
/// Maximum byte length of a storage key for WASM contracts.
/// All contract storage is prefixed with the contract's account ID,
/// preventing collision with pallet_storage keys (prefixed with b"verdisst").
pub const MaxStorageKeyLen: u32 = 128;
```

---

## FINDING 15: `DepositPerItem` and `DepositPerByte` Both Set to `1 * UNITS` — Byte Deposit Is Excessively High

**Severity: MEDIUM**
**Location: `pallet_contracts::Config`**

`DepositPerByte = 1 * UNITS = 1 VRDX per byte`. A 10 KB contract storage entry would cost 10,000 VRDX ≈ ~$X at any non-trivial token price. This makes contract storage economically inaccessible. The canonical Substrate value is in the range of milliunit per byte.

```rust
// BEFORE
pub const DepositPerItem: Balance = 1 * UNITS;  // 1 VRDX per storage item
pub const DepositPerByte: Balance = 1 * UNITS;  // 1 VRDX per byte — far too high

// AFTER
pub const DepositPerItem: Balance = UNITS / 10;        // 0.1 VRDX per item
pub const DepositPerByte: Balance = UNITS / 1_000_000; // 1 micro-VRDX per byte
```

---

## FINDING 16: `MaxPriceImpact` of 10% Per Swap — MEV and Price Manipulation

**Severity: MEDIUM**
**Location: `pallet_amm_dex::Config`**

Allowing 10% price impact per single swap means a single transaction can move the pool price by up to 10%. On an on-chain AMM with deterministic ordering, MEV bots can sandwich-attack every large swap profitably. Standard DEX implementations use 1–3% maximum slippage tolerance enforced by the *user*, not by the protocol. The protocol-level guard should be much tighter (e.g., 3–5%) or replaced with per-pool configurable limits.

```rust
// BEFORE
pub const MaxPriceImpact: sp_runtime::Permill = sp_runtime::Permill::from_percent(10);

// AFTER — tighten to 3% protocol-level maximum; users can set lower slippage tolerance
pub const MaxPriceImpact: sp_runtime::Permill = sp_runtime::Permill::from_percent(3);
```

---

## FINDING 17: `InvestorAllocationConst` Not Verified Against Circulating Supply

**Severity: MEDIUM**
**Location: `pallet_tokenomics::Config`**

`InvestorAllocation = 5_000_000_000 * UNITS` (5 billion VRDX = 5% of total supply). `CIRCULATING_SUPPLY = 17_000_000_000 * UNITS`. The investor allocation is 29.4% of circulating supply. If this is allocated at genesis without vesting verification, early investors can dump 5B tokens immediately. There is no compile-time assertion that `InvestorAllocationConst ≤ CIRCULATING_SUPPLY`, and no check that the sum of all genesis allocations equals `TOTAL_SUPPLY`.

```rust
// AFTER — add compile-time supply consistency assertions
const _: () = {
    assert!(
        InvestorAllocationConst::get() <= CIRCULATING_SUPPLY,
        "Investor allocation exceeds circulating supply"
    );
    // Add similar assertions for all other allocations once defined
    assert!(
        CIRCULATING_SUPPLY <= TOTAL_SUPPLY,
        "Circulating supply exceeds total supply"
    );
};

// As a parameter_types! block addition:
parameter_types! {
    pub const InvestorAllocationConst: Balance = 5_000_000_000 * UNITS; // unchanged value
    pub const TotalSupplyConst: Balance = 100_000_000_000 * UNITS;      // unchanged value
}

// Add after parameter_types! block:
static_assertions::const_assert!(
    InvestorAllocationConst::get() < TotalSupplyConst::get()
);
```

---

## FINDING 18: `ReportLongevity` Comment Is Internally Inconsistent

**Severity: MEDIUM**
**Location: `pallet_babe::Config` / `parameter_types!`**

`ReportLongevity = 18_000_000` with comment "500 blocks * 6 epochs * 6s = covers slash defer period". The math: 500 blocks × 6 epochs = 3,000 blocks. At 6 seconds per block that is 18,000 seconds = 18,000,000 milliseconds. So the value is **milliseconds**, not blocks. BABE's `ReportLongevity` is in **slots** (= blocks at 1 slot/block). 18,000,000 slots at 6 seconds/slot = 125,000 days — astronomically large. The correct value should be in slots, not milliseconds.

```rust
// BEFORE
pub const ReportLongevity: u64 = 18_000_000; // comment claims "500 blocks * 6 epochs * 6s"
                                               // but 18_000_000 slots = 125,000 days

// AFTER — express in slots (= blocks); 84 epochs × 2400 blocks/epoch = 201,600 slots ≈ 14 days
// This matches the UnbondingPeriod, ensuring reports can be filed during the slash defer window.
pub const ReportLongevity: u64 =
    (84 as u64)          // epochs (= MaxSetIdSessionEntries)
    * (2_400 as u64);    // blocks per epoch (after fix from Finding 7)
                         // = 201,600 slots ≈ 14 days
```

---

## FINDING 19: `MaxSetIdSessionEntries` for GRANDPA Set to 84 — Mismatched with Epoch Length

**Severity: MEDIUM**
**Location: `pallet_grandpa::Config`**

`MaxSetIdSessionEntries = ConstU64<84>`. This represents how many session entries GRANDPA tracks for set-ID history (used in equivocation proofs). With 500-block epochs this is 84 × 500 = 42,000 blocks = ~3.5 days of history. With the corrected 2400-block epochs (Finding 7), it becomes 84 × 2400 = 201,600 blocks = 14 days, which aligns with `UnbondingPeriod`. The value itself is reasonable **only after** fixing Finding 7; document this dependency.

```rust
// BEFORE — undocumented dependency on epoch length
type MaxSetIdSessionEntries = ConstU64<84>;

// AFTER — document the dependency explicitly
// 84 sessions × 2400 blocks/session = 201,600 blocks ≈ 14 days
// This MUST equal UnbondingPeriod / EpochLength to ensure equivocation
// proofs can be submitted throughout the full unbonding window.
type MaxSetIdSessionEntries = ConstU64<84>; // value unchanged; comment added
```

---

## FINDING 20: `TransactionByteFee` Is 100,000 Raw Units — Effectively Zero

**Severity: MEDIUM**
**Location: `pallet_transaction_payment::Config`**

`TransactionByteFee = 100_000` raw units. With `UNITS = 1_000_000_000`, this is `0.0001 VRDX` per byte. A 10 KB transaction costs 1 VRDX. This is workable but combined with `WeightToFee = IdentityFee` (1 weight unit = 1 raw unit of fee), ultra-heavy transactions become extremely cheap. The `IdentityFee` mapping means block execution weight of ~2×10¹² ref-time units would cost 2,000 VRDX for a single transaction filling an entire block — define whether this is intentional.

```rust
// BEFORE — undocumented fee policy
type WeightToFee = IdentityFee<Balance>;
type LengthToFee = IdentityFee<Balance>;

// AFTER — use a scaled fee that targets a human-readable amount per
// average transaction (~0.01 VRDX for a simple transfer)
// IdentityFee is only appropriate if weights are calibrated to raw units.
// If weights follow WEIGHT_REF_TIME_PER_SECOND = 10^12, a simple transfer
// costs ~125_000_000 weight, so fee = 125_000_000 raw units = 0.125 VRDX.
// Consider:
use frame_support::weights::WeightToFeeCoefficients;
pub struct LinearWeightToFee;
impl frame_support::weights::WeightToFee for LinearWeightToFee {
    type Balance = Balance;
    fn weight_to_fee(weight: &Weight) -> Balance {
        // 1 VRDX per 10^12 ref_time units (1 second of compute)
        (weight.ref_time() as Balance)
            .saturating_mul(UNITS)
            .saturating_div(WEIGHT_REF_TIME_PER_SECOND as Balance)
    }
}

// In pallet_transaction_payment::Config:
type WeightToFee = LinearWeightToFee;
```

---

## FINDING 21: `FullIdentificationOf::convert` Always Returns `Some(())` — Equivocation Proofs Accept Invalid Validators

**Severity: MEDIUM**
**Location: `FullIdentificationOf`**

The converter returns `Some(())` for **any** `AccountId` regardless of whether that account is actually a registered validator. GRANDPA and BABE equivocation proof verification calls this converter to confirm the reported key-owner was a real validator in the reported session. Returning `Some(())` unconditionally means equivocation reports can name any account — including non-validators — and the proof will be accepted, potentially triggering slashes against innocent accounts.

```rust
// BEFORE — always returns Some(())
impl sp_runtime::traits::Convert<AccountId, Option<()>> for FullIdentificationOf {
    fn convert(a: AccountId) -> Option<()> {
        Some(())
    }
}

// AFTER — only return Some(()) if the account is a registered validator
impl sp_runtime::traits::Convert<AccountId, Option<()>> for FullIdentificationOf {
    fn convert(a: AccountId) -> Option<()> {
        // Only validators registered in pallet_dpos can be equivocators
        if pallet_dpos::Pallet::<Runtime>::is_registered_validator(&a) {
            Some(())
        } else {
            None
        }
    }
}
```

---

## FINDING 22: `pallet_authorship` — `EventHandler = ()` Drops Block Reward Triggers

**Severity: MEDIUM**
**Location: `pallet_authorship::Config`**

`type EventHandler = ()` means block authorship events are discarded. If `pallet_dpos` relies on authorship events to credit block rewards to the block author, rewards will never be paid. The handler should be wired to `pallet_dpos` or `pallet_tokenomics`.

```rust
// BEFORE
impl pallet_authorship::Config for Runtime {
    type FindAuthor = pallet_session::FindAccountFromAuthorIndex<Runtime, Babe>;
    type EventHandler = (); // rewards silently dropped
}

// AFTER — wire DPoS as the event handler so block authors receive rewards
impl pallet_authorship::Config for Runtime {
    type FindAuthor = pallet_session::FindAccountFromAuthorIndex<Runtime, Babe>;
    type EventHandler = Dpos; // pallet_dpos must impl pallet_authorship::EventHandler
}
```

---

## FINDING 23: `FeeMultiplierUpdate = ()` — No Dynamic Fee Adjustment

**Severity: MEDIUM**
**Location: `pallet_transaction_payment::Config`**

`type FeeMultiplierUpdate = ()` disables the slow-adjusting fee multiplier that normally prevents block spam. Without it, if the chain is fully loaded, fees do not rise to throttle demand. Combined with the low `TransactionByteFee`, an attacker can sustain a DoS by filling blocks at minimal cost indefinitely.

```rust
// BEFORE
type FeeMultiplierUpdate = (); // no fee adjustment

// AFTER — use the standard slow-adjusting multiplier
use pallet_transaction_payment::TargetedFeeAdjustment;
use sp_runtime::FixedPointNumber;

parameter_types! {
    /// Target 25% block fullness for fee adjustment
    pub const TargetBlockFullness: Perquintill = Perquintill::from_percent(25);
    pub AdjustmentVariable: sp_runtime::FixedU128 =
        sp_runtime::FixedU128::saturating_from_rational(75, 1_000_000);
    pub MinimumMultiplier: sp_runtime::FixedU128 =
        sp_runtime::FixedU128::saturating_from_rational(1, 10);
    pub MaximumMultiplier: sp_runtime::FixedU128 = sp_runtime::FixedU128::from(1_000u128);
}

type FeeMultiplierUpdate = TargetedFeeAdjustment<
    Runtime,
    TargetBlockFullness,
    AdjustmentVariable,
    MinimumMultiplier,
    MaximumMultiplier,
>;
```

---

## FINDING 24: `MinGreenScore = 0` Allows Validators with No Green Credentials

**Severity: LOW**
**Location: `pallet_eco::Config`**

For a chain marketing itself as "carbon-negative", `MinGreenScore = 0` means validators can have zero green score and still participate. This undermines the core value proposition.

```rust
// BEFORE
pub const MinGreenScore: u8 = 0;

// AFTER — require at least a minimal green credential score
pub const MinGreenScore: u8 = 10; // minimum 10/100 green score to register as validator
```

---

## FINDING 25: `MaxCarbonCredits = 1_000` — Hard Cap May Block Adoption

**Severity: LOW**
**Location: `pallet_eco::Config`**

A hard cap of 1,000 carbon credits chain-wide means at any moment only 1,000 credits exist on-chain. For a blockchain targeting global carbon markets, this is extremely restrictive.

```rust
// BEFORE
pub const MaxCarbonCredits: u32 = 1_000;

// AFTER — increase to support meaningful market volume
pub const MaxCarbonCredits: u32 = 1_000_000; // 1M credits chain-wide
```

---

## FINDING 26: `BlockHashCount` of 7,200 — Memory Pressure

**Severity: LOW**
**Location: `parameter_types!`**

Storing 7,200 block hashes (1 hour at 6s blocks) is the Polkadot standard but doubles memory usage vs. the more common 2,400. Ensure node hardware requirements are documented accordingly.

```rust
// BEFORE
pub const BlockHashCount: BlockNumber = 7200; // 1 hour of hashes

// AFTER (optional tuning) — 2,400 blocks = 4 hours of history is
// sufficient for finality lag; reduces state size
pub const BlockHashCount: BlockNumber = 2_400;
```

---

## Summary Table

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | **CRITICAL** | WASM getrandom | Zero-entropy PRNG — all random bytes are 0x00 |
| 2 | **CRITICAL** | Crate attributes | Blanket `#[allow]` suppresses all warnings |
| 3 | **CRITICAL** | CallFilter | No-op filter provides zero protection |
| 4 | **HIGH** | pallet_balances | ExistentialDeposit too high, breaks contracts/DEX |
| 5 | **HIGH** | pallet_fungible_tokens | CreateTokenDeposit type is u64 not Balance |
| 6 | **HIGH** | pallet_dpos | MinValidatorStake too high for network growth |
| 7 | **HIGH** | pallet_babe/dpos/session | EpochDuration mismatch across three pallets |
| 8 | **HIGH** | pallet_dpos | BlockReward 257% APR at genesis stake levels |
| 9 | **HIGH** | pallet_dpos | MinimumValidatorCount not wired into Config |
| 10 | **HIGH** | parameter_types | SS58Prefix 909 is unregistered |
| 11 | **HIGH** | VerdisOffenceHandler | Calls private pallet_dpos::do_slash bypassing invariants |
| 12 | **HIGH** | pallet_contracts | CallFilter=Everything allows contracts to call Sudo |
| 13 | **MEDIUM** | pallet_contracts | UnsafeUnstableInterface — needs explicit documentation guard |
| 14 | **MEDIUM** | pallet_storage | No storage key namespace isolation documented |
| 15 | **MEDIUM** | pallet_contracts | DepositPerByte = 1 VRDX makes storage inaccessible |
| 16 | **MEDIUM** | pallet_amm_dex | MaxPriceImpact 10% enables sandwich MEV |
| 17 | **MEDIUM** | pallet_tokenomics | No compile-time supply consistency assertion |
| 18 | **MEDIUM** | pallet_babe | ReportLongevity in milliseconds not slots — 125,000 days |
| 19 | **MEDIUM** | pallet_grandpa | MaxSetIdSessionEntries undocumented epoch dependency |
| 20 | **MEDIUM** | tx_payment | IdentityFee with no calibration — undefined fee policy |
| 21 | **MEDIUM** | FullIdentificationOf | Returns Some(()) for non-validators — invalid slash targets |
| 22 | **MEDIUM** | pallet_authorship | EventHandler=() drops all block reward triggers |
| 23 | **MEDIUM** | tx_payment | FeeMultiplierUpdate=() enables block-spam DoS |
| 24 | **LOW** | pallet_eco | MinGreenScore=0 contradicts chain mission |
| 25 | **LOW** | pallet_eco | MaxCarbonCredits=1,000 too low for market adoption |
| 26 | **LOW** | parameter_types | BlockHashCount=7,200 — document RAM requirements |