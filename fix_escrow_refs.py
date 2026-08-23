#!/usr/bin/env python3
"""Fix all escrow references across presale pallet and test files."""

# ============================================================
# Fix 1: Update pallet's public escrow_account() to return round-0 escrow
# ============================================================
with open("/opt/verdis-chain-rust/pallets/presale/src/lib.rs") as f:
    lib = f.read()

old_escrow_fn = """        /// Returns the deterministic escrow account for this pallet.
        pub fn escrow_account() -> T::AccountId {
            T::PalletId::get().into_account_truncating()
        }"""

new_escrow_fn = """        /// Returns the escrow account for round 0 (backward compat).
        /// Use round_escrow(round_id) for per-round escrow accounts.
        pub fn escrow_account() -> T::AccountId {
            Self::round_escrow(0)
        }"""

lib = lib.replace(old_escrow_fn, new_escrow_fn)
with open("/opt/verdis-chain-rust/pallets/presale/src/lib.rs", "w") as f:
    f.write(lib)
print("1. Updated pallet escrow_account() to return round_escrow(0)")

# ============================================================
# Fix 2: Update tests.rs - make escrow_account() return round-0 escrow
# ============================================================
with open("/opt/verdis-chain-rust/pallets/presale/src/tests.rs") as f:
    tests = f.read()

old_test_helper = """fn escrow_account() -> u64 {
    PresalePalletId::get().into_account_truncating()
}"""

new_test_helper = """fn escrow_account() -> u64 {
    // Backward compat: returns round-0 escrow (most tests use round 0)
    PresalePalletId::get().into_sub_account_truncating(0u32)
}"""

tests = tests.replace(old_test_helper, new_test_helper)
print("2. Updated tests.rs escrow_account() helper")

# Fix the deterministic test
old_det_test = """fn test_escrow_account_deterministic() {
        let escrow = Presale::escrow_account();
        let expected: u64 = PresalePalletId::get().into_account_truncating();"""

new_det_test = """fn test_escrow_account_deterministic() {
        let escrow = Presale::escrow_account();
        let expected: u64 = PresalePalletId::get().into_sub_account_truncating(0u32);"""

tests = tests.replace(old_det_test, new_det_test)
print("3. Updated deterministic escrow test")

# Fix the funded-in-genesis test to check round-0 escrow
old_funded_test = """fn test_escrow_account_funded_in_genesis() {
        let escrow = escrow_account();"""
# This should already work since escrow_account() now returns round-0 escrow
# But let's verify it checks the right balance
print("4. escrow_account_funded_in_genesis should work (uses escrow_account() = round-0)")

with open("/opt/verdis-chain-rust/pallets/presale/src/tests.rs", "w") as f:
    f.write(tests)

# ============================================================
# Fix 3: Update halborn_tests.rs escrow_account()
# ============================================================
with open("/opt/verdis-chain-rust/pallets/presale/src/halborn_tests.rs") as f:
    halborn = f.read()

old_halborn = """fn escrow_account() -> u64 {
    PresalePalletId::get().into_account_truncating()
}"""

new_halborn = """fn escrow_account() -> u64 {
    PresalePalletId::get().into_sub_account_truncating(0u32)
}"""

if old_halborn in halborn:
    halborn = halborn.replace(old_halborn, new_halborn)
    with open("/opt/verdis-chain-rust/pallets/presale/src/halborn_tests.rs", "w") as f:
        f.write(halborn)
    print("5. Updated halborn_tests.rs escrow_account()")
else:
    # Try the already-updated version
    old_halborn2 = "PresalePalletId::get().into_sub_account_truncating(0u32)"
    if old_halborn2 in halborn:
        print("5. halborn_tests.rs already updated")
    else:
        print("5. WARNING: halborn_tests.rs escrow_account() not found")

# ============================================================
# Fix 4: Update luna_adversarial_tests.rs
# ============================================================
with open("/opt/verdis-chain-rust/pallets/presale/src/luna_adversarial_tests.rs") as f:
    luna = f.read()

if "into_account_truncating" in luna:
    luna = luna.replace(
        "PresalePalletId::get().into_account_truncating()",
        "PresalePalletId::get().into_sub_account_truncating(0u32)"
    )
    with open("/opt/verdis-chain-rust/pallets/presale/src/luna_adversarial_tests.rs", "w") as f:
        f.write(luna)
    print("6. Updated luna_adversarial_tests.rs escrow references")
else:
    print("6. luna_adversarial_tests.rs already updated or no references")

# ============================================================
# Fix 5: Check presale_tests.rs for escrow references
# ============================================================
with open("/opt/verdis-chain-rust/pallets/presale/src/presale_tests.rs") as f:
    presale_tests = f.read()

if "into_account_truncating" in presale_tests:
    presale_tests = presale_tests.replace(
        "PresalePalletId::get().into_account_truncating()",
        "PresalePalletId::get().into_sub_account_truncating(0u32)"
    )
    with open("/opt/verdis-chain-rust/pallets/presale/src/presale_tests.rs", "w") as f:
        f.write(presale_tests)
    print("7. Updated presale_tests.rs escrow references")
else:
    print("7. presale_tests.rs no direct escrow references")

print("\nAll escrow references fixed!")
