#!/usr/bin/env python3
"""Fix governance origins that use EnsureRoot (won't work without sudo)."""

with open("runtime/src/lib.rs") as f:
    code = f.read()

fixes = []

# 1. TechnicalCommittee SetMembersOrigin: EnsureRoot -> Council 2/3
old = """impl pallet_collective::Config<pallet_collective::Instance2> for Runtime {
    type RuntimeOrigin = RuntimeOrigin;
    type Proposal = RuntimeCall;
    type RuntimeEvent = RuntimeEvent;
    type MotionDuration = TechnicalCommitteeMotionDuration;
    type MaxProposals = TechnicalCommitteeMaxProposals;
    type MaxMembers = TechnicalCommitteeMaxMembers;
    type DefaultVote = pallet_collective::PrimeDefaultVote;
    type WeightInfo = ();
    type SetMembersOrigin = EnsureRoot<AccountId>;
    type MaxProposalWeight = MaximumSchedulerWeight;
    type DisapproveOrigin = EnsureRoot<AccountId>;
    type KillOrigin = EnsureRoot<AccountId>;
    type Consideration = ();
}"""

new = """impl pallet_collective::Config<pallet_collective::Instance2> for Runtime {
    type RuntimeOrigin = RuntimeOrigin;
    type Proposal = RuntimeCall;
    type RuntimeEvent = RuntimeEvent;
    type MotionDuration = TechnicalCommitteeMotionDuration;
    type MaxProposals = TechnicalCommitteeMaxProposals;
    type MaxMembers = TechnicalCommitteeMaxMembers;
    type DefaultVote = pallet_collective::PrimeDefaultVote;
    type WeightInfo = ();
    // Post-sudo: Council (2/3) controls tech committee composition
    type SetMembersOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    type MaxProposalWeight = MaximumSchedulerWeight;
    // Council (1/3) can disapprove, Council (2/3) can kill
    type DisapproveOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 1, 3>;
    type KillOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    type Consideration = ();
}"""

if old in code:
    code = code.replace(old, new)
    fixes.append("TechnicalCommittee: SetMembersOrigin/Disapprove/Kill -> Council (post-sudo)")
else:
    fixes.append("SKIP: TechnicalCommittee block not found")

# 2. Treasury SpendOrigin: EnsureRootWithSuccess -> Council 2/3
old_treasury = "    type SpendOrigin = frame_system::EnsureRootWithSuccess<AccountId, TreasuryMaxSpend>;"
new_treasury = """    // Post-sudo: Council (2/3) approves treasury spending
    type SpendOrigin = pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;"""

if old_treasury in code:
    code = code.replace(old_treasury, new_treasury)
    fixes.append("Treasury: SpendOrigin -> Council 2/3 (post-sudo)")
else:
    fixes.append("SKIP: Treasury SpendOrigin not found")

# 3. Check for any other EnsureRoot in governance contexts
import re
remaining_ensure_root = [m.start() for m in re.finditer(r'EnsureRoot', code)]
if remaining_ensure_root:
    # Show context of remaining EnsureRoot
    for pos in remaining_ensure_root:
        context = code[max(0,pos-80):pos+80]
        # Skip if it's in a comment or non-governance context
        if 'sudo' not in context.lower() and 'governance' not in context.lower():
            fixes.append(f"NOTE: EnsureRoot still at pos {pos}: ...{context.strip()[:60]}...")

with open("runtime/src/lib.rs", "w") as f:
    f.write(code)

for f in fixes:
    print(f)
