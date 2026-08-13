#!/usr/bin/env python3
"""Fix C5: Add per-token max_supply to fungible-tokens + fix compile."""

with open("pallets/fungible-tokens/src/lib.rs") as f:
    ft = f.read()

# 1. Add max_supply field to TokenInfo struct
old_struct = """pub struct TokenInfo<AccountId, Balance> {
    pub owner: AccountId,
    pub name: BoundedVec<u8, frame_support::traits::ConstU32<MAX_TOKEN_NAME>>,
    pub symbol: BoundedVec<u8, frame_support::traits::ConstU32<MAX_TOKEN_SYMBOL>>,
    pub decimals: u8,
    pub total_supply: Balance,
    pub is_frozen: bool,
    pub created_block: u32,
}"""

new_struct = """pub struct TokenInfo<AccountId, Balance> {
    pub owner: AccountId,
    pub name: BoundedVec<u8, frame_support::traits::ConstU32<MAX_TOKEN_NAME>>,
    pub symbol: BoundedVec<u8, frame_support::traits::ConstU32<MAX_TOKEN_SYMBOL>>,
    pub decimals: u8,
    pub total_supply: Balance,
    pub max_supply: Balance,
    pub is_frozen: bool,
    pub created_block: u32,
}"""

if old_struct in ft:
    ft = ft.replace(old_struct, new_struct)
    print("Added max_supply field to TokenInfo")
else:
    print("SKIP: TokenInfo struct not found")

# 2. Set max_supply in create function
old_create = """            let token = TokenInfo {
                owner: who.clone(),
                name: name_bounded,
                symbol: symbol_bounded,
                decimals,
                total_supply: 0,
                is_frozen: false,
                created_block: <frame_system::Pallet<T>>::block_number().try_into().unwrap_or(0),
            };"""

new_create = """            let token = TokenInfo {
                owner: who.clone(),
                name: name_bounded,
                symbol: symbol_bounded,
                decimals,
                total_supply: 0,
                max_supply: T::MaxBalance::get(),
                is_frozen: false,
                created_block: <frame_system::Pallet<T>>::block_number().try_into().unwrap_or(0),
            };"""

if old_create in ft:
    ft = ft.replace(old_create, new_create)
    print("Set max_supply = MaxBalance in create()")
else:
    # Try alternate format
    old_create2 = """            let token = TokenInfo {
                owner: who.clone(),
                name: name_bounded,
                symbol: symbol_bounded,
                decimals,
                total_supply: 0,
                is_frozen: false,
                created_block: <frame_system::Pallet<T>>::block_number().try_into().unwrap_or(0),
            };"""
    new_create2 = """            let token = TokenInfo {
                owner: who.clone(),
                name: name_bounded,
                symbol: symbol_bounded,
                decimals,
                total_supply: 0,
                max_supply: T::MaxBalance::get(),
                is_frozen: false,
                created_block: <frame_system::Pallet<T>>::block_number().try_into().unwrap_or(0),
            };"""
    if old_create2 in ft:
        ft = ft.replace(old_create2, new_create2)
        print("Set max_supply in create() (alt format)")
    else:
        print("SKIP: create() token construction not found")

# 3. Add set_max_supply extrinsic and check in mint
# Add max_supply check to mint function (in addition to MaxBalance)
old_mint_check = """            let new_supply = token
                .total_supply
                .checked_add(amount)
                .ok_or(Error::<T>::Overflow)?;
            ensure!(
                new_supply <= T::MaxBalance::get(),
                Error::<T>::MaxBalanceExceeded
            );"""

new_mint_check = """            let new_supply = token
                .total_supply
                .checked_add(amount)
                .ok_or(Error::<T>::Overflow)?;
            ensure!(
                new_supply <= token.max_supply,
                Error::<T>::MaxBalanceExceeded
            );"""

if old_mint_check in ft:
    ft = ft.replace(old_mint_check, new_mint_check)
    print("Mint: check against per-token max_supply")
else:
    print("SKIP: mint check not found")

# 4. Add set_max_supply extrinsic after freeze/thaw
# Find the freeze extrinsic and add set_max_supply after it
old_freeze = """        pub fn freeze(origin: OriginFor<T>, token_id: u64) -> DispatchResult {
            let who = ensure_signed(origin)?;
            let mut token = Tokens::<T>::get(token_id).ok_or(Error::<T>::TokenNotFound)?;
            ensure!(token.owner == who, Error::<T>::NotTokenOwner);
            ensure!(!token.is_frozen, Error::<T>::TokenFrozen);
            token.is_frozen = true;
            Tokens::<T>::insert(token_id, token);
            Self::deposit_event(Event::Frozen { token_id });
            Ok(())
        }"""

new_freeze = """        pub fn freeze(origin: OriginFor<T>, token_id: u64) -> DispatchResult {
            let who = ensure_signed(origin)?;
            let mut token = Tokens::<T>::get(token_id).ok_or(Error::<T>::TokenNotFound)?;
            ensure!(token.owner == who, Error::<T>::NotTokenOwner);
            ensure!(!token.is_frozen, Error::<T>::TokenFrozen);
            token.is_frozen = true;
            Tokens::<T>::insert(token_id, token);
            Self::deposit_event(Event::Frozen { token_id });
            Ok(())
        }

        /// Set per-token max supply cap (owner only, cannot be lowered below current supply)
        #[pallet::call_index(11)]
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
            Self::deposit_event(Event::MaxSupplySet { token_id, max_supply });
            Ok(())
        }"""

if old_freeze in ft:
    ft = ft.replace(old_freeze, new_freeze)
    print("Added set_max_supply extrinsic")
else:
    print("SKIP: freeze extrinsic not found")

# 5. Add MaxSupplySet event
old_event = """    pub enum Event<T: Config> {"""

# Check if MaxSupplySet already exists
if "MaxSupplySet" not in ft:
    # Find the last event variant and add after it
    # Find the Events enum
    import re
    event_match = re.search(r'pub enum Event<T: Config>\s*\{([^}]+)\}', ft, re.DOTALL)
    if event_match:
        events_body = event_match.group(1)
        # Add MaxSupplySet before the closing brace
        ft = ft.replace(
            events_body.rstrip(),
            events_body.rstrip().rstrip() + "\n        MaxSupplySet { token_id: u64, max_supply: u128 },\n"
        )
        print("Added MaxSupplySet event")
    else:
        print("SKIP: Event enum not found")
else:
    print("SKIP: MaxSupplySet already exists")

# 6. Update existing test calls that construct TokenInfo to include max_supply
# The tests might directly construct TokenInfo objects
ft = ft.replace(
    "total_supply: 0,\n                is_frozen: false,",
    "total_supply: 0,\n                max_supply: u128::MAX,\n                is_frozen: false,",
)
# Also handle any other pattern
ft = ft.replace(
    "total_supply: 0,\n            is_frozen: false,",
    "total_supply: 0,\n            max_supply: u128::MAX,\n            is_frozen: false,",
)

with open("pallets/fungible-tokens/src/lib.rs", "w") as f:
    f.write(ft)
