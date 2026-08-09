#![allow(clippy::type_complexity)]
#![allow(clippy::let_unit_value)]
//! # Verdis Presale Pallet
//!
//! On-chain presale/IDO contribution system with:
//! - Multiple contribution rounds (Seed, Community, Presale, TGE)
//! - Per-round per-account caps (independent per round)
//! - Per-round whitelist (independent per round)
//! - Vesting schedule integration (atomic)
//! - Overflow protection (checked arithmetic throughout)
//! - Admin controls (start/stop, whitelist, emergency pause)
//! - Atomic accounting (all-or-nothing state changes)

#![cfg_attr(not(feature = "std"), no_std)]
#![allow(deprecated)]
use codec::{Decode, Encode, MaxEncodedLen};
use frame_support::{
    dispatch::DispatchResult,
    ensure,
    pallet_prelude::*,
    traits::{Currency, EnsureOrigin, Get, ReservableCurrency},
    PalletId,
};
use frame_system::pallet_prelude::*;
use scale_info::TypeInfo;
use sp_runtime::traits::Zero;
use sp_std::prelude::*;

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use super::*;

    type BalanceOf<T> =
        <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

    /// Trait for vesting integration — implemented by the runtime to bridge to the vesting pallet
    pub trait VestingHandler<AccountId, Balance> {
        /// Create a vesting entry for `who` with `schedule_label` and `amount`.
        /// Returns Err if vesting cannot be created (e.g. schedule not found).
        fn assign_vesting(
            who: &AccountId,
            schedule_label: Vec<u8>,
            amount: Balance,
        ) -> DispatchResult;
    }

    /// Default no-op implementation (for testing without vesting pallet)
    impl<AccountId, Balance> VestingHandler<AccountId, Balance> for () {
        fn assign_vesting(_: &AccountId, _: Vec<u8>, _: Balance) -> DispatchResult {
            Ok(())
        }
    }

    /// Presale round configuration
    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo, Debug)]
    pub struct SaleRound<Balance, BlockNumber> {
        pub label: BoundedVec<u8, ConstU32<32>>,
        pub token_price: Balance,
        pub total_allocation: Balance,
        pub sold: Balance,
        pub per_account_cap: Balance,
        pub start_block: BlockNumber,
        pub end_block: BlockNumber,
        pub vesting_label: BoundedVec<u8, ConstU32<64>>,
        pub is_active: bool,
    }

    /// User contribution record — per (round_id, account_id)
    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo, Debug, Default)]
    pub struct UserContribution<Balance> {
        pub total_purchased: Balance,
        pub total_paid: Balance,
    }

    // === Storage ===

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::storage]
    #[pallet::getter(fn rounds)]
    pub type Rounds<T: Config> =
        StorageMap<_, Blake2_128Concat, u32, SaleRound<BalanceOf<T>, BlockNumberFor<T>>>;

    #[pallet::storage]
    pub type NextRoundId<T: Config> = StorageValue<_, u32, ValueQuery>;

    /// Per-round per-account contributions: (round_id, account_id) → UserContribution
    #[pallet::storage]
    #[pallet::getter(fn contributions)]
    pub type Contributions<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        u32,
        Blake2_128Concat,
        T::AccountId,
        UserContribution<BalanceOf<T>>,
    >;

    /// Per-round whitelist: (round_id, account_id) → bool
    #[pallet::storage]
    #[pallet::getter(fn is_whitelisted)]
    pub type Whitelist<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        u32,
        Blake2_128Concat,
        T::AccountId,
        bool,
        ValueQuery,
    >;

    #[pallet::storage]
    #[pallet::getter(fn is_paused)]
    pub type Paused<T: Config> = StorageValue<_, bool, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn total_raised)]
    pub type TotalRaised<T: Config> = StorageValue<_, BalanceOf<T>, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn total_sold)]
    pub type TotalSold<T: Config> = StorageValue<_, BalanceOf<T>, ValueQuery>;

    // === Events ===

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        RoundCreated {
            round_id: u32,
            label: Vec<u8>,
            allocation: BalanceOf<T>,
            price: BalanceOf<T>,
        },
        RoundActivated {
            round_id: u32,
        },
        RoundDeactivated {
            round_id: u32,
        },
        Contribution {
            who: T::AccountId,
            round_id: u32,
            payment_amount: BalanceOf<T>,
            token_amount: BalanceOf<T>,
        },
        VestingCreated {
            who: T::AccountId,
            round_id: u32,
            token_amount: BalanceOf<T>,
            vesting_label: Vec<u8>,
        },
        Paused,
        Unpaused,
        WhitelistUpdated {
            who: T::AccountId,
            whitelisted: bool,
        },
    }

    // === Errors ===

    #[pallet::error]
    pub enum Error<T> {
        RoundNotFound,
        RoundNotActive,
        RoundNotStarted,
        RoundEnded,
        Paused,
        ExceedsPerAccountCap,
        ExceedsRoundAllocation,
        NotWhitelisted,
        InsufficientPayment,
        ZeroPayment,
        RoundAlreadyExists,
        LabelTooLong,
        VestingLabelTooLong,
        NoContribution,
        CalculationOverflow,
        VestingFailed,
        InvalidGenesisConfig,
    }

    // === Config ===

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        type Currency: ReservableCurrency<Self::AccountId>;
        #[pallet::constant]
        type PalletId: Get<PalletId>;
        type AdminOrigin: EnsureOrigin<Self::RuntimeOrigin>;
        type Vesting: VestingHandler<Self::AccountId, BalanceOf<Self>>;
        type WeightInfo: WeightInfo;
    }

    // === Genesis ===

    #[pallet::genesis_config]
    #[derive(frame_support::DefaultNoBound)]
    pub struct GenesisConfig<T: Config> {
        pub initial_rounds: Vec<(
            Vec<u8>,      // label
            BalanceOf<T>, // token_price
            BalanceOf<T>, // total_allocation
            BalanceOf<T>, // per_account_cap
            u32,          // start_block
            u32,          // end_block
            Vec<u8>,      // vesting_label
        )>,
    }

    #[pallet::genesis_build]
    impl<T: Config> BuildGenesisConfig for GenesisConfig<T> {
        fn build(&self) {
            for (label, price, allocation, cap, start, end, vesting_label) in &self.initial_rounds {
                // Validate genesis — fail loudly on invalid data
                let label_bv: BoundedVec<u8, ConstU32<32>> = label
                    .clone()
                    .try_into()
                    .expect("Presale genesis: label too long");
                let vesting_bv: BoundedVec<u8, ConstU32<64>> = vesting_label
                    .clone()
                    .try_into()
                    .expect("Presale genesis: vesting_label too long");
                assert!(
                    *price > BalanceOf::<T>::zero(),
                    "Presale genesis: price must be > 0"
                );
                assert!(
                    *allocation > BalanceOf::<T>::zero(),
                    "Presale genesis: allocation must be > 0"
                );
                assert!(
                    end > start,
                    "Presale genesis: end_block must be > start_block"
                );

                let round = SaleRound {
                    label: label_bv,
                    token_price: *price,
                    total_allocation: *allocation,
                    sold: BalanceOf::<T>::zero(),
                    per_account_cap: *cap,
                    start_block: BlockNumberFor::<T>::from(*start),
                    end_block: BlockNumberFor::<T>::from(*end),
                    vesting_label: vesting_bv,
                    is_active: false,
                };

                let round_id = NextRoundId::<T>::get();
                Rounds::<T>::insert(round_id, round);
                NextRoundId::<T>::put(round_id + 1);
            }
        }
    }

    // === Extrinsics ===

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Create a new sale round (admin only)
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::create_round())]
        pub fn create_round(
            origin: OriginFor<T>,
            label: Vec<u8>,
            token_price: BalanceOf<T>,
            total_allocation: BalanceOf<T>,
            per_account_cap: BalanceOf<T>,
            start_block: BlockNumberFor<T>,
            end_block: BlockNumberFor<T>,
            vesting_label: Vec<u8>,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            let label_bv: BoundedVec<u8, ConstU32<32>> = label
                .clone()
                .try_into()
                .map_err(|_| Error::<T>::LabelTooLong)?;
            let vesting_bv: BoundedVec<u8, ConstU32<64>> = vesting_label
                .clone()
                .try_into()
                .map_err(|_| Error::<T>::VestingLabelTooLong)?;

            ensure!(
                token_price > BalanceOf::<T>::zero(),
                Error::<T>::InsufficientPayment
            );
            ensure!(
                total_allocation > BalanceOf::<T>::zero(),
                Error::<T>::InsufficientPayment
            );
            ensure!(end_block > start_block, Error::<T>::RoundNotStarted);

            let round = SaleRound {
                label: label_bv,
                token_price,
                total_allocation,
                sold: BalanceOf::<T>::zero(),
                per_account_cap,
                start_block,
                end_block,
                vesting_label: vesting_bv,
                is_active: false,
            };

            let round_id = NextRoundId::<T>::get();
            Rounds::<T>::insert(round_id, round);
            NextRoundId::<T>::put(round_id + 1);

            Self::deposit_event(Event::RoundCreated {
                round_id,
                label,
                allocation: total_allocation,
                price: token_price,
            });
            Ok(())
        }

        /// Activate a sale round (admin only)
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::activate_round())]
        pub fn activate_round(origin: OriginFor<T>, round_id: u32) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;
            Rounds::<T>::try_mutate(round_id, |round_opt| {
                let round = round_opt.as_mut().ok_or(Error::<T>::RoundNotFound)?;
                round.is_active = true;
                Self::deposit_event(Event::RoundActivated { round_id });
                Ok(())
            })
        }

        /// Deactivate a sale round (admin only)
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::deactivate_round())]
        pub fn deactivate_round(origin: OriginFor<T>, round_id: u32) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;
            Rounds::<T>::try_mutate(round_id, |round_opt| {
                let round = round_opt.as_mut().ok_or(Error::<T>::RoundNotFound)?;
                round.is_active = false;
                Self::deposit_event(Event::RoundDeactivated { round_id });
                Ok(())
            })
        }

        /// Contribute to a sale round
        /// Payment is reserved; tokens are credited with vesting (atomic)
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::contribute())]
        pub fn contribute(
            origin: OriginFor<T>,
            round_id: u32,
            payment_amount: BalanceOf<T>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            ensure!(!Paused::<T>::get(), Error::<T>::Paused);
            ensure!(
                payment_amount > BalanceOf::<T>::zero(),
                Error::<T>::ZeroPayment
            );

            let round = Rounds::<T>::get(round_id).ok_or(Error::<T>::RoundNotFound)?;
            ensure!(round.is_active, Error::<T>::RoundNotActive);

            let current_block = frame_system::Pallet::<T>::block_number();
            ensure!(
                current_block >= round.start_block,
                Error::<T>::RoundNotStarted
            );
            ensure!(current_block < round.end_block, Error::<T>::RoundEnded);

            // Per-round whitelist check
            if Whitelist::<T>::iter_prefix(round_id).next().is_some() {
                ensure!(
                    Whitelist::<T>::get(round_id, &who),
                    Error::<T>::NotWhitelisted
                );
            }

            // Calculate token amount (checked arithmetic)
            let token_amount = payment_amount
                .checked_mul(&round.token_price)
                .ok_or(Error::<T>::CalculationOverflow)?;

            // Per-round per-account cap check
            let contribution = Contributions::<T>::get(round_id, &who).unwrap_or_default();
            let new_total = contribution
                .total_purchased
                .checked_add(&token_amount)
                .ok_or(Error::<T>::CalculationOverflow)?;
            ensure!(
                new_total <= round.per_account_cap,
                Error::<T>::ExceedsPerAccountCap
            );

            // Round allocation check
            let new_sold = round
                .sold
                .checked_add(&token_amount)
                .ok_or(Error::<T>::CalculationOverflow)?;
            ensure!(
                new_sold <= round.total_allocation,
                Error::<T>::ExceedsRoundAllocation
            );

            // Calculate new totals (checked arithmetic — no saturating)
            let new_total_paid = contribution
                .total_paid
                .checked_add(&payment_amount)
                .ok_or(Error::<T>::CalculationOverflow)?;
            let new_global_raised = TotalRaised::<T>::get()
                .checked_add(&payment_amount)
                .ok_or(Error::<T>::CalculationOverflow)?;
            let new_global_sold = TotalSold::<T>::get()
                .checked_add(&token_amount)
                .ok_or(Error::<T>::CalculationOverflow)?;

            // === All checks passed — now mutate state ===

            // Reserve payment from contributor
            T::Currency::reserve(&who, payment_amount)
                .map_err(|_| Error::<T>::InsufficientPayment)?;

            // Create vesting entry (atomic — if this fails, reserve is auto-reverted by Substrate)
            if !round.vesting_label.is_empty() {
                T::Vesting::assign_vesting(
                    &who,
                    round.vesting_label.clone().into_inner(),
                    token_amount,
                )
                .map_err(|_| Error::<T>::VestingFailed)?;

                Self::deposit_event(Event::VestingCreated {
                    who: who.clone(),
                    round_id,
                    token_amount,
                    vesting_label: round.vesting_label.clone().into_inner(),
                });
            }

            // Update round sold
            Rounds::<T>::mutate(round_id, |round_opt| {
                if let Some(r) = round_opt {
                    r.sold = new_sold;
                }
            });

            // Update per-round contribution
            Contributions::<T>::insert(
                round_id,
                &who,
                UserContribution {
                    total_purchased: new_total,
                    total_paid: new_total_paid,
                },
            );

            // Update global totals (checked — no saturating)
            TotalRaised::<T>::put(new_global_raised);
            TotalSold::<T>::put(new_global_sold);

            Self::deposit_event(Event::Contribution {
                who: who.clone(),
                round_id,
                payment_amount,
                token_amount,
            });

            Ok(())
        }

        /// Emergency pause all rounds (admin only)
        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::set_paused())]
        pub fn set_paused(origin: OriginFor<T>, paused: bool) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;
            Paused::<T>::put(paused);
            if paused {
                Self::deposit_event(Event::Paused);
            } else {
                Self::deposit_event(Event::Unpaused);
            }
            Ok(())
        }

        /// Update whitelist for a specific round (admin only)
        #[pallet::call_index(5)]
        #[pallet::weight(T::WeightInfo::update_whitelist())]
        pub fn update_whitelist(
            origin: OriginFor<T>,
            round_id: u32,
            who: T::AccountId,
            whitelisted: bool,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;
            Whitelist::<T>::insert(round_id, &who, whitelisted);
            Self::deposit_event(Event::WhitelistUpdated { who, whitelisted });
            Ok(())
        }
    }

    // === Weight Info ===

    pub trait WeightInfo {
        fn create_round() -> frame_support::weights::Weight;
        fn activate_round() -> frame_support::weights::Weight;
        fn deactivate_round() -> frame_support::weights::Weight;
        fn contribute() -> frame_support::weights::Weight;
        fn set_paused() -> frame_support::weights::Weight;
        fn update_whitelist() -> frame_support::weights::Weight;
    }

    pub struct SubstrateWeight<T>(PhantomData<T>);
    impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
        fn create_round() -> frame_support::weights::Weight {
            frame_support::weights::Weight::from_parts(10_000, 0)
        }
        fn activate_round() -> frame_support::weights::Weight {
            frame_support::weights::Weight::from_parts(5_000, 0)
        }
        fn deactivate_round() -> frame_support::weights::Weight {
            frame_support::weights::Weight::from_parts(5_000, 0)
        }
        fn contribute() -> frame_support::weights::Weight {
            frame_support::weights::Weight::from_parts(20_000, 0)
        }
        fn set_paused() -> frame_support::weights::Weight {
            frame_support::weights::Weight::from_parts(5_000, 0)
        }
        fn update_whitelist() -> frame_support::weights::Weight {
            frame_support::weights::Weight::from_parts(10_000, 0)
        }
    }

    #[cfg(feature = "std")]
    impl WeightInfo for () {
        fn create_round() -> frame_support::weights::Weight {
            frame_support::weights::Weight::from_parts(10_000, 0)
        }
        fn activate_round() -> frame_support::weights::Weight {
            frame_support::weights::Weight::from_parts(5_000, 0)
        }
        fn deactivate_round() -> frame_support::weights::Weight {
            frame_support::weights::Weight::from_parts(5_000, 0)
        }
        fn contribute() -> frame_support::weights::Weight {
            frame_support::weights::Weight::from_parts(20_000, 0)
        }
        fn set_paused() -> frame_support::weights::Weight {
            frame_support::weights::Weight::from_parts(5_000, 0)
        }
        fn update_whitelist() -> frame_support::weights::Weight {
            frame_support::weights::Weight::from_parts(10_000, 0)
        }
    }
}

#[cfg(test)]
mod tests;
