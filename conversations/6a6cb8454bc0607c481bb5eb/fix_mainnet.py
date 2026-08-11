#!/usr/bin/env python3
"""Fix mainnet genesis: 6 BABE/GRANDPA authorities + differentiated stakes"""

FILE = "/opt/verdis-chain-rust/node/src/chain_spec.rs"

with open(FILE) as f:
    content = f.read()

original = content

# Fix 1: Change mainnet ID from "verdis" to "verdis-mainnet"
content = content.replace('.with_id("verdis")\n    .with_protocol_id("verdis")',
                          '.with_id("verdis-mainnet")\n    .with_protocol_id("verdis-mainnet")')

# Fix 2: Only use first 6 validators for BABE/GRANDPA authorities
# Change from:
#   let babe_authorities: Vec<(BabeId, u64)> = session_keys
#       .iter()
#       .map(|(_, _, keys)| (keys.babe.clone(), 1))
#       .collect();
# To:
#   let babe_authorities: Vec<(BabeId, u64)> = session_keys
#       .iter()
#       .take(6)  // Only 6 initial authorities matching ActiveValidatorCount
#       .map(|(_, _, keys)| (keys.babe.clone(), 1))
#       .collect();

# This pattern appears 3 times (dev, testnet, mainnet). Only fix the mainnet one (last occurrence).
# The mainnet section starts with "fn mainnet_genesis"
mainnet_section_start = content.index("fn mainnet_genesis()")
mainnet_section = content[mainnet_section_start:]

# Fix BABE authorities in mainnet
mainnet_babe_old = """    let babe_authorities: Vec<(BabeId, u64)> = session_keys
        .iter()
        .map(|(_, _, keys)| (keys.babe.clone(), 1))
        .collect();
    let grandpa_authorities: Vec<(GrandpaId, u64)> = session_keys
        .iter()
        .map(|(_, _, keys)| (keys.grandpa.clone(), 1))
        .collect();"""

mainnet_babe_new = """    // Only first 6 validators are initial BABE/GRANDPA authorities
    // (matching ActiveValidatorCount=6). Others join via epoch rotation.
    let babe_authorities: Vec<(BabeId, u64)> = session_keys
        .iter()
        .take(6)
        .map(|(_, _, keys)| (keys.babe.clone(), 1))
        .collect();
    let grandpa_authorities: Vec<(GrandpaId, u64)> = session_keys
        .iter()
        .take(6)
        .map(|(_, _, keys)| (keys.grandpa.clone(), 1))
        .collect();"""

# Only replace in the mainnet section
new_mainnet_section = mainnet_section.replace(mainnet_babe_old, mainnet_babe_new, 1)
content = content[:mainnet_section_start] + new_mainnet_section

# Fix 3: Differentiate mainnet validator stakes (6 active at 10M, 15 standby at 1M)
mainnet_bal_old = """    // Fund ALL 21 validators with stake + existential deposit
    for uri in uris.iter() {
        let acct: AccountId = sr_from(uri).public().into();
        balances.push((acct, 10_001_000 * u));
    }

    // DPoS validators (21)
    let dpos_validators: Vec<(AccountId, u128, bool)> = uris
        .iter()
        .map(|uri| {
            let acct: AccountId = sr_from(uri).public().into();
            (acct, 10_000_000 * u, true)
        })
        .collect();"""

mainnet_bal_new = """    // Fund validators: 6 active (10.001M each) + 15 standby (1.001M each)
    for (i, uri) in uris.iter().enumerate() {
        let acct: AccountId = sr_from(uri).public().into();
        let amount = if i < 6 { 10_001_000 * u } else { 1_001_000 * u };
        balances.push((acct, amount));
    }

    // DPoS validators (21): 6 active (10M stake) + 15 standby (1M stake)
    let dpos_validators: Vec<(AccountId, u128, bool)> = uris
        .iter()
        .enumerate()
        .map(|(i, uri)| {
            let acct: AccountId = sr_from(uri).public().into();
            let stake = if i < 6 { 10_000_000 * u } else { 1_000_000 * u };
            (acct, stake, true)
        })
        .collect();"""

content = content.replace(mainnet_bal_old, mainnet_bal_new)

# Fix 4: Update mainnet team pool deduction (6*10.001M + 15*1.001M = 75.021M)
content = content.replace(
    "(team_multisig.clone(), 5 * bn - 21 * 10_001_000 * u),  // Team (5B) minus 21 validator funding",
    "(team_multisig.clone(), 5 * bn - 6 * 10_001_000 * u - 15 * 1_001_000 * u),  // Team (5B) minus validator funding (6 active + 15 standby)"
)

# Write
if content != original:
    with open(FILE, 'w') as f:
        f.write(content)
    print("All mainnet fixes applied")
else:
    print("No changes made")
