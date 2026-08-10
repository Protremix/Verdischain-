import re

with open("/opt/verdis-chain-rust/node/src/chain_spec.rs", "r") as f:
    content = f.read()

# Find mainnet_genesis function
mainnet_start = content.find("fn mainnet_genesis()")
if mainnet_start < 0:
    print("ERROR: mainnet_genesis not found")
    exit(1)

# Find matching closing brace
brace_count = 0
mainnet_end = mainnet_start
for i in range(mainnet_start, len(content)):
    if content[i] == "{":
        brace_count += 1
    elif content[i] == "}":
        brace_count -= 1
        if brace_count == 0:
            mainnet_end = i + 1
            break

mainnet = content[mainnet_start:mainnet_end]

# Replace ALL match *uri { ... } blocks with sr_from(uri).public().into()
# Use re.DOTALL for multiline matching
# Pattern 1: match *uri { ... };
# This matches the entire match block including the closing };
mainnet = re.sub(
    r'let acct: AccountId = match \*uri \{.*?\};',
    'let acct: AccountId = sr_from(uri).public().into();',
    mainnet,
    flags=re.DOTALL
)

# Pattern 2: .map(|uri| match *uri { ... })
# This matches the council_members map
mainnet = re.sub(
    r'\.map\(\|uri\| match \*uri \{.*?\}\)',
    '.map(|uri| sr_from(uri).public().into())',
    mainnet,
    flags=re.DOTALL
)

# Also fix the sr_from call format - mainnet uris are full strings like "//MAINNET_VALIDATOR_1"
# The old format was: sr_from(&format!("//{}", uri))
# Since the uri is already a full string like "//MAINNET_VALIDATOR_1", we need:
# sr_from(uri) not sr_from(&format!("//{}", uri))
# Actually sr_from takes &str, and uri is &String, so sr_from(uri) should work
# But let's make sure - the _ => arm used sr_from(&format!("//{}", uri))
# This would produce "////MAINNET_VALIDATOR_1" - double prefix!
# But we already replaced the entire match block, so this is handled.

content = content[:mainnet_start] + mainnet + content[mainnet_end:]

with open("/opt/verdis-chain-rust/node/src/chain_spec.rs", "w") as f:
    f.write(content)

# Verify
with open("/opt/verdis-chain-rust/node/src/chain_spec.rs", "r") as f:
    check = f.read()

mainnet_check = check[check.find("fn mainnet_genesis()"):]
if "Sr25519Keyring" in mainnet_check[:3000]:
    print("WARNING: Sr25519Keyring still found in mainnet_genesis")
else:
    print("OK: No Sr25519Keyring in mainnet_genesis")

if "match *uri" in mainnet_check[:3000]:
    print("WARNING: match *uri still found in mainnet_genesis")
else:
    print("OK: No match *uri in mainnet_genesis")

print("Done: mainnet_genesis match blocks replaced")
