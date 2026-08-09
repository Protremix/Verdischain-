//! Benchmarking for the Verdis Eco pallet
#![cfg(feature = "runtime-benchmarks")]
#![allow(unused_variables, unused_imports, unused_must_use, clippy::all)]

use crate::pallet::*;
use frame_benchmarking::v2::*;
use frame_support::{traits::ConstU32, BoundedVec};
use frame_system::RawOrigin;
use sp_std::vec;

#[benchmarks]
mod benches {
    use super::*;
    use crate::pallet::*;

    #[benchmark]
    fn mint_carbon_credit() {
        let caller: T::AccountId = whitelisted_caller();
        let id = b"credit-1".to_vec();
        let project_name = b"Amazon Reforestation".to_vec();
        let tons_co2 = 100u64;

        #[extrinsic_call]
        mint_carbon_credit(
            RawOrigin::Root,
            caller.clone(),
            id.clone(),
            project_name,
            tons_co2,
        );

        let id_bv: BoundedVec<u8, ConstU32<64>> = id.try_into().unwrap();
        assert!(CarbonCredits::<T>::contains_key(&id_bv));
    }

    #[benchmark]
    fn verify_carbon_credit() {
        let caller: T::AccountId = whitelisted_caller();
        let id = b"credit-1".to_vec();
        let project_name = b"Amazon Reforestation".to_vec();
        let tons_co2 = 100u64;

        let _ = Pallet::<T>::mint_carbon_credit(
            RawOrigin::Root.into(),
            caller.clone(),
            id.clone(),
            project_name,
            tons_co2,
        );

        #[extrinsic_call]
        verify_carbon_credit(RawOrigin::Root, id.clone());

        let id_bv: BoundedVec<u8, ConstU32<64>> = id.try_into().unwrap();
        let credit = CarbonCredits::<T>::get(&id_bv).expect("Credit should exist");
        assert!(credit.verified);
    }

    #[benchmark]
    fn retire_carbon_credit() {
        let caller: T::AccountId = whitelisted_caller();
        let id = b"credit-1".to_vec();
        let project_name = b"Amazon Reforestation".to_vec();
        let tons_co2 = 100u64;

        let _ = Pallet::<T>::mint_carbon_credit(
            RawOrigin::Root.into(),
            caller.clone(),
            id.clone(),
            project_name,
            tons_co2,
        );

        #[extrinsic_call]
        retire_carbon_credit(RawOrigin::Signed(caller), id.clone());

        let id_bv: BoundedVec<u8, ConstU32<64>> = id.try_into().unwrap();
        let credit = CarbonCredits::<T>::get(&id_bv).expect("Credit should exist");
        assert!(credit.retired);
    }

    #[benchmark]
    fn transfer_carbon_credit() {
        let caller: T::AccountId = whitelisted_caller();
        let recipient: T::AccountId = account("recipient", 0, 0);
        let id = b"credit-1".to_vec();
        let project_name = b"Amazon Reforestation".to_vec();
        let tons_co2 = 100u64;

        let _ = Pallet::<T>::mint_carbon_credit(
            RawOrigin::Root.into(),
            caller.clone(),
            id.clone(),
            project_name,
            tons_co2,
        );

        #[extrinsic_call]
        transfer_carbon_credit(RawOrigin::Signed(caller), id.clone(), recipient.clone());

        let id_bv: BoundedVec<u8, ConstU32<64>> = id.try_into().unwrap();
        let credit = CarbonCredits::<T>::get(&id_bv).expect("Credit should exist");
        assert_eq!(credit.owner, recipient);
    }

    #[benchmark]
    fn create_reforest_project() {
        let caller: T::AccountId = whitelisted_caller();
        let id = b"project-1".to_vec();
        let name = b"Amazon Basin".to_vec();
        let trees_planted = 10_000u32;
        let location = b"Brazil".to_vec();

        #[extrinsic_call]
        create_reforest_project(
            RawOrigin::Root,
            id.clone(),
            name,
            trees_planted,
            location,
        );

        let id_bv: BoundedVec<u8, ConstU32<64>> = id.try_into().unwrap();
        assert!(ReforestProjects::<T>::contains_key(&id_bv));
    }

    #[benchmark]
    fn update_reforest_project() {
        let caller: T::AccountId = whitelisted_caller();
        let id = b"project-1".to_vec();
        let name = b"Amazon Basin".to_vec();
        let initial_trees = 10_000u32;
        let location = b"Brazil".to_vec();

        let _ = Pallet::<T>::create_reforest_project(
            RawOrigin::Root.into(),
            id.clone(),
            name,
            initial_trees,
            location,
        );

        let updated_trees = 15_000u32;
        let survival_rate = 85u8;

        #[extrinsic_call]
        update_reforest_project(RawOrigin::Root, id.clone(), updated_trees, survival_rate);

        let id_bv: BoundedVec<u8, ConstU32<64>> = id.try_into().unwrap();
        let proj = ReforestProjects::<T>::get(&id_bv).expect("Project should exist");
        assert_eq!(proj.trees_planted, updated_trees);
        assert_eq!(proj.survival_rate, survival_rate);
    }

    #[benchmark]
    fn verify_reforest_project() {
        let caller: T::AccountId = whitelisted_caller();
        let id = b"project-1".to_vec();
        let name = b"Amazon Basin".to_vec();
        let trees = 10_000u32;
        let location = b"Brazil".to_vec();

        let _ = Pallet::<T>::create_reforest_project(
            RawOrigin::Root.into(),
            id.clone(),
            name,
            trees,
            location,
        );

        #[extrinsic_call]
        verify_reforest_project(RawOrigin::Root, id.clone());

        let id_bv: BoundedVec<u8, ConstU32<64>> = id.try_into().unwrap();
        let proj = ReforestProjects::<T>::get(&id_bv).expect("Project should exist");
        assert!(proj.verified);
    }

    #[benchmark]
    fn register_green_validator() {
        let caller: T::AccountId = whitelisted_caller();
        let energy_source = b"Solar/Wind Hybrid".to_vec();
        let carbon_offset = 5_000u64;
        let trees_planted = 1_000u32;
        let score = 80u8;

        #[extrinsic_call]
        register_green_validator(
            RawOrigin::Signed(caller.clone()),
            energy_source,
            carbon_offset,
            trees_planted,
            score,
        );

        assert!(GreenValidators::<T>::contains_key(&caller));
    }

    #[benchmark]
    fn update_green_score() {
        let caller: T::AccountId = whitelisted_caller();
        let energy_source = b"Solar/Wind Hybrid".to_vec();
        let carbon_offset = 5_000u64;
        let trees_planted = 1_000u32;
        let initial_score = 80u8;

        let _ = Pallet::<T>::register_green_validator(
            RawOrigin::Signed(caller.clone()).into(),
            energy_source,
            carbon_offset,
            trees_planted,
            initial_score,
        );

        let new_score = 95u8;

        #[extrinsic_call]
        update_green_score(RawOrigin::Root, caller.clone(), new_score);

        let gv = GreenValidators::<T>::get(&caller).expect("Validator should exist");
        assert_eq!(gv.score, new_score);
    }

    impl_benchmark_test_suite!(Pallet, crate::tests::new_test_ext(), crate::tests::Test,);
}
