import sys

path = "/opt/verdis-chain-rust/pallets/vesting/src/lib.rs"
with open(path, "r") as f:
    content = f.read()

old = "BoundedVec<UserVestingEntry<BalanceOf<T>, BlockNumberFor<T>>, ConstU32<16>>"
new = "BoundedVec<UserVestingEntry<BalanceOf<T>, BlockNumberFor<T>>, T::MaxSchedulesPerAccount>"
content = content.replace(old, new)

with open(path, "w") as f:
    f.write(content)
print("Fixed: UserVestings now uses T::MaxSchedulesPerAccount bound")
