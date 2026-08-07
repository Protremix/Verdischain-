#![allow(clippy::let_unit_value)]
use crate::{self as pallet_eco, *};
use frame_support::{
    assert_noop, assert_ok, construct_runtime, derive_impl, parameter_types,
    traits::{ConstU16, ConstU32, ConstU64},
    BoundedVec, PalletId,
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
        Eco: pallet_eco,
    }
);

#[derive_impl(frame_system::config_preludes::TestDefaultConfig)]
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
    type BlockHashCount = ConstU64<250>;
    type Version = ();
    type PalletInfo = PalletInfo;
    type AccountData = ();
    type OnNewAccount = ();
    type OnKilledAccount = ();
    type SystemWeightInfo = ();
    type SS58Prefix = ConstU16<42>;
    type OnSetCode = ();
    type MaxConsumers = ConstU32<16>;
}

parameter_types! {
    pub const EcoPalletId: PalletId = PalletId(*b"ver/ecoo");
    pub const MaxCarbonCredits: u32 = 1000;
    pub const MaxReforestProjects: u32 = 500;
    pub const MaxGreenValidators: u32 = 101;
    pub const MinGreenScore: u8 = 0;
    pub const MaxGreenScore: u8 = 100;
}

impl pallet_eco::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type PalletId = EcoPalletId;
    type MaxCarbonCredits = MaxCarbonCredits;
    type MaxReforestProjects = MaxReforestProjects;
    type MaxGreenValidators = MaxGreenValidators;
    type MinGreenScore = MinGreenScore;
    type MaxGreenScore = MaxGreenScore;
    type WeightInfo = pallet_eco::SubstrateWeight<Test>;
}

pub fn new_test_ext() -> sp_io::TestExternalities {
    let t = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();
    let mut ext = sp_io::TestExternalities::new(t);
    ext.execute_with(|| System::set_block_number(1));
    ext
}

fn bv64(bytes: &[u8]) -> BoundedVec<u8, ConstU32<64>> {
    bytes.to_vec().try_into().unwrap()
}

// =========================================================================
// mint_carbon_credit tests
// =========================================================================

#[test]
fn mint_carbon_credit_success() {
    new_test_ext().execute_with(|| {
        let credit_id = b"credit-001".to_vec();
        let project_name = b"Project Amazon".to_vec();
        let tons = 100u64;

        assert_ok!(Eco::mint_carbon_credit(
            RuntimeOrigin::signed(1),
            credit_id.clone(),
            project_name.clone(),
            tons
        ));

        // Check storage
        let credit = Eco::carbon_credits(bv64(b"credit-001")).expect("Credit should exist");
        assert_eq!(credit.tons_co2, 100);
        assert_eq!(credit.verified, false);
        assert_eq!(credit.retired, false);
        assert_eq!(credit.owner, 1);

        // Check aggregate offset
        assert_eq!(Eco::total_co2_offset(), 100);

        // Check event deposit
        System::assert_has_event(
            Event::CarbonCreditMinted {
                id: credit_id,
                tons_co2: tons,
                owner: 1,
            }
            .into(),
        );
    });
}

#[test]
fn mint_carbon_credit_already_exists_fails() {
    new_test_ext().execute_with(|| {
        let credit_id = b"credit-001".to_vec();

        assert_ok!(Eco::mint_carbon_credit(
            RuntimeOrigin::signed(1),
            credit_id.clone(),
            b"Project 1".to_vec(),
            100
        ));

        // Duplicate mint attempt should fail
        assert_noop!(
            Eco::mint_carbon_credit(
                RuntimeOrigin::signed(1),
                credit_id,
                b"Project 1 duplicate".to_vec(),
                200
            ),
            Error::<Test>::CreditAlreadyExists
        );
    });
}

#[test]
fn mint_carbon_credit_max_reached_fails() {
    new_test_ext().execute_with(|| {
        // Pre-fill storage up to MaxCarbonCredits (1000)
        for i in 0..1000u32 {
            let id = format!("credit_{:04}", i).into_bytes();
            assert_ok!(Eco::mint_carbon_credit(
                RuntimeOrigin::signed(1),
                id,
                b"Project".to_vec(),
                10
            ));
        }

        // The 1001st mint should exceed MaxCarbonCredits limit
        let overflow_id = b"credit_overflow".to_vec();
        assert_noop!(
            Eco::mint_carbon_credit(
                RuntimeOrigin::signed(1),
                overflow_id,
                b"Project".to_vec(),
                10
            ),
            Error::<Test>::MaxCarbonCreditsReached
        );
    });
}

// =========================================================================
// verify_carbon_credit tests
// =========================================================================

#[test]
fn verify_carbon_credit_success() {
    new_test_ext().execute_with(|| {
        let credit_id = b"credit-001".to_vec();

        assert_ok!(Eco::mint_carbon_credit(
            RuntimeOrigin::signed(1),
            credit_id.clone(),
            b"Project".to_vec(),
            50
        ));

        // Verify credit as root
        assert_ok!(Eco::verify_carbon_credit(
            RuntimeOrigin::root(),
            credit_id.clone()
        ));

        let credit = Eco::carbon_credits(bv64(b"credit-001")).unwrap();
        assert_eq!(credit.verified, true);

        System::assert_has_event(Event::CarbonCreditVerified { id: credit_id }.into());
    });
}

#[test]
fn verify_carbon_credit_not_root_fails() {
    new_test_ext().execute_with(|| {
        let credit_id = b"credit-001".to_vec();

        assert_ok!(Eco::mint_carbon_credit(
            RuntimeOrigin::signed(1),
            credit_id.clone(),
            b"Project".to_vec(),
            50
        ));

        // Signed origin should fail (must be root)
        assert_noop!(
            Eco::verify_carbon_credit(RuntimeOrigin::signed(1), credit_id),
            DispatchError::BadOrigin
        );
    });
}

#[test]
fn verify_carbon_credit_not_found_fails() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Eco::verify_carbon_credit(RuntimeOrigin::root(), b"non-existent".to_vec()),
            Error::<Test>::CreditNotFound
        );
    });
}

#[test]
fn verify_carbon_credit_already_verified_fails() {
    new_test_ext().execute_with(|| {
        let credit_id = b"credit-001".to_vec();

        assert_ok!(Eco::mint_carbon_credit(
            RuntimeOrigin::signed(1),
            credit_id.clone(),
            b"Project".to_vec(),
            50
        ));

        assert_ok!(Eco::verify_carbon_credit(
            RuntimeOrigin::root(),
            credit_id.clone()
        ));

        // Second verification should fail
        assert_noop!(
            Eco::verify_carbon_credit(RuntimeOrigin::root(), credit_id),
            Error::<Test>::AlreadyVerified
        );
    });
}

// =========================================================================
// retire_carbon_credit tests
// =========================================================================

#[test]
fn retire_carbon_credit_success() {
    new_test_ext().execute_with(|| {
        let credit_id = b"credit-001".to_vec();
        let tons = 75u64;

        assert_ok!(Eco::mint_carbon_credit(
            RuntimeOrigin::signed(1),
            credit_id.clone(),
            b"Project".to_vec(),
            tons
        ));

        assert_ok!(Eco::retire_carbon_credit(
            RuntimeOrigin::signed(1),
            credit_id.clone()
        ));

        let credit = Eco::carbon_credits(bv64(b"credit-001")).unwrap();
        assert_eq!(credit.retired, true);
        assert_eq!(Eco::total_credits_retired(), tons);

        System::assert_has_event(
            Event::CarbonCreditRetired {
                id: credit_id,
                tons_co2: tons,
            }
            .into(),
        );
    });
}

#[test]
fn retire_carbon_credit_not_found_fails() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Eco::retire_carbon_credit(RuntimeOrigin::signed(1), b"non-existent".to_vec()),
            Error::<Test>::CreditNotFound
        );
    });
}

#[test]
fn retire_carbon_credit_already_retired_fails() {
    new_test_ext().execute_with(|| {
        let credit_id = b"credit-001".to_vec();

        assert_ok!(Eco::mint_carbon_credit(
            RuntimeOrigin::signed(1),
            credit_id.clone(),
            b"Project".to_vec(),
            50
        ));

        assert_ok!(Eco::retire_carbon_credit(
            RuntimeOrigin::signed(1),
            credit_id.clone()
        ));

        // Retiring an already retired credit fails
        assert_noop!(
            Eco::retire_carbon_credit(RuntimeOrigin::signed(1), credit_id),
            Error::<Test>::CreditAlreadyRetired
        );
    });
}

#[test]
fn retire_carbon_credit_not_owner_fails() {
    new_test_ext().execute_with(|| {
        let credit_id = b"credit-001".to_vec();

        assert_ok!(Eco::mint_carbon_credit(
            RuntimeOrigin::signed(1),
            credit_id.clone(),
            b"Project".to_vec(),
            50
        ));

        // Account 2 attempts to retire credit owned by Account 1
        assert_noop!(
            Eco::retire_carbon_credit(RuntimeOrigin::signed(2), credit_id),
            Error::<Test>::NotCreditOwner
        );
    });
}

// =========================================================================
// transfer_carbon_credit tests
// =========================================================================

#[test]
fn transfer_carbon_credit_success() {
    new_test_ext().execute_with(|| {
        let credit_id = b"credit-001".to_vec();

        assert_ok!(Eco::mint_carbon_credit(
            RuntimeOrigin::signed(1),
            credit_id.clone(),
            b"Project".to_vec(),
            50
        ));

        assert_ok!(Eco::transfer_carbon_credit(
            RuntimeOrigin::signed(1),
            credit_id.clone(),
            2
        ));

        let credit = Eco::carbon_credits(bv64(b"credit-001")).unwrap();
        assert_eq!(credit.owner, 2);

        System::assert_has_event(
            Event::CarbonCreditTransferred {
                id: credit_id,
                from: 1,
                to: 2,
            }
            .into(),
        );
    });
}

#[test]
fn transfer_carbon_credit_not_owner_fails() {
    new_test_ext().execute_with(|| {
        let credit_id = b"credit-001".to_vec();

        assert_ok!(Eco::mint_carbon_credit(
            RuntimeOrigin::signed(1),
            credit_id.clone(),
            b"Project".to_vec(),
            50
        ));

        // Non-owner account 2 tries to transfer credit from 1 to 3
        assert_noop!(
            Eco::transfer_carbon_credit(RuntimeOrigin::signed(2), credit_id, 3),
            Error::<Test>::NotCreditOwner
        );
    });
}

#[test]
fn transfer_carbon_credit_not_found_fails() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Eco::transfer_carbon_credit(RuntimeOrigin::signed(1), b"non-existent".to_vec(), 2),
            Error::<Test>::CreditNotFound
        );
    });
}

#[test]
fn transfer_carbon_credit_retired_fails() {
    new_test_ext().execute_with(|| {
        let credit_id = b"credit-001".to_vec();

        assert_ok!(Eco::mint_carbon_credit(
            RuntimeOrigin::signed(1),
            credit_id.clone(),
            b"Project".to_vec(),
            50
        ));

        assert_ok!(Eco::retire_carbon_credit(
            RuntimeOrigin::signed(1),
            credit_id.clone()
        ));

        // Attempting to transfer a retired credit fails
        assert_noop!(
            Eco::transfer_carbon_credit(RuntimeOrigin::signed(1), credit_id, 2),
            Error::<Test>::CreditAlreadyRetired
        );
    });
}

// =========================================================================
// create_reforest_project tests
// =========================================================================

#[test]
fn create_reforest_project_success() {
    new_test_ext().execute_with(|| {
        let project_id = b"proj-001".to_vec();
        let project_name = b"Green Forest Initiative".to_vec();
        let trees = 1000u32;
        let location = b"Madrid, Spain".to_vec();

        assert_ok!(Eco::create_reforest_project(
            RuntimeOrigin::signed(1),
            project_id.clone(),
            project_name.clone(),
            trees,
            location
        ));

        let proj = Eco::reforest_projects(bv64(b"proj-001")).expect("Project should exist");
        assert_eq!(proj.trees_planted, 1000);
        assert_eq!(proj.survival_rate, 0);
        assert_eq!(proj.verified, false);
        assert_eq!(Eco::total_trees_planted(), 1000);

        System::assert_has_event(
            Event::ReforestProjectCreated {
                id: project_id,
                name: project_name,
                trees,
            }
            .into(),
        );
    });
}

#[test]
fn create_reforest_project_already_exists_fails() {
    new_test_ext().execute_with(|| {
        let project_id = b"proj-001".to_vec();

        assert_ok!(Eco::create_reforest_project(
            RuntimeOrigin::signed(1),
            project_id.clone(),
            b"Project 1".to_vec(),
            500,
            b"Location 1".to_vec()
        ));

        assert_noop!(
            Eco::create_reforest_project(
                RuntimeOrigin::signed(1),
                project_id,
                b"Project 1 Dup".to_vec(),
                500,
                b"Location 1".to_vec()
            ),
            Error::<Test>::ProjectAlreadyExists
        );
    });
}

#[test]
fn create_reforest_project_max_reached_fails() {
    new_test_ext().execute_with(|| {
        // Pre-fill storage up to MaxReforestProjects (500)
        for i in 0..500u32 {
            let id = format!("proj_{:04}", i).into_bytes();
            assert_ok!(Eco::create_reforest_project(
                RuntimeOrigin::signed(1),
                id,
                b"Reforest Project".to_vec(),
                100,
                b"Location".to_vec()
            ));
        }

        // The 501st creation fails
        let overflow_id = b"proj_overflow".to_vec();
        assert_noop!(
            Eco::create_reforest_project(
                RuntimeOrigin::signed(1),
                overflow_id,
                b"Reforest Project".to_vec(),
                100,
                b"Location".to_vec()
            ),
            Error::<Test>::MaxReforestProjectsReached
        );
    });
}

// =========================================================================
// update_reforest_project tests
// =========================================================================

#[test]
fn update_reforest_project_success() {
    new_test_ext().execute_with(|| {
        let project_id = b"proj-001".to_vec();

        assert_ok!(Eco::create_reforest_project(
            RuntimeOrigin::signed(1),
            project_id.clone(),
            b"Project 1".to_vec(),
            500,
            b"Location 1".to_vec()
        ));

        assert_ok!(Eco::update_reforest_project(
            RuntimeOrigin::root(),
            project_id.clone(),
            750,
            92
        ));

        let proj = Eco::reforest_projects(bv64(b"proj-001")).unwrap();
        assert_eq!(proj.trees_planted, 750);
        assert_eq!(proj.survival_rate, 92);

        System::assert_has_event(
            Event::ReforestProjectUpdated {
                id: project_id,
                trees: 750,
                survival_rate: 92,
            }
            .into(),
        );
    });
}

#[test]
fn update_reforest_project_not_root_fails() {
    new_test_ext().execute_with(|| {
        let project_id = b"proj-001".to_vec();

        assert_ok!(Eco::create_reforest_project(
            RuntimeOrigin::signed(1),
            project_id.clone(),
            b"Project 1".to_vec(),
            500,
            b"Location 1".to_vec()
        ));

        assert_noop!(
            Eco::update_reforest_project(RuntimeOrigin::signed(1), project_id, 750, 90),
            DispatchError::BadOrigin
        );
    });
}

#[test]
fn update_reforest_project_not_found_fails() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Eco::update_reforest_project(RuntimeOrigin::root(), b"non-existent".to_vec(), 500, 90),
            Error::<Test>::ProjectNotFound
        );
    });
}

// =========================================================================
// verify_reforest_project tests
// =========================================================================

#[test]
fn verify_reforest_project_success() {
    new_test_ext().execute_with(|| {
        let project_id = b"proj-001".to_vec();

        assert_ok!(Eco::create_reforest_project(
            RuntimeOrigin::signed(1),
            project_id.clone(),
            b"Project 1".to_vec(),
            500,
            b"Location 1".to_vec()
        ));

        assert_ok!(Eco::verify_reforest_project(
            RuntimeOrigin::root(),
            project_id.clone()
        ));

        let proj = Eco::reforest_projects(bv64(b"proj-001")).unwrap();
        assert_eq!(proj.verified, true);

        System::assert_has_event(Event::ReforestProjectVerified { id: project_id }.into());
    });
}

#[test]
fn verify_reforest_project_not_root_fails() {
    new_test_ext().execute_with(|| {
        let project_id = b"proj-001".to_vec();

        assert_ok!(Eco::create_reforest_project(
            RuntimeOrigin::signed(1),
            project_id.clone(),
            b"Project 1".to_vec(),
            500,
            b"Location 1".to_vec()
        ));

        assert_noop!(
            Eco::verify_reforest_project(RuntimeOrigin::signed(1), project_id),
            DispatchError::BadOrigin
        );
    });
}

#[test]
fn verify_reforest_project_not_found_fails() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Eco::verify_reforest_project(RuntimeOrigin::root(), b"non-existent".to_vec()),
            Error::<Test>::ProjectNotFound
        );
    });
}

// =========================================================================
// register_green_validator tests
// =========================================================================

#[test]
fn register_green_validator_success() {
    new_test_ext().execute_with(|| {
        let energy_source = b"Solar & Wind".to_vec();
        let score = 85u8;

        assert_ok!(Eco::register_green_validator(
            RuntimeOrigin::signed(1),
            energy_source.clone(),
            200,
            500,
            score
        ));

        let validator = Eco::green_validators(1).expect("Validator should exist");
        assert_eq!(validator.address, 1);
        assert_eq!(validator.renewable_energy, true);
        assert_eq!(validator.score, score);
        assert_eq!(validator.carbon_offset, 200);
        assert_eq!(validator.trees_planted, 500);

        System::assert_has_event(
            Event::GreenValidatorRegistered {
                address: 1,
                energy_source,
                score,
            }
            .into(),
        );
    });
}

#[test]
fn register_green_validator_already_registered_fails() {
    new_test_ext().execute_with(|| {
        assert_ok!(Eco::register_green_validator(
            RuntimeOrigin::signed(1),
            b"Solar".to_vec(),
            100,
            200,
            80
        ));

        assert_noop!(
            Eco::register_green_validator(
                RuntimeOrigin::signed(1),
                b"Hydro".to_vec(),
                150,
                300,
                85
            ),
            Error::<Test>::ValidatorAlreadyRegistered
        );
    });
}

#[test]
fn register_green_validator_max_reached_fails() {
    new_test_ext().execute_with(|| {
        // Register up to MaxGreenValidators (101 accounts: 1..=101)
        for account in 1..=101u64 {
            assert_ok!(Eco::register_green_validator(
                RuntimeOrigin::signed(account),
                b"Renewable".to_vec(),
                100,
                100,
                80
            ));
        }

        // Account 102 fails to register
        assert_noop!(
            Eco::register_green_validator(
                RuntimeOrigin::signed(102),
                b"Renewable".to_vec(),
                100,
                100,
                80
            ),
            Error::<Test>::MaxGreenValidatorsReached
        );
    });
}

// =========================================================================
// update_green_score tests
// =========================================================================

#[test]
fn update_green_score_success() {
    new_test_ext().execute_with(|| {
        assert_ok!(Eco::register_green_validator(
            RuntimeOrigin::signed(1),
            b"Solar".to_vec(),
            100,
            200,
            80
        ));

        assert_ok!(Eco::update_green_score(RuntimeOrigin::signed(1), 95));

        let validator = Eco::green_validators(1).unwrap();
        assert_eq!(validator.score, 95);

        System::assert_has_event(
            Event::GreenScoreUpdated {
                address: 1,
                score: 95,
            }
            .into(),
        );
    });
}

#[test]
fn update_green_score_not_registered_fails() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Eco::update_green_score(RuntimeOrigin::signed(1), 90),
            Error::<Test>::ValidatorNotFound
        );
    });
}

#[test]
fn update_green_score_out_of_range_fails() {
    new_test_ext().execute_with(|| {
        assert_ok!(Eco::register_green_validator(
            RuntimeOrigin::signed(1),
            b"Solar".to_vec(),
            100,
            200,
            80
        ));

        // Score above MaxGreenScore (100) should fail
        assert_noop!(
            Eco::update_green_score(RuntimeOrigin::signed(1), 101),
            Error::<Test>::InvalidScore
        );
    });
}

// =========================================================================
// genesis_config test
// =========================================================================

#[test]
fn genesis_config_builds_correctly() {
    let mut storage = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();

    pallet_eco::GenesisConfig::<Test> {
        carbon_credits: vec![(
            b"gen-credit-1".to_vec(),
            b"Gen Project".to_vec(),
            500u64,
            true,
            1u64,
        )],
        reforest_projects: vec![(
            b"gen-proj-1".to_vec(),
            b"Gen Reforest".to_vec(),
            2000u32,
            b"Spain".to_vec(),
            90u8,
            true,
        )],
        green_validators: vec![(1u64, true, b"Wind".to_vec(), 500u64, 2000u32, 95u8)],
    }
    .assimilate_storage(&mut storage)
    .unwrap();

    let mut ext = sp_io::TestExternalities::new(storage);
    ext.execute_with(|| {
        let credit = Eco::carbon_credits(bv64(b"gen-credit-1")).unwrap();
        assert_eq!(credit.tons_co2, 500);
        assert_eq!(credit.verified, true);
        assert_eq!(credit.owner, 1);

        let proj = Eco::reforest_projects(bv64(b"gen-proj-1")).unwrap();
        assert_eq!(proj.trees_planted, 2000);
        assert_eq!(proj.survival_rate, 90);
        assert_eq!(proj.verified, true);

        let val = Eco::green_validators(1).unwrap();
        assert_eq!(val.score, 95);

        assert_eq!(Eco::total_co2_offset(), 500);
        assert_eq!(Eco::total_trees_planted(), 2000);
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

    const PALLET_NAME: &str = "eco";

    #[test]
    #[ignore]
    fn real_bench() {
        new_test_ext().execute_with(|| {{
            use frame_system::Pallet as System;
            System::<Test>::set_block_number(1);
            
            let mut results: Vec<(&str, u64)> = Vec::new();

            // Benchmark: mint_carbon_credit
            let mut idx = 0u64;
            let w = measure_bench("mint_carbon_credit", 50, || {
                idx += 1;
                let id = format!("cc_{}", idx).into_bytes();
                Eco::mint_carbon_credit(RuntimeOrigin::signed(1), id, b"Amazon Project".to_vec(), 100).is_ok()
            });
            results.push(("mint_carbon_credit", w));

            // Benchmark: create_reforest_project
            let mut ridx = 0u64;
            let w = measure_bench("create_reforest_project", 50, || {
                ridx += 1;
                let id = format!("rf_{}", ridx).into_bytes();
                Eco::create_reforest_project(RuntimeOrigin::signed(1), id, b"Reforest A".to_vec(), 1000, b"Brazil".to_vec()).is_ok()
            });
            results.push(("create_reforest_project", w));

            // Benchmark: register_green_validator
            let mut vidx = 0u64;
            let w = measure_bench("register_green_validator", 50, || {
                vidx += 1;
                let src = format!("solar_{}", vidx).into_bytes();
                Eco::register_green_validator(RuntimeOrigin::signed(vidx), src, 1000, 500, 90).is_ok()
            });
            results.push(("register_green_validator", w));

            println!("\n//! WeightInfo for pallet-eco (real benchmark)");
            println!("pub struct WeightInfo;");
            for (name, weight) in &results {
                println!("// {}: {} weight units", name, weight);
            }

        }});
    }
}
