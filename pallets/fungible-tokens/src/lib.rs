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
    clippy::unnecessary_cast,
    clippy::needless_borrows_for_generic_args,
    clippy::manual_checked_ops
)]
//! # Verdis Fungible Tokens Pallet
//!
//! Native user-created fungible tokens for the Verdis blockchain.
//! Supports token creation, minting, burning, transfers, approvals,
//! allowances, metadata, supply tracking, and event emission.

#![cfg_attr(not(feature = "std"), no_std)]
use codec::{Decode, Encode, MaxEncodedLen};
use frame_support::{
    dispatch::DispatchResult,
    ensure,
    traits::{Get, ReservableCurrency},
    Blake2_128Concat, BoundedVec, PalletId,
};
use frame_system::ensure_signed;
use scale_info::TypeInfo;
use sp_std::prelude::*;

pub use pallet::*;
pub mod weights;
pub use weights::SubstrateWeight;

pub const MAX_TOKEN_NAME: u32 = 32;
pub const MAX_TOKEN_SYMBOL: u32 = 12;
pub const MAX_METADATA: u32 = 128;

type BalanceOf<T> = <<T as Config>::Currency as frame_support::traits::Currency<
    <T as frame_system::Config>::AccountId,
>>::Balance;

#[derive(Encode, Decode, Clone, PartialEq, Eq, TypeInfo, MaxEncodedLen, Debug)]
pub struct TokenInfo<AccountId, Balance> {
    pub owner: AccountId,
    pub name: BoundedVec<u8, frame_support::traits::ConstU32<MAX_TOKEN_NAME>>,
    pub symbol: BoundedVec<u8, frame_support::traits::ConstU32<MAX_TOKEN_SYMBOL>>,
    pub decimals: u8,
    pub total_supply: Balance,
    pub max_supply: Balance,
    pub is_frozen: bool,
    pub created_block: u32,
}

#[derive(Encode, Decode, Clone, PartialEq, Eq, TypeInfo, MaxEncodedLen, Debug)]
pub struct TokenMetadata {
    pub description: BoundedVec<u8, frame_support::traits::ConstU32<MAX_METADATA>>,
    pub logo_uri: BoundedVec<u8, frame_support::traits::ConstU32<MAX_METADATA>>,
}

use frame_support::weights::Weight;

/// Weight functions for Fungible Tokens pallet.
pub trait WeightInfo {
    fn create() -> Weight;
    fn mint() -> Weight;
    fn burn() -> Weight;
    fn transfer() -> Weight;
    fn approve() -> Weight;
    fn transfer_from() -> Weight;
    fn set_metadata(n: u32) -> Weight;
    fn freeze() -> Weight;
    fn thaw() -> Weight;
    fn destroy() -> Weight;
    fn batch_transfer(b: u32) -> Weight;
    fn transfer_ownership() -> Weight;
}

impl WeightInfo for () {
    fn create() -> Weight {
        Weight::from_parts(10_000, 0)
    }
    fn mint() -> Weight {
        Weight::from_parts(5_000, 0)
    }
    fn burn() -> Weight {
        Weight::from_parts(5_000, 0)
    }
    fn transfer() -> Weight {
        Weight::from_parts(5_000, 0)
    }
    fn approve() -> Weight {
        Weight::from_parts(3_000, 0)
    }
    fn transfer_from() -> Weight {
        Weight::from_parts(5_000, 0)
    }
    fn set_metadata(_n: u32) -> Weight {
        Weight::from_parts(3_000, 0)
    }
    fn freeze() -> Weight {
        Weight::from_parts(2_000, 0)
    }
    fn thaw() -> Weight {
        Weight::from_parts(2_000, 0)
    }
    fn destroy() -> Weight {
        Weight::from_parts(5_000, 0)
    }
    fn batch_transfer(b: u32) -> Weight {
        Weight::from_parts(10_000 * (b as u64).max(1), 0)
    }
    fn transfer_ownership() -> Weight {
        Weight::from_parts(3_000, 0)
    }
}

#[frame_support::pallet]
pub mod pallet {
    use super::*;
    use frame_support::pallet_prelude::*;
    use frame_system::pallet_prelude::*;

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        type Currency: ReservableCurrency<Self::AccountId>;
        type PalletId: Get<PalletId>;
        #[pallet::constant]
        type MaxTokensPerAccount: Get<u32>;
        #[pallet::constant]
        type CreateTokenDeposit: Get<BalanceOf<Self>>;
        #[pallet::constant]
        type MaxBalance: Get<u128>;
        type WeightInfo: WeightInfo;
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::storage]
    pub type NextTokenId<T> = StorageValue<_, u64, ValueQuery>;

    #[pallet::storage]
    pub type Tokens<T: Config> =
        StorageMap<_, Blake2_128Concat, u64, TokenInfo<T::AccountId, u128>>;

    #[pallet::storage]
    pub type TokenMetadataMap<T: Config> = StorageMap<_, Blake2_128Concat, u64, TokenMetadata>;

    #[pallet::storage]
    pub type TokenBalances<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        u64,
        Blake2_128Concat,
        T::AccountId,
        u128,
        ValueQuery,
    >;

    #[pallet::storage]
    pub type Allowances<T: Config> = StorageDoubleMap<
        _,
        Blake2_128Concat,
        u64,
        Blake2_128Concat,
        (T::AccountId, T::AccountId),
        u128,
        ValueQuery,
    >;

    #[pallet::storage]
    pub type TokensByOwner<T: Config> =
        StorageMap<_, Blake2_128Concat, T::AccountId, BoundedVec<u64, T::MaxTokensPerAccount>>;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        OwnershipTransferred {
            token_id: u64,
            old_owner: T::AccountId,
            new_owner: T::AccountId,
        },
        TokenCreated {
            token_id: u64,
            owner: T::AccountId,
            name: Vec<u8>,
            symbol: Vec<u8>,
            decimals: u8,
        },
        Minted {
            token_id: u64,
            to: T::AccountId,
            amount: u128,
        },
        Burned {
            token_id: u64,
            from: T::AccountId,
            amount: u128,
        },
        Transferred {
            token_id: u64,
            from: T::AccountId,
            to: T::AccountId,
            amount: u128,
        },
        Approved {
            token_id: u64,
            owner: T::AccountId,
            spender: T::AccountId,
            amount: u128,
        },
        MetadataSet {
            token_id: u64,
            description: Vec<u8>,
            logo_uri: Vec<u8>,
        },
        TokenFrozen {
            token_id: u64,
        },
        TokenThawed {
            token_id: u64,
        },
        TokenDestroyed {
            token_id: u64,
            owner: T::AccountId,
        },
        MaxSupplySet {
            token_id: u64,
            max_supply: u128,
        },
    }

    #[pallet::error]
    pub enum Error<T> {
        TokenNotFound,
        NotTokenOwner,
        TokenFrozen,
        TokenNotFrozen,
        InsufficientBalance,
        InsufficientAllowance,
        Overflow,
        Underflow,
        NameTooLong,
        SymbolTooLong,
        MetadataTooLong,
        EmptyName,
        EmptySymbol,
        TooManyTokensPerAccount,
        MaxBalanceExceeded,
    MaxSupplyCannotIncrease,
        NotApproved,
        TokenStillHasSupply,
        ZeroAmount,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Create a new fungible token
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::create())]
        pub fn create(
            origin: OriginFor<T>,
            name: Vec<u8>,
            symbol: Vec<u8>,
            decimals: u8,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            ensure!(!name.is_empty(), Error::<T>::EmptyName);
            ensure!(!symbol.is_empty(), Error::<T>::EmptySymbol);
            ensure!(name.len() as u32 <= MAX_TOKEN_NAME, Error::<T>::NameTooLong);
            ensure!(
                symbol.len() as u32 <= MAX_TOKEN_SYMBOL,
                Error::<T>::SymbolTooLong
            );

            let deposit = T::CreateTokenDeposit::get();
            T::Currency::reserve(&who, deposit)?;

            let mut owner_tokens = TokensByOwner::<T>::get(&who).unwrap_or_default();
            ensure!(
                (owner_tokens.len() as u32) < T::MaxTokensPerAccount::get(),
                Error::<T>::TooManyTokensPerAccount
            );

            let token_id = NextTokenId::<T>::get();
            NextTokenId::<T>::set(token_id.saturating_add(1));

            let name_bounded =
                BoundedVec::try_from(name.clone()).map_err(|_| Error::<T>::NameTooLong)?;
            let symbol_bounded =
                BoundedVec::try_from(symbol.clone()).map_err(|_| Error::<T>::SymbolTooLong)?;

            let token_info = TokenInfo {
                owner: who.clone(),
                name: name_bounded,
                symbol: symbol_bounded,
                decimals,
                total_supply: 0u128,
                max_supply: T::MaxBalance::get(),
                is_frozen: false,
                created_block: <frame_system::Pallet<T>>::block_number()
                    .try_into()
                    .unwrap_or(0),
            };

            Tokens::<T>::insert(token_id, token_info);
            owner_tokens
                .try_push(token_id)
                .map_err(|_| Error::<T>::TooManyTokensPerAccount)?;
            TokensByOwner::<T>::insert(&who, owner_tokens);

            Self::deposit_event(Event::TokenCreated {
                token_id,
                owner: who,
                name,
                symbol,
                decimals,
            });
            Ok(())
        }

        /// Mint tokens to an account (token owner only)
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::mint())]
        pub fn mint(
            origin: OriginFor<T>,
            token_id: u64,
            to: T::AccountId,
            amount: u128,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            ensure!(amount > 0, Error::<T>::ZeroAmount);

            let mut token = Tokens::<T>::get(token_id).ok_or(Error::<T>::TokenNotFound)?;
            ensure!(token.owner == who, Error::<T>::NotTokenOwner);
            ensure!(!token.is_frozen, Error::<T>::TokenFrozen);

            let new_supply = token
                .total_supply
                .checked_add(amount)
                .ok_or(Error::<T>::Overflow)?;
            ensure!(
                new_supply <= token.max_supply,
                Error::<T>::MaxBalanceExceeded
            );

            let balance = TokenBalances::<T>::get(token_id, &to);
            let new_balance = balance.checked_add(amount).ok_or(Error::<T>::Overflow)?;
            TokenBalances::<T>::insert(token_id, &to, new_balance);

            token.total_supply = new_supply;
            Tokens::<T>::insert(token_id, token);

            Self::deposit_event(Event::Minted {
                token_id,
                to,
                amount,
            });
            Ok(())
        }

        /// Burn tokens from your own account
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::burn())]
        pub fn burn(origin: OriginFor<T>, token_id: u64, amount: u128) -> DispatchResult {
            let who = ensure_signed(origin)?;
            ensure!(amount > 0, Error::<T>::ZeroAmount);

            let mut token = Tokens::<T>::get(token_id).ok_or(Error::<T>::TokenNotFound)?;
            ensure!(!token.is_frozen, Error::<T>::TokenFrozen);

            let balance = TokenBalances::<T>::get(token_id, &who);
            ensure!(balance >= amount, Error::<T>::InsufficientBalance);
            TokenBalances::<T>::insert(token_id, &who, balance.saturating_sub(amount));

            token.total_supply = token
                .total_supply
                .checked_sub(amount)
                .ok_or(Error::<T>::Underflow)?;
            Tokens::<T>::insert(token_id, token);

            Self::deposit_event(Event::Burned {
                token_id,
                from: who,
                amount,
            });
            Ok(())
        }

        /// Transfer tokens to another account
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::transfer())]
        pub fn transfer(
            origin: OriginFor<T>,
            token_id: u64,
            to: T::AccountId,
            amount: u128,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            if who == to {
                return Ok(());
            }
            ensure!(amount > 0, Error::<T>::ZeroAmount);

            let token = Tokens::<T>::get(token_id).ok_or(Error::<T>::TokenNotFound)?;
            ensure!(!token.is_frozen, Error::<T>::TokenFrozen);

            let from_balance = TokenBalances::<T>::get(token_id, &who);
            ensure!(from_balance >= amount, Error::<T>::InsufficientBalance);

            let to_balance = TokenBalances::<T>::get(token_id, &to);
            let new_to_balance = to_balance.checked_add(amount).ok_or(Error::<T>::Overflow)?;

            TokenBalances::<T>::insert(token_id, &who, from_balance.saturating_sub(amount));
            TokenBalances::<T>::insert(token_id, &to, new_to_balance);

            Self::deposit_event(Event::Transferred {
                token_id,
                from: who,
                to,
                amount,
            });
            Ok(())
        }

        /// Approve a spender to transfer tokens on your behalf
        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::approve())]
        pub fn approve(
            origin: OriginFor<T>,
            token_id: u64,
            spender: T::AccountId,
            amount: u128,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            let token = Tokens::<T>::get(token_id).ok_or(Error::<T>::TokenNotFound)?;
            ensure!(!token.is_frozen, Error::<T>::TokenFrozen);

            Allowances::<T>::insert(token_id, (&who, &spender), amount);

            Self::deposit_event(Event::Approved {
                token_id,
                owner: who,
                spender,
                amount,
            });
            Ok(())
        }

        /// Transfer tokens on behalf of an approved account
        #[pallet::call_index(5)]
        #[pallet::weight(T::WeightInfo::transfer_from())]
        pub fn transfer_from(
            origin: OriginFor<T>,
            token_id: u64,
            from: T::AccountId,
            to: T::AccountId,
            amount: u128,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            ensure!(amount > 0, Error::<T>::ZeroAmount);

            let token = Tokens::<T>::get(token_id).ok_or(Error::<T>::TokenNotFound)?;
            ensure!(!token.is_frozen, Error::<T>::TokenFrozen);

            let allowance = Allowances::<T>::get(token_id, (&from, &who));
            ensure!(allowance >= amount, Error::<T>::InsufficientAllowance);

            let from_balance = TokenBalances::<T>::get(token_id, &from);
            ensure!(from_balance >= amount, Error::<T>::InsufficientBalance);

            let to_balance = TokenBalances::<T>::get(token_id, &to);
            let new_to_balance = to_balance.checked_add(amount).ok_or(Error::<T>::Overflow)?;

            TokenBalances::<T>::insert(token_id, &from, from_balance.saturating_sub(amount));
            TokenBalances::<T>::insert(token_id, &to, new_to_balance);
            Allowances::<T>::insert(token_id, (&from, &who), allowance.saturating_sub(amount));

            Self::deposit_event(Event::Transferred {
                token_id,
                from,
                to,
                amount,
            });
            Ok(())
        }

        /// Set extended metadata for a token (owner only)
        #[pallet::call_index(6)]
        #[pallet::weight(T::WeightInfo::set_metadata(description.len() as u32))]
        pub fn set_metadata(
            origin: OriginFor<T>,
            token_id: u64,
            description: Vec<u8>,
            logo_uri: Vec<u8>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            let token = Tokens::<T>::get(token_id).ok_or(Error::<T>::TokenNotFound)?;
            ensure!(token.owner == who, Error::<T>::NotTokenOwner);
            ensure!(
                description.len() as u32 <= MAX_METADATA,
                Error::<T>::MetadataTooLong
            );
            ensure!(
                logo_uri.len() as u32 <= MAX_METADATA,
                Error::<T>::MetadataTooLong
            );

            let desc_bounded = BoundedVec::try_from(description.clone())
                .map_err(|_| Error::<T>::MetadataTooLong)?;
            let logo_bounded =
                BoundedVec::try_from(logo_uri.clone()).map_err(|_| Error::<T>::MetadataTooLong)?;

            TokenMetadataMap::<T>::insert(
                token_id,
                TokenMetadata {
                    description: desc_bounded,
                    logo_uri: logo_bounded,
                },
            );
            Self::deposit_event(Event::MetadataSet {
                token_id,
                description,
                logo_uri,
            });
            Ok(())
        }

        /// Freeze a token (owner only)
        #[pallet::call_index(7)]
        #[pallet::weight(T::WeightInfo::freeze())]
        pub fn freeze(origin: OriginFor<T>, token_id: u64) -> DispatchResult {
            let who = ensure_signed(origin)?;
            let mut token = Tokens::<T>::get(token_id).ok_or(Error::<T>::TokenNotFound)?;
            ensure!(token.owner == who, Error::<T>::NotTokenOwner);
            ensure!(!token.is_frozen, Error::<T>::TokenFrozen);
            token.is_frozen = true;
            Tokens::<T>::insert(token_id, token);
            Self::deposit_event(Event::TokenFrozen { token_id });
            Ok(())
        }

        /// Unfreeze a token (owner only)
        #[pallet::call_index(8)]
        #[pallet::weight(T::WeightInfo::thaw())]
        pub fn thaw(origin: OriginFor<T>, token_id: u64) -> DispatchResult {
            let who = ensure_signed(origin)?;
            let mut token = Tokens::<T>::get(token_id).ok_or(Error::<T>::TokenNotFound)?;
            ensure!(token.owner == who, Error::<T>::NotTokenOwner);
            ensure!(token.is_frozen, Error::<T>::TokenNotFrozen);
            token.is_frozen = false;
            Tokens::<T>::insert(token_id, token);
            Self::deposit_event(Event::TokenThawed { token_id });
            Ok(())
        }

        /// Destroy a token — requires zero total supply (owner only)
        #[pallet::call_index(9)]
        #[pallet::weight(T::WeightInfo::destroy())]
        pub fn destroy(origin: OriginFor<T>, token_id: u64) -> DispatchResult {
            let who = ensure_signed(origin)?;
            let token = Tokens::<T>::get(token_id).ok_or(Error::<T>::TokenNotFound)?;
            ensure!(token.owner == who, Error::<T>::NotTokenOwner);
            ensure!(token.total_supply == 0, Error::<T>::TokenStillHasSupply);

            Tokens::<T>::remove(token_id);
            TokenMetadataMap::<T>::remove(token_id);

            let mut owner_tokens = TokensByOwner::<T>::get(&who).unwrap_or_default();
            owner_tokens.retain(|&id| id != token_id);
            if owner_tokens.is_empty() {
                TokensByOwner::<T>::remove(&who);
            } else {
                TokensByOwner::<T>::insert(&who, owner_tokens);
            }

            let deposit = T::CreateTokenDeposit::get();
            T::Currency::unreserve(&who, deposit);

            Self::deposit_event(Event::TokenDestroyed {
                token_id,
                owner: who,
            });
            Ok(())
        }

        /// Batch transfer tokens to multiple recipients
        #[pallet::call_index(10)]
        #[pallet::weight(T::WeightInfo::batch_transfer(recipients.len() as u32))]
        pub fn batch_transfer(
            origin: OriginFor<T>,
            token_id: u64,
            recipients: Vec<(T::AccountId, u128)>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            let token = Tokens::<T>::get(token_id).ok_or(Error::<T>::TokenNotFound)?;
            ensure!(!token.is_frozen, Error::<T>::TokenFrozen);

            let mut total_needed: u128 = 0;
            for (_, amount) in recipients.iter() {
                ensure!(*amount > 0, Error::<T>::ZeroAmount);
                total_needed = total_needed
                    .checked_add(*amount)
                    .ok_or(Error::<T>::Overflow)?;
            }

            let from_balance = TokenBalances::<T>::get(token_id, &who);
            ensure!(
                from_balance >= total_needed,
                Error::<T>::InsufficientBalance
            );

            for (to, amount) in recipients.into_iter() {
                let to_balance = TokenBalances::<T>::get(token_id, &to);
                let new_to_balance = to_balance.checked_add(amount).ok_or(Error::<T>::Overflow)?;
                TokenBalances::<T>::insert(token_id, &to, new_to_balance);
                Self::deposit_event(Event::Transferred {
                    token_id,
                    from: who.clone(),
                    to,
                    amount,
                });
            }

            TokenBalances::<T>::insert(token_id, &who, from_balance.saturating_sub(total_needed));
            Ok(())
        }

        /// Transfer token ownership to a new account
        #[pallet::call_index(11)]
        #[pallet::weight(T::WeightInfo::transfer_ownership())]
        pub fn transfer_ownership(
            origin: OriginFor<T>,
            token_id: u64,
            new_owner: T::AccountId,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            let mut token = Tokens::<T>::get(token_id).ok_or(Error::<T>::TokenNotFound)?;
            ensure!(token.owner == who, Error::<T>::NotTokenOwner);

            // Update owner tracking
            let mut old_owner_tokens = TokensByOwner::<T>::get(&who).unwrap_or_default();
            old_owner_tokens.retain(|&id| id != token_id);
            if old_owner_tokens.is_empty() {
                TokensByOwner::<T>::remove(&who);
            } else {
                TokensByOwner::<T>::insert(&who, old_owner_tokens);
            }

            let mut new_owner_tokens = TokensByOwner::<T>::get(&new_owner).unwrap_or_default();
            new_owner_tokens
                .try_push(token_id)
                .map_err(|_| Error::<T>::TooManyTokensPerAccount)?;
            TokensByOwner::<T>::insert(&new_owner, new_owner_tokens);

            token.owner = new_owner.clone();
            Tokens::<T>::insert(token_id, token);

            // Transfer the native deposit reserve from old owner to new owner
            let deposit = T::CreateTokenDeposit::get();
            T::Currency::unreserve(&who, deposit);
            T::Currency::reserve(&new_owner, deposit)
                .map_err(|_| Error::<T>::InsufficientBalance)?;

            Self::deposit_event(Event::OwnershipTransferred {
                token_id,
                old_owner: who,
                new_owner,
            });
            Ok(())
        }

        /// Set per-token max supply cap (owner only, cannot be lowered below current supply)
        #[pallet::call_index(12)]
        #[pallet::weight(T::WeightInfo::mint())]
        pub fn set_max_supply(
            origin: OriginFor<T>,
            token_id: u64,
            max_supply: u128,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            let mut token = Tokens::<T>::get(token_id).ok_or(Error::<T>::TokenNotFound)?;
            ensure!(token.owner == who, Error::<T>::NotTokenOwner);
            // One-way ratchet: can only decrease max_supply, never increase.
            // This protects token holders from dilution via cap inflation.
            ensure!(
                max_supply <= token.max_supply,
                Error::<T>::MaxSupplyCannotIncrease
            );
            ensure!(
                max_supply >= token.total_supply,
                Error::<T>::MaxBalanceExceeded
            );
            token.max_supply = max_supply;
            Tokens::<T>::insert(token_id, token);
            Self::deposit_event(Event::MaxSupplySet {
                token_id,
                max_supply,
            });
            Ok(())
        }
    }

    impl<T: Config> Pallet<T> {
        pub fn balance_of(token_id: u64, who: &T::AccountId) -> u128 {
            TokenBalances::<T>::get(token_id, who)
        }

        /// Internal transfer — callable from other pallets (no origin check)
        pub fn do_transfer(
            token_id: u64,
            from: &T::AccountId,
            to: &T::AccountId,
            amount: u128,
        ) -> DispatchResult {
            let token = Tokens::<T>::get(token_id).ok_or(Error::<T>::TokenNotFound)?;
            ensure!(!token.is_frozen, Error::<T>::TokenFrozen);
            if from == to {
                return Ok(());
            }
            ensure!(amount > 0, Error::<T>::ZeroAmount);

            let from_balance = TokenBalances::<T>::get(token_id, from);
            ensure!(from_balance >= amount, Error::<T>::InsufficientBalance);

            let to_balance = TokenBalances::<T>::get(token_id, to);
            let new_to_balance = to_balance.checked_add(amount).ok_or(Error::<T>::Overflow)?;

            TokenBalances::<T>::insert(token_id, from, from_balance - amount);
            TokenBalances::<T>::insert(token_id, to, new_to_balance);

            Self::deposit_event(Event::Transferred {
                token_id,
                from: from.clone(),
                to: to.clone(),
                amount,
            });
            Ok(())
        }
        pub fn total_supply(token_id: u64) -> Option<u128> {
            Tokens::<T>::get(token_id).map(|t| t.total_supply)
        }
        pub fn allowance(token_id: u64, owner: &T::AccountId, spender: &T::AccountId) -> u128 {
            Allowances::<T>::get(token_id, (owner, spender))
        }
        pub fn token_info(token_id: u64) -> Option<TokenInfo<T::AccountId, u128>> {
            Tokens::<T>::get(token_id)
        }
        pub fn tokens_by_owner(who: &T::AccountId) -> Vec<u64> {
            TokensByOwner::<T>::get(who).unwrap_or_default().into()
        }
    }
}

#[cfg(test)]
mod tests;

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;
