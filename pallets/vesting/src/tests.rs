#![allow(clippy::let_unit_value)]
use crate::{self as pallet_vesting, *};
use frame_support::{
    assert_noop, assert_ok, construct_runtime, parameter_types,
    traits::{ConstU32, ConstU64, Everything},
    PalletId,
};
use sp_core::H256;
use sp_runtime::{
    traits::{BlakeTwo256, IdentityLookup},
    BuildStorage, DispatchError,
};

type Block = frame_system::mocking::MockBlock<Test>;

construct_runtime!(
    pub enum Test {
        System: frame_system,
        Balances: pallet_balances,
        Vesting: pallet_vesting,
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

parameter_types! {
    pub const VestingPalletId: PalletId = PalletId(*b"v/vestng");
}

impl pallet_vesting::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type Currency = Balances;
    type PalletId = VestingPalletId;
    type WeightInfo = pallet_vesting::SubstrateWeight<Test>;
}

pub fn new_test_ext() -> sp_io::TestExternalities {
    let mut t = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();

    pallet_balances::GenesisConfig::<Test> {
        balances: vec![(1, 10_000), (2, 20_000), (3, 50_000)],
        dev_accounts: None,
    }
    .assimilate_storage(&mut t)
    .unwrap();

    pallet_vesting::GenesisConfig::<Test> {
        vesting_schedules: vec![
            (b"ido_30".to_vec(), 1_000, 30, 0), // 30 days vesting, 0 day cliff
            (b"team_cliff".to_vec(), 10_000, 60, 10), // 60 days vesting, 10 day cliff
        ],
    }
    .assimilate_storage(&mut t)
    .unwrap();

    let mut ext = sp_io::TestExternalities::new(t);
    ext.execute_with(|| System::set_block_number(1));
    ext
}

#[test]
fn assign_vesting_root_and_non_root() {
    new_test_ext().execute_with(|| {
        let user = 1;

        // Non-root fails
        assert_noop!(
            Vesting::assign_vesting(RuntimeOrigin::signed(2), user, b"ido_30".to_vec(), 1_000),
            DispatchError::BadOrigin
        );

        // Schedule not found
        assert_noop!(
            Vesting::assign_vesting(
                RuntimeOrigin::root(),
                user,
                b"invalid_schedule".to_vec(),
                1_000
            ),
            Error::<Test>::ScheduleNotFound
        );

        // Root succeeds
        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            user,
            b"ido_30".to_vec(),
            1_000
        ));

        assert_eq!(Vesting::get_locked_balance(&user), 1_000);
        assert_eq!(Vesting::get_unlocked_balance(&user), 9_000); // 10_000 total free balance - 1_000 locked
    });
}

#[test]
fn release_vested_nothing_before_cliff() {
    new_test_ext().execute_with(|| {
        let user = 1;

        // Assign team schedule with 10 day cliff
        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            user,
            b"team_cliff".to_vec(),
            5_000
        ));

        // Block 1 is < 10 days (172800 blocks)
        System::set_block_number(100);

        // Before cliff -> Nothing to release
        assert_noop!(
            Vesting::release_vested(RuntimeOrigin::signed(user)),
            Error::<Test>::NothingToRelease
        );
    });
}

#[test]
fn release_vested_success_after_cliff_and_full() {
    new_test_ext().execute_with(|| {
        let user = 1;

        // Assign schedule with 0 cliff, 30 days (518400 blocks)
        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            user,
            b"ido_30".to_vec(),
            3_000
        ));

        assert_eq!(Vesting::get_locked_balance(&user), 3_000);

        // Fast forward 15 days = 15 * 17280 = 259200 blocks
        System::set_block_number(1 + 259_200);

        // Partial release (half vested)
        assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(user)));
        // Half of 3,000 = 1,500 vested and released
        assert_eq!(Vesting::get_locked_balance(&user), 1_500);

        // Fast forward past 30 days = 30 * 17280 = 518400 blocks
        System::set_block_number(1 + 518_400);

        assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(user)));
        assert_eq!(Vesting::get_locked_balance(&user), 0);
        assert_eq!(Vesting::get_unlocked_balance(&user), 10_000);
    });
}

#[test]
fn release_vested_no_vesting_for_account() {
    new_test_ext().execute_with(|| {
        // User 2 has no vesting entry
        assert_noop!(
            Vesting::release_vested(RuntimeOrigin::signed(2)),
            Error::<Test>::NoVestingForAccount
        );
    });
}

#[test]
fn check_transfer_and_before_transfer() {
    new_test_ext().execute_with(|| {
        let user = 1; // total balance 10,000

        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            user,
            b"ido_30".to_vec(),
            8_000
        ));

        // Free = 10,000 - 8,000 = 2,000

        // Trying to transfer 3,000 exceeds unlocked balance (2,000)
        assert_noop!(
            Vesting::check_transfer(RuntimeOrigin::signed(user), user, 3_000),
            Error::<Test>::TransferLocked
        );

        assert_noop!(
            Vesting::before_transfer(&user, 3_000),
            Error::<Test>::TransferLocked
        );

        // Transfer 2,000 is allowed
        assert_ok!(Vesting::check_transfer(
            RuntimeOrigin::signed(user),
            user,
            2_000
        ));
        assert_ok!(Vesting::before_transfer(&user, 2_000));
    });
}

#[test]
fn get_locked_and_unlocked_balances() {
    new_test_ext().execute_with(|| {
        let user = 2; // balance 20,000

        assert_eq!(Vesting::get_locked_balance(&user), 0);
        assert_eq!(Vesting::get_unlocked_balance(&user), 20_000);

        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            user,
            b"team_cliff".to_vec(),
            5_000
        ));

        assert_eq!(Vesting::get_locked_balance(&user), 5_000);
        assert_eq!(Vesting::get_unlocked_balance(&user), 15_000);
    });
}

#[test]
fn multiple_vesting_schedules() {
    new_test_ext().execute_with(|| {
        let user = 3; // balance 50,000

        // Assign schedule 1: ido_30 (amount 2,000, 30 days, 0 cliff)
        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            user,
            b"ido_30".to_vec(),
            2_000
        ));

        // Assign schedule 2: team_cliff (amount 10,000, 60 days, 10 day cliff)
        assert_ok!(Vesting::assign_vesting(
            RuntimeOrigin::root(),
            user,
            b"team_cliff".to_vec(),
            10_000
        ));

        // Total locked = 2,000 + 10,000 = 12,000
        assert_eq!(Vesting::get_locked_balance(&user), 12_000);
        assert_eq!(Vesting::get_unlocked_balance(&user), 38_000);

        // Fast forward 15 days (259,200 blocks)
        // ido_30: 15/30 = half vested = 1,000
        // team_cliff: 15 days elapsed >= 10 day cliff. 15/60 = 1/4 vested = 2,500
        // Total vested = 1,000 + 2,500 = 3,500
        System::set_block_number(1 + 259_200);

        assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(user)));

        // Locked balance decreased by 3,500 -> 12,000 - 3,500 = 8,500
        assert_eq!(Vesting::get_locked_balance(&user), 8_500);
        assert_eq!(Vesting::get_unlocked_balance(&user), 41_500);
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

    const PALLET_NAME: &str = "vesting";

    #[test]
    #[ignore]
    fn real_bench() {
        new_test_ext().execute_with(|| {{
            use frame_system::Pallet as System;
            System::<Test>::set_block_number(1);
            
            let mut results: Vec<(&str, u64)> = Vec::new();

            // Benchmark: assign_vesting (root only)
            let mut idx = 10u64;
            let w = measure_bench("assign_vesting", 50, || {
                idx += 1;
                Vesting::assign_vesting(RuntimeOrigin::root(), idx, b"ido_30".to_vec(), 1_000).is_ok()
            });
            results.push(("assign_vesting", w));

            // Benchmark: release_vested (needs time to pass)
            assert_ok!(Vesting::assign_vesting(RuntimeOrigin::root(), 1, b"ido_30".to_vec(), 1_000));
            // Advance block number to simulate time passing
            System::<Test>::set_block_number(1000);
            let w = measure_bench("release_vested", 50, || {
                Vesting::release_vested(RuntimeOrigin::signed(1)).is_ok()
            });
            results.push(("release_vested", w));

            println!("\n//! WeightInfo for pallet-vesting (real benchmark)");
            println!("pub struct WeightInfo;");
            for (name, weight) in &results {
                println!("// {}: {} weight units", name, weight);
            }

        }});
    }
}
