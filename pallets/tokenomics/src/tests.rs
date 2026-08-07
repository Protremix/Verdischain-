#![allow(clippy::let_unit_value)]
use crate::{self as pallet_tokenomics, *};
use frame_support::{
    assert_noop, assert_ok, construct_runtime, parameter_types,
    traits::{ConstU32, ConstU64, Everything},
    PalletId,
};
use sp_core::H256;
use sp_runtime::{
    traits::{AccountIdConversion, BlakeTwo256, IdentityLookup},
    BuildStorage, DispatchError,
};

type Block = frame_system::mocking::MockBlock<Test>;

construct_runtime!(
    pub enum Test {
        System: frame_system,
        Balances: pallet_balances,
        Tokenomics: pallet_tokenomics,
    }
);

parameter_types! {
    pub const BlockHashCount: u64 = 250;
}

impl frame_system::Config for Test {
    type BaseCallFilter = Everything;
    type BlockWeights = ();
    type BlockLength = ();
    type DbWeight = ();
    type RuntimeOrigin = RuntimeOrigin;
    type RuntimeCall = RuntimeCall;
    type Nonce = u64;
    type Hash = H256;
    type Hashing = BlakeTwo256;
    type AccountId = u64;
    type Lookup = IdentityLookup<Self::AccountId>;
    type Block = Block;
    type RuntimeEvent = RuntimeEvent;
    type BlockHashCount = BlockHashCount;
    type Version = ();
    type PalletInfo = PalletInfo;
    type AccountData = pallet_balances::AccountData<u64>;
    type OnNewAccount = ();
    type OnKilledAccount = ();
    type SystemWeightInfo = ();
    type SS58Prefix = ();
    type OnSetCode = ();
    type MaxConsumers = ConstU32<16>;
    type RuntimeTask = ();
    type ExtensionsWeightInfo = ();
    type SingleBlockMigrations = ();
    type MultiBlockMigrator = ();
    type PreInherents = ();
    type PostInherents = ();
    type PostTransactions = ();
}

impl pallet_balances::Config for Test {
    type MaxLocks = ConstU32<50>;
    type MaxReserves = ConstU32<50>;
    type ReserveIdentifier = [u8; 8];
    type Balance = u64;
    type RuntimeEvent = RuntimeEvent;
    type DustRemoval = ();
    type ExistentialDeposit = ConstU64<1>;
    type AccountStore = System;
    type WeightInfo = ();
    type FreezeIdentifier = ();
    type MaxFreezes = ConstU32<0>;
    type RuntimeHoldReason = ();
    type RuntimeFreezeReason = ();
    type DoneSlashHandler = ();
}

const UNITS: u64 = 1_000;
const TOTAL_SUPPLY_VAL: u64 = 100_000_000_000 * UNITS;
const INVESTOR_ALLOCATION_VAL: u64 = 12_000_000_000 * UNITS;

parameter_types! {
    pub const TotalSupplyConst: u64 = TOTAL_SUPPLY_VAL;
    pub const InvestorAllocationConst: u64 = INVESTOR_ALLOCATION_VAL;
    pub const TokenomicsPalletId: PalletId = PalletId(*b"v/toknom");
}

impl pallet_tokenomics::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type Currency = Balances;
    type TotalSupply = TotalSupplyConst;
    type InvestorAllocation = InvestorAllocationConst;
    type PalletId = TokenomicsPalletId;
    type WeightInfo = pallet_tokenomics::SubstrateWeight<Test>;
}

pub fn treasury_account() -> u64 {
    TokenomicsPalletId::get().into_account_truncating()
}

pub fn new_test_ext() -> sp_io::TestExternalities {
    let mut t = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();

    let treasury = treasury_account();

    pallet_balances::GenesisConfig::<Test> {
        balances: vec![
            (1, 100_000),
            (2, 100_000),
            (treasury, 50_000_000_000 * UNITS),
        ],
        dev_accounts: None,
    }
    .assimilate_storage(&mut t)
    .unwrap();

    pallet_tokenomics::GenesisConfig::<Test> {
        total_supply: TOTAL_SUPPLY_VAL,
        max_supply: TOTAL_SUPPLY_VAL,
        circulating_supply: 0,
        investor_allocation: INVESTOR_ALLOCATION_VAL,
        distribution: vec![
            (b"Community".to_vec(), 35_000_000_000 * UNITS, 35, 365, 30),
            (b"Investors".to_vec(), INVESTOR_ALLOCATION_VAL, 12, 180, 14),
        ],
        presale_price: 5, // 5 bps = $0.0005
    }
    .assimilate_storage(&mut t)
    .unwrap();

    let mut ext = sp_io::TestExternalities::new(t);
    ext.execute_with(|| System::set_block_number(1));
    ext
}

#[test]
fn give_consent_works() {
    new_test_ext().execute_with(|| {
        assert_eq!(ConsentGiven::<Test>::get(1), None);
        assert_ok!(Tokenomics::give_consent(RuntimeOrigin::signed(1)));
        assert_eq!(ConsentGiven::<Test>::get(1), Some(true));

        // Already consented error
        assert_noop!(
            Tokenomics::give_consent(RuntimeOrigin::signed(1)),
            Error::<Test>::AlreadyConsented
        );
    });
}

#[test]
fn purchase_consent_required() {
    new_test_ext().execute_with(|| {
        // Without consent -> fails
        assert_noop!(
            Tokenomics::purchase(RuntimeOrigin::signed(1), 1000 * UNITS),
            Error::<Test>::ConsentRequired
        );
    });
}

#[test]
fn purchase_success() {
    new_test_ext().execute_with(|| {
        assert_ok!(Tokenomics::give_consent(RuntimeOrigin::signed(1)));

        let amount = 1_000_000 * UNITS;
        let expected_cost = amount * 5 / 10_000; // price_bps = 5

        let initial_balance = Balances::free_balance(1);
        let initial_treasury = Balances::free_balance(treasury_account());

        assert_ok!(Tokenomics::purchase(RuntimeOrigin::signed(1), amount));

        assert_eq!(Balances::free_balance(1), initial_balance + amount);
        assert_eq!(
            Balances::free_balance(treasury_account()),
            initial_treasury - amount
        );

        assert_eq!(PresaleSold::<Test>::get(), amount);
        assert_eq!(PresaleRaised::<Test>::get(), expected_cost);
        assert_eq!(CirculatingSupply::<Test>::get(), amount);
    });
}

#[test]
fn purchase_insufficient_treasury_funds() {
    new_test_ext().execute_with(|| {
        assert_ok!(Tokenomics::give_consent(RuntimeOrigin::signed(1)));

        // Try purchasing more than treasury balance (50B * UNITS)
        let too_much = 60_000_000_000 * UNITS;
        assert!(Tokenomics::purchase(RuntimeOrigin::signed(1), too_much).is_err());
    });
}

#[test]
fn purchase_investor_allocation_cap() {
    new_test_ext().execute_with(|| {
        assert_ok!(Tokenomics::give_consent(RuntimeOrigin::signed(1)));

        let too_much = INVESTOR_ALLOCATION_VAL + 1;
        assert_noop!(
            Tokenomics::purchase(RuntimeOrigin::signed(1), too_much),
            Error::<Test>::MaxInvestorAllocationReached
        );
    });
}

#[test]
fn update_presale_price_root_and_non_root() {
    new_test_ext().execute_with(|| {
        // Non-root fails
        assert_noop!(
            Tokenomics::update_presale_price(RuntimeOrigin::signed(1), 10),
            DispatchError::BadOrigin
        );

        // Root succeeds
        assert_ok!(Tokenomics::update_presale_price(RuntimeOrigin::root(), 10));
        assert_eq!(PresalePrice::<Test>::get(), 10);
    });
}

#[test]
fn release_distribution_works() {
    new_test_ext().execute_with(|| {
        let cat_name = b"Community".to_vec();
        let release_amt = 1_000_000 * UNITS;

        // Non-root fails
        assert_noop!(
            Tokenomics::release_distribution(
                RuntimeOrigin::signed(1),
                cat_name.clone(),
                release_amt
            ),
            DispatchError::BadOrigin
        );

        // Invalid category fails
        assert_noop!(
            Tokenomics::release_distribution(
                RuntimeOrigin::root(),
                b"NonExistent".to_vec(),
                release_amt
            ),
            Error::<Test>::InvalidCategory
        );

        // Root succeeds
        assert_ok!(Tokenomics::release_distribution(
            RuntimeOrigin::root(),
            cat_name.clone(),
            release_amt
        ));

        let cat_bv: BoundedVec<u8, ConstU32<32>> = cat_name.clone().try_into().unwrap();
        let cat = Distribution::<Test>::get(&cat_bv).unwrap();
        assert_eq!(cat.released, release_amt);
        assert_eq!(CirculatingSupply::<Test>::get(), release_amt);

        // Exceeding distribution capacity fails
        let exceed_amt = 35_000_000_000 * UNITS;
        assert_noop!(
            Tokenomics::release_distribution(RuntimeOrigin::root(), cat_name, exceed_amt),
            Error::<Test>::DistributionComplete
        );
    });
}

#[test]
fn total_supply_and_investor_allocation_constants() {
    new_test_ext().execute_with(|| {
        assert_eq!(TotalSupply::<Test>::get(), TOTAL_SUPPLY_VAL);
        assert_eq!(
            <Test as Config>::InvestorAllocation::get(),
            INVESTOR_ALLOCATION_VAL
        );
    });
}


// ==================== REAL BENCHMARK WEIGHT GENERATION ====================
#[cfg(feature = "runtime-benchmarks")]
mod real_bench {
    use super::*;
    use super::{Test, new_test_ext};
    use std::time::Instant;
    use frame_support::traits::fungible::Mutate;

    fn measure_bench<F: FnMut() -> bool>(name: &str, iters: u32, mut f: F) -> u64 {
        let mut times: Vec<u64> = Vec::new();
        for _ in 0..iters {
            let start = Instant::now();
            let ok = f();
            let elapsed = start.elapsed().as_nanos() as u64;
            if ok { times.push(elapsed); }
        }
        if times.is_empty() {
            println!("  {pallet}::{name} -> FAILED", pallet = PALLET_NAME, name = name);
            return 10_000;
        }
        let avg = times.iter().sum::<u64>() / times.len() as u64;
        let max = *times.iter().max().unwrap();
        let weight = (avg as f64 * 1.25).max(10000.0) as u64;
        println!("  {pallet}::{name} -> avg={avg}ns max={max}ns weight={weight}", pallet = PALLET_NAME, name = name, avg = avg, max = max, weight = weight);
        weight
    }

    const PALLET_NAME: &str = "tokenomics";

    #[test]
    #[ignore]
    fn real_bench() {
        new_test_ext().execute_with(|| {{
            use frame_system::Pallet as System;
            System::<Test>::set_block_number(1);
            
            use crate::tests::UNITS;
            let mut results: Vec<(&str, u64)> = Vec::new();

            // Benchmark: give_consent
            let mut idx = 10u64;
            let w = measure_bench("give_consent", 50, || {
                idx += 1;
                <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&idx, 100_000);
                Tokenomics::give_consent(RuntimeOrigin::signed(idx)).is_ok()
            });
            results.push(("give_consent", w));

            // Benchmark: purchase (needs consent first)
            <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&5, 100_000);
            assert_ok!(Tokenomics::give_consent(RuntimeOrigin::signed(5)));
            let w = measure_bench("purchase", 50, || {
                <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&5, 100_000);
                Tokenomics::purchase(RuntimeOrigin::signed(5), 100).is_ok()
            });
            results.push(("purchase", w));

            // Benchmark: release_distribution (root only)
            let w = measure_bench("release_distribution", 50, || {
                Tokenomics::release_distribution(RuntimeOrigin::root(), b"team".to_vec(), 1000).is_ok()
            });
            results.push(("release_distribution", w));

            println!("\n//! WeightInfo for pallet-tokenomics (real benchmark)");
            println!("pub struct WeightInfo;");
            for (name, weight) in &results {
                println!("// {}: {} weight units", name, weight);
            }

        }});
    }
}
