import re

# Fix chain_spec.rs: multiple issues
with open("/opt/verdis-chain-rust/node/src/chain_spec.rs", "r") as f:
    content = f.read()

# 1. Fix testnet_genesis: revert team_multisig back to sudo_account
# Only in the testnet_genesis function (lines ~393-725)
testnet_start = content.find("fn testnet_genesis()")
mainnet_start = content.find("fn mainnet_genesis()")

if testnet_start and mainnet_start:
    testnet_section = content[testnet_start:mainnet_start]
    # Check if team_multisig is in testnet
    if "team_multisig" in testnet_section:
        # The testnet should still use sudo_account
        # Find the definition and replace
        testnet_fixed = testnet_section.replace(
            "(team_multisig.clone(), 5 * bn),",
            "(sudo_account.clone(), 5 * bn - 6 * 10_001_000 * u),"
        )
        # Also need to add back sudo_account definition if it was removed
        if "let sudo_account" not in testnet_fixed and "let team_multisig" in testnet_fixed:
            testnet_fixed = testnet_fixed.replace(
                "let team_multisig:",
                "let sudo_account:"
            )
        elif "let sudo_account" not in testnet_fixed:
            # Add sudo_account back
            testnet_fixed = testnet_fixed.replace(
                "    let eco_pool:",
                "    let sudo_account: AccountId = Sr25519Keyring::Alice.to_account_id();\n    let eco_pool:"
            )
        content = content[:testnet_start] + testnet_fixed + content[mainnet_start:]

# 2. Fix dev_genesis: check if it was also affected
dev_start = content.find("fn dev_genesis()")
if dev_start and testnet_start:
    dev_section = content[dev_start:testnet_start]
    if "team_multisig" in dev_section:
        dev_fixed = dev_section.replace(
            "(team_multisig.clone(), 5 * bn),",
            "(sudo_account.clone(), 5 * bn - 6 * 10_001_000 * u),"
        )
        if "let sudo_account" not in dev_fixed and "let team_multisig" in dev_fixed:
            dev_fixed = dev_fixed.replace("let team_multisig:", "let sudo_account:")
        content = content[:dev_start] + dev_fixed + content[testnet_start:]

# 3. Fix mainnet_genesis: replace all Sr25519Keyring match arms with sr_from
mainnet_start = content.find("fn mainnet_genesis()")
if mainnet_start:
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
    
    # Replace build_session_keys to work with Vec<String>
    # Create a new function or convert
    mainnet = mainnet.replace(
        "let session_keys = build_session_keys(&uris);",
        "let uri_refs: Vec<&str> = uris.iter().map(|s| s.as_str()).collect();\n    let session_keys = build_session_keys(&uri_refs);"
    )
    
    # Replace ALL match *uri blocks with simple sr_from calls
    # Pattern: match *uri { "Alice" => ..., "Bob" => ..., _ => ... }
    # Replace with: sr_from(uri).public().into()
    
    # For the validator balances loop
    mainnet = re.sub(
        r'let acct: AccountId = match \*uri \{[^}]+\};\n(\s+)balances\.push',
        r'let acct: AccountId = sr_from(uri).public().into();\n\1balances.push',
        mainnet
    )
    
    # For dpos_validators
    mainnet = re.sub(
        r'let acct: AccountId = match \*uri \{[^}]+\};\n(\s+)\(acct, 10_000_000',
        r'let acct: AccountId = sr_from(uri).public().into();\n\1(acct, 10_000_000',
        mainnet
    )
    
    # For validator_names
    mainnet = re.sub(
        r'let acct: AccountId = match \*uri \{[^}]+\};\n(\s+)\(acct, uri\.as_bytes',
        r'let acct: AccountId = sr_from(uri).public().into();\n\1(acct, uri.as_bytes',
        mainnet
    )
    
    # For council_members
    mainnet = re.sub(
        r'\.map\(\|uri\| match \*uri \{[^}]+\}\)',
        '.map(|uri| sr_from(uri).public().into())',
        mainnet
    )
    
    content = content[:mainnet_start] + mainnet + content[mainnet_end:]

with open("/opt/verdis-chain-rust/node/src/chain_spec.rs", "w") as f:
    f.write(content)

print("Done: chain_spec.rs fully fixed")
