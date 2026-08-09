import re

with open("/opt/verdis-chain-rust/pallets/vesting/src/benchmarking.rs") as f:
    v = f.read()

# Fix assign_vesting: add funding before the vestings setup
old_assign = """        let mut vestings = BoundedVec::default();
        for _ in 0..(s - 1) {
            let entry = UserVestingEntry {
                schedule: label_bv.clone(),
                total_amount: amount,
                released: BalanceOf::<T>::zero(),
                start_block: frame_system::Pallet::<T>::block_number(),
                vested: BalanceOf::<T>::zero(),
            };
            assert!(vestings.try_push(entry).is_ok());
        }
        UserVestings::<T>::insert(&target, vestings);

        #[extrinsic_call]
        assign_vesting(RawOrigin::Root, target.clone(), schedule_label, amount);"""

new_assign = """        // Fund the target account so the lock can be set
        let funding = amount.saturating_mul(100u32.into());
        let _ = T::Currency::make_free_balance_be(&target, funding);

        let mut vestings = BoundedVec::default();
        for _ in 0..(s - 1) {
            let entry = UserVestingEntry {
                schedule: label_bv.clone(),
                total_amount: amount,
                released: BalanceOf::<T>::zero(),
                start_block: frame_system::Pallet::<T>::block_number(),
                vested: BalanceOf::<T>::zero(),
            };
            assert!(vestings.try_push(entry).is_ok());
        }
        UserVestings::<T>::insert(&target, vestings);

        #[extrinsic_call]
        assign_vesting(RawOrigin::Root, target.clone(), schedule_label, amount);"""

v = v.replace(old_assign, new_assign)

# Fix release_vested: add funding after total_locked is computed
old_release = """        let mut vestings = BoundedVec::default();
        let mut total_locked = BalanceOf::<T>::zero();
        for _ in 0..s {
            let entry = UserVestingEntry {
                schedule: label_bv.clone(),
                total_amount: amount,
                released: BalanceOf::<T>::zero(),
                start_block: 0u32.into(),
                vested: BalanceOf::<T>::zero(),
            };
            assert!(vestings.try_push(entry).is_ok());
            total_locked = total_locked.saturating_add(amount);
        }
        UserVestings::<T>::insert(&caller, vestings);
        LockedBalances::<T>::insert(&caller, total_locked);"""

new_release = """        let mut vestings = BoundedVec::default();
        let mut total_locked = BalanceOf::<T>::zero();
        for _ in 0..s {
            let entry = UserVestingEntry {
                schedule: label_bv.clone(),
                total_amount: amount,
                released: BalanceOf::<T>::zero(),
                start_block: 0u32.into(),
                vested: BalanceOf::<T>::zero(),
            };
            assert!(vestings.try_push(entry).is_ok());
            total_locked = total_locked.saturating_add(amount);
        }
        // Fund the caller account so the lock can be set
        let funding = total_locked.saturating_mul(100u32.into());
        let _ = T::Currency::make_free_balance_be(&caller, funding);
        UserVestings::<T>::insert(&caller, vestings);
        LockedBalances::<T>::insert(&caller, total_locked);"""

v = v.replace(old_release, new_release)

with open("/opt/verdis-chain-rust/pallets/vesting/src/benchmarking.rs", "w") as f:
    f.write(v)

print("Vesting benchmarking fixed")
print(f"assign_replaced: {old_assign in v == False}")
print(f"release_replaced: {old_release in v == False}")
