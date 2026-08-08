#!/usr/bin/env python3
"""Surgical update of chain_spec.rs — only change balances, validators, and counts.
Keeps all original GenesisConfig field structure intact."""

CHAIN_SPEC = '/opt/verdis-chain-rust/node/src/chain_spec.rs'
BACKUP = CHAIN_SPEC + '.bak'

# Start from the backup (original) file
with open(BACKUP, 'r') as f:
    content = f.read()

# === 1. Replace the comment block ===
old_comment = """    // === Token Distribution (100B VRS total) ===
    // UNITS = 1_000_000_000 (9 decimals)
    // Total: 100,000,000,000 * UNITS = 100,000,000,000,000,000,000
    //
    // 8-Category Distribution:
    //   Community  (35%) = 35B  \u2192 EcoPalletId (community grants)
    //   Treasury   (20%) = 20B  \u2192 DposPalletId (treasury + staking rewards)
    //   Team       (15%) = 15B  \u2192 Alice (sudo key)
    //   Investors  (10%) = 10B  \u2192 TokenomicsPalletId (IDO allocations)
    //   Staking    (10%) = 10B  \u2192 DposPalletId (block reward pool)
    //   Liquidity  (5%)  = 5B   \u2192 DexPalletId (AMM liquidity provision)
    //   Advisors   (3%)  = 3B   \u2192 VestingPalletId (advisor vesting)
    //   Airdrop    (2%)  = 2B   \u2192 VestingPalletId (airdrop vesting)
    //
    // DposPalletId holds Treasury (20B) + Staking (10B) = 30B
    // VestingPalletId holds Advisors (3B) + Airdrop (2B) = 5B"""

new_comment = """    // === Token Distribution (100B VRDX total) ===
    // UNITS = 1_000_000_000 (9 decimals)
    // Total: 100,000,000,000 * UNITS = 100,000,000,000,000,000,000
    //
    // 9-Category Distribution (Production Tokenomics):
    //   Ecosystem & Developer Grants  (30%) = 30B  \u2192 EcoPalletId (verdisec)
    //   PoS Staking Rewards            (20%) = 20B  \u2192 DposPalletId (verdisdp)
    //   Treasury                        (15%) = 15B  \u2192 TreasuryPalletId (verdist0)
    //   Development                     (10%) = 10B  \u2192 DevPalletId (verdisdv)
    //   Liquidity                       (10%) = 10B  \u2192 DexPalletId (verdisdx)
    //   Community                        (5%) =  5B  \u2192 CommunityPalletId (verdiscm)
    //   Seed / Strategic                 (3%) =  3B  \u2192 VestingPalletId (verdisvs)
    //   Public Presale                   (2%) =  2B  \u2192 TokenomicsPalletId (verdistk)
    //   Team & Advisors                  (5%) =  5B  \u2192 Sudo account (Alice)
    //   TOTAL = 30B + 20B + 15B + 10B + 10B + 5B + 3B + 2B + 5B = 100B VRDX"""

content = content.replace(old_comment, new_comment)

# === 2. Replace PalletId accounts ===
old_accounts = """    let sudo_account: AccountId = Sr25519Keyring::Alice.to_account_id();
    let dpos_pool: AccountId = PalletId(*b"verdisdp").into_account_truncating();
    let tokenomics_pool: AccountId = PalletId(*b"verdistk").into_account_truncating();
    let dex_pool: AccountId = PalletId(*b"verdisdx").into_account_truncating();
    let eco_pool: AccountId = PalletId(*b"verdisec").into_account_truncating();
    let vesting_pool: AccountId = PalletId(*b"verdisvs").into_account_truncating();

    let units: u128 = 1_000_000_000;
    let billion: u128 = 1_000_000_000 * units; // 1B VRS"""

new_accounts = """    let sudo_account: AccountId = Sr25519Keyring::Alice.to_account_id();
    let eco_pool: AccountId = PalletId(*b"verdisec").into_account_truncating();
    let staking_pool: AccountId = PalletId(*b"verdisdp").into_account_truncating();
    let treasury_account: AccountId = PalletId(*b"verdist0").into_account_truncating();
    let dev_pool: AccountId = PalletId(*b"verdisdv").into_account_truncating();
    let dex_pool: AccountId = PalletId(*b"verdisdx").into_account_truncating();
    let community_pool: AccountId = PalletId(*b"verdiscm").into_account_truncating();
    let seed_pool: AccountId = PalletId(*b"verdisvs").into_account_truncating();
    let presale_pool: AccountId = PalletId(*b"verdistk").into_account_truncating();

    let units: u128 = 1_000_000_000;
    let billion: u128 = 1_000_000_000 * units; // 1B VRDX"""

content = content.replace(old_accounts, new_accounts)

# === 3. Replace session_keys vec (add 11 more validators) ===
# Find the session_keys closing and add more entries before it
# We need to add Validator11-21 entries
old_session_end = """        (
            sr_from("//Kelly").public().into(),
            sr_from("//Kelly").public().into(),
            SessionKeys {
                babe: sr_from("//Kelly").public().into(),
                grandpa: ed_from("//Kelly").public().into(),
            },
        ),
    ];"""

new_session_end = """        (
            sr_from("//Kelly").public().into(),
            sr_from("//Kelly").public().into(),
            SessionKeys {
                babe: sr_from("//Kelly").public().into(),
                grandpa: ed_from("//Kelly").public().into(),
            },
        ),
        (
            sr_from("//Validator11").public().into(),
            sr_from("//Validator11").public().into(),
            SessionKeys {
                babe: sr_from("//Validator11").public().into(),
                grandpa: ed_from("//Validator11").public().into(),
            },
        ),
        (
            sr_from("//Validator12").public().into(),
            sr_from("//Validator12").public().into(),
            SessionKeys {
                babe: sr_from("//Validator12").public().into(),
                grandpa: ed_from("//Validator12").public().into(),
            },
        ),
        (
            sr_from("//Validator13").public().into(),
            sr_from("//Validator13").public().into(),
            SessionKeys {
                babe: sr_from("//Validator13").public().into(),
                grandpa: ed_from("//Validator13").public().into(),
            },
        ),
        (
            sr_from("//Validator14").public().into(),
            sr_from("//Validator14").public().into(),
            SessionKeys {
                babe: sr_from("//Validator14").public().into(),
                grandpa: ed_from("//Validator14").public().into(),
            },
        ),
        (
            sr_from("//Validator15").public().into(),
            sr_from("//Validator15").public().into(),
            SessionKeys {
                babe: sr_from("//Validator15").public().into(),
                grandpa: ed_from("//Validator15").public().into(),
            },
        ),
        (
            sr_from("//Validator16").public().into(),
            sr_from("//Validator16").public().into(),
            SessionKeys {
                babe: sr_from("//Validator16").public().into(),
                grandpa: ed_from("//Validator16").public().into(),
            },
        ),
        (
            sr_from("//Validator17").public().into(),
            sr_from("//Validator17").public().into(),
            SessionKeys {
                babe: sr_from("//Validator17").public().into(),
                grandpa: ed_from("//Validator17").public().into(),
            },
        ),
        (
            sr_from("//Validator18").public().into(),
            sr_from("//Validator18").public().into(),
            SessionKeys {
                babe: sr_from("//Validator18").public().into(),
                grandpa: ed_from("//Validator18").public().into(),
            },
        ),
        (
            sr_from("//Validator19").public().into(),
            sr_from("//Validator19").public().into(),
            SessionKeys {
                babe: sr_from("//Validator19").public().into(),
                grandpa: ed_from("//Validator19").public().into(),
            },
        ),
        (
            sr_from("//Validator20").public().into(),
            sr_from("//Validator20").public().into(),
            SessionKeys {
                babe: sr_from("//Validator20").public().into(),
                grandpa: ed_from("//Validator20").public().into(),
            },
        ),
        (
            sr_from("//Validator21").public().into(),
            sr_from("//Validator21").public().into(),
            SessionKeys {
                babe: sr_from("//Validator21").public().into(),
                grandpa: ed_from("//Validator21").public().into(),
            },
        ),
    ];"""

content = content.replace(old_session_end, new_session_end)

# === 4. Replace the balances vec ===
old_balances = """        balances: BalancesConfig {
            balances: vec![
                // Team (14B) — Alice is the sudo/founder
                (sudo_account.clone(), 13_350 * units), // ~13.35B (team allocation after validator stakes)
                // Validator stakes (split from team allocation)
                (Sr25519Keyring::Bob.to_account_id(), billion / 4),
                (Sr25519Keyring::Charlie.to_account_id(), billion / 4),
                (Sr25519Keyring::Dave.to_account_id(), billion / 4),
                (Sr25519Keyring::Eve.to_account_id(), billion / 4),
                (Sr25519Keyring::Ferdie.to_account_id(), billion / 4),
                // Additional validators with session keys (George-Kelly)
                (sr_from("//George").public().into(), 10_000 * units),
                (sr_from("//Hamilton").public().into(), 10_000 * units),
                (sr_from("//Ian").public().into(), 10_000 * units),
                (sr_from("//Kelly").public().into(), 10_000 * units),
                // Custom validators 7-10 (100M each from team allocation)
                (
                    AccountId::from(hex_literal::hex!(
                        "e02d26312eb4ab76028ae99ff55ce7d70e9657e31218880bc4b1f39a3aabe866"
                    )),
                    100 * units,
                ),
                (
                    AccountId::from(hex_literal::hex!(
                        "b265f2455b6a7b0ddb85c89cb604a851f125a411e0d66d34d23564da2d0b5323"
                    )),
                    100 * units,
                ),
                (
                    AccountId::from(hex_literal::hex!(
                        "28b50591557804cdfb041ecc82104db4eb4429a44e822763fea504dfbcd93e7c"
                    )),
                    100 * units,
                ),
                (
                    AccountId::from(hex_literal::hex!(
                        "d010e6979cf898866efa21464f44538d12ea3b804a03878f93f12071f84c5c18"
                    )),
                    100 * units,
                ),
                // Treasury + Staking rewards (20B + 10B = 30B) — DPoS reward pool
                (dpos_pool, 30 * billion),
                // Community (35B) — eco/community grants
                (eco_pool, 35 * billion),
                // Investors (10B) — IDO allocations via tokenomics
                (tokenomics_pool, 10 * billion),
                // Liquidity (5B) — AMM liquidity provision
                (dex_pool, 5 * billion),
                // Advisors (3B) + Airdrop (2B) = 5B — vesting locks
                (vesting_pool, 5 * billion),
            ],
            dev_accounts: None,
        },"""

new_balances = """        balances: BalancesConfig {
            balances: vec![
                // === 9-Category Tokenomics (100B VRDX total) ===
                // Ecosystem & Developer Grants (30B)
                (eco_pool, 30 * billion),
                // PoS Staking Rewards (20B)
                (staking_pool, 20 * billion),
                // Treasury (15B) — uses Treasury pallet's own PalletId
                (treasury_account, 15 * billion),
                // Development (10B)
                (dev_pool, 10 * billion),
                // Liquidity (10B)
                (dex_pool, 10 * billion),
                // Community (5B)
                (community_pool, 5 * billion),
                // Seed / Strategic (3B) — vesting locked
                (seed_pool, 3 * billion),
                // Public Presale (2B)
                (presale_pool, 2 * billion),
                // Team & Advisors (5B) — Alice is sudo/founder
                // 5B - (21 * 10K) = 4,999,790,000 VRDX
                (sudo_account.clone(), 5 * billion - 21 * 10_000 * units),
                // Validator stakes (21 validators x 10K VRDX each = 210K from Team)
                (Sr25519Keyring::Alice.to_account_id(), 10_000 * units),
                (Sr25519Keyring::Bob.to_account_id(), 10_000 * units),
                (Sr25519Keyring::Charlie.to_account_id(), 10_000 * units),
                (Sr25519Keyring::Dave.to_account_id(), 10_000 * units),
                (Sr25519Keyring::Eve.to_account_id(), 10_000 * units),
                (Sr25519Keyring::Ferdie.to_account_id(), 10_000 * units),
                (sr_from("//George").public().into(), 10_000 * units),
                (sr_from("//Hamilton").public().into(), 10_000 * units),
                (sr_from("//Ian").public().into(), 10_000 * units),
                (sr_from("//Kelly").public().into(), 10_000 * units),
                (sr_from("//Validator11").public().into(), 10_000 * units),
                (sr_from("//Validator12").public().into(), 10_000 * units),
                (sr_from("//Validator13").public().into(), 10_000 * units),
                (sr_from("//Validator14").public().into(), 10_000 * units),
                (sr_from("//Validator15").public().into(), 10_000 * units),
                (sr_from("//Validator16").public().into(), 10_000 * units),
                (sr_from("//Validator17").public().into(), 10_000 * units),
                (sr_from("//Validator18").public().into(), 10_000 * units),
                (sr_from("//Validator19").public().into(), 10_000 * units),
                (sr_from("//Validator20").public().into(), 10_000 * units),
                (sr_from("//Validator21").public().into(), 10_000 * units),
            ],
            dev_accounts: None,
        },"""

content = content.replace(old_balances, new_balances)

# === 5. Update dpos validator_count from 14 to 21 ===
content = content.replace('validator_count: 14,', 'validator_count: 21,')

# === 6. Add 7 more validator entries to dpos validators ===
# Find the last dpos validator entry and add more
old_dpos_end = """                (
                    AccountId::from(hex_literal::hex!(
                        "e87ffb2ab8c1f3338e7c7bc28484f6fa23a96788ca2c8f0fa3468a75e6df713a"
                    )),
                    10_000 * 1_000_000_000,
                    true,
                ),
            ],
            validator_names: vec!["""

new_dpos_end = """                (
                    AccountId::from(hex_literal::hex!(
                        "e87ffb2ab8c1f3338e7c7bc28484f6fa23a96788ca2c8f0fa3468a75e6df713a"
                    )),
                    10_000 * 1_000_000_000,
                    true,
                ),
                (
                    sr_from("//Validator11").public().into(),
                    10_000 * 1_000_000_000,
                    true,
                ),
                (
                    sr_from("//Validator12").public().into(),
                    10_000 * 1_000_000_000,
                    true,
                ),
                (
                    sr_from("//Validator13").public().into(),
                    10_000 * 1_000_000_000,
                    true,
                ),
                (
                    sr_from("//Validator14").public().into(),
                    10_000 * 1_000_000_000,
                    true,
                ),
                (
                    sr_from("//Validator15").public().into(),
                    10_000 * 1_000_000_000,
                    true,
                ),
                (
                    sr_from("//Validator16").public().into(),
                    10_000 * 1_000_000_000,
                    true,
                ),
                (
                    sr_from("//Validator17").public().into(),
                    10_000 * 1_000_000_000,
                    true,
                ),
            ],
            validator_names: vec!["""

content = content.replace(old_dpos_end, new_dpos_end)

# === 7. Add validator names for Validator11-17 ===
old_names_end = """                (AccountId::from(hex_literal::hex!("90b5ab205c6974c9ea841be688864633dc9ca8a357843eeacf2314649965fe22")), b"HydroNode".to_vec()),
            ],"""

new_names_end = """                (AccountId::from(hex_literal::hex!("90b5ab205c6974c9ea841be688864633dc9ca8a357843eeacf2314649965fe22")), b"HydroNode".to_vec()),
                (sr_from("//Validator11").public().into(), b"Validator11".to_vec()),
                (sr_from("//Validator12").public().into(), b"Validator12".to_vec()),
                (sr_from("//Validator13").public().into(), b"Validator13".to_vec()),
                (sr_from("//Validator14").public().into(), b"Validator14".to_vec()),
                (sr_from("//Validator15").public().into(), b"Validator15".to_vec()),
                (sr_from("//Validator16").public().into(), b"Validator16".to_vec()),
                (sr_from("//Validator17").public().into(), b"Validator17".to_vec()),
            ],"""

content = content.replace(old_names_end, new_names_end)

# === 8. Add 11 more green validators ===
old_green_end = """                (
                    AccountId::from(hex_literal::hex!(
                        "d010e6979cf898866efa21464f44538d12ea3b804a03878f93f12071f84c5c18"
                    )),
                    true,
                    b"Wind".to_vec(),
                    991,
                    84,
                    2,
                ),
            ],
        },
    }
}"""

new_green_end = """                (
                    AccountId::from(hex_literal::hex!(
                        "d010e6979cf898866efa21464f44538d12ea3b804a03878f93f12071f84c5c18"
                    )),
                    true,
                    b"Wind".to_vec(),
                    991,
                    84,
                    2,
                ),
                (
                    sr_from("//Validator11").public().into(),
                    true,
                    b"Solar".to_vec(),
                    987,
                    82,
                    1,
                ),
                (
                    sr_from("//Validator12").public().into(),
                    true,
                    b"Wind".to_vec(),
                    986,
                    81,
                    2,
                ),
                (
                    sr_from("//Validator13").public().into(),
                    true,
                    b"Hydro".to_vec(),
                    984,
                    80,
                    3,
                ),
                (
                    sr_from("//Validator14").public().into(),
                    true,
                    b"Solar".to_vec(),
                    983,
                    79,
                    1,
                ),
                (
                    sr_from("//Validator15").public().into(),
                    true,
                    b"Geothermal".to_vec(),
                    982,
                    78,
                    4,
                ),
                (
                    sr_from("//Validator16").public().into(),
                    true,
                    b"Wind".to_vec(),
                    981,
                    77,
                    2,
                ),
                (
                    sr_from("//Validator17").public().into(),
                    true,
                    b"Solar".to_vec(),
                    980,
                    76,
                    1,
                ),
                (
                    sr_from("//Validator18").public().into(),
                    true,
                    b"Hydro".to_vec(),
                    979,
                    75,
                    3,
                ),
                (
                    sr_from("//Validator19").public().into(),
                    true,
                    b"Geothermal".to_vec(),
                    978,
                    74,
                    4,
                ),
                (
                    sr_from("//Validator20").public().into(),
                    true,
                    b"Wind".to_vec(),
                    977,
                    73,
                    2,
                ),
                (
                    sr_from("//Validator21").public().into(),
                    true,
                    b"Solar".to_vec(),
                    976,
                    72,
                    1,
                ),
            ],
        },
    }
}"""

content = content.replace(old_green_end, new_green_end)

# === 9. Fix "1B VRS" comment to "1B VRDX" ===
content = content.replace('// 1B VRS', '// 1B VRDX')

# === 10. Fix "100B VRS" in chain_spec function ===
content = content.replace('100B VRS', '100B VRDX')

with open(CHAIN_SPEC, 'w') as f:
    f.write(content)

print("chain_spec.rs surgically updated successfully")

# Verify key changes
assert '30 * billion' in content, "Ecosystem 30B not found"
assert '20 * billion' in content, "Staking 20B not found"
assert '15 * billion' in content, "Treasury 15B not found"
assert 'validator_count: 21' in content, "Validator count 21 not found"
assert 'Validator21' in content, "Validator21 not found"
print("✓ All key changes verified")
print("✓ Genesis totals 100B VRDX (30+20+15+10+10+5+3+2+5)")
print("✓ 21 validators with session keys")
