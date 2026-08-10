import re

path = "/opt/verdis-chain-rust/pallets/presale/src/tests.rs"
with open(path, "r") as f:
    content = f.read()

# For each test that uses whitelist, add set_whitelist_required call after create_and_activate_round
# The pattern is: create_and_activate_round(...) followed by update_whitelist

# Test 1: test_whitelist (line 261)
content = content.replace(
    """        create_and_activate_round(0, 5, 1000, 100, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::update_whitelist(RuntimeOrigin::root(), 0, 1, true));""",
    """        create_and_activate_round(0, 5, 1000, 100, 1, 100, b"vest".to_vec());
        assert_ok!(Presale::set_whitelist_required(RuntimeOrigin::root(), 0, true));
        assert_ok!(Presale::update_whitelist(RuntimeOrigin::root(), 0, 1, true));"""
)

# Test 2: test_per_round_whitelist_independence (line 656)
# Need to see this test to fix it
content = content.replace(
    """fn test_per_round_whitelist_independence() {""",
    """fn test_per_round_whitelist_independence() {
    // H-02 FIX: whitelist_required flag must be set per round"""
)

# Test 3: test_attacker_whitelist_bypass (line 762)
content = content.replace(
    """fn test_attacker_whitelist_bypass() {""",
    """fn test_attacker_whitelist_bypass() {
    // H-02 FIX: whitelist_required flag prevents bypass"""
)

# Test 4: test_invariant_whitelist_restrictions_per_round (line 1167)
content = content.replace(
    """fn test_invariant_whitelist_restrictions_per_round() {""",
    """fn test_invariant_whitelist_restrictions_per_round() {
    // H-02 FIX: whitelist_required flag enforces per-round restrictions"""
)

# Now I need to add set_whitelist_required calls in the test bodies where whitelist is used
# Let me find all create_and_activate_round calls that are followed by update_whitelist
# and add set_whitelist_required between them

# General pattern: after any create_and_activate_round that is followed by update_whitelist,
# add set_whitelist_required
# This regex finds create_and_activate_round(...) followed by update_whitelist
# and inserts set_whitelist_required between them

# Let me be more specific - find each test and add the call
# For test_per_round_whitelist_independence, test_attacker_whitelist_bypass, test_invariant_whitelist_restrictions_per_round

# Find all instances where create_and_activate_round is followed by update_whitelist
# and insert set_whitelist_required
lines = content.split('\n')
new_lines = []
i = 0
while i < len(lines):
    new_lines.append(lines[i])
    # Check if this line has create_and_activate_round
    if 'create_and_activate_round(' in lines[i]:
        # Check if it's a multi-line call (ends with open paren)
        # Collect the full call
        while i < len(lines) and not lines[i].rstrip().endswith('));'):
            i += 1
            new_lines.append(lines[i])
        # Now check if next non-empty line has update_whitelist
        if i + 1 < len(lines):
            # Look ahead for update_whitelist
            for j in range(i+1, min(i+5, len(lines))):
                if 'update_whitelist' in lines[j] and 'set_whitelist_required' not in content[max(0, sum(len(l)+1 for l in lines[:i])):content.find('update_whitelist', sum(len(l)+1 for l in lines[:i]))]:
                    # Insert set_whitelist_required call with the same round_id
                    # Extract round_id from the create_and_activate_round call
                    # Get indentation from the next line
                    indent = len(lines[j]) - len(lines[j].lstrip())
                    round_id = '0'  # default
                    # Try to extract round_id from create_and_activate_round call
                    for k in range(i, -1, -1):
                        if 'create_and_activate_round(' in lines[k]:
                            # First argument is round_id_expected
                            match = re.search(r'create_and_activate_round\((\d+)', lines[k])
                            if match:
                                round_id = match.group(1)
                            break
                    new_lines.append(' ' * indent + f'assert_ok!(Presale::set_whitelist_required(RuntimeOrigin::root(), {round_id}, true));')
                    break
    i += 1

content = '\n'.join(new_lines)

with open(path, "w") as f:
    f.write(content)
print("Fixed: set_whitelist_required calls added to whitelist tests")
