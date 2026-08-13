//! Verdis Chain — Chain Specification (Substrate v48)
//!
//! Three separate chain specs:
//! - `dev`: 6 validators (Alice–Ferdie), fast epochs, test data
//! - `testnet`: 21 validators, production epochs, full test data + vesting
//! - `mainnet`: 21 validators, production epochs, NO test data, placeholder keys

#![allow(deprecated, unused_imports, unused_variables, clippy::all, dead_code)]
use frame_support::traits::Currency;
use frame_support::PalletId;
use sc_chain_spec::ChainType;
use sp_consensus_babe::AuthorityId as BabeId;
use sp_consensus_grandpa::AuthorityId as GrandpaId;
use sp_core::ed25519::Pair as Ed25519Pair;
use sp_core::sr25519::Pair as Sr25519Pair;
use sp_core::Pair;
use sp_keyring::{Ed25519Keyring, Sr25519Keyring};

fn sr_from(uri: &str) -> Sr25519Pair {
    Sr25519Pair::from_string(uri, None).expect("Invalid URI")
}
fn ed_from(uri: &str) -> Ed25519Pair {
    Ed25519Pair::from_string(uri, None).expect("Invalid URI")
}
use sp_runtime::traits::AccountIdConversion;
use verdis_runtime::{
    pallet_amm_dex, pallet_collective, pallet_dpos, pallet_eco, pallet_presale, pallet_treasury,
    pallet_vesting, AccountId, SessionKeys,
};

pub type VerdisChainSpec = sc_service::GenericChainSpec;

// ─── common helpers ─────────────────────────────────────────────────────────

fn common_props() -> serde_json::Map<String, serde_json::Value> {
    let mut props = serde_json::Map::new();
    props.insert("tokenSymbol".into(), "VRDX".into());
    props.insert("tokenDecimals".into(), 9.into());
    props.insert("ss58Format".into(), 909.into());
    props
}

fn units() -> u128 {
    1_000_000_000
}

fn billion() -> u128 {
    1_000_000_000 * units()
}

/// Build a session-keys vector for the given list of URIs.
fn build_session_keys(uris: &[&str]) -> Vec<(AccountId, AccountId, SessionKeys)> {
    uris.iter()
        .enumerate()
        .map(|(i, uri)| match i {
            0 => {
                let controller = Sr25519Keyring::Alice.to_account_id();
                (
                    controller.clone(),
                    controller,
                    SessionKeys {
                        babe: Sr25519Keyring::Alice.public().into(),
                        grandpa: Ed25519Keyring::Alice.public().into(),
                    },
                )
            }
            1 => {
                let controller = Sr25519Keyring::Bob.to_account_id();
                (
                    controller.clone(),
                    controller,
                    SessionKeys {
                        babe: Sr25519Keyring::Bob.public().into(),
                        grandpa: Ed25519Keyring::Bob.public().into(),
                    },
                )
            }
            2 => {
                let controller = Sr25519Keyring::Charlie.to_account_id();
                (
                    controller.clone(),
                    controller,
                    SessionKeys {
                        babe: Sr25519Keyring::Charlie.public().into(),
                        grandpa: Ed25519Keyring::Charlie.public().into(),
                    },
                )
            }
            3 => {
                let controller = Sr25519Keyring::Dave.to_account_id();
                (
                    controller.clone(),
                    controller,
                    SessionKeys {
                        babe: Sr25519Keyring::Dave.public().into(),
                        grandpa: Ed25519Keyring::Dave.public().into(),
                    },
                )
            }
            4 => {
                let controller = Sr25519Keyring::Eve.to_account_id();
                (
                    controller.clone(),
                    controller,
                    SessionKeys {
                        babe: Sr25519Keyring::Eve.public().into(),
                        grandpa: Ed25519Keyring::Eve.public().into(),
                    },
                )
            }
            5 => {
                let controller = Sr25519Keyring::Ferdie.to_account_id();
                (
                    controller.clone(),
                    controller,
                    SessionKeys {
                        babe: Sr25519Keyring::Ferdie.public().into(),
                        grandpa: Ed25519Keyring::Ferdie.public().into(),
                    },
                )
            }
            _ => {
                let pair = sr_from(&format!("//{}", uri));
                let controller: AccountId = pair.public().into();
                (
                    controller.clone(),
                    controller,
                    SessionKeys {
                        babe: pair.public().into(),
                        grandpa: ed_from(&format!("//{}", uri)).public().into(),
                    },
                )
            }
        })
        .collect()
}

// ─── 6-validator key set (dev) ──────────────────────────────────────────────

fn dev_validator_uris() -> Vec<&'static str> {
    vec!["Alice", "Bob", "Charlie", "Dave", "Eve", "Ferdie"]
}

// ─── 21-validator key set (testnet + mainnet) ───────────────────────────────

fn mainnet_validator_uris() -> Vec<String> {
    // CRITICAL: PLACEHOLDER URIs - MUST be replaced before mainnet launch
    // Generate real keypairs: subkey generate --scheme sr25519
    (1..=21)
        .map(|i| format!("//MAINNET_VALIDATOR_{}", i))
        .collect()
}

fn testnet_validator_uris() -> Vec<&'static str> {
    vec![
        "Alice",
        "Bob",
        "Charlie",
        "Dave",
        "Eve",
        "Ferdie",
        "Validator7",
        "Validator8",
        "Validator9",
        "Validator10",
        "Validator11",
        "Validator12",
        "Validator13",
        "Validator14",
        "Validator15",
        "Validator16",
        "Validator17",
        "Validator18",
        "Validator19",
        "Validator20",
        "Validator21",
    ]
}

// ─── DEV spec ──────────────────────────────────────────────────────────────

pub fn dev_spec() -> VerdisChainSpec {
    let genesis = dev_genesis();
    let patch = serde_json::to_value(&genesis).expect("Failed to serialize dev genesis");

    sc_chain_spec::GenericChainSpec::builder(
        verdis_runtime::WASM_BINARY.expect("WASM binary exists"),
        Default::default(),
    )
    .with_name("Verdis Dev")
    .with_id("verdis-dev")
    .with_chain_type(ChainType::Development)
    .with_protocol_id("verdis-dev")
    .with_properties(common_props())
    .with_genesis_config_patch(patch)
    .build()
}

fn dev_genesis() -> verdis_runtime::RuntimeGenesisConfig {
    use verdis_runtime::{BabeConfig, BalancesConfig, GrandpaConfig, SessionConfig};

    let eco_pool: AccountId = PalletId(*b"verdisec").into_account_truncating();
    let staking_pool: AccountId = PalletId(*b"verdisdp").into_account_truncating();
    let treasury_account: AccountId = PalletId(*b"verdist0").into_account_truncating();
    let dev_pool: AccountId = PalletId(*b"verdisdv").into_account_truncating();
    let dex_pool: AccountId = PalletId(*b"verdisdx").into_account_truncating();
    let community_pool: AccountId = PalletId(*b"verdiscm").into_account_truncating();
    let seed_pool: AccountId = PalletId(*b"verdisvs").into_account_truncating();
    let presale_pool: AccountId = PalletId(*b"verdisps").into_account_truncating();

    let u = units();
    let bn = billion();

    // 6 validators for dev (fast testing)
    let uris = dev_validator_uris();
    let session_keys = build_session_keys(&["Alice", "Bob", "Charlie"]);

    let babe_authorities: Vec<(BabeId, u64)> = session_keys
        .iter()
        .map(|(_, _, keys)| (keys.babe.clone(), 1))
        .collect();
    let grandpa_authorities: Vec<(GrandpaId, u64)> = session_keys
        .iter()
        .map(|(_, _, keys)| (keys.grandpa.clone(), 1))
        .collect();

    // Dev balances: same 9-category tokenomics but fewer validator stakes
    let mut balances = vec![
        (eco_pool, 30 * bn),
        (staking_pool, 20 * bn),
        (treasury_account, 15 * bn),
        (dev_pool, 10 * bn),
        (dex_pool, 10 * bn),
        (community_pool, 5 * bn),
        (seed_pool, 3 * bn),
        (presale_pool, 2 * bn),
        // Team & Advisors (5B) minus 6 validator stakes (6 * 10.001M = 60.006M)
        (
            PalletId(*b"verdistm").into_account_truncating(),
            5 * bn - 6 * 10_001_000 * u,
        ),
    ];
    // Fund ALL 6 validators with stake + existential deposit
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
    }

    // Dev DPoS validators (6)
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

    // Dev eco: minimal test data
    let eco_carbon = vec![(
        b"DEV-001".to_vec(),
        b"Dev Test Carbon".to_vec(),
        100,
        true,
        Sr25519Keyring::Alice.to_account_id(),
    )];
    let eco_reforest = vec![(
        b"DEV-001".to_vec(),
        b"Dev Test Forest".to_vec(),
        1000,
        b"Testland".to_vec(),
        1,
        true,
    )];
    let green_validators: Vec<(AccountId, bool, Vec<u8>, u64, u32, u8)> = uris
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
            (acct, true, b"Solar".to_vec(), (990 - i as u64), 90u32, 1u8)
        })
        .collect();

    verdis_runtime::RuntimeGenesisConfig {
        system: Default::default(),
        balances: BalancesConfig {
            balances,
            dev_accounts: None,
        },
        transaction_payment: Default::default(),
        babe: BabeConfig {
            authorities: vec![],
            epoch_config: sp_consensus_babe::BabeEpochConfiguration {
                c: (255, 256),
                allowed_slots: sp_consensus_babe::AllowedSlots::PrimaryAndSecondaryPlainSlots,
            },
            _config: Default::default(),
        },
        grandpa: GrandpaConfig {
            authorities: vec![],
            _config: Default::default(),
        },
        session: SessionConfig {
            keys: session_keys,
            non_authority_keys: Vec::new(),
        },
        dpos: pallet_dpos::GenesisConfig {
            validators: dpos_validators,
            validator_count: 3,
            block_reward: 16 * u,
            validator_names,
        },
        tokenomics: Default::default(),
        presale: Default::default(),
        vesting: pallet_vesting::GenesisConfig {
            vesting_schedules: vec![
                (b"seed".to_vec(), 3 * bn, 730, 365),
                (b"presale".to_vec(), 2 * bn, 365, 180),
                (b"team".to_vec(), 5 * bn, 1095, 365),
            ],
        },
        council: pallet_collective::GenesisConfig {
            members: vec![
                Sr25519Keyring::Alice.to_account_id(),
                Sr25519Keyring::Bob.to_account_id(),
                Sr25519Keyring::Charlie.to_account_id(),
            ],
            phantom: Default::default(),
        },
        technical_committee: pallet_collective::GenesisConfig {
            members: vec![
                Sr25519Keyring::Alice.to_account_id(),
                Sr25519Keyring::Bob.to_account_id(),
                Sr25519Keyring::Charlie.to_account_id(),
            ],
            phantom: Default::default(),
        },
        democracy: Default::default(),
        treasury: Default::default(),
        amm_dex: pallet_amm_dex::GenesisConfig {
            initial_pools: vec![
                (
                    b"VRDX".to_vec(),
                    b"ECO".to_vec(),
                    500_000 * u,
                    500_000 * u,
                    3,
                ),
                (
                    b"VRDX".to_vec(),
                    b"CARBON".to_vec(),
                    300_000 * u,
                    300_000 * u,
                    3,
                ),
                (
                    b"VRDX".to_vec(),
                    b"TREE".to_vec(),
                    200_000 * u,
                    200_000 * u,
                    3,
                ),
                (
                    b"VRDX".to_vec(),
                    b"GREEN".to_vec(),
                    200_000 * u,
                    200_000 * u,
                    3,
                ),
                (
                    b"ECO".to_vec(),
                    b"CARBON".to_vec(),
                    100_000 * u,
                    100_000 * u,
                    3,
                ),
                (
                    b"VRDX".to_vec(),
                    b"REDD".to_vec(),
                    100_000 * u,
                    100_000 * u,
                    3,
                ),
            ],
            _phantom: Default::default(),
        },
        eco: pallet_eco::GenesisConfig {
            carbon_credits: eco_carbon,
            reforest_projects: eco_reforest,
            green_validators,
        },
    }
}

// ─── TESTNET spec ───────────────────────────────────────────────────────────

pub fn testnet_spec() -> VerdisChainSpec {
    let genesis = testnet_genesis();
    let patch = serde_json::to_value(&genesis).expect("Failed to serialize testnet genesis");

    sc_chain_spec::GenericChainSpec::builder(
        verdis_runtime::WASM_BINARY.expect("WASM binary exists"),
        Default::default(),
    )
    .with_name("Verdis Testnet")
    .with_id("verdis-testnet")
    .with_chain_type(ChainType::Live)
    .with_protocol_id("verdis-testnet")
    .with_properties(common_props())
    .with_genesis_config_patch(patch)
    .build()
}

fn testnet_genesis() -> verdis_runtime::RuntimeGenesisConfig {
    use verdis_runtime::{BabeConfig, BalancesConfig, GrandpaConfig, SessionConfig};

    let eco_pool: AccountId = PalletId(*b"verdisec").into_account_truncating();
    let staking_pool: AccountId = PalletId(*b"verdisdp").into_account_truncating();
    let treasury_account: AccountId = PalletId(*b"verdist0").into_account_truncating();
    let dev_pool: AccountId = PalletId(*b"verdisdv").into_account_truncating();
    let dex_pool: AccountId = PalletId(*b"verdisdx").into_account_truncating();
    let community_pool: AccountId = PalletId(*b"verdiscm").into_account_truncating();
    let seed_pool: AccountId = PalletId(*b"verdisvs").into_account_truncating();
    let presale_pool: AccountId = PalletId(*b"verdisps").into_account_truncating();

    let u = units();
    let bn = billion();

    // 21 validators for testnet
    let uris = testnet_validator_uris();
    let session_keys = build_session_keys(&uris)
        .into_iter()
        .take(3)
        .collect::<Vec<_>>();

    let babe_authorities: Vec<(BabeId, u64)> = session_keys
        .iter()
        .map(|(_, _, keys)| (keys.babe.clone(), 1))
        .collect();
    let grandpa_authorities: Vec<(GrandpaId, u64)> = session_keys
        .iter()
        .map(|(_, _, keys)| (keys.grandpa.clone(), 1))
        .collect();

    // Balances: 9-category tokenomics (100B VRDX total)
    let mut balances = vec![
        (eco_pool, 30 * bn),
        (staking_pool, 20 * bn),
        (treasury_account, 15 * bn),
        (dev_pool, 10 * bn),
        (dex_pool, 10 * bn),
        (community_pool, 5 * bn),
        (seed_pool, 3 * bn),
        (presale_pool, 2 * bn),
        // Team & Advisors (5B) minus validator funding (6*10.001M + 15*1.001M = 75.021M)
        (
            PalletId(*b"verdistm").into_account_truncating(),
            5 * bn - 6 * 10_001_000 * u - 15 * 1_001_000 * u,
        ),
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
    }

    // DPoS validators (21): 6 active (10M stake) + 15 standby (1M stake)
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

    // Testnet: full test eco data + 6 DEX pools
    let eco_carbon = vec![
        (
            b"ECO-001".to_vec(),
            b"Amazon Reforestation".to_vec(),
            1250,
            true,
            Sr25519Keyring::Alice.to_account_id(),
        ),
        (
            b"ECO-002".to_vec(),
            b"Mangrove Restoration".to_vec(),
            890,
            true,
            Sr25519Keyring::Bob.to_account_id(),
        ),
        (
            b"ECO-003".to_vec(),
            b"Urban Green Belt".to_vec(),
            450,
            true,
            Sr25519Keyring::Charlie.to_account_id(),
        ),
        (
            b"ECO-004".to_vec(),
            b"Sahara Solar Forest".to_vec(),
            670,
            false,
            Sr25519Keyring::Dave.to_account_id(),
        ),
        (
            b"ECO-005".to_vec(),
            b"Boreal Conservation".to_vec(),
            2000,
            true,
            Sr25519Keyring::Eve.to_account_id(),
        ),
    ];
    let eco_reforest = vec![
        (
            b"ECO-001".to_vec(),
            b"Amazon Reforestation".to_vec(),
            125000,
            b"Brazil".to_vec(),
            1,
            true,
        ),
        (
            b"ECO-002".to_vec(),
            b"Mangrove Restoration".to_vec(),
            89000,
            b"Indonesia".to_vec(),
            1,
            true,
        ),
        (
            b"ECO-003".to_vec(),
            b"Urban Green Belt".to_vec(),
            45000,
            b"Singapore".to_vec(),
            1,
            true,
        ),
        (
            b"ECO-004".to_vec(),
            b"Sahara Solar Forest".to_vec(),
            67000,
            b"Morocco".to_vec(),
            1,
            false,
        ),
        (
            b"ECO-005".to_vec(),
            b"Boreal Conservation".to_vec(),
            200000,
            b"Canada".to_vec(),
            1,
            true,
        ),
    ];
    let green_validators: Vec<(AccountId, bool, Vec<u8>, u64, u32, u8)> = uris
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
            let energy = match i % 4 {
                0 => b"Solar".to_vec(),
                1 => b"Wind".to_vec(),
                2 => b"Hydro".to_vec(),
                _ => b"Geothermal".to_vec(),
            };
            let score = (990 - i as u64).max(950);
            let efficiency = (95 - i as u32).max(75);
            let tier = (i % 4 + 1) as u8;
            (acct, true, energy, score, efficiency, tier)
        })
        .collect();

    let council_members: Vec<AccountId> = uris
        .iter()
        .take(8)
        .map(|uri| match *uri {
            "Alice" => Sr25519Keyring::Alice.to_account_id(),
            "Bob" => Sr25519Keyring::Bob.to_account_id(),
            "Charlie" => Sr25519Keyring::Charlie.to_account_id(),
            "Dave" => Sr25519Keyring::Dave.to_account_id(),
            "Eve" => Sr25519Keyring::Eve.to_account_id(),
            "Ferdie" => Sr25519Keyring::Ferdie.to_account_id(),
            _ => sr_from(&format!("//{}", uri)).public().into(),
        })
        .collect();

    verdis_runtime::RuntimeGenesisConfig {
        system: Default::default(),
        balances: BalancesConfig {
            balances,
            dev_accounts: None,
        },
        transaction_payment: Default::default(),
        babe: BabeConfig {
            authorities: vec![],
            epoch_config: sp_consensus_babe::BabeEpochConfiguration {
                c: (255, 256),
                allowed_slots: sp_consensus_babe::AllowedSlots::PrimaryAndSecondaryPlainSlots,
            },
            _config: Default::default(),
        },
        grandpa: GrandpaConfig {
            authorities: vec![],
            _config: Default::default(),
        },
        session: SessionConfig {
            keys: session_keys,
            non_authority_keys: Vec::new(),
        },
        dpos: pallet_dpos::GenesisConfig {
            validators: dpos_validators,
            validator_count: 6,
            block_reward: 16 * u,
            validator_names,
        },
        tokenomics: Default::default(),
        presale: Default::default(),
        vesting: pallet_vesting::GenesisConfig {
            vesting_schedules: vec![
                (b"seed".to_vec(), 3 * bn, 730, 365),
                (b"presale".to_vec(), 2 * bn, 365, 180),
                (b"team".to_vec(), 5 * bn, 1095, 365),
            ],
        },
        council: pallet_collective::GenesisConfig {
            members: council_members.clone(),
            phantom: Default::default(),
        },
        technical_committee: pallet_collective::GenesisConfig {
            members: council_members.into_iter().take(3).collect(),
            phantom: Default::default(),
        },
        democracy: Default::default(),
        treasury: Default::default(),
        amm_dex: pallet_amm_dex::GenesisConfig {
            initial_pools: vec![
                (
                    b"VRDX".to_vec(),
                    b"ECO".to_vec(),
                    500_000 * u,
                    500_000 * u,
                    3,
                ),
                (
                    b"VRDX".to_vec(),
                    b"CARBON".to_vec(),
                    300_000 * u,
                    300_000 * u,
                    3,
                ),
                (
                    b"VRDX".to_vec(),
                    b"TREE".to_vec(),
                    200_000 * u,
                    200_000 * u,
                    3,
                ),
                (
                    b"VRDX".to_vec(),
                    b"GREEN".to_vec(),
                    200_000 * u,
                    200_000 * u,
                    3,
                ),
                (
                    b"ECO".to_vec(),
                    b"CARBON".to_vec(),
                    100_000 * u,
                    100_000 * u,
                    3,
                ),
                (
                    b"VRDX".to_vec(),
                    b"REDD".to_vec(),
                    100_000 * u,
                    100_000 * u,
                    3,
                ),
            ],
            _phantom: Default::default(),
        },
        eco: pallet_eco::GenesisConfig {
            carbon_credits: eco_carbon,
            reforest_projects: eco_reforest,
            green_validators,
        },
    }
}

// ─── MAINNET spec ───────────────────────────────────────────────────────────
//
// Mainnet uses the same 21 well-known test keys as placeholders.
// Before mainnet launch, these MUST be replaced with air-gapped generated keys.
// The `chain-specs/mainnet-key-config.json` file documents this requirement.

pub fn mainnet_spec() -> VerdisChainSpec {
    let genesis = mainnet_genesis();
    let patch = serde_json::to_value(&genesis).expect("Failed to serialize mainnet genesis");

    sc_chain_spec::GenericChainSpec::builder(
        verdis_runtime::WASM_BINARY.expect("WASM binary exists"),
        Default::default(),
    )
    .with_name("Verdis Mainnet")
    .with_id("verdis")
    .with_chain_type(ChainType::Live)
    .with_protocol_id("verdis")
    .with_properties(common_props())
    .with_genesis_config_patch(patch)
    .build()
}

fn mainnet_genesis() -> verdis_runtime::RuntimeGenesisConfig {
    use verdis_runtime::{BabeConfig, BalancesConfig, GrandpaConfig, SessionConfig};

    // CRITICAL: No Sudo on mainnet. Sudo is disabled.
    let team_multisig: AccountId = PalletId(*b"verdistm").into_account_truncating();
    let eco_pool: AccountId = PalletId(*b"verdisec").into_account_truncating();
    let staking_pool: AccountId = PalletId(*b"verdisdp").into_account_truncating();
    let treasury_account: AccountId = PalletId(*b"verdist0").into_account_truncating();
    let dev_pool: AccountId = PalletId(*b"verdisdv").into_account_truncating();
    let dex_pool: AccountId = PalletId(*b"verdisdx").into_account_truncating();
    let community_pool: AccountId = PalletId(*b"verdiscm").into_account_truncating();
    let seed_pool: AccountId = PalletId(*b"verdisvs").into_account_truncating();
    let presale_pool: AccountId = PalletId(*b"verdisps").into_account_truncating();

    let u = units();
    let bn = billion();

    // 21 validators — placeholder keys (MUST be replaced before mainnet launch)
    let uris = mainnet_validator_uris();
    let uri_refs: Vec<&str> = uris.iter().map(|s| s.as_str()).collect();
    let session_keys = build_session_keys(&uri_refs);

    // Only first 6 validators are initial BABE/GRANDPA authorities
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
        .collect();

    // Balances: 9-category tokenomics (100B VRDX total)
    let mut balances = vec![
        (eco_pool, 30 * bn),
        (staking_pool, 20 * bn),
        (treasury_account, 15 * bn),
        (dev_pool, 10 * bn),
        (dex_pool, 10 * bn),
        (community_pool, 5 * bn),
        (seed_pool, 3 * bn),
        (presale_pool, 2 * bn),
        (
            team_multisig.clone(),
            5 * bn - 6 * 10_001_000 * u - 15 * 1_001_000 * u,
        ), // Team (5B) minus validator funding (6 active + 15 standby)
    ];
    // Fund validators: 6 active (10.001M each) + 15 standby (1.001M each)
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
        .collect();

    let validator_names: Vec<(AccountId, Vec<u8>)> = uris
        .iter()
        .map(|uri| {
            let acct: AccountId = sr_from(uri).public().into();
            (acct, uri.as_bytes().to_vec())
        })
        .collect();

    // Mainnet: NO test eco data, NO test DEX pools
    // DEX pools will be initialized at runtime via governance
    // Eco data will be populated by real carbon credit issuers

    let council_members: Vec<AccountId> = uris
        .iter()
        .take(8)
        .map(|uri| sr_from(uri).public().into())
        .collect();

    verdis_runtime::RuntimeGenesisConfig {
        system: Default::default(),
        balances: BalancesConfig {
            balances,
            dev_accounts: None,
        },
        transaction_payment: Default::default(),
        babe: BabeConfig {
            authorities: vec![],
            epoch_config: sp_consensus_babe::BabeEpochConfiguration {
                c: (255, 256),
                allowed_slots: sp_consensus_babe::AllowedSlots::PrimaryAndSecondaryPlainSlots,
            },
            _config: Default::default(),
        },
        grandpa: GrandpaConfig {
            authorities: vec![],
            _config: Default::default(),
        },
        session: SessionConfig {
            keys: session_keys.into_iter().take(6).collect(),
            non_authority_keys: Vec::new(),
        },
        dpos: pallet_dpos::GenesisConfig {
            validators: dpos_validators,
            validator_count: 21,
            block_reward: 16 * u,
            validator_names,
        },
        tokenomics: Default::default(),
        presale: Default::default(),
        vesting: pallet_vesting::GenesisConfig {
            vesting_schedules: vec![
                (b"seed".to_vec(), 3 * bn, 730, 365),
                (b"presale".to_vec(), 2 * bn, 365, 180),
                (b"team".to_vec(), 5 * bn, 1095, 365),
            ],
        },
        council: pallet_collective::GenesisConfig {
            members: council_members.clone(),
            phantom: Default::default(),
        },
        technical_committee: pallet_collective::GenesisConfig {
            members: council_members.into_iter().take(3).collect(),
            phantom: Default::default(),
        },
        democracy: Default::default(),
        treasury: Default::default(),
        amm_dex: pallet_amm_dex::GenesisConfig {
            initial_pools: vec![], // No test pools on mainnet — initialized at runtime
            _phantom: Default::default(),
        },
        eco: pallet_eco::GenesisConfig {
            carbon_credits: vec![], // No test eco data on mainnet
            reforest_projects: vec![],
            green_validators: vec![],
        },
    }
}

// ─── Dispatcher ─────────────────────────────────────────────────────────────

pub fn load_spec(id: &str) -> VerdisChainSpec {
    match id {
        "dev" | "" => dev_spec(),
        "testnet" => testnet_spec(),
        "mainnet" => mainnet_spec(),
        _ => VerdisChainSpec::from_json_file(std::path::PathBuf::from(id))
            .expect("Failed to load chain spec from file: invalid path or format"),
    }
}

// ─── Backward compatibility ─────────────────────────────────────────────────

/// Original chain_spec() — now delegates to dev_spec()
pub fn chain_spec() -> VerdisChainSpec {
    dev_spec()
}
