import re

# FIX H-08: Division by zero in DEX price oracle
with open("/opt/verdis-chain-rust/pallets/amm-dex/src/lib.rs", "r") as f:
    content = f.read()

# Replace all pool.reserve_a / pool.reserve_b with safe division
# Pattern 1: / pool.reserve_a
content = content.replace(
    "/ pool.reserve_a;",
    ".checked_div(&pool.reserve_a).unwrap_or(0u32.into());"
)
content = content.replace(
    "/ pool.reserve_b;",
    ".checked_div(&pool.reserve_b).unwrap_or(0u32.into());"
)

# Also fix the swap function division - denominator could be zero
# The denominator is reserve_in + amount_in_after_fee, which can't be zero if amount_in > 0
# But if reserve_in = 0 and amount_in_after_fee = 0 (100% fee), it could be zero
# Already handled by the InsufficientLiquidity check, but let's add explicit guard
old_swap_div = """            let amount_out = numerator / denominator;"""
new_swap_div = """            let amount_out = numerator.checked_div(&denominator).ok_or(Error::<T>::InsufficientLiquidity)?;"""
content = content.replace(old_swap_div, new_swap_div)

# FIX H-01: Add MaxCommission to DPoS
print("DEX fixes applied")

with open("/opt/verdis-chain-rust/pallets/amm-dex/src/lib.rs", "w") as f:
    f.write(content)

# Now fix DPoS commission cap
with open("/opt/verdis-chain-rust/pallets/dpos/src/lib.rs", "r") as f:
    dpos = f.read()

# Add MaxCommission config trait if it doesn't exist
if "MaxCommission" not in dpos:
    # Add to Config trait
    old_config = "    type MaxStakePerValidator: Get<BalanceOf<Self>>;"
    new_config = "    type MaxStakePerValidator: Get<BalanceOf<Self>>;\n    type MaxCommission: Get<u8>;"
    dpos = dpos.replace(old_config, new_config)

# Add the cap check in set_commission
old_commission = """        pub fn set_commission(
            origin: OriginFor<T>,
            rate: u8,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            ensure!(rate <= 100, Error::<T>::InvalidSlashReason);"""

new_commission = """        pub fn set_commission(
            origin: OriginFor<T>,
            rate: u8,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;
            ensure!(rate <= T::MaxCommission::get(), Error::<T>::CommissionTooHigh);"""

dpos = dpos.replace(old_commission, new_commission)

# Add CommissionTooHigh error if it doesn't exist
if "CommissionTooHigh" not in dpos:
    dpos = dpos.replace(
        "InvalidSlashReason,",
        "InvalidSlashReason,\n        CommissionTooHigh,"
    )

with open("/opt/verdis-chain-rust/pallets/dpos/src/lib.rs", "w") as f:
    f.write(dpos)

print("DPoS commission cap added")

# Now add MaxCommission to runtime config
with open("/opt/verdis-chain-rust/runtime/src/lib.rs", "r") as f:
    runtime = f.read()

if "MaxCommission" not in runtime:
    # Add constant
    runtime = runtime.replace(
        "pub const MaxStakePerValidator: Balance = 1_000_000_000 * UNITS;",
        "pub const MaxStakePerValidator: Balance = 1_000_000_000 * UNITS;\n    pub const MaxCommission: u8 = 20; // Maximum 20% commission"
    )
    # Add to Config impl
    runtime = runtime.replace(
        "type MaxStakePerValidator = MaxStakePerValidator;",
        "type MaxStakePerValidator = MaxStakePerValidator;\n    type MaxCommission = MaxCommission;"
    )

with open("/opt/verdis-chain-rust/runtime/src/lib.rs", "w") as f:
    f.write(runtime)

print("Runtime MaxCommission configured")
