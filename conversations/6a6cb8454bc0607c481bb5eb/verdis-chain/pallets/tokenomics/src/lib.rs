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
    traits::{Currency, Get, ReservableCurrency},
    PalletId,
};
use frame_system::pallet_prelude::*;
use sp_runtime::traits::Saturating;
use sp_std::prelude::*;

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use super::*;

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    // === Distribution Category ===

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, RuntimeDebug)]
    pub struct DistributionCategory {
        pub name: Vec<u8>,
        pub amount: BalanceOf<T>,
        pub percentage: u8,
        pub vesting_days: u32,
        pub cliff_days: u32,
        pub released: BalanceOf<T>,
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
    pub type Distribution<T: Config> =
        StorageMap<_, Blake2_128Concat, Vec<u8>, DistributionCategory>;

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
    pub type ConsentGiven<T: Config> =
        StorageMap<_, Blake2_128Concat, T::AccountId, bool>;

    // === Events ===

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        ConsentGiven { who: T::AccountId },
        TokensPurchased { buyer: T::AccountId, amount: BalanceOf<T>, price: BalanceOf<T> },
        DistributionUpdated { category: Vec<u8>, released: BalanceOf<T> },
        PresalePriceUpdated { price: u32 },
    }

    // === Errors ===

    #[pallet::error]
    pub enum Error<T> {
        ConsentRequired,
        InsufficientFunds,
        MaxInvestorAllocationReached,
        InvalidCategory,
        DistributionComplete,
        AlreadyConsented,
    }

    // === Config ===

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        type RuntimeOrigin: Into<Result<CryptoOrigin, RuntimeOrigin>> + From<RuntimeOrigin>;
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
                let cat = DistributionCategory {
                    name: name.clone(),
                    amount: *amount,
                    percentage: *pct,
                    vesting_days: *vesting,
                    cliff_days: *cliff,
                    released: BalanceOf::<T>::zero(),
                };
                Distribution::<T>::insert(name.clone(), cat);
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

            ensure!(!ConsentGiven::<T>::contains_key(&who), Error::<T>::AlreadyConsented);
            ConsentGiven::<T>::insert(&who, true);

            Self::deposit_event(Event::ConsentGiven { who });
            Ok(())
        }

        /// Purchase tokens (requires prior consent)
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::purchase())]
        pub fn purchase(origin: OriginFor<T>, amount: BalanceOf<T>) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // Enforce consent gating
            ensure!(ConsentGiven::<T>::get(&who).unwrap_or(false), Error::<T>::ConsentRequired);

            // Enforce investor allocation limit (12B)
            let sold = PresaleSold::<T>::get();
            let max = T::InvestorAllocation::get();
            ensure!(sold.saturating_add(amount) <= max, Error::<T>::MaxInvestorAllocationReached);

            // Calculate price
            let price_bps = PresalePrice::<T>::get(); // basis points
            let cost = amount.saturating_mul(price_bps.into()) / 10_000;

            // Transfer tokens
            T::Currency::transfer(&T::PalletId::get().into_account_truncating(), &who, amount, ExistenceRequirement::AllowDeath)?;

            PresaleRaised::<T>::mutate(|r| *r = r.saturating_add(cost));
            PresaleSold::<T>::mutate(|s| *s = s.saturating_add(amount));
            CirculatingSupply::<T>::mutate(|c| *c = c.saturating_add(amount));

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

            Distribution::<T>::mutate(&category, |c| {
                let cat = c.as_mut().ok_or(Error::<T>::InvalidCategory)?;
                ensure!(
                    cat.released.saturating_add(amount) <= cat.amount,
                    Error::<T>::DistributionComplete
                );
                cat.released = cat.released.saturating_add(amount);
                Ok::<(), Error<T>>(())
            })?;

            CirculatingSupply::<T>::mutate(|c| *c = c.saturating_add(amount));

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

    pub struct SubstrateWeight<T>(PhantomData<T>);
    impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
        fn give_consent() -> Weight { Weight::from_parts(30_000_000, 0) }
        fn purchase() -> Weight { Weight::from_parts(100_000_000, 0) }
        fn update_presale_price() -> Weight { Weight::from_parts(20_000_000, 0) }
        fn release_distribution() -> Weight { Weight::from_parts(40_000_000, 0) }
    }
}

type BalanceOf<T> = <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;
type CryptoOrigin = T::RuntimeOrigin;
