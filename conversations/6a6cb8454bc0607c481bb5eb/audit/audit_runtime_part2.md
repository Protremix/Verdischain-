# Substrate Runtime Code Review

## Executive Summary

I identified **18 findings** across all review categories. Several are CRITICAL security issues that could lead to chain compromise or fund loss.

---

## CRITICAL Findings

### CRITICAL-1: Treasury Burn Rate Destroying 10% of Funds Per Spend Period

**Location:** Treasury parameter_types / pallet_treasury::Config

**Description:** `TreasuryBurn` is set to `Permill::from_percent(10)`, meaning 10% of treasury funds are burned every spend period (600 blocks ≈ 1 hour at 6s blocks). This is economically catastrophic — the treasury would lose ~99% of funds within days. Polkadot mainnet uses 1%. Most chains use 0% or a negligible value.

```rust
// BEFORE
pub const TreasuryBurn: Permill = Permill::from_percent(10);

// AFTER
pub const TreasuryBurn: Permill = Permill::from_percent(0);
// OR if burn is desired: Permill::from_parts(1_000) // 0.1%
```

---

### CRITICAL-2: Uncapped Treasury Spend Origin Allows Draining Entire Treasury

**Location:** pallet_treasury::Config — `SpendOrigin` / `TreasuryMaxSpend`

**Description:** `TreasuryMaxSpend` is set to `Balance::MAX`, meaning any root-level spend proposal can drain the entire treasury in a single call. This should be a governance-appropriate cap.

```rust
// BEFORE
pub const TreasuryMaxSpend: Balance = Balance::MAX;

// AFTER
pub const TreasuryMaxSpend: Balance = 1_000_000 * UNITS; // or appropriate chain-specific cap
```

---

### CRITICAL-3: GreenTreasuryImpl Uses Hardcoded All-0xFF Address (Burn Address)

**Location:** `GreenTreasuryImpl` struct

**Description:** `AccountId::from([0xff; 32])` is a well-known burn/dead address. Any funds sent to the "green treasury" are permanently and irreversibly burned. This is almost certainly unintentional and should derive from a `PalletId` like the rest of the treasury infrastructure. The `GreenTreasuryPalletId` is already defined but unused here.

```rust
// BEFORE
pub struct GreenTreasuryImpl;
impl Get<AccountId> for GreenTreasuryImpl {
    fn get() -> AccountId {
        AccountId::from([0xff; 32])
    }
}

// AFTER
pub struct GreenTreasuryImpl;
impl Get<AccountId> for GreenTreasuryImpl {
    fn get() -> AccountId {
        GreenTreasuryPalletId::get().into_account_truncating()
    }
}
```

---

### CRITICAL-4: BABE Equivocation Reporting Disabled (Returns None)

**Location:** `impl_runtime_apis!` — `sp_consensus_babe::BabeApi`

**Description:** Both `generate_key_ownership_proof` and `submit_report_equivocation_unsigned_extrinsic` return `None`. This means validator equivocation (double-block production) **cannot be reported or slashed**. Validators can equivocate with zero consequences, directly compromising consensus safety.

```rust
// BEFORE
fn generate_key_ownership_proof(
    _slot: sp_consensus_babe::Slot,
    _authority_id: sp_consensus_babe::AuthorityId,
) -> Option<sp_consensus_babe::OpaqueKeyOwnershipProof> {
    None
}
fn submit_report_equivocation_unsigned_extrinsic(
    _equivocation_proof: sp_consensus_babe::EquivocationProof<<Block as BlockT>::Header>,
    _key_owner_proof: sp_consensus_babe::OpaqueKeyOwnershipProof,
) -> Option<()> {
    None
}

// AFTER
fn generate_key_ownership_proof(
    slot: sp_consensus_babe::Slot,
    authority_id: sp_consensus_babe::AuthorityId,
) -> Option<sp_consensus_babe::OpaqueKeyOwnershipProof> {
    use sp_runtime::traits::OpaqueKeys;
    Historical::prove((sp_consensus_babe::KEY_TYPE, &authority_id))
        .map(|p| p.encode())
        .map(sp_consensus_babe::OpaqueKeyOwnershipProof::new)
}
fn submit_report_equivocation_unsigned_extrinsic(
    equivocation_proof: sp_consensus_babe::EquivocationProof<<Block as BlockT>::Header>,
    key_owner_proof: sp_consensus_babe::OpaqueKeyOwnershipProof,
) -> Option<()> {
    let key_owner_proof = key_owner_proof.decode()?;
    Babe::submit_unsigned_equivocation_report(equivocation_proof, key_owner_proof)
}
```

---

### CRITICAL-5: GRANDPA Equivocation Reporting Disabled (Returns None)

**Location:** `impl_runtime_apis!` — `sp_consensus_grandpa::GrandpaApi`

**Description:** Same issue as CRITICAL-4 but for GRANDPA finality. Validators who equivocate on finality votes face zero consequences, undermining finality guarantees.

```rust
// BEFORE
fn submit_report_equivocation_unsigned_extrinsic(
    _equivocation: sp_consensus_grandpa::EquivocationProof<...>,
    _key_owner: sp_consensus_grandpa::OpaqueKeyOwnershipProof,
) -> Option<()> {
    None
}
fn generate_key_ownership_proof(
    _set_id: sp_consensus_grandpa::SetId,
    _authority_id: sp_consensus_grandpa::AuthorityId,
) -> Option<sp_consensus_grandpa::OpaqueKeyOwnershipProof> {
    None
}

// AFTER
fn submit_report_equivocation_unsigned_extrinsic(
    equivocation_proof: sp_consensus_grandpa::EquivocationProof<
        <Block as BlockT>::Hash,
        NumberFor<Block>,
    >,
    key_owner_proof: sp_consensus_grandpa::OpaqueKeyOwnershipProof,
) -> Option<()> {
    let key_owner_proof = key_owner_proof.decode()?;
    Grandpa::submit_unsigned_equivocation_report(equivocation_proof, key_owner_proof)
}
fn generate_key_ownership_proof(
    set_id: sp_consensus_grandpa::SetId,
    authority_id: sp_consensus_grandpa::AuthorityId,
) -> Option<sp_consensus_grandpa::OpaqueKeyOwnershipProof> {
    Historical::prove((sp_consensus_grandpa::KEY_TYPE, &authority_id))
        .map(|p| p.encode())
        .map(sp_consensus_grandpa::OpaqueKeyOwnershipProof::new)
}
```

---

### CRITICAL-6: Sudo Pallet Present in Production Runtime

**Location:** `construct_runtime!` — index 6

**Description:** `Sudo: pallet_sudo = 6` grants a single key unrestricted root access over the entire chain — bypassing all governance. This is appropriate only for testnets. A production chain must remove Sudo and replace it with governance-gated root origins. Its presence means one compromised key = chain takeover.

```rust
// BEFORE (in construct_runtime!)
Sudo: pallet_sudo = 6,

// AFTER — Remove entirely and ensure all root operations go through governance:
// Delete the Sudo line and update any pallet configs that use `EnsureRoot`
// to use appropriate collective/democracy origins instead.
// Also remove from SignedExtra if applicable.
```

---

### CRITICAL-7: BABE c Parameter Set to Near-Deterministic (255/256)

**Location:** `impl_runtime_apis!` — `BabeApi::configuration()`

**Description:** The `c` parameter `(255, 256)` in BABE configuration represents the probability threshold for VRF-based primary slot claims. A value of `255/256 ≈ 0.996` means almost every slot will have a primary block producer, eliminating the randomness guarantees that BABE relies on for unpredictable leader election. The standard value is `(1, 4)` meaning 25% primary slot probability.

```rust
// BEFORE
c: (255, 256),

// AFTER
c: <Runtime as pallet_babe::Config>::ExpectedBlockTime::get()
    .saturating_mul(1)
    .saturating_div(4)
    // Or simply use the pallet's configured constant:
c: PRIMARY_PROBABILITY,
// Where PRIMARY_PROBABILITY should be defined in pallet_babe::Config as (1, 4)
```

Or inline:

```rust
// BEFORE
c: (255, 256),

// AFTER
c: (1, 4),
```

---

## HIGH Findings

### HIGH-1: Pallet Index Gaps and Ordering Inconsistencies in construct_runtime!

**Location:** `construct_runtime!`

**Description:** Indices 10–19, 21–29, 48–49 are missing/skipped without explanation. Gaps are acceptable but the ordering of pallets does not match their indices (e.g., `Council = 43` and `Democracy = 44` appear after `Treasury = 47` in the source). More critically, `Presale: pallet_presale = 58` breaks the sequential pattern dramatically. Index gaps permanently waste encoding space and make future additions confusing. The out-of-order declaration also makes auditing difficult.

```rust
// BEFORE (excerpt showing ordering mismatch)
        Treasury: pallet_treasury = 47,
        Council: pallet_collective::<Instance1> = 43,
        Democracy: pallet_democracy = 44,

// AFTER — declare in index order for maintainability:
        Council: pallet_collective::<Instance1> = 43,
        Democracy: pallet_democracy = 44,
        Historical: pallet_session::historical = 45,
        Offences: pallet_offences = 46,
        Treasury: pallet_treasury = 47,
        // 48, 49 reserved
        FungibleTokens: pallet_fungible_tokens = 50,
        // ... rest in order
        Presale: pallet_presale = 59, // document why this index was chosen
```

---

### HIGH-2: Contracts bare_call Uses Weight::MAX as Default Gas Limit

**Location:** `impl_runtime_apis!` — `ContractsApi::call` and `ContractsApi::instantiate`

**Description:** When `gas_limit` is `None`, the implementation falls back to `frame_support::weights::Weight::MAX`. This allows RPC callers to trigger unbounded contract execution in the dry-run path. While `bare_call` is off-chain, nodes processing this RPC call can be DoS'd by malicious contracts that consume maximum resources.

```rust
// BEFORE
gas_limit.unwrap_or(frame_support::weights::Weight::MAX),

// AFTER
gas_limit.unwrap_or_else(|| {
    // Use the block's maximum allowed weight as a sensible upper bound
    <Runtime as frame_system::Config>::BlockWeights::get()
        .max_block
        .saturating_div(10) // 10% of block weight for a single dry-run call
}),
```

---

### HIGH-3: Democracy Periods Are Extremely Short (600 Blocks ≈ 1 Hour)

**Location:** Democracy `parameter_types!`

**Description:** At 6-second block times, 600 blocks = 1 hour. This makes `LaunchPeriod`, `VotingPeriod`, `EnactmentPeriod`, and `CooloffPeriod` all 1 hour — far too short for meaningful on-chain governance. Malicious proposals can be launched, voted on, enacted, and have their cooloff expire within a single working day. Kusama uses 7 days for voting; Polkadot uses 28 days.

```rust
// BEFORE
pub const LaunchPeriod: BlockNumber = 600;       // ~1 hour
pub const VotingPeriod: BlockNumber = 600;       // ~1 hour
pub const FastTrackVotingPeriod: BlockNumber = 300; // ~30 min
pub const EnactmentPeriod: BlockNumber = 600;    // ~1 hour
pub const CooloffPeriod: BlockNumber = 600;      // ~1 hour

// AFTER (assuming 6s block time)
pub const LaunchPeriod: BlockNumber = 7 * DAYS;        // 100_800 blocks
pub const VotingPeriod: BlockNumber = 7 * DAYS;        // 100_800 blocks  
pub const FastTrackVotingPeriod: BlockNumber = 3 * HOURS; // 1_800 blocks
pub const EnactmentPeriod: BlockNumber = 2 * DAYS;     // 28_800 blocks
pub const CooloffPeriod: BlockNumber = 7 * DAYS;       // 100_800 blocks
// Where: DAYS = 14_400, HOURS = 600
```

---

### HIGH-4: Council Motion Duration Too Short

**Location:** Council `parameter_types!`

**Description:** `CouncilMotionDuration = 600` blocks = ~1 hour. Council members in different time zones will be unable to vote on motions. Polkadot uses 7 days (`7 * DAYS`).

```rust
// BEFORE
pub const CouncilMotionDuration: BlockNumber = 600;

// AFTER
pub const CouncilMotionDuration: BlockNumber = 3 * DAYS; // 43_200 blocks at 6s
```

---

### HIGH-5: Democracy `InstantAllowed = true` With Only 2/3 Council Required

**Location:** `pallet_democracy::Config`

**Description:** `InstantAllowed = ConstBool<true>` combined with `FastTrackOrigin` requiring only a 2/3 council supermajority (and `FastTrackVotingPeriod = 300` blocks = 30 minutes) means the council can bypass normal governance and enact any proposal in 30 minutes. This is an extreme governance attack surface. Instant should require unanimous council vote.

```rust
// BEFORE
type InstantAllowed = ConstBool<true>;
type InstantOrigin =
    pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 1, 1>;

// AFTER
type InstantAllowed = ConstBool<false>;
// If instant must be kept, restrict to root only:
type InstantOrigin = EnsureRoot<AccountId>;
```

---

## MEDIUM Findings

### MEDIUM-1: TreasuryPalletId Uses Non-Standard Identifier

**Location:** Treasury `parameter_types!`

**Description:** `PalletId(*b"verdist0")` — the `0` suffix is not a standard PalletId convention and suggests copy-paste error. PalletIds must be exactly 8 bytes and should be semantically meaningful. Compare with the properly named `GreenTreasuryPalletId(*b"vrds/trs")`.

```rust
// BEFORE
pub const TreasuryPalletId: PalletId = PalletId(*b"verdist0");

// AFTER
pub const TreasuryPalletId: PalletId = PalletId(*b"vrd/trea");
```

---

### MEDIUM-2: NFT MetadataDepositBase and DepositPerByte Are Excessively High

**Location:** NFTs `parameter_types!`

**Description:** `NftMetadataDeposit = 10 * UNITS` as base + `NftDepositPerByte = 1 * UNITS` per byte means a 100-byte metadata string costs `10 + 100 = 110 UNITS` just in deposits. This will price out legitimate users. Standard chains use micro-unit deposits per byte (e.g., `deposit(1, 0)` patterns from `pallet_assets`).

```rust
// BEFORE
pub const NftMetadataDeposit: Balance = 10 * UNITS;
pub const NftAttributeDeposit: Balance = 1 * UNITS;
pub const NftDepositPerByte: Balance = 1 * UNITS;

// AFTER
pub const NftMetadataDeposit: Balance = UNITS / 10;        // 0.1 UNITS base
pub const NftAttributeDeposit: Balance = UNITS / 100;      // 0.01 UNITS base
pub const NftDepositPerByte: Balance = UNITS / 1_000;      // 0.001 UNITS per byte
```

---

### MEDIUM-3: WeightInfo = () on All Custom Pallets and Several System Pallets

**Location:** Multiple `impl pallet_X::Config for Runtime` blocks

**Description:** Every pallet using `type WeightInfo = ()` assigns zero weight to all its extrinsics. This means those operations are **free** from the block weight perspective, allowing adversarial users to fill blocks with zero-weight transactions, causing DoS. This affects: `pallet_treasury`, `pallet_collective`, `pallet_democracy`, `pallet_nfts`, `pallet_poh`, `pallet_gulf_stream`, `pallet_turbine`, `pallet_zk_compression`, `pallet_address_lookup_tables`, `pallet_sealevel`, `pallet_ibc`.

```rust
// BEFORE (example for treasury)
type WeightInfo = ();

// AFTER
type WeightInfo = pallet_treasury::weights::SubstrateWeight<Runtime>;
// For custom pallets that lack generated weights, at minimum use:
type WeightInfo = pallet_X::weights::SubstrateWeight<Runtime>;
// And run: cargo build --features runtime-benchmarks && ./target/release/node benchmark pallet ...
```

---

### MEDIUM-4: NFT MaxDeadlineDuration Type Mismatch Risk

**Location:** NFTs `parameter_types!` and `pallet_nfts::Config`

**Description:** `NftMaxDeadlineDuration` is declared as `u32 = 201_600` but `pallet_nfts` expects `MaxDeadlineDuration` to be a `BlockNumber` (typically `u32` or `u64` depending on chain configuration). If `BlockNumber` is `u64`, this silently truncates. Additionally, 201,600 blocks at 6s = 14 days, which should be documented explicitly and matched against the type system.

```rust
// BEFORE
pub const NftMaxDeadlineDuration: u32 = 201600;

// AFTER
pub const NftMaxDeadlineDuration: BlockNumber = 14 * DAYS; // 201_600 at 6s blocks
// This ensures type consistency and self-documents the intent
```

---

### MEDIUM-5: try-runtime Test Asserts Weight != Zero (Wrong Assertion)

**Location:** `#[cfg(all(test, feature = "try-runtime"))]` — `try_runtime_upgrade_succeeds`

**Description:** The test asserts that runtime upgrade weight is non-zero. If there are no migrations to run, `execute_on_runtime_upgrade()` legitimately returns zero weight. This test will falsely fail on a clean upgrade with no migrations, creating noise and potentially masking real issues. The correct test is that the upgrade doesn't panic.

```rust
// BEFORE
#[test]
fn try_runtime_upgrade_succeeds() {
    new_test_ext().execute_with(|| {
        let weight = Executive::execute_on_runtime_upgrade();
        assert!(
            weight != frame_support::weights::Weight::zero(),
            "Runtime upgrade should consume weight"
        );
    });
}

// AFTER
#[test]
fn try_runtime_upgrade_succeeds() {
    new_test_ext().execute_with(|| {
        // execute_on_runtime_upgrade returns 0 weight when there are no migrations;
        // the important property is that it does not panic or return an error.
        let _weight = Executive::execute_on_runtime_upgrade();
        // If using try-runtime's pre/post upgrade hooks:
        // Executive::try_runtime_upgrade(UpgradeCheckSelect::All).unwrap();
    });
}
```

---

## LOW Findings

### LOW-1: StringLimit Shared Between NFTs and Assets Creates Coupling

**Location:** `parameter_types!` — `StringLimit`

**Description:** A single `StringLimit = 64` is shared between both the (commented-out) Assets pallet and the NFTs pallet. If Assets is re-enabled with different string requirements, changing this value will affect NFTs. These should be separate constants.

```rust
// BEFORE
parameter_types! {
    pub const StringLimit: u32 = 64;
}
// Used by both Assets and NFTs

// AFTER
parameter_types! {
    pub const AssetStringLimit: u32 = 50;   // pallet_assets standard
    pub const NftStringLimit: u32 = 256;    // NFTs may need longer names/descriptions
}
// In pallet_nfts::Config:
type StringLimit = NftStringLimit;
```

---

### LOW-2: MaxComputeUnits Typed as u64 Constant May Not Match Pallet Expectation

**Location:** `parameter_types!` — `MaxComputeUnits`

**Description:** `pub const MaxComputeUnits: u64 = 200_000` — if `pallet_sealevel::Config::MaxComputeUnits` expects a `Get<u32>` (common for frame constants), this will cause a compile-time type mismatch. The value `200_000` also matches Solana's per-transaction compute unit limit, which may be intentional but should be documented.

```rust
// BEFORE
pub const MaxComputeUnits: u64 = 200_000;

// AFTER
// Verify pallet_sealevel::Config::MaxComputeUnits bound, then:
pub const MaxComputeUnits: u32 = 200_000; // Solana-compatible CU limit per tx
// OR if u64 is correct, add a comment:
pub const MaxComputeUnits: u64 = 200_000; // Matches Solana's per-transaction CU budget
```

---

### LOW-3: Genesis Builder Returns Empty Preset Names

**Location:** `impl_runtime_apis!` — `sp_genesis_builder::GenesisBuilder`

**Description:** `preset_names()` returns `Default::default()` (empty vec) and `get_preset` always returns `None`. This means `chain-spec-builder` tooling cannot auto-generate genesis configs from presets, forcing all deployments to manually craft JSON genesis. At minimum a `"development"` preset should be provided.

```rust
// BEFORE
fn get_preset(id: &Option<sp_genesis_builder::PresetId>) -> Option<Vec<u8>> {
    frame_support::genesis_builder_helper::get_preset::<RuntimeGenesisConfig>(
        id,
        |_| None,
    )
}
fn preset_names() -> Vec<sp_genesis_builder::PresetId> {
    Default::default()
}

// AFTER
fn get_preset(id: &Option<sp_genesis_builder::PresetId>) -> Option<Vec<u8>> {
    frame_support::genesis_builder_helper::get_preset::<RuntimeGenesisConfig>(
        id,
        |preset_name| match preset_name {
            "development" => Some(development_genesis_preset()),
            "local_testnet" => Some(local_testnet_genesis_preset()),
            _ => None,
        },
    )
}
fn preset_names() -> Vec<sp_genesis_builder::PresetId> {
    vec![
        sp_genesis_builder::PresetId::from("development"),
        sp_genesis_builder::PresetId::from("local_testnet"),
    ]
}
// Implement development_genesis_preset() and local_testnet_genesis_preset()
// returning serde_json encoded RuntimeGenesisConfig
```

---

## Summary Table

| ID | Severity | Category | One-Line Description |
|---|---|---|---|
| CRITICAL-1 | CRITICAL | Parameter Tuning | 10% treasury burn destroys funds each spend period |
| CRITICAL-2 | CRITICAL | Parameter Tuning | Uncapped treasury spend allows full drain in one tx |
| CRITICAL-3 | CRITICAL | Genesis/Funds | Green treasury routes to burn address `[0xff;32]` |
| CRITICAL-4 | CRITICAL | Security | BABE equivocation reporting disabled, no slashing |
| CRITICAL-5 | CRITICAL | Security | GRANDPA equivocation reporting disabled, no slashing |
| CRITICAL-6 | CRITICAL | Security | Sudo pallet present, single key owns entire chain |
| CRITICAL-7 | CRITICAL | Parameter Tuning | BABE `c=(255/256)` destroys VRF randomness |
| HIGH-1 | HIGH | construct_runtime! | Pallet declaration order mismatches indices |
| HIGH-2 | HIGH | Security | `Weight::MAX` gas default enables RPC DoS |
| HIGH-3 | HIGH | Parameter Tuning | Governance periods are 1 hour — too short |
| HIGH-4 | HIGH | Parameter Tuning | Council motion duration 1 hour — too short |
| HIGH-5 | HIGH | Security | InstantAllowed=true with low council threshold |
| MEDIUM-1 | MEDIUM | Pallet Config | Non-standard TreasuryPalletId with trailing `0` |
| MEDIUM-2 | MEDIUM | Parameter Tuning | NFT deposit per byte priced at 1 UNIT — too high |
| MEDIUM-3 | MEDIUM | Security | `WeightInfo = ()` on 11 pallets enables DoS |
| MEDIUM-4 | MEDIUM | Pallet Config | NFT deadline duration type may mismatch BlockNumber |
| MEDIUM-5 | MEDIUM | Testing | try-runtime test asserts wrong invariant |
| LOW-1 | LOW | Pallet Config | Shared StringLimit couples Assets and NFTs |
| LOW-2 | LOW | Pallet Config | MaxComputeUnits u64 may not match pallet bound |
| LOW-3 | LOW | Genesis Config | No genesis presets defined for tooling |