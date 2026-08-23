#!/usr/bin/env python3
import sys

with open("/opt/verdis-chain-rust/pallets/presale/src/lib.rs") as f:
    c = f.read()

# 1. Add EnforceUniqueVestingLabels to Config trait
old_config = "    type Treasury: Get<T::AccountId>;"
new_config = "    type Treasury: Get<T::AccountId>;\n    /// Enforce globally unique vesting labels per round (enable for mainnet)\n    type EnforceUniqueVestingLabels: Get<bool>;"
c = c.replace(old_config, new_config)

# 2. Make the uniqueness check conditional on the config flag
old_check = """            // MASTER-6 FIX: Enforce globally unique vesting labels per round.
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
new_check = """            // MASTER-6 FIX: Enforce globally unique vesting labels per round.
            // Prevents cross-round vesting deletion: a refund for round A
            // must not remove vesting belonging to round B.
            // Enabled via Config::EnforceUniqueVestingLabels (mainnet only).
            if T::EnforceUniqueVestingLabels::get() {
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
                }
            }"""
c = c.replace(old_check, new_check)

with open("/opt/verdis-chain-rust/pallets/presale/src/lib.rs", "w") as f:
    f.write(c)

print("Config flag added for EnforceUniqueVestingLabels")
