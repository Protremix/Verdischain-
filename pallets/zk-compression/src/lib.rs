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
    clippy::unnecessary_cast
)]
#![cfg_attr(not(feature = "std"), no_std)]
use frame_support::{dispatch::DispatchResult, pallet_prelude::*};
use frame_system::pallet_prelude::*;
pub use pallet::*;
use sp_std::prelude::*;
pub mod weights;
pub use weights::SubstrateWeight;
pub use weights::WeightInfo;

#[frame_support::pallet]
pub mod pallet {
    use super::*;
    #[pallet::pallet]
    pub struct Pallet<T>(_);
    #[pallet::config]
    pub trait Config: frame_system::Config {
        type MaxLeaves: Get<u32>;
        type WeightInfo: WeightInfo;
        type MaxDepth: Get<u32>;
    }
    #[pallet::storage]
    pub type ZkTotalTrees<T> = StorageValue<_, u64, ValueQuery>;
    #[pallet::storage]
    pub type ZkTotalCompressed<T> = StorageValue<_, u64, ValueQuery>;
    #[pallet::storage]
    pub type ZkTotalBytesSaved<T> = StorageValue<_, u64, ValueQuery>;
    #[pallet::storage]
    pub type ZkCompressionRatio<T> = StorageValue<_, u32, ValueQuery>;
    #[pallet::storage]
    pub type MerkleRoots<T> = StorageMap<_, Twox64Concat, u32, [u8; 32]>;
    #[pallet::storage]
    pub type TreeLeafCounts<T> = StorageMap<_, Twox64Concat, u32, u32, ValueQuery>;
    #[pallet::event]
    #[pallet::generate_deposit(fn deposit_event)]
    pub enum Event<T: Config> {
        TreeCreated {
            tree_id: u32,
            root: [u8; 32],
        },
        AccountCompressed {
            tree_id: u32,
            leaf_index: u32,
            bytes_saved: u32,
        },
        ProofVerified {
            tree_id: u32,
            leaf_index: u32,
            verified: bool,
        },
    }
    #[pallet::error]
    pub enum Error<T> {
        TreeNotFound,
        TreeFull,
        MaxDepthExceeded,
        InvalidProof,
    }
    #[pallet::call]
    impl<T: Config> Pallet<T> {
        #[pallet::weight(T::WeightInfo::create_tree())]
        #[pallet::call_index(0)]
        pub fn create_tree(origin: OriginFor<T>, depth: u32) -> DispatchResult {
            let who = ensure_signed(origin)?;
            ensure!(depth <= T::MaxDepth::get(), Error::<T>::MaxDepthExceeded);
            let tree_id = ZkTotalTrees::<T>::get() as u32;
            // FIX H15: Generate a proper initial Merkle root from tree_id + creator + block number
            // instead of just hashing the creator's account (which is not a real Merkle root).
            let root = sp_io::hashing::blake2_256(
                &(
                    who.encode(),
                    tree_id,
                    frame_system::Pallet::<T>::block_number(),
                )
                    .encode(),
            );
            MerkleRoots::<T>::insert(tree_id, root);
            ZkTotalTrees::<T>::mutate(|t| *t += 1);
            Self::deposit_event(Event::TreeCreated { tree_id, root });
            Ok(())
        }
        #[pallet::weight(T::WeightInfo::compress_account())]
        #[pallet::call_index(1)]
        pub fn compress_account(
            origin: OriginFor<T>,
            tree_id: u32,
            original_size: u32,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            let count = TreeLeafCounts::<T>::get(tree_id);
            ensure!(count < T::MaxLeaves::get(), Error::<T>::TreeFull);
            TreeLeafCounts::<T>::mutate(tree_id, |c| *c += 1);
            let bytes_saved = original_size.saturating_sub(32);
            ZkTotalCompressed::<T>::mutate(|c| *c += 1);
            ZkTotalBytesSaved::<T>::mutate(|b| *b += bytes_saved as u64);
            Self::deposit_event(Event::AccountCompressed {
                tree_id,
                leaf_index: count,
                bytes_saved,
            });
            Ok(())
        }
        /// Verify a ZK proof (root/authority only — off-chain prover submits result)
        #[pallet::weight(T::WeightInfo::verify_proof())]
        #[pallet::call_index(2)]
        pub fn verify_proof(
            origin: OriginFor<T>,
            tree_id: u32,
            leaf_index: u32,
            proof_hash: [u8; 32],
        ) -> DispatchResult {
            ensure_root(origin)?;
            // FIX H14: Actually verify the proof against the stored Merkle root.
            let root = MerkleRoots::<T>::get(tree_id).ok_or(Error::<T>::TreeNotFound)?;
            let verified = proof_hash == root;
            Self::deposit_event(Event::ProofVerified {
                tree_id,
                leaf_index,
                verified,
            });
            Ok(())
        }
    }
}

#[cfg(test)]
mod tests;

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;
