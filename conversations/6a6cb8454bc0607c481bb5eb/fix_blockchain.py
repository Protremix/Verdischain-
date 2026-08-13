#!/usr/bin/env python3
"""Fix all blockchain vulnerabilities identified by Kimi audit."""
import sys

def fix_dex():
    """Fix DEX CEI violations in remove_liquidity and swap."""
    with open("pallets/amm-dex/src/lib.rs") as f:
        code = f.read()
    
    fixes = []
    
    # FIX 1: remove_liquidity — move state update before transfers
    old_remove = """            let dex_account: T::AccountId = T::PalletId::get().into_account_truncating();
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
            })?;"""
    
    new_remove = """            // CEI: Update state FIRST, then transfer (prevents reentrancy)
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
            )?;"""
    
    if old_remove in code:
        code = code.replace(old_remove, new_remove)
        fixes.append("FIX 1: DEX remove_liquidity CEI order fixed (state before transfers)")
    else:
        fixes.append("FIX 1: SKIP - remove_liquidity pattern not found")
    
    # FIX 2: swap — move reserve update before transfers
    old_swap = """            // Transfers FIRST (before state update for atomicity)
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
            )?;"""
    
    if old_swap in code:
        new_swap = """            // CEI: Update state FIRST, then transfer (prevents reentrancy)
            if is_a_to_b {
                pool.reserve_a = pool.reserve_a.checked_add(&amount_in).ok_or(Error::<T>::ArithmeticOverflow)?;
                pool.reserve_b = pool.reserve_b.checked_sub(&amount_out).ok_or(Error::<T>::ArithmeticUnderflow)?;
            } else {
                pool.reserve_b = pool.reserve_b.checked_add(&amount_in).ok_or(Error::<T>::ArithmeticOverflow)?;
                pool.reserve_a = pool.reserve_a.checked_sub(&amount_out).ok_or(Error::<T>::ArithmeticUnderflow)?;
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
            )?;"""
        
        code = code.replace(old_swap, new_swap)
        fixes.append("FIX 2: DEX swap CEI order fixed (state before transfers)")
        
        # Remove the duplicate state update that was after the transfers
        old_dup = """            // Update pool reserves
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
            Pools::<T>::insert(pool_id, pool);"""
        
        if old_dup in code:
            code = code.replace(old_dup, "")
            fixes.append("FIX 2b: Removed duplicate swap state update")
        else:
            fixes.append("FIX 2b: No duplicate found (may be different format)")
    else:
        fixes.append("FIX 2: SKIP - swap transfer pattern not found")
    
    with open("pallets/amm-dex/src/lib.rs", "w") as f:
        f.write(code)
    
    return fixes


def fix_presale():
    """Fix presale claim_refund CEI violation — clear state before transfers."""
    with open("pallets/presale/src/lib.rs") as f:
        code = f.read()
    
    fixes = []
    
    # The current order is: transfer tokens to escrow -> clear contribution -> update raised -> transfer refund
    # Fix: clear contribution -> update raised -> transfer tokens to escrow -> transfer refund
    old_refund = """            let refund_amount = contribution.total_paid;

            // Return purchased tokens from user to escrow (prevents double-dip exploit)
            let escrow = T::PalletId::get().into_account_truncating();
            let tokens_to_return = contribution.total_purchased;
            if tokens_to_return > BalanceOf::<T>::zero() {
                T::Currency::transfer(
                    &who,
                    &escrow,
                    tokens_to_return,
                    ExistenceRequirement::KeepAlive,
                ).map_err(|_| Error::<T>::InsufficientPayment)?;
            }

            // Clear contribution record
            Contributions::<T>::remove(round_id, &who);

            // Decrement RoundRaised and TotalRaised to prevent escrow accounting mismatch
            RoundRaised::<T>::mutate(round_id, |raised| {
                *raised = raised.checked_sub(&refund_amount).unwrap_or(0u32.into());
            });
            TotalRaised::<T>::mutate(|total| {
                *total = total.checked_sub(&refund_amount).unwrap_or(0u32.into());
            });

            // Transfer refund from escrow to user
            T::Currency::transfer(
                &escrow,
                &who,
                refund_amount,"""
    
    new_refund = """            let refund_amount = contribution.total_paid;
            let tokens_to_return = contribution.total_purchased;

            // CEI: Clear state FIRST (prevents reentrant double-claim)
            Contributions::<T>::remove(round_id, &who);

            // Decrement RoundRaised and TotalRaised
            RoundRaised::<T>::mutate(round_id, |raised| {
                *raised = raised.checked_sub(&refund_amount).unwrap_or(0u32.into());
            });
            TotalRaised::<T>::mutate(|total| {
                *total = total.checked_sub(&refund_amount).unwrap_or(0u32.into());
            });

            // Interactions: return purchased tokens to escrow, then refund
            let escrow = T::PalletId::get().into_account_truncating();
            if tokens_to_return > BalanceOf::<T>::zero() {
                T::Currency::transfer(
                    &who,
                    &escrow,
                    tokens_to_return,
                    ExistenceRequirement::KeepAlive,
                ).map_err(|_| Error::<T>::InsufficientPayment)?;
            }

            // Transfer refund from escrow to user
            T::Currency::transfer(
                &escrow,
                &who,
                refund_amount,"""
    
    if old_refund in code:
        code = code.replace(old_refund, new_refund)
        fixes.append("FIX 3: Presale claim_refund CEI order fixed (state before transfers)")
    else:
        fixes.append("FIX 3: SKIP - claim_refund pattern not found")
    
    with open("pallets/presale/src/lib.rs", "w") as f:
        f.write(code)
    
    return fixes


def fix_dpos():
    """Fix DPoS unregister — add cooldown and pending slash check."""
    with open("pallets/dpos/src/lib.rs") as f:
        code = f.read()
    
    fixes = []
    
    # Current unregister: immediately unreserve + remove validator
    # Fix: Check pending slashes, add unbonding period before funds release
    old_unregister = """        pub fn unregister_validator(origin: OriginFor<T>) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let validator = Validators::<T>::get(&who).ok_or(Error::<T>::ValidatorNotFound)?;
            ensure!(validator.active, Error::<T>::NotActiveValidator);
            ensure!(
                validator.total_votes <= validator.stake,
                Error::<T>::ActiveDelegations
            );

            T::Currency::unreserve(&who, validator.stake);
            Validators::<T>::remove(&who);
            ValidatorList::<T>::mutate(|v| v.retain(|a| a != &who));
            ActiveValidators::<T>::mutate(|v| v.retain(|a| a != &who));
            TotalStaked::<T>::try_mutate(|t| -> Result<(), Error<T>> {
                *t = t
                    .checked_sub(&validator.stake)
                    .ok_or(Error::<T>::Overflow)?;
                Ok(())
            })?;

            Self::deposit_event(Event::ValidatorUnregistered { who });
            Ok(())
        }"""
    
    new_unregister = """        pub fn unregister_validator(origin: OriginFor<T>) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let validator = Validators::<T>::get(&who).ok_or(Error::<T>::ValidatorNotFound)?;
            ensure!(validator.active, Error::<T>::NotActiveValidator);
            ensure!(
                validator.total_votes <= validator.stake,
                Error::<T>::ActiveDelegations
            );

            // Check for pending slashing events — cannot unregister while slashable
            let slash_count = SlashingEvents::<T>::get(&who);
            ensure!(slash_count == 0, Error::<T>::PendingSlashing);

            // Queue for unbonding instead of immediate release
            // Funds are locked for UnbondingPeriod blocks to allow slash application
            let current_block = frame_system::Pallet::<T>::block_number();
            let unbonding_period = T::UnbondingPeriod::get();
            let unlock_block = current_block + unbonding_period.into();

            UnbondingQueue::<T>::try_mutate(&who, |queue| {
                queue.try_push(UnbondingRequest {
                    who: who.clone(),
                    amount: validator.stake,
                    unlock_block,
                }).map_err(|_| Error::<T>::Overflow)
            })?;

            // Remove from active validator sets
            Validators::<T>::remove(&who);
            ValidatorList::<T>::mutate(|v| v.retain(|a| a != &who));
            ActiveValidators::<T>::mutate(|v| v.retain(|a| a != &who));
            TotalStaked::<T>::try_mutate(|t| -> Result<(), Error<T>> {
                *t = t
                    .checked_sub(&validator.stake)
                    .ok_or(Error::<T>::Overflow)?;
                Ok(())
            })?;

            Self::deposit_event(Event::ValidatorUnregistered { who });
            Ok(())
        }"""
    
    if old_unregister in code:
        code = code.replace(old_unregister, new_unregister)
        fixes.append("FIX 4: DPoS unregister — added pending slash check + unbonding queue")
    else:
        fixes.append("FIX 4: SKIP - unregister pattern not found")
    
    # Add PendingSlashing error if not exists
    if "PendingSlashing" not in code:
        # Add after SlashingFailed error
        code = code.replace(
            "SlashingFailed,",
            "SlashingFailed,\n        PendingSlashing,"
        )
        fixes.append("FIX 4b: Added PendingSlashing error variant")
    
    with open("pallets/dpos/src/lib.rs", "w") as f:
        f.write(code)
    
    return fixes


def fix_storage():
    """Fix storage cleanup_expired — add iteration cap."""
    with open("pallets/storage/src/lib.rs") as f:
        code = f.read()
    
    fixes = []
    
    # Add max iteration cap to cleanup_expired
    old_cleanup = "        pub fn cleanup_expired(origin: OriginFor<T>, ids: Vec<Vec<u8>>) -> DispatchResult {\n            let _caller = ensure_signed(origin)?;\n"
    
    new_cleanup = """        pub fn cleanup_expired(origin: OriginFor<T>, ids: Vec<Vec<u8>>) -> DispatchResult {
            let _caller = ensure_signed(origin)?;

            // Cap iterations to prevent block weight exhaustion
            ensure!(ids.len() <= 50, Error::<T>::TooManyIds);
"""
    
    if old_cleanup in code:
        code = code.replace(old_cleanup, new_cleanup)
        fixes.append("FIX 5: Storage cleanup_expired — added 50-item iteration cap")
        
        # Add TooManyIds error if not exists
        if "TooManyIds" not in code:
            # Find the error enum and add
            code = code.replace(
                "MaxRecordsReached,",
                "MaxRecordsReached,\n        TooManyIds,"
            )
            fixes.append("FIX 5b: Added TooManyIds error variant")
    else:
        fixes.append("FIX 5: SKIP - cleanup pattern not found")
    
    with open("pallets/storage/src/lib.rs", "w") as f:
        f.write(code)
    
    return fixes


def fix_eco():
    """Fix eco — add per-period mint ceiling for carbon credits."""
    with open("pallets/eco/src/lib.rs") as f:
        code = f.read()
    
    fixes = []
    
    # Add a per-block mint limit — max 10 carbon credits per block
    old_mint = """            ensure!(
                (CarbonCredits::<T>::iter().count() as u32) < T::MaxCarbonCredits::get(),
                Error::<T>::MaxCarbonCreditsReached
            );"""
    
    new_mint = """            ensure!(
                (CarbonCredits::<T>::iter().count() as u32) < T::MaxCarbonCredits::get(),
                Error::<T>::MaxCarbonCreditsReached
            );

            // Per-block mint ceiling: max 5 credits per block to prevent governance abuse
            let current_block = frame_system::Pallet::<T>::block_number();
            let last_mint_block = LastMintBlock::<T>::get();
            let credits_this_block = CreditsMintedThisBlock::<T>::get();
            ensure!(
                current_block != last_mint_block || credits_this_block < 5,
                Error::<T>::PerBlockMintLimitReached
            );
            if current_block != last_mint_block {
                CreditsMintedThisBlock::<T>::put(1u32);
                LastMintBlock::<T>::put(current_block);
            } else {
                CreditsMintedThisBlock::<T>::put(credits_this_block + 1);
            }"""
    
    if old_mint in code:
        code = code.replace(old_mint, new_mint)
        fixes.append("FIX 6: Eco mint_carbon_credit — added per-block mint ceiling (5)")
        
        # Add storage items and error
        if "LastMintBlock" not in code:
            # Add storage maps after existing storage declarations
            code = code.replace(
                "    #[pallet::storage]\n    #[pallet::getter(fn total_co2_offset)]",
                """    #[pallet::storage]
    #[pallet::getter(fn last_mint_block)]
    pub type LastMintBlock<T: Config> =
        StorageValue<_, frame_system::pallet_prelude::BlockNumberFor<T>, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn credits_minted_this_block)]
    pub type CreditsMintedThisBlock<T: Config> = StorageValue<_, u32, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn total_co2_offset)]"""
            )
            fixes.append("FIX 6b: Added LastMintBlock + CreditsMintedThisBlock storage")
        
        if "PerBlockMintLimitReached" not in code:
            code = code.replace(
                "MaxCarbonCreditsReached,",
                "MaxCarbonCreditsReached,\n        PerBlockMintLimitReached,"
            )
            fixes.append("FIX 6c: Added PerBlockMintLimitReached error")
    else:
        fixes.append("FIX 6: SKIP - mint pattern not found")
    
    with open("pallets/eco/src/lib.rs", "w") as f:
        f.write(code)
    
    return fixes


if __name__ == "__main__":
    all_fixes = []
    all_fixes.extend(fix_dex())
    all_fixes.extend(fix_presale())
    all_fixes.extend(fix_dpos())
    all_fixes.extend(fix_storage())
    all_fixes.extend(fix_eco())
    
    for f in all_fixes:
        print(f)
