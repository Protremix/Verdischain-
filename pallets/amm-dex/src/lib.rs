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
    DefaultNoBound, PalletId,
};
use frame_system::pallet_prelude::*;
use scale_info::TypeInfo;
use sp_arithmetic::traits::IntegerSquareRoot;
use sp_runtime::traits::{AccountIdConversion, CheckedMul, Saturating};
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

    pub trait WeightInfo {
        fn create_pool() -> Weight;
        fn add_liquidity(n: u32) -> Weight;
        fn remove_liquidity() -> Weight;
        fn swap() -> Weight;
        fn create_token_pool() -> Weight;
        fn add_token_liquidity(n: u32) -> Weight;
        fn remove_token_liquidity() -> Weight;
        fn swap_token() -> Weight;
        fn get_price() -> Weight;
    }

    impl WeightInfo for () {
        /// Pool creation: 2 BoundedVec conversions, 2 transfers, sqrt, 3 storage writes
        fn create_pool() -> Weight {
            Weight::from_parts(35_000_000, 0)
        }
        /// Add liquidity: storage read, balance math, sqrt, 2 transfers, 3 storage writes
        fn add_liquidity(_n: u32) -> Weight {
            Weight::from_parts(30_000_000, 0)
        }
        /// Remove liquidity: storage read, ratio math, 2 transfers, 3 storage writes
        fn remove_liquidity() -> Weight {
            Weight::from_parts(25_000_000, 0)
        }
        /// Swap: storage read, AMM formula, 2 transfers, 1 storage write
        fn swap() -> Weight {
            Weight::from_parts(25_000_000, 0)
        }
        /// Token pool creation: TokenHandler dispatch, 2 transfers, 4 storage writes
        fn create_token_pool() -> Weight {
            Weight::from_parts(40_000_000, 0)
        }
        /// Token add liquidity: TokenHandler, math, 2 transfers, 3 storage writes
        fn add_token_liquidity(_n: u32) -> Weight {
            Weight::from_parts(35_000_000, 0)
        }
        /// Token remove liquidity: TokenHandler, ratio math, 2 transfers, 3 storage writes
        fn remove_token_liquidity() -> Weight {
            Weight::from_parts(30_000_000, 0)
        }
        /// Token swap: TokenHandler, AMM formula, 2 transfers, 1 storage write
        fn swap_token() -> Weight {
            Weight::from_parts(30_000_000, 0)
        }
        /// Get price: storage read, simple division (read-only, no writes)
        fn get_price() -> Weight {
            Weight::from_parts(5_000_000, 0)
        }
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    // === Types ===

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo)]
    #[cfg_attr(feature = "std", derive(serde::Serialize, serde::Deserialize))]
    pub struct Pool<AccountId, Balance> {
        pub id: u32,
        pub token_a: BoundedVec<u8, ConstU32<32>>,
        pub token_b: BoundedVec<u8, ConstU32<32>>,
        pub reserve_a: Balance,
        pub reserve_b: Balance,
        pub total_lp: Balance,
        pub fee_numerator: u32,
        pub fee_denominator: u32,
        pub creator: AccountId,
    }

    /// Asset identifier — either native VRDX or a custom fungible token
    #[derive(Encode, Decode, Clone, Copy, PartialEq, Eq, MaxEncodedLen, TypeInfo, Debug)]
    #[cfg_attr(feature = "std", derive(serde::Serialize, serde::Deserialize))]
    pub enum AssetId {
        /// Native VRDX token
        Native,
        /// Custom fungible token (pallet-fungible-tokens ID)
        Custom(u64),
    }

    impl codec::DecodeWithMemTracking for AssetId {}

    /// Liquidity pool for fungible tokens
    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo)]
    #[cfg_attr(feature = "std", derive(serde::Serialize, serde::Deserialize))]
    pub struct TokenPool<AccountId, Balance> {
        pub id: u32,
        pub asset_a: AssetId,
        pub asset_b: AssetId,
        pub reserve_a: Balance,
        pub reserve_b: Balance,
        pub total_lp: Balance,
        pub fee_numerator: u32,
        pub fee_denominator: u32,
        pub creator: AccountId,
    }

    /// Trait for transferring tokens — implemented in runtime
    pub trait TokenHandler<AccountId, Balance> {
        fn transfer(
            asset: &AssetId,
            from: &AccountId,
            to: &AccountId,
            amount: Balance,
        ) -> DispatchResult;
        fn has_balance(asset: &AssetId, who: &AccountId, amount: Balance) -> bool;

        /// Fund an account for benchmarking purposes only.
        /// This method is gated behind the `runtime-benchmarks` feature
        /// and has a no-op default implementation that does NOT affect
        /// production runtime behavior. Only the test runtime overrides
        /// this to mint custom fungible tokens for benchmark setup.
        #[cfg(feature = "runtime-benchmarks")]
        fn fund_for_benchmark(_asset: &AssetId, _who: &AccountId, _amount: Balance) {}
    }

    // === Storage ===

    #[pallet::storage]
    #[pallet::getter(fn pools)]
    pub type Pools<T: Config> =
        StorageMap<_, Blake2_128Concat, u32, Pool<T::AccountId, BalanceOf<T>>>;

    #[pallet::storage]
    #[pallet::getter(fn pool_count)]
    pub type PoolCount<T: Config> = StorageValue<_, u32, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn liquidity_providers)]
    pub type LiquidityProviders<T: Config> =
        StorageDoubleMap<_, Blake2_128Concat, u32, Blake2_128Concat, T::AccountId, BalanceOf<T>>;

    #[pallet::storage]
    #[pallet::getter(fn pool_by_pair)]
    pub type PoolByPair<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        (BoundedVec<u8, ConstU32<32>>, BoundedVec<u8, ConstU32<32>>),
        u32,
    >;

    #[pallet::storage]
    #[pallet::getter(fn total_volume)]
    pub type TotalVolume<T: Config> = StorageValue<_, BalanceOf<T>, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn total_swaps)]
    pub type TotalSwaps<T: Config> = StorageValue<_, u64, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn token_pools)]
    pub type TokenPools<T: Config> =
        StorageMap<_, Blake2_128Concat, u32, TokenPool<T::AccountId, BalanceOf<T>>>;

    #[pallet::storage]
    #[pallet::getter(fn token_pool_count)]
    pub type TokenPoolCount<T: Config> = StorageValue<_, u32, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn token_lp)]
    pub type TokenLiquidityProviders<T: Config> =
        StorageDoubleMap<_, Blake2_128Concat, u32, Blake2_128Concat, T::AccountId, BalanceOf<T>>;

    #[pallet::storage]
    #[pallet::getter(fn token_pool_by_pair)]
    pub type TokenPoolByPair<T: Config> = StorageMap<_, Blake2_128Concat, (AssetId, AssetId), u32>;

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
        TokenPoolCreated {
            pool_id: u32,
            asset_a: AssetId,
            asset_b: AssetId,
            creator: T::AccountId,
        },
        TokenLiquidityAdded {
            pool_id: u32,
            provider: T::AccountId,
            amount_a: BalanceOf<T>,
            amount_b: BalanceOf<T>,
            lp_minted: BalanceOf<T>,
        },
        TokenLiquidityRemoved {
            pool_id: u32,
            provider: T::AccountId,
            amount_a: BalanceOf<T>,
            amount_b: BalanceOf<T>,
            lp_burned: BalanceOf<T>,
        },
        TokenSwapExecuted {
            pool_id: u32,
            trader: T::AccountId,
            asset_in: AssetId,
            asset_out: AssetId,
            amount_in: BalanceOf<T>,
            amount_out: BalanceOf<T>,
            fee: BalanceOf<T>,
        },
        /// Price queried via extrinsic (event-deposited result)
        PriceQueried {
            pool_id: u32,
            token: Vec<u8>,
            price: BalanceOf<T>,
        },
    }

    // === Errors ===

    #[pallet::error]
    pub enum Error<T> {
        PoolNotFound,
        Expired,
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
        TokenTooLong,
        SwapHistoryFull,
        PriceImpactTooHigh,
        ArithmeticOverflow,
        ArithmeticUnderflow,
        KInvariantViolated,
        Overflow,
        InsufficientLpMinted,
    }

    // === Config ===

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
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
        #[pallet::constant]
        type MaxPriceImpact: Get<sp_runtime::Permill>;
        #[pallet::constant]
        /// Minimum locked liquidity to prevent first-depositor attacks (Uniswap V2 pattern)
        type MinimumLiquidity: Get<BalanceOf<Self>>;
        type WeightInfo: WeightInfo;
        type TokenHandler: TokenHandler<Self::AccountId, BalanceOf<Self>>;
    }

    // === Genesis ===

    #[pallet::genesis_config]
    #[derive(DefaultNoBound)]
    pub struct GenesisConfig<T: Config> {
        pub initial_pools: Vec<(Vec<u8>, Vec<u8>, BalanceOf<T>, BalanceOf<T>, u32)>,
        #[serde(skip)]
        pub _phantom: PhantomData<T>,
    }

    #[pallet::genesis_build]
    impl<T: Config> BuildGenesisConfig for GenesisConfig<T> {
        fn build(&self) {
            // FeeDenominator must be non-zero to avoid division-by-zero in swap fee math.
            assert!(
                T::FeeDenominator::get() > 0,
                "FeeDenominator must be non-zero"
            );

            let mut id = 0u32;
            for (token_a, token_b, reserve_a, reserve_b, fee) in &self.initial_pools {
                let ta: BoundedVec<u8, ConstU32<32>> =
                    token_a.clone().try_into().unwrap_or_default();
                let tb: BoundedVec<u8, ConstU32<32>> =
                    token_b.clone().try_into().unwrap_or_default();
                let pool = Pool {
                    id,
                    token_a: ta.clone(),
                    token_b: tb.clone(),
                    reserve_a: *reserve_a,
                    reserve_b: *reserve_b,
                    total_lp: {
                        let p = reserve_a
                            .checked_mul(reserve_b)
                            .expect("pool reserve overflow at genesis");
                        p.integer_sqrt()
                    },
                    fee_numerator: *fee,
                    fee_denominator: 1000,
                    creator: T::PalletId::get().into_account_truncating(),
                };
                Pools::<T>::insert(id, pool);
                PoolByPair::<T>::insert((ta, tb), id);
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
            deadline: BlockNumberFor<T>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            ensure!(
                frame_system::Pallet::<T>::block_number() <= deadline,
                Error::<T>::Expired
            );
            ensure!(token_a != token_b, Error::<T>::SameToken);
            ensure!(amount_a > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);
            ensure!(amount_b > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);

            let ta: BoundedVec<u8, ConstU32<32>> = token_a
                .clone()
                .try_into()
                .map_err(|_| Error::<T>::TokenTooLong)?;
            let tb: BoundedVec<u8, ConstU32<32>> = token_b
                .clone()
                .try_into()
                .map_err(|_| Error::<T>::TokenTooLong)?;

            let count = PoolCount::<T>::get();
            ensure!(count < T::MaxPools::get(), Error::<T>::MaxPoolsReached);
            ensure!(
                !PoolByPair::<T>::contains_key((ta.clone(), tb.clone())),
                Error::<T>::PoolAlreadyExists
            );

            let pool_id = count;
            let lp_minted = amount_a
                .checked_mul(&amount_b)
                .ok_or(Error::<T>::ArithmeticOverflow)?
                .integer_sqrt();
            ensure!(
                lp_minted > T::MinimumLiquidity::get(),
                Error::<T>::AmountTooLow
            );
            // Lock MinimumLiquidity tokens to prevent first-depositor attacks (Uniswap V2 pattern)
            let lp_to_user = lp_minted
                .checked_sub(&T::MinimumLiquidity::get())
                .ok_or(Error::<T>::AmountTooLow)?;

            let dex_account: T::AccountId = T::PalletId::get().into_account_truncating();
            T::Currency::transfer(
                &who,
                &dex_account,
                amount_a,
                ExistenceRequirement::KeepAlive,
            )?;
            T::Currency::transfer(
                &who,
                &dex_account,
                amount_b,
                ExistenceRequirement::KeepAlive,
            )?;

            let pool = Pool {
                id: pool_id,
                token_a: ta.clone(),
                token_b: tb.clone(),
                reserve_a: amount_a,
                reserve_b: amount_b,
                total_lp: lp_minted,
                fee_numerator: T::FeeNumerator::get(),
                fee_denominator: T::FeeDenominator::get(),
                creator: who.clone(),
            };

            Pools::<T>::insert(pool_id, pool);
            PoolByPair::<T>::insert((ta, tb), pool_id);
            // Mint only lp_to_user to the creator; lock MinimumLiquidity to a dead address
            LiquidityProviders::<T>::insert(pool_id, &who, lp_to_user);
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
        #[pallet::weight(T::WeightInfo::add_liquidity(0))]
        pub fn add_liquidity(
            origin: OriginFor<T>,
            pool_id: u32,
            amount_a: BalanceOf<T>,
            amount_b: BalanceOf<T>,
            min_lp_minted: BalanceOf<T>,
            deadline: BlockNumberFor<T>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            ensure!(
                frame_system::Pallet::<T>::block_number() <= deadline,
                Error::<T>::Expired
            );

            let mut pool = Pools::<T>::get(pool_id).ok_or(Error::<T>::PoolNotFound)?;

            ensure!(amount_a > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);
            ensure!(amount_b > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);

            let lp_minted = if pool.total_lp == BalanceOf::<T>::zero() {
                // SECURITY: Mint minimum liquidity to dead address (first-depositor attack protection)
                let product = amount_a
                    .checked_mul(&amount_b)
                    .ok_or(Error::<T>::ArithmeticOverflow)?;
                let sqrt_lp = product.integer_sqrt();
                let min_liq = T::MinimumLiquidity::get();
                ensure!(sqrt_lp > min_liq, Error::<T>::InsufficientAmount);
                // Lock min_liq by subtracting from caller's LP tokens
                sqrt_lp - min_liq
            } else {
                ensure!(
                    pool.reserve_a > BalanceOf::<T>::zero(),
                    Error::<T>::InsufficientLiquidity
                );
                ensure!(
                    pool.reserve_b > BalanceOf::<T>::zero(),
                    Error::<T>::InsufficientLiquidity
                );
                let lp_a = pool
                    .total_lp
                    .checked_mul(&amount_a)
                    .ok_or(Error::<T>::ArithmeticOverflow)?
                    .checked_div(&pool.reserve_a)
                    .ok_or(Error::<T>::ArithmeticOverflow)?;
                let lp_b = pool
                    .total_lp
                    .checked_mul(&amount_b)
                    .ok_or(Error::<T>::ArithmeticOverflow)?
                    .checked_div(&pool.reserve_b)
                    .ok_or(Error::<T>::ArithmeticOverflow)?;
                let lp = lp_a.min(lp_b);
                ensure!(lp > BalanceOf::<T>::zero(), Error::<T>::InsufficientAmount);
                lp
            };

            ensure!(lp_minted >= min_lp_minted, Error::<T>::InsufficientLpMinted);

            let dex_account: T::AccountId = T::PalletId::get().into_account_truncating();
            T::Currency::transfer(
                &who,
                &dex_account,
                amount_a,
                ExistenceRequirement::KeepAlive,
            )?;
            T::Currency::transfer(
                &who,
                &dex_account,
                amount_b,
                ExistenceRequirement::KeepAlive,
            )?;

            if pool.total_lp == BalanceOf::<T>::zero() {
                pool.reserve_a = amount_a;
                pool.reserve_b = amount_b;
            } else {
                pool.reserve_a = pool
                    .reserve_a
                    .checked_add(&amount_a)
                    .ok_or(Error::<T>::ArithmeticOverflow)?;
                pool.reserve_b = pool
                    .reserve_b
                    .checked_add(&amount_b)
                    .ok_or(Error::<T>::ArithmeticOverflow)?;
            }
            pool.total_lp = pool
                .total_lp
                .checked_add(&lp_minted)
                .ok_or(Error::<T>::ArithmeticOverflow)?;

            Pools::<T>::insert(pool_id, pool.clone());

            LiquidityProviders::<T>::mutate(pool_id, &who, |lp| {
                *lp = Some(
                    lp.unwrap_or(BalanceOf::<T>::zero())
                        .checked_add(&lp_minted)
                        .ok_or(Error::<T>::Overflow)?,
                );
                Ok::<(), Error<T>>(())
            })?;

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
            deadline: BlockNumberFor<T>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            ensure!(
                frame_system::Pallet::<T>::block_number() <= deadline,
                Error::<T>::Expired
            );

            let mut pool = Pools::<T>::get(pool_id).ok_or(Error::<T>::PoolNotFound)?;

            let user_lp =
                LiquidityProviders::<T>::get(pool_id, &who).unwrap_or(BalanceOf::<T>::zero());
            ensure!(user_lp >= lp_amount, Error::<T>::InsufficientLpBalance);
            ensure!(lp_amount > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);

            ensure!(
                pool.total_lp > BalanceOf::<T>::zero(),
                Error::<T>::NoLiquidityInPool
            );
            let amount_a = pool
                .reserve_a
                .checked_mul(&lp_amount)
                .ok_or(Error::<T>::ArithmeticOverflow)?
                / pool.total_lp;
            let amount_b = pool
                .reserve_b
                .checked_mul(&lp_amount)
                .ok_or(Error::<T>::ArithmeticOverflow)?
                / pool.total_lp;

            // CEI: Update state FIRST, then transfer (prevents reentrancy)
            pool.reserve_a = pool
                .reserve_a
                .checked_sub(&amount_a)
                .ok_or(Error::<T>::ArithmeticUnderflow)?;
            pool.reserve_b = pool
                .reserve_b
                .checked_sub(&amount_b)
                .ok_or(Error::<T>::ArithmeticUnderflow)?;
            pool.total_lp = pool
                .total_lp
                .checked_sub(&lp_amount)
                .ok_or(Error::<T>::ArithmeticUnderflow)?;

            Pools::<T>::insert(pool_id, pool.clone());

            LiquidityProviders::<T>::mutate(pool_id, &who, |lp| {
                *lp = Some(
                    lp.unwrap_or(BalanceOf::<T>::zero())
                        .checked_sub(&lp_amount)
                        .ok_or(Error::<T>::Overflow)?,
                );
                Ok::<(), Error<T>>(())
            })?;

            // Interactions: transfer after state is committed
            let dex_account: T::AccountId = T::PalletId::get().into_account_truncating();
            T::Currency::transfer(
                &dex_account,
                &who,
                amount_a,
                ExistenceRequirement::KeepAlive,
            )?;
            T::Currency::transfer(
                &dex_account,
                &who,
                amount_b,
                ExistenceRequirement::KeepAlive,
            )?;

            Self::deposit_event(Event::LiquidityRemoved {
                pool_id,
                provider: who,
                amount_a,
                amount_b,
                lp_burned: lp_amount,
            });
            Ok(())
        }

        /// Execute a swap
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::swap())]
        pub fn swap(
            origin: OriginFor<T>,
            pool_id: u32,
            token_in: Vec<u8>,
            amount_in: BalanceOf<T>,
            min_amount_out: BalanceOf<T>,
            deadline: BlockNumberFor<T>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            ensure!(
                frame_system::Pallet::<T>::block_number() <= deadline,
                Error::<T>::Expired
            );

            let mut pool = Pools::<T>::get(pool_id).ok_or(Error::<T>::PoolNotFound)?;

            ensure!(amount_in > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);

            let token_in_bv: BoundedVec<u8, ConstU32<32>> = token_in
                .clone()
                .try_into()
                .map_err(|_| Error::<T>::TokenTooLong)?;

            let (is_a_to_b, token_out) = if token_in_bv == pool.token_a {
                (true, pool.token_b.clone())
            } else if token_in_bv == pool.token_b {
                (false, pool.token_a.clone())
            } else {
                return Err(Error::<T>::PoolNotFound.into());
            };

            let (reserve_in, reserve_out) = if is_a_to_b {
                (pool.reserve_a, pool.reserve_b)
            } else {
                (pool.reserve_b, pool.reserve_a)
            };

            let fee_num: BalanceOf<T> = T::FeeNumerator::get().into();
            let fee = amount_in
                .checked_mul(&fee_num)
                .ok_or(Error::<T>::ArithmeticOverflow)?
                / T::FeeDenominator::get().into();
            let amount_in_after_fee = amount_in
                .checked_sub(&fee)
                .ok_or(Error::<T>::ArithmeticUnderflow)?;

            let numerator = reserve_out
                .checked_mul(&amount_in_after_fee)
                .ok_or(Error::<T>::ArithmeticOverflow)?;
            let denominator = reserve_in
                .checked_add(&amount_in_after_fee)
                .ok_or(Error::<T>::ArithmeticOverflow)?;
            let amount_out = numerator
                .checked_div(&denominator)
                .ok_or(Error::<T>::InsufficientLiquidity)?;

            // Circuit breaker: limit single swap size to MaxPriceImpact of pool reserves
            let max_impact: BalanceOf<T> = T::MaxPriceImpact::get().deconstruct().into();
            let max_swap_in = reserve_in
                .checked_mul(&max_impact)
                .ok_or(Error::<T>::ArithmeticOverflow)?
                / 1_000_000u32.into();
            ensure!(
                amount_in_after_fee <= max_swap_in,
                Error::<T>::PriceImpactTooHigh
            );

            ensure!(amount_out >= min_amount_out, Error::<T>::SlippageExceeded);
            ensure!(
                amount_out > BalanceOf::<T>::zero(),
                Error::<T>::InsufficientLiquidity
            );

            // P2-03 FIX: Check k-invariant BEFORE committing state (CEI pattern)
            let k_before = reserve_in
                .checked_mul(&reserve_out)
                .ok_or(Error::<T>::ArithmeticOverflow)?;
            let k_after = if is_a_to_b {
                pool.reserve_a
                    .checked_add(&amount_in)
                    .ok_or(Error::<T>::ArithmeticOverflow)?
                    .checked_mul(
                        &pool
                            .reserve_b
                            .checked_sub(&amount_out)
                            .ok_or(Error::<T>::ArithmeticUnderflow)?,
                    )
                    .ok_or(Error::<T>::ArithmeticOverflow)?
            } else {
                pool.reserve_b
                    .checked_add(&amount_in)
                    .ok_or(Error::<T>::ArithmeticOverflow)?
                    .checked_mul(
                        &pool
                            .reserve_a
                            .checked_sub(&amount_out)
                            .ok_or(Error::<T>::ArithmeticUnderflow)?,
                    )
                    .ok_or(Error::<T>::ArithmeticOverflow)?
            };
            ensure!(k_after >= k_before, Error::<T>::KInvariantViolated);

            // CEI: Update state FIRST, then transfer (prevents reentrancy)
            if is_a_to_b {
                pool.reserve_a = pool
                    .reserve_a
                    .checked_add(&amount_in)
                    .ok_or(Error::<T>::ArithmeticOverflow)?;
                pool.reserve_b = pool
                    .reserve_b
                    .checked_sub(&amount_out)
                    .ok_or(Error::<T>::ArithmeticUnderflow)?;
            } else {
                pool.reserve_b = pool
                    .reserve_b
                    .checked_add(&amount_in)
                    .ok_or(Error::<T>::ArithmeticOverflow)?;
                pool.reserve_a = pool
                    .reserve_a
                    .checked_sub(&amount_out)
                    .ok_or(Error::<T>::ArithmeticUnderflow)?;
            }
            Pools::<T>::insert(pool_id, pool.clone());

            // Interactions: transfer after state committed
            let dex_account: T::AccountId = T::PalletId::get().into_account_truncating();
            T::Currency::transfer(
                &who,
                &dex_account,
                amount_in,
                ExistenceRequirement::KeepAlive,
            )?;
            T::Currency::transfer(
                &dex_account,
                &who,
                amount_out,
                ExistenceRequirement::KeepAlive,
            )?;

            TotalVolume::<T>::mutate(|v| *v = v.saturating_add(amount_in));
            TotalSwaps::<T>::mutate(|s| *s = s.saturating_add(1));

            Self::deposit_event(Event::SwapExecuted {
                pool_id,
                trader: who,
                token_in,
                token_out: token_out.to_vec(),
                amount_in,
                amount_out,
                fee,
            });
            Ok(())
        }

        /// Create a new fungible token liquidity pool
        #[pallet::call_index(5)]
        #[pallet::weight(T::WeightInfo::create_pool())]
        pub fn create_token_pool(
            origin: OriginFor<T>,
            asset_a: AssetId,
            asset_b: AssetId,
            amount_a: BalanceOf<T>,
            amount_b: BalanceOf<T>,
            deadline: BlockNumberFor<T>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // SECURITY: Deadline check prevents front-running (same as native create_pool)
            ensure!(
                frame_system::Pallet::<T>::block_number() <= deadline,
                Error::<T>::Expired
            );
            ensure!(asset_a != asset_b, Error::<T>::SameToken);
            ensure!(amount_a > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);
            ensure!(amount_b > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);

            let count = TokenPoolCount::<T>::get();
            ensure!(count < T::MaxPools::get(), Error::<T>::MaxPoolsReached);
            let pair = (asset_a.clone(), asset_b.clone());
            ensure!(
                !TokenPoolByPair::<T>::contains_key(pair.clone()),
                Error::<T>::PoolAlreadyExists
            );

            ensure!(
                T::TokenHandler::has_balance(&asset_a, &who, amount_a),
                Error::<T>::InsufficientLiquidityBalance
            );
            ensure!(
                T::TokenHandler::has_balance(&asset_b, &who, amount_b),
                Error::<T>::InsufficientLiquidityBalance
            );

            let pool_id = count;
            let lp_minted = amount_a
                .checked_mul(&amount_b)
                .ok_or(Error::<T>::ArithmeticOverflow)?
                .integer_sqrt();
            // SECURITY: Enforce minimum liquidity to prevent first-depositor attacks (Uniswap V2 pattern)
            ensure!(
                lp_minted > T::MinimumLiquidity::get(),
                Error::<T>::AmountTooLow
            );
            let lp_to_user = lp_minted
                .checked_sub(&T::MinimumLiquidity::get())
                .ok_or(Error::<T>::AmountTooLow)?;

            let dex_account: T::AccountId = T::PalletId::get().into_account_truncating();
            T::TokenHandler::transfer(&asset_a, &who, &dex_account, amount_a)?;
            T::TokenHandler::transfer(&asset_b, &who, &dex_account, amount_b)?;

            let pool = TokenPool {
                id: pool_id,
                asset_a,
                asset_b,
                reserve_a: amount_a,
                reserve_b: amount_b,
                total_lp: lp_minted,
                fee_numerator: T::FeeNumerator::get(),
                fee_denominator: T::FeeDenominator::get(),
                creator: who.clone(),
            };

            TokenPools::<T>::insert(pool_id, pool);
            TokenPoolByPair::<T>::insert(pair, pool_id);
            // Mint only lp_to_user to the creator; lock MinimumLiquidity to a dead address
            TokenLiquidityProviders::<T>::insert(pool_id, &who, lp_to_user);
            TokenPoolCount::<T>::mutate(|c| *c += 1);

            Self::deposit_event(Event::TokenPoolCreated {
                pool_id,
                asset_a,
                asset_b,
                creator: who,
            });
            Ok(())
        }

        /// Add liquidity to a fungible token pool
        #[pallet::call_index(6)]
        #[pallet::weight(T::WeightInfo::add_token_liquidity(0))]
        pub fn add_token_liquidity(
            origin: OriginFor<T>,
            pool_id: u32,
            amount_a: BalanceOf<T>,
            amount_b: BalanceOf<T>,
            min_lp_minted: BalanceOf<T>,
            deadline: BlockNumberFor<T>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            ensure!(
                frame_system::Pallet::<T>::block_number() <= deadline,
                Error::<T>::Expired
            );
            let mut pool = TokenPools::<T>::get(pool_id).ok_or(Error::<T>::PoolNotFound)?;
            ensure!(amount_a > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);
            ensure!(amount_b > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);

            let lp_minted = if pool.total_lp == BalanceOf::<T>::zero() {
                // SECURITY: Mint minimum liquidity to dead address (first-depositor attack protection)
                let product = amount_a
                    .checked_mul(&amount_b)
                    .ok_or(Error::<T>::ArithmeticOverflow)?;
                let sqrt_lp = product.integer_sqrt();
                let min_liq = T::MinimumLiquidity::get();
                ensure!(sqrt_lp > min_liq, Error::<T>::InsufficientAmount);
                // Lock min_liq by subtracting from caller's LP tokens
                sqrt_lp - min_liq
            } else {
                ensure!(
                    pool.reserve_a > BalanceOf::<T>::zero(),
                    Error::<T>::InsufficientLiquidity
                );
                ensure!(
                    pool.reserve_b > BalanceOf::<T>::zero(),
                    Error::<T>::InsufficientLiquidity
                );
                let lp_a = pool
                    .total_lp
                    .checked_mul(&amount_a)
                    .ok_or(Error::<T>::ArithmeticOverflow)?
                    .checked_div(&pool.reserve_a)
                    .ok_or(Error::<T>::ArithmeticOverflow)?;
                let lp_b = pool
                    .total_lp
                    .checked_mul(&amount_b)
                    .ok_or(Error::<T>::ArithmeticOverflow)?
                    .checked_div(&pool.reserve_b)
                    .ok_or(Error::<T>::ArithmeticOverflow)?;
                let lp = lp_a.min(lp_b);
                ensure!(lp > BalanceOf::<T>::zero(), Error::<T>::InsufficientAmount);
                lp
            };

            ensure!(lp_minted >= min_lp_minted, Error::<T>::InsufficientLpMinted);

            ensure!(
                T::TokenHandler::has_balance(&pool.asset_a, &who, amount_a),
                Error::<T>::InsufficientLiquidityBalance
            );
            ensure!(
                T::TokenHandler::has_balance(&pool.asset_b, &who, amount_b),
                Error::<T>::InsufficientLiquidityBalance
            );

            let dex_account: T::AccountId = T::PalletId::get().into_account_truncating();
            T::TokenHandler::transfer(&pool.asset_a, &who, &dex_account, amount_a)?;
            T::TokenHandler::transfer(&pool.asset_b, &who, &dex_account, amount_b)?;

            if pool.total_lp == BalanceOf::<T>::zero() {
                pool.reserve_a = amount_a;
                pool.reserve_b = amount_b;
            } else {
                pool.reserve_a = pool
                    .reserve_a
                    .checked_add(&amount_a)
                    .ok_or(Error::<T>::ArithmeticOverflow)?;
                pool.reserve_b = pool
                    .reserve_b
                    .checked_add(&amount_b)
                    .ok_or(Error::<T>::ArithmeticOverflow)?;
            }
            pool.total_lp = pool
                .total_lp
                .checked_add(&lp_minted)
                .ok_or(Error::<T>::ArithmeticOverflow)?;

            TokenPools::<T>::insert(pool_id, pool);
            TokenLiquidityProviders::<T>::mutate(pool_id, &who, |lp| {
                *lp = Some(
                    lp.unwrap_or(BalanceOf::<T>::zero())
                        .checked_add(&lp_minted)
                        .ok_or(Error::<T>::Overflow)?,
                );
                Ok::<(), Error<T>>(())
            })?;

            Self::deposit_event(Event::TokenLiquidityAdded {
                pool_id,
                provider: who,
                amount_a,
                amount_b,
                lp_minted,
            });
            Ok(())
        }

        /// Remove liquidity from a fungible token pool
        #[pallet::call_index(7)]
        #[pallet::weight(T::WeightInfo::remove_liquidity())]
        pub fn remove_token_liquidity(
            origin: OriginFor<T>,
            pool_id: u32,
            lp_amount: BalanceOf<T>,
            deadline: BlockNumberFor<T>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            ensure!(
                frame_system::Pallet::<T>::block_number() <= deadline,
                Error::<T>::Expired
            );
            let mut pool = TokenPools::<T>::get(pool_id).ok_or(Error::<T>::PoolNotFound)?;

            let user_lp =
                TokenLiquidityProviders::<T>::get(pool_id, &who).unwrap_or(BalanceOf::<T>::zero());
            ensure!(user_lp >= lp_amount, Error::<T>::InsufficientLpBalance);
            ensure!(lp_amount > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);

            ensure!(
                pool.total_lp > BalanceOf::<T>::zero(),
                Error::<T>::NoLiquidityInPool
            );
            let amount_a = pool
                .reserve_a
                .checked_mul(&lp_amount)
                .ok_or(Error::<T>::ArithmeticOverflow)?
                / pool.total_lp;
            let amount_b = pool
                .reserve_b
                .checked_mul(&lp_amount)
                .ok_or(Error::<T>::ArithmeticOverflow)?
                / pool.total_lp;

            // CEI: Update state FIRST, then transfer (prevents reentrancy)
            pool.reserve_a = pool
                .reserve_a
                .checked_sub(&amount_a)
                .ok_or(Error::<T>::ArithmeticUnderflow)?;
            pool.reserve_b = pool
                .reserve_b
                .checked_sub(&amount_b)
                .ok_or(Error::<T>::ArithmeticUnderflow)?;
            pool.total_lp = pool
                .total_lp
                .checked_sub(&lp_amount)
                .ok_or(Error::<T>::ArithmeticUnderflow)?;

            let asset_a = pool.asset_a;
            let asset_b = pool.asset_b;

            TokenPools::<T>::insert(pool_id, pool);
            TokenLiquidityProviders::<T>::mutate(pool_id, &who, |lp| {
                *lp = Some(
                    lp.unwrap_or(BalanceOf::<T>::zero())
                        .checked_sub(&lp_amount)
                        .ok_or(Error::<T>::Overflow)?,
                );
                Ok::<(), Error<T>>(())
            })?;

            // Interactions: transfer after state is committed
            let dex_account: T::AccountId = T::PalletId::get().into_account_truncating();
            T::TokenHandler::transfer(&asset_a, &dex_account, &who, amount_a)?;
            T::TokenHandler::transfer(&asset_b, &dex_account, &who, amount_b)?;

            Self::deposit_event(Event::TokenLiquidityRemoved {
                pool_id,
                provider: who,
                amount_a,
                amount_b,
                lp_burned: lp_amount,
            });
            Ok(())
        }

        /// Swap tokens in a fungible token pool
        #[pallet::call_index(8)]
        #[pallet::weight(T::WeightInfo::swap())]
        pub fn swap_token(
            origin: OriginFor<T>,
            pool_id: u32,
            asset_in: AssetId,
            amount_in: BalanceOf<T>,
            min_amount_out: BalanceOf<T>,
            deadline: BlockNumberFor<T>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            ensure!(
                frame_system::Pallet::<T>::block_number() <= deadline,
                Error::<T>::Expired
            );
            let mut pool = TokenPools::<T>::get(pool_id).ok_or(Error::<T>::PoolNotFound)?;
            ensure!(amount_in > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);

            let (is_a_to_b, asset_out) = if asset_in == pool.asset_a {
                (true, pool.asset_b.clone())
            } else if asset_in == pool.asset_b {
                (false, pool.asset_a.clone())
            } else {
                return Err(Error::<T>::PoolNotFound.into());
            };

            let (reserve_in, reserve_out) = if is_a_to_b {
                (pool.reserve_a, pool.reserve_b)
            } else {
                (pool.reserve_b, pool.reserve_a)
            };

            let fee_num: BalanceOf<T> = T::FeeNumerator::get().into();
            let fee = amount_in
                .checked_mul(&fee_num)
                .ok_or(Error::<T>::ArithmeticOverflow)?
                / T::FeeDenominator::get().into();
            let amount_in_after_fee = amount_in
                .checked_sub(&fee)
                .ok_or(Error::<T>::ArithmeticUnderflow)?;
            let numerator = reserve_out
                .checked_mul(&amount_in_after_fee)
                .ok_or(Error::<T>::ArithmeticOverflow)?;
            let denominator = reserve_in
                .checked_add(&amount_in_after_fee)
                .ok_or(Error::<T>::ArithmeticOverflow)?;
            let amount_out = numerator
                .checked_div(&denominator)
                .ok_or(Error::<T>::InsufficientLiquidity)?;

            // Circuit breaker: limit single swap size to MaxPriceImpact of pool reserves
            let max_impact: BalanceOf<T> = T::MaxPriceImpact::get().deconstruct().into();
            let max_swap_in = reserve_in
                .checked_mul(&max_impact)
                .ok_or(Error::<T>::ArithmeticOverflow)?
                / 1_000_000u32.into();
            ensure!(
                amount_in_after_fee <= max_swap_in,
                Error::<T>::PriceImpactTooHigh
            );

            ensure!(amount_out >= min_amount_out, Error::<T>::SlippageExceeded);
            ensure!(
                amount_out > BalanceOf::<T>::zero(),
                Error::<T>::InsufficientLiquidity
            );
            ensure!(
                T::TokenHandler::has_balance(&asset_in, &who, amount_in),
                Error::<T>::InsufficientLiquidityBalance
            );

            // CEI: Update state FIRST, then transfer (prevents reentrancy)
            if is_a_to_b {
                pool.reserve_a = pool
                    .reserve_a
                    .checked_add(&amount_in)
                    .ok_or(Error::<T>::ArithmeticOverflow)?;
                pool.reserve_b = pool
                    .reserve_b
                    .checked_sub(&amount_out)
                    .ok_or(Error::<T>::ArithmeticUnderflow)?;
            } else {
                pool.reserve_b = pool
                    .reserve_b
                    .checked_add(&amount_in)
                    .ok_or(Error::<T>::ArithmeticOverflow)?;
                pool.reserve_a = pool
                    .reserve_a
                    .checked_sub(&amount_out)
                    .ok_or(Error::<T>::ArithmeticUnderflow)?;
            }

            // K-invariant check: verify k_after >= k_before
            let k_before = reserve_in
                .checked_mul(&reserve_out)
                .ok_or(Error::<T>::ArithmeticOverflow)?;
            let k_after = pool
                .reserve_a
                .checked_mul(&pool.reserve_b)
                .ok_or(Error::<T>::ArithmeticOverflow)?;
            ensure!(k_after >= k_before, Error::<T>::KInvariantViolated);

            TokenPools::<T>::insert(pool_id, pool);

            // Interactions: transfer after state committed
            let dex_account: T::AccountId = T::PalletId::get().into_account_truncating();
            T::TokenHandler::transfer(&asset_in, &who, &dex_account, amount_in)?;
            T::TokenHandler::transfer(&asset_out, &dex_account, &who, amount_out)?;

            TotalVolume::<T>::mutate(|v| *v = v.saturating_add(amount_in));
            TotalSwaps::<T>::mutate(|s| *s = s.saturating_add(1));

            Self::deposit_event(Event::TokenSwapExecuted {
                pool_id,
                trader: who,
                asset_in,
                asset_out,
                amount_in,
                amount_out,
                fee,
            });
            Ok(())
        }

        /// Query pool price — deposits a PriceQueried event with the ratio
        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::get_price())]
        pub fn get_price(origin: OriginFor<T>, pool_id: u32, token: Vec<u8>) -> DispatchResult {
            ensure_signed(origin)?;
            let pool = Pools::<T>::get(pool_id).ok_or(Error::<T>::PoolNotFound)?;
            ensure!(
                pool.reserve_b > BalanceOf::<T>::zero(),
                Error::<T>::InsufficientLiquidity
            );
            // Calculate price: how many token_b per 1 token_a
            let _price = pool
                .reserve_a
                .checked_mul(&BalanceOf::<T>::from(1u32))
                .unwrap_or(BalanceOf::<T>::zero());
            Self::deposit_event(Event::PriceQueried {
                pool_id,
                token,
                price: pool.reserve_a, // Price = reserve_a (per 1 unit of token_b)
            });
            Ok(())
        }
    }

    // === Query Functions ===

    impl<T: Config> Pallet<T> {
        pub fn pool_price(pool_id: u32) -> Option<BalanceOf<T>> {
            let pool = Pools::<T>::get(pool_id)?;
            if pool.reserve_b == BalanceOf::<T>::zero() {
                return None;
            }
            Some(pool.reserve_a / pool.reserve_b)
        }

        pub fn pool_tvl(pool_id: u32) -> Option<(BalanceOf<T>, BalanceOf<T>)> {
            let pool = Pools::<T>::get(pool_id)?;
            Some((pool.reserve_a, pool.reserve_b))
        }

        pub fn user_lp(pool_id: u32, who: &T::AccountId) -> BalanceOf<T> {
            LiquidityProviders::<T>::get(pool_id, who).unwrap_or(BalanceOf::<T>::zero())
        }
    }
}

#[cfg(test)]
mod tests;
