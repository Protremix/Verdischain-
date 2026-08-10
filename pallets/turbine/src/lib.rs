#![allow(
    clippy::let_unit_value,
    deprecated,
    clippy::clone_on_copy,
    clippy::type_complexity,
    clippy::needless_borrow,
    clippy::collapsible_if,
    clippy::redundant_closure,
    clippy::manual_saturating_arithmetic,
    clippy::unnecessary_cast
)]
#![cfg_attr(not(feature = "std"), no_std)]
use frame_support::{dispatch::DispatchResult, pallet_prelude::*};
use frame_system::pallet_prelude::*;
pub use pallet::*;
use sp_std::prelude::*;

#[frame_support::pallet]
pub mod pallet {
    use super::*;
    #[pallet::pallet]
    pub struct Pallet<T>(_);
    #[pallet::config]
    pub trait Config: frame_system::Config {
        type MaxShards: Get<u32>;
        type RedundancyFactor: Get<u32>;
        type MaxValidatorsPerNode: Get<u32>;
    }
    #[pallet::storage]
    pub type TurbineTotalShards<T> = StorageValue<_, u64, ValueQuery>;
    #[pallet::storage]
    pub type TurbineTotalBlocks<T> = StorageValue<_, u64, ValueQuery>;
    #[pallet::storage]
    pub type TurbineTreeDepth<T> = StorageValue<_, u32, ValueQuery>;
    #[pallet::storage]
    pub type TurbineValidatorCount<T> = StorageValue<_, u32, ValueQuery>;
    #[pallet::storage]
    pub type BlockShardCount<T> = StorageMap<_, Twox64Concat, u32, u32, ValueQuery>;
    #[pallet::event]
    #[pallet::generate_deposit(fn deposit_event)]
    pub enum Event<T: Config> {
        ShardPropagated { shard_id: u32, block_number: u32 },
        BlockSharded { block_number: u32, shard_count: u32 },
        TreeRebuilt { depth: u32, validator_count: u32 },
    }
    #[pallet::error]
    pub enum Error<T> {
        MaxShardsExceeded,
        InvalidShardIndex,
        NoValidators,
    }
    #[pallet::call]
    impl<T: Config> Pallet<T> {
        #[pallet::weight(0)]
        #[pallet::call_index(0)]
        pub fn register_shard(
            origin: OriginFor<T>,
            block_number: u32,
            shard_index: u32,
            total_shards: u32,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            ensure!(
                total_shards <= T::MaxShards::get(),
                Error::<T>::MaxShardsExceeded
            );
            TurbineTotalShards::<T>::mutate(|s| *s += 1);
            BlockShardCount::<T>::mutate(block_number, |c| *c += 1);
            Self::deposit_event(Event::ShardPropagated {
                shard_id: shard_index,
                block_number,
            });
            Ok(())
        }
        #[pallet::weight(0)]
        #[pallet::call_index(1)]
        pub fn rebuild_tree(origin: OriginFor<T>, validator_count: u32) -> DispatchResult {
            ensure_root(origin)?;
            ensure!(validator_count > 0, Error::<T>::NoValidators);
            let depth = Self::calc_depth(validator_count, T::MaxValidatorsPerNode::get());
            TurbineTreeDepth::<T>::put(depth);
            TurbineValidatorCount::<T>::put(validator_count);
            Self::deposit_event(Event::TreeRebuilt {
                depth,
                validator_count,
            });
            Ok(())
        }
        #[pallet::weight(0)]
        #[pallet::call_index(2)]
        pub fn mark_block_propagated(origin: OriginFor<T>, block_number: u32) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            TurbineTotalBlocks::<T>::mutate(|b| *b += 1);
            let sc = BlockShardCount::<T>::get(block_number);
            Self::deposit_event(Event::BlockSharded {
                block_number,
                shard_count: sc,
            });
            Ok(())
        }
    }
    impl<T: Config> Pallet<T> {
        fn calc_depth(count: u32, fanout: u32) -> u32 {
            if fanout == 0 {
                return 1;
            }
            let mut d = 1;
            let mut n = fanout;
            while n < count {
                n = n.saturating_mul(fanout);
                d += 1;
            }
            d
        }
    }
}

#[cfg(test)]
mod tests;
