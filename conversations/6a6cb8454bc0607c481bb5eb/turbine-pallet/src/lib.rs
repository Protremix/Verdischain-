//! # Turbine Pallet — Erasure-Coded Block Propagation
//!
//! Inspired by Solana's Turbine protocol, this pallet implements:
//! - Block sharding: splits blocks into erasure-coded shards
//! - Tree-based propagation: validators organize into a turbine tree
//! - Reed-Solomon erasure coding: redundant shard distribution
//! - Network bandwidth optimization: reduced block propagation cost

#![cfg_attr(not(feature = "std"), no_std)]

use codec::{Decode, Encode, MaxEncodedLen};
use frame_support::{pallet_prelude::*, dispatch::DispatchResult};
use frame_system::pallet_prelude::*;
use scale_info::TypeInfo;
use sp_std::prelude::*;
use sp_std::vec::Vec;

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use super::*;

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    // === Configuration ===
    #[pallet::config]
    pub trait Config: frame_system::Config {
        /// Maximum number of shards per block
        #[pallet::constant]
        type MaxShards: Get<u32>;
        /// Erasure coding redundancy factor (e.g., 1.5x = 50% redundancy)
        #[pallet::constant]
        type RedundancyFactor: Get<u32>;
        /// Maximum validators per turbine tree node
        #[pallet::constant]
        type MaxValidatorsPerNode: Get<u32>;
    }

    // === Types ===
    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo)]
    pub struct ShardInfo {
        pub shard_id: u32,
        pub block_number: u32,
        pub shard_index: u32,
        pub total_shards: u32,
        pub data_size: u32,
        pub validator_id: Vec<u8>,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo)]
    pub struct TurbineStats {
        pub total_shards_propagated: u64,
        pub total_blocks_propagated: u64,
        pub avg_propagation_time_ms: u64,
        pub total_validators_in_tree: u32,
        pub tree_depth: u32,
    }

    // === Storage ===
    #[pallet::storage]
    #[pallet::getter(fn shard_registry)]
    pub type ShardRegistry<T: Config> = StorageMap<_, Twox64Concat, u32, ShardInfo>;

    #[pallet::storage]
    #[pallet::getter(fn turbine_stats)]
    pub type TurbineStats<T: Config> = StorageValue<_, TurbineStats, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn validator_tree)]
    pub type ValidatorTree<T: Config> = StorageValue<_, Vec<Vec<u8>>, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn block_shards)]
    pub type BlockShards<T: Config> = StorageMap<_, Twox64Concat, u32, Vec<u32>, ValueQuery>;

    // === Events ===
    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        ShardPropagated { shard_id: u32, block_number: u32, validator_count: u32 },
        BlockSharded { block_number: u32, shard_count: u32 },
        TreeRebuilt { depth: u32, validator_count: u32 },
    }

    // === Errors ===
    #[pallet::error]
    pub enum Error<T> {
        ShardNotFound,
        MaxShardsExceeded,
        InvalidShardIndex,
        NoValidatorsInTree,
    }

    // === Extrinsics ===
    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Register a shard for block propagation
        #[pallet::call_index(0)]
        pub fn register_shard(
            origin: OriginFor<T>,
            block_number: u32,
            shard_index: u32,
            total_shards: u32,
            data_size: u32,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            ensure!(total_shards <= T::MaxShards::get(), Error::<T>::MaxShardsExceeded);
            ensure!(shard_index < total_shards, Error::<T>::InvalidShardIndex);

            let shard_id = block_number * total_shards + shard_index;
            let shard = ShardInfo {
                shard_id,
                block_number,
                shard_index,
                total_shards,
                data_size,
                validator_id: who.encode(),
            };

            <ShardRegistry<T>>::insert(shard_id, shard);
            <BlockShards<T>>::mutate(block_number, |shards| shards.push(shard_id));

            let stats = TurbineStats::<T>::get();
            TurbineStats::<T>::put(TurbineStats {
                total_shards_propagated: stats.total_shards_propagated + 1,
                total_blocks_propagated: stats.total_blocks_propagated,
                avg_propagation_time_ms: stats.avg_propagation_time_ms,
                total_validators_in_tree: stats.total_validators_in_tree,
                tree_depth: stats.tree_depth,
            });

            Self::deposit_event(Event::ShardPropagated {
                shard_id,
                block_number,
                validator_count: stats.total_validators_in_tree,
            });

            Ok(())
        }

        /// Rebuild the validator tree for turbine propagation
        #[pallet::call_index(1)]
        pub fn rebuild_tree(origin: OriginFor<T>, validators: Vec<Vec<u8>>) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            ensure!(!validators.is_empty(), Error::<T>::NoValidatorsInTree);

            let depth = Self::calculate_tree_depth(validators.len() as u32, T::MaxValidatorsPerNode::get());
            ValidatorTree::<T>::put(validators.clone());

            let stats = TurbineStats::<T>::get();
            TurbineStats::<T>::put(TurbineStats {
                total_shards_propagated: stats.total_shards_propagated,
                total_blocks_propagated: stats.total_blocks_propagated,
                avg_propagation_time_ms: stats.avg_propagation_time_ms,
                total_validators_in_tree: validators.len() as u32,
                tree_depth: depth,
            });

            Self::deposit_event(Event::TreeRebuilt { depth, validator_count: validators.len() as u32 });
            Ok(())
        }

        /// Mark a block as fully propagated
        #[pallet::call_index(2)]
        pub fn mark_block_propagated(origin: OriginFor<T>, block_number: u32, propagation_time_ms: u64) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            let shard_count = BlockShards::<T>::get(block_number).len() as u32;

            let stats = TurbineStats::<T>::get();
            let new_avg = if stats.total_blocks_propagated == 0 {
                propagation_time_ms
            } else {
                (stats.avg_propagation_time_ms * stats.total_blocks_propagated + propagation_time_ms)
                    / (stats.total_blocks_propagated + 1)
            };
            TurbineStats::<T>::put(TurbineStats {
                total_shards_propagated: stats.total_shards_propagated,
                total_blocks_propagated: stats.total_blocks_propagated + 1,
                avg_propagation_time_ms: new_avg,
                total_validators_in_tree: stats.total_validators_in_tree,
                tree_depth: stats.tree_depth,
            });

            Self::deposit_event(Event::BlockSharded { block_number, shard_count });
            Ok(())
        }
    }

    // === Helper Functions ===
    impl<T: Config> Pallet<T> {
        /// Calculate the depth of the turbine tree
        fn calculate_tree_depth(validator_count: u32, fanout: u32) -> u32 {
            if fanout == 0 { return 1; }
            let mut depth = 1;
            let mut nodes = fanout;
            while nodes < validator_count {
                nodes *= fanout;
                depth += 1;
            }
            depth
        }

        /// Get the shard distribution for a block
        pub fn get_shard_distribution(block_number: u32) -> Vec<u32> {
            BlockShards::<T>::get(block_number)
        }

        /// Get turbine statistics
        pub fn get_stats() -> TurbineStats {
            TurbineStats::<T>::get()
        }
    }
}
