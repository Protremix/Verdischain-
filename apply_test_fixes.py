#!/usr/bin/env python3
"""Update presale tests for per-round escrow + PaymentCurrency."""

with open("/opt/verdis-chain-rust/pallets/presale/src/tests.rs") as f:
    tests = f.read()

# Fix 1: Add PaymentCurrency to test Config
old_test_config = """impl crate::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type Currency = Balances;
    type PalletId = PresalePalletId;
    type AdminOrigin = frame_system::EnsureRoot<u64>;
    type Vesting = ();
    type WeightInfo = ();
    type Treasury = TestTreasury;
}"""

new_test_config = """impl crate::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type Currency = Balances;
    type PaymentCurrency = Balances;
    type PalletId = PresalePalletId;
    type AdminOrigin = frame_system::EnsureRoot<u64>;
    type Vesting = ();
    type WeightInfo = ();
    type Treasury = TestTreasury;
}"""

tests = tests.replace(old_test_config, new_test_config)
print("1. Added PaymentCurrency to test Config")

# Fix 2: Update genesis to fund per-round escrows (round 0 and round 1)
old_genesis = """    let escrow = PresalePalletId::get().into_account_truncating();
    pallet_balances::GenesisConfig::<Test> {
        dev_accounts: None,
        balances: vec![
            (1, 1_000_000_000),
            (2, 1_000_000_000),
            (3, 1_000_000_000),
            (escrow, 1_000_000_000_000),
        ],
    }"""

new_genesis = """    let escrow_0 = PresalePalletId::get().into_sub_account_truncating(0u32);
    let escrow_1 = PresalePalletId::get().into_sub_account_truncating(1u32);
    let escrow_2 = PresalePalletId::get().into_sub_account_truncating(2u32);
    pallet_balances::GenesisConfig::<Test> {
        dev_accounts: None,
        balances: vec![
            (1, 1_000_000_000),
            (2, 1_000_000_000),
            (3, 1_000_000_000),
            (escrow_0, 1_000_000_000_000),
            (escrow_1, 1_000_000_000_000),
            (escrow_2, 1_000_000_000_000),
        ],
    }"""

tests = tests.replace(old_genesis, new_genesis)
print("2. Updated genesis to fund per-round escrows")

# Fix 3: Update escrow_account() helper to take round_id
old_helper = """fn escrow_account() -> u64 {
    PresalePalletId::get().into_account_truncating()
}"""

new_helper = """fn escrow_account() -> u64 {
    PresalePalletId::get().into_account_truncating()
}

fn round_escrow_account(round_id: u32) -> u64 {
    PresalePalletId::get().into_sub_account_truncating(round_id)
}"""

tests = tests.replace(old_helper, new_helper)
print("3. Added round_escrow_account() helper")

# Fix 4: Update test that checks escrow balance to use round_escrow_account
old_escrow_test = """        let escrow = escrow_account();
        let escrow_before = Balances::free_balance(escrow);"""

new_escrow_test = """        let escrow = round_escrow_account(0);
        let escrow_before = Balances::free_balance(escrow);"""

tests = tests.replace(old_escrow_test, new_escrow_test, 1)
print("4. Updated escrow balance test to use round_escrow_account(0)")

# Fix 5: Update halborn_tests escrow reference
# Check if halborn_tests uses escrow_account
print("\nChecking halborn_tests for escrow references...")

with open("/opt/verdis-chain-rust/pallets/presale/src/halborn_tests.rs") as f:
    halborn = f.read()

if "into_account_truncating" in halborn:
    halborn = halborn.replace(
        "PresalePalletId::get().into_account_truncating()",
        "PresalePalletId::get().into_sub_account_truncating(0u32)"
    )
    with open("/opt/verdis-chain-rust/pallets/presale/src/halborn_tests.rs", "w") as f:
        f.write(halborn)
    print("5. Updated halborn_tests escrow references")
else:
    print("5. No escrow references in halborn_tests")

# Fix 6: Check luna_adversarial_tests for escrow references
print("\nChecking luna_adversarial_tests for escrow references...")

with open("/opt/verdis-chain-rust/pallets/presale/src/luna_adversarial_tests.rs") as f:
    luna = f.read()

if "into_account_truncating" in luna:
    luna = luna.replace(
        "PresalePalletId::get().into_account_truncating()",
        "PresalePalletId::get().into_sub_account_truncating(0u32)"
    )
    with open("/opt/verdis-chain-rust/pallets/presale/src/luna_adversarial_tests.rs", "w") as f:
        f.write(luna)
    print("6. Updated luna_adversarial_tests escrow references")
else:
    print("6. No escrow references in luna_adversarial_tests")

with open("/opt/verdis-chain-rust/pallets/presale/src/tests.rs", "w") as f:
    f.write(tests)
print("\n=== Tests updated ===")

# Fix 7: Check vesting test config for MaxSchedulesPerAccount
print("\nChecking vesting tests...")
with open("/opt/verdis-chain-rust/pallets/vesting/src/lib.rs") as f:
    vesting = f.read()

# The vesting tests are in lib.rs itself. Check if MaxSchedulesPerAccount is in test config
if "type MaxSchedulesPerAccount = MaxSchedulesPerAccount" in vesting:
    print("7. Vesting test config has MaxSchedulesPerAccount - weight annotation will work")
else:
    print("7. WARNING: MaxSchedulesPerAccount not found in vesting test config")

print("\nAll test updates complete!")
