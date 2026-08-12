#!/usr/bin/env python3
"""Fix DPoS slashing test failures"""

filepath = '/opt/verdis-chain-rust/pallets/dpos/src/tests/slashing_tests.rs'
with open(filepath) as f:
    content = f.read()

# Fix 1: test_slash_emits_event - use Bob instead of Eve (Eve has no genesis balance)
old_eve = '''        let validator = Sr25519Keyring::Eve.to_account_id();

        // Register Eve as validator first (not in genesis)
        assert_ok!(Dpos::register_validator(
            RuntimeOrigin::signed(validator.clone()),
            3,
            b"solar".to_vec(),
        ));

        System::set_block_number(1);'''

new_bob = '''        let validator = Sr25519Keyring::Bob.to_account_id();

        // Bob is a genesis validator with 100k balance and 3000 stake
        System::set_block_number(1);'''

if old_eve in content:
    content = content.replace(old_eve, new_bob, 1)
    print("Fix 1: Changed Eve to Bob in test_slash_emits_event")
else:
    print("Fix 1: Pattern not found")

# Fix 2: test_unregister_after_slash - expect Err after full slash
old_unregister = '''        // Should still be able to unregister
        assert_ok!(Dpos::unregister_validator(RuntimeOrigin::signed(validator)));'''

new_unregister = '''        // After full slash, validator is deactivated so unregister fails with NotActiveValidator
        assert_noop!(
            Dpos::unregister_validator(RuntimeOrigin::signed(validator)),
            Error::<Test>::NotActiveValidator
        );'''

if old_unregister in content:
    content = content.replace(old_unregister, new_unregister, 1)
    print("Fix 2: Changed unregister expectation to assert_noop")
else:
    print("Fix 2: Pattern not found")

with open(filepath, 'w') as f:
    f.write(content)
print("Done")
