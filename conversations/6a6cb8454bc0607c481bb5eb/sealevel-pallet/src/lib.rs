//! # Sealevel Pallet — Parallel Smart Contract Execution
//!
//! Inspired by Solana's Sealevel, this pallet provides:
//! - Parallel execution of non-conflicting transactions
//! - Read-write lock tracking for account access
//! - Batch execution with conflict detection
//! - Compute unit tracking per transaction
//! - Multi-threaded execution scheduling (conceptual, not OS-level)

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

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type MaxComputeUnits: Get<u64>;
        type MaxParallelBatches: Get<u32>;
    }

    // === Types ===
    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo)]
    pub enum AccessMode {
        Read,
        Write,
        ReadWrite,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo)]
    pub struct AccountAccess {
        pub account: Vec<u8>,
        pub mode: AccessMode,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo)]
    pub struct ExecutionBatch {
        pub batch_id: u32,
        pub tx_indices: Vec<u32>,
        pub is_parallel: bool,
        pub compute_units_used: u64,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo)]
    pub struct SealevelStats {
        pub total_batches: u64,
        pub parallel_batches: u64,
        pub sequential_batches: u64,
        pub total_transactions_executed: u64,
        pub avg_compute_units_per_tx: u64,
        pub conflicts_detected: u64,
        pub parallelization_rate: u32,
    }

    // === Storage ===
    #[pallet::storage]
    #[pallet::getter(fn batch_registry)]
    pub type BatchRegistry<T: Config> = StorageMap<_, Twox64Concat, u32, ExecutionBatch>;

    #[pallet::storage]
    #[pallet::getter(fn sealevel_stats)]
    pub type SealevelStats<T: Config> = StorageValue<_, SealevelStats, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn next_batch_id)]
    pub type NextBatchId<T: Config> = StorageValue<_, u32, ValueQuery>;

    // === Events ===
    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        BatchCreated { batch_id: u32, tx_count: u32, parallel: bool },
        BatchExecuted { batch_id: u32, compute_units: u64, parallel: bool },
        ConflictDetected { batch_id: u32, tx_index_1: u32, tx_index_2: u32, account: Vec<u8> },
        ComputeBudgetExceeded { batch_id: u32, tx_index: u32, units: u64 },
    }

    // === Errors ===
    #[pallet::error]
    pub enum Error<T> {
        BatchNotFound,
        ComputeBudgetExceeded,
        MaxBatchSizeExceeded,
    }

    // === Extrinsics ===
    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Create an execution batch with parallelism analysis
        #[pallet::call_index(0)]
        pub fn create_batch(
            origin: OriginFor<T>,
            tx_count: u32,
            account_accesses: Vec<AccountAccess>,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            ensure!(tx_count <= T::MaxParallelBatches::get(), Error::<T>::MaxBatchSizeExceeded);

            let batch_id = NextBatchId::<T>::get();
            NextBatchId::<T>::put(batch_id + 1);

            // Analyze conflicts to determine if batch can be parallel
            let is_parallel = Self::analyze_conflicts(&account_accesses);

            let batch = ExecutionBatch {
                batch_id,
                tx_indices: (0..tx_count).collect(),
                is_parallel,
                compute_units_used: 0,
            };

            BatchRegistry::<T>::insert(batch_id, batch);

            let stats = SealevelStats::<T>::get();
            let parallel_batches = if is_parallel { stats.parallel_batches + 1 } else { stats.parallel_batches };
            let sequential_batches = if !is_parallel { stats.sequential_batches + 1 } else { stats.sequential_batches };
            let parallelization_rate = ((parallel_batches * 100) / (parallel_batches + sequential_batches).max(1)) as u32;

            SealevelStats::<T>::put(SealevelStats {
                total_batches: stats.total_batches + 1,
                parallel_batches,
                sequential_batches,
                total_transactions_executed: stats.total_transactions_executed,
                avg_compute_units_per_tx: stats.avg_compute_units_per_tx,
                conflicts_detected: stats.conflicts_detected,
                parallelization_rate,
            });

            Self::deposit_event(Event::BatchCreated { batch_id, tx_count, parallel: is_parallel });
            Ok(())
        }

        /// Report execution results for a batch
        #[pallet::call_index(1)]
        pub fn report_execution(
            origin: OriginFor<T>,
            batch_id: u32,
            compute_units_used: u64,
            tx_count: u32,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;
            ensure!(compute_units_used <= T::MaxComputeUnits::get(), Error::<T>::ComputeBudgetExceeded);

            let batch = BatchRegistry::<T>::get(batch_id).ok_or(Error::<T>::BatchNotFound)?;
            let updated_batch = ExecutionBatch {
                batch_id,
                tx_indices: batch.tx_indices,
                is_parallel: batch.is_parallel,
                compute_units_used,
            };
            BatchRegistry::<T>::insert(batch_id, updated_batch);

            let stats = SealevelStats::<T>::get();
            let new_avg = if stats.total_transactions_executed == 0 {
                compute_units_used / tx_count.max(1) as u64
            } else {
                (stats.avg_compute_units_per_tx * stats.total_transactions_executed + compute_units_used)
                    / (stats.total_transactions_executed + tx_count as u64)
            };
            SealevelStats::<T>::put(SealevelStats {
                total_batches: stats.total_batches,
                parallel_batches: stats.parallel_batches,
                sequential_batches: stats.sequential_batches,
                total_transactions_executed: stats.total_transactions_executed + tx_count as u64,
                avg_compute_units_per_tx: new_avg,
                conflicts_detected: stats.conflicts_detected,
                parallelization_rate: stats.parallelization_rate,
            });

            Self::deposit_event(Event::BatchExecuted { batch_id, compute_units, parallel: batch.is_parallel });
            Ok(())
        }

        /// Report a conflict (for analysis and optimization)
        #[pallet::call_index(2)]
        pub fn report_conflict(
            origin: OriginFor<T>,
            batch_id: u32,
            tx_index_1: u32,
            tx_index_2: u32,
            conflicting_account: Vec<u8>,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;

            let stats = SealevelStats::<T>::get();
            SealevelStats::<T>::put(SealevelStats {
                total_batches: stats.total_batches,
                parallel_batches: stats.parallel_batches,
                sequential_batches: stats.sequential_batches,
                total_transactions_executed: stats.total_transactions_executed,
                avg_compute_units_per_tx: stats.avg_compute_units_per_tx,
                conflicts_detected: stats.conflicts_detected + 1,
                parallelization_rate: stats.parallelization_rate,
            });

            Self::deposit_event(Event::ConflictDetected { batch_id, tx_index_1, tx_index_2, account: conflicting_account });
            Ok(())
        }
    }

    // === Helper Functions ===
    impl<T: Config> Pallet<T> {
        /// Analyze if transactions can be parallelized based on account access patterns
        fn analyze_conflicts(accesses: &[AccountAccess]) -> bool {
            // If any write-write or write-read conflicts exist, cannot parallelize
            for i in 0..accesses.len() {
                for j in (i+1)..accesses.len() {
                    if accesses[i].account == accesses[j].account {
                        let i_writes = matches!(accesses[i].mode, AccessMode::Write | AccessMode::ReadWrite);
                        let j_writes = matches!(accesses[j].mode, AccessMode::Write | AccessMode::ReadWrite);
                        if i_writes || j_writes {
                            return false; // Conflict: cannot parallelize
                        }
                    }
                }
            }
            true // No conflicts: can parallelize
        }

        pub fn get_stats() -> SealevelStats {
            SealevelStats::<T>::get()
        }

        pub fn get_batch(batch_id: u32) -> Option<ExecutionBatch> {
            BatchRegistry::<T>::get(batch_id)
        }
    }
}
