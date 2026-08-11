#!/usr/bin/env python3
"""Fix BoundedVec try_into calls in circuit-breaker pallet."""

with open("/tmp/lib.rs", "r") as f:
    content = f.read()

# Fix is_paused
old1 = """            let name_vec = pallet_name.to_vec();
            let name_bv: BoundedVec<u8, ConstU32<32>> = match name_vec.try_into() {
                Ok(bv) => bv,
                Err(_) => return false,
            };"""
new1 = """            let name_bv: BoundedVec<u8, ConstU32<32>> = match Vec::from(pallet_name).try_into() {
                Ok(bv) => bv,
                Err(_) => return false,
            };"""
content = content.replace(old1, new1, 1)

# Fix pause_pallet and unpause_pallet
old2 = """            let name_bv: BoundedVec<u8, ConstU32<32>> =
                pallet_name.clone().try_into().map_err(|_| Error::<T>::PalletNameTooLong)?;"""
new2 = """            let name_bv: BoundedVec<u8, ConstU32<32>> =
                Vec::from(pallet_name.clone()).try_into().map_err(|_| Error::<T>::PalletNameTooLong)?;"""
content = content.replace(old2, new2)

with open("/tmp/lib.rs", "w") as f:
    f.write(content)
print("Fixed all try_into calls")
