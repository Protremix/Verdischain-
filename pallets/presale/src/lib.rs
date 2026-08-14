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
    clippy::needless_borrows_for_generic_args,
    clippy::incompatible_msrv
)]
//! # Verdis Presale Pallet
//!
//! On-chain presale/IDO contribution system with:
//! - **Escrow-based payments**: buyer pays into a deterministic Presale Escrow
//!   account (derived from PalletId), NOT user reserved balances.
//! - Per-round per-account caps (independent per round)
//! - Per-round whitelist (independent per round)
//! - Vesting schedule integration (atomic)
//! - Overflow protection (checked arithmetic throughout — no saturating for financial accounting)
//! - **O(1) fund collection** from escrow (no unbounded contributor iteration)
//! - **Double-collection prevention** via `RoundFundsCollected` flag
//! - **Round-end enforcement**: collection only after `end_block`
//! - **Escrow VRDX balance verification**: contribution fails if escrow lacks tokens
//! - Admin controls (start/stop, whitelist, emergency pause)
//! - Atomic accounting (all-or-nothing state changes)
//!
//! ## Payment Flow
//! ```text
//! Buyer --payment--> Presale Escrow Account
//! Presale Escrow Account --VRDX--> Buyer
//! Presale Escrow Account --vesting--> Vesting Pallet
//! ```
//!
//! ## Collection Flow
//! ```text
//! After round.end_block:
//!   Admin calls collect_funds(round_id, beneficiary)
//!   Presale Escrow --RoundRaised amount--> Beneficiary
//!   RoundFundsCollected = true  (prevents double collection)
//! ```
//!
//! ## Price Formula
//! `token_amount = payment_amount.checked_mul(token_price)`
//! where `token_price` = tokens per payment unit (e.g. price=5 means 5 VRDX per 1 unit of payment).

#![cfg_attr(not(feature = "std"), no_std)]
use codec::{Decode, Encode, MaxEncodedLen};
use frame_support::{
    ensure,
    pallet_prelude::*,
    traits::{Currency, EnsureOrigin, ExistenceRequirement, Get},
    PalletId,
};
use frame_system::pallet_prelude::*;
use scale_info::TypeInfo;
use sp_runtime::traits::{AccountIdConversion, Zero};
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
        /// Price numerator: token_amount = (payment_amount * token_price) / price_precision
        /// For integer ratios (5 VRDX per 1 payment unit): token_price=5, price_precision=1
        /// For fractional ratios (0.5 VRDX per 1 payment unit): token_price=5, price_precision=10
        /// For 9-decimal fixed point: token_price=5*10^9, price_precision=10^9
        pub token_price: Balance,
        /// Denominator for price calculation. Default 1 for backward compatibility.
        pub price_precision: Balance,
        pub total_allocation: Balance,
        pub sold: Balance,
        pub per_account_cap: Balance,
        pub start_block: BlockNumber,
        pub end_block: BlockNumber,
        pub vesting_label: BoundedVec<u8, ConstU32<64>>,
        pub is_active: bool,
        /// If true, only whitelisted accounts can contribute
        pub whitelist_required: bool,
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

    /// P0-4 FIX: Global whitelist enforcement flag.
    /// When true, ALL rounds require whitelisting regardless of per-round setting.
    #[pallet::storage]
    #[pallet::getter(fn whitelist_enforced)]
    pub type WhitelistEnforced<T: Config> = StorageValue<_, bool, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn is_paused)]
    pub type Paused<T: Config> = StorageValue<_, bool, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn total_raised)]
    pub type TotalRaised<T: Config> = StorageValue<_, BalanceOf<T>, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn total_sold)]
    pub type TotalSold<T: Config> = StorageValue<_, BalanceOf<T>, ValueQuery>;

    /// Per-round raised amount — total payment received for each round.
    /// Used by collect_funds() for O(1) collection.
    #[pallet::storage]
    #[pallet::getter(fn round_raised)]
    pub type RoundRaised<T: Config> =
        StorageMap<_, Blake2_128Concat, u32, BalanceOf<T>, ValueQuery>;

    /// Per-round funds collected flag — prevents double collection.
    #[pallet::storage]
    #[pallet::getter(fn round_funds_collected)]
    pub type RoundFundsCollected<T: Config> =
        StorageMap<_, Blake2_128Concat, u32, bool, ValueQuery>;

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
        /// Funds collected from escrow to beneficiary (O(1) operation)
        FundsCollected {
            round_id: u32,
            amount: BalanceOf<T>,
            collected_by: T::AccountId,
        },
        /// Refund claimed by a contributor from a failed/cancelled round
        RefundClaimed {
            round_id: u32,
            account: T::AccountId,
            amount: BalanceOf<T>,
        },
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
        InsufficientAllocation,
        NotWhitelisted,
        RoundNotRefundable,
        InsufficientPayment,
        ZeroPayment,
        RoundAlreadyExists,
        LabelTooLong,
        VestingLabelTooLong,
        EmptyVestingLabel,
        NoContribution,
        CalculationOverflow,
        VestingFailed,
        InvalidGenesisConfig,
        /// Funds have already been collected for this round
        FundsAlreadyCollected,
        /// Round has not ended yet — collection requires block >= end_block
        RoundNotEnded,
        /// Presale escrow does not have enough VRDX to fulfill this contribution
        InsufficientEscrowBalance,
    }

    // === Config ===

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        type Currency: Currency<Self::AccountId>;
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
                assert!(
                    !vesting_label.is_empty(),
                    "Presale genesis: vesting_label must not be empty"
                );

                let round = SaleRound {
                    label: label_bv,
                    token_price: *price,
                    price_precision: <BalanceOf<T> as From<u32>>::from(1u32),
                    total_allocation: *allocation,
                    sold: BalanceOf::<T>::zero(),
                    per_account_cap: *cap,
                    start_block: BlockNumberFor::<T>::from(*start),
                    end_block: BlockNumberFor::<T>::from(*end),
                    vesting_label: vesting_bv,
                    is_active: false,
                    whitelist_required: false,
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
            ensure!(!vesting_label.is_empty(), Error::<T>::EmptyVestingLabel);

            let round = SaleRound {
                label: label_bv,
                token_price,
                price_precision: <BalanceOf<T> as From<u32>>::from(1u32),
                total_allocation,
                sold: BalanceOf::<T>::zero(),
                per_account_cap,
                start_block,
                end_block,
                vesting_label: vesting_bv,
                is_active: false,
                whitelist_required: false,
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

        /// Contribute to a sale round.
        ///
        /// Payment flow: buyer → presale escrow (transfer, not reserve).
        /// Token flow: presale escrow → buyer (with vesting).
        /// All state changes are atomic — on failure, no financial state changes remain.
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

            // P0-4 FIX: Whitelist check — enforced if per-round OR global flag is set
            if round.whitelist_required || WhitelistEnforced::<T>::get() {
                ensure!(
                    Whitelist::<T>::get(round_id, &who),
                    Error::<T>::NotWhitelisted
                );
            }

            // === Price formula: token_amount = (payment_amount * token_price) / price_precision ===
            // This prevents over-issuance when using fixed-point price representation
            let gross_amount = payment_amount
                .checked_mul(&round.token_price)
                .ok_or(Error::<T>::CalculationOverflow)?;
            let token_amount = if round.price_precision > BalanceOf::<T>::zero() {
                gross_amount
                    .checked_div(&round.price_precision)
                    .ok_or(Error::<T>::CalculationOverflow)?
            } else {
                gross_amount // Fallback for zero precision (treats as 1)
            };

            // Prevent zero-token purchases from truncation
            ensure!(
                token_amount > BalanceOf::<T>::zero(),
                Error::<T>::ZeroPayment
            );

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
            let new_round_raised = RoundRaised::<T>::get(round_id)
                .checked_add(&payment_amount)
                .ok_or(Error::<T>::CalculationOverflow)?;
            let new_global_raised = TotalRaised::<T>::get()
                .checked_add(&payment_amount)
                .ok_or(Error::<T>::CalculationOverflow)?;
            let new_global_sold = TotalSold::<T>::get()
                .checked_add(&token_amount)
                .ok_or(Error::<T>::CalculationOverflow)?;

            // === Verify escrow has enough VRDX before any state mutation ===
            let escrow = T::PalletId::get().into_account_truncating();
            let escrow_balance = T::Currency::free_balance(&escrow);
            ensure!(
                escrow_balance >= token_amount,
                Error::<T>::InsufficientEscrowBalance
            );

            // === All checks passed — now perform state mutations (atomic) ===

            // 1. Transfer payment from buyer to presale escrow
            T::Currency::transfer(
                &who,
                &escrow,
                payment_amount,
                ExistenceRequirement::KeepAlive,
            )
            .map_err(|_| Error::<T>::InsufficientPayment)?;

            // 2. Transfer purchased VRDX from escrow to buyer
            T::Currency::transfer(
                &escrow,
                &who,
                token_amount,
                ExistenceRequirement::AllowDeath,
            )
            .map_err(|_| Error::<T>::InsufficientAllocation)?;

            // 3. Create vesting entry (if this fails, the transfers above are reverted
            //    by the dispatchable's automatic state rollback)
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

            // 4. Update round sold
            Rounds::<T>::mutate(round_id, |round_opt| {
                if let Some(r) = round_opt {
                    r.sold = new_sold;
                }
            });

            // 5. Update per-round contribution
            Contributions::<T>::insert(
                round_id,
                &who,
                UserContribution {
                    total_purchased: new_total,
                    total_paid: new_total_paid,
                },
            );

            // 6. Update round-level raised amount
            RoundRaised::<T>::insert(round_id, new_round_raised);

            // 7. Update global totals (checked — no saturating)
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

        /// Collect raised funds from a completed round (admin only).
        ///
        /// O(1) operation — transfers `RoundRaised[round_id]` from the presale
        /// escrow account to the beneficiary. Does NOT iterate over contributors.
        ///
        /// Requirements:
        /// - Round must exist
        /// - Current block >= round.end_block (round must have ended)
        /// - Funds must not have been collected already (no double collection)
        #[pallet::call_index(6)]
        #[pallet::weight(T::WeightInfo::collect_funds())]
        pub fn collect_funds(
            origin: OriginFor<T>,
            round_id: u32,
            beneficiary: T::AccountId,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            // Load round
            let round = Rounds::<T>::get(round_id).ok_or(Error::<T>::RoundNotFound)?;

            // Verify round has ended (block >= end_block)
            let current_block = frame_system::Pallet::<T>::block_number();
            ensure!(current_block >= round.end_block, Error::<T>::RoundNotEnded);

            // Prevent double collection
            ensure!(
                !RoundFundsCollected::<T>::get(round_id),
                Error::<T>::FundsAlreadyCollected
            );

            // Get the total raised for this round
            let round_raised = RoundRaised::<T>::get(round_id);

            // Transfer from escrow to beneficiary (O(1) — no contributor iteration)
            if round_raised > BalanceOf::<T>::zero() {
                let escrow = T::PalletId::get().into_account_truncating();
                T::Currency::transfer(
                    &escrow,
                    &beneficiary,
                    round_raised,
                    ExistenceRequirement::AllowDeath,
                )?;
            }

            // Mark funds as collected (prevents double collection)
            RoundFundsCollected::<T>::insert(round_id, true);

            Self::deposit_event(Event::FundsCollected {
                round_id,
                amount: round_raised,
                collected_by: beneficiary,
            });

            Ok(())
        }

        /// Set whitelist enforcement for a round (admin only)
        #[pallet::call_index(7)]
        #[pallet::weight(T::WeightInfo::update_whitelist())]
        pub fn set_whitelist_required(
            origin: OriginFor<T>,
            round_id: u32,
            required: bool,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            Rounds::<T>::try_mutate(round_id, |round_opt| -> Result<(), Error<T>> {
                let round = round_opt.as_mut().ok_or(Error::<T>::RoundNotFound)?;
                round.whitelist_required = required;
                Ok(())
            })?;

            Ok(())
        }

        /// Claim a refund for a failed/cancelled presale round.
        /// Only works when the round is inactive AND past its end block.
        #[pallet::call_index(8)]
        #[pallet::weight(T::WeightInfo::collect_funds())]
        pub fn claim_refund(origin: OriginFor<T>, round_id: u32) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let round = Rounds::<T>::get(round_id).ok_or(Error::<T>::RoundNotFound)?;

            // Round must be inactive and past its end block
            ensure!(!round.is_active, Error::<T>::RoundNotRefundable);
            let current_block = frame_system::Pallet::<T>::block_number();
            ensure!(
                current_block >= round.end_block,
                Error::<T>::RoundNotRefundable
            );

            // Get user's contribution
            let contribution =
                Contributions::<T>::get(round_id, &who).ok_or(Error::<T>::NoContribution)?;
            ensure!(
                contribution.total_paid > BalanceOf::<T>::zero(),
                Error::<T>::NoContribution
            );

            let refund_amount = contribution.total_paid;
            let tokens_to_return = contribution.total_purchased;

            // CEI: Clear state FIRST (prevents reentrant double-claim)
            Contributions::<T>::remove(round_id, &who);

            // Decrement RoundRaised and TotalRaised
            RoundRaised::<T>::mutate(round_id, |raised| {
                *raised = raised.checked_sub(&refund_amount).unwrap_or(0u32.into());
            });
            TotalRaised::<T>::mutate(|total| {
                *total = total.checked_sub(&refund_amount).unwrap_or(0u32.into());
            });

            // Interactions: return purchased tokens to escrow, then refund
            let escrow = T::PalletId::get().into_account_truncating();
            if tokens_to_return > BalanceOf::<T>::zero() {
                T::Currency::transfer(
                    &who,
                    &escrow,
                    tokens_to_return,
                    ExistenceRequirement::KeepAlive,
                )
                .map_err(|_| Error::<T>::InsufficientPayment)?;
            }

            // Transfer refund from escrow to user
            T::Currency::transfer(
                &escrow,
                &who,
                refund_amount,
                ExistenceRequirement::KeepAlive,
            )?;

            Self::deposit_event(Event::RefundClaimed {
                round_id,
                account: who,
                amount: refund_amount,
            });

            Ok(())
        }
    }

    pub trait WeightInfo {
        fn create_round() -> frame_support::weights::Weight;
        fn activate_round() -> frame_support::weights::Weight;
        fn deactivate_round() -> frame_support::weights::Weight;
        fn contribute() -> frame_support::weights::Weight;
        fn set_paused() -> frame_support::weights::Weight;
        fn update_whitelist() -> frame_support::weights::Weight;
        fn collect_funds() -> frame_support::weights::Weight;
        fn set_whitelist_required() -> frame_support::weights::Weight;
        fn claim_refund() -> frame_support::weights::Weight;
    }

    pub struct SubstrateWeight<T>(core::marker::PhantomData<T>);
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
        fn collect_funds() -> frame_support::weights::Weight {
            // O(1) — no contributor iteration
            frame_support::weights::Weight::from_parts(15_000, 0)
        }
        fn set_whitelist_required() -> frame_support::weights::Weight {
            frame_support::weights::Weight::from_parts(5_000, 0)
        }
        fn claim_refund() -> frame_support::weights::Weight {
            frame_support::weights::Weight::from_parts(15_000, 0)
        }
    }

    impl<T: Config> Pallet<T> {
        /// Returns the deterministic escrow account for this pallet.
        pub fn escrow_account() -> T::AccountId {
            T::PalletId::get().into_account_truncating()
        }
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
    fn collect_funds() -> frame_support::weights::Weight {
        frame_support::weights::Weight::from_parts(15_000, 0)
    }
    fn set_whitelist_required() -> frame_support::weights::Weight {
        frame_support::weights::Weight::from_parts(5_000, 0)
    }
    fn claim_refund() -> frame_support::weights::Weight {
        frame_support::weights::Weight::from_parts(15_000, 0)
    }
}

#[cfg(test)]
mod tests;

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;
