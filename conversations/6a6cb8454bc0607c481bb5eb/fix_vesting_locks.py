import re

# FIX C-07: Add balance lock to vesting pallet
with open("/opt/verdis-chain-rust/pallets/vesting/src/lib.rs", "r") as f:
    content = f.read()

# Find the assign_vesting function and add a balance lock after assignment
# The lock should prevent users from transferring vested tokens until they unlock

old_assign_end = """            LockedBalances::<T>::mutate(&who, |l| {
                *l = l.checked_add(&amount).ok_or(Error::<T>::Overflow)?;
                Ok::<(), DispatchError>(())
            })?;

            Self::deposit_event(Event::VestingAssigned {
                who: who.clone(),
                schedule: schedule.clone(),
                amount,
            });
            Ok(())
        }"""

new_assign_end = """            LockedBalances::<T>::mutate(&who, |l| {
                *l = l.checked_add(&amount).ok_or(Error::<T>::Overflow)?;
                Ok::<(), DispatchError>(())
            })?;

            // Apply actual balance lock to prevent transfer of vested tokens
            let locked = LockedBalances::<T>::get(&who);
            T::Currency::set_lock(
                VESTING_LOCK_ID,
                &who,
                locked,
                WithdrawReasons::except(WithdrawReasons::TRANSFER),
            );

            Self::deposit_event(Event::VestingAssigned {
                who: who.clone(),
                schedule: schedule.clone(),
                amount,
            });
            Ok(())
        }"""

content = content.replace(old_assign_end, new_assign_end)

# Also update release_vested to remove the lock when fully released
old_release_end = """            // Remove lock if no more vested balance
            if LockedBalances::<T>::get(&who).is_zero() {
                T::Currency::remove_lock(VESTING_LOCK_ID, &who);
            }

            Self::deposit_event(Event::VestedReleased {
                who: who.clone(),
                amount: total_releasable,
            });
            Ok(())"""

# Check if the lock removal already exists
if "remove_lock" not in content:
    # Add lock removal after reducing locked balance
    old_locked_update = """            LockedBalances::<T>::mutate(&who, |l| *l = l.saturating_sub(total_releasable));

            Self::deposit_event(Event::VestedReleased {"""
    new_locked_update = """            LockedBalances::<T>::mutate(&who, |l| {
                *l = l.checked_sub(&total_releasable).ok_or(Error::<T>::Underflow)?;
            });

            // Update or remove the balance lock
            let remaining = LockedBalances::<T>::get(&who);
            if remaining.is_zero() {
                T::Currency::remove_lock(VESTING_LOCK_ID, &who);
            } else {
                T::Currency::set_lock(
                    VESTING_LOCK_ID,
                    &who,
                    remaining,
                    WithdrawReasons::except(WithdrawReasons::TRANSFER),
                );
            }

            Self::deposit_event(Event::VestedReleased {"""
    content = content.replace(old_locked_update, new_locked_update)

# Add VESTING_LOCK_ID constant if it doesn't exist
if "VESTING_LOCK_ID" not in content:
    # Add after the imports or at the top of the module
    content = content.replace(
        "    #[pallet::pallet]",
        "    /// Lock identifier for vesting balance locks\n    pub const VESTING_LOCK_ID: [u8; 8] = *b\"verdivst\";\n\n    #[pallet::pallet]"
    )

# Add WithdrawReasons import if not present
if "WithdrawReasons" not in content:
    content = content.replace(
        "use frame_support::traits::Currency",
        "use frame_support::traits::{Currency, WithdrawReasons}"
    )
    # Also check other import patterns
    if "WithdrawReasons" not in content:
        content = content.replace(
            "use frame_support::traits::Get",
            "use frame_support::traits::{Get, WithdrawReasons}"
        )

with open("/opt/verdis-chain-rust/pallets/vesting/src/lib.rs", "w") as f:
    f.write(content)

print("Done: vesting balance locks added")
