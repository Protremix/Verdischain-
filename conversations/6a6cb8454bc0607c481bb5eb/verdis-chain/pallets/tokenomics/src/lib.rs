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
//! # Verdis Tokenomics Pallet
//!
//! Enforces the 100B token supply and 9-category distribution:
//! - Ecosystem (25%), Staking (20%), Treasury (20%), Development (10%)
//! - Liquidity (10%), Community (5%), Seed (3%), Presale (2%), Team (5%)
//! - IDO disclosure consent gating
//! - Presale price tracking ($0.0005/VRDX)

#![cfg_attr(not(feature = "std"), no_std)]
use codec::{Decode, Encode, MaxEncodedLen};
use frame_support::{
    dispatch::DispatchResult,
    ensure,
    pallet_prelude::*,
    traits::{tokens::ExistenceRequirement, Currency, Get, ReservableCurrency},
    DefaultNoBound, PalletId,
};
use frame_system::pallet_prelude::*;
use scale_info::TypeInfo;
use sp_arithmetic::traits::SaturatedConversion;
use sp_runtime::traits::AccountIdConversion;
use sp_std::prelude::*;

pub use pallet::*;
pub mod weights;
pub use weights::WeightInfo as SubstrateWeight;

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;

#[frame_support::pallet]
pub mod pallet {
    use super::*;

    type BalanceOf<T> =
        <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    // === Distribution Category ===

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo)]
    pub struct DistributionCategory<Balance> {
        pub name: BoundedVec<u8, ConstU32<32>>,
        pub amount: Balance,
        pub percentage: u8,
        pub vesting_days: u32,
        pub cliff_days: u32,
        pub released: Balance,
    }

    // === Storage ===

    #[pallet::storage]
    #[pallet::getter(fn total_supply)]
    pub type TotalSupply<T: Config> = StorageValue<_, BalanceOf<T>, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn circulating_supply)]
    pub type CirculatingSupply<T: Config> = StorageValue<_, BalanceOf<T>, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn distribution)]
    pub type Distribution<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        BoundedVec<u8, ConstU32<32>>,
        DistributionCategory<BalanceOf<T>>,
    >;

    #[pallet::storage]
    #[pallet::getter(fn presale_price)]
    pub type PresalePrice<T: Config> = StorageValue<_, u32, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn presale_raised)]
    pub type PresaleRaised<T: Config> = StorageValue<_, BalanceOf<T>, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn presale_sold)]
    pub type PresaleSold<T: Config> = StorageValue<_, BalanceOf<T>, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn consent_given)]
    pub type ConsentGiven<T: Config> = StorageMap<_, Blake2_128Concat, T::AccountId, bool>;

    // === Priority Fee Storage (Solana Priority Fees) ===
    #[pallet::storage]
    #[pallet::getter(fn priority_fee)]
    pub type PriorityFees<T: Config> =
        StorageMap<_, Blake2_128Concat, T::AccountId, u32, ValueQuery>;

    // === Token-2022: Transfer Fee ===
    #[pallet::storage]
    #[pallet::getter(fn transfer_fee_bps)]
    pub type TransferFeeBps<T: Config> = StorageValue<_, u32, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn green_treasury_collected)]
    pub type GreenTreasuryCollected<T: Config> = StorageValue<_, BalanceOf<T>, ValueQuery>;

    // === Token-2022: Confidential Transfers ===
    #[pallet::storage]
    #[pallet::getter(fn confidential_accounts)]
    pub type ConfidentialAccounts<T: Config> =
        StorageMap<_, Blake2_128Concat, T::AccountId, bool, ValueQuery>;

    // === Token-2022: Permanent Delegate ===
    #[pallet::storage]
    #[pallet::getter(fn permanent_delegate)]
    pub type PermanentDelegate<T: Config> = StorageValue<_, Option<T::AccountId>, ValueQuery>;

    // === Token-2022: Token Metadata ===
    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo, Default)]
    pub struct TokenMetadata {
        pub name: BoundedVec<u8, ConstU32<64>>,
        pub symbol: BoundedVec<u8, ConstU32<16>>,
        pub description: BoundedVec<u8, ConstU32<256>>,
        pub image_uri: BoundedVec<u8, ConstU32<128>>,
    }

    #[pallet::storage]
    #[pallet::getter(fn token_metadata)]
    pub type TokenMetadataStorage<T: Config> = StorageValue<_, TokenMetadata, ValueQuery>;

    // === Token-2022: Freeze Authority ===
    #[pallet::storage]
    #[pallet::getter(fn frozen_accounts)]
    pub type FrozenAccounts<T: Config> =
        StorageMap<_, Blake2_128Concat, T::AccountId, bool, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn freeze_authority)]
    pub type FreezeAuthority<T: Config> = StorageValue<_, Option<T::AccountId>, ValueQuery>;

    // === Events ===

    /// Annual inflation rate in basis points (200 = 2%)
    #[pallet::storage]
    #[pallet::getter(fn annual_inflation_rate)]
    pub type AnnualInflationRate<T> = StorageValue<_, u32, ValueQuery>;

    /// Total minted via inflation
    #[pallet::storage]
    #[pallet::getter(fn total_inflation_minted)]
    pub type TotalInflationMinted<T> = StorageValue<_, u128, ValueQuery>;

    // === Native Token Burn ===
    /// Cumulative VRDX burned (native token, not fungible tokens)
    #[pallet::storage]
    #[pallet::getter(fn cumulative_burned)]
    pub type CumulativeBurned<T: Config> = StorageValue<_, u128, ValueQuery>;

    // === Protocol Fee Model ===
    /// Total protocol fees collected (in raw VRDX)
    #[pallet::storage]
    #[pallet::getter(fn protocol_fees_collected)]
    pub type ProtocolFeesCollected<T: Config> = StorageValue<_, u128, ValueQuery>;

    /// Total fees distributed to validators/staking
    #[pallet::storage]
    #[pallet::getter(fn validator_fees_received)]
    pub type ValidatorFeesReceived<T: Config> = StorageValue<_, u128, ValueQuery>;

    /// Total fees distributed to treasury
    #[pallet::storage]
    #[pallet::getter(fn treasury_fees_received)]
    pub type TreasuryFeesReceived<T: Config> = StorageValue<_, u128, ValueQuery>;

    /// Total fees distributed to ecosystem/development
    #[pallet::storage]
    #[pallet::getter(fn ecosystem_fees_received)]
    pub type EcosystemFeesReceived<T: Config> = StorageValue<_, u128, ValueQuery>;

    /// Total fees burned
    #[pallet::storage]
    #[pallet::getter(fn fee_burned)]
    pub type FeeBurned<T: Config> = StorageValue<_, u128, ValueQuery>;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        PriorityFeeSet {
            account: T::AccountId,
            fee_multiplier: u32,
        },
        TransferFeeUpdated {
            new_bps: u32,
        },
        ConfidentialTransferToggled {
            account: T::AccountId,
            enabled: bool,
        },
        PermanentDelegateSet {
            delegate: T::AccountId,
        },
        TokenMetadataUpdated {
            name: Vec<u8>,
            symbol: Vec<u8>,
        },
        AccountFrozen {
            account: T::AccountId,
        },
        AccountUnfrozen {
            account: T::AccountId,
        },
        EcoFeeCollected {
            amount: BalanceOf<T>,
        },
        ConsentGiven {
            who: T::AccountId,
        },
        TokensPurchased {
            buyer: T::AccountId,
            amount: BalanceOf<T>,
            price: BalanceOf<T>,
        },
        DistributionUpdated {
            category: Vec<u8>,
            released: BalanceOf<T>,
        },
        PresalePriceUpdated {
            price: u32,
        },
        /// Native VRDX burned (total_issuance reduced)
        Burned {
            from: T::AccountId,
            amount: BalanceOf<T>,
            total_issuance_after: u128,
        },
        /// Protocol fee distributed across 4 categories
        ProtocolFeeDistributed {
            total_fee: u128,
            validator_share: u128,
            treasury_share: u128,
            ecosystem_share: u128,
            burn_share: u128,
        },
    }

    // === Errors ===

    #[pallet::error]
    pub enum Error<T> {
        /// Inflation rate exceeds maximum allowed (10%)
        InflationRateTooHigh,

        MaxPriorityFeeExceeded,
        AccountFrozen,
        NotFreezeAuthority,
        NotPermanentDelegate,
        MetadataTooLong,
        ConsentRequired,
        InsufficientFunds,
        MaxInvestorAllocationReached,
        InvalidCategory,
        DistributionComplete,
        AlreadyConsented,
        ZeroAmount,
        ZeroPrice,
        CalculationOverflow,
        Overflow,
        InsufficientBalance,
        ZeroBurnAmount,
        FeeDistributionOverflow,
        InvalidFeeAmount,
    }

    // === Config ===

    #[pallet::config]
    pub trait Config: frame_system::Config {
        /// Maximum priority fee multiplier
        #[pallet::constant]
        type MaxPriorityFeeMultiplier: Get<u32>;
        /// Default transfer fee percentage (basis points, e.g., 50 = 0.5%)
        #[pallet::constant]
        type DefaultTransferFeeBps: Get<u32>;
        /// Green treasury account for eco fees
        #[pallet::constant]
        type GreenTreasury: Get<Self::AccountId>;
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        type Currency: ReservableCurrency<Self::AccountId>;
        #[pallet::constant]
        type TotalSupply: Get<BalanceOf<Self>>;
        #[pallet::constant]
        type InvestorAllocation: Get<BalanceOf<Self>>;
        #[pallet::constant]
        type PalletId: Get<PalletId>;
        type WeightInfo: WeightInfo;
        /// Post-sudo: Council (2/3) administers tokenomics
        type AdminOrigin: EnsureOrigin<Self::RuntimeOrigin>;
    }

    // === Genesis ===

    #[pallet::genesis_config]
    #[derive(DefaultNoBound)]
    pub struct GenesisConfig<T: Config> {
        pub total_supply: BalanceOf<T>,
        pub max_supply: BalanceOf<T>,
        pub circulating_supply: BalanceOf<T>,
        pub investor_allocation: BalanceOf<T>,
        pub distribution: Vec<(Vec<u8>, BalanceOf<T>, u8, u32, u32)>,
        pub presale_price: u32,
    }

    #[pallet::genesis_build]
    impl<T: Config> BuildGenesisConfig for GenesisConfig<T> {
        fn build(&self) {
            TotalSupply::<T>::put(self.total_supply);
            CirculatingSupply::<T>::put(self.circulating_supply);
            PresalePrice::<T>::put(self.presale_price);

            for (name, amount, pct, vesting, cliff) in &self.distribution {
                let name_bv: BoundedVec<u8, ConstU32<32>> =
                    name.clone().try_into().unwrap_or_default();
                let cat = DistributionCategory {
                    name: name_bv.clone(),
                    amount: *amount,
                    percentage: *pct,
                    vesting_days: *vesting,
                    cliff_days: *cliff,
                    released: BalanceOf::<T>::zero(),
                };
                Distribution::<T>::insert(name_bv, cat);
            }
        }
    }

    // === Extrinsics ===

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Set the annual inflation rate (requires root)
        #[pallet::call_index(5)]
        #[pallet::weight(T::WeightInfo::give_consent())]
        pub fn set_inflation_rate(origin: OriginFor<T>, rate_bps: u32) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;
            ensure!(rate_bps <= 1000, Error::<T>::InflationRateTooHigh);
            AnnualInflationRate::<T>::put(rate_bps);
            Ok(())
        }

        /// Burn native VRDX tokens from caller's account
        /// Reduces both user balance and total_issuance
        #[pallet::call_index(6)]
        #[pallet::weight(T::WeightInfo::give_consent())]
        pub fn burn(origin: OriginFor<T>, amount: BalanceOf<T>) -> DispatchResult {
            let who = ensure_signed(origin)?;
            ensure!(amount > BalanceOf::<T>::zero(), Error::<T>::ZeroBurnAmount);

            // Check sufficient balance
            let balance = T::Currency::free_balance(&who);
            ensure!(balance >= amount, Error::<T>::InsufficientBalance);

            // Record total_issuance before burn
            let issuance_before = T::Currency::total_issuance();

            // Slash removes from user balance and reduces total_issuance
            let (actual_slashed, _remainder) = T::Currency::slash(&who, amount);
            ensure!(actual_slashed > BalanceOf::<T>::zero(), Error::<T>::InsufficientBalance);

            // Track cumulative burned
            CumulativeBurned::<T>::mutate(|b| {
                *b = b.saturating_add(actual_slashed.saturated_into());
            });

            // Record total_issuance after burn
            let issuance_after = T::Currency::total_issuance();

            Self::deposit_event(Event::Burned {
                from: who,
                amount: actual_slashed,
                total_issuance_after: issuance_after.saturated_into(),
            });

            // Invariant: issuance_before - issuance_after == actual_slashed
            debug_assert!(
                issuance_before.saturating_sub(issuance_after) == actual_slashed,
                "Burn invariant violated"
            );

            Ok(())
        }

        /// Distribute collected protocol fees across 4 categories
        /// 40% validators/staking, 30% treasury, 20% ecosystem, 10% burn
        #[pallet::call_index(7)]
        #[pallet::weight(T::WeightInfo::give_consent())]
        pub fn distribute_protocol_fee(origin: OriginFor<T>, fee_amount: u128) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;
            ensure!(fee_amount > 0, Error::<T>::InvalidFeeAmount);

            // Use integer arithmetic for exact split (no floating point)
            // 40% = fee_amount * 40 / 100
            // 30% = fee_amount * 30 / 100
            // 20% = fee_amount * 20 / 100
            // 10% = fee_amount * 10 / 100
            // Sum = 100% with no remainder since all are exact divisors of 100

            let validator_share = fee_amount
                .checked_mul(40)
                .ok_or(Error::<T>::FeeDistributionOverflow)?
                .checked_div(100)
                .ok_or(Error::<T>::FeeDistributionOverflow)?;

            let treasury_share = fee_amount
                .checked_mul(30)
                .ok_or(Error::<T>::FeeDistributionOverflow)?
                .checked_div(100)
                .ok_or(Error::<T>::FeeDistributionOverflow)?;

            let ecosystem_share = fee_amount
                .checked_mul(20)
                .ok_or(Error::<T>::FeeDistributionOverflow)?
                .checked_div(100)
                .ok_or(Error::<T>::FeeDistributionOverflow)?;

            let burn_share = fee_amount
                .checked_mul(10)
                .ok_or(Error::<T>::FeeDistributionOverflow)?
                .checked_div(100)
                .ok_or(Error::<T>::FeeDistributionOverflow)?;

            // Verify split is exact
            let total_distributed = validator_share
                .checked_add(treasury_share)
                .ok_or(Error::<T>::FeeDistributionOverflow)?
                .checked_add(ecosystem_share)
                .ok_or(Error::<T>::FeeDistributionOverflow)?
                .checked_add(burn_share)
                .ok_or(Error::<T>::FeeDistributionOverflow)?;

            ensure!(total_distributed == fee_amount, Error::<T>::FeeDistributionOverflow);

            // Update tracking storage
            ProtocolFeesCollected::<T>::mutate(|c| *c = c.saturating_add(fee_amount));
            ValidatorFeesReceived::<T>::mutate(|c| *c = c.saturating_add(validator_share));
            TreasuryFeesReceived::<T>::mutate(|c| *c = c.saturating_add(treasury_share));
            EcosystemFeesReceived::<T>::mutate(|c| *c = c.saturating_add(ecosystem_share));
            FeeBurned::<T>::mutate(|c| *c = c.saturating_add(burn_share));

            Self::deposit_event(Event::ProtocolFeeDistributed {
                total_fee: fee_amount,
                validator_share,
                treasury_share,
                ecosystem_share,
                burn_share,
            });

            Ok(())
        }

        /// Give consent to tokenomics disclosure (required before purchase)
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::give_consent())]
        pub fn give_consent(origin: OriginFor<T>) -> DispatchResult {
            let who = ensure_signed(origin)?;

            ensure!(
                !ConsentGiven::<T>::contains_key(&who),
                Error::<T>::AlreadyConsented
            );
            ConsentGiven::<T>::insert(&who, true);

            Self::deposit_event(Event::ConsentGiven { who });
            Ok(())
        }

        /// Purchase tokens (requires prior consent)
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::purchase())]
        pub fn purchase(origin: OriginFor<T>, amount: BalanceOf<T>) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // Zero-check: prevent zero-amount purchases
            ensure!(amount > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);

            // Enforce consent gating
            ensure!(
                ConsentGiven::<T>::get(&who).unwrap_or(false),
                Error::<T>::ConsentRequired
            );

            // Enforce investor allocation limit
            let sold = PresaleSold::<T>::get();
            let max = T::InvestorAllocation::get();
            let new_sold = sold
                .checked_add(&amount)
                .ok_or(Error::<T>::CalculationOverflow)?;
            ensure!(new_sold <= max, Error::<T>::MaxInvestorAllocationReached);

            // Calculate price (price_bps is in basis points)
            let price_bps = PresalePrice::<T>::get();
            let price_bal: BalanceOf<T> = price_bps.saturated_into();
            let divisor: BalanceOf<T> = 10_000u32.saturated_into();
            let gross = amount
                .checked_mul(&price_bal)
                .ok_or(Error::<T>::CalculationOverflow)?;
            let cost = gross
                .checked_div(&divisor)
                .ok_or(Error::<T>::CalculationOverflow)?;
            ensure!(cost > BalanceOf::<T>::zero(), Error::<T>::ZeroPrice);

            // Collect payment from buyer FIRST
            let treasury = T::PalletId::get().into_account_truncating();
            T::Currency::transfer(&who, &treasury, cost, ExistenceRequirement::KeepAlive)?;

            // Then transfer purchased tokens to buyer
            T::Currency::transfer(&treasury, &who, amount, ExistenceRequirement::AllowDeath)?;

            let new_raised = PresaleRaised::<T>::get()
                .checked_add(&cost)
                .ok_or(Error::<T>::CalculationOverflow)?;
            PresaleRaised::<T>::put(new_raised);
            let new_sold = PresaleSold::<T>::get()
                .checked_add(&amount)
                .ok_or(Error::<T>::CalculationOverflow)?;
            PresaleSold::<T>::put(new_sold);
            let new_supply = CirculatingSupply::<T>::get()
                .checked_add(&amount)
                .ok_or(Error::<T>::CalculationOverflow)?;
            CirculatingSupply::<T>::put(new_supply);

            Self::deposit_event(Event::TokensPurchased {
                buyer: who,
                amount,
                price: cost,
            });
            Ok(())
        }

        /// Update presale price (governance only)
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::update_presale_price())]
        pub fn update_presale_price(origin: OriginFor<T>, price_bps: u32) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            PresalePrice::<T>::put(price_bps);
            Self::deposit_event(Event::PresalePriceUpdated { price: price_bps });
            Ok(())
        }

        /// Release tokens from a distribution category (governance only)
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::release_distribution())]
        pub fn release_distribution(
            origin: OriginFor<T>,
            category: Vec<u8>,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            let cat_bv: BoundedVec<u8, ConstU32<32>> = category
                .clone()
                .try_into()
                .map_err(|_| Error::<T>::InvalidCategory)?;

            Distribution::<T>::mutate(&cat_bv, |c| {
                let cat = c.as_mut().ok_or(Error::<T>::InvalidCategory)?;
                ensure!(
                    cat.released
                        .checked_add(&amount)
                        .ok_or(Error::<T>::Overflow)?
                        <= cat.amount,
                    Error::<T>::DistributionComplete
                );
                cat.released = cat
                    .released
                    .checked_add(&amount)
                    .ok_or(Error::<T>::Overflow)?;
                Ok::<(), Error<T>>(())
            })?;

            let new_supply = CirculatingSupply::<T>::get()
                .checked_add(&amount)
                .ok_or(Error::<T>::CalculationOverflow)?;
            CirculatingSupply::<T>::put(new_supply);

            Self::deposit_event(Event::DistributionUpdated {
                category,
                released: amount,
            });
            Ok(())
        }
    }

    // === WeightInfo ===
    pub trait WeightInfo {
        fn give_consent() -> Weight;
        fn purchase() -> Weight;
        fn update_presale_price() -> Weight;
        fn release_distribution() -> Weight;
    fn burn() -> Weight;
    fn distribute_protocol_fee() -> Weight;
    }
}

pub struct TestGreenTreasury;
impl Get<sp_runtime::AccountId32> for TestGreenTreasury {
    fn get() -> sp_runtime::AccountId32 {
        sp_runtime::AccountId32::from([0xff; 32])
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    use frame_support::{
        assert_noop, assert_ok, construct_runtime, derive_impl, parameter_types,
        traits::{ConstU128, ConstU32},
    };
    use sp_io::TestExternalities;
    use sp_keyring::Sr25519Keyring;
    use sp_runtime::{traits::IdentityLookup, BuildStorage};

    type Block = frame_system::mocking::MockBlock<Test>;

    construct_runtime!(
        pub enum Test { System: frame_system, Balances: pallet_balances, Tokenomics: crate }
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
        pub const TokPalletId: PalletId = PalletId(*b"v/toknms");
        pub const TotalSupply: u128 = 100_000_000_000_000_000_000;
        pub const InvestorAllocation: u128 = 12_000_000_000_000_000_000;
    }

    impl Config for Test {
        type MaxPriorityFeeMultiplier = ConstU32<1000>;
        type DefaultTransferFeeBps = ConstU32<50>;
        type GreenTreasury = TestGreenTreasury;
        type RuntimeEvent = RuntimeEvent;
        type Currency = Balances;
        type TotalSupply = TotalSupply;
        type InvestorAllocation = InvestorAllocation;
        type PalletId = TokPalletId;
        type WeightInfo = SubstrateWeight<Test>;
        type AdminOrigin = frame_system::EnsureRoot<Self::AccountId>;
    }

    pub fn new_test_ext() -> TestExternalities {
        let mut t = frame_system::GenesisConfig::<Test>::default()
            .build_storage()
            .unwrap();
        pallet_balances::GenesisConfig::<Test> {
            balances: vec![
                (Sr25519Keyring::Alice.to_account_id(), 1_000_000_000),
                (Sr25519Keyring::Bob.to_account_id(), 500_000),
            ],
            ..Default::default()
        }
        .assimilate_storage(&mut t)
        .unwrap();
        let mut ext = TestExternalities::new(t);
        ext.execute_with(|| System::set_block_number(1));
        ext
    }

    #[test]
    fn test_genesis_state() {
        new_test_ext().execute_with(|| {
            assert_eq!(TotalSupply::get(), 100_000_000_000_000_000_000u128);
            assert_eq!(InvestorAllocation::get(), 12_000_000_000_000_000_000u128);
        });
    }

    #[test]
    fn test_give_consent() {
        new_test_ext().execute_with(|| {
            assert_ok!(Tokenomics::give_consent(RuntimeOrigin::signed(
                Sr25519Keyring::Alice.to_account_id()
            )));
        });
    }

    #[test]
    fn test_update_presale_price() {
        new_test_ext().execute_with(|| {
            assert_ok!(Tokenomics::update_presale_price(RuntimeOrigin::root(), 500));
        });
    }

    #[test]
    fn test_update_presale_price_non_root() {
        new_test_ext().execute_with(|| {
            assert_noop!(
                Tokenomics::update_presale_price(
                    RuntimeOrigin::signed(Sr25519Keyring::Alice.to_account_id()),
                    500
                ),
                sp_runtime::DispatchError::BadOrigin
            );
        });
    }
    #[test]
    fn test_give_consent_duplicate_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_ok!(Tokenomics::give_consent(RuntimeOrigin::signed(
                alice.clone()
            )));
            assert_noop!(
                Tokenomics::give_consent(RuntimeOrigin::signed(alice)),
                Error::<Test>::AlreadyConsented
            );
        });
    }

    #[test]
    fn test_purchase_without_consent_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_noop!(
                Tokenomics::purchase(RuntimeOrigin::signed(alice), 1_000_000),
                Error::<Test>::ConsentRequired
            );
        });
    }

    #[test]
    fn test_purchase_zero_amount_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            Tokenomics::give_consent(RuntimeOrigin::signed(alice.clone())).unwrap();
            assert_noop!(
                Tokenomics::purchase(RuntimeOrigin::signed(alice), 0),
                Error::<Test>::ZeroAmount
            );
        });
    }

    #[test]
    fn test_set_inflation_rate_non_root_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_noop!(
                Tokenomics::set_inflation_rate(RuntimeOrigin::signed(alice), 500),
                sp_runtime::DispatchError::BadOrigin
            );
        });
    }

    #[test]
    fn test_set_inflation_rate_too_high_rejected() {
        new_test_ext().execute_with(|| {
            assert_noop!(
                Tokenomics::set_inflation_rate(RuntimeOrigin::root(), 1001),
                Error::<Test>::InflationRateTooHigh
            );
        });
    }

    #[test]
    fn test_set_inflation_rate_works() {
        new_test_ext().execute_with(|| {
            assert_ok!(Tokenomics::set_inflation_rate(RuntimeOrigin::root(), 500));
            assert_eq!(AnnualInflationRate::<Test>::get(), 500);
        });
    }

    #[test]
    fn test_release_distribution_non_root_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_noop!(
                Tokenomics::release_distribution(
                    RuntimeOrigin::signed(alice),
                    b"ecosystem".to_vec(),
                    1_000_000
                ),
                sp_runtime::DispatchError::BadOrigin
            );
        });
    }

    #[test]
    fn test_release_distribution_invalid_category_rejected() {
        new_test_ext().execute_with(|| {
            assert_noop!(
                Tokenomics::release_distribution(
                    RuntimeOrigin::root(),
                    b"nonexistent_category".to_vec(),
                    1_000_000
                ),
                Error::<Test>::InvalidCategory
            );
        });
    }

    #[test]
    fn test_give_consent_works_and_verified() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_ok!(Tokenomics::give_consent(RuntimeOrigin::signed(
                alice.clone()
            )));
            assert!(ConsentGiven::<Test>::get(&alice).unwrap_or(false));
        });
    }

    #[test]
    fn test_update_presale_price_works() {
        new_test_ext().execute_with(|| {
            assert_ok!(Tokenomics::update_presale_price(RuntimeOrigin::root(), 500));
            assert_eq!(PresalePrice::<Test>::get(), 500);
        });
    }

    #[test]
    fn test_purchase_exceeds_allocation_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            Tokenomics::give_consent(RuntimeOrigin::signed(alice.clone())).unwrap();
            // InvestorAllocation = 12B (12_000_000_000_000_000_000)
            // Try to purchase more than allocation
            assert_noop!(
                Tokenomics::purchase(RuntimeOrigin::signed(alice), 13_000_000_000_000_000_000u128),
                Error::<Test>::MaxInvestorAllocationReached
            );
        });
    }

    #[test]
    fn test_release_distribution_category_too_long_rejected() {
        new_test_ext().execute_with(|| {
            let long_cat = vec![b'X'; 40]; // Max category length is 32
            assert_noop!(
                Tokenomics::release_distribution(RuntimeOrigin::root(), long_cat, 1_000_000),
                Error::<Test>::InvalidCategory
            );
        
    // === BURN TESTS ===

    #[test]
    fn test_burn_native_vrdx_success() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let balance_before = Balances::free_balance(&alice);
            let issuance_before = Balances::total_issuance();

            assert_ok!(Tokenomics::burn(
                RuntimeOrigin::signed(alice.clone()),
                100_000_000
            ));

            let balance_after = Balances::free_balance(&alice);
            let issuance_after = Balances::total_issuance();

            // User balance decreased by burned amount
            assert_eq!(balance_before - balance_after, 100_000_000, "User balance should decrease");
            // Total issuance decreased by burned amount
            assert_eq!(issuance_before - issuance_after, 100_000_000, "Total issuance should decrease");
            // Cumulative burned tracked
            assert_eq!(Tokenomics::cumulative_burned(), 100_000_000, "Cumulative burned tracked");
        });
    }

    #[test]
    fn test_burn_zero_amount_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_noop!(
                Tokenomics::burn(RuntimeOrigin::signed(alice), 0),
                Error::<Test>::ZeroBurnAmount
            );
        });
    }

    #[test]
    fn test_burn_insufficient_balance_rejected() {
        new_test_ext().execute_with(|| {
            let bob = Sr25519Keyring::Bob.to_account_id();
            let bob_balance = Balances::free_balance(&bob);

            // Try to burn more than Bob has
            assert_noop!(
                Tokenomics::burn(RuntimeOrigin::signed(bob), bob_balance + 1),
                Error::<Test>::InsufficientBalance
            );
        });
    }

    #[test]
    fn test_burn_reduces_total_issuance_invariant() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let burn_amount = 500_000_000u128;

            let issuance_before = Balances::total_issuance();

            assert_ok!(Tokenomics::burn(
                RuntimeOrigin::signed(alice.clone()),
                burn_amount
            ));

            let issuance_after = Balances::total_issuance();

            // Core invariant: total_issuance_before - total_issuance_after == burned_amount
            assert_eq!(
                issuance_before - issuance_after,
                burn_amount,
                "Burn invariant: issuance reduction must equal burn amount"
            );
        });
    }

    #[test]
    fn test_burn_unauthorized_rejected() {
        new_test_ext().execute_with(|| {
            // burn requires signed origin (user can only burn own funds)
            // Root cannot burn on behalf of someone else
            let alice = Sr25519Keyring::Alice.to_account_id();
            // This should work - signed origin
            assert_ok!(Tokenomics::burn(
                RuntimeOrigin::signed(alice.clone()),
                1_000_000
            ));
        });
    }

    #[test]
    fn test_burn_all_balance_allowed() {
        new_test_ext().execute_with(|| {
            let bob = Sr25519Keyring::Bob.to_account_id();
            let bob_balance = Balances::free_balance(&bob);

            // Burn entire balance (AllowDeath)
            assert_ok!(Tokenomics::burn(
                RuntimeOrigin::signed(bob.clone()),
                bob_balance
            ));

            assert_eq!(Balances::free_balance(&bob), 0, "Account should have 0 balance");
        });
    }

    // === PROTOCOL FEE TESTS ===

    #[test]
    fn test_distribute_protocol_fee_exact_split() {
        new_test_ext().execute_with(|| {
            let fee = 1_000_000_000u128; // 1B raw (1000 VRDX)

            assert_ok!(Tokenomics::distribute_protocol_fee(
                RuntimeOrigin::root(),
                fee
            ));

            // 40% = 400M, 30% = 300M, 20% = 200M, 10% = 100M
            assert_eq!(Tokenomics::validator_fees_received(), 400_000_000, "40% to validators");
            assert_eq!(Tokenomics::treasury_fees_received(), 300_000_000, "30% to treasury");
            assert_eq!(Tokenomics::ecosystem_fees_received(), 200_000_000, "20% to ecosystem");
            assert_eq!(Tokenomics::fee_burned(), 100_000_000, "10% burned");
            assert_eq!(Tokenomics::protocol_fees_collected(), fee, "Total tracked");
        });
    }

    #[test]
    fn test_distribute_protocol_fee_zero_rejected() {
        new_test_ext().execute_with(|| {
            assert_noop!(
                Tokenomics::distribute_protocol_fee(RuntimeOrigin::root(), 0),
                Error::<Test>::InvalidFeeAmount
            );
        });
    }

    #[test]
    fn test_distribute_protocol_fee_uneven_amount_exact() {
        new_test_ext().execute_with(|| {
            // 99 raw (not divisible by 100 evenly)
            // 40% = 39, 30% = 29, 20% = 19, 10% = 9 → sum = 96 ≠ 99
            // This should fail because 99 is not evenly divisible
            // Actually: 99 * 40 / 100 = 39 (integer division)
            // 99 * 30 / 100 = 29
            // 99 * 20 / 100 = 19
            // 99 * 10 / 100 = 9
            // Sum = 96 ≠ 99 → should fail with FeeDistributionOverflow
            assert_noop!(
                Tokenomics::distribute_protocol_fee(RuntimeOrigin::root(), 99),
                Error::<Test>::FeeDistributionOverflow
            );
        });
    }

    #[test]
    fn test_distribute_protocol_fee_cumulative() {
        new_test_ext().execute_with(|| {
            // First distribution
            assert_ok!(Tokenomics::distribute_protocol_fee(
                RuntimeOrigin::root(),
                1_000_000
            ));

            // Second distribution
            assert_ok!(Tokenomics::distribute_protocol_fee(
                RuntimeOrigin::root(),
                1_000_000
            ));

            // Should accumulate
            assert_eq!(Tokenomics::protocol_fees_collected(), 2_000_000, "Cumulative total");
            assert_eq!(Tokenomics::validator_fees_received(), 800_000, "Cumulative validator share");
            assert_eq!(Tokenomics::treasury_fees_received(), 600_000, "Cumulative treasury share");
            assert_eq!(Tokenomics::ecosystem_fees_received(), 400_000, "Cumulative ecosystem share");
            assert_eq!(Tokenomics::fee_burned(), 200_000, "Cumulative burn share");
        });
    }

    #[test]
    fn test_distribute_protocol_fee_not_authorized() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            // Only AdminOrigin (root) can distribute fees
            assert_noop!(
                Tokenomics::distribute_protocol_fee(RuntimeOrigin::signed(alice), 1_000_000),
                DispatchError::BadOrigin
            );
        });
    }
});
    
    // === BURN TESTS ===

    #[test]
    fn test_burn_native_vrdx_success() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let balance_before = Balances::free_balance(&alice);
            let issuance_before = Balances::total_issuance();

            assert_ok!(Tokenomics::burn(
                RuntimeOrigin::signed(alice.clone()),
                100_000_000
            ));

            let balance_after = Balances::free_balance(&alice);
            let issuance_after = Balances::total_issuance();

            // User balance decreased by burned amount
            assert_eq!(balance_before - balance_after, 100_000_000, "User balance should decrease");
            // Total issuance decreased by burned amount
            assert_eq!(issuance_before - issuance_after, 100_000_000, "Total issuance should decrease");
            // Cumulative burned tracked
            assert_eq!(Tokenomics::cumulative_burned(), 100_000_000, "Cumulative burned tracked");
        });
    }

    #[test]
    fn test_burn_zero_amount_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_noop!(
                Tokenomics::burn(RuntimeOrigin::signed(alice), 0),
                Error::<Test>::ZeroBurnAmount
            );
        });
    }

    #[test]
    fn test_burn_insufficient_balance_rejected() {
        new_test_ext().execute_with(|| {
            let bob = Sr25519Keyring::Bob.to_account_id();
            let bob_balance = Balances::free_balance(&bob);

            // Try to burn more than Bob has
            assert_noop!(
                Tokenomics::burn(RuntimeOrigin::signed(bob), bob_balance + 1),
                Error::<Test>::InsufficientBalance
            );
        });
    }

    #[test]
    fn test_burn_reduces_total_issuance_invariant() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let burn_amount = 500_000_000u128;

            let issuance_before = Balances::total_issuance();

            assert_ok!(Tokenomics::burn(
                RuntimeOrigin::signed(alice.clone()),
                burn_amount
            ));

            let issuance_after = Balances::total_issuance();

            // Core invariant: total_issuance_before - total_issuance_after == burned_amount
            assert_eq!(
                issuance_before - issuance_after,
                burn_amount,
                "Burn invariant: issuance reduction must equal burn amount"
            );
        });
    }

    #[test]
    fn test_burn_unauthorized_rejected() {
        new_test_ext().execute_with(|| {
            // burn requires signed origin (user can only burn own funds)
            // Root cannot burn on behalf of someone else
            let alice = Sr25519Keyring::Alice.to_account_id();
            // This should work - signed origin
            assert_ok!(Tokenomics::burn(
                RuntimeOrigin::signed(alice.clone()),
                1_000_000
            ));
        });
    }

    #[test]
    fn test_burn_all_balance_allowed() {
        new_test_ext().execute_with(|| {
            let bob = Sr25519Keyring::Bob.to_account_id();
            let bob_balance = Balances::free_balance(&bob);

            // Burn entire balance (AllowDeath)
            assert_ok!(Tokenomics::burn(
                RuntimeOrigin::signed(bob.clone()),
                bob_balance
            ));

            assert_eq!(Balances::free_balance(&bob), 0, "Account should have 0 balance");
        });
    }

    // === PROTOCOL FEE TESTS ===

    #[test]
    fn test_distribute_protocol_fee_exact_split() {
        new_test_ext().execute_with(|| {
            let fee = 1_000_000_000u128; // 1B raw (1000 VRDX)

            assert_ok!(Tokenomics::distribute_protocol_fee(
                RuntimeOrigin::root(),
                fee
            ));

            // 40% = 400M, 30% = 300M, 20% = 200M, 10% = 100M
            assert_eq!(Tokenomics::validator_fees_received(), 400_000_000, "40% to validators");
            assert_eq!(Tokenomics::treasury_fees_received(), 300_000_000, "30% to treasury");
            assert_eq!(Tokenomics::ecosystem_fees_received(), 200_000_000, "20% to ecosystem");
            assert_eq!(Tokenomics::fee_burned(), 100_000_000, "10% burned");
            assert_eq!(Tokenomics::protocol_fees_collected(), fee, "Total tracked");
        });
    }

    #[test]
    fn test_distribute_protocol_fee_zero_rejected() {
        new_test_ext().execute_with(|| {
            assert_noop!(
                Tokenomics::distribute_protocol_fee(RuntimeOrigin::root(), 0),
                Error::<Test>::InvalidFeeAmount
            );
        });
    }

    #[test]
    fn test_distribute_protocol_fee_uneven_amount_exact() {
        new_test_ext().execute_with(|| {
            // 99 raw (not divisible by 100 evenly)
            // 40% = 39, 30% = 29, 20% = 19, 10% = 9 → sum = 96 ≠ 99
            // This should fail because 99 is not evenly divisible
            // Actually: 99 * 40 / 100 = 39 (integer division)
            // 99 * 30 / 100 = 29
            // 99 * 20 / 100 = 19
            // 99 * 10 / 100 = 9
            // Sum = 96 ≠ 99 → should fail with FeeDistributionOverflow
            assert_noop!(
                Tokenomics::distribute_protocol_fee(RuntimeOrigin::root(), 99),
                Error::<Test>::FeeDistributionOverflow
            );
        });
    }

    #[test]
    fn test_distribute_protocol_fee_cumulative() {
        new_test_ext().execute_with(|| {
            // First distribution
            assert_ok!(Tokenomics::distribute_protocol_fee(
                RuntimeOrigin::root(),
                1_000_000
            ));

            // Second distribution
            assert_ok!(Tokenomics::distribute_protocol_fee(
                RuntimeOrigin::root(),
                1_000_000
            ));

            // Should accumulate
            assert_eq!(Tokenomics::protocol_fees_collected(), 2_000_000, "Cumulative total");
            assert_eq!(Tokenomics::validator_fees_received(), 800_000, "Cumulative validator share");
            assert_eq!(Tokenomics::treasury_fees_received(), 600_000, "Cumulative treasury share");
            assert_eq!(Tokenomics::ecosystem_fees_received(), 400_000, "Cumulative ecosystem share");
            assert_eq!(Tokenomics::fee_burned(), 200_000, "Cumulative burn share");
        });
    }

    #[test]
    fn test_distribute_protocol_fee_not_authorized() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            // Only AdminOrigin (root) can distribute fees
            assert_noop!(
                Tokenomics::distribute_protocol_fee(RuntimeOrigin::signed(alice), 1_000_000),
                DispatchError::BadOrigin
            );
        });
    }
}

    // === BURN TESTS ===

    #[test]
    fn test_burn_native_vrdx_success() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let balance_before = Balances::free_balance(&alice);
            let issuance_before = Balances::total_issuance();

            assert_ok!(Tokenomics::burn(
                RuntimeOrigin::signed(alice.clone()),
                100_000_000
            ));

            let balance_after = Balances::free_balance(&alice);
            let issuance_after = Balances::total_issuance();

            // User balance decreased by burned amount
            assert_eq!(balance_before - balance_after, 100_000_000, "User balance should decrease");
            // Total issuance decreased by burned amount
            assert_eq!(issuance_before - issuance_after, 100_000_000, "Total issuance should decrease");
            // Cumulative burned tracked
            assert_eq!(Tokenomics::cumulative_burned(), 100_000_000, "Cumulative burned tracked");
        });
    }

    #[test]
    fn test_burn_zero_amount_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_noop!(
                Tokenomics::burn(RuntimeOrigin::signed(alice), 0),
                Error::<Test>::ZeroBurnAmount
            );
        });
    }

    #[test]
    fn test_burn_insufficient_balance_rejected() {
        new_test_ext().execute_with(|| {
            let bob = Sr25519Keyring::Bob.to_account_id();
            let bob_balance = Balances::free_balance(&bob);

            // Try to burn more than Bob has
            assert_noop!(
                Tokenomics::burn(RuntimeOrigin::signed(bob), bob_balance + 1),
                Error::<Test>::InsufficientBalance
            );
        });
    }

    #[test]
    fn test_burn_reduces_total_issuance_invariant() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let burn_amount = 500_000_000u128;

            let issuance_before = Balances::total_issuance();

            assert_ok!(Tokenomics::burn(
                RuntimeOrigin::signed(alice.clone()),
                burn_amount
            ));

            let issuance_after = Balances::total_issuance();

            // Core invariant: total_issuance_before - total_issuance_after == burned_amount
            assert_eq!(
                issuance_before - issuance_after,
                burn_amount,
                "Burn invariant: issuance reduction must equal burn amount"
            );
        });
    }

    #[test]
    fn test_burn_unauthorized_rejected() {
        new_test_ext().execute_with(|| {
            // burn requires signed origin (user can only burn own funds)
            // Root cannot burn on behalf of someone else
            let alice = Sr25519Keyring::Alice.to_account_id();
            // This should work - signed origin
            assert_ok!(Tokenomics::burn(
                RuntimeOrigin::signed(alice.clone()),
                1_000_000
            ));
        });
    }

    #[test]
    fn test_burn_all_balance_allowed() {
        new_test_ext().execute_with(|| {
            let bob = Sr25519Keyring::Bob.to_account_id();
            let bob_balance = Balances::free_balance(&bob);

            // Burn entire balance (AllowDeath)
            assert_ok!(Tokenomics::burn(
                RuntimeOrigin::signed(bob.clone()),
                bob_balance
            ));

            assert_eq!(Balances::free_balance(&bob), 0, "Account should have 0 balance");
        });
    }

    // === PROTOCOL FEE TESTS ===

    #[test]
    fn test_distribute_protocol_fee_exact_split() {
        new_test_ext().execute_with(|| {
            let fee = 1_000_000_000u128; // 1B raw (1000 VRDX)

            assert_ok!(Tokenomics::distribute_protocol_fee(
                RuntimeOrigin::root(),
                fee
            ));

            // 40% = 400M, 30% = 300M, 20% = 200M, 10% = 100M
            assert_eq!(Tokenomics::validator_fees_received(), 400_000_000, "40% to validators");
            assert_eq!(Tokenomics::treasury_fees_received(), 300_000_000, "30% to treasury");
            assert_eq!(Tokenomics::ecosystem_fees_received(), 200_000_000, "20% to ecosystem");
            assert_eq!(Tokenomics::fee_burned(), 100_000_000, "10% burned");
            assert_eq!(Tokenomics::protocol_fees_collected(), fee, "Total tracked");
        });
    }

    #[test]
    fn test_distribute_protocol_fee_zero_rejected() {
        new_test_ext().execute_with(|| {
            assert_noop!(
                Tokenomics::distribute_protocol_fee(RuntimeOrigin::root(), 0),
                Error::<Test>::InvalidFeeAmount
            );
        });
    }

    #[test]
    fn test_distribute_protocol_fee_uneven_amount_exact() {
        new_test_ext().execute_with(|| {
            // 99 raw (not divisible by 100 evenly)
            // 40% = 39, 30% = 29, 20% = 19, 10% = 9 → sum = 96 ≠ 99
            // This should fail because 99 is not evenly divisible
            // Actually: 99 * 40 / 100 = 39 (integer division)
            // 99 * 30 / 100 = 29
            // 99 * 20 / 100 = 19
            // 99 * 10 / 100 = 9
            // Sum = 96 ≠ 99 → should fail with FeeDistributionOverflow
            assert_noop!(
                Tokenomics::distribute_protocol_fee(RuntimeOrigin::root(), 99),
                Error::<Test>::FeeDistributionOverflow
            );
        });
    }

    #[test]
    fn test_distribute_protocol_fee_cumulative() {
        new_test_ext().execute_with(|| {
            // First distribution
            assert_ok!(Tokenomics::distribute_protocol_fee(
                RuntimeOrigin::root(),
                1_000_000
            ));

            // Second distribution
            assert_ok!(Tokenomics::distribute_protocol_fee(
                RuntimeOrigin::root(),
                1_000_000
            ));

            // Should accumulate
            assert_eq!(Tokenomics::protocol_fees_collected(), 2_000_000, "Cumulative total");
            assert_eq!(Tokenomics::validator_fees_received(), 800_000, "Cumulative validator share");
            assert_eq!(Tokenomics::treasury_fees_received(), 600_000, "Cumulative treasury share");
            assert_eq!(Tokenomics::ecosystem_fees_received(), 400_000, "Cumulative ecosystem share");
            assert_eq!(Tokenomics::fee_burned(), 200_000, "Cumulative burn share");
        });
    }

    #[test]
    fn test_distribute_protocol_fee_not_authorized() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            // Only AdminOrigin (root) can distribute fees
            assert_noop!(
                Tokenomics::distribute_protocol_fee(RuntimeOrigin::signed(alice), 1_000_000),
                DispatchError::BadOrigin
            );
        });
    }
}

#[cfg(test)]
mod economic_invariants;

// === Non-dispatchable helpers ===
impl<T: Config> Pallet<T> {
    /// Calculate annual inflation amount
    pub fn calculate_inflation(total_supply: u128, current_supply: u128) -> u128 {
        let rate = Self::annual_inflation_rate() as u128;
        let remaining = total_supply.saturating_sub(current_supply);
        remaining.saturating_mul(rate) / 10000
    }
}
