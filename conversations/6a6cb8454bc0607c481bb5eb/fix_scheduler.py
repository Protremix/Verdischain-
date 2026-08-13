#!/usr/bin/env python3
"""Fix Scheduler origins for post-sudo governance."""

with open("runtime/src/lib.rs") as f:
    code = f.read()

fixes = []

# Find and fix Scheduler ScheduleOrigin and ManagerOrigin
old_scheduler = """    type ScheduleOrigin = EnsureRoot<AccountId>;
    type MaxWeight = MaximumSchedulerWeight;"""

new_scheduler = """    // Post-sudo: Tech Committee (1/3) can schedule, Council (2/3) manages
    type ScheduleOrigin = pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance2, 1, 3>;
    type MaxWeight = MaximumSchedulerWeight;"""

if old_scheduler in code:
    code = code.replace(old_scheduler, new_scheduler)
    fixes.append("Scheduler: ScheduleOrigin -> Tech Committee 1/3 (post-sudo)")
else:
    # Try alternate pattern
    old2 = "    type ScheduleOrigin = EnsureRoot"
    new2 = "    // Post-sudo: Tech Committee (1/3) can schedule\n    type ScheduleOrigin = pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance2, 1, 3>"
    if old2 in code:
        code = code.replace(old2, new2)
        fixes.append("Scheduler: ScheduleOrigin -> Tech Committee 1/3 (post-sudo)")
    else:
        fixes.append("SKIP: Scheduler ScheduleOrigin not found")

# Fix ManagerOrigin
old_mgr = "    type ManagerOrigin = EnsureRoot<AccountId>;"
new_mgr = "    // Post-sudo: Council (2/3) manages scheduler\n    type ManagerOrigin = pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;"

if old_mgr in code:
    code = code.replace(old_mgr, new_mgr)
    fixes.append("Scheduler: ManagerOrigin -> Council 2/3 (post-sudo)")
else:
    fixes.append("SKIP: Scheduler ManagerOrigin not found")

with open("runtime/src/lib.rs", "w") as f:
    f.write(code)

for f in fixes:
    print(f)

# Count remaining
import re
remaining = re.findall(r'type \w+ = .*EnsureRoot', code)
print(f"\nRemaining EnsureRoot types: {len(remaining)} (Identity/NFTs - non-critical for mainnet)")
