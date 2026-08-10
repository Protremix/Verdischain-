import re

# Fix vesting pallet
with open("/opt/verdis-chain-rust/pallets/vesting/src/lib.rs", "r") as f:
    content = f.read()

# 1. Remove duplicate WithdrawReasons import (line 11)
content = content.replace(
    "use frame_support::traits::WithdrawReasons;\n",
    "",
    1  # Only remove the first occurrence (the standalone import)
)

# 2. Add Overflow and Underflow to the error enum
content = content.replace(
    "        ScheduleAlreadyExists,\n    }",
    "        ScheduleAlreadyExists,\n        Overflow,\n        Underflow,\n    }"
)

# 3. Check if the set_lock call uses the right WithdrawReasons path
# The original import is: traits::{tokens::WithdrawReasons, ...}
# But the code uses WithdrawReasons::TRANSFER and WithdrawReasons::except(...)
# In Substrate, WithdrawReasons is a flags type. Let's check if the usage is correct.
# The set_lock signature: set_lock(id: LockIdentifier, who: &AccountId, amount: Balance, reasons: WithdrawReasons)
# WithdrawReasons::TRANSFER is a single reason, but we might want all reasons except transfer
# Actually, to lock tokens from being transferred, we should use WithdrawReasons::TRANSFER
# (meaning: lock transfers) or just WithdrawReasons::all()

# Check if we need to use a different method. In Substrate v48:
# - set_lock takes WithdrawReasons which is a bitflags
# - To prevent transfers: WithdrawReasons::TRANSFER
# - But actually, "set_lock" with TRANSFER means "the lock prevents TRANSFER withdrawals"
# - So WithdrawReasons::TRANSFER is correct - it means the locked amount cannot be transferred

# 4. Also check if VESTING_LOCK_ID is properly defined
if "VESTING_LOCK_ID" in content and "const VESTING_LOCK_ID" not in content:
    # Need to add the constant
    content = content.replace(
        "    #[pallet::pallet]",
        "    /// Lock identifier for vesting balance locks\n    pub const VESTING_LOCK_ID: [u8; 8] = *b\"verdivst\";\n\n    #[pallet::pallet]"
    )

with open("/opt/verdis-chain-rust/pallets/vesting/src/lib.rs", "w") as f:
    f.write(content)
print("Vesting: all fixes applied")

# Also check if there are any other references to Overflow in vesting that need the error variant
with open("/opt/verdis-chain-rust/pallets/vesting/src/lib.rs", "r") as f:
    content = f.read()
if "Error::<T>::Overflow" in content:
    print("Vesting: Overflow error is used - variant added")
if "Error::<T>::Underflow" in content:
    print("Vesting: Underflow error is used - variant added")
