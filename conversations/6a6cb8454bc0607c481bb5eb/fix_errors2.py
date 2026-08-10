import re

# Fix 1: Presale - price_precision: 1 should be typed
with open("/opt/verdis-chain-rust/pallets/presale/src/lib.rs", "r") as f:
    content = f.read()

content = content.replace("price_precision: 1,", "price_precision: 1u32.into(),")
content = content.replace("price_precision: BalanceOf::<T>::one(),", "price_precision: 1u32.into(),")
# Also fix any raw 1 that didn't get typed
content = re.sub(r'price_precision:\s*1\b(?!u32)', 'price_precision: 1u32.into()', content)

with open("/opt/verdis-chain-rust/pallets/presale/src/lib.rs", "w") as f:
    f.write(content)
print("Presale: price_precision typed")

# Fix 2: Tokenomics - ? operator in closures
with open("/opt/verdis-chain-rust/pallets/tokenomics/src/lib.rs", "r") as f:
    content = f.read()

content = content.replace(
    "PresaleRaised::<T>::mutate(|r| *r = r.checked_add(&cost).ok_or(Error::<T>::CalculationOverflow)?);",
    "let new_raised = PresaleRaised::<T>::get().checked_add(&cost).ok_or(Error::<T>::CalculationOverflow)?;\n            PresaleRaised::<T>::put(new_raised);"
)
content = content.replace(
    "PresaleSold::<T>::mutate(|s| *s = s.checked_add(&amount).ok_or(Error::<T>::CalculationOverflow)?);",
    "let new_sold = PresaleSold::<T>::get().checked_add(&amount).ok_or(Error::<T>::CalculationOverflow)?;\n            PresaleSold::<T>::put(new_sold);"
)
# Fix ALL CirculatingSupply mutate closures (there are 2)
content = re.sub(
    r'CirculatingSupply::<T>::mutate\(\|c\| \*c = c\.checked_add\(&amount\)\.ok_or\(Error::<T>::CalculationOverflow\)\?\);',
    'let new_supply = CirculatingSupply::<T>::get().checked_add(&amount).ok_or(Error::<T>::CalculationOverflow)?;\n            CirculatingSupply::<T>::put(new_supply);',
    content
)

with open("/opt/verdis-chain-rust/pallets/tokenomics/src/lib.rs", "w") as f:
    f.write(content)
print("Tokenomics: closure ? operators fixed")

# Fix 3: Vesting - fix closures and imports
with open("/opt/verdis-chain-rust/pallets/vesting/src/lib.rs", "r") as f:
    content = f.read()

# Fix the mutate closures that use ? inside
content = content.replace(
    """            LockedBalances::<T>::mutate(&who, |l| {
                *l = l.checked_add(&amount).ok_or(Error::<T>::Overflow)?;
                Ok::<(), DispatchError>(())
            })?;""",
    """            let new_locked = LockedBalances::<T>::get(&who)
                .checked_add(&amount)
                .ok_or(Error::<T>::Overflow)?;
            LockedBalances::<T>::insert(&who, new_locked);"""
)

# Fix the checked_sub closure
content = content.replace(
    """            LockedBalances::<T>::mutate(&who, |l| {
                *l = l.checked_sub(&total_releasable).ok_or(Error::<T>::Underflow)?;
            });""",
    """            let new_locked = LockedBalances::<T>::get(&who)
                .checked_sub(&total_releasable)
                .ok_or(Error::<T>::Underflow)?;
            LockedBalances::<T>::insert(&who, new_locked);"""
)

# Also check for the old saturating_sub pattern if it still exists
content = content.replace(
    "LockedBalances::<T>::mutate(&who, |l| *l = l.saturating_sub(total_releasable));",
    """let new_locked = LockedBalances::<T>::get(&who)
                .checked_sub(&total_releasable)
                .ok_or(Error::<T>::Underflow)?;
            LockedBalances::<T>::insert(&who, new_locked);"""
)

# Ensure WithdrawReasons is imported
if "WithdrawReasons" in content and "use" not in content.split("WithdrawReasons")[0].split("\n")[-1]:
    # Check if it's already in an import
    if "use frame_support::traits::WithdrawReasons" not in content and "WithdrawReasons" in content:
        # Add it to existing imports or create new import
        if "use frame_support::traits::{Get, WithdrawReasons" in content:
            pass  # Already imported
        elif "use frame_support::traits::Currency" in content:
            content = content.replace(
                "use frame_support::traits::Currency",
                "use frame_support::traits::{Currency, WithdrawReasons}"
            )
        elif "use frame_support::traits::{Get" in content:
            content = content.replace(
                "use frame_support::traits::{Get,",
                "use frame_support::traits::{Get, WithdrawReasons,"
            )
        else:
            # Add new import line after first use statement
            content = content.replace(
                "use frame_support",
                "use frame_support::traits::WithdrawReasons;\nuse frame_support",
                1
            )

with open("/opt/verdis-chain-rust/pallets/vesting/src/lib.rs", "w") as f:
    f.write(content)
print("Vesting: closures and imports fixed")
