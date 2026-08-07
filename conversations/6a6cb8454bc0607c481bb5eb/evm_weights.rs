//! Weight functions for pallet_evm
#![cfg_attr(rustfmt, rustfmt_skip)]
#![allow(unused_parens)]
#![allow(unused_imports)]

use frame_support::{traits::Get, weights::Weight};
use core::marker::PhantomData;

/// Weight functions needed for pallet_evm.
pub trait WeightInfo {
    fn deploy_contract() -> Weight;
    fn call_contract() -> Weight;
    fn execute_code() -> Weight;
}

/// Weights for pallet_evm using the Substrate node and recommended hardware.
pub struct SubstrateWeight<T>(PhantomData<T>);
impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
    fn deploy_contract() -> Weight {
        Weight::from_parts(50_000_000, 5000)
            .saturating_add(T::DbWeight::get().reads(2_u64))
            .saturating_add(T::DbWeight::get().writes(2_u64))
    }
    fn call_contract() -> Weight {
        Weight::from_parts(100_000_000, 10000)
            .saturating_add(T::DbWeight::get().reads(3_u64))
            .saturating_add(T::DbWeight::get().writes(1_u64))
    }
    fn execute_code() -> Weight {
        Weight::from_parts(80_000_000, 8000)
            .saturating_add(T::DbWeight::get().reads(1_u64))
    }
}

/// Weight info for tests.
impl WeightInfo for () {
    fn deploy_contract() -> Weight {
        Weight::from_parts(50_000_000, 5000)
    }
    fn call_contract() -> Weight {
        Weight::from_parts(100_000_000, 10000)
    }
    fn execute_code() -> Weight {
        Weight::from_parts(80_000_000, 8000)
    }
}
