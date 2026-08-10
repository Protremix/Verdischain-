import re

path = "/opt/verdis-chain-rust/pallets/vesting/src/lib.rs"
with open(path, "r") as f:
    content = f.read()

# Replace the test to use 10 entries (matching MaxSchedulesPerAccount=10)
old_test = """    fn test_max_vesting_entries_per_account() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();

            // Assign 16 vesting entries (the max BoundedVec size)
            for i in 0..16 {
                let label = format!("sch{}", i);
                assert_ok!(Vesting::add_schedule(
                    RuntimeOrigin::root(),
                    label.as_bytes().to_vec(),
                    1_000_000u128,
                    60,
                    30,
                ));
                assert_ok!(Vesting::assign_vesting(
                    RuntimeOrigin::root(),
                    alice.clone(),
                    label.as_bytes().to_vec(),
                    1_000_000u128,
                ));
            }

            // 17th should fail with MaxVestingSchedules
            assert_ok!(Vesting::add_schedule(
                RuntimeOrigin::root(),
                b"sch16".to_vec(),
                1_000_000u128,
                60,
                30,
            ));
            assert_noop!(
                Vesting::assign_vesting(
                    RuntimeOrigin::root(),
                    alice,
                    b"sch16".to_vec(),
                    1_000_000u128,
                ),
                Error::<Test>::MaxVestingSchedules
            );
        });
    }"""

new_test = """    fn test_max_vesting_entries_per_account() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();

            // Assign 10 vesting entries (the max per-account limit)
            for i in 0..10 {
                let label = format!("sch{}", i);
                assert_ok!(Vesting::add_schedule(
                    RuntimeOrigin::root(),
                    label.as_bytes().to_vec(),
                    1_000_000u128,
                    60,
                    30,
                ));
                assert_ok!(Vesting::assign_vesting(
                    RuntimeOrigin::root(),
                    alice.clone(),
                    label.as_bytes().to_vec(),
                    1_000_000u128,
                ));
            }

            // 11th should fail with MaxVestingSchedules
            assert_ok!(Vesting::add_schedule(
                RuntimeOrigin::root(),
                b"sch10".to_vec(),
                1_000_000u128,
                60,
                30,
            ));
            assert_noop!(
                Vesting::assign_vesting(
                    RuntimeOrigin::root(),
                    alice,
                    b"sch10".to_vec(),
                    1_000_000u128,
                ),
                Error::<Test>::MaxVestingSchedules
            );
        });
    }"""

content = content.replace(old_test, new_test)

with open(path, "w") as f:
    f.write(content)
print("Fixed: test_max_vesting_entries_per_account updated for MaxSchedulesPerAccount=10")
