#!/usr/bin/env python3
"""Generate corrected benchmarking files for all 5 pallets."""

BASE = "/opt/verdis-chain/pallets"

# Common header with BalanceOf type alias
def header(name):
    return f'''//! Benchmarking for pallet_{name}

#![cfg(feature = "runtime-benchmarks")]

use super::*;
use frame_support::traits::Currency;
use frame_benchmarking::{{benchmarks, whitelisted_caller}};
use frame_system::RawOrigin;

type BalanceOf<T> = <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

benchmarks! {{
'''

# DPoS - already compiles, just add let _ = for deposit_creating
DPOS = '''
    register_validator {
        let caller: T::AccountId = whitelisted_caller();
        let _ = T::Currency::deposit_creating(&caller, T::MinStake::get() * 2u32.into());
    }: _(RawOrigin::Signed(caller), 80u8, b"Solar".to_vec())

    unregister_validator {
        let caller: T::AccountId = whitelisted_caller();
        let _ = T::Currency::deposit_creating(&caller, T::MinStake::get() * 2u32.into());
        Pallet::<T>::register_validator(RawOrigin::Signed(caller.clone()).into(), 80u8, b"Solar".to_vec())?;
    }: _(RawOrigin::Signed(caller))

    vote {
        let caller: T::AccountId = whitelisted_caller();
        let validator: T::AccountId = whitelisted_caller();
        let _ = T::Currency::deposit_creating(&validator, T::MinStake::get() * 2u32.into());
        let _ = T::Currency::deposit_creating(&caller, T::MinStake::get() * 10u32.into());
        Pallet::<T>::register_validator(RawOrigin::Signed(validator.clone()).into(), 80u8, b"Solar".to_vec())?;
    }: _(RawOrigin::Signed(caller), validator, T::MinStake::get())

    unvote {
        let caller: T::AccountId = whitelisted_caller();
        let validator: T::AccountId = whitelisted_caller();
        let _ = T::Currency::deposit_creating(&validator, T::MinStake::get() * 2u32.into());
        let _ = T::Currency::deposit_creating(&caller, T::MinStake::get() * 10u32.into());
        Pallet::<T>::register_validator(RawOrigin::Signed(validator.clone()).into(), 80u8, b"Solar".to_vec())?;
        Pallet::<T>::vote(RawOrigin::Signed(caller.clone()).into(), validator.clone(), T::MinStake::get())?;
    }: _(RawOrigin::Signed(caller), validator)

    slash_validator {
        let validator: T::AccountId = whitelisted_caller();
        let _ = T::Currency::deposit_creating(&validator, T::MinStake::get() * 2u32.into());
        Pallet::<T>::register_validator(RawOrigin::Signed(validator.clone()).into(), 80u8, b"Solar".to_vec())?;
    }: _(RawOrigin::Root, validator, T::MinStake::get() / 2u32.into(), b"Misbehavior".to_vec())

    update_green_score {
        let caller: T::AccountId = whitelisted_caller();
        let _ = T::Currency::deposit_creating(&caller, T::MinStake::get() * 2u32.into());
        Pallet::<T>::register_validator(RawOrigin::Signed(caller.clone()).into(), 80u8, b"Solar".to_vec())?;
    }: _(RawOrigin::Signed(caller), 90u8)
'''

# AmmDex - create_pool(origin, token_a: Vec<u8>, token_b: Vec<u8>, amount_a, amount_b)
# add_liquidity(origin, pool_id, amount_a, amount_b)
# remove_liquidity(origin, pool_id, lp_amount)
# swap(origin, pool_id, token_in: Vec<u8>, amount_in, min_amount_out)
# get_price(origin, pool_id)
AMM = '''
    create_pool {
        let caller: T::AccountId = whitelisted_caller();
        let token_a = b"TOKEN_A".to_vec();
        let token_b = b"TOKEN_B".to_vec();
        let amount_a = T::Currency::minimum_balance() * 1000u32.into();
        let amount_b = T::Currency::minimum_balance() * 2000u32.into();
        let _ = T::Currency::deposit_creating(&caller, amount_a + amount_b);
    }: _(RawOrigin::Signed(caller), token_a, token_b, amount_a, amount_b)

    add_liquidity {
        let caller: T::AccountId = whitelisted_caller();
        let token_a = b"TOKEN_A".to_vec();
        let token_b = b"TOKEN_B".to_vec();
        let amount_a = T::Currency::minimum_balance() * 1000u32.into();
        let amount_b = T::Currency::minimum_balance() * 2000u32.into();
        let _ = T::Currency::deposit_creating(&caller, (amount_a + amount_b) * 2u32.into());
        Pallet::<T>::create_pool(RawOrigin::Signed(caller.clone()).into(), token_a, token_b, amount_a, amount_b)?;
    }: _(RawOrigin::Signed(caller), 0u32, amount_a, amount_b)

    remove_liquidity {
        let caller: T::AccountId = whitelisted_caller();
        let token_a = b"TOKEN_A".to_vec();
        let token_b = b"TOKEN_B".to_vec();
        let amount_a = T::Currency::minimum_balance() * 1000u32.into();
        let amount_b = T::Currency::minimum_balance() * 2000u32.into();
        let _ = T::Currency::deposit_creating(&caller, (amount_a + amount_b) * 2u32.into());
        Pallet::<T>::create_pool(RawOrigin::Signed(caller.clone()).into(), token_a, token_b, amount_a, amount_b)?;
        Pallet::<T>::add_liquidity(RawOrigin::Signed(caller.clone()).into(), 0u32, amount_a, amount_b)?;
    }: _(RawOrigin::Signed(caller), 0u32, amount_a)

    swap {
        let caller: T::AccountId = whitelisted_caller();
        let token_a = b"TOKEN_A".to_vec();
        let token_b = b"TOKEN_B".to_vec();
        let amount_a = T::Currency::minimum_balance() * 1000u32.into();
        let amount_b = T::Currency::minimum_balance() * 2000u32.into();
        let _ = T::Currency::deposit_creating(&caller, (amount_a + amount_b) * 2u32.into());
        Pallet::<T>::create_pool(RawOrigin::Signed(caller.clone()).into(), token_a.clone(), token_b, amount_a, amount_b)?;
    }: _(RawOrigin::Signed(caller), 0u32, token_a, amount_a / 10u32.into(), BalanceOf::<T>::zero())

    get_price {
        let caller: T::AccountId = whitelisted_caller();
        let token_a = b"TOKEN_A".to_vec();
        let token_b = b"TOKEN_B".to_vec();
        let amount_a = T::Currency::minimum_balance() * 1000u32.into();
        let amount_b = T::Currency::minimum_balance() * 2000u32.into();
        let _ = T::Currency::deposit_creating(&caller, (amount_a + amount_b) * 2u32.into());
        Pallet::<T>::create_pool(RawOrigin::Signed(caller.clone()).into(), token_a, token_b, amount_a, amount_b)?;
    }: _(RawOrigin::Signed(caller), 0u32)
'''

# Eco - mint_carbon_credit(origin, id: Vec<u8>, project_name: Vec<u8>, tons_co2: u64)
# verify_carbon_credit(origin, id: Vec<u8>)
# retire_carbon_credit(origin, id: Vec<u8>)
# transfer_carbon_credit(origin, id: Vec<u8>, to: T::AccountId)
# create_reforest_project(origin, id: Vec<u8>, name: Vec<u8>, trees_planted: u32, location: Vec<u8>)
# update_reforest_project(origin, id: Vec<u8>, trees_planted: u32, survival_rate: u8)
# verify_reforest_project(origin, id: Vec<u8>)
# register_green_validator(origin, energy_source: Vec<u8>, carbon_offset: u64, trees_planted: u32, score: u8)
# update_green_score(origin, score: u8)
ECO = '''
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
'''

# Tokenomics - give_consent(origin)
# purchase(origin, amount: BalanceOf<T>)
# update_presale_price(origin, price_bps: u32)
# release_distribution(origin, category: Vec<u8>, amount: BalanceOf<T>)
TOK = '''
    give_consent {
        let caller: T::AccountId = whitelisted_caller();
    }: _(RawOrigin::Signed(caller))

    purchase {
        let caller: T::AccountId = whitelisted_caller();
        let amount = T::Currency::minimum_balance() * 1000u32.into();
        let _ = T::Currency::deposit_creating(&caller, amount * 2u32.into());
        Pallet::<T>::give_consent(RawOrigin::Signed(caller.clone()).into())?;
    }: _(RawOrigin::Signed(caller), amount)

    update_presale_price {
        let price_bps: u32 = 500;
    }: update_presale_price(RawOrigin::Root, price_bps)

    release_distribution {
        let recipient: T::AccountId = whitelisted_caller();
        let category = b"treasury".to_vec();
        let amount = T::Currency::minimum_balance() * 1000u32.into();
        let _ = T::Currency::deposit_creating(&recipient, amount * 2u32.into());
    }: release_distribution(RawOrigin::Root, category, amount)
'''

# Vesting - assign_vesting(origin, who: T::AccountId, schedule_label: Vec<u8>, amount: BalanceOf<T>)
# release_vested(origin)
# check_transfer(origin, from: T::AccountId, amount: BalanceOf<T>)
VEST = '''
    assign_vesting {
        let recipient: T::AccountId = whitelisted_caller();
        let label = b"team".to_vec();
        let amount = T::Currency::minimum_balance() * 1000u32.into();
        let _ = T::Currency::deposit_creating(&recipient, amount * 2u32.into());
    }: assign_vesting(RawOrigin::Root, recipient, label, amount)

    release_vested {
        let caller: T::AccountId = whitelisted_caller();
        let label = b"team".to_vec();
        let amount = T::Currency::minimum_balance() * 1000u32.into();
        let _ = T::Currency::deposit_creating(&caller, amount * 2u32.into());
        Pallet::<T>::assign_vesting(RawOrigin::Root, caller.clone(), label, amount)?;
    }: _(RawOrigin::Signed(caller))

    check_transfer {
        let caller: T::AccountId = whitelisted_caller();
        let from: T::AccountId = whitelisted_caller();
        let label = b"team".to_vec();
        let amount = T::Currency::minimum_balance() * 1000u32.into();
        let _ = T::Currency::deposit_creating(&from, amount * 2u32.into());
        Pallet::<T>::assign_vesting(RawOrigin::Root, from.clone(), label, amount / 2u32.into())?;
    }: _(RawOrigin::Signed(caller), from, amount / 4u32.into())
'''

files = {
    "dpos": DPOS,
    "amm-dex": AMM,
    "eco": ECO,
    "tokenomics": TOK,
    "vesting": VEST,
}

for name, body in files.items():
    content = header(name) + body + "\n}\n"
    path = f"{BASE}/{name}/src/benchmarking.rs"
    with open(path, "w") as f:
        f.write(content)
    print(f"Written {name}/benchmarking.rs")

print("\nAll benchmarking files corrected.")
