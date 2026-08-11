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
    clippy::manual_checked_ops,
    clippy::needless_borrows_for_generic_args
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
        type MaxComputeUnits: Get<u64>;
        type MaxParallelBatches: Get<u32>;
    }
    #[pallet::storage]
    pub type SealevelTotalBatches<T> = StorageValue<_, u64, ValueQuery>;
    #[pallet::storage]
    pub type SealevelParallelBatches<T> = StorageValue<_, u64, ValueQuery>;
    #[pallet::storage]
    pub type SealevelSequentialBatches<T> = StorageValue<_, u64, ValueQuery>;
    #[pallet::storage]
    pub type SealevelTotalTxs<T> = StorageValue<_, u64, ValueQuery>;
    #[pallet::storage]
    pub type SealevelAvgComputeUnits<T> = StorageValue<_, u64, ValueQuery>;
    #[pallet::storage]
    pub type SealevelConflicts<T> = StorageValue<_, u64, ValueQuery>;
    #[pallet::storage]
    pub type SealevelParallelizationRate<T> = StorageValue<_, u32, ValueQuery>;
    #[pallet::storage]
    pub type NextBatchId<T> = StorageValue<_, u32, ValueQuery>;
    #[pallet::storage]
    pub type BatchParallel<T> = StorageMap<_, Twox64Concat, u32, bool, ValueQuery>;
    #[pallet::storage]
    pub type BatchComputeUnits<T> = StorageMap<_, Twox64Concat, u32, u64, ValueQuery>;
    #[pallet::event]
    #[pallet::generate_deposit(fn deposit_event)]
    pub enum Event<T: Config> {
        BatchCreated {
            batch_id: u32,
            tx_count: u32,
            parallel: bool,
        },
        BatchExecuted {
            batch_id: u32,
            compute_units: u64,
            parallel: bool,
        },
        ConflictDetected {
            batch_id: u32,
            tx1: u32,
            tx2: u32,
        },
    }
    #[pallet::error]
    pub enum Error<T> {
        BatchNotFound,
        ComputeBudgetExceeded,
        MaxBatchSizeExceeded,
    }
    #[pallet::call]
    impl<T: Config> Pallet<T> {
        #[pallet::weight(0)]
        #[pallet::call_index(0)]
        pub fn create_batch(
            origin: OriginFor<T>,
            tx_count: u32,
            has_conflicts: bool,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            ensure!(
                tx_count <= T::MaxParallelBatches::get(),
                Error::<T>::MaxBatchSizeExceeded
            );
            let batch_id = NextBatchId::<T>::get();
            NextBatchId::<T>::mutate(|b| *b += 1);
            let parallel = !has_conflicts;
            BatchParallel::<T>::insert(batch_id, parallel);
            SealevelTotalBatches::<T>::mutate(|b| *b += 1);
            if parallel {
                SealevelParallelBatches::<T>::mutate(|b| *b += 1);
            } else {
                SealevelSequentialBatches::<T>::mutate(|b| *b += 1);
            }
            let total = SealevelTotalBatches::<T>::get();
            let parallel_count = SealevelParallelBatches::<T>::get();
            if total > 0 {
                SealevelParallelizationRate::<T>::put((parallel_count * 100 / total) as u32);
            }
            Self::deposit_event(Event::BatchCreated {
                batch_id,
                tx_count,
                parallel,
            });
            Ok(())
        }
        #[pallet::weight(0)]
        #[pallet::call_index(1)]
        pub fn report_execution(
            origin: OriginFor<T>,
            batch_id: u32,
            compute_units: u64,
            tx_count: u32,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            ensure!(
                compute_units <= T::MaxComputeUnits::get(),
                Error::<T>::ComputeBudgetExceeded
            );
            let parallel = BatchParallel::<T>::get(batch_id);
            BatchComputeUnits::<T>::insert(batch_id, compute_units);
            SealevelTotalTxs::<T>::mutate(|t| *t += tx_count as u64);
            let total_txs = SealevelTotalTxs::<T>::get();
            if total_txs > 0 {
                let avg = (SealevelAvgComputeUnits::<T>::get() * (total_txs - tx_count as u64)
                    + compute_units)
                    / total_txs;
                SealevelAvgComputeUnits::<T>::put(avg);
            }
            Self::deposit_event(Event::BatchExecuted {
                batch_id,
                compute_units,
                parallel,
            });
            Ok(())
        }
        #[pallet::weight(0)]
        #[pallet::call_index(2)]
        pub fn report_conflict(
            origin: OriginFor<T>,
            batch_id: u32,
            tx1: u32,
            tx2: u32,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            SealevelConflicts::<T>::mutate(|c| *c += 1);
            Self::deposit_event(Event::ConflictDetected { batch_id, tx1, tx2 });
            Ok(())
        }
    }
}

#[cfg(test)]
mod tests;

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;
