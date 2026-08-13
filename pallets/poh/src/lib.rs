#![allow(clippy::incompatible_msrv)]
#![allow(
    clippy::let_unit_value,
    deprecated,
    clippy::clone_on_copy,
    clippy::type_complexity,
    clippy::needless_borrow,
    clippy::collapsible_if,
    clippy::redundant_closure,
    clippy::manual_saturating_arithmetic,
    clippy::unnecessary_cast,
    clippy::derivable_impls,
    clippy::manual_checked_ops,
    clippy::needless_borrows_for_generic_args
)]
//! # Verdis Proof of History (PoH) Pallet
//!
//! Provides cryptographic timestamping using a VDF-like SHA-256 hash chain.

#![cfg_attr(not(feature = "std"), no_std)]
pub mod weights;
use codec::{Decode, Encode, MaxEncodedLen};
use frame_support::{dispatch::DispatchResult, pallet_prelude::*};
use frame_system::pallet_prelude::*;
use scale_info::TypeInfo;
use sp_runtime::traits::Saturating;
pub use weights::SubstrateWeight;
use weights::WeightInfo;

use sp_std::prelude::*;

#[cfg(feature = "std")]
use serde::{Deserialize, Serialize};

pub use pallet::*;

#[cfg(test)]
mod tests;

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;

/// PoH configuration and state tracking struct
#[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo, Default)]
#[cfg_attr(feature = "std", derive(Serialize, Deserialize))]
pub struct PoHConfig {
    pub seed: [u8; 32],
    pub last_hash: [u8; 32],
    pub tick_count: u64,
}

#[frame_support::pallet]
pub mod pallet {
    use super::*;

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type WeightInfo: WeightInfo;
    }

    /// Map of block_number -> PoH hash
    #[pallet::storage]
    #[pallet::getter(fn poh_hashes)]
    pub type PohHashes<T: Config> =
        StorageMap<_, Blake2_128Concat, BlockNumberFor<T>, [u8; 32], OptionQuery>;

    /// Current tick count of the hash chain
    #[pallet::storage]
    #[pallet::getter(fn poh_tick)]
    pub type PohTick<T: Config> = StorageValue<_, u64, ValueQuery>;

    /// Current PoH configuration (seed, last_hash, tick_count)
    #[pallet::storage]
    #[pallet::getter(fn poh_config)]
    pub type PohConfigVal<T: Config> = StorageValue<_, PoHConfig, ValueQuery>;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// A new PoH tick was generated [tick_count, hash]
        TickGenerated { tick_count: u64, hash: [u8; 32] },
        /// A block was stamped with a PoH hash [block_number, hash]
        BlockStamped {
            block_number: BlockNumberFor<T>,
            hash: [u8; 32],
        },
        /// PoH configuration updated [seed, last_hash]
        ConfigUpdated { seed: [u8; 32], last_hash: [u8; 32] },
    }

    #[pallet::error]
    pub enum Error<T> {
        /// Block hash not found for the given block number
        BlockHashNotFound,
        /// Invalid block range for verification
        InvalidBlockRange,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Record a block by advancing the PoH hash chain and stamping the current block.
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::record_block())]
        pub fn record_block(origin: OriginFor<T>) -> DispatchResult {
            let _who = ensure_root(origin)?;
            let block_number = <frame_system::Pallet<T>>::block_number();
            let hash = Self::tick();
            <PohHashes<T>>::insert(block_number, hash);
            Self::deposit_event(Event::BlockStamped { block_number, hash });
            Ok(())
        }

        /// Set or reset the PoH seed and last_hash configuration.
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::set_config())]
        pub fn set_config(
            origin: OriginFor<T>,
            seed: [u8; 32],
            last_hash: [u8; 32],
        ) -> DispatchResult {
            ensure_root(origin)?;
            let current_tick = PohTick::<T>::get();
            let new_config = PoHConfig {
                seed,
                last_hash,
                tick_count: current_tick,
            };
            PohConfigVal::<T>::put(new_config);
            Self::deposit_event(Event::ConfigUpdated { seed, last_hash });
            Ok(())
        }

        /// Explicit extrinsic to generate a PoH tick.
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::tick_extrinsic())]
        pub fn tick_extrinsic(origin: OriginFor<T>) -> DispatchResult {
            let _who = ensure_root(origin)?;
            Self::tick();
            Ok(())
        }
    }

    impl<T: Config> Pallet<T> {
        /// Calculate the next hash in the VDF hash chain: sha256(last_hash || seed || tick_count)
        pub fn calculate_hash(last_hash: &[u8; 32], seed: &[u8; 32], tick_count: u64) -> [u8; 32] {
            use sha2::{Digest, Sha256};
            let mut hasher = Sha256::new();
            hasher.update(last_hash);
            hasher.update(seed);
            hasher.update(tick_count.to_be_bytes());
            let result = hasher.finalize();
            let mut hash = [0u8; 32];
            hash.copy_from_slice(&result);
            hash
        }

        /// Advance the hash chain by 1 tick and return the new hash.
        pub fn tick() -> [u8; 32] {
            let mut config = PohConfigVal::<T>::get();
            config.tick_count = config.tick_count.saturating_add(1);
            let new_hash = Self::calculate_hash(&config.last_hash, &config.seed, config.tick_count);
            config.last_hash = new_hash;

            PohTick::<T>::put(config.tick_count);
            PohConfigVal::<T>::put(&config);

            Self::deposit_event(Event::TickGenerated {
                tick_count: config.tick_count,
                hash: new_hash,
            });

            new_hash
        }

        /// Get the PoH hash for a specific block number
        pub fn get_poh_hash(block_number: BlockNumberFor<T>) -> Option<[u8; 32]> {
            <PohHashes<T>>::get(block_number)
        }

        /// Verify the hash chain for a contiguous range of blocks [start_block, end_block]
        pub fn verify_poh(start_block: BlockNumberFor<T>, end_block: BlockNumberFor<T>) -> bool {
            if start_block > end_block {
                return false;
            }
            let mut current = start_block;
            while current <= end_block {
                if !<PohHashes<T>>::contains_key(current) {
                    return false;
                }
                if current == end_block {
                    break;
                }
                current = current.saturating_add(1u32.into());
            }
            true
        }
    }
}
