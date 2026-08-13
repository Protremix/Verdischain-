#!/usr/bin/env python3
"""Fix all remaining compilation errors."""

def fix_dpos():
    with open("pallets/dpos/src/lib.rs") as f:
        code = f.read()
    
    fixes = []
    
    # 1. Add PendingSlashing to Error enum (before the closing brace)
    if "PendingSlashing" not in code.split("pub enum Error")[1].split("}")[0]:
        code = code.replace(
            "        Overflow,\n    }",
            "        Overflow,\n        PendingSlashing,\n    }"
        )
        fixes.append("Added PendingSlashing to DPoS Error enum")
    
    # 2. Fix unregister_validator: use try_into for block number, fix UnbondingRequest fields, fix try_mutate
    old_unreg = """            // Check for pending slashing events — cannot unregister while slashable
            let slash_count = SlashingEvents::<T>::get(&who);
            ensure!(slash_count == 0, Error::<T>::PendingSlashing);

            // Queue for unbonding instead of immediate release
            // Funds are locked for UnbondingPeriod blocks to allow slash application
            let current_block: u32 = frame_system::Pallet::<T>::block_number().saturating_into();
            let unbonding_period = T::UnbondingPeriod::get();
            let unlock_block = current_block.saturating_add(unbonding_period);

            UnbondingQueue::<T>::try_mutate(&who, |queue| {
                queue.try_push(UnbondingRequest {
                    who: who.clone(),
                    amount: validator.stake,
                    unlock_block,
                }).map_err(|_| Error::<T>::Overflow)
            })?;"""
    
    new_unreg = """            // Check for pending slashing events — cannot unregister while slashable
            let slash_count = SlashingEvents::<T>::get(&who);
            ensure!(slash_count == 0, Error::<T>::PendingSlashing);

            // Queue for unbonding instead of immediate release
            let current_block: u32 = frame_system::Pallet::<T>::block_number().try_into().unwrap_or(0);
            let unbonding_period = T::UnbondingPeriod::get();
            let unlock_block = current_block.saturating_add(unbonding_period);

            UnbondingQueue::<T>::try_mutate(&who, |maybe_queue| {
                let queue = maybe_queue.get_or_insert_with(BoundedVec::default);
                queue.try_push(UnbondingRequest {
                    who: who.clone(),
                    validator: who.clone(),
                    amount: validator.stake,
                    unlock_block,
                }).map_err(|_| Error::<T>::UnbondingQueueFull)
            })?;"""
    
    if old_unreg in code:
        code = code.replace(old_unreg, new_unreg)
        fixes.append("Fixed DPoS unregister: block number conversion + UnbondingRequest fields + try_mutate")
    else:
        fixes.append("SKIP: DPoS unregister pattern not found for compile fix")
    
    with open("pallets/dpos/src/lib.rs", "w") as f:
        f.write(code)
    return fixes


def fix_eco():
    with open("pallets/eco/src/lib.rs") as f:
        code = f.read()
    
    fixes = []
    
    # 1. Add PerBlockMintLimitReached to Error enum
    if "PerBlockMintLimitReached" not in code.split("pub enum Error")[1].split("}")[0]:
        code = code.replace(
            "        LocationTooLong,\n    }",
            "        LocationTooLong,\n        PerBlockMintLimitReached,\n    }"
        )
        fixes.append("Added PerBlockMintLimitReached to Eco Error enum")
    
    # 2. Add storage declarations for LastMintBlock and CreditsMintedThisBlock
    # Check if they already exist as #[pallet::storage]
    if "pub type LastMintBlock" not in code:
        # Add before TotalCO2Offset
        code = code.replace(
            "    #[pallet::storage]\n    #[pallet::getter(fn total_co2_offset)]",
            """    #[pallet::storage]
    #[pallet::getter(fn last_mint_block)]
    pub type LastMintBlock<T: Config> = StorageValue<_, u32, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn credits_minted_this_block)]
    pub type CreditsMintedThisBlock<T: Config> = StorageValue<_, u32, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn total_co2_offset)]"""
        )
        fixes.append("Added LastMintBlock + CreditsMintedThisBlock storage declarations")
    
    # 3. Fix block number conversion: use try_into instead of saturating_into
    old_block = "let current_block: u32 = frame_system::Pallet::<T>::block_number().saturating_into();"
    new_block = "let current_block: u32 = frame_system::Pallet::<T>::block_number().try_into().unwrap_or(0);"
    
    if old_block in code:
        code = code.replace(old_block, new_block)
        fixes.append("Fixed Eco block number conversion (saturating_into -> try_into)")
    
    with open("pallets/eco/src/lib.rs", "w") as f:
        f.write(code)
    return fixes


def fix_storage():
    with open("pallets/storage/src/lib.rs") as f:
        code = f.read()
    
    fixes = []
    
    # Add TooManyIds to Error enum
    if "TooManyIds" not in code.split("pub enum Error")[1].split("}")[0]:
        code = code.replace(
            "        DepositOverflow,\n    }",
            "        DepositOverflow,\n        TooManyIds,\n    }"
        )
        fixes.append("Added TooManyIds to Storage Error enum")
    else:
        # Check if it's in the ensure! but not in the enum
        in_enum = "TooManyIds" in code.split("pub enum Error")[1].split("}")[0]
        if not in_enum:
            code = code.replace(
                "        DepositOverflow,\n    }",
                "        DepositOverflow,\n        TooManyIds,\n    }"
            )
            fixes.append("Added TooManyIds to Storage Error enum (was missing)")
    
    with open("pallets/storage/src/lib.rs", "w") as f:
        f.write(code)
    return fixes


if __name__ == "__main__":
    all_fixes = []
    all_fixes.extend(fix_dpos())
    all_fixes.extend(fix_eco())
    all_fixes.extend(fix_storage())
    
    for f in all_fixes:
        print(f)
