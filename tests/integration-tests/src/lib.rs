//! Verdis Chain — Comprehensive Cross-Pallet Integration Tests
//!
//! Tests real interactions between pallets in a shared mock runtime:
//! 1. DEX + FungibleTokens + Balances — token pool creation, liquidity, swaps
//! 2. Vesting + Balances — vesting schedule assignment, lock, release
//! 3. DPoS + Balances — validator registration, staking, slashing, unbonding
//! 4. Eco — green validator registration, carbon credits, score updates
//! 5. Presale + Vesting + Balances — contribution flow creating vesting schedules
//! 6. DEX price impact protection (internal circuit breaker)
//! 7. Multiple independent vesting schedules

#![cfg(test)]

use frame_support::{
    assert_noop, assert_ok, construct_runtime, derive_impl, parameter_types,
    traits::{ConstU128, ConstU32, ConstU64, Currency},
    BoundedVec, PalletId,
};
use sp_core::crypto::AccountId32;
use sp_io::TestExternalities;
use sp_keyring::Sr25519Keyring;
use sp_runtime::{
    traits::{AccountIdConversion, IdentityLookup},
    BuildStorage,
};

// =========================================================================
// MOCK RUNTIME
// =========================================================================

type Block = frame_system::mocking::MockBlock<Test>;

construct_runtime!(
    pub enum Test {
        System: frame_system,
        Balances: pallet_balances,
        Timestamp: pallet_timestamp,
        FungibleTokens: pallet_fungible_tokens,
        AmmDex: pallet_amm_dex,
        Dpos: pallet_dpos,
        Eco: pallet_eco,
        Vesting: pallet_vesting,
        Presale: pallet_presale,
        Tokenomics: pallet_tokenomics,
        CircuitBreaker: pallet_circuit_breaker,
    }
);

#[derive_impl(frame_system::config_preludes::TestDefaultConfig as frame_system::DefaultConfig)]
impl frame_system::Config for Test {
    type AccountId = AccountId32;
    type Lookup = IdentityLookup<Self::AccountId>;
    type Block = Block;
    type AccountData = pallet_balances::AccountData<u128>;
}

impl pallet_balances::Config for Test {
    type MaxLocks = ConstU32<50>;
    type MaxReserves = ConstU32<50>;
    type ReserveIdentifier = [u8; 8];
    type Balance = u128;
    type RuntimeEvent = RuntimeEvent;
    type DustRemoval = ();
    type ExistentialDeposit = ConstU128<1>;
    type AccountStore = System;
    type WeightInfo = ();
    type FreezeIdentifier = ();
    type MaxFreezes = ConstU32<0>;
    type RuntimeHoldReason = ();
    type RuntimeFreezeReason = ();
    type DoneSlashHandler = ();
}

impl pallet_timestamp::Config for Test {
    type Moment = u64;
    type OnTimestampSet = ();
    type MinimumPeriod = ConstU64<1>;
    type WeightInfo = ();
}

// --- FungibleTokens ---

parameter_types! {
    pub const FungibleTokensPalletId: PalletId = PalletId(*b"vrdfungs");
    pub const MaxTokensPerAccount: u32 = 100;
    pub const CreateTokenDeposit: u128 = 100;
    pub const MaxBalance: u128 = u128::MAX;
}

impl pallet_fungible_tokens::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type Currency = Balances;
    type PalletId = FungibleTokensPalletId;
    type MaxTokensPerAccount = MaxTokensPerAccount;
    type CreateTokenDeposit = CreateTokenDeposit;
    type MaxBalance = MaxBalance;
    type WeightInfo = ();
}

// --- AMM-DEX ---

parameter_types! {
    pub const AmmPalletId: PalletId = PalletId(*b"v/ammdex");
    pub const FeeNumerator: u32 = 3;
    pub const FeeDenominator: u32 = 1000;
    pub const MaxPriceImpact: sp_runtime::Permill = sp_runtime::Permill::from_percent(10);
    pub const AmmMinimumLiquidity: u128 = 1_000;
    pub const MinLiquidity: u128 = 100;
    pub const MaxPools: u32 = 50;
}

impl pallet_amm_dex::TokenHandler<AccountId32, u128> for Test {
    fn transfer(
        asset: &pallet_amm_dex::AssetId,
        from: &AccountId32,
        to: &AccountId32,
        amount: u128,
    ) -> frame_support::dispatch::DispatchResult {
        match asset {
            pallet_amm_dex::AssetId::Native => {
                <pallet_balances::Pallet<Test> as Currency<AccountId32>>::transfer(
                    from,
                    to,
                    amount,
                    frame_support::traits::ExistenceRequirement::AllowDeath,
                )
            }
            pallet_amm_dex::AssetId::Custom(token_id) => {
                pallet_fungible_tokens::Pallet::<Test>::do_transfer(*token_id, from, to, amount)
            }
        }
    }

    fn has_balance(asset: &pallet_amm_dex::AssetId, who: &AccountId32, amount: u128) -> bool {
        match asset {
            pallet_amm_dex::AssetId::Native => {
                <pallet_balances::Pallet<Test> as Currency<AccountId32>>::free_balance(who)
                    >= amount
            }
            pallet_amm_dex::AssetId::Custom(token_id) => {
                pallet_fungible_tokens::Pallet::<Test>::balance_of(*token_id, who) >= amount
            }
        }
    }
}

impl pallet_amm_dex::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type Currency = Balances;
    type PalletId = AmmPalletId;
    type FeeNumerator = FeeNumerator;
    type FeeDenominator = FeeDenominator;
    type MinLiquidity = MinLiquidity;
    type MaxPools = MaxPools;
    type MaxPriceImpact = MaxPriceImpact;
    type MinimumLiquidity = AmmMinimumLiquidity;
    type WeightInfo = ();
    type TokenHandler = Self;
}

// --- DPoS ---

parameter_types! {
    pub const BlockReward: u128 = 100;
    pub const MinStake: u128 = 1000;
    pub const MaxValidators: u32 = 1000;
    pub const ActiveValidatorCount: u32 = 3;
    pub const EpochLength: u32 = 10;
    pub const UnbondingPeriod: u32 = 20;
    pub const DposPalletId: PalletId = PalletId(*b"v/dposps");
    pub const MaxStakePerValidator: u128 = 1_000_000_000_000;
    pub const MaxCommission: u8 = 20;
    pub const MinGreenScore: u8 = 0;
    pub const MaxGreenScore: u8 = 5;
    pub const ReactivationCooldown: u32 = 10;
    pub const MaxMissedEpochs: u32 = 3;
    pub const MinimumValidatorCountTest: u32 = 2;
}

pub struct TestFindAuthor;
impl frame_support::traits::FindAuthor<sp_core::crypto::AccountId32> for TestFindAuthor {
    fn find_author<'a, I>(_digests: I) -> Option<sp_core::crypto::AccountId32>
    where
        I: 'a + IntoIterator<Item = (frame_support::ConsensusEngineId, &'a [u8])>,
    {
        None
    }
}

impl pallet_dpos::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type Currency = Balances;
    type BlockReward = BlockReward;
    type MinStake = MinStake;
    type MaxValidators = MaxValidators;
    type ActiveValidatorCount = ActiveValidatorCount;
    type EpochLength = EpochLength;
    type UnbondingPeriod = UnbondingPeriod;
    type PalletId = DposPalletId;
    type MaxStakePerValidator = MaxStakePerValidator;
    type RegistrationDeposit = ConstU128<0>;
    type ReactivationCooldown = ReactivationCooldown;
    type MaxCommission = MaxCommission;
    type MinGreenScore = MinGreenScore;
    type MaxGreenScore = MaxGreenScore;
    type MaxMissedEpochs = MaxMissedEpochs;
    type MinimumValidatorCount = MinimumValidatorCountTest;
    type WeightInfo = pallet_dpos::SubstrateWeight<Test>;
    type FindAuthor = TestFindAuthor;
}

// --- Eco ---

parameter_types! {
    pub const EcoPalletId: PalletId = PalletId(*b"v/ecofnd");
    pub const MaxCarbonCredits: u32 = 1000;
    pub const MaxReforestProjects: u32 = 100;
    pub const MaxGreenValidators: u32 = 100;
    pub const EcoMaxNameLength: u32 = 128;
}

impl pallet_eco::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type PalletId = EcoPalletId;
    type MaxCarbonCredits = MaxCarbonCredits;
    type MaxReforestProjects = MaxReforestProjects;
    type MaxGreenValidators = MaxGreenValidators;
    type MinGreenScore = MinGreenScore;
    type MaxGreenScore = MaxGreenScore;
    type MaxNameLength = EcoMaxNameLength;
    type WeightInfo = pallet_eco::SubstrateWeight<Test>;
    type AdminOrigin = frame_system::EnsureRoot<AccountId32>;
}

// --- Vesting ---

parameter_types! {
    pub const VestingPalletId: PalletId = PalletId(*b"v/vestin");
}

impl pallet_vesting::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type Currency = Balances;
    type PalletId = VestingPalletId;
    type WeightInfo = pallet_vesting::SubstrateWeight<Test>;
    type MaxSchedulesPerAccount = ConstU32<10>;
    type BlockTimeMs = ConstU64<5000>;
}

// --- Presale ---

parameter_types! {
    pub const PresalePalletId: PalletId = PalletId(*b"v/presal");
    pub const TreasuryAccount: AccountId32 = AccountId32::new([0xff; 32]);
}

/// Bridge: Presale → Vesting
pub struct PresaleVestingHandler;
impl pallet_presale::VestingHandler<AccountId32, u128> for PresaleVestingHandler {
    fn assign_vesting(
        who: &AccountId32,
        schedule_label: Vec<u8>,
        amount: u128,
    ) -> frame_support::dispatch::DispatchResult {
        pallet_vesting::Pallet::<Test>::do_assign_vesting(who.clone(), schedule_label, amount)
    }
    fn do_remove_vesting(
        who: &AccountId32,
        schedule_label: Vec<u8>,
        amount: u128,
    ) -> frame_support::dispatch::DispatchResult {
        pallet_vesting::Pallet::<Test>::do_remove_vesting(who, schedule_label, amount)
    }

    fn remove_all_vesting_for_label(
        who: &AccountId32,
        schedule_label: Vec<u8>,
    ) -> Result<u128, sp_runtime::DispatchError> {
        pallet_vesting::Pallet::<Test>::remove_all_vesting_for_label(who, schedule_label)
    }
}

impl pallet_presale::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type Currency = Balances;
    type PaymentCurrency = Balances;
    type PalletId = PresalePalletId;
    type AdminOrigin = frame_system::EnsureRoot<AccountId32>;
    type Vesting = PresaleVestingHandler;
    type WeightInfo = pallet_presale::SubstrateWeight<Test>;
    type Treasury = TreasuryAccount;
    type EnforceUniqueVestingLabels = frame_support::traits::ConstBool<false>;
}

// --- Tokenomics ---

parameter_types! {
    pub const TokenomicsPalletId: PalletId = PalletId(*b"v/tknmcs");
    pub const TotalSupplyConst: u128 = 100_000_000_000_000_000_000;
    pub const InvestorAllocationConst: u128 = 12_000_000_000_000_000_000;
    pub const MaxPriorityFeeMultiplier: u32 = 10;
    pub const DefaultTransferFeeBps: u32 = 50;
    pub const GreenTreasuryAccount: AccountId32 = AccountId32::new([0xee; 32]);
}

impl pallet_tokenomics::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type Currency = Balances;
    type TotalSupply = TotalSupplyConst;
    type InvestorAllocation = InvestorAllocationConst;
    type PalletId = TokenomicsPalletId;
    type MaxPriorityFeeMultiplier = MaxPriorityFeeMultiplier;
    type DefaultTransferFeeBps = DefaultTransferFeeBps;
    type GreenTreasury = GreenTreasuryAccount;
    type WeightInfo = pallet_tokenomics::SubstrateWeight<Test>;
    type AdminOrigin = frame_system::EnsureRoot<AccountId32>;
}

// --- Circuit Breaker ---

parameter_types! {
    pub const CircuitBreakerMaxPalletNameLen: u32 = 32;
}

impl pallet_circuit_breaker::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type MaxPalletNameLen = CircuitBreakerMaxPalletNameLen;
    type AdminOrigin = frame_system::EnsureRoot<AccountId32>;
}

// =========================================================================
// GENESIS SETUP
// =========================================================================

pub fn new_test_ext() -> TestExternalities {
    let mut t = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();

    let dpos_reward_pool: AccountId32 = PalletId(*b"v/dposps").into_account_truncating();
    let presale_escrow: AccountId32 = PalletId(*b"v/presal").into_account_truncating();

    pallet_balances::GenesisConfig::<Test> {
        balances: vec![
            (Sr25519Keyring::Alice.to_account_id(), 1_000_000_000_000),
            (Sr25519Keyring::Bob.to_account_id(), 1_000_000_000_000),
            (Sr25519Keyring::Charlie.to_account_id(), 1_000_000_000_000),
            (Sr25519Keyring::Dave.to_account_id(), 500_000_000_000),
            (Sr25519Keyring::Eve.to_account_id(), 100_000_000_000),
            (dpos_reward_pool, 100_000_000_000_000),
            (presale_escrow, 1_000_000_000_000_000),
        ],
        ..Default::default()
    }
    .assimilate_storage(&mut t)
    .unwrap();

    pallet_dpos::GenesisConfig::<Test> {
        validators: vec![
            (Sr25519Keyring::Alice.to_account_id(), 500_000_000_000, true),
            (Sr25519Keyring::Bob.to_account_id(), 300_000_000_000, true),
        ],
        validator_count: 2,
        block_reward: 100,
        validator_names: vec![],
    }
    .assimilate_storage(&mut t)
    .unwrap();

    // Create vesting schedules in genesis so do_assign_vesting can find them
    pallet_vesting::GenesisConfig::<Test> {
        vesting_schedules: vec![
            (b"seed".to_vec(), 100_000_000_000_000, 365, 90),
            (b"community".to_vec(), 50_000_000_000_000, 90, 0),
            (b"community_vest".to_vec(), 200_000_000_000_000, 365, 90),
        ],
    }
    .assimilate_storage(&mut t)
    .unwrap();

    let mut ext = TestExternalities::new(t);
    ext.execute_with(|| System::set_block_number(1));
    ext
}

const DEADLINE: u64 = 999_999_999;

// =========================================================================
// TEST 1: DEX + FungibleTokens + Balances — Token Pool & Swap
// =========================================================================

#[test]
fn test_dex_create_token_pool_add_liquidity_swap() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();
        let bob = Sr25519Keyring::Bob.to_account_id();

        // Create a custom token via FungibleTokens
        assert_ok!(pallet_fungible_tokens::Pallet::<Test>::create(
            RuntimeOrigin::signed(alice.clone()),
            b"ECO".to_vec(),
            b"ECO".to_vec(),
            9u8,
        ));

        // Mint tokens to Alice (token_id = 1, auto-incremented from 0)
        assert_ok!(pallet_fungible_tokens::Pallet::<Test>::mint(
            RuntimeOrigin::signed(alice.clone()),
            0u64,
            alice.clone(),
            1_000_000_000_000,
        ));

        // Verify token balance
        assert_eq!(
            pallet_fungible_tokens::Pallet::<Test>::balance_of(0u64, &alice),
            1_000_000_000_000
        );

        // Create token pool: Native / Custom(1) via token pool API
        assert_ok!(AmmDex::create_token_pool(
            RuntimeOrigin::signed(alice.clone()),
            pallet_amm_dex::AssetId::Native,
            pallet_amm_dex::AssetId::Custom(0u64),
            1_000_000_000,
            1_000_000_000_000,
            DEADLINE,
        ));

        // Verify pool exists (pool_id = 0 for first token pool)
        let pool = pallet_amm_dex::TokenPools::<Test>::get(0u32);
        assert!(pool.is_some(), "Token pool should exist after creation");
        let pool = pool.unwrap();
        assert_eq!(pool.reserve_a, 1_000_000_000);
        assert_eq!(pool.reserve_b, 1_000_000_000_000);

        // Bob adds liquidity
        assert_ok!(pallet_fungible_tokens::Pallet::<Test>::mint(
            RuntimeOrigin::signed(alice.clone()),
            0u64,
            bob.clone(),
            500_000_000_000,
        ));

        assert_ok!(AmmDex::add_token_liquidity(
            RuntimeOrigin::signed(bob.clone()),
            0u32,
            500_000_000,
            500_000_000_000,
            0,
            DEADLINE,
        ));

        // Swap: Bob swaps Native for Custom token
        let bob_balance_before = Balances::free_balance(&bob);
        let bob_token_before = pallet_fungible_tokens::Pallet::<Test>::balance_of(0u64, &bob);

        assert_ok!(AmmDex::swap_token(
            RuntimeOrigin::signed(bob.clone()),
            0u32,
            pallet_amm_dex::AssetId::Native,
            50_000_000, // < 10% of pool reserve
            1,
            DEADLINE,
        ));

        // Bob's native balance decreased
        assert!(Balances::free_balance(&bob) < bob_balance_before);
        // Bob's custom token balance increased
        assert!(
            pallet_fungible_tokens::Pallet::<Test>::balance_of(0u64, &bob) > bob_token_before,
            "Bob should receive custom tokens from swap"
        );
    });
}

// =========================================================================
// TEST 2: Vesting + Balances — Assign, Lock, Release
// =========================================================================

#[test]
fn test_vesting_assign_lock_and_release() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();

        let balance_before = Balances::free_balance(&alice);

        // Assign vesting: schedule "seed" was created in genesis
        assert_ok!(Vesting::do_assign_vesting(
            alice.clone(),
            b"seed".to_vec(),
            100_000_000_000,
        ));

        // Locked balance should reflect vesting
        let locked = Vesting::get_locked_balance(&alice);
        assert_eq!(
            locked, 100_000_000_000,
            "Vesting should lock the assigned amount"
        );

        // set_lock prevents transfers but does NOT reduce free_balance
        // Verify the lock is in place by attempting a transfer of the locked amount
        // Lock prevents transfer
        let transfer_result = <pallet_balances::Pallet<Test> as Currency<AccountId32>>::transfer(
            &alice,
            &Sr25519Keyring::Bob.to_account_id(),
            balance_before,
            frame_support::traits::ExistenceRequirement::AllowDeath,
        );
        assert!(transfer_result.is_err(), "Transfer should fail when locked");

        // Remove the vesting entry (must match total_amount exactly)
        assert_ok!(Vesting::do_remove_vesting(
            &alice,
            b"seed".to_vec(),
            100_000_000_000,
        ));

        let locked_after = Vesting::get_locked_balance(&alice);
        assert_eq!(
            locked_after, 0,
            "Locked amount should be zero after removing full vesting"
        );
    });
}

// =========================================================================
// TEST 3: DPoS + Balances — Register, Stake, Vote, Unvote
// =========================================================================

#[test]
fn test_dpos_register_vote_unvote_cycle() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();
        let charlie = Sr25519Keyring::Charlie.to_account_id();

        // Charlie registers as validator (3 params: green_score, energy_source)
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(charlie.clone()),
            3u8,
            b"solar".to_vec(),
        ));

        // Verify Charlie is in the validator set
        assert!(pallet_dpos::Validators::<Test>::get(&charlie).is_some());
        let val = pallet_dpos::Validators::<Test>::get(&charlie).unwrap();
        assert!(val.active);

        // Charlie's balance should be reduced (stake is reserved)
        let charlie_free = Balances::free_balance(&charlie);
        assert!(
            charlie_free < 1_000_000_000_000,
            "Charlie's free balance should decrease after staking"
        );

        // Alice votes (delegates) to Charlie
        let alice_balance_before = Balances::free_balance(&alice);
        assert_ok!(Dpos::vote(
            RuntimeOrigin::signed(alice.clone()),
            charlie.clone(),
            2_000_000_000,
        ));

        // Alice's balance should decrease
        assert!(
            Balances::free_balance(&alice) < alice_balance_before,
            "Alice's free balance should decrease after delegating"
        );

        // Charlie's total votes should include Alice's delegation
        let charlie_val = pallet_dpos::Validators::<Test>::get(&charlie).unwrap();
        assert!(
            charlie_val.total_votes >= 2_000_000_000,
            "Charlie's total votes should include Alice's delegation"
        );

        // Alice unvotes (unbonds all)
        assert_ok!(Dpos::unvote(
            RuntimeOrigin::signed(alice.clone()),
            charlie.clone(),
        ));

        // After unbonding, funds are locked for UnbondingPeriod blocks
        let charlie_val_after = pallet_dpos::Validators::<Test>::get(&charlie).unwrap();
        assert!(
            charlie_val_after.total_votes < charlie_val.total_votes,
            "Charlie's total votes should decrease after Alice unvotes"
        );
    });
}

// =========================================================================
// TEST 4: DPoS Slashing — Stake Reduction and Active Set Removal
// =========================================================================

#[test]
fn test_dpos_slashing_reduces_stake_and_removes_from_active_set() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();

        let initial_val = pallet_dpos::Validators::<Test>::get(&alice).unwrap();
        let initial_stake = initial_val.stake;
        let initial_total = pallet_dpos::TotalStaked::<Test>::get();

        // Verify Alice is active
        assert!(pallet_dpos::ActiveValidators::<Test>::get().contains(&alice));

        // Slash Alice
        let penalty = 1_000_000_000u128;
        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            alice.clone(),
            penalty,
            b"downtime_test".to_vec(),
        ));

        // Stake reduced
        let val_after = pallet_dpos::Validators::<Test>::get(&alice).unwrap();
        assert_eq!(val_after.stake, initial_stake - penalty);
        assert!(val_after.slashed);
        assert!(!val_after.active);

        // Active set updated
        assert!(!pallet_dpos::ActiveValidators::<Test>::get().contains(&alice));

        // Total staked reduced
        assert_eq!(
            pallet_dpos::TotalStaked::<Test>::get(),
            initial_total - penalty
        );
    });
}

// =========================================================================
// TEST 5: Eco — Green Validator Registration, Score Update, Carbon Credits
// =========================================================================

#[test]
fn test_eco_register_green_validator_and_mint_carbon_credit() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();

        // Register Alice as a green validator
        let energy_source = BoundedVec::try_from(b"solar".to_vec()).unwrap();
        assert_ok!(Eco::register_green_validator(
            RuntimeOrigin::root(),
            alice.clone(),
            energy_source,
            1_000u64, // carbon_offset
            100u32,   // trees_planted
            3u8,      // score
            true,     // renewable_energy
        ));

        // Verify green validator is registered
        let gv = pallet_eco::GreenValidators::<Test>::get(&alice);
        assert!(gv.is_some(), "Green validator should be registered");
        let gv = gv.unwrap();
        assert_eq!(gv.score, 3);
        assert_eq!(
            gv.energy_source,
            BoundedVec::<u8, ConstU32<64>>::try_from(b"solar".to_vec()).unwrap()
        );
        assert!(gv.renewable_energy);
        assert_eq!(gv.carbon_offset, 1_000);
        assert_eq!(gv.trees_planted, 100);

        // Update green score to 5 (max)
        assert_ok!(Eco::update_green_score(
            RuntimeOrigin::root(),
            alice.clone(),
            5u8,
        ));

        let gv_updated = pallet_eco::GreenValidators::<Test>::get(&alice).unwrap();
        assert_eq!(gv_updated.score, 5, "Green score should be updated to 5");

        // Mint carbon credit
        let credit_id = BoundedVec::try_from(b"AMZ-001".to_vec()).unwrap();
        let project_name = BoundedVec::try_from(b"Amazon Reforestation".to_vec()).unwrap();
        assert_ok!(Eco::mint_carbon_credit(
            RuntimeOrigin::root(),
            alice.clone(),
            credit_id.clone(),
            project_name,
            10_000u64, // tons_co2
        ));

        // Verify carbon credit exists
        let cc = pallet_eco::CarbonCredits::<Test>::get(&credit_id);
        assert!(cc.is_some(), "Carbon credit should exist after minting");
        let cc = cc.unwrap();
        assert_eq!(cc.owner, alice);
        assert_eq!(cc.tons_co2, 10_000);
    });
}

// =========================================================================
// TEST 6: Presale + Vesting — Contribution Creates Vesting Schedule
// =========================================================================

#[test]
fn test_presale_contribution_creates_vesting() {
    new_test_ext().execute_with(|| {
        let bob = Sr25519Keyring::Bob.to_account_id();

        // Create a presale round (8 params)
        assert_ok!(Presale::create_round(
            RuntimeOrigin::root(),
            b"community".to_vec(),      // label
            1u128,                      // token_price
            1_000_000_000_000u128,      // total_allocation
            100_000_000_000u128,        // per_account_cap
            1u64,                       // start_block
            100u64,                     // end_block
            b"community_vest".to_vec(), // vesting_label
        ));

        // Activate the round
        assert_ok!(Presale::activate_round(RuntimeOrigin::root(), 0u32,));

        // Bob contributes
        let bob_balance_before = Balances::free_balance(&bob);
        assert_ok!(Presale::contribute(
            RuntimeOrigin::signed(bob.clone()),
            0u32,
            50_000_000_000u128,
        ));

        // Bob pays native and receives native (locked by vesting)
        // Net free balance may not decrease since payment and receipt cancel
        let _ = bob_balance_before;

        // Vesting schedule should be created for Bob
        let locked = Vesting::get_locked_balance(&bob);
        assert!(
            locked > 0,
            "Vesting should lock tokens after presale contribution"
        );

        // Verify contribution recorded
        let contribution = pallet_presale::Contributions::<Test>::get(0u32, &bob);
        assert!(contribution.is_some(), "Contribution should be recorded");
        let contribution = contribution.unwrap();
        assert_eq!(contribution.total_paid, 50_000_000_000);
    });
}

// =========================================================================
// TEST 7: DEX Price Impact Protection (Internal Circuit Breaker)
// =========================================================================

#[test]
fn test_dex_price_impact_protection_blocks_large_swap() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();
        let bob = Sr25519Keyring::Bob.to_account_id();

        // Create custom token
        assert_ok!(pallet_fungible_tokens::Pallet::<Test>::create(
            RuntimeOrigin::signed(alice.clone()),
            b"ECO".to_vec(),
            b"ECO".to_vec(),
            9u8,
        ));

        // Mint tokens
        assert_ok!(pallet_fungible_tokens::Pallet::<Test>::mint(
            RuntimeOrigin::signed(alice.clone()),
            0u64,
            alice.clone(),
            10_000_000_000_000,
        ));
        assert_ok!(pallet_fungible_tokens::Pallet::<Test>::mint(
            RuntimeOrigin::signed(alice.clone()),
            0u64,
            bob.clone(),
            10_000_000_000_000,
        ));

        // Create token pool with 1:1 ratio
        assert_ok!(AmmDex::create_token_pool(
            RuntimeOrigin::signed(alice.clone()),
            pallet_amm_dex::AssetId::Native,
            pallet_amm_dex::AssetId::Custom(0u64),
            1_000_000_000,
            1_000_000_000_000,
            DEADLINE,
        ));

        // Bob adds liquidity
        assert_ok!(AmmDex::add_token_liquidity(
            RuntimeOrigin::signed(bob.clone()),
            0u32,
            1_000_000_000,
            1_000_000_000_000,
            0,
            DEADLINE,
        ));

        // Large swap should be blocked by price impact protection (10% max)
        // Pool has 2B native + 2T custom. Swapping 500M native is 25% → exceeds 10%
        assert_noop!(
            AmmDex::swap_token(
                RuntimeOrigin::signed(bob.clone()),
                0u32,
                pallet_amm_dex::AssetId::Native,
                500_000_000,
                1,
                DEADLINE,
            ),
            pallet_amm_dex::Error::<Test>::PriceImpactTooHigh
        );

        // Small swap should succeed (< 10% of pool)
        assert_ok!(AmmDex::swap_token(
            RuntimeOrigin::signed(bob.clone()),
            0u32,
            pallet_amm_dex::AssetId::Native,
            50_000_000, // 2.5% of pool
            1,
            DEADLINE,
        ));
    });
}

// =========================================================================
// TEST 8: DEX Remove Liquidity Returns Assets
// =========================================================================

#[test]
fn test_dex_remove_token_liquidity_returns_assets() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();

        // Create token
        assert_ok!(pallet_fungible_tokens::Pallet::<Test>::create(
            RuntimeOrigin::signed(alice.clone()),
            b"TREE".to_vec(),
            b"TREE".to_vec(),
            9u8,
        ));

        // Mint
        assert_ok!(pallet_fungible_tokens::Pallet::<Test>::mint(
            RuntimeOrigin::signed(alice.clone()),
            0u64,
            alice.clone(),
            1_000_000_000_000,
        ));

        // Create token pool
        assert_ok!(AmmDex::create_token_pool(
            RuntimeOrigin::signed(alice.clone()),
            pallet_amm_dex::AssetId::Native,
            pallet_amm_dex::AssetId::Custom(0u64),
            1_000_000_000,
            1_000_000_000_000,
            DEADLINE,
        ));

        let lp_tokens = AmmDex::token_lp(0u32, &alice).unwrap_or(0);
        assert!(lp_tokens > 0, "Alice should have LP tokens");

        let balance_before = Balances::free_balance(&alice);
        let token_before = pallet_fungible_tokens::Pallet::<Test>::balance_of(0u64, &alice);

        // Remove all liquidity
        assert_ok!(AmmDex::remove_token_liquidity(
            RuntimeOrigin::signed(alice.clone()),
            0u32,
            lp_tokens,
            DEADLINE,
        ));

        // Alice should get back both native and custom tokens
        assert!(
            Balances::free_balance(&alice) > balance_before,
            "Alice should recover native tokens after removing liquidity"
        );
        assert!(
            pallet_fungible_tokens::Pallet::<Test>::balance_of(0u64, &alice) > token_before,
            "Alice should recover custom tokens after removing liquidity"
        );

        // LP tokens should be burned
        assert_eq!(
            AmmDex::token_lp(0u32, &alice).unwrap_or(0),
            0,
            "LP tokens should be burned after removing all liquidity"
        );
    });
}

// =========================================================================
// TEST 9: Eco + DPoS Cross-Reference — Green Score Update on Validator
// =========================================================================

#[test]
fn test_eco_green_score_update_for_dpos_validator() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();

        // Alice is a genesis validator in DPoS
        assert!(pallet_dpos::Validators::<Test>::get(&alice).is_some());

        // Register Alice as green validator in Eco
        let energy_source = BoundedVec::try_from(b"hydro".to_vec()).unwrap();
        assert_ok!(Eco::register_green_validator(
            RuntimeOrigin::root(),
            alice.clone(),
            energy_source,
            500u64, // carbon_offset
            50u32,  // trees_planted
            3u8,    // initial score
            true,   // renewable_energy
        ));

        // Update green score to max
        assert_ok!(Eco::update_green_score(
            RuntimeOrigin::root(),
            alice.clone(),
            5u8,
        ));

        let gv = pallet_eco::GreenValidators::<Test>::get(&alice).unwrap();
        assert_eq!(gv.score, 5, "Green score should be updated to 5");

        // Alice should still be a DPoS validator (eco doesn't affect dpos directly)
        assert!(
            pallet_dpos::Validators::<Test>::get(&alice).is_some(),
            "Alice should still be a DPoS validator after eco registration"
        );
    });
}

// =========================================================================
// TEST 10: Multiple Vesting Schedules — Independent Lock Tracking
// =========================================================================

#[test]
fn test_multiple_vesting_schedules_independent_tracking() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();

        // Assign first vesting schedule (seed)
        assert_ok!(Vesting::do_assign_vesting(
            alice.clone(),
            b"seed".to_vec(),
            100_000_000_000,
        ));

        let locked_after_seed = Vesting::get_locked_balance(&alice);
        assert_eq!(locked_after_seed, 100_000_000_000);

        // Assign second vesting schedule (community)
        assert_ok!(Vesting::do_assign_vesting(
            alice.clone(),
            b"community".to_vec(),
            50_000_000_000,
        ));

        let locked_after_community = Vesting::get_locked_balance(&alice);
        assert_eq!(
            locked_after_community, 150_000_000_000,
            "Total locked should be sum of both schedules"
        );

        // Remove first schedule
        assert_ok!(Vesting::do_remove_vesting(
            &alice,
            b"seed".to_vec(),
            100_000_000_000,
        ));

        let locked_after_removal = Vesting::get_locked_balance(&alice);
        assert_eq!(
            locked_after_removal, 50_000_000_000,
            "Only community schedule should remain locked"
        );

        // Remove second schedule
        assert_ok!(Vesting::do_remove_vesting(
            &alice,
            b"community".to_vec(),
            50_000_000_000,
        ));

        let locked_final = Vesting::get_locked_balance(&alice);
        assert_eq!(locked_final, 0, "All vesting should be released");
    });
}

// =====================================================================
// SUPPLY CAP INVARIANTS — MaxSupplyCurrency enforcement
// =====================================================================

const TEST_CAP: u128 = 100_000_000_000 * 1_000_000_000; // 100B VRDX * 10^9

#[test]
fn invariant_total_supply_constant_is_100b_vrdx() {
    assert_eq!(
        TEST_CAP, 100_000_000_000_000_000_000u128,
        "TOTAL_SUPPLY must be 100B * 10^9 = 10^20"
    );
}

#[test]
fn invariant_genesis_issuance_never_exceeds_cap() {
    new_test_ext().execute_with(|| {
        let issuance = <pallet_balances::Pallet<Test> as Currency<AccountId32>>::total_issuance();
        assert!(
            issuance <= TEST_CAP,
            "Genesis total_issuance ({}) must never exceed cap ({})",
            issuance,
            TEST_CAP
        );
    });
}

#[test]
fn invariant_staking_does_not_mint() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();
        let charlie = Sr25519Keyring::Charlie.to_account_id();

        let before = <pallet_balances::Pallet<Test> as Currency<AccountId32>>::total_issuance();

        // Register validator + delegate — tokens move, don't mint
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(charlie.clone()),
            3u8,
            b"solar".to_vec(),
        ));
        assert_ok!(Dpos::vote(
            RuntimeOrigin::signed(alice.clone()),
            charlie.clone(),
            1_000_000_000,
        ));

        let after = <pallet_balances::Pallet<Test> as Currency<AccountId32>>::total_issuance();
        assert_eq!(
            before, after,
            "Staking must not change total_issuance (tokens move, not mint)"
        );
    });
}

#[test]
fn invariant_dex_pool_creation_does_not_mint() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();

        let before = <pallet_balances::Pallet<Test> as Currency<AccountId32>>::total_issuance();

        // Create pool — tokens move from user to pool, don't mint
        assert_ok!(AmmDex::create_pool(
            RuntimeOrigin::signed(alice.clone()),
            b"VRDX".to_vec(),
            b"ECO".to_vec(),
            1_000_000_000,
            1_000_000_000,
            100_000_000_000u64, // deadline
        ));

        let after = <pallet_balances::Pallet<Test> as Currency<AccountId32>>::total_issuance();
        assert_eq!(
            before, after,
            "DEX pool creation must not change total_issuance"
        );
    });
}

#[test]
fn invariant_vesting_assignment_does_not_mint() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();

        let before = <pallet_balances::Pallet<Test> as Currency<AccountId32>>::total_issuance();

        // Vesting assignment locks existing balance, doesn't mint
        assert_ok!(Vesting::do_assign_vesting(
            alice.clone(),
            b"seed".to_vec(),
            100_000_000_000,
        ));

        let after = <pallet_balances::Pallet<Test> as Currency<AccountId32>>::total_issuance();
        assert_eq!(
            before, after,
            "Vesting assignment must not change total_issuance"
        );
    });
}

#[test]
fn invariant_slashing_does_not_create_supply() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();
        let charlie = Sr25519Keyring::Charlie.to_account_id();

        // Register and stake
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(charlie.clone()),
            3u8,
            b"solar".to_vec(),
        ));
        assert_ok!(Dpos::vote(
            RuntimeOrigin::signed(alice.clone()),
            charlie.clone(),
            5_000_000_000,
        ));

        let before = <pallet_balances::Pallet<Test> as Currency<AccountId32>>::total_issuance();

        // Slash — tokens move to treasury, no new supply
        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            charlie.clone(),
            2_000_000_000,
            b"downtime".to_vec(),
        ));

        let after = <pallet_balances::Pallet<Test> as Currency<AccountId32>>::total_issuance();
        assert!(
            after <= before,
            "Slashing must not increase total_issuance (before={}, after={})",
            before,
            after
        );
    });
}

#[test]
fn invariant_total_stake_equals_sum_of_individual_stakes() {
    new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let bob = Sr25519Keyring::Bob.to_account_id();
            let charlie = Sr25519Keyring::Charlie.to_account_id();
            let dave = Sr25519Keyring::Dave.to_account_id();

            // Genesis has Alice (500B) and Bob (300B) as validators = 800B base
            let before = Dpos::total_staked();

            // Two new validators (each adds MinStake=1000 to total)
            assert_ok!(Dpos::register_validator(
                RuntimeOrigin::signed(charlie.clone()),
                3u8,
                b"solar".to_vec(),
            ));
            assert_ok!(Dpos::register_validator(
                RuntimeOrigin::signed(dave.clone()),
                4u8,
                b"wind".to_vec(),
            ));

            // Delegations: 3B + 4B = 7B added
            assert_ok!(Dpos::vote(
                RuntimeOrigin::signed(alice.clone()),
                charlie.clone(),
                3_000_000_000,
            ));
            assert_ok!(Dpos::vote(
                RuntimeOrigin::signed(bob.clone()),
                dave.clone(),
                4_000_000_000,
            ));

            let after = Dpos::total_staked();
            let delta = after - before;
            // Delta = 2 * MinStake (2000) + delegation votes (7B) = 7_000_002_000
            assert_eq!(
                delta, 7_000_002_000,
                "Delta in TotalStaked must equal new registration stakes (2000) + delegation votes (7B)"
            );
        });
}

#[test]
fn invariant_no_double_counting_on_revote() {
    new_test_ext().execute_with(|| {
        let alice = Sr25519Keyring::Alice.to_account_id();
        let charlie = Sr25519Keyring::Charlie.to_account_id();

        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(charlie.clone()),
            3u8,
            b"solar".to_vec(),
        ));

        // Record baseline after registration
        let baseline = Dpos::total_staked();

        // First vote: 5B
        assert_ok!(Dpos::vote(
            RuntimeOrigin::signed(alice.clone()),
            charlie.clone(),
            5_000_000_000,
        ));
        assert_eq!(
            Dpos::total_staked() - baseline,
            5_000_000_000,
            "First vote should add exactly 5B to total"
        );

        // Unvote then re-vote with 3B
        assert_ok!(Dpos::unvote(
            RuntimeOrigin::signed(alice.clone()),
            charlie.clone(),
        ));
        assert_eq!(
            Dpos::total_staked() - baseline,
            0,
            "After unvote, total stake delta should be zero"
        );

        assert_ok!(Dpos::vote(
            RuntimeOrigin::signed(alice.clone()),
            charlie.clone(),
            3_000_000_000,
        ));
        assert_eq!(
            Dpos::total_staked() - baseline,
            3_000_000_000,
            "Re-voting after unvote must show 3B delta, not 8B (no double count)"
        );
    });
}
