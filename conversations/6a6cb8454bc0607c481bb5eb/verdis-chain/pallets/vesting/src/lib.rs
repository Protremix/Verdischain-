//! # Verdis Vesting Pallet
//!
//! Protocol-level vesting enforcement with:
//! - Schedule-based token locks (30/60-day vesting for IDO stages)
//! - beforeTransfer hook pattern (Ethereum-style)
//! - Transfer blocking for vested tokens
//! - Cliff and linear vesting schedules
//! - Integration with DEX swaps, staking, and transfers

#![cfg_attr(not(feature = "std"), no_std)]

use codec::{Decode, Encode, MaxEncodedLen};
use frame_support::{
    dispatch::DispatchResult,
    ensure,
    pallet_prelude::*,
    traits::{Currency, Get, ReservableCurrency, tokens::ExistenceRequirement},
    PalletId, DefaultNoBound,
};
use scale_info::TypeInfo;
use frame_system::pallet_prelude::*;
use sp_runtime::traits::Saturating;
use sp_arithmetic::traits::SaturatedConversion;
use sp_std::prelude::*;

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use super::*;

    type BalanceOf<T> = <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    // === Vesting Schedule ===

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo)]
    pub struct VestingSchedule<Balance> {
        pub label: BoundedVec<u8, ConstU32<64>>,
        pub total_amount: Balance,
        pub vesting_days: u32,
        pub cliff_days: u32,
    }

    // === User Vesting Entry ===

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo)]
    pub struct UserVestingEntry<Balance, BlockNumber> {
        pub schedule: BoundedVec<u8, ConstU32<64>>,
        pub total_amount: Balance,
        pub released: Balance,
        pub start_block: BlockNumber,
        pub vested: Balance,
    }

    // === Storage ===

    #[pallet::storage]
    #[pallet::getter(fn schedules)]
    pub type Schedules<T: Config> =
        StorageMap<_, Blake2_128Concat, BoundedVec<u8, ConstU32<64>>, VestingSchedule<BalanceOf<T>>>;

    #[pallet::storage]
    #[pallet::getter(fn user_vesting)]
    pub type UserVestings<T: Config> =
        StorageMap<_, Blake2_128Concat, T::AccountId, BoundedVec<UserVestingEntry<BalanceOf<T>, BlockNumberFor<T>>, ConstU32<16>>>;

    #[pallet::storage]
    #[pallet::getter(fn locked_balances)]
    pub type LockedBalances<T: Config> =
        StorageMap<_, Blake2_128Concat, T::AccountId, BalanceOf<T>, ValueQuery>;

    // === Events ===

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        VestingScheduleAdded { label: Vec<u8>, amount: BalanceOf<T>, vesting_days: u32, cliff_days: u32 },
        VestingAssigned { who: T::AccountId, schedule: Vec<u8>, amount: BalanceOf<T> },
        VestingReleased { who: T::AccountId, amount: BalanceOf<T> },
        TransferBlocked { from: T::AccountId, amount: BalanceOf<T>, reason: Vec<u8> },
    }

    // === Errors ===

    #[pallet::error]
    pub enum Error<T> {
        ScheduleNotFound,
        AlreadyVesting,
        NoVestingForAccount,
        VestingNotStarted,
        NothingToRelease,
        InsufficientUnlocked,
        TransferLocked,
        LabelTooLong,
        MaxVestingSchedules,
    }

    // === Config ===

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        type Currency: ReservableCurrency<Self::AccountId>;
        #[pallet::constant]
        type PalletId: Get<PalletId>;
        type WeightInfo: WeightInfo;
    }

    // === Genesis ===

    #[pallet::genesis_config]
    #[derive(DefaultNoBound)]
    pub struct GenesisConfig<T: Config> {
        pub vesting_schedules: Vec<(Vec<u8>, BalanceOf<T>, u32, u32)>,
    }

    #[pallet::genesis_build]
    impl<T: Config> BuildGenesisConfig for GenesisConfig<T> {
        fn build(&self) {
            for (label, amount, vesting_days, cliff_days) in &self.vesting_schedules {
                let label_bv: BoundedVec<u8, ConstU32<64>> = label.clone().try_into().unwrap_or_default();
                let schedule = VestingSchedule {
                    label: label_bv.clone(),
                    total_amount: *amount,
                    vesting_days: *vesting_days,
                    cliff_days: *cliff_days,
                };
                Schedules::<T>::insert(label_bv, schedule);
            }
        }
    }

    // === Extrinsics ===

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Assign vesting to an account (governance only)
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::assign_vesting())]
        pub fn assign_vesting(
            origin: OriginFor<T>,
            who: T::AccountId,
            schedule_label: Vec<u8>,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            ensure_root(origin)?;

            let label_bv: BoundedVec<u8, ConstU32<64>> = schedule_label.clone().try_into().map_err(|_| Error::<T>::LabelTooLong)?;
            let schedule = Schedules::<T>::get(&label_bv)
                .ok_or(Error::<T>::ScheduleNotFound)?;

            let current_block = frame_system::Pallet::<T>::block_number();

            let entry = UserVestingEntry {
                schedule: label_bv.clone(),
                total_amount: amount,
                released: BalanceOf::<T>::zero(),
                start_block: current_block,
                vested: BalanceOf::<T>::zero(),
            };

            UserVestings::<T>::mutate(&who, |v| {
                let vestings = v.get_or_insert_with(|| BoundedVec::default());
                vestings.try_push(entry).map_err(|_| Error::<T>::MaxVestingSchedules).ok();
            });

            LockedBalances::<T>::mutate(&who, |l| *l = l.saturating_add(amount));

            Self::deposit_event(Event::VestingAssigned {
                who,
                schedule: schedule_label,
                amount,
            });
            Ok(())
        }

        /// Release vested tokens (called by the vested account)
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::release_vested())]
        pub fn release_vested(origin: OriginFor<T>) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let vesting = UserVestings::<T>::get(&who).ok_or(Error::<T>::NoVestingForAccount)?;
            let current_block = frame_system::Pallet::<T>::block_number();
            let block_time_ms = 5000u64; // 5 second blocks
            let blocks_per_day = (86_400_000 / block_time_ms) as u32;

            let mut total_releasable = BalanceOf::<T>::zero();

            for v in &vesting {
                let elapsed_blocks: u32 = current_block.saturating_sub(v.start_block)
                    .try_into().unwrap_or(0);
                let elapsed_days = elapsed_blocks / blocks_per_day;

                let schedule = Schedules::<T>::get(&v.schedule)
                    .ok_or(Error::<T>::ScheduleNotFound)?;

                if elapsed_days < schedule.cliff_days {
                    continue;
                }

                let vested = if elapsed_days >= schedule.vesting_days {
                    v.total_amount
                } else {
                    v.total_amount.saturating_mul(elapsed_days.saturated_into())
                        / schedule.vesting_days.saturated_into()
                };

                let releasable = vested.saturating_sub(v.released);
                total_releasable = total_releasable.saturating_add(releasable);
            }

            ensure!(total_releasable > BalanceOf::<T>::zero(), Error::<T>::NothingToRelease);

            // Update vesting records
            UserVestings::<T>::mutate(&who, |vests| {
                if let Some(vests) = vests {
                    for v in vests.iter_mut() {
                        let elapsed_blocks: u32 = current_block.saturating_sub(v.start_block)
                            .try_into().unwrap_or(0);
                        let elapsed_days = elapsed_blocks / blocks_per_day;
                        let schedule = Schedules::<T>::get(&v.schedule);
                        if let Some(s) = schedule {
                            if elapsed_days >= s.cliff_days {
                                let vested = if elapsed_days >= s.vesting_days {
                                    v.total_amount
                                } else {
                                    v.total_amount.saturating_mul(elapsed_days.saturated_into())
                                        / s.vesting_days.saturated_into()
                                };
                                v.vested = vested;
                                let releasable = vested.saturating_sub(v.released);
                                v.released = v.released.saturating_add(releasable);
                            }
                        }
                    }
                }
            });

            LockedBalances::<T>::mutate(&who, |l| *l = l.saturating_sub(total_releasable));

            Self::deposit_event(Event::VestingReleased {
                who,
                amount: total_releasable,
            });
            Ok(())
        }

        /// Check if a transfer should be blocked by vesting (called before transfer)
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::check_transfer())]
        pub fn check_transfer(
            origin: OriginFor<T>,
            from: T::AccountId,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            let _ = ensure_signed(origin)?;

            let locked = LockedBalances::<T>::get(&from);
            let free = T::Currency::free_balance(&from).saturating_sub(locked);

            if free < amount {
                Self::deposit_event(Event::TransferBlocked {
                    from,
                    amount,
                    reason: b"Vesting lock active".to_vec(),
                });
                return Err(Error::<T>::TransferLocked.into());
            }

            Ok(())
        }
    }

    // === beforeTransfer Hook ===
    impl<T: Config> Pallet<T> {
        /// Called before any token transfer to enforce vesting locks
        pub fn before_transfer(
            from: &T::AccountId,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            let locked = LockedBalances::<T>::get(from);
            let free = T::Currency::free_balance(from).saturating_sub(locked);

            if free < amount {
                return Err(Error::<T>::TransferLocked.into());
            }
            Ok(())
        }

        /// Get the locked balance for an account
        pub fn get_locked_balance(who: &T::AccountId) -> BalanceOf<T> {
            LockedBalances::<T>::get(who)
        }

        /// Get the unlocked (free) balance for an account
        pub fn get_unlocked_balance(who: &T::AccountId) -> BalanceOf<T> {
            T::Currency::free_balance(who).saturating_sub(LockedBalances::<T>::get(who))
        }
    }

    // === WeightInfo ===
    pub trait WeightInfo {
        fn assign_vesting() -> Weight;
        fn release_vested() -> Weight;
        fn check_transfer() -> Weight;
    }

    pub struct SubstrateWeight<T>(PhantomData<T>);
    impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
        fn assign_vesting() -> Weight { Weight::from_parts(80_000_000, 0) }
        fn release_vested() -> Weight { Weight::from_parts(100_000_000, 0) }
        fn check_transfer() -> Weight { Weight::from_parts(30_000_000, 0) }
    }
}
