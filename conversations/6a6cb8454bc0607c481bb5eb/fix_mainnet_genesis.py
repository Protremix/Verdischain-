import re

with open("/opt/verdis-chain-rust/node/src/chain_spec.rs", "r") as f:
    content = f.read()

# 1. Add mainnet_validator_uris function
mainnet_uris = '''
fn mainnet_validator_uris() -> Vec<String> {
    // CRITICAL: PLACEHOLDER URIs - MUST be replaced before mainnet launch
    // Generate real keypairs: subkey generate --scheme sr25519
    (1..=21).map(|i| format!("//MAINNET_VALIDATOR_{}", i)).collect()
}

'''

if "fn mainnet_validator_uris" not in content:
    testnet_fn = "fn testnet_validator_uris() -> Vec<&'static str> {"
    content = content.replace(testnet_fn, mainnet_uris + testnet_fn)

# 2. Fix mainnet_genesis: remove sudo, use placeholder keys
old_header = "fn mainnet_genesis() -> verdis_runtime::RuntimeGenesisConfig {\n    use verdis_runtime::{BabeConfig, BalancesConfig, GrandpaConfig, SessionConfig, SudoConfig};\n\n    let sudo_account: AccountId = Sr25519Keyring::Alice.to_account_id();"
new_header = "fn mainnet_genesis() -> verdis_runtime::RuntimeGenesisConfig {\n    use verdis_runtime::{BabeConfig, BalancesConfig, GrandpaConfig, SessionConfig};\n\n    // CRITICAL: No Sudo on mainnet. Sudo is disabled.\n    let team_multisig: AccountId = PalletId(*b\"verdistm\").into_account_truncating();"
content = content.replace(old_header, new_header)

# 3. Replace sudo_account in balances with team_multisig
content = content.replace(
    "(sudo_account.clone(), 5 * bn - 6 * 10_001_000 * u),",
    "(team_multisig.clone(), 5 * bn),"
)

# 4. Replace testnet_validator_uris() call in mainnet with mainnet_validator_uris()
mainnet_start = content.find("fn mainnet_genesis()")
if mainnet_start >= 0:
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
    
    # Replace testnet_validator_uris() with mainnet_validator_uris()
    mainnet = mainnet.replace("let uris = testnet_validator_uris();", "let uris = mainnet_validator_uris();")
    
    # Replace all Sr25519Keyring match blocks with sr_from
    mainnet = re.sub(
        r'let acct: AccountId = match \*uri \{[^}]+\};\n(\s+)balances\.push',
        r'let acct: AccountId = sr_from(uri).public().into();\n\1balances.push',
        mainnet
    )
    
    mainnet = re.sub(
        r'let acct: AccountId = match \*uri \{[^}]+\};\n(\s+)\(acct, 10_000_000',
        r'let acct: AccountId = sr_from(uri).public().into();\n\1(acct, 10_000_000',
        mainnet
    )
    
    mainnet = re.sub(
        r'let acct: AccountId = match \*uri \{[^}]+\};\n(\s+)\(acct, uri\.as_bytes',
        r'let acct: AccountId = sr_from(uri).public().into();\n\1(acct, uri.as_bytes',
        mainnet
    )
    
    mainnet = re.sub(
        r'\.map\(\|uri\| match \*uri \{[^}]+\}\)',
        '.map(|uri| sr_from(uri).public().into())',
        mainnet
    )
    
    # Remove SudoConfig
    mainnet = mainnet.replace(
        "sudo: SudoConfig {\n            key: Some(sudo_account),\n        },",
        "// Sudo removed from mainnet - governance via Democracy/Council only"
    )
    
    content = content[:mainnet_start] + mainnet + content[mainnet_end:]

with open("/opt/verdis-chain-rust/node/src/chain_spec.rs", "w") as f:
    f.write(content)

print("Done: mainnet_genesis updated")
