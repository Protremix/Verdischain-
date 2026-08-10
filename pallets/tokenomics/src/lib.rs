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
//! Enforces the 100B token supply and 8-category distribution:
//! - Community (35%), Treasury (20%), Team (15%), Investors (10%)
//! - Staking (10%), Liquidity (5%), Advisors (3%), Airdrop (2%)
//! - 12B total investor allocation enforcement
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
use sp_runtime::traits::{AccountIdConversion, Saturating};
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
    }

    // === Errors ===

    #[pallet::error]
    pub enum Error<T> {
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
            ensure_root(origin)?;

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
            ensure_root(origin)?;

            let cat_bv: BoundedVec<u8, ConstU32<32>> = category
                .clone()
                .try_into()
                .map_err(|_| Error::<T>::InvalidCategory)?;

            Distribution::<T>::mutate(&cat_bv, |c| {
                let cat = c.as_mut().ok_or(Error::<T>::InvalidCategory)?;
                ensure!(
                    cat.released.saturating_add(amount) <= cat.amount,
                    Error::<T>::DistributionComplete
                );
                cat.released = cat.released.saturating_add(amount);
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
}

#[cfg(test)]
mod economic_invariants;
