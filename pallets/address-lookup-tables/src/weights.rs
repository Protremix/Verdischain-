//! WeightInfo for pallet-address-lookup-tables
use core::marker::PhantomData;
use frame_support::{traits::Get, weights::Weight};

pub trait WeightInfo {
    fn create_table() -> Weight;
    fn add_address() -> Weight;
    fn deactivate_table() -> Weight;
    fn lookup_address() -> Weight;
}

pub struct SubstrateWeight<T>(PhantomData<T>);
impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
    fn create_table() -> Weight {
        Weight::from_parts(15_000, 0)
            .saturating_add(T::DbWeight::get().reads(1))
            .saturating_add(T::DbWeight::get().writes(1))
    }
    fn add_address() -> Weight {
        Weight::from_parts(10_000, 0)
            .saturating_add(T::DbWeight::get().reads(2))
            .saturating_add(T::DbWeight::get().writes(1))
    }
    fn deactivate_table() -> Weight {
        Weight::from_parts(10_000, 0)
            .saturating_add(T::DbWeight::get().reads(1))
            .saturating_add(T::DbWeight::get().writes(1))
    }
    fn lookup_address() -> Weight {
        Weight::from_parts(5_000, 0).saturating_add(T::DbWeight::get().reads(1))
    }
}

impl WeightInfo for () {
    fn create_table() -> Weight {
        Weight::from_parts(15_000, 0)
    }
    fn add_address() -> Weight {
        Weight::from_parts(10_000, 0)
    }
    fn deactivate_table() -> Weight {
        Weight::from_parts(10_000, 0)
    }
    fn lookup_address() -> Weight {
        Weight::from_parts(5_000, 0)
    }
}
