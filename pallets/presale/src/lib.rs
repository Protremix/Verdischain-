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
//! #[derive(Encode, Decode, DecodeWithMemTracking, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo, Debug)]Verdis Presale Pallet
//!
//! On-chain presale/IDO contribution system with:
//! - **Explicit round state machine**: Pending → Active → Successful/Failed/Cancelled → Closed
//! - **Per-round escrow**: each round has its own deterministic sub-account escrow
//!   account (derived from PalletId), NOT user reserved balances.
//! - Per-round per-account caps (independent per round)
//! - Per-round whitelist (independent per round)
//! - Vesting schedule integration (atomic)
//! - Overflow protection (checked arithmetic throughout — no saturating for financial accounting)
//! - **O(1) fund collection** from per-round escrow (no unbounded contributor iteration)
//! - **Double-collection prevention** via `RoundFundsCollected` flag
//! - **Round-end enforcement**: collection only after `end_block`
//! - **Escrow VRDX balance verification**: contribution fails if escrow lacks tokens
//! - Admin controls (start/stop, whitelist, emergency pause, cancel, finalize)
//! - Atomic accounting (all-or-nothing state changes)
//! - **Refund safety**: collect_funds() CANNOT run on Failed/Cancelled rounds
//!   — users always retain refund rights until admin explicitly finalizes as Successful
//!
//! ##[derive(Encode, Decode, DecodeWithMemTracking, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo, Debug)]State Machine
//! ```text
//! Pending → Active → (end_block reached, admin finalizes)
//!   → Successful (sold >= min_allocation) → collect_funds() → Closed
//!   → Failed (sold < min_allocation) → claim_refund()
//! Active → (admin cancels) → Cancelled → claim_refund()
//! ```
//!
//! ##[derive(Encode, Decode, DecodeWithMemTracking, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo, Debug)]Payment Flow
//! ```text
//! Buyer --payment (PaymentCurrency)--> Per-Round Escrow Account
//! Per-Round Escrow Account --VRDX (Currency)--> Buyer
//! Per-Round Escrow Account --vesting--> Vesting Pallet
//! ```
//!
//! ##[derive(Encode, Decode, DecodeWithMemTracking, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo, Debug)]Collection Flow
//! ```text
//! After round.end_block + admin finalizes as Successful:
//!   Admin calls collect_funds(round_id, beneficiary)
//!   Per-Round Escrow --RoundRaised (PaymentCurrency)--> Beneficiary
//!   RoundFundsCollected = true  (prevents double collection)
//!   Status = Closed
//! ```
//!
//! ##[derive(Encode, Decode, DecodeWithMemTracking, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo, Debug)]Refund Flow (Failed/Cancelled rounds only)
//! ```text
//! User calls claim_refund(round_id):
//!   1. Remove ALL vesting entries for this round's label (unlocks tokens)
//!   2. Transfer purchased tokens back from user → escrow
//!   3. Transfer payment from escrow → user
//!   4. Clean up contribution record
//! ```
//!
//! ##[derive(Encode, Decode, DecodeWithMemTracking, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo, Debug)]Price Formula
//! `token_amount = payment_amount.checked_mul(token_price) / price_precision`

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

        /// Remove a specific vesting entry for `who` matching `schedule_label` and `amount`.
        /// Returns Err if no matching vesting entry exists.
        fn do_remove_vesting(
            who: &AccountId,
            schedule_label: Vec<u8>,
            amount: Balance,
        ) -> DispatchResult;

        /// Remove ALL vesting entries for `who` matching `schedule_label`.
        /// Returns the total unlocked amount, or Err if no matching entries exist.
        /// This is used during refund to clean up multiple contribution vesting entries.
        fn remove_all_vesting_for_label(
            who: &AccountId,
            schedule_label: Vec<u8>,
        ) -> Result<Balance, DispatchError>;
    }

    /// Default no-op implementation (for testing without vesting pallet)
    impl<AccountId, Balance: Zero> VestingHandler<AccountId, Balance> for () {
        fn assign_vesting(_: &AccountId, _: Vec<u8>, _: Balance) -> DispatchResult {
            Ok(())
        }
        fn do_remove_vesting(_: &AccountId, _: Vec<u8>, _: Balance) -> DispatchResult {
            Ok(())
        }
        fn remove_all_vesting_for_label(
            _: &AccountId,
            _: Vec<u8>,
        ) -> Result<Balance, DispatchError> {
            Ok(Balance::zero())
        }
    }

    /// Explicit round status — prevents collect_funds() from running on failed rounds
    #[derive(
        Encode,
        Decode,
        DecodeWithMemTracking,
        Clone,
        PartialEq,
        Eq,
        MaxEncodedLen,
        TypeInfo,
        Debug,
        Default,
    )]
    pub enum RoundStatus {
        /// Created but not yet activated
        #[default]
        Pending,
        /// Accepting contributions
        Active,
        /// Round ended, min_allocation met, funds collectible by admin
        Successful,
        /// Round ended, min_allocation NOT met, refunds available
        Failed,
        /// Admin cancelled before end_block, refunds available immediately
        Cancelled,
        /// Funds collected, round fully resolved
        Closed,
    }

    /// Presale round configuration
    #[derive(
        Encode, Decode, DecodeWithMemTracking, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo, Debug,
    )]
    pub struct SaleRound<Balance, BlockNumber> {
        pub label: BoundedVec<u8, ConstU32<32>>,
        /// Price numerator: token_amount = (payment_amount * token_price) / price_precision
        pub token_price: Balance,
        /// Denominator for price calculation. Default 1 for backward compatibility.
        pub price_precision: Balance,
        pub total_allocation: Balance,
        /// Minimum allocation that must be sold for the round to be Successful.
        /// If sold < min_allocation at end_block, round is Failed.
        /// Set to 0 to accept any amount sold as success.
        pub min_allocation: Balance,
        pub sold: Balance,
        pub per_account_cap: Balance,
        pub start_block: BlockNumber,
        pub end_block: BlockNumber,
        pub vesting_label: BoundedVec<u8, ConstU32<64>>,
        /// Current round status (state machine)
        pub status: RoundStatus,
        /// If true, only whitelisted accounts can contribute
        pub whitelist_required: bool,
    }

    /// User contribution record — per (round_id, account_id)
    #[derive(
        Encode,
        Decode,
        DecodeWithMemTracking,
        Clone,
        PartialEq,
        Eq,
        MaxEncodedLen,
        TypeInfo,
        Debug,
        Default,
    )]
    pub struct UserContribution<Balance> {
        pub total_purchased: Balance,
        pub total_paid: Balance,
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    // === Storage ===

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
        RoundFinalized {
            round_id: u32,
            status: RoundStatus,
            sold: BalanceOf<T>,
        },
        RoundCancelled {
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
        /// Unsold tokens swept to treasury after all refunds
        UnsoldTokensSwept {
            round_id: u32,
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
        /// Vesting label already used by another round (cross-round isolation)
        DuplicateVestingLabel,
        /// Presale escrow does not have enough VRDX to fulfill this contribution
        InsufficientEscrowBalance,
        /// Price precision must be non-zero (P2-04 fix)
        InvalidPricePrecision,
        /// Round is not in the required status for this operation
        RoundStatusInvalid,
        /// Round must be finalized before this operation
        RoundNotFinalized,
        /// Round has already been finalized
        RoundAlreadyFinalized,
        /// Vesting cleanup failed during refund
        VestingCleanupFailed,
        /// Min allocation cannot exceed total allocation
        InvalidMinAllocation,
    }

    // === Config ===

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        /// Token currency - VRDX tokens distributed to buyers.
        type Currency: Currency<Self::AccountId>;
        /// Payment currency - asset buyers pay with.
        /// For testnet, set to the same as Currency (native VRDX bonus-rate presale).
        /// For mainnet, set to a stablecoin or other accepted payment asset.
        type PaymentCurrency: Currency<Self::AccountId, Balance = BalanceOf<Self>>;
        #[pallet::constant]
        type PalletId: Get<PalletId>;
        type AdminOrigin: EnsureOrigin<Self::RuntimeOrigin>;
        type Vesting: VestingHandler<Self::AccountId, BalanceOf<Self>>;
        type WeightInfo: WeightInfo;
        /// Treasury account for sweeping unsold tokens
        type Treasury: Get<Self::AccountId>;
        /// Enforce globally unique vesting labels per round (enable for mainnet)
        type EnforceUniqueVestingLabels: Get<bool>;
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
                    min_allocation: BalanceOf::<T>::zero(), // default: any amount sold = success
                    sold: BalanceOf::<T>::zero(),
                    per_account_cap: *cap,
                    start_block: BlockNumberFor::<T>::from(*start),
                    end_block: BlockNumberFor::<T>::from(*end),
                    vesting_label: vesting_bv,
                    status: RoundStatus::Pending,
                    whitelist_required: false,
                };

                let round_id = NextRoundId::<T>::get();
                Rounds::<T>::insert(round_id, round);
                NextRoundId::<T>::put(round_id + 1);
            }
        }
    }

    // === Extrinsics ===

    // Per-Round Escrow: each round gets its own deterministic sub-account
    // derived from PalletId + round_id. This isolates funds per round so
    // collect_funds for one round cannot drain another round payments.
    impl<T: Config> Pallet<T> {
        fn round_escrow(round_id: u32) -> T::AccountId {
            T::PalletId::get().into_sub_account_truncating(round_id)
        }
    }

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

            // MASTER-6 FIX: Enforce globally unique vesting labels per round.
            // Prevents cross-round vesting deletion: a refund for round A
            // must not remove vesting belonging to round B.
            // Enabled via Config::EnforceUniqueVestingLabels (mainnet only).
            if T::EnforceUniqueVestingLabels::get() {
                let vesting_bv_check: BoundedVec<u8, ConstU32<64>> = vesting_label
                    .clone()
                    .try_into()
                    .map_err(|_| Error::<T>::VestingLabelTooLong)?;
                let current_next = NextRoundId::<T>::get();
                for existing_id in 0..current_next {
                    if let Some(existing_round) = Rounds::<T>::get(existing_id) {
                        ensure!(
                            existing_round.vesting_label != vesting_bv_check,
                            Error::<T>::DuplicateVestingLabel
                        );
                    }
                }
            }

            let round = SaleRound {
                label: label_bv,
                token_price,
                price_precision: <BalanceOf<T> as From<u32>>::from(1u32),
                total_allocation,
                min_allocation: BalanceOf::<T>::zero(),
                sold: BalanceOf::<T>::zero(),
                per_account_cap,
                start_block,
                end_block,
                vesting_label: vesting_bv,
                status: RoundStatus::Pending,
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
                ensure!(
                    round.status == RoundStatus::Pending,
                    Error::<T>::RoundStatusInvalid
                );
                round.status = RoundStatus::Active;
                Self::deposit_event(Event::RoundActivated { round_id });
                Ok(())
            })
        }

        /// Deactivate a sale round (admin only) — pauses contributions without changing state
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::deactivate_round())]
        pub fn deactivate_round(origin: OriginFor<T>, round_id: u32) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;
            // Deactivation is now done via set_paused() or cancel_round()
            // This extrinsic is kept for backward compatibility but does nothing
            // unless the round is Active, in which case it reverts to Pending
            Rounds::<T>::try_mutate(round_id, |round_opt| {
                let round = round_opt.as_mut().ok_or(Error::<T>::RoundNotFound)?;
                ensure!(
                    round.status == RoundStatus::Active,
                    Error::<T>::RoundStatusInvalid
                );
                round.status = RoundStatus::Pending;
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
            ensure!(
                round.status == RoundStatus::Active,
                Error::<T>::RoundNotActive
            );

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
            let gross_amount = payment_amount
                .checked_mul(&round.token_price)
                .ok_or(Error::<T>::CalculationOverflow)?;
            ensure!(
                round.price_precision > BalanceOf::<T>::zero(),
                Error::<T>::InvalidPricePrecision
            );
            let token_amount = gross_amount
                .checked_div(&round.price_precision)
                .ok_or(Error::<T>::CalculationOverflow)?;

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
            let escrow = Self::round_escrow(round_id);
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

            // 7. Update global totals
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

        /// Collect raised funds from a SUCCESSFUL round (admin only).
        ///
        /// O(1) operation — transfers `RoundRaised[round_id]` from the presale
        /// escrow account to the beneficiary. Does NOT iterate over contributors.
        ///
        /// Requirements:
        /// - Round must exist
        /// - Round status must be Successful (admin must call finalize_round first)
        /// - Funds must not have been collected already (no double collection)
        ///
        /// CRITICAL: This function CANNOT run on Failed or Cancelled rounds.
        /// This ensures users always retain refund rights for failed rounds.
        #[pallet::call_index(6)]
        #[pallet::weight(T::WeightInfo::collect_funds())]
        pub fn collect_funds(
            origin: OriginFor<T>,
            round_id: u32,
            beneficiary: T::AccountId,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            let round = Rounds::<T>::get(round_id).ok_or(Error::<T>::RoundNotFound)?;

            // CRITICAL: Only Successful rounds can have funds collected.
            // Failed/Cancelled rounds must allow refunds first.
            ensure!(
                round.status == RoundStatus::Successful,
                Error::<T>::RoundStatusInvalid
            );

            // Prevent double collection
            ensure!(
                !RoundFundsCollected::<T>::get(round_id),
                Error::<T>::FundsAlreadyCollected
            );

            // Get the total raised for this round
            let round_raised = RoundRaised::<T>::get(round_id);

            // Transfer payment funds from per-round escrow to beneficiary
            if round_raised > BalanceOf::<T>::zero() {
                let escrow = Self::round_escrow(round_id);
                T::PaymentCurrency::transfer(
                    &escrow,
                    &beneficiary,
                    round_raised,
                    ExistenceRequirement::AllowDeath,
                )?;
            }

            // Mark funds as collected and close the round
            RoundFundsCollected::<T>::insert(round_id, true);
            Rounds::<T>::mutate(round_id, |round_opt| {
                if let Some(r) = round_opt {
                    r.status = RoundStatus::Closed;
                }
            });

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

        /// Claim a refund for a Failed or Cancelled presale round.
        ///
        /// Requirements:
        /// - Round status must be Failed or Cancelled
        /// - User must have a contribution
        /// - Funds must not have been collected (always true for Failed/Cancelled)
        ///
        /// Flow:
        /// 1. Remove ALL vesting entries for this round's label (unlocks tokens)
        /// 2. Transfer purchased tokens back from user → escrow
        /// 3. Transfer payment from escrow → user
        /// 4. Clean up contribution record (CEI: state cleared first)
        #[pallet::call_index(8)]
        #[pallet::weight(T::WeightInfo::claim_refund())]
        pub fn claim_refund(origin: OriginFor<T>, round_id: u32) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let round = Rounds::<T>::get(round_id).ok_or(Error::<T>::RoundNotFound)?;

            // CRITICAL: Only Failed or Cancelled rounds allow refunds.
            // Successful rounds must go through collect_funds() — users get vested tokens, not refunds.
            ensure!(
                round.status == RoundStatus::Failed || round.status == RoundStatus::Cancelled,
                Error::<T>::RoundNotRefundable
            );

            // Safety: funds should never be collected on a Failed/Cancelled round,
            // but we check anyway as a defense-in-depth measure.
            ensure!(
                !RoundFundsCollected::<T>::get(round_id),
                Error::<T>::FundsAlreadyCollected
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
            let escrow = Self::round_escrow(round_id);

            // FIX P2-4: Verify escrow has sufficient payment balance before mutations
            ensure!(
                T::PaymentCurrency::free_balance(&escrow) >= refund_amount,
                Error::<T>::InsufficientEscrowBalance
            );

            // CEI: Clear state FIRST (prevents reentrant double-claim)
            Contributions::<T>::remove(round_id, &who);

            // Decrement RoundRaised and TotalRaised
            RoundRaised::<T>::mutate(round_id, |raised| {
                *raised = raised.checked_sub(&refund_amount).unwrap_or(0u32.into());
            });
            TotalRaised::<T>::mutate(|total| {
                *total = total.checked_sub(&refund_amount).unwrap_or(0u32.into());
            });

            // === Fix: Remove vesting FIRST, then transfer tokens back ===
            // The old code tried to transfer tokens while they were still locked by vesting.
            // Now we remove all vesting entries for this label first, unlocking the tokens.

            if tokens_to_return > BalanceOf::<T>::zero() && !round.vesting_label.is_empty() {
                // Use remove_all_vesting_for_label to handle multiple contributions correctly.
                // The old code called do_remove_vesting with the cumulative amount, which
                // wouldn't match any individual vesting entry from multiple contributions.
                T::Vesting::remove_all_vesting_for_label(
                    &who,
                    round.vesting_label.clone().into_inner(),
                )
                .map_err(|_| Error::<T>::VestingCleanupFailed)?;
            }

            // Transfer VRDX tokens back from user to per-round escrow
            if tokens_to_return > BalanceOf::<T>::zero() {
                T::Currency::transfer(
                    &who,
                    &escrow,
                    tokens_to_return,
                    ExistenceRequirement::KeepAlive,
                )
                .map_err(|_| Error::<T>::InsufficientPayment)?;
            }

            // Transfer refund (payment tokens) from per-round escrow to user
            T::PaymentCurrency::transfer(
                &escrow,
                &who,
                refund_amount,
                ExistenceRequirement::KeepAlive,
            )?;

            // Fix double-accounting: reduce the round's sold counter by the refunded amount
            let new_round_sold = {
                Rounds::<T>::try_mutate(round_id, |round_opt| -> Result<BalanceOf<T>, Error<T>> {
                    let r = round_opt.as_mut().ok_or(Error::<T>::RoundNotFound)?;
                    r.sold = r
                        .sold
                        .checked_sub(&tokens_to_return)
                        .ok_or(Error::<T>::CalculationOverflow)?;
                    Ok(r.sold)
                })?
            };

            // Reduce global TotalSold counter
            TotalSold::<T>::mutate(|total| {
                *total = total.checked_sub(&tokens_to_return).unwrap_or(0u32.into());
            });

            // If all tokens in this round are refunded (sold == 0), sweep remaining
            // unsold tokens from escrow back to treasury
            if new_round_sold.is_zero() {
                let treasury = T::Treasury::get();
                let escrow_balance = T::Currency::free_balance(&escrow);
                let sweep_amount = if escrow_balance >= round.total_allocation {
                    round.total_allocation
                } else {
                    escrow_balance
                };
                if sweep_amount > BalanceOf::<T>::zero() {
                    let _ = T::Currency::transfer(
                        &escrow,
                        &treasury,
                        sweep_amount,
                        ExistenceRequirement::AllowDeath,
                    );
                    Self::deposit_event(Event::UnsoldTokensSwept {
                        round_id,
                        amount: sweep_amount,
                    });
                }
            }

            Self::deposit_event(Event::RefundClaimed {
                round_id,
                account: who,
                amount: refund_amount,
            });

            Ok(())
        }

        /// Finalize a round after end_block (admin only).
        ///
        /// Automatically determines if the round was Successful or Failed based on
        /// whether `sold >= min_allocation`. This must be called before collect_funds()
        /// or claim_refund() can be used.
        ///
        /// Requirements:
        /// - Round must exist
        /// - Round status must be Active
        /// - Current block must be >= round.end_block
        #[pallet::call_index(9)]
        #[pallet::weight(T::WeightInfo::activate_round())]
        pub fn finalize_round(origin: OriginFor<T>, round_id: u32) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            Rounds::<T>::try_mutate(round_id, |round_opt| {
                let round = round_opt.as_mut().ok_or(Error::<T>::RoundNotFound)?;

                ensure!(
                    round.status == RoundStatus::Active,
                    Error::<T>::RoundAlreadyFinalized
                );

                let current_block = frame_system::Pallet::<T>::block_number();
                ensure!(current_block >= round.end_block, Error::<T>::RoundNotEnded);

                // Determine success/failure based on min_allocation
                let new_status = if round.sold >= round.min_allocation {
                    RoundStatus::Successful
                } else {
                    RoundStatus::Failed
                };

                let sold = round.sold;
                round.status = new_status.clone();

                Self::deposit_event(Event::RoundFinalized {
                    round_id,
                    status: new_status,
                    sold,
                });

                Ok(())
            })
        }

        /// Cancel an active round (admin only).
        ///
        /// Immediately sets the round status to Cancelled, allowing refunds
        /// without waiting for end_block. Used when admin needs to abort a round
        /// due to issues (e.g., security concerns, insufficient interest).
        ///
        /// Requirements:
        /// - Round must exist
        /// - Round status must be Active (can only cancel active rounds)
        #[pallet::call_index(10)]
        #[pallet::weight(T::WeightInfo::activate_round())]
        pub fn cancel_round(origin: OriginFor<T>, round_id: u32) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            Rounds::<T>::try_mutate(round_id, |round_opt| {
                let round = round_opt.as_mut().ok_or(Error::<T>::RoundNotFound)?;

                ensure!(
                    round.status == RoundStatus::Active,
                    Error::<T>::RoundStatusInvalid
                );

                round.status = RoundStatus::Cancelled;

                Self::deposit_event(Event::RoundCancelled { round_id });

                Ok(())
            })
        }

        /// Set the minimum allocation for a round (admin only).
        ///
        /// Must be called while the round is still Pending (before activation).
        /// min_allocation determines whether the round is Successful or Failed
        /// when finalized.
        ///
        /// Requirements:
        /// - Round must exist
        /// - Round status must be Pending
        /// - min_allocation <= total_allocation
        #[pallet::call_index(11)]
        #[pallet::weight(T::WeightInfo::activate_round())]
        pub fn set_min_allocation(
            origin: OriginFor<T>,
            round_id: u32,
            min_allocation: BalanceOf<T>,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            Rounds::<T>::try_mutate(round_id, |round_opt| {
                let round = round_opt.as_mut().ok_or(Error::<T>::RoundNotFound)?;

                ensure!(
                    round.status == RoundStatus::Pending,
                    Error::<T>::RoundStatusInvalid
                );

                ensure!(
                    min_allocation <= round.total_allocation,
                    Error::<T>::InvalidMinAllocation
                );

                round.min_allocation = min_allocation;

                Ok(())
            })
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
            // Weight accounts for: contribution lookup, vesting removal
            // (iterates all vesting entries for user), multiple transfers,
            // state cleanup, potential treasury sweep.
            // Base: 15,000 + vesting iteration: 5,000 * max 20 entries = 100,000
            // Total: 115,000 (conservative upper bound)
            frame_support::weights::Weight::from_parts(115_000, 0)
        }
    }

    impl<T: Config> Pallet<T> {
        /// Returns the escrow account for round 0 (backward compat).
        /// Use round_escrow(round_id) for per-round escrow accounts.
        pub fn escrow_account() -> T::AccountId {
            Self::round_escrow(0)
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
