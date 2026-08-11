#!/usr/bin/env python3
"""Fix two P0 bugs in chain_spec.rs at SHA fc3f410:
1. Missing team pool (5B) from balances vector
2. Equal stakes causing rotate_epoch() to select keyless validators
"""
import sys

FILE = "/opt/verdis-chain-rust/node/src/chain_spec.rs"

with open(FILE) as f:
    content = f.read()

original = content

# ========================================
# FIX 1: DEV GENESIS — Add team pool entry
# ========================================
# The dev balances vector has 8 entries (95B) but is missing the 9th (team 5B).
# Add team_multisig entry with 5B minus validator stakes.

dev_old = """        (presale_pool, 2 * bn),
        // Team & Advisors (5B) minus 6 validator stakes (6 * 10K = 60K)
            ];
    // Fund ALL 6 validators with stake + existential deposit"""

dev_new = """        (presale_pool, 2 * bn),
        // Team & Advisors (5B) minus 6 validator stakes (6 * 10.001M = 60.006M)
        (PalletId(*b"verdistm").into_account_truncating(), 5 * bn - 6 * 10_001_000 * u),
            ];
    // Fund ALL 6 validators with stake + existential deposit"""

if dev_old in content:
    content = content.replace(dev_old, dev_new)
    print("FIX 1a: Added team pool to dev_genesis balances")
else:
    print("FIX 1a: SKIP - dev pattern not found")

# ========================================
# FIX 2: TESTNET GENESIS — Add team pool + differentiate stakes
# ========================================
# Fix 2a: Add team pool entry
testnet_bal_old = """        (presale_pool, 2 * bn),
        // Team & Advisors (5B) minus 6 validator stakes (6 * 10M = 60M)
            ];
    // Fund ALL 21 validators with stake + existential deposit
    for uri in uris.iter() {
        let acct: AccountId = match *uri {
            "Alice" => Sr25519Keyring::Alice.to_account_id(),
            "Bob" => Sr25519Keyring::Bob.to_account_id(),
            "Charlie" => Sr25519Keyring::Charlie.to_account_id(),
            "Dave" => Sr25519Keyring::Dave.to_account_id(),
            "Eve" => Sr25519Keyring::Eve.to_account_id(),
            "Ferdie" => Sr25519Keyring::Ferdie.to_account_id(),
            _ => sr_from(&format!("//{}", uri)).public().into(),
        };
        balances.push((acct, 10_001_000 * u));
    }"""

testnet_bal_new = """        (presale_pool, 2 * bn),
        // Team & Advisors (5B) minus validator funding (6*10.001M + 15*1.001M = 75.021M)
        (PalletId(*b"verdistm").into_account_truncating(), 5 * bn - 6 * 10_001_000 * u - 15 * 1_001_000 * u),
            ];
    // Fund validators: 6 active (10.001M each) + 15 standby (1.001M each)
    for (i, uri) in uris.iter().enumerate() {
        let acct: AccountId = match *uri {
            "Alice" => Sr25519Keyring::Alice.to_account_id(),
            "Bob" => Sr25519Keyring::Bob.to_account_id(),
            "Charlie" => Sr25519Keyring::Charlie.to_account_id(),
            "Dave" => Sr25519Keyring::Dave.to_account_id(),
            "Eve" => Sr25519Keyring::Eve.to_account_id(),
            "Ferdie" => Sr25519Keyring::Ferdie.to_account_id(),
            _ => sr_from(&format!("//{}", uri)).public().into(),
        };
        let amount = if i < 6 { 10_001_000 * u } else { 1_001_000 * u };
        balances.push((acct, amount));
    }"""

if testnet_bal_old in content:
    content = content.replace(testnet_bal_old, testnet_bal_new)
    print("FIX 2a: Added team pool + differentiated validator balances in testnet_genesis")
else:
    print("FIX 2a: SKIP - testnet balance pattern not found")

# Fix 2b: Differentiate DPOS stakes — Alice-Ferdie 10M, V7-V21 1M
testnet_dpos_old = """    // DPoS validators (21)
    let dpos_validators: Vec<(AccountId, u128, bool)> = uris
        .iter()
        .map(|uri| {
            let acct: AccountId = match *uri {
                "Alice" => Sr25519Keyring::Alice.to_account_id(),
                "Bob" => Sr25519Keyring::Bob.to_account_id(),
                "Charlie" => Sr25519Keyring::Charlie.to_account_id(),
                "Dave" => Sr25519Keyring::Dave.to_account_id(),
                "Eve" => Sr25519Keyring::Eve.to_account_id(),
                "Ferdie" => Sr25519Keyring::Ferdie.to_account_id(),
                _ => sr_from(&format!("//{}", uri)).public().into(),
            };
            (acct, 10_000_000 * u, true)
        })
        .collect();

    let validator_names: Vec<(AccountId, Vec<u8>)> = uris
        .iter()
        .map(|uri| {
            let acct: AccountId = match *uri {
                "Alice" => Sr25519Keyring::Alice.to_account_id(),
                "Bob" => Sr25519Keyring::Bob.to_account_id(),
                "Charlie" => Sr25519Keyring::Charlie.to_account_id(),
                "Dave" => Sr25519Keyring::Dave.to_account_id(),
                "Eve" => Sr25519Keyring::Eve.to_account_id(),
                "Ferdie" => Sr25519Keyring::Ferdie.to_account_id(),
                _ => sr_from(&format!("//{}", uri)).public().into(),
            };
            (acct, uri.as_bytes().to_vec())
        })
        .collect();

    // Testnet: full test eco data + 6 DEX pools"""

testnet_dpos_new = """    // DPoS validators (21): 6 active (10M stake) + 15 standby (1M stake)
    // Higher stake ensures rotate_epoch() selects validators with session keys
    let dpos_validators: Vec<(AccountId, u128, bool)> = uris
        .iter()
        .enumerate()
        .map(|(i, uri)| {
            let acct: AccountId = match *uri {
                "Alice" => Sr25519Keyring::Alice.to_account_id(),
                "Bob" => Sr25519Keyring::Bob.to_account_id(),
                "Charlie" => Sr25519Keyring::Charlie.to_account_id(),
                "Dave" => Sr25519Keyring::Dave.to_account_id(),
                "Eve" => Sr25519Keyring::Eve.to_account_id(),
                "Ferdie" => Sr25519Keyring::Ferdie.to_account_id(),
                _ => sr_from(&format!("//{}", uri)).public().into(),
            };
            let stake = if i < 6 { 10_000_000 * u } else { 1_000_000 * u };
            (acct, stake, true)
        })
        .collect();

    let validator_names: Vec<(AccountId, Vec<u8>)> = uris
        .iter()
        .map(|uri| {
            let acct: AccountId = match *uri {
                "Alice" => Sr25519Keyring::Alice.to_account_id(),
                "Bob" => Sr25519Keyring::Bob.to_account_id(),
                "Charlie" => Sr25519Keyring::Charlie.to_account_id(),
                "Dave" => Sr25519Keyring::Dave.to_account_id(),
                "Eve" => Sr25519Keyring::Eve.to_account_id(),
                "Ferdie" => Sr25519Keyring::Ferdie.to_account_id(),
                _ => sr_from(&format!("//{}", uri)).public().into(),
            };
            (acct, uri.as_bytes().to_vec())
        })
        .collect();

    // Testnet: full test eco data + 6 DEX pools"""

# Only replace the FIRST occurrence (testnet), not dev
idx = content.find(testnet_dpos_old)
if idx >= 0:
    # Find the second occurrence of the dpos pattern to skip dev
    # Actually, the dev version has different comment: "Dev DPoS validators (6)"
    # and doesn't have the "Testnet: full test eco data" line
    content = content[:idx] + testnet_dpos_new + content[idx + len(testnet_dpos_old):]
    print("FIX 2b: Differentiated DPOS stakes in testnet_genesis (6x10M + 15x1M)")
else:
    print("FIX 2b: SKIP - testnet dpos pattern not found")

# ========================================
# FIX 3: MAINNET GENESIS — Add team pool entry
# ========================================
mainnet_old = """        (presale_pool, 2 * bn),
        (team_multisig.clone(), 5 * bn),
            ];"""

mainnet_new = """        (presale_pool, 2 * bn),
        // Team & Advisors (5B) minus 21 validator stakes (21 * 10.001M = 210.021M)
        (team_multisig.clone(), 5 * bn - 21 * 10_001_000 * u),
            ];"""

if mainnet_old in content:
    content = content.replace(mainnet_old, mainnet_new)
    print("FIX 3: Fixed mainnet team pool to account for 21 validator stakes")
else:
    print("FIX 3: SKIP - mainnet pattern not found (may already be correct)")

# Write
if content != original:
    with open(FILE, 'w') as f:
        f.write(content)
    print("\nAll fixes applied to %s" % FILE)
    print("Changes: %d chars -> %d chars" % (len(original), len(content)))
else:
    print("\nNo changes made")
    sys.exit(1)
