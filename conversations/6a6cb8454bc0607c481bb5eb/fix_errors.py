import re

# Fix missing error variants

# 1. Tokenomics: Add ZeroAmount, ZeroPrice, CalculationOverflow
with open("/opt/verdis-chain-rust/pallets/tokenomics/src/lib.rs", "r") as f:
    content = f.read()

# Add error variants after AlreadyConsented
content = content.replace(
    "        AlreadyConsented,\n    }",
    "        AlreadyConsented,\n        ZeroAmount,\n        ZeroPrice,\n        CalculationOverflow,\n    }"
)

with open("/opt/verdis-chain-rust/pallets/tokenomics/src/lib.rs", "w") as f:
    f.write(content)
print("Tokenomics: error variants added")

# 2. DPoS: Add CommissionTooHigh
with open("/opt/verdis-chain-rust/pallets/dpos/src/lib.rs", "r") as f:
    content = f.read()

# Find the last error variant before closing brace
content = content.replace(
    "        VoteStorageFull,\n        UnbondingQueueFull,",
    "        VoteStorageFull,\n        UnbondingQueueFull,\n        CommissionTooHigh,"
)

with open("/opt/verdis-chain-rust/pallets/dpos/src/lib.rs", "w") as f:
    f.write(content)
print("DPoS: CommissionTooHigh error added")

# 3. Check vesting compilation error (E0308 - type mismatch)
with open("/opt/verdis-chain-rust/pallets/vesting/src/lib.rs", "r") as f:
    vesting = f.read()

# The set_lock API might have different signature
# Check if we need to import WithdrawReasons differently
# Also the lock_id might need to be different type
print("Checking vesting...")
