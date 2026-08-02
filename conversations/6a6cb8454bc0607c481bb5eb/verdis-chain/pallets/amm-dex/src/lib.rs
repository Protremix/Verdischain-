//! # Verdis AMM DEX Pallet
//!
//! Constant-product AMM (x*y=k) decentralized exchange with:
//! - Liquidity pool creation
//! - Add/remove liquidity
//! - Token swaps with 0.3% fee
//! - LP token tracking
//! - Price oracle from pool reserves

#![cfg_attr(not(feature = "std"), no_std)]

use codec::{Decode, Encode, MaxEncodedLen};
use frame_support::{
    dispatch::DispatchResult,
    ensure,
    pallet_prelude::*,
    traits::{Currency, ExistenceRequirement, Get, ReservableCurrency},
    PalletId,
};
use frame_system::pallet_prelude::*;
use sp_runtime::traits::{AccountIdConversion, Saturating};
use sp_std::{collections::btree_map::BTreeMap, prelude::*};

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use super::*;

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    // === Types ===

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, RuntimeDebug)]
    pub struct Pool<AccountId, Balance> {
        pub id: u32,
        pub token_a: Vec<u8>,
        pub token_b: Vec<u8>,
        pub reserve_a: Balance,
        pub reserve_b: Balance,
        pub total_lp: Balance,
        pub fee_numerator: u32,
        pub fee_denominator: u32,
        pub creator: AccountId,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, RuntimeDebug)]
    pub struct LiquidityProvider<AccountId, Balance> {
        pub provider: AccountId,
        pub pool_id: u32,
        pub lp_amount: Balance,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, RuntimeDebug)]
    pub struct SwapRecord<Balance> {
        pub pool_id: u32,
        pub token_in: Vec<u8>,
        pub token_out: Vec<u8>,
        pub amount_in: Balance,
        pub amount_out: Balance,
        pub fee: Balance,
    }

    // === Storage ===

    #[pallet::storage]
    #[pallet::getter(fn pools)]
    pub type Pools<T: Config> = StorageMap<_, Blake2_128Concat, u32, Pool<T::AccountId, BalanceOf<T>>>;

    #[pallet::storage]
    #[pallet::getter(fn pool_count)]
    pub type PoolCount<T: Config> = StorageValue<_, u32, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn liquidity_providers)]
    pub type LiquidityProviders<T: Config> =
        StorageDoubleMap<_, Blake2_128Concat, u32, Blake2_128Concat, T::AccountId, BalanceOf<T>>;

    #[pallet::storage]
    #[pallet::getter(fn pool_by_pair)]
    pub type PoolByPair<T: Config> =
        StorageMap<_, Blake2_128Concat, (Vec<u8>, Vec<u8>), u32>;

    #[pallet::storage]
    #[pallet::getter(fn swap_history)]
    pub type SwapHistory<T: Config> = StorageValue<_, Vec<SwapRecord<BalanceOf<T>>>, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn total_volume)]
    pub type TotalVolume<T: Config> = StorageValue<_, BalanceOf<T>, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn total_swaps)]
    pub type TotalSwaps<T: Config> = StorageValue<_, u64, ValueQuery>;

    // === Events ===

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        PoolCreated {
            pool_id: u32,
            token_a: Vec<u8>,
            token_b: Vec<u8>,
            creator: T::AccountId,
        },
        LiquidityAdded {
            pool_id: u32,
            provider: T::AccountId,
            amount_a: BalanceOf<T>,
            amount_b: BalanceOf<T>,
            lp_minted: BalanceOf<T>,
        },
        LiquidityRemoved {
            pool_id: u32,
            provider: T::AccountId,
            amount_a: BalanceOf<T>,
            amount_b: BalanceOf<T>,
            lp_burned: BalanceOf<T>,
        },
        SwapExecuted {
            pool_id: u32,
            trader: T::AccountId,
            token_in: Vec<u8>,
            token_out: Vec<u8>,
            amount_in: BalanceOf<T>,
            amount_out: BalanceOf<T>,
            fee: BalanceOf<T>,
        },
    }

    // === Errors ===

    #[pallet::error]
    pub enum Error<T> {
        PoolNotFound,
        PoolAlreadyExists,
        MaxPoolsReached,
        InsufficientLiquidity,
        InsufficientLiquidityBalance,
        InsufficientAmount,
        InvalidPoolId,
        NoLiquidityInPool,
        InsufficientLpBalance,
        ZeroAmount,
        SameToken,
        SlippageExceeded,
        AmountTooLow,
    }

    // === Config ===

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        type RuntimeOrigin: Into<Result<CryptoOrigin, RuntimeOrigin>> + From<RuntimeOrigin>;
        type Currency: ReservableCurrency<Self::AccountId>;
        #[pallet::constant]
        type PalletId: Get<PalletId>;
        #[pallet::constant]
        type FeeNumerator: Get<u32>;
        #[pallet::constant]
        type FeeDenominator: Get<u32>;
        #[pallet::constant]
        type MinLiquidity: Get<BalanceOf<Self>>;
        #[pallet::constant]
        type MaxPools: Get<u32>;
        type WeightInfo: WeightInfo;
    }

    // === Genesis ===

    #[pallet::genesis_config]
    #[derive(DefaultNoBound)]
    pub struct GenesisConfig<T: Config> {
        pub initial_pools: Vec<(Vec<u8>, Vec<u8>, BalanceOf<T>, BalanceOf<T>, u32)>,
    }

    #[pallet::genesis_build]
    impl<T: Config> BuildGenesisConfig for GenesisConfig<T> {
        fn build(&self) {
            let mut id = 0u32;
            for (token_a, token_b, reserve_a, reserve_b, fee) in &self.initial_pools {
                let pool = Pool {
                    id,
                    token_a: token_a.clone(),
                    token_b: token_b.clone(),
                    reserve_a: *reserve_a,
                    reserve_b: *reserve_b,
                    total_lp: (*reserve_a * *reserve_b).integer_sqrt(),
                    fee_numerator: *fee,
                    fee_denominator: 1000,
                    creator: T::PalletId::get().into_account_truncating(),
                };
                Pools::<T>::insert(id, pool);
                PoolByPair::<T>::insert((token_a.clone(), token_b.clone()), id);
                id += 1;
            }
            PoolCount::<T>::put(id);
        }
    }

    // === Extrinsics ===

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Create a new liquidity pool
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::create_pool())]
        pub fn create_pool(
            origin: OriginFor<T>,
            token_a: Vec<u8>,
            token_b: Vec<u8>,
            amount_a: BalanceOf<T>,
            amount_b: BalanceOf<T>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            ensure!(token_a != token_b, Error::<T>::SameToken);
            ensure!(amount_a > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);
            ensure!(amount_b > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);

            let count = PoolCount::<T>::get();
            ensure!(count < T::MaxPools::get(), Error::<T>::MaxPoolsReached);
            ensure!(
                !PoolByPair::<T>::contains_key((token_a.clone(), token_b.clone())),
                Error::<T>::PoolAlreadyExists
            );

            let pool_id = count;
            let lp_minted = (amount_a * amount_b).integer_sqrt();
            ensure!(lp_minted >= T::MinLiquidity::get(), Error::<T>::AmountTooLow);

            // Reserve initial liquidity
            T::Currency::reserve(&who, amount_a)?;
            T::Currency::reserve(&who, amount_b)?;

            let pool = Pool {
                id: pool_id,
                token_a: token_a.clone(),
                token_b: token_b.clone(),
                reserve_a: amount_a,
                reserve_b: amount_b,
                total_lp: lp_minted,
                fee_numerator: T::FeeNumerator::get(),
                fee_denominator: T::FeeDenominator::get(),
                creator: who.clone(),
            };

            Pools::<T>::insert(pool_id, pool);
            PoolByPair::<T>::insert((token_a.clone(), token_b.clone()), pool_id);
            LiquidityProviders::<T>::insert(pool_id, &who, lp_minted);
            PoolCount::<T>::mutate(|c| *c += 1);

            Self::deposit_event(Event::PoolCreated {
                pool_id,
                token_a,
                token_b,
                creator: who,
            });
            Ok(())
        }

        /// Add liquidity to an existing pool
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::add_liquidity())]
        pub fn add_liquidity(
            origin: OriginFor<T>,
            pool_id: u32,
            amount_a: BalanceOf<T>,
            amount_b: BalanceOf<T>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let mut pool = Pools::<T>::get(pool_id).ok_or(Error::<T>::PoolNotFound)?;

            ensure!(amount_a > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);
            ensure!(amount_b > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);

            // Calculate LP tokens proportionally
            let lp_a = pool.total_lp.saturating_mul(amount_a) / pool.reserve_a;
            let lp_b = pool.total_lp.saturating_mul(amount_b) / pool.reserve_b;
            let lp_minted = lp_a.min(lp_b);

            ensure!(lp_minted > BalanceOf::<T>::zero(), Error::<T>::InsufficientAmount);

            T::Currency::reserve(&who, amount_a)?;
            T::Currency::reserve(&who, amount_b)?;

            pool.reserve_a = pool.reserve_a.saturating_add(amount_a);
            pool.reserve_b = pool.reserve_b.saturating_add(amount_b);
            pool.total_lp = pool.total_lp.saturating_add(lp_minted);

            Pools::<T>::insert(pool_id, pool.clone());

            LiquidityProviders::<T>::mutate(pool_id, &who, |lp| {
                *lp = lp.unwrap_or(BalanceOf::<T>::zero()).saturating_add(lp_minted);
            });

            Self::deposit_event(Event::LiquidityAdded {
                pool_id,
                provider: who,
                amount_a,
                amount_b,
                lp_minted,
            });
            Ok(())
        }

        /// Remove liquidity from a pool
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::remove_liquidity())]
        pub fn remove_liquidity(
            origin: OriginFor<T>,
            pool_id: u32,
            lp_amount: BalanceOf<T>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let mut pool = Pools::<T>::get(pool_id).ok_or(Error::<T>::PoolNotFound)?;
            let user_lp = LiquidityProviders::<T>::get(pool_id, &who).unwrap_or(BalanceOf::<T>::zero());

            ensure!(lp_amount > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);
            ensure!(user_lp >= lp_amount, Error::<T>::InsufficientLpBalance);
            ensure!(pool.total_lp > BalanceOf::<T>::zero(), Error::<T>::NoLiquidityInPool);

            // Calculate proportional amounts
            let amount_a = pool.reserve_a.saturating_mul(lp_amount) / pool.total_lp;
            let amount_b = pool.reserve_b.saturating_mul(lp_amount) / pool.total_lp;

            T::Currency::unreserve(&who, amount_a);
            T::Currency::unreserve(&who, amount_b);

            pool.reserve_a = pool.reserve_a.saturating_sub(amount_a);
            pool.reserve_b = pool.reserve_b.saturating_sub(amount_b);
            pool.total_lp = pool.total_lp.saturating_sub(lp_amount);

            Pools::<T>::insert(pool_id, pool.clone());

            LiquidityProviders::<T>::mutate(pool_id, &who, |lp| {
                *lp = lp.unwrap_or(BalanceOf::<T>::zero()).saturating_sub(lp_amount);
            });

            Self::deposit_event(Event::LiquidityRemoved {
                pool_id,
                provider: who,
                amount_a,
                amount_b,
                lp_burned: lp_amount,
            });
            Ok(())
        }

        /// Execute a token swap
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::swap())]
        pub fn swap(
            origin: OriginFor<T>,
            pool_id: u32,
            token_in: Vec<u8>,
            amount_in: BalanceOf<T>,
            min_amount_out: BalanceOf<T>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let mut pool = Pools::<T>::get(pool_id).ok_or(Error::<T>::PoolNotFound)?;

            ensure!(amount_in > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);

            // Determine swap direction
            let (is_a_to_b, reserve_in, reserve_out) = if pool.token_a == token_in {
                (true, pool.reserve_a, pool.reserve_b)
            } else if pool.token_b == token_in {
                (false, pool.reserve_b, pool.reserve_a)
            } else {
                return Err(Error::<T>::PoolNotFound.into());
            };

            // Calculate output amount with fee: (x*y=k)
            // amount_out = reserve_out * amount_in * fee / (reserve_in * fee_den + amount_in * fee)
            let amount_in_with_fee = amount_in.saturating_mul(
                T::FeeDenominator::get().saturating_sub(T::FeeNumerator::get()).into()
            );
            let numerator = amount_in_with_fee.saturating_mul(reserve_out);
            let denominator = reserve_in
                .saturating_mul(T::FeeDenominator::get().into())
                .saturating_add(amount_in_with_fee);

            let amount_out = numerator / denominator;
            let fee = amount_in.saturating_mul(T::FeeNumerator::get().into())
                / T::FeeDenominator::get().into();

            ensure!(amount_out >= min_amount_out, Error::<T>::SlippageExceeded);
            ensure!(amount_out < reserve_out, Error::<T>::InsufficientLiquidity);

            T::Currency::reserve(&who, amount_in)?;
            T::Currency::unreserve(&who, amount_out);

            if is_a_to_b {
                pool.reserve_a = pool.reserve_a.saturating_add(amount_in);
                pool.reserve_b = pool.reserve_b.saturating_sub(amount_out);
            } else {
                pool.reserve_b = pool.reserve_b.saturating_add(amount_in);
                pool.reserve_a = pool.reserve_a.saturating_sub(amount_out);
            }

            Pools::<T>::insert(pool_id, pool.clone());

            // Record swap
            let token_out = if is_a_to_b { pool.token_b.clone() } else { pool.token_a.clone() };
            SwapHistory::<T>::mutate(|h| {
                h.push(SwapRecord {
                    pool_id,
                    token_in: token_in.clone(),
                    token_out: token_out.clone(),
                    amount_in,
                    amount_out,
                    fee,
                });
                if h.len() > 1000 {
                    h.remove(0);
                }
            });
            TotalVolume::<T>::mutate(|v| *v = v.saturating_add(amount_in));
            TotalSwaps::<T>::mutate(|s| *s += 1);

            Self::deposit_event(Event::SwapExecuted {
                pool_id,
                trader: who,
                token_in,
                token_out,
                amount_in,
                amount_out,
                fee,
            });
            Ok(())
        }
    }

    // === Internal Functions ===
    impl<T: Config> Pallet<T> {
        /// Get the price of token A in terms of token B for a pool
        pub fn get_price(pool_id: u32) -> Option<(BalanceOf<T>, BalanceOf<T>)> {
            let pool = Pools::<T>::get(pool_id)?;
            if pool.reserve_a > BalanceOf::<T>::zero() {
                Some((pool.reserve_b / pool.reserve_a, pool.reserve_a))
            } else {
                None
            }
        }

        /// Get all pools
        pub fn get_all_pools() -> Vec<Pool<T::AccountId, BalanceOf<T>>> {
            Pools::<T>::iter().map(|(_, p)| p).collect()
        }

        /// Get pool by token pair
        pub fn get_pool_by_pair(token_a: Vec<u8>, token_b: Vec<u8>) -> Option<u32> {
            PoolByPair::<T>::get((token_a, token_b))
        }
    }

    // === WeightInfo ===
    pub trait WeightInfo {
        fn create_pool() -> Weight;
        fn add_liquidity() -> Weight;
        fn remove_liquidity() -> Weight;
        fn swap() -> Weight;
    }

    pub struct SubstrateWeight<T>(PhantomData<T>);
    impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
        fn create_pool() -> Weight { Weight::from_parts(120_000_000, 0) }
        fn add_liquidity() -> Weight { Weight::from_parts(80_000_000, 0) }
        fn remove_liquidity() -> Weight { Weight::from_parts(70_000_000, 0) }
        fn swap() -> Weight { Weight::from_parts(100_000_000, 0) }
    }
}

type BalanceOf<T> = <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;
type CryptoOrigin = T::RuntimeOrigin;
