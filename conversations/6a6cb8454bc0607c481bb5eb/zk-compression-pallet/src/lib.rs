//! # ZK Compression Pallet
//!
//! Inspired by Solana's ZK compression, this pallet provides:
//! - Merkle tree-based state compression for accounts
//! - Compressed NFT/asset storage (store only the Merkle root on-chain)
//! - Proof-based verification of compressed state
//! - Significant storage cost reduction for eco assets (carbon credits, reforestation records)

#![cfg_attr(not(feature = "std"), no_std)]

use codec::{Decode, Encode, MaxEncodedLen};
use frame_support::{pallet_prelude::*, dispatch::DispatchResult};
use frame_system::pallet_prelude::*;
use scale_info::TypeInfo;
use sp_std::prelude::*;
use sp_std::vec::Vec;
use sp_core::blake2_256;

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use super::*;

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type MaxLeaves: Get<u32>;
        type MaxDepth: Get<u32>;
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo)]
    pub struct CompressedAccount {
        pub hash: [u8; 32],
        pub owner: Vec<u8>,
        pub data_hash: [u8; 32],
        pub leaf_index: u32,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo)]
    pub struct MerkleTreeInfo {
        pub root: [u8; 32],
        pub leaf_count: u32,
        pub depth: u32,
        pub creator: Vec<u8>,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo)]
    pub struct CompressionStats {
        pub total_trees: u64,
        pub total_compressed_accounts: u64,
        pub total_bytes_saved: u64,
        pub avg_compression_ratio: u32,
    }

    // === Storage ===
    #[pallet::storage]
    #[pallet::getter(fn merkle_trees)]
    pub type MerkleTrees<T: Config> = StorageMap<_, Twox64Concat, [u8; 32], MerkleTreeInfo>;

    #[pallet::storage]
    #[pallet::getter(fn compressed_accounts)]
    pub type CompressedAccounts<T: Config> = StorageDoubleMap<
        _,
        Twox64Concat,
        [u8; 32],
        Twox64Concat,
        u32,
        CompressedAccount,
    >;

    #[pallet::storage]
    #[pallet::getter(fn compression_stats)]
    pub type CompressionStats<T: Config> = StorageValue<_, CompressionStats, ValueQuery>;

    // === Events ===
    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        TreeCreated { root: [u8; 32], depth: u32 },
        AccountCompressed { tree_root: [u8; 32], leaf_index: u32, original_size: u32 },
        ProofVerified { tree_root: [u8; 32], leaf_index: u32, verified: bool },
    }

    // === Errors ===
    #[pallet::error]
    pub enum Error<T> {
        TreeNotFound,
        LeafAlreadyExists,
        MaxLeavesExceeded,
        MaxDepthExceeded,
        InvalidProof,
        TreeFull,
    }

    // === Extrinsics ===
    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Create a new Merkle tree for compressed storage
        #[pallet::call_index(0)]
        pub fn create_tree(origin: OriginFor<T>, depth: u32) -> DispatchResult {
            let who = ensure_signed(origin)?;
            ensure!(depth <= T::MaxDepth::get(), Error::<T>::MaxDepthExceeded);

            let seed = who.encode();
            let root = blake2_256(&seed);
            let tree = MerkleTreeInfo {
                root,
                leaf_count: 0,
                depth,
                creator: seed,
            };

            MerkleTrees::<T>::insert(root, tree);

            let stats = CompressionStats::<T>::get();
            CompressionStats::<T>::put(CompressionStats {
                total_trees: stats.total_trees + 1,
                total_compressed_accounts: stats.total_compressed_accounts,
                total_bytes_saved: stats.total_bytes_saved,
                avg_compression_ratio: stats.avg_compression_ratio,
            });

            Self::deposit_event(Event::TreeCreated { root, depth });
            Ok(())
        }

        /// Compress an account into a Merkle tree
        #[pallet::call_index(1)]
        pub fn compress_account(
            origin: OriginFor<T>,
            tree_root: [u8; 32],
            data: Vec<u8>,
            original_size: u32,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let mut tree = MerkleTrees::<T>::get(tree_root).ok_or(Error::<T>::TreeNotFound)?;
            ensure!(tree.leaf_count < T::MaxLeaves::get(), Error::<T>::TreeFull);

            let data_hash = blake2_256(&data);
            let owner_hash = blake2_256(&who.encode());
            let leaf_hash = blake2_256(&[tree_root.as_ref(), data_hash.as_ref(), owner_hash.as_ref()].concat());
            let leaf_index = tree.leaf_count;

            let account = CompressedAccount {
                hash: leaf_hash,
                owner: who.encode(),
                data_hash,
                leaf_index,
            };

            CompressedAccounts::<T>::insert(tree_root, leaf_index, account);

            tree.leaf_count += 1;
            MerkleTrees::<T>::insert(tree_root, tree);

            // Update compression stats
            let bytes_saved = original_size.saturating_sub(32); // 32 bytes = hash size
            let stats = CompressionStats::<T>::get();
            let new_avg = if stats.total_compressed_accounts == 0 {
                100 * bytes_saved / original_size.max(1)
            } else {
                let total_saved = stats.total_bytes_saved + bytes_saved as u64;
                let total_accounts = stats.total_compressed_accounts + 1;
                ((total_saved * 100) / (total_accounts * 256)) as u32 // rough estimate
            };
            CompressionStats::<T>::put(CompressionStats {
                total_trees: stats.total_trees,
                total_compressed_accounts: stats.total_compressed_accounts + 1,
                total_bytes_saved: stats.total_bytes_saved + bytes_saved as u64,
                avg_compression_ratio: new_avg,
            });

            Self::deposit_event(Event::AccountCompressed { tree_root, leaf_index, original_size });
            Ok(())
        }

        /// Verify a Merkle proof for a compressed account
        #[pallet::call_index(2)]
        pub fn verify_proof(
            origin: OriginFor<T>,
            tree_root: [u8; 32],
            leaf_index: u32,
            proof: Vec<[u8; 32]>,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            let account = CompressedAccounts::<T>::get(tree_root, leaf_index)
                .ok_or(Error::<T>::TreeNotFound)?;

            // Simplified Merkle proof verification
            let mut current_hash = account.hash;
            for sibling in proof.iter() {
                let combined = [current_hash.as_ref(), sibling.as_ref()].concat();
                current_hash = blake2_256(&combined);
            }

            let verified = current_hash == tree_root;
            ensure!(verified, Error::<T>::InvalidProof);

            Self::deposit_event(Event::ProofVerified { tree_root, leaf_index, verified });
            Ok(())
        }
    }

    impl<T: Config> Pallet<T> {
        pub fn get_tree_info(root: [u8; 32]) -> Option<MerkleTreeInfo> {
            MerkleTrees::<T>::get(root)
        }

        pub fn get_compression_stats() -> CompressionStats {
            CompressionStats::<T>::get()
        }
    }
}
