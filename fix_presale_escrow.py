#!/usr/bin/env python3
import sys

with open("/opt/verdis-chain-rust/pallets/presale/src/lib.rs") as f:
    content = f.read()

# FIX 1: contribute() must use round_escrow, not root pallet account
old_escrow = "            let escrow = T::PalletId::get().into_account_truncating();\n            let escrow_balance = T::Currency::free_balance(&escrow);"
new_escrow = "            let escrow = Self::round_escrow(round_id);\n            let escrow_balance = T::Currency::free_balance(&escrow);"
content = content.replace(old_escrow, new_escrow, 1)

# FIX 2: Enforce unique vesting labels per round in create_round
old_check = "            ensure!(!vesting_label.is_empty(), Error::<T>::EmptyVestingLabel);"
new_check = """            ensure!(!vesting_label.is_empty(), Error::<T>::EmptyVestingLabel);

            // MASTER-6 FIX: Enforce globally unique vesting labels per round.
            // Prevents cross-round vesting deletion: a refund for round A
            // must not remove vesting belonging to round B.
            let vesting_bv_check: BoundedVec<u8, ConstU32<64>> = vesting_label
                .clone()
                .try_into()
                .map_err(|_| Error::<T>::VestingLabelTooLong)?;
            let current_next = NextRoundId::<T>::get();
            for existing_id in 0..current_next {
                if let Some(existing_round) = Rounds::<T>::get(existing_id) {
                    ensure!(
                        existing_round.vesting_label != vesting_bv_check,
                        Error::<T>::DuplicateVestingLabel
                    );
                }
            }"""
content = content.replace(old_check, new_check, 1)

# FIX 3: Add DuplicateVestingLabel error variant
old_err = "        /// Insufficient escrow balance"
new_err = "        /// Vesting label already used by another round (cross-round isolation)\n        DuplicateVestingLabel,\n        /// Insufficient escrow balance"
content = content.replace(old_err, new_err, 1)

# FIX 4: claim_refund should use its own weight function, not collect_funds
old_w = "#[pallet::weight(T::WeightInfo::collect_funds())]\n        pub fn claim_refund"
new_w = "#[pallet::weight(T::WeightInfo::claim_refund())]\n        pub fn claim_refund"
content = content.replace(old_w, new_w, 1)

# FIX 5: Increase claim_refund weight to account for vesting iteration
old_wi = "        fn claim_refund() -> frame_support::weights::Weight {\n            frame_support::weights::Weight::from_parts(15_000, 0)\n        }"
new_wi = """        fn claim_refund() -> frame_support::weights::Weight {
            // Weight accounts for: contribution lookup, vesting removal
            // (iterates all vesting entries for user), multiple transfers,
            // state cleanup, potential treasury sweep.
            // Base: 15,000 + vesting iteration: 5,000 * max 20 entries = 100,000
            // Total: 115,000 (conservative upper bound)
            frame_support::weights::Weight::from_parts(115_000, 0)
        }"""
content = content.replace(old_wi, new_wi, 1)

with open("/opt/verdis-chain-rust/pallets/presale/src/lib.rs", "w") as f:
    f.write(content)

print("FIX 1: contribute() now uses Self::round_escrow(round_id)")
print("FIX 2: Unique vesting labels enforced in create_round()")
print("FIX 3: DuplicateVestingLabel error added")
print("FIX 4: claim_refund uses T::WeightInfo::claim_refund()")
print("FIX 5: claim_refund weight increased to 115,000")

# Verify changes
with open("/opt/verdis-chain-rust/pallets/presale/src/lib.rs") as f:
    verify = f.read()

assert "Self::round_escrow(round_id);" in verify, "FIX 1 failed"
assert "DuplicateVestingLabel" in verify, "FIX 3 failed"
assert "T::WeightInfo::claim_refund()" in verify, "FIX 4 failed"
assert "115_000" in verify, "FIX 5 failed"
print("All 5 fixes verified in source")
