//! # Verdis Vesting Pallet
//!
//! Protocol-level vesting enforcement with:
//! - Schedule-based token locks (30/60-day vesting for IDO stages)
//! - Native Substrate balance locks via LockableCurrency
//! - Cliff and linear vesting schedules
//! - Integration with DEX swaps, staking, and transfers

#![cfg_attr(not(feature = "std"), no_std)]
use codec::{Decode, Encode, MaxEncodedLen};
use frame_support::{
    dispatch::DispatchResult,
    ensure,
    pallet_prelude::*,
    traits::{tokens::WithdrawReasons, Currency, Get, LockableCurrency, ReservableCurrency},
    DefaultNoBound, PalletId,
};
use frame_system::pallet_prelude::*;
use scale_info::TypeInfo;
use sp_arithmetic::traits::SaturatedConversion;
use sp_runtime::traits::Saturating;

use sp_std::prelude::*;

pub use pallet::*;
pub mod weights;
pub use weights::SubstrateWeight;

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;

#[frame_support::pallet]
pub mod pallet {
    use super::*;

    type BalanceOf<T> =
        <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

    /// Lock identifier for vesting locks — must be unique 8 bytes
    pub const VESTING_LOCK_ID: [u8; 8] = *b"v/vsting";

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
    pub type Schedules<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        BoundedVec<u8, ConstU32<64>>,
        VestingSchedule<BalanceOf<T>>,
    >;

    #[pallet::storage]
    #[pallet::getter(fn user_vesting)]
    pub type UserVestings<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        BoundedVec<UserVestingEntry<BalanceOf<T>, BlockNumberFor<T>>, T::MaxSchedulesPerAccount>,
    >;

    #[pallet::storage]
    #[pallet::getter(fn locked_balances)]
    pub type LockedBalances<T: Config> =
        StorageMap<_, Blake2_128Concat, T::AccountId, BalanceOf<T>, ValueQuery>;

    // === Events ===

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        VestingScheduleAdded {
            label: Vec<u8>,
            amount: BalanceOf<T>,
            vesting_days: u32,
            cliff_days: u32,
        },
        VestingAssigned {
            who: T::AccountId,
            schedule: Vec<u8>,
            amount: BalanceOf<T>,
        },
        VestingReleased {
            who: T::AccountId,
            amount: BalanceOf<T>,
        },
        LockUpdated {
            who: T::AccountId,
            locked: BalanceOf<T>,
        },
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
        ScheduleAlreadyExists,
        Overflow,
        Underflow,
    }

    // === Config ===

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        type Currency: ReservableCurrency<Self::AccountId> + LockableCurrency<Self::AccountId>;
        #[pallet::constant]
        type PalletId: Get<PalletId>;
        type WeightInfo: WeightInfo;
        /// Maximum number of vesting schedules per account
        #[pallet::constant]
        type MaxSchedulesPerAccount: Get<u32>;
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
                let label_bv: BoundedVec<u8, ConstU32<64>> =
                    label.clone().try_into().unwrap_or_default();
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
        /// Add a vesting schedule (governance only)
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::add_schedule(0))]
        pub fn add_schedule(
            origin: OriginFor<T>,
            label: Vec<u8>,
            total_amount: BalanceOf<T>,
            vesting_days: u32,
            cliff_days: u32,
        ) -> DispatchResult {
            ensure_root(origin)?;

            let label_bv: BoundedVec<u8, ConstU32<64>> = label
                .clone()
                .try_into()
                .map_err(|_| Error::<T>::LabelTooLong)?;

            ensure!(
                !Schedules::<T>::contains_key(&label_bv),
                Error::<T>::ScheduleAlreadyExists
            );
            ensure!(vesting_days > 0, Error::<T>::VestingNotStarted);
            ensure!(cliff_days <= vesting_days, Error::<T>::VestingNotStarted);

            let schedule = VestingSchedule {
                label: label_bv.clone(),
                total_amount,
                vesting_days,
                cliff_days,
            };
            Schedules::<T>::insert(label_bv, schedule);

            Self::deposit_event(Event::VestingScheduleAdded {
                label,
                amount: total_amount,
                vesting_days,
                cliff_days,
            });
            Ok(())
        }

        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::assign_vesting(0))]
        pub fn assign_vesting(
            origin: OriginFor<T>,
            who: T::AccountId,
            schedule_label: Vec<u8>,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            ensure_root(origin)?;
            Self::do_assign_vesting(who, schedule_label, amount)
        }

        /// Release vested tokens (called by the vested account)
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::release_vested(0))]
        pub fn release_vested(origin: OriginFor<T>) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let vesting = UserVestings::<T>::get(&who).ok_or(Error::<T>::NoVestingForAccount)?;
            let current_block = frame_system::Pallet::<T>::block_number();
            let block_time_ms = 5000u64; // 5 second blocks
            let blocks_per_day = (86_400_000 / block_time_ms) as u32;

            let mut total_releasable = BalanceOf::<T>::zero();

            for v in &vesting {
                let elapsed_blocks: u32 = current_block
                    .saturating_sub(v.start_block)
                    .try_into()
                    .unwrap_or(0);
                let elapsed_days = elapsed_blocks / blocks_per_day;

                let schedule =
                    Schedules::<T>::get(&v.schedule).ok_or(Error::<T>::ScheduleNotFound)?;

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

            ensure!(
                total_releasable > BalanceOf::<T>::zero(),
                Error::<T>::NothingToRelease
            );

            // Update vesting records
            UserVestings::<T>::mutate(&who, |vests| {
                if let Some(vests) = vests {
                    for v in vests.iter_mut() {
                        let elapsed_blocks: u32 = current_block
                            .saturating_sub(v.start_block)
                            .try_into()
                            .unwrap_or(0);
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

            // Reduce locked balance tracking
            let new_locked = LockedBalances::<T>::get(&who)
                .checked_sub(&total_releasable)
                .ok_or(Error::<T>::Underflow)?;
            LockedBalances::<T>::insert(&who, new_locked);

            // Update or remove the native Substrate lock
            let remaining_locked = LockedBalances::<T>::get(&who);
            if remaining_locked.is_zero() {
                T::Currency::remove_lock(VESTING_LOCK_ID, &who);
            } else {
                T::Currency::set_lock(
                    VESTING_LOCK_ID,
                    &who,
                    remaining_locked,
                    WithdrawReasons::TRANSFER,
                );
            }

            Self::deposit_event(Event::LockUpdated {
                who: who.clone(),
                locked: remaining_locked,
            });
            Self::deposit_event(Event::VestingReleased {
                who,
                amount: total_releasable,
            });
            Ok(())
        }
    }

    // === Utility Functions ===
    impl<T: Config> Pallet<T> {
        /// Assign vesting to an account (governance only)
        /// Internal function to create vesting entry — callable by other pallets (no origin check)
        pub fn do_assign_vesting(
            who: T::AccountId,
            schedule_label: Vec<u8>,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            let label_bv: BoundedVec<u8, ConstU32<64>> = schedule_label
                .clone()
                .try_into()
                .map_err(|_| Error::<T>::LabelTooLong)?;
            let _schedule = Schedules::<T>::get(&label_bv).ok_or(Error::<T>::ScheduleNotFound)?;

            let current_block = frame_system::Pallet::<T>::block_number();

            let entry = UserVestingEntry {
                schedule: label_bv.clone(),
                total_amount: amount,
                released: BalanceOf::<T>::zero(),
                start_block: current_block,
                vested: BalanceOf::<T>::zero(),
            };

            UserVestings::<T>::try_mutate(&who, |maybe_vestings| {
                let vestings = maybe_vestings.get_or_insert_with(|| BoundedVec::default());
                vestings
                    .try_push(entry)
                    .map_err(|_| Error::<T>::MaxVestingSchedules)
            })?;

            let new_locked = LockedBalances::<T>::get(&who)
                .checked_add(&amount)
                .ok_or(Error::<T>::MaxVestingSchedules)?;
            LockedBalances::<T>::insert(&who, new_locked);

            T::Currency::set_lock(VESTING_LOCK_ID, &who, new_locked, WithdrawReasons::TRANSFER);

            Self::deposit_event(Event::LockUpdated {
                who: who.clone(),
                locked: new_locked,
            });
            Self::deposit_event(Event::VestingAssigned {
                who,
                schedule: schedule_label,
                amount,
            });
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
        fn add_schedule(s: u32) -> Weight;
        fn assign_vesting(s: u32) -> Weight;
        fn release_vested(s: u32) -> Weight;
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use frame_support::traits::UnfilteredDispatchable;
    use frame_support::{
        assert_noop, assert_ok, construct_runtime, derive_impl, parameter_types,
        traits::{ConstU128, ConstU32},
    };
    use sp_io::TestExternalities;
    use sp_keyring::Sr25519Keyring;
    use sp_runtime::{traits::IdentityLookup, BuildStorage};

    type Block = frame_system::mocking::MockBlock<Test>;

    construct_runtime!(
        pub enum Test { System: frame_system, Balances: pallet_balances, Vesting: crate }
    );

    #[derive_impl(frame_system::config_preludes::TestDefaultConfig as frame_system::DefaultConfig)]
    impl frame_system::Config for Test {
        type AccountId = sp_core::crypto::AccountId32;
        type Lookup = IdentityLookup<Self::AccountId>;
        type Block = Block;
        type AccountData = pallet_balances::AccountData<u128>;
    }

    impl pallet_balances::Config for Test {
        type MaxLocks = ConstU32<50>;
        type MaxReserves = ConstU32<50>;
        type ReserveIdentifier = [u8; 8];
        type Balance = u128;
        type RuntimeEvent = RuntimeEvent;
        type DustRemoval = ();
        type ExistentialDeposit = ConstU128<1>;
        type AccountStore = System;
        type WeightInfo = ();
        type FreezeIdentifier = ();
        type MaxFreezes = ConstU32<0>;
        type RuntimeHoldReason = ();
        type RuntimeFreezeReason = ();
        type DoneSlashHandler = ();
    }

    parameter_types! {
        pub const VestPalletId: PalletId = PalletId(*b"v/vestng");
        pub const MaxVestingSchedules: u32 = 16;
        pub const MaxSchedulesPerAccount: u32 = 10;
    }

    impl Config for Test {
        type RuntimeEvent = RuntimeEvent;
        type Currency = Balances;
        type PalletId = VestPalletId;
        type WeightInfo = SubstrateWeight<Test>;
        type MaxSchedulesPerAccount = MaxSchedulesPerAccount;
    }

    pub fn new_test_ext() -> TestExternalities {
        let mut t = frame_system::GenesisConfig::<Test>::default()
            .build_storage()
            .unwrap();
        pallet_balances::GenesisConfig::<Test> {
            balances: vec![
                (Sr25519Keyring::Alice.to_account_id(), 1_000_000_000),
                (Sr25519Keyring::Bob.to_account_id(), 100_000),
            ],
            ..Default::default()
        }
        .assimilate_storage(&mut t)
        .unwrap();
        // Add a vesting schedule in genesis
        GenesisConfig::<Test> {
            vesting_schedules: vec![(b"seed".to_vec(), 1_000_000_000u128, 60, 30)],
        }
        .assimilate_storage(&mut t)
        .unwrap();
        let mut ext = TestExternalities::new(t);
        ext.execute_with(|| System::set_block_number(1));
        ext
    }

    #[test]
    fn test_genesis_with_schedule() {
        new_test_ext().execute_with(|| {
            assert_eq!(UserVestings::<Test>::iter().count(), 0);
            let key: BoundedVec<u8, ConstU32<64>> = b"seed".to_vec().try_into().unwrap();
            assert!(Schedules::<Test>::contains_key(&key));
        });
    }

    #[test]
    fn test_add_schedule() {
        new_test_ext().execute_with(|| {
            assert_ok!(Vesting::add_schedule(
                RuntimeOrigin::root(),
                b"team".to_vec(),
                500_000_000u128,
                365,
                90,
            ));
            let key: BoundedVec<u8, ConstU32<64>> = b"team".to_vec().try_into().unwrap();
            assert!(Schedules::<Test>::contains_key(&key));
        });
    }

    #[test]
    fn test_add_schedule_duplicate() {
        new_test_ext().execute_with(|| {
            assert_noop!(
                Vesting::add_schedule(
                    RuntimeOrigin::root(),
                    b"seed".to_vec(),
                    500_000_000u128,
                    365,
                    90,
                ),
                Error::<Test>::ScheduleAlreadyExists
            );
        });
    }

    #[test]
    fn test_add_schedule_non_root() {
        new_test_ext().execute_with(|| {
            assert_noop!(
                Vesting::add_schedule(
                    RuntimeOrigin::signed(Sr25519Keyring::Alice.to_account_id()),
                    b"team".to_vec(),
                    500_000_000u128,
                    365,
                    90,
                ),
                sp_runtime::DispatchError::BadOrigin
            );
        });
    }

    #[test]
    fn test_assign_vesting() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_ok!(Vesting::assign_vesting(
                RuntimeOrigin::root(),
                alice.clone(),
                b"seed".to_vec(),
                500_000_000u128,
            ));
            assert_eq!(LockedBalances::<Test>::get(&alice), 500_000_000);
            // Lock is enforced by Balances pallet — transferable should be reduced
            let transferable = pallet_balances::Pallet::<Test>::usable_balance(&alice);
            assert!(transferable < 1_000_000_000);
        });
    }

    #[test]
    fn test_vesting_blocks_transfer() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let bob = Sr25519Keyring::Bob.to_account_id();

            // Assign vesting for the full balance
            assert_ok!(Vesting::assign_vesting(
                RuntimeOrigin::root(),
                alice.clone(),
                b"seed".to_vec(),
                1_000_000_000u128,
            ));

            // Transfer should fail — all funds are locked
            assert_noop!(
                pallet_balances::Call::<Test>::transfer_allow_death {
                    dest: bob,
                    value: 100_000_000u128
                }
                .dispatch_bypass_filter(RuntimeOrigin::signed(alice.clone())),
                sp_runtime::DispatchError::Token(sp_runtime::TokenError::Frozen)
            );
        });
    }

    #[test]
    fn test_release_without_vesting() {
        new_test_ext().execute_with(|| {
            assert_noop!(
                Vesting::release_vested(RuntimeOrigin::signed(
                    Sr25519Keyring::Alice.to_account_id()
                )),
                Error::<Test>::NoVestingForAccount
            );
        });
    }

    #[test]
    fn test_release_before_cliff() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            Vesting::assign_vesting(
                RuntimeOrigin::root(),
                alice.clone(),
                b"seed".to_vec(),
                500_000_000u128,
            )
            .unwrap();

            // Cliff is 30 days, we're at block 1 — nothing to release
            assert_noop!(
                Vesting::release_vested(RuntimeOrigin::signed(alice)),
                Error::<Test>::NothingToRelease
            );
        });
    }

    #[test]
    fn test_release_after_full_vesting() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let bob = Sr25519Keyring::Bob.to_account_id();

            Vesting::assign_vesting(
                RuntimeOrigin::root(),
                alice.clone(),
                b"seed".to_vec(),
                500_000_000u128,
            )
            .unwrap();

            // Advance past vesting period (60 days * 17280 blocks/day = 1036800 blocks)
            // blocks_per_day = 86400000 / 5000 = 17280
            System::set_block_number(1 + 1036800);

            assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(
                alice.clone()
            )));
            assert_eq!(LockedBalances::<Test>::get(&alice), 0);

            // Transfer should now work
            assert_ok!(pallet_balances::Call::<Test>::transfer_allow_death {
                dest: bob,
                value: 100_000_000u128
            }
            .dispatch_bypass_filter(RuntimeOrigin::signed(alice)));
        });
    }

    #[test]
    fn test_partial_release() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();

            Vesting::assign_vesting(
                RuntimeOrigin::root(),
                alice.clone(),
                b"seed".to_vec(),
                500_000_000u128,
            )
            .unwrap();

            // Advance to 45 days (past cliff=30, before full=60)
            // 45 * 17280 = 777600
            System::set_block_number(1 + 777600);

            assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(
                alice.clone()
            )));

            // Should have released ~75% (45/60 days)
            let remaining = LockedBalances::<Test>::get(&alice);
            assert!(remaining > 0 && remaining < 500_000_000);
        });
    }
    // === COMPREHENSIVE VESTING TESTS ===

    #[test]
    fn test_assign_vesting_non_root() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_noop!(
                Vesting::assign_vesting(
                    RuntimeOrigin::signed(alice.clone()),
                    alice,
                    b"seed".to_vec(),
                    500_000_000u128,
                ),
                sp_runtime::DispatchError::BadOrigin
            );
        });
    }

    #[test]
    fn test_assign_vesting_nonexistent_schedule() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_noop!(
                Vesting::assign_vesting(
                    RuntimeOrigin::root(),
                    alice,
                    b"nonexistent".to_vec(),
                    500_000_000u128,
                ),
                Error::<Test>::ScheduleNotFound
            );
        });
    }

    #[test]
    fn test_add_schedule_label_too_long() {
        new_test_ext().execute_with(|| {
            let long_label = vec![b'x'; 65]; // Max is 64
            assert_noop!(
                Vesting::add_schedule(RuntimeOrigin::root(), long_label, 500_000_000u128, 365, 90,),
                Error::<Test>::LabelTooLong
            );
        });
    }

    #[test]
    fn test_add_schedule_zero_vesting_days() {
        new_test_ext().execute_with(|| {
            assert_noop!(
                Vesting::add_schedule(
                    RuntimeOrigin::root(),
                    b"instant".to_vec(),
                    500_000_000u128,
                    0,
                    0,
                ),
                Error::<Test>::VestingNotStarted
            );
        });
    }

    #[test]
    fn test_add_schedule_cliff_gt_vesting_days() {
        new_test_ext().execute_with(|| {
            assert_noop!(
                Vesting::add_schedule(
                    RuntimeOrigin::root(),
                    b"bad_cliff".to_vec(),
                    500_000_000u128,
                    30,
                    60, // cliff > vesting_days
                ),
                Error::<Test>::VestingNotStarted
            );
        });
    }

    #[test]
    fn test_multiple_schedules_same_account() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();

            // Add a second schedule
            assert_ok!(Vesting::add_schedule(
                RuntimeOrigin::root(),
                b"team".to_vec(),
                300_000_000u128,
                365,
                90,
            ));

            // Assign both schedules to Alice
            assert_ok!(Vesting::assign_vesting(
                RuntimeOrigin::root(),
                alice.clone(),
                b"seed".to_vec(),
                500_000_000u128,
            ));
            assert_ok!(Vesting::assign_vesting(
                RuntimeOrigin::root(),
                alice.clone(),
                b"team".to_vec(),
                300_000_000u128,
            ));

            // Should have 2 vesting entries
            let vestings = UserVestings::<Test>::get(&alice).unwrap();
            assert_eq!(vestings.len(), 2);

            // Total locked should be sum of both
            assert_eq!(LockedBalances::<Test>::get(&alice), 800_000_000);
        });
    }

    #[test]
    fn test_max_vesting_entries_per_account() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();

            // Assign 10 vesting entries (the max per-account limit)
            for i in 0..10 {
                let label = format!("sch{}", i);
                assert_ok!(Vesting::add_schedule(
                    RuntimeOrigin::root(),
                    label.as_bytes().to_vec(),
                    1_000_000u128,
                    60,
                    30,
                ));
                assert_ok!(Vesting::assign_vesting(
                    RuntimeOrigin::root(),
                    alice.clone(),
                    label.as_bytes().to_vec(),
                    1_000_000u128,
                ));
            }

            // 11th should fail with MaxVestingSchedules
            assert_ok!(Vesting::add_schedule(
                RuntimeOrigin::root(),
                b"sch10".to_vec(),
                1_000_000u128,
                60,
                30,
            ));
            assert_noop!(
                Vesting::assign_vesting(
                    RuntimeOrigin::root(),
                    alice,
                    b"sch10".to_vec(),
                    1_000_000u128,
                ),
                Error::<Test>::MaxVestingSchedules
            );
        });
    }

    #[test]
    fn test_release_at_exact_cliff_boundary() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();

            Vesting::assign_vesting(
                RuntimeOrigin::root(),
                alice.clone(),
                b"seed".to_vec(),
                600_000_000u128,
            )
            .unwrap();

            // Advance to exactly 30 days (the cliff boundary)
            // 30 * 17280 = 518400 blocks
            System::set_block_number(1 + 518400);

            assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(
                alice.clone()
            )));

            // At day 30 of 60, should have released 50% = 300M
            let released_entry = UserVestings::<Test>::get(&alice).unwrap();
            let entry = &released_entry[0];
            assert_eq!(
                entry.released, 300_000_000,
                "At cliff boundary (half vesting), 50% should be released"
            );
        });
    }

    #[test]
    fn test_progressive_release_multiple_times() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();

            Vesting::assign_vesting(
                RuntimeOrigin::root(),
                alice.clone(),
                b"seed".to_vec(),
                600_000_000u128,
            )
            .unwrap();

            // Release at day 30 (cliff boundary, 50% = 300M)
            System::set_block_number(1 + 518400); // 30 days
            assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(
                alice.clone()
            )));
            assert_eq!(LockedBalances::<Test>::get(&alice), 300_000_000);

            // Release at day 45 (75% = 450M, additional 150M)
            System::set_block_number(1 + 777600); // 45 days
            assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(
                alice.clone()
            )));
            assert_eq!(LockedBalances::<Test>::get(&alice), 150_000_000);

            // Release at day 60 (100% = 600M, remaining 150M)
            System::set_block_number(1 + 1036800); // 60 days
            assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(
                alice.clone()
            )));
            assert_eq!(LockedBalances::<Test>::get(&alice), 0);
        });
    }

    #[test]
    fn test_release_nothing_after_full_release() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();

            Vesting::assign_vesting(
                RuntimeOrigin::root(),
                alice.clone(),
                b"seed".to_vec(),
                500_000_000u128,
            )
            .unwrap();

            // Full release
            System::set_block_number(1 + 1036800);
            assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(
                alice.clone()
            )));
            assert_eq!(LockedBalances::<Test>::get(&alice), 0);

            // Try to release again — should fail
            assert_noop!(
                Vesting::release_vested(RuntimeOrigin::signed(alice)),
                Error::<Test>::NothingToRelease
            );
        });
    }

    #[test]
    fn test_transfer_after_partial_release() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let bob = Sr25519Keyring::Bob.to_account_id();

            // Assign vesting for half the balance
            assert_ok!(Vesting::assign_vesting(
                RuntimeOrigin::root(),
                alice.clone(),
                b"seed".to_vec(),
                500_000_000u128,
            ));

            // Advance to day 30 (cliff boundary, 50% released = 250M)
            System::set_block_number(1 + 518400);
            assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(
                alice.clone()
            )));

            // Alice should be able to transfer the released portion
            assert_ok!(pallet_balances::Call::<Test>::transfer_allow_death {
                dest: bob,
                value: 100_000_000u128
            }
            .dispatch_bypass_filter(RuntimeOrigin::signed(alice.clone())));

            // But not more than what's unlocked
            let usable = pallet_balances::Pallet::<Test>::usable_balance(&alice);
            // After releasing 250M of 500M locked, usable should be 1B - 250M remaining = 750M
            // But the actual transfer of 100M already happened, so usable = 750M - 100M = 650M
            // Key assertion: usable is reduced (not full 1B - existential)
            assert!(
                usable < 1_000_000_000,
                "Usable balance should be reduced by remaining lock"
            );
            assert!(
                usable > 500_000_000,
                "Usable should include released portion"
            );
        });
    }

    #[test]
    fn test_do_assign_vesting_internal() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();

            // Call the internal function directly (simulates cross-pallet call from presale)
            assert_ok!(Vesting::do_assign_vesting(
                alice.clone(),
                b"seed".to_vec(),
                500_000_000u128,
            ));

            assert_eq!(LockedBalances::<Test>::get(&alice), 500_000_000);
            let vestings = UserVestings::<Test>::get(&alice).unwrap();
            assert_eq!(vestings.len(), 1);
            assert_eq!(vestings[0].total_amount, 500_000_000);
        });
    }

    #[test]
    fn test_genesis_multiple_schedules() {
        let mut t = frame_system::GenesisConfig::<Test>::default()
            .build_storage()
            .unwrap();
        pallet_balances::GenesisConfig::<Test> {
            balances: vec![(Sr25519Keyring::Alice.to_account_id(), 1_000_000_000)],
            ..Default::default()
        }
        .assimilate_storage(&mut t)
        .unwrap();
        GenesisConfig::<Test> {
            vesting_schedules: vec![
                (b"seed".to_vec(), 1_000_000_000u128, 365, 90),
                (b"team".to_vec(), 500_000_000u128, 730, 365),
                (b"community".to_vec(), 200_000_000u128, 90, 0),
            ],
        }
        .assimilate_storage(&mut t)
        .unwrap();
        let mut ext = TestExternalities::new(t);
        ext.execute_with(|| System::set_block_number(1));
        ext.execute_with(|| {
            let key_seed: BoundedVec<u8, ConstU32<64>> = b"seed".to_vec().try_into().unwrap();
            let key_team: BoundedVec<u8, ConstU32<64>> = b"team".to_vec().try_into().unwrap();
            let key_comm: BoundedVec<u8, ConstU32<64>> = b"community".to_vec().try_into().unwrap();
            assert!(Schedules::<Test>::contains_key(&key_seed));
            assert!(Schedules::<Test>::contains_key(&key_team));
            assert!(Schedules::<Test>::contains_key(&key_comm));
        });
    }

    #[test]
    fn test_release_exactly_at_start_block() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();

            Vesting::assign_vesting(
                RuntimeOrigin::root(),
                alice.clone(),
                b"seed".to_vec(),
                500_000_000u128,
            )
            .unwrap();

            // At block 1 (start), nothing vested yet (cliff = 30 days)
            assert_noop!(
                Vesting::release_vested(RuntimeOrigin::signed(alice)),
                Error::<Test>::NothingToRelease
            );
        });
    }

    #[test]
    fn test_assign_zero_amount() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();

            // Assigning zero should work but lock nothing meaningful
            assert_ok!(Vesting::assign_vesting(
                RuntimeOrigin::root(),
                alice.clone(),
                b"seed".to_vec(),
                0u128,
            ));
            assert_eq!(LockedBalances::<Test>::get(&alice), 0);

            // Vesting entry should still exist
            let vestings = UserVestings::<Test>::get(&alice).unwrap();
            assert_eq!(vestings.len(), 1);
            assert_eq!(vestings[0].total_amount, 0);
        });
    }

    #[test]
    fn test_assign_vesting_preserves_existing_entries() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();

            // Add a second schedule
            assert_ok!(Vesting::add_schedule(
                RuntimeOrigin::root(),
                b"team".to_vec(),
                300_000_000u128,
                365,
                90,
            ));

            // First assignment
            assert_ok!(Vesting::assign_vesting(
                RuntimeOrigin::root(),
                alice.clone(),
                b"seed".to_vec(),
                500_000_000u128,
            ));

            // Second assignment should not remove the first
            assert_ok!(Vesting::assign_vesting(
                RuntimeOrigin::root(),
                alice.clone(),
                b"team".to_vec(),
                300_000_000u128,
            ));

            let vestings = UserVestings::<Test>::get(&alice).unwrap();
            assert_eq!(vestings.len(), 2, "Both entries should be preserved");
            assert_eq!(vestings[0].total_amount, 500_000_000);
            assert_eq!(vestings[1].total_amount, 300_000_000);
        });
    }

    #[test]
    fn test_cliff_zero_immediate_vesting() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();

            // Add a schedule with zero cliff (immediate vesting start)
            assert_ok!(Vesting::add_schedule(
                RuntimeOrigin::root(),
                b"immediate".to_vec(),
                500_000_000u128,
                60,
                0, // No cliff
            ));

            assert_ok!(Vesting::assign_vesting(
                RuntimeOrigin::root(),
                alice.clone(),
                b"immediate".to_vec(),
                500_000_000u128,
            ));

            // At block 1, some tokens should be vestable (day 0 out of 60 = 0%)
            // Actually at day 0, elapsed_days = 0, so vested = 0. Need to advance at least 1 day
            // 1 day = 17280 blocks
            System::set_block_number(1 + 17280);

            assert_ok!(Vesting::release_vested(RuntimeOrigin::signed(
                alice.clone()
            )));

            // At day 1 of 60, should have ~1/60 vested = ~8.33M
            let locked = LockedBalances::<Test>::get(&alice);
            assert!(locked < 500_000_000, "Some tokens should be released");
            assert!(locked > 0, "Not all should be released yet");
        });
    }
}
