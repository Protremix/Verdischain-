//! WeightInfo for pallet-zk-compression
use core::marker::PhantomData;
use frame_support::{traits::Get, weights::Weight};

pub trait WeightInfo {
    fn create_tree() -> Weight;
    fn compress_account() -> Weight;
    fn verify_proof() -> Weight;
}

pub struct SubstrateWeight<T>(PhantomData<T>);
impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
    fn create_tree() -> Weight {
        Weight::from_parts(50_000, 0)
            .saturating_add(T::DbWeight::get().reads(1))
            .saturating_add(T::DbWeight::get().writes(2))
    }
    fn compress_account() -> Weight {
        Weight::from_parts(30_000, 0)
            .saturating_add(T::DbWeight::get().reads(3))
            .saturating_add(T::DbWeight::get().writes(2))
    }
    fn verify_proof() -> Weight {
        Weight::from_parts(100_000, 0).saturating_add(T::DbWeight::get().reads(2))
    }
}

impl WeightInfo for () {
    fn create_tree() -> Weight {
        Weight::from_parts(50_000, 0)
    }
    fn compress_account() -> Weight {
        Weight::from_parts(30_000, 0)
    }
    fn verify_proof() -> Weight {
        Weight::from_parts(100_000, 0)
    }
}
