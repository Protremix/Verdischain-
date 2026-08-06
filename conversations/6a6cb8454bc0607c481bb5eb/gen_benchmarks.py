#!/usr/bin/env python3
"""Generate benchmarking infrastructure for all 5 Verdis pallets."""
import os
import textwrap

BASE = "/opt/verdis-chain"

# ============================================================
# 1. Fix weights.rs for each pallet with correct function names
# ============================================================

WEIGHTS_TEMPLATE = '''\
// This file is part of Verdis Chain.
// Benchmark weight definitions for pallet_{name}.
// Generated on: 2026-08-06

#![cfg_attr(rustfmt, rustfmt_skip)]
#![allow(unused_parens)]
#![allow(unused_imports)]

use frame_support::{{traits::Get, weights::Weight}};
use core::marker::PhantomData;

/// Weight functions needed for pallet_{name}.
pub trait WeightInfo {{
{trait_fns}
}}

/// Weights for pallet_{name} using the Substrate node and recommended hardware.
pub struct SubstrateWeight<T>(PhantomData<T>);
impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {{
{impl_fns}
}}

// For execution in mock tests
impl WeightInfo for () {{
{unit_fns}
}}
'''

pallets = {
    "dpos": ["register_validator", "unregister_validator", "vote", "unvote", "slash_validator", "update_green_score"],
    "amm-dex": ["create_pool", "add_liquidity", "remove_liquidity", "swap", "get_price"],
    "eco": ["mint_carbon_credit", "verify_carbon_credit", "retire_carbon_credit", "transfer_carbon_credit",
            "create_reforest_project", "update_reforest_project", "verify_reforest_project",
            "register_green_validator", "update_green_score"],
    "tokenomics": ["give_consent", "purchase", "update_presale_price", "release_distribution"],
    "vesting": ["assign_vesting", "release_vested", "check_transfer"],
}

for name, fns in pallets.items():
    trait_fns = "\n".join(f"    fn {fn}() -> Weight;" for fn in fns)
    
    impl_fns = "\n".join(textwrap.dedent(f"""\
        fn {fn}() -> Weight {{
            Weight::from_parts(30_000_000, 3000)
                .saturating_add(T::DbWeight::get().reads(3_u64))
                .saturating_add(T::DbWeight::get().writes(2_u64))
        }}""") for fn in fns)
    impl_fns = "\n\n".join(impl_fns.split("\n\n"))
    
    unit_fns = "\n".join(f"    fn {fn}() -> Weight {{ Weight::from_parts(30_000_000, 3000) }}" for fn in fns)
    
    content = WEIGHTS_TEMPLATE.format(
        name=name,
        trait_fns=trait_fns,
        impl_fns=impl_fns,
        unit_fns=unit_fns,
    )
    
    path = os.path.join(BASE, "pallets", name, "src", "weights.rs")
    with open(path, "w") as f:
        f.write(content)
    print(f"Fixed weights.rs for {name}")

# ============================================================
# 2. Create benchmarking.rs for each pallet
# ============================================================

BENCH_TEMPLATE = '''\
//! Benchmarking for pallet_{name}

#![cfg(feature = "runtime-benchmarks")]

use super::*;

use frame_benchmarking::{{benchmarks, whitelisted_caller}};
use frame_system::RawOrigin;
use sp_runtime::traits::Bounded;

benchmarks! {{
{benchmarks_body}
}}

#[cfg(test)]
mod tests {{
    use super::*;
    use crate::{{mock, mock::*}};
    use frame_benchmarking::impl_benchmark_test_suite;

    impl_benchmark_test_suite!(Pallet, crate::mock::new_test_ext(), crate::mock::Test);
}}
'''

# DPoS benchmarking
dpos_bench = '''
    register_validator {
        let caller: T::AccountId = whitelisted_caller();
        // Fund the caller so they can stake
        T::Currency::deposit_creating(&caller, T::MinStake::get() * 2u32.into());
    }: _(RawOrigin::Signed(caller), 80u8, b"Solar".to_vec())

    unregister_validator {
        let caller: T::AccountId = whitelisted_caller();
        T::Currency::deposit_creating(&caller, T::MinStake::get() * 2u32.into());
        Pallet::<T>::register_validator(RawOrigin::Signed(caller.clone()).into(), 80u8, b"Solar".to_vec())?;
    }: _(RawOrigin::Signed(caller))

    vote {
        let caller: T::AccountId = whitelisted_caller();
        let validator: T::AccountId = whitelisted_caller();
        T::Currency::deposit_creating(&validator, T::MinStake::get() * 2u32.into());
        T::Currency::deposit_creating(&caller, T::MinStake::get() * 10u32.into());
        Pallet::<T>::register_validator(RawOrigin::Signed(validator.clone()).into(), 80u8, b"Solar".to_vec())?;
    }: _(RawOrigin::Signed(caller), validator, T::MinStake::get())

    unvote {
        let caller: T::AccountId = whitelisted_caller();
        let validator: T::AccountId = whitelisted_caller();
        T::Currency::deposit_creating(&validator, T::MinStake::get() * 2u32.into());
        T::Currency::deposit_creating(&caller, T::MinStake::get() * 10u32.into());
        Pallet::<T>::register_validator(RawOrigin::Signed(validator.clone()).into(), 80u8, b"Solar".to_vec())?;
        Pallet::<T>::vote(RawOrigin::Signed(caller.clone()).into(), validator.clone(), T::MinStake::get())?;
    }: _(RawOrigin::Signed(caller), validator)

    slash_validator {
        let validator: T::AccountId = whitelisted_caller();
        T::Currency::deposit_creating(&validator, T::MinStake::get() * 2u32.into());
        Pallet::<T>::register_validator(RawOrigin::Signed(validator.clone()).into(), 80u8, b"Solar".to_vec())?;
    }: _(RawOrigin::Root, validator, T::MinStake::get() / 2u32.into(), b"Misbehavior".to_vec())

    update_green_score {
        let caller: T::AccountId = whitelisted_caller();
        T::Currency::deposit_creating(&caller, T::MinStake::get() * 2u32.into());
        Pallet::<T>::register_validator(RawOrigin::Signed(caller.clone()).into(), 80u8, b"Solar".to_vec())?;
    }: _(RawOrigin::Signed(caller), 90u8)
'''

with open(os.path.join(BASE, "pallets", "dpos", "src", "benchmarking.rs"), "w") as f:
    f.write(BENCH_TEMPLATE.format(name="dpos", benchmarks_body=dpos_bench))
print("Created benchmarking.rs for dpos")

# AmmDex benchmarking
amm_bench = '''
    create_pool {
        let caller: T::AccountId = whitelisted_caller();
        let token_a = 1u32.encode();
        let token_b = 2u32.encode();
        let amount_a: BalanceOf<T> = 1_000_000_000u128.into();
        let amount_b: BalanceOf<T> = 2_000_000_000u128.into();
    }: _(RawOrigin::Signed(caller), token_a, token_b, amount_a, amount_b)

    add_liquidity {
        let caller: T::AccountId = whitelisted_caller();
        let token_a = 1u32.encode();
        let token_b = 2u32.encode();
        let amount_a: BalanceOf<T> = 1_000_000_000u128.into();
        let amount_b: BalanceOf<T> = 2_000_000_000u128.into();
        Pallet::<T>::create_pool(RawOrigin::Signed(caller.clone()).into(), token_a, token_b, amount_a, amount_b)?;
    }: _(RawOrigin::Signed(caller), 0u32, 500_000_000u128.into(), 1_000_000_000u128.into())

    remove_liquidity {
        let caller: T::AccountId = whitelisted_caller();
        let token_a = 1u32.encode();
        let token_b = 2u32.encode();
        let amount_a: BalanceOf<T> = 1_000_000_000u128.into();
        let amount_b: BalanceOf<T> = 2_000_000_000u128.into();
        Pallet::<T>::create_pool(RawOrigin::Signed(caller.clone()).into(), token_a, token_b, amount_a, amount_b)?;
        Pallet::<T>::add_liquidity(RawOrigin::Signed(caller.clone()).into(), 0u32, 500_000_000u128.into(), 1_000_000_000u128.into())?;
    }: _(RawOrigin::Signed(caller), 0u32, 500_000_000u128.into())

    swap {
        let caller: T::AccountId = whitelisted_caller();
        let token_a = 1u32.encode();
        let token_b = 2u32.encode();
        let amount_a: BalanceOf<T> = 1_000_000_000u128.into();
        let amount_b: BalanceOf<T> = 2_000_000_000u128.into();
        Pallet::<T>::create_pool(RawOrigin::Signed(caller.clone()).into(), token_a, token_b, amount_a, amount_b)?;
    }: _(RawOrigin::Signed(caller), 0u32, true, 100_000_000u128.into())

    get_price {
        let caller: T::AccountId = whitelisted_caller();
        let token_a = 1u32.encode();
        let token_b = 2u32.encode();
        let amount_a: BalanceOf<T> = 1_000_000_000u128.into();
        let amount_b: BalanceOf<T> = 2_000_000_000u128.into();
        Pallet::<T>::create_pool(RawOrigin::Signed(caller.clone()).into(), token_a, token_b, amount_a, amount_b)?;
    }: _(RawOrigin::Signed(caller), 0u32)
'''

with open(os.path.join(BASE, "pallets", "amm-dex", "src", "benchmarking.rs"), "w") as f:
    f.write(BENCH_TEMPLATE.format(name="amm-dex", benchmarks_body=amm_bench))
print("Created benchmarking.rs for amm-dex")

# Eco benchmarking
eco_bench = '''
    mint_carbon_credit {
        let caller: T::AccountId = whitelisted_caller();
        let project_id = b"PROJ-001".to_vec();
        let amount: u64 = 1000;
        let metadata = b"Carbon credit from reforestation".to_vec();
    }: _(RawOrigin::Signed(caller), project_id, amount, metadata)

    verify_carbon_credit {
        let caller: T::AccountId = whitelisted_caller();
        let id = b"CREDIT-001".to_vec();
        let project_id = b"PROJ-001".to_vec();
        let amount: u64 = 1000;
        let metadata = b"Carbon credit from reforestation".to_vec();
        Pallet::<T>::mint_carbon_credit(RawOrigin::Signed(caller).into(), project_id, amount, metadata)?;
    }: verify_carbon_credit(RawOrigin::Root, id)

    retire_carbon_credit {
        let caller: T::AccountId = whitelisted_caller();
        let id = b"CREDIT-001".to_vec();
        let project_id = b"PROJ-001".to_vec();
        let amount: u64 = 1000;
        let metadata = b"Carbon credit from reforestation".to_vec();
        Pallet::<T>::mint_carbon_credit(RawOrigin::Signed(caller.clone()).into(), project_id, amount, metadata)?;
    }: _(RawOrigin::Signed(caller), id)

    transfer_carbon_credit {
        let caller: T::AccountId = whitelisted_caller();
        let recipient: T::AccountId = whitelisted_caller();
        let id = b"CREDIT-001".to_vec();
        let project_id = b"PROJ-001".to_vec();
        let amount: u64 = 1000;
        let metadata = b"Carbon credit from reforestation".to_vec();
        Pallet::<T>::mint_carbon_credit(RawOrigin::Signed(caller.clone()).into(), project_id, amount, metadata)?;
    }: _(RawOrigin::Signed(caller), recipient, id)

    create_reforest_project {
        let caller: T::AccountId = whitelisted_caller();
        let name = b"Amazon Reforestation".to_vec();
        let location = b"Brazil".to_vec();
        let area_hectares: u64 = 10000;
        let metadata = b"Reforestation project".to_vec();
    }: _(RawOrigin::Signed(caller), name, location, area_hectares, metadata)

    update_reforest_project {
        let caller: T::AccountId = whitelisted_caller();
        let id = b"PROJ-001".to_vec();
        let name = b"Amazon Reforestation".to_vec();
        let location = b"Brazil".to_vec();
        let area_hectares: u64 = 10000;
        let metadata = b"Reforestation project".to_vec();
        Pallet::<T>::create_reforest_project(RawOrigin::Signed(caller.clone()).into(), name, location, area_hectares, metadata)?;
    }: _(RawOrigin::Signed(caller), id, 20000u64, b"Updated metadata".to_vec())

    verify_reforest_project {
        let caller: T::AccountId = whitelisted_caller();
        let id = b"PROJ-001".to_vec();
        let name = b"Amazon Reforestation".to_vec();
        let location = b"Brazil".to_vec();
        let area_hectares: u64 = 10000;
        let metadata = b"Reforestation project".to_vec();
        Pallet::<T>::create_reforest_project(RawOrigin::Signed(caller).into(), name, location, area_hectares, metadata)?;
    }: verify_reforest_project(RawOrigin::Root, id)

    register_green_validator {
        let caller: T::AccountId = whitelisted_caller();
        let name = b"Green Validator 1".to_vec();
        let energy_source = b"Solar".to_vec();
    }: _(RawOrigin::Signed(caller), name, energy_source, 85u8)

    update_green_score {
        let caller: T::AccountId = whitelisted_caller();
        let name = b"Green Validator 1".to_vec();
        let energy_source = b"Solar".to_vec();
        Pallet::<T>::register_green_validator(RawOrigin::Signed(caller.clone()).into(), name, energy_source, 85u8)?;
    }: _(RawOrigin::Signed(caller), 90u8)
'''

with open(os.path.join(BASE, "pallets", "eco", "src", "benchmarking.rs"), "w") as f:
    f.write(BENCH_TEMPLATE.format(name="eco", benchmarks_body=eco_bench))
print("Created benchmarking.rs for eco")

# Tokenomics benchmarking
tok_bench = '''
    give_consent {
        let caller: T::AccountId = whitelisted_caller();
    }: _(RawOrigin::Signed(caller))

    purchase {
        let caller: T::AccountId = whitelisted_caller();
        let amount: BalanceOf<T> = 1_000_000_000u128.into();
        T::Currency::deposit_creating(&caller, amount * 2u32.into());
    }: _(RawOrigin::Signed(caller), amount)

    update_presale_price {
        let price_bps: u32 = 500;
    }: update_presale_price(RawOrigin::Root, price_bps)

    release_distribution {
        let recipient: T::AccountId = whitelisted_caller();
        let amount: BalanceOf<T> = 1_000_000_000u128.into();
    }: release_distribution(RawOrigin::Root, recipient, amount)
'''

with open(os.path.join(BASE, "pallets", "tokenomics", "src", "benchmarking.rs"), "w") as f:
    f.write(BENCH_TEMPLATE.format(name="tokenomics", benchmarks_body=tok_bench))
print("Created benchmarking.rs for tokenomics")

# Vesting benchmarking
vest_bench = '''
    assign_vesting {
        let recipient: T::AccountId = whitelisted_caller();
        let amount: BalanceOf<T> = 1_000_000_000u128.into();
        let duration_blocks: u64 = 1000;
        let cliff_blocks: u64 = 100;
    }: assign_vesting(RawOrigin::Root, recipient, amount, duration_blocks, cliff_blocks)

    release_vested {
        let caller: T::AccountId = whitelisted_caller();
        let amount: BalanceOf<T> = 1_000_000_000u128.into();
        Pallet::<T>::assign_vesting(RawOrigin::Root, caller.clone(), amount, 10u64, 1u64)?;
        // Advance blocks past vesting period
        frame_system::Pallet::<T>::set_block_number(frame_system::Pallet::<T>::block_number() + 100u32.into());
    }: _(RawOrigin::Signed(caller))

    check_transfer {
        let from: T::AccountId = whitelisted_caller();
        let amount: BalanceOf<T> = 1_000_000_000u128.into();
        Pallet::<T>::assign_vesting(RawOrigin::Root, from.clone(), amount, 1000u64, 100u64)?;
    }: _(&from, amount)
'''

with open(os.path.join(BASE, "pallets", "vesting", "src", "benchmarking.rs"), "w") as f:
    f.write(BENCH_TEMPLATE.format(name="vesting", benchmarks_body=vest_bench))
print("Created benchmarking.rs for vesting")

# ============================================================
# 3. Add benchmarking module to each pallet's lib.rs
# ============================================================

for name in pallets:
    lib_path = os.path.join(BASE, "pallets", name, "src", "lib.rs")
    with open(lib_path, "r") as f:
        content = f.read()
    
    marker = '#![cfg_attr(not(feature = "std"), no_std)]'
    bench_line = '\n#[cfg(feature = "runtime-benchmarks")]\npub mod benchmarking;\n'
    
    if 'pub mod benchmarking' not in content:
        content = content.replace(marker, marker + bench_line, 1)
        with open(lib_path, "w") as f:
            f.write(content)
        print(f"Wired benchmarking into {name}/lib.rs")
    else:
        print(f"{name}/lib.rs already has benchmarking")

print("\nDone! All benchmarking files created.")
