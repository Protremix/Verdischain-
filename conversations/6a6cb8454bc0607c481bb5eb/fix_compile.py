#!/usr/bin/env python3
"""Fix compilation errors from the audit fixes."""

def fix_dpos_compile():
    """Fix DPoS unlock_block type mismatch."""
    with open("pallets/dpos/src/lib.rs") as f:
        code = f.read()
    
    fixes = []
    
    # Fix: unlock_block needs to be u32, but block_number() returns BlockNumberFor<T>
    # Use saturating_into() to convert
    old = "            let current_block = frame_system::Pallet::<T>::block_number();\n            let unbonding_period = T::UnbondingPeriod::get();\n            let unlock_block = current_block + unbonding_period.into();"
    
    new = "            let current_block: u32 = frame_system::Pallet::<T>::block_number().saturating_into();\n            let unbonding_period = T::UnbondingPeriod::get();\n            let unlock_block = current_block.saturating_add(unbonding_period);"
    
    if old in code:
        code = code.replace(old, new)
        fixes.append("Fixed DPoS unlock_block type (BlockNumberFor -> u32)")
    else:
        # Try alternate patterns
        old2 = "let unlock_block = current_block + unbonding_period.into();"
        new2 = "let unlock_block: u32 = current_block.saturating_add(unbonding_period);"
        if old2 in code:
            code = code.replace(old2, new2)
            fixes.append("Fixed DPoS unlock_block (alternate pattern)")
        
        # Also fix the current_block to be u32
        old3 = "let current_block = frame_system::Pallet::<T>::block_number();\n            let unbonding_period = T::UnbondingPeriod::get();"
        new3 = "let current_block: u32 = frame_system::Pallet::<T>::block_number().saturating_into();\n            let unbonding_period = T::UnbondingPeriod::get();"
        if old3 in code:
            code = code.replace(old3, new3)
            fixes.append("Fixed DPoS current_block type")
    
    with open("pallets/dpos/src/lib.rs", "w") as f:
        f.write(code)
    return fixes


def fix_eco_compile():
    """Fix Eco storage type errors."""
    with open("pallets/eco/src/lib.rs") as f:
        code = f.read()
    
    fixes = []
    
    # Fix 1: Use u32 for LastMintBlock instead of BlockNumberFor (simpler)
    old_storage = """    #[pallet::storage]
    #[pallet::getter(fn last_mint_block)]
    pub type LastMintBlock<T: Config> =
        StorageValue<_, frame_system::pallet_prelude::BlockNumberFor<T>, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn credits_minted_this_block)]
    pub type CreditsMintedThisBlock<T: Config> = StorageValue<_, u32, ValueQuery>;"""
    
    new_storage = """    #[pallet::storage]
    #[pallet::getter(fn last_mint_block)]
    pub type LastMintBlock<T: Config> = StorageValue<_, u32, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn credits_minted_this_block)]
    pub type CreditsMintedThisBlock<T: Config> = StorageValue<_, u32, ValueQuery>;"""
    
    if old_storage in code:
        code = code.replace(old_storage, new_storage)
        fixes.append("Fixed Eco LastMintBlock type (BlockNumberFor -> u32)")
    
    # Fix 2: Use saturating_into for block number conversion
    old_mint = """            let current_block = frame_system::Pallet::<T>::block_number();
            let last_mint_block = LastMintBlock::<T>::get();
            let credits_this_block = CreditsMintedThisBlock::<T>::get();"""
    
    new_mint = """            let current_block: u32 = frame_system::Pallet::<T>::block_number().saturating_into();
            let last_mint_block = LastMintBlock::<T>::get();
            let credits_this_block = CreditsMintedThisBlock::<T>::get();"""
    
    if old_mint in code:
        code = code.replace(old_mint, new_mint)
        fixes.append("Fixed Eco block number type conversion")
    
    # Fix 3: Remove the BlockNumberFor put and use u32
    old_put = "                LastMintBlock::<T>::put(current_block);"
    new_put = "                LastMintBlock::<T>::put(current_block);"
    # This should be fine since both are u32 now
    
    with open("pallets/eco/src/lib.rs", "w") as f:
        f.write(code)
    return fixes


def fix_storage_compile():
    """Fix Storage TooManyIds error."""
    with open("pallets/storage/src/lib.rs") as f:
        code = f.read()
    
    fixes = []
    
    # Check if TooManyIds was added
    if "TooManyIds" not in code:
        # Find the error enum and add TooManyIds
        # Look for any error variant to add after
        lines = code.split("\n")
        for i, line in enumerate(lines):
            if "MaxRecordsReached" in line or "MaxSize" in line or "StorageNotFound" in line:
                # Add TooManyIds after this line
                lines.insert(i + 1, "        TooManyIds,")
                fixes.append(f"Added TooManyIds error at line {i+1}")
                break
        code = "\n".join(lines)
    else:
        fixes.append("TooManyIds already exists")
    
    with open("pallets/storage/src/lib.rs", "w") as f:
        f.write(code)
    return fixes


if __name__ == "__main__":
    all_fixes = []
    all_fixes.extend(fix_dpos_compile())
    all_fixes.extend(fix_eco_compile())
    all_fixes.extend(fix_storage_compile())
    
    for f in all_fixes:
        print(f)
