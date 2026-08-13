#!/usr/bin/env python3
"""Fix all remaining EnsureRoot origins for post-sudo governance."""

with open("runtime/src/lib.rs") as f:
    code = f.read()

fixes = []

# 1. Council (Instance1) DisapproveOrigin and KillOrigin
old_council = """    type SetMembersOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    type MaxProposalWeight = MaximumSchedulerWeight;
    type DisapproveOrigin = EnsureRoot<AccountId>;
    type KillOrigin = EnsureRoot<AccountId>;
    type Consideration = ();
}

// === Technical Committee"""

new_council = """    type SetMembersOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    type MaxProposalWeight = MaximumSchedulerWeight;
    // Post-sudo: Council self-governs — simple majority disapprove, 2/3 kill
    type DisapproveOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 1, 2>;
    type KillOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    type Consideration = ();
}

// === Technical Committee"""

if old_council in code:
    code = code.replace(old_council, new_council)
    fixes.append("Council: DisapproveOrigin -> 1/2, KillOrigin -> 2/3 (post-sudo)")
else:
    fixes.append("SKIP: Council DisapproveOrigin/KillOrigin block not found")

# 2. Presale AdminOrigin: EnsureRoot -> Council 2/3
old_presale = "    type AdminOrigin = frame_system::EnsureRoot<AccountId>;"
new_presale = "    // Post-sudo: Council (2/3) administers presale\n    type AdminOrigin = pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;"

if old_presale in code:
    code = code.replace(old_presale, new_presale)
    fixes.append("Presale: AdminOrigin -> Council 2/3 (post-sudo)")
else:
    fixes.append("SKIP: Presale AdminOrigin not found")

# 3. Democracy BlacklistOrigin: EnsureRoot -> Council 2/3
old_blacklist = "    type BlacklistOrigin = EnsureRoot<AccountId>;"
new_blacklist = "    // Post-sudo: Council (2/3) can blacklist proposals\n    type BlacklistOrigin = pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;"

if old_blacklist in code:
    code = code.replace(old_blacklist, new_blacklist)
    fixes.append("Democracy: BlacklistOrigin -> Council 2/3 (post-sudo)")
else:
    fixes.append("SKIP: Democracy BlacklistOrigin not found")

# 4. Democracy CancelProposalOrigin: EnsureRoot -> Council 2/3
old_cancel = "    type CancelProposalOrigin = EnsureRoot<AccountId>;"
new_cancel = "    // Post-sudo: Council (2/3) can cancel proposals\n    type CancelProposalOrigin = pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;"

if old_cancel in code:
    code = code.replace(old_cancel, new_cancel)
    fixes.append("Democracy: CancelProposalOrigin -> Council 2/3 (post-sudo)")
else:
    fixes.append("SKIP: Democracy CancelProposalOrigin not found")

with open("runtime/src/lib.rs", "w") as f:
    f.write(code)

for f in fixes:
    print(f)

# Verify no remaining critical EnsureRoot
import re
remaining = re.findall(r'type \w+ = .*EnsureRoot', code)
if remaining:
    print(f"\nRemaining EnsureRoot types: {len(remaining)}")
    for r in remaining:
        print(f"  {r.strip()}")
