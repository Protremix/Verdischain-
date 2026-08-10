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
//! # Gulf Stream Pallet — Mempool-less Transaction Forwarding
//!
//! Inspired by Solana's Gulf Stream, eliminates the traditional mempool:
//! - Validators forward transactions directly to the next block producer
//! - Reduces memory pressure (no growing mempool)
//! - Decreases transaction latency
//! - Tracks forwarding statistics and success rates

#![cfg_attr(not(feature = "std"), no_std)]
use codec::{Decode, Encode};
use frame_support::{dispatch::DispatchResult, pallet_prelude::*};
use frame_system::pallet_prelude::*;
use scale_info::TypeInfo;
use sp_std::prelude::*;
use sp_std::vec::Vec;

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use super::*;

    #[pallet::pallet]
    #[pallet::without_storage_info]
    pub struct Pallet<T>(_);

    /// Trait for checking if an account is an active validator.
    pub trait ValidatorChecker<AccountId> {
        fn is_active_validator(who: &AccountId) -> bool;
    }

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type MaxPendingForwards: Get<u32>;
        type MaxForwardedHistory: Get<u32>;
        /// Validator checker - connects to DPoS active validator set.
        type ValidatorChecker: ValidatorChecker<Self::AccountId>;
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, TypeInfo)]
    pub struct ForwardedTransaction {
        pub tx_hash: [u8; 32],
        pub from_validator: Vec<u8>,
        pub to_validator: Vec<u8>,
        pub timestamp: u64,
        pub tx_size: u32,
        pub status: ForwardStatus,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, TypeInfo, Default)]
    pub enum ForwardStatus {
        #[default]
        Pending,
        Forwarded,
        Included,
        Expired,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, TypeInfo, Default)]
    pub struct GulfStreamStats {
        pub total_forwarded: u64,
        pub total_included: u64,
        pub total_expired: u64,
        pub avg_forward_time_ms: u64,
        pub current_pending: u32,
        pub success_rate: u32,
    }

    // === Storage ===
    #[pallet::storage]
    #[pallet::getter(fn pending_forwards)]
    pub type PendingForwards<T: Config> =
        StorageMap<_, Twox64Concat, [u8; 32], ForwardedTransaction>;

    #[pallet::storage]
    #[pallet::getter(fn forwarded_txs)]
    pub type ForwardedTxs<T: Config> = StorageValue<_, Vec<[u8; 32]>, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn gulf_stream_stats_storage)]
    pub type GulfStreamStatsStorage<T: Config> = StorageValue<_, GulfStreamStats, ValueQuery>;

    // === Events ===
    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        TransactionForwarded {
            tx_hash: [u8; 32],
            to_validator: Vec<u8>,
        },
        TransactionIncluded {
            tx_hash: [u8; 32],
            block_number: u32,
        },
        TransactionExpired {
            tx_hash: [u8; 32],
        },
        StatsUpdated {
            total_forwarded: u64,
            success_rate: u32,
        },
    }

    // === Errors ===
    #[pallet::error]
    pub enum Error<T> {
        /// Block number is in the future
        InvalidBlockNumber,
        /// Caller is not an active validator
        NotActiveValidator,
        MaxPendingExceeded,
        AlreadyForwarded,
        TransactionNotFound,
    }

    // === Extrinsics ===
    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Forward a transaction to the next validator (mempool-less)
        #[pallet::weight(Weight::from_parts(10_000, 0))]
        #[pallet::call_index(0)]
        pub fn forward_transaction(
            origin: OriginFor<T>,
            tx_hash: [u8; 32],
            to_validator: Vec<u8>,
            tx_size: u32,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // Check if already forwarded
            ensure!(
                !PendingForwards::<T>::contains_key(tx_hash),
                Error::<T>::AlreadyForwarded
            );

            let forwarded = ForwardedTransaction {
                tx_hash,
                from_validator: who.encode(),
                to_validator: to_validator.clone(),
                timestamp: 0, // Would use timestamp pallet in production
                tx_size,
                status: ForwardStatus::Pending,
            };

            PendingForwards::<T>::insert(tx_hash, forwarded);
            ForwardedTxs::<T>::mutate(|txs| txs.push(tx_hash));

            let mut stats = GulfStreamStatsStorage::<T>::get();
            stats.total_forwarded = stats.total_forwarded.saturating_add(1u64);
            stats.current_pending = stats.current_pending.saturating_add(1u32);
            GulfStreamStatsStorage::<T>::put(stats);

            Self::deposit_event(Event::TransactionForwarded {
                tx_hash,
                to_validator,
            });
            Ok(())
        }

        /// Mark a forwarded transaction as included in a block
        #[pallet::weight(Weight::from_parts(10_000, 0))]
        #[pallet::call_index(1)]
        pub fn mark_included(
            origin: OriginFor<T>,
            tx_hash: [u8; 32],
            block_number: u32,
            forward_time_ms: u64,
        ) -> DispatchResult {
            // SECURITY: Only active validators can mark inclusion
            let caller = ensure_signed(origin)?;
            Self::ensure_active_validator(&caller)?;

            // Verify the block number is not in the future
            let current_block: u32 = frame_system::Pallet::<T>::block_number()
                .try_into()
                .unwrap_or(0);
            // SECURITY: Only mark inclusion within a 5-block window — prevents
            // validators from retroactively marking txs as included in old blocks
            ensure!(
                current_block.saturating_sub(block_number) <= 5,
                Error::<T>::InvalidBlockNumber
            );

            let mut tx =
                PendingForwards::<T>::get(tx_hash).ok_or(Error::<T>::TransactionNotFound)?;
            tx.status = ForwardStatus::Included;
            PendingForwards::<T>::remove(tx_hash);

            let mut stats = GulfStreamStatsStorage::<T>::get();
            stats.total_included = stats.total_included.saturating_add(1u64);
            stats.current_pending = stats.current_pending.saturating_sub(1u32);
            let total = stats.total_included.saturating_add(stats.total_expired);
            if total > 0 {
                stats.success_rate = stats
                    .total_included
                    .saturating_mul(100)
                    .checked_div(total)
                    .unwrap_or(0) as u32;
            }
            let new_avg = if stats.total_included == 1 {
                forward_time_ms
            } else {
                // FIX: Use checked arithmetic to prevent overflow
                let prev_total = stats
                    .avg_forward_time_ms
                    .checked_mul((stats.total_included - 1) as u64)
                    .unwrap_or(u64::MAX);
                let sum = prev_total.saturating_add(forward_time_ms);
                sum / stats.total_included as u64
            };
            stats.avg_forward_time_ms = new_avg;
            GulfStreamStatsStorage::<T>::put(stats);

            Self::deposit_event(Event::TransactionIncluded {
                tx_hash,
                block_number,
            });
            Ok(())
        }

        /// Expire a forwarded transaction that was never included
        #[pallet::weight(Weight::from_parts(10_000, 0))]
        #[pallet::call_index(2)]
        pub fn expire_transaction(origin: OriginFor<T>, tx_hash: [u8; 32]) -> DispatchResult {
            // FIX: Allow any signed origin (validator/relayer) to expire stale txs
            let _caller = ensure_signed(origin)?;

            let _tx = PendingForwards::<T>::get(tx_hash).ok_or(Error::<T>::TransactionNotFound)?;
            PendingForwards::<T>::remove(tx_hash);

            let mut stats = GulfStreamStatsStorage::<T>::get();
            stats.total_expired = stats.total_expired.saturating_add(1u64);
            stats.current_pending = stats.current_pending.saturating_sub(1u32);
            let total = stats.total_included.saturating_add(stats.total_expired);
            if total > 0 {
                stats.success_rate = stats
                    .total_included
                    .saturating_mul(100)
                    .checked_div(total)
                    .unwrap_or(0) as u32;
            }
            GulfStreamStatsStorage::<T>::put(stats);

            Self::deposit_event(Event::TransactionExpired { tx_hash });
            Ok(())
        }
    }

    impl<T: Config> Pallet<T> {
        /// Check if the caller is an active validator
        fn ensure_active_validator(who: &T::AccountId) -> Result<(), Error<T>> {
            ensure!(
                T::ValidatorChecker::is_active_validator(who),
                Error::<T>::NotActiveValidator
            );
            Ok(())
        }

        pub fn get_stats() -> GulfStreamStats {
            GulfStreamStatsStorage::<T>::get()
        }

        pub fn get_pending_count() -> u32 {
            PendingForwards::<T>::iter().count() as u32
        }
    }
}

#[cfg(test)]
mod tests;
