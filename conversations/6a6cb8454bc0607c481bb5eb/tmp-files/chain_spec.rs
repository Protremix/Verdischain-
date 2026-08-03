//! Verdis Chain — Chain Specification (Substrate v48)

use sp_consensus_babe::AuthorityId as BabeId;
use sp_consensus_grandpa::AuthorityId as GrandpaId;
use sp_core::crypto::{Ss58Codec, Public};
use sp_runtime::BuildStorage;
use verdis_runtime::{AccountId, Signature, VERDIS_RUNTIME_VERSION};

pub type VerdisChainSpec = sc_service::GenericChainSpec<verdis_runtime::GenesisConfig>;

impl VerdisChainSpec {
    pub fn chain_spec() -> Self {
        Self::from_genesis(
            "Verdis",
            "verdis",
            ChainType::Development,
            genesis_config,
            vec![],
            None,
            None,
            None,
            Default::default(),
        )
    }
}

use sc_chain_spec::ChainType;

fn genesis_config() -> verdis_runtime::GenesisConfig {
    use verdis_runtime::{
        BalancesConfig, SudoConfig, BabeConfig, GrandpaConfig, SessionConfig,
        VerdisEcoConfig, AMMConfig,
    };

    // Developer keys
    let sudo_account: AccountId =
        sp_keyring::Sr25519Keyring::Alice.to_account_id();

    // Initial validators (Alice, Bob, Charlie)
    let babe_authorities: Vec<(BabeId, u64)> = vec![
        (
            sp_keyring::Sr25519Keyring::Alice.public().into(),
            1,
        ),
        (
            sp_keyring::Sr25519Keyring::Bob.public().into(),
            1,
        ),
        (
            sp_keyring::Sr25519Keyring::Charlie.public().into(),
            1,
        ),
    ];

    let grandpa_authorities: Vec<(GrandpaId, u64)> = vec![
        (
            sp_keyring::Ed25519Keyring::Alice.public().into(),
            1,
        ),
        (
            sp_keyring::Ed25519Keyring::Bob.public().into(),
            1,
        ),
        (
            sp_keyring::Ed25519Keyring::Charlie.public().into(),
            1,
        ),
    ];

    let session_keys: Vec<(AccountId, AccountId, verdis_runtime::SessionKeys)> =
        vec![
            (
                sp_keyring::Sr25519Keyring::Alice.to_account_id(),
                sp_keyring::Sr25519Keyring::Alice.to_account_id(),
                verdis_runtime::SessionKeys {
                    babe: sp_keyring::Sr25519Keyring::Alice.public().into(),
                    grandpa: sp_keyring::Ed25519Keyring::Alice.public().into(),
                },
            ),
            (
                sp_keyring::Sr25519Keyring::Bob.to_account_id(),
                sp_keyring::Sr25519Keyring::Bob.to_account_id(),
                verdis_runtime::SessionKeys {
                    babe: sp_keyring::Sr25519Keyring::Bob.public().into(),
                    grandpa: sp_keyring::Ed25519Keyring::Bob.public().into(),
                },
            ),
            (
                sp_keyring::Sr25519Keyring::Charlie.to_account_id(),
                sp_keyring::Sr25519Keyring::Charlie.to_account_id(),
                verdis_runtime::SessionKeys {
                    babe: sp_keyring::Sr25519Keyring::Charlie.public().into(),
                    grandpa: sp_keyring::Ed25519Keyring::Charlie.public().into(),
                },
            ),
        ];

    verdis_runtime::GenesisConfig {
        balances: BalancesConfig {
            balances: vec![
                (sudo_account.clone(), 100_000_000_000_000_000u128),
                (
                    sp_keyring::Sr25519Keyring::Bob.to_account_id(),
                    50_000_000_000_000_000u128,
                ),
                (
                    sp_keyring::Sr25519Keyring::Charlie.to_account_id(),
                    50_000_000_000_000_000u128,
                ),
            ],
        },
        sudo: SudoConfig {
            key: sudo_account,
        },
        babe: BabeConfig {
            authorities: babe_authorities,
            epoch_config: verdis_runtime::BABE_EPOCH_CONFIG.clone(),
        },
        grandpa: GrandpaConfig {
            authorities: grandpa_authorities,
        },
        session: SessionConfig {
            keys: session_keys,
        },
        system: Default::default(),
        transaction_payment: Default::default(),
        verdis_eco: VerdisEcoConfig {
            carbon_credits: Vec::new(),
            reforestation_projects: Vec::new(),
        },
        amm: AMMConfig {
            pools: Vec::new(),
        },
    }
}

/// Development keys for testing
pub fn dev_keys() -> Vec<(String, String)> {
    vec![
        ("Alice".to_string(), "//Alice".to_string()),
        ("Bob".to_string(), "//Bob".to_string()),
        ("Charlie".to_string(), "//Charlie".to_string()),
    ]
}
