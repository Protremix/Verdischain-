//! Benchmarking for pallet_eco

#![cfg(feature = "runtime-benchmarks")]

use super::*;
use frame_benchmarking::{benchmarks, whitelisted_caller};
use frame_system::RawOrigin;

benchmarks! {

    mint_carbon_credit {
        let caller: T::AccountId = whitelisted_caller();
        let id = b"CREDIT-001".to_vec();
        let project_name = b"Amazon Reforestation".to_vec();
        let tons_co2: u64 = 1000;
    }: _(RawOrigin::Signed(caller), id, project_name, tons_co2)

    verify_carbon_credit {
        let caller: T::AccountId = whitelisted_caller();
        let id = b"CREDIT-001".to_vec();
        let project_name = b"Amazon Reforestation".to_vec();
        let tons_co2: u64 = 1000;
        Pallet::<T>::mint_carbon_credit(RawOrigin::Signed(caller).into(), id.clone(), project_name, tons_co2)?;
    }: verify_carbon_credit(RawOrigin::Root, id)

    retire_carbon_credit {
        let caller: T::AccountId = whitelisted_caller();
        let id = b"CREDIT-001".to_vec();
        let project_name = b"Amazon Reforestation".to_vec();
        let tons_co2: u64 = 1000;
        Pallet::<T>::mint_carbon_credit(RawOrigin::Signed(caller.clone()).into(), id.clone(), project_name, tons_co2)?;
    }: _(RawOrigin::Signed(caller), id)

    transfer_carbon_credit {
        let caller: T::AccountId = whitelisted_caller();
        let recipient: T::AccountId = whitelisted_caller();
        let id = b"CREDIT-001".to_vec();
        let project_name = b"Amazon Reforestation".to_vec();
        let tons_co2: u64 = 1000;
        Pallet::<T>::mint_carbon_credit(RawOrigin::Signed(caller.clone()).into(), id.clone(), project_name, tons_co2)?;
    }: _(RawOrigin::Signed(caller), id, recipient)

    create_reforest_project {
        let caller: T::AccountId = whitelisted_caller();
        let id = b"PROJ-001".to_vec();
        let name = b"Amazon Reforestation".to_vec();
        let trees_planted: u32 = 10000;
        let location = b"Brazil".to_vec();
    }: _(RawOrigin::Signed(caller), id, name, trees_planted, location)

    update_reforest_project {
        let caller: T::AccountId = whitelisted_caller();
        let id = b"PROJ-001".to_vec();
        let name = b"Amazon Reforestation".to_vec();
        let trees_planted: u32 = 10000;
        let location = b"Brazil".to_vec();
        Pallet::<T>::create_reforest_project(RawOrigin::Signed(caller).into(), id.clone(), name, trees_planted, location)?;
    }: update_reforest_project(RawOrigin::Root, id, 20000u32, 85u8)

    verify_reforest_project {
        let caller: T::AccountId = whitelisted_caller();
        let id = b"PROJ-001".to_vec();
        let name = b"Amazon Reforestation".to_vec();
        let trees_planted: u32 = 10000;
        let location = b"Brazil".to_vec();
        Pallet::<T>::create_reforest_project(RawOrigin::Signed(caller).into(), id.clone(), name, trees_planted, location)?;
    }: verify_reforest_project(RawOrigin::Root, id)

    register_green_validator {
        let caller: T::AccountId = whitelisted_caller();
        let energy_source = b"Solar".to_vec();
        let carbon_offset: u64 = 5000;
        let trees_planted: u32 = 100;
        let score: u8 = 85;
    }: _(RawOrigin::Signed(caller), energy_source, carbon_offset, trees_planted, score)

    update_green_score {
        let caller: T::AccountId = whitelisted_caller();
        let energy_source = b"Solar".to_vec();
        let carbon_offset: u64 = 5000;
        let trees_planted: u32 = 100;
        let score: u8 = 85;
        Pallet::<T>::register_green_validator(RawOrigin::Signed(caller.clone()).into(), energy_source, carbon_offset, trees_planted, score)?;
    }: _(RawOrigin::Signed(caller), 90u8)

}
