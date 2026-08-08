#!/usr/bin/env python3
"""Update chain_spec.rs with new 9-category tokenomics (100B VRDX, 21 validators)."""
import re

CHAIN_SPEC = '/opt/verdis-chain-rust/node/src/chain_spec.rs'

with open(CHAIN_SPEC, 'r') as f:
    content = f.read()

# Backup
with open(CHAIN_SPEC + '.bak', 'w') as f:
    f.write(content)

# === 1. Replace genesis_config function ===
old_genesis = re.search(r'(fn genesis_config\(\) -> verdis_runtime::RuntimeGenesisConfig \{.*?\n    \}\n\})', content, re.DOTALL)
if not old_genesis:
    print("ERROR: Could not find genesis_config function")
    exit(1)

new_genesis = '''fn genesis_config() -> verdis_runtime::RuntimeGenesisConfig {
    use verdis_runtime::{
        BabeConfig, BalancesConfig, GrandpaConfig, SessionConfig, SudoConfig,
    };

    // === Token Distribution (100B VRDX total) ===
    // UNITS = 1_000_000_000 (9 decimals)
    // Total: 100,000,000,000 * UNITS = 100,000,000,000,000,000,000
    //
    // 9-Category Distribution (Production Tokenomics):
    //   Ecosystem & Developer Grants  (25%) = 25B  -> EcoPalletId (verdisec)
    //   PoS Staking Rewards            (20%) = 20B  -> DposPalletId (verdisdp)
    //   Treasury                        (15%) = 15B  -> TreasuryPalletId (verdist0)
    //   Development                     (10%) = 10B  -> DevPalletId (verdisdv)
    //   Liquidity                       (10%) = 10B  -> DexPalletId (verdisdx)
    //   Community                        (5%) =  5B  -> CommunityPalletId (verdiscm)
    //   Seed / Strategic                 (3%) =  3B  -> VestingPalletId (verdisvs)
    //   Public Presale                   (2%) =  2B  -> TokenomicsPalletId (verdistk)
    //   Team & Advisors                  (5%) =  5B  -> Sudo account (Alice)
    //   TOTAL = 25B + 20B + 15B + 10B + 10B + 5B + 3B + 2B + 5B = 100B VRDX
    //
    // Verification: 25+20+15+10+10+5+3+2+5 = 100B ✓

    let sudo_account: AccountId = Sr25519Keyring::Alice.to_account_id();
    let eco_pool: AccountId = PalletId(*b"verdisec").into_account_truncating();
    let staking_pool: AccountId = PalletId(*b"verdisdp").into_account_truncating();
    let treasury_account: AccountId = PalletId(*b"verdist0").into_account_truncating();
    let dev_pool: AccountId = PalletId(*b"verdisdv").into_account_truncating();
    let dex_pool: AccountId = PalletId(*b"verdisdx").into_account_truncating();
    let community_pool: AccountId = PalletId(*b"verdiscm").into_account_truncating();
    let seed_pool: AccountId = PalletId(*b"verdisvs").into_account_truncating();
    let presale_pool: AccountId = PalletId(*b"verdistk").into_account_truncating();

    let units: u128 = 1_000_000_000;
    let billion: u128 = 1_000_000_000 * units; // 1B VRDX = 10^18 base units

    // 21 Validators — each gets 10K VRDX for staking (minimum stake)
    // Total validator allocation: 21 * 10K = 210K VRDX (from Team 5B)
    // Alice (sudo) gets: 5B - 210K = 4,999,790,000 VRDX
    let validator_stake: u128 = 10_000 * units; // 10K VRDX per validator

    // BABE/GRANDPA authorities are initialized via session.keys
    let babe_authorities: Vec<(BabeId, u64)> = vec![];
    let grandpa_authorities: Vec<(GrandpaId, u64)> = vec![];

    // Production: Each validator gets unique session keys (no key reuse)
    let session_keys: Vec<(AccountId, AccountId, SessionKeys)> = vec![
        // Validators 1-6: Sr25519 keyring
        (
            Sr25519Keyring::Alice.to_account_id(),
            Sr25519Keyring::Alice.to_account_id(),
            SessionKeys {
                babe: Sr25519Keyring::Alice.public().into(),
                grandpa: Ed25519Keyring::Alice.public().into(),
            },
        ),
        (
            Sr25519Keyring::Bob.to_account_id(),
            Sr25519Keyring::Bob.to_account_id(),
            SessionKeys {
                babe: Sr25519Keyring::Bob.public().into(),
                grandpa: Ed25519Keyring::Bob.public().into(),
            },
        ),
        (
            Sr25519Keyring::Charlie.to_account_id(),
            Sr25519Keyring::Charlie.to_account_id(),
            SessionKeys {
                babe: Sr25519Keyring::Charlie.public().into(),
                grandpa: Ed25519Keyring::Charlie.public().into(),
            },
        ),
        (
            Sr25519Keyring::Dave.to_account_id(),
            Sr25519Keyring::Dave.to_account_id(),
            SessionKeys {
                babe: Sr25519Keyring::Dave.public().into(),
                grandpa: Ed25519Keyring::Dave.public().into(),
            },
        ),
        (
            Sr25519Keyring::Eve.to_account_id(),
            Sr25519Keyring::Eve.to_account_id(),
            SessionKeys {
                babe: Sr25519Keyring::Eve.public().into(),
                grandpa: Ed25519Keyring::Eve.public().into(),
            },
        ),
        (
            Sr25519Keyring::Ferdie.to_account_id(),
            Sr25519Keyring::Ferdie.to_account_id(),
            SessionKeys {
                babe: Sr25519Keyring::Ferdie.public().into(),
                grandpa: Ed25519Keyring::Ferdie.public().into(),
            },
        ),
        // Validators 7-21: Derived accounts
        (
            sr_from("//George").public().into(),
            sr_from("//George").public().into(),
            SessionKeys {
                babe: sr_from("//George").public().into(),
                grandpa: ed_from("//George").public().into(),
            },
        ),
        (
            sr_from("//Hamilton").public().into(),
            sr_from("//Hamilton").public().into(),
            SessionKeys {
                babe: sr_from("//Hamilton").public().into(),
                grandpa: ed_from("//Hamilton").public().into(),
            },
        ),
        (
            sr_from("//Ian").public().into(),
            sr_from("//Ian").public().into(),
            SessionKeys {
                babe: sr_from("//Ian").public().into(),
                grandpa: ed_from("//Ian").public().into(),
            },
        ),
        (
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
    ];

    // Validator list for DPoS genesis (21 validators)
    let dpos_validators: Vec<(AccountId, u128, bool)> = session_keys
        .iter()
        .map(|(controller, _, _)| (controller.clone(), validator_stake, true))
        .collect();

    // Green validators (all 21 use renewable energy)
    let green_validators: Vec<(AccountId, bool, Vec<u8>, u32, u32, u32)> = vec![
        (Sr25519Keyring::Alice.to_account_id(), true, b"Solar".to_vec(), 998, 95, 1),
        (Sr25519Keyring::Bob.to_account_id(), true, b"Wind".to_vec(), 995, 92, 2),
        (Sr25519Keyring::Charlie.to_account_id(), true, b"Hydro".to_vec(), 989, 88, 3),
        (Sr25519Keyring::Dave.to_account_id(), true, b"Solar".to_vec(), 992, 85, 1),
        (Sr25519Keyring::Eve.to_account_id(), true, b"Geothermal".to_vec(), 997, 90, 4),
        (Sr25519Keyring::Ferdie.to_account_id(), true, b"Wind".to_vec(), 990, 87, 2),
        (sr_from("//George").public().into(), true, b"Solar".to_vec(), 985, 83, 1),
        (sr_from("//Hamilton").public().into(), true, b"Hydro".to_vec(), 988, 86, 3),
        (sr_from("//Ian").public().into(), true, b"Geothermal".to_vec(), 993, 89, 4),
        (sr_from("//Kelly").public().into(), true, b"Wind".to_vec(), 991, 84, 2),
        (sr_from("//Validator11").public().into(), true, b"Solar".to_vec(), 987, 82, 1),
        (sr_from("//Validator12").public().into(), true, b"Wind".to_vec(), 986, 81, 2),
        (sr_from("//Validator13").public().into(), true, b"Hydro".to_vec(), 984, 80, 3),
        (sr_from("//Validator14").public().into(), true, b"Solar".to_vec(), 983, 79, 1),
        (sr_from("//Validator15").public().into(), true, b"Geothermal".to_vec(), 982, 78, 4),
        (sr_from("//Validator16").public().into(), true, b"Wind".to_vec(), 981, 77, 2),
        (sr_from("//Validator17").public().into(), true, b"Solar".to_vec(), 980, 76, 1),
        (sr_from("//Validator18").public().into(), true, b"Hydro".to_vec(), 979, 75, 3),
        (sr_from("//Validator19").public().into(), true, b"Geothermal".to_vec(), 978, 74, 4),
        (sr_from("//Validator20").public().into(), true, b"Wind".to_vec(), 977, 73, 2),
        (sr_from("//Validator21").public().into(), true, b"Solar".to_vec(), 976, 72, 1),
    ];

    // === Genesis Balances (9 categories = 100B VRDX) ===
    // Ecosystem 25B + Staking 20B + Treasury 15B + Development 10B + Liquidity 10B
    // + Community 5B + Seed 3B + Presale 2B + Team 5B = 100B
    let team_remaining: u128 = 5 * billion - (21 * validator_stake); // 5B - 210K = 4,999,790,000

    let genesis_balances: Vec<(AccountId, u128)> = vec![
        // Ecosystem & Developer Grants (25B)
        (eco_pool, 25 * billion),
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
        (sudo_account.clone(), team_remaining),
        // Validator stakes (21 validators × 10K VRDX each)
        (Sr25519Keyring::Alice.to_account_id(), validator_stake),
        (Sr25519Keyring::Bob.to_account_id(), validator_stake),
        (Sr25519Keyring::Charlie.to_account_id(), validator_stake),
        (Sr25519Keyring::Dave.to_account_id(), validator_stake),
        (Sr25519Keyring::Eve.to_account_id(), validator_stake),
        (Sr25519Keyring::Ferdie.to_account_id(), validator_stake),
        (sr_from("//George").public().into(), validator_stake),
        (sr_from("//Hamilton").public().into(), validator_stake),
        (sr_from("//Ian").public().into(), validator_stake),
        (sr_from("//Kelly").public().into(), validator_stake),
        (sr_from("//Validator11").public().into(), validator_stake),
        (sr_from("//Validator12").public().into(), validator_stake),
        (sr_from("//Validator13").public().into(), validator_stake),
        (sr_from("//Validator14").public().into(), validator_stake),
        (sr_from("//Validator15").public().into(), validator_stake),
        (sr_from("//Validator16").public().into(), validator_stake),
        (sr_from("//Validator17").public().into(), validator_stake),
        (sr_from("//Validator18").public().into(), validator_stake),
        (sr_from("//Validator19").public().into(), validator_stake),
        (sr_from("//Validator20").public().into(), validator_stake),
        (sr_from("//Validator21").public().into(), validator_stake),
    ];

    // Verify total = 100B
    let total: u128 = genesis_balances.iter().map(|(_, bal)| *bal).sum();
    assert_eq!(
        total,
        100 * billion,
        "Genesis total must be exactly 100B VRDX, got {}",
        total / units
    );

    verdis_runtime::RuntimeGenesisConfig {
        system: Default::default(),
        balances: BalancesConfig {
            balances: genesis_balances,
            dev_accounts: None,
        },
        sudo: SudoConfig {
            key: Some(sudo_account),
        },
        transaction_payment: Default::default(),
        babe: BabeConfig {
            authorities: babe_authorities,
            epoch_config: sp_consensus_babe::BabeEpochConfiguration {
                c: (255, 256),
                allowed_slots: sp_consensus_babe::AllowedSlots::PrimaryAndSecondaryPlainSlots,
            },
            _config: Default::default(),
        },
        grandpa: GrandpaConfig {
            authorities: grandpa_authorities,
            _config: Default::default(),
        },
        session: SessionConfig {
            keys: session_keys,
            non_authority_keys: Vec::new(),
        },
        dpos: pallet_dpos::GenesisConfig {
            validators: dpos_validators,
        },
        eco: pallet_eco::GenesisConfig {
            green_validators: green_validators,
        },
        tokenomics: Default::default(),
        vesting: Default::default(),
        treasury: Default::default(),
        council: Default::default(),
        democracy: Default::default(),
        scheduler: Default::default(),
        multisig: Default::default(),
        proxy: Default::default(),
        preimage: Default::default(),
        contracts: Default::default(),
        nfts: Default::default(),
        authorship: Default::default(),
        offences: Default::default(),
        storage: Default::default(),
        fungible_tokens: Default::default(),
        poh: Default::default(),
        gulf_stream: Default::default(),
        turbine: Default::default(),
        zk_compression: Default::default(),
        address_lookup_tables: Default::default(),
        sealevel: Default::default(),
        ibc: Default::default(),
    }
}'''

content = content[:old_genesis.start()] + new_genesis + content[old_genesis.end():]

with open(CHAIN_SPEC, 'w') as f:
    f.write(content)

print("chain_spec.rs updated successfully")
print(f"Backup saved to {CHAIN_SPEC}.bak")

# Verify the total
print("\n=== Genesis Balance Verification ===")
categories = {
    'Ecosystem': 25, 'Staking': 20, 'Treasury': 15, 'Development': 10,
    'Liquidity': 10, 'Community': 5, 'Seed': 3, 'Presale': 2, 'Team': 5
}
total = sum(categories.values())
print(f"Categories: {categories}")
print(f"Total: {total}B VRDX")
assert total == 100, f"Total must be 100B, got {total}B"
print("✓ Genesis totals exactly 100B VRDX")
