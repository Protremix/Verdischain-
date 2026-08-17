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
    pub trait Config: frame_system::Config + pallet_timestamp::Config {
        type MaxPendingForwards: Get<u32>;
        type MaxForwardedHistory: Get<u32>;
        type MaxForwardTimeMs: Get<u64>;
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
        AlreadyProcessed,
        InvalidForwardTime,
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
            // FIX H16.3: Restrict to active validators only
            let caller = ensure_signed(origin)?;
            Self::ensure_active_validator(&caller)?;

            // FIX H16.1: Enforce MaxPendingForwards bound
            let pending_count = PendingForwards::<T>::iter().count();
            ensure!(
                pending_count < T::MaxPendingForwards::get() as usize,
                Error::<T>::MaxPendingExceeded
            );

            // Check if already forwarded
            ensure!(
                !PendingForwards::<T>::contains_key(tx_hash),
                Error::<T>::AlreadyForwarded
            );

            // FIX H16.5: Use pallet_timestamp instead of hardcoded 0
            let timestamp: u64 = pallet_timestamp::Pallet::<T>::get().try_into().unwrap_or(0u64);

            let forwarded = ForwardedTransaction {
                tx_hash,
                from_validator: caller.encode(),
                to_validator: to_validator.clone(),
                timestamp,
                tx_size,
                status: ForwardStatus::Pending,
            };

            PendingForwards::<T>::insert(tx_hash, forwarded);

            // FIX H16.2: Bound ForwardedTxs Vec with pruning
            let mut forwarded_txs = ForwardedTxs::<T>::get();
            let max_history = T::MaxForwardedHistory::get() as usize;
            if forwarded_txs.len() >= max_history {
                let excess = forwarded_txs.len() + 1 - max_history;
                forwarded_txs.drain(0..excess);
            }
            forwarded_txs.push(tx_hash);
            ForwardedTxs::<T>::put(forwarded_txs);

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
                block_number <= current_block && current_block - block_number <= 5,
                Error::<T>::InvalidBlockNumber
            );

            let tx = PendingForwards::<T>::get(tx_hash).ok_or(Error::<T>::TransactionNotFound)?;
            // SECURITY: Verify the transaction is still pending (not already processed)
            ensure!(
                tx.status == ForwardStatus::Pending,
                Error::<T>::AlreadyProcessed
            );
            // SECURITY: Bound forward_time_ms to prevent stat manipulation
            ensure!(
                forward_time_ms <= T::MaxForwardTimeMs::get(),
                Error::<T>::InvalidForwardTime
            );
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
            let tf = stats.total_forwarded;
            let sr = stats.success_rate;
            GulfStreamStatsStorage::<T>::put(stats);
            Self::deposit_event(Event::StatsUpdated {
                total_forwarded: tf,
                success_rate: sr,
            });

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
            // FIX H16.4: Restrict to active validators only
            let caller = ensure_signed(origin)?;
            Self::ensure_active_validator(&caller)?;

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

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;
