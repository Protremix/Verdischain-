#![allow(clippy::let_unit_value)]
use crate::{self as pallet_dpos, *};
use frame_support::{
    assert_noop, assert_ok, construct_runtime, parameter_types,
    traits::{ConstU32, ConstU64},
    BoundedVec, PalletId,
};
use frame_system::EnsureRoot;
use sp_core::H256;
use sp_runtime::{
    traits::{BlakeTwo256, IdentityLookup},
    BuildStorage, DispatchError,
};

type Block = frame_system::mocking::MockBlock<Test>;

pub const UNITS: u64 = 1_000_000_000_000;

construct_runtime!(
    pub enum Test {
        System: frame_system,
        Balances: pallet_balances,
        Dpos: pallet_dpos,
    }
);

parameter_types! {
    pub const BlockHashCount: u64 = 250;
    pub const SS58Prefix: u16 = 42;
}

impl frame_system::Config for Test {
    type BaseCallFilter = frame_support::traits::Everything;
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
    type SS58Prefix = SS58Prefix;
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
    type MaxFreezes = ();
    type RuntimeHoldReason = ();
    type RuntimeFreezeReason = ();
    type DoneSlashHandler = ();
}

parameter_types! {
    pub const BlockReward: u64 = 16 * UNITS;
    pub const MinStake: u64 = 10_000 * UNITS;
    pub const MaxValidators: u32 = 101;
    pub const ActiveValidatorCount: u32 = 21;
    pub const EpochLength: u32 = 100;
    pub const DposPalletId: PalletId = PalletId(*b"ver/dpos");
}

impl pallet_dpos::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type Currency = Balances;
    type BlockReward = BlockReward;
    type MinStake = MinStake;
    type MaxValidators = MaxValidators;
    type ActiveValidatorCount = ActiveValidatorCount;
    type EpochLength = EpochLength;
    type PalletId = DposPalletId;
    type WeightInfo = pallet_dpos::SubstrateWeight<Test>;
}

pub fn new_test_ext() -> sp_io::TestExternalities {
    let mut t = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();

    pallet_balances::GenesisConfig::<Test> {
        balances: vec![
            (1, 100_000 * UNITS),
            (2, 100_000 * UNITS),
            (3, 100_000 * UNITS),
            (4, 100_000 * UNITS),
            (5, 5_000 * UNITS),
        ],
        dev_accounts: None,
    }
    .assimilate_storage(&mut t)
    .unwrap();

    let mut ext = sp_io::TestExternalities::new(t);
    ext.execute_with(|| System::set_block_number(1));
    ext
}

// === register_validator tests ===

#[test]
fn register_validator_success() {
    new_test_ext().execute_with(|| {
        let green_score = 85;
        let energy_source = b"Solar".to_vec();

        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(1),
            green_score,
            energy_source.clone()
        ));

        let val = Validators::<Test>::get(1).expect("Validator should exist");
        assert_eq!(val.address, 1);
        assert_eq!(val.stake, MinStake::get());
        assert_eq!(val.total_votes, MinStake::get());
        assert_eq!(val.blocks_produced, 0);
        assert_eq!(val.rewards_earned, 0);
        assert!(val.active);
        assert!(!val.slashed);
        assert_eq!(val.green_score, green_score);
        assert_eq!(val.energy_source.to_vec(), energy_source);

        assert!(ValidatorList::<Test>::get().contains(&1));
        assert_eq!(TotalStaked::<Test>::get(), MinStake::get());
        assert_eq!(Balances::reserved_balance(1), MinStake::get());

        System::assert_has_event(RuntimeEvent::Dpos(Event::ValidatorRegistered {
            who: 1,
            stake: MinStake::get(),
        }));
    });
}

#[test]
fn register_validator_fails_already_registered() {
    new_test_ext().execute_with(|| {
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(1),
            80,
            b"Wind".to_vec()
        ));

        assert_noop!(
            Dpos::register_validator(RuntimeOrigin::signed(1), 80, b"Wind".to_vec()),
            Error::<Test>::ValidatorAlreadyRegistered
        );
    });
}

#[test]
fn register_validator_fails_insufficient_funds() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Dpos::register_validator(RuntimeOrigin::signed(5), 80, b"Solar".to_vec()),
            Error::<Test>::InsufficientFunds
        );
    });
}

#[test]
fn register_validator_fails_max_validators_reached() {
    new_test_ext().execute_with(|| {
        let mut list = BoundedVec::<u64, ConstU32<101>>::default();
        for i in 1000..1201 {
            if list.try_push(i as u64).is_err() {
                break;
            }
        }
        assert_eq!(list.len(), 101);
        ValidatorList::<Test>::put(list);

        assert_noop!(
            Dpos::register_validator(RuntimeOrigin::signed(1), 80, b"Solar".to_vec()),
            Error::<Test>::MaxValidatorsReached
        );
    });
}

// === unregister_validator tests ===

#[test]
fn unregister_validator_success() {
    new_test_ext().execute_with(|| {
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(1),
            80,
            b"Hydro".to_vec()
        ));
        assert_eq!(TotalStaked::<Test>::get(), MinStake::get());
        assert_eq!(Balances::reserved_balance(1), MinStake::get());

        assert_ok!(Dpos::unregister_validator(RuntimeOrigin::signed(1)));

        assert!(Validators::<Test>::get(1).is_none());
        assert!(!ValidatorList::<Test>::get().contains(&1));
        assert!(!ActiveValidators::<Test>::get().contains(&1));
        assert_eq!(TotalStaked::<Test>::get(), 0);
        assert_eq!(Balances::reserved_balance(1), 0);

        System::assert_has_event(RuntimeEvent::Dpos(Event::ValidatorUnregistered { who: 1 }));
    });
}

#[test]
fn unregister_validator_fails_not_found() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Dpos::unregister_validator(RuntimeOrigin::signed(1)),
            Error::<Test>::ValidatorNotFound
        );
    });
}

#[test]
fn unregister_validator_fails_not_active() {
    new_test_ext().execute_with(|| {
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(1),
            80,
            b"Geothermal".to_vec()
        ));

        Validators::<Test>::mutate(1, |v| {
            if let Some(ref mut val) = v {
                val.active = false;
            }
        });

        assert_noop!(
            Dpos::unregister_validator(RuntimeOrigin::signed(1)),
            Error::<Test>::NotActiveValidator
        );
    });
}

// === vote tests ===

#[test]
fn vote_success() {
    new_test_ext().execute_with(|| {
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(1),
            80,
            b"Solar".to_vec()
        ));

        let vote_amount = 5_000 * UNITS;
        assert_ok!(Dpos::vote(RuntimeOrigin::signed(2), 1, vote_amount));

        let votes = Votes::<Test>::get(2).expect("Votes should exist for account 2");
        assert_eq!(votes.len(), 1);
        assert_eq!(votes[0].voter, 2);
        assert_eq!(votes[0].validator, 1);
        assert_eq!(votes[0].amount, vote_amount);

        let val = Validators::<Test>::get(1).unwrap();
        assert_eq!(val.total_votes, MinStake::get() + vote_amount);

        assert_eq!(TotalStaked::<Test>::get(), MinStake::get() + vote_amount);
        assert_eq!(Balances::reserved_balance(2), vote_amount);

        System::assert_has_event(RuntimeEvent::Dpos(Event::Voted {
            voter: 2,
            validator: 1,
            amount: vote_amount,
        }));
    });
}

#[test]
fn vote_fails_validator_not_found() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Dpos::vote(RuntimeOrigin::signed(2), 99, 1_000 * UNITS),
            Error::<Test>::ValidatorNotFound
        );
    });
}

#[test]
fn vote_fails_insufficient_funds() {
    new_test_ext().execute_with(|| {
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(1),
            80,
            b"Solar".to_vec()
        ));

        assert_noop!(
            Dpos::vote(RuntimeOrigin::signed(5), 1, 10_000 * UNITS),
            Error::<Test>::InsufficientFunds
        );
    });
}

// === unvote tests ===

#[test]
fn unvote_success() {
    new_test_ext().execute_with(|| {
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(1),
            80,
            b"Solar".to_vec()
        ));

        let vote_amount = 2_000 * UNITS;
        assert_ok!(Dpos::vote(RuntimeOrigin::signed(2), 1, vote_amount));
        assert_eq!(Balances::reserved_balance(2), vote_amount);

        assert_ok!(Dpos::unvote(RuntimeOrigin::signed(2), 1));

        let votes = Votes::<Test>::get(2).unwrap_or_default();
        assert!(votes.is_empty());

        let val = Validators::<Test>::get(1).unwrap();
        assert_eq!(val.total_votes, MinStake::get());
        assert_eq!(TotalStaked::<Test>::get(), MinStake::get());
        assert_eq!(Balances::reserved_balance(2), 0);

        System::assert_has_event(RuntimeEvent::Dpos(Event::Unvoted {
            voter: 2,
            validator: 1,
        }));
    });
}

#[test]
fn unvote_fails_no_votes_for_validator() {
    new_test_ext().execute_with(|| {
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(1),
            80,
            b"Solar".to_vec()
        ));

        assert_noop!(
            Dpos::unvote(RuntimeOrigin::signed(2), 1),
            Error::<Test>::NoVotesForValidator
        );
    });
}

// === slash_validator tests ===

#[test]
fn slash_validator_success() {
    new_test_ext().execute_with(|| {
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(1),
            80,
            b"Solar".to_vec()
        ));

        let penalty = 2_000 * UNITS;
        let reason = b"Double signing".to_vec();

        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            1,
            penalty,
            reason.clone()
        ));

        let val = Validators::<Test>::get(1).unwrap();
        assert_eq!(val.stake, MinStake::get() - penalty);
        assert!(val.slashed);

        assert_eq!(SlashingEvents::<Test>::get(1), 1);
        assert_eq!(TotalStaked::<Test>::get(), MinStake::get() - penalty);

        System::assert_has_event(RuntimeEvent::Dpos(Event::ValidatorSlashed {
            who: 1,
            penalty,
            reason,
        }));
    });
}

#[test]
fn slash_validator_fails_not_root() {
    new_test_ext().execute_with(|| {
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(1),
            80,
            b"Solar".to_vec()
        ));

        assert_noop!(
            Dpos::slash_validator(
                RuntimeOrigin::signed(2),
                1,
                1_000 * UNITS,
                b"Slash".to_vec()
            ),
            DispatchError::BadOrigin
        );
    });
}

#[test]
fn slash_validator_fails_not_found() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Dpos::slash_validator(
                RuntimeOrigin::root(),
                99,
                1_000 * UNITS,
                b"Not found".to_vec()
            ),
            Error::<Test>::ValidatorNotFound
        );
    });
}

#[test]
fn slash_validator_fails_invalid_reason() {
    new_test_ext().execute_with(|| {
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(1),
            80,
            b"Solar".to_vec()
        ));

        assert_noop!(
            Dpos::slash_validator(RuntimeOrigin::root(), 1, 1_000 * UNITS, vec![]),
            Error::<Test>::InvalidSlashReason
        );
    });
}

// === update_green_score tests ===

#[test]
fn update_green_score_success() {
    new_test_ext().execute_with(|| {
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(1),
            80,
            b"Solar".to_vec()
        ));

        let new_score = 98;
        assert_ok!(Dpos::update_green_score(
            RuntimeOrigin::root(),
            1,
            new_score
        ));

        let val = Validators::<Test>::get(1).unwrap();
        assert_eq!(val.green_score, new_score);

        System::assert_has_event(RuntimeEvent::Dpos(Event::GreenScoreUpdated {
            validator: 1,
            score: new_score,
        }));
    });
}

#[test]
fn update_green_score_fails_not_validator() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Dpos::update_green_score(RuntimeOrigin::root(), 2, 90),
            Error::<Test>::NotValidator
        );
    });
}

// === reward_block_producer tests ===

#[test]
fn reward_block_producer_success() {
    new_test_ext().execute_with(|| {
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(1),
            80,
            b"Solar".to_vec()
        ));

        let initial_balance = Balances::free_balance(1);

        Dpos::reward_block_producer(&1, 10);

        let val = Validators::<Test>::get(1).unwrap();
        assert_eq!(val.blocks_produced, 1);
        assert_eq!(val.rewards_earned, BlockReward::get());

        assert_eq!(
            Balances::free_balance(1),
            initial_balance + BlockReward::get()
        );

        System::assert_has_event(RuntimeEvent::Dpos(Event::BlockReward {
            validator: 1,
            reward: BlockReward::get(),
            block: 10,
        }));
    });
}

#[test]
fn reward_block_producer_non_validator_ignored() {
    new_test_ext().execute_with(|| {
        let initial_balance = Balances::free_balance(99);

        Dpos::reward_block_producer(&99, 10);

        assert_eq!(Balances::free_balance(99), initial_balance);
        assert!(Validators::<Test>::get(99).is_none());
    });
}

// === total_staked tracking tests ===

#[test]
fn total_staked_tracking() {
    new_test_ext().execute_with(|| {
        assert_eq!(TotalStaked::<Test>::get(), 0);

        // 1. Register Validator 1
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(1),
            80,
            b"Solar".to_vec()
        ));
        assert_eq!(TotalStaked::<Test>::get(), MinStake::get());

        // 2. Register Validator 2
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(2),
            90,
            b"Wind".to_vec()
        ));
        assert_eq!(TotalStaked::<Test>::get(), 2 * MinStake::get());

        // 3. Account 3 votes for Validator 1
        let vote_amount = 3_000 * UNITS;
        assert_ok!(Dpos::vote(RuntimeOrigin::signed(3), 1, vote_amount));
        assert_eq!(
            TotalStaked::<Test>::get(),
            2 * MinStake::get() + vote_amount
        );

        // 4. Account 3 unvotes
        assert_ok!(Dpos::unvote(RuntimeOrigin::signed(3), 1));
        assert_eq!(TotalStaked::<Test>::get(), 2 * MinStake::get());

        // 5. Slash Validator 1
        let slash_amount = 4_000 * UNITS;
        assert_ok!(Dpos::slash_validator(
            RuntimeOrigin::root(),
            1,
            slash_amount,
            b"Misbehavior".to_vec()
        ));
        assert_eq!(
            TotalStaked::<Test>::get(),
            2 * MinStake::get() - slash_amount
        );

        // 6. Unregister Validator 2
        assert_ok!(Dpos::unregister_validator(RuntimeOrigin::signed(2)));
        assert_eq!(TotalStaked::<Test>::get(), MinStake::get() - slash_amount);
    });
}

// ==================== REAL BENCHMARK WEIGHT GENERATION ====================
// Run with: SKIP_WASM_BUILD=1 cargo test --features runtime-benchmarks -p pallet-dpos -- real_bench --nocapture --ignored

#[cfg(feature = "runtime-benchmarks")]
mod real_bench {
    use super::*;
    use super::{Dpos, RuntimeOrigin, Test, new_test_ext, UNITS};
    use std::time::Instant;
    use frame_support::traits::fungible::Mutate;
    use frame_support::assert_ok;
    use crate::*;

    fn measure_bench<F: FnMut() -> bool>(name: &str, iters: u32, mut f: F) -> u64 {
        let mut times: Vec<u64> = Vec::new();
        for _ in 0..iters {
            let start = Instant::now();
            let ok = f();
            let elapsed = start.elapsed().as_nanos() as u64;
            if ok { times.push(elapsed); }
        }
        if times.is_empty() {
            println!("  dpos::{} -> FAILED", name);
            return 10_000;
        }
        let avg = times.iter().sum::<u64>() / times.len() as u64;
        let max = *times.iter().max().unwrap();
        let weight = (avg as f64 * 1.25).max(10000.0) as u64;
        println!("  dpos::{} -> avg={}ns max={}ns weight={}", name, avg, max, weight);
        weight
    }

    #[test]
    #[ignore]
    fn real_bench_dpos() {
        new_test_ext().execute_with(|| {
            use frame_system::Pallet as System;
            System::<Test>::set_block_number(1);

            // Setup: fund accounts
            for i in 1u64..=300u64 {
                <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&i, 100_000 * UNITS);
            }

            let mut results: Vec<(&str, u64)> = Vec::new();

            // Benchmark: register_validator
            let mut idx = 100u64;
            let w = measure_bench("register_validator", 50, || {
                idx += 1;
                Dpos::register_validator(RuntimeOrigin::signed(idx), 80, b"Wind".to_vec()).is_ok()
            });
            results.push(("register_validator", w));

            // Register a validator for vote benchmark
            assert_ok!(Dpos::register_validator(RuntimeOrigin::signed(10), 80, b"Solar".to_vec()));

            // Benchmark: vote - use genesis-funded accounts (1-5 have 100k UNITS each)
            // Reset balances and re-fund for each iteration
            let mut vote_idx = 0u64;
            let w = measure_bench("vote", 50, || {
                vote_idx += 1;
                let voter = (vote_idx % 5) + 1;
                // Reset balance to ensure funds available
                <pallet_balances::Pallet<Test> as Mutate<u64>>::set_balance(&voter, 100_000 * UNITS);
                Dpos::vote(RuntimeOrigin::signed(voter), 10, 100 * UNITS).is_ok()
            });
            results.push(("vote", w));

            // Benchmark: update_green_score
            assert_ok!(Dpos::register_validator(RuntimeOrigin::signed(20), 85, b"Geothermal".to_vec()));
            let w = measure_bench("update_green_score", 50, || {
                Dpos::update_green_score(RuntimeOrigin::root(), 20, 95).is_ok()
            });
            results.push(("update_green_score", w));

            // Print weight file
            println!("\n//! WeightInfo for pallet-dpos (real benchmark)");
            println!("pub struct WeightInfo;");
            for (name, weight) in &results {
                println!("// {}: {} weight units", name, weight);
            }
        });
    }
}
