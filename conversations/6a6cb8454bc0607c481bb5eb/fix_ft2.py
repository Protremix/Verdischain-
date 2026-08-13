#!/usr/bin/env python3
"""Fix fungible-tokens: create max_supply, event enum, set_max_supply extrinsic."""

with open("pallets/fungible-tokens/src/lib.rs") as f:
    ft = f.read()

# 1. Fix broken event enum — remove the incorrectly placed MaxSupplySet
ft = ft.replace(
    """        OwnershipTransferred {
        token_id: u64,
        old_owner: T::AccountId,
        new_owner: T::AccountId,
        MaxSupplySet { token_id: u64, max_supply: u128 },

    },""",
    """        OwnershipTransferred {
            token_id: u64,
            old_owner: T::AccountId,
            new_owner: T::AccountId,
        },
        MaxSupplySet {
            token_id: u64,
            max_supply: u128,
        },
    },"""
)
print("Fixed event enum")

# 2. Fix create function — add max_supply
old_create_token = """            let token_info = TokenInfo {
                owner: who.clone(),
                name: name_bounded,
                symbol: symbol_bounded,
                decimals,
                total_supply: 0u128,
                is_frozen: false,"""

new_create_token = """            let token_info = TokenInfo {
                owner: who.clone(),
                name: name_bounded,
                symbol: symbol_bounded,
                decimals,
                total_supply: 0u128,
                max_supply: T::MaxBalance::get(),
                is_frozen: false,"""

if old_create_token in ft:
    ft = ft.replace(old_create_token, new_create_token)
    print("Fixed create() with max_supply")
else:
    print("SKIP: create token_info not found")

# 3. Add set_max_supply extrinsic after transfer_ownership (call_index 11)
old_transfer_ownership_end = """        pub fn transfer_ownership(
            origin: OriginFor<T>,
            token_id: u64,
            new_owner: T::AccountId,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            let mut token = Tokens::<T>::get(token_id).ok_or(Error::<T>::TokenNotFound)?;
            ensure!(token.owner == who, Error::<T>::NotTokenOwner);
            ensure!(!token.is_frozen, Error::<T>::TokenFrozen);

            let old_owner = token.owner.clone();
            token.owner = new_owner.clone();
            Tokens::<T>::insert(token_id, token);

            // Update owner-to-tokens mapping
            let mut old_tokens = TokensByOwner::<T>::get(&old_owner).unwrap_or_default();
            old_tokens.retain(|&id| id != token_id);
            TokensByOwner::<T>::insert(&old_owner, old_tokens);

            let mut new_tokens = TokensByOwner::<T>::get(&new_owner).unwrap_or_default();
            if !new_tokens.contains(&token_id) {
                new_tokens.try_push(token_id).ok();
            }
            TokensByOwner::<T>::insert(&new_owner, new_tokens);

            Self::deposit_event(Event::OwnershipTransferred {
                token_id,
                old_owner,
                new_owner,
            });
            Ok(())
        }"""

new_transfer_ownership_end = old_transfer_ownership_end + """

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
            ensure!(max_supply >= token.total_supply, Error::<T>::MaxBalanceExceeded);
            token.max_supply = max_supply;
            Tokens::<T>::insert(token_id, token);
            Self::deposit_event(Event::MaxSupplySet {
                token_id,
                max_supply,
            });
            Ok(())
        }"""

if old_transfer_ownership_end in ft:
    ft = ft.replace(old_transfer_ownership_end, new_transfer_ownership_end)
    print("Added set_max_supply extrinsic (call_index 12)")
else:
    print("SKIP: transfer_ownership not found for set_max_supply")

# 4. Fix any test TokenInfo constructions that need max_supply
ft = ft.replace(
    "total_supply: 0u128,\n                max_supply: T::MaxBalance::get(),\n                is_frozen: false,",
    "total_supply: 0u128,\n                max_supply: T::MaxBalance::get(),\n                is_frozen: false,"
)

with open("pallets/fungible-tokens/src/lib.rs", "w") as f:
    f.write(ft)
