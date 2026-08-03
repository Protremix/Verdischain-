//! Verdis Chain — Chain Specification (Substrate v48)

use sc_chain_spec::ChainType;
use sp_consensus_babe::AuthorityId as BabeId;
use sp_consensus_grandpa::AuthorityId as GrandpaId;
use sp_keyring::{Ed25519Keyring, Sr25519Keyring};
use verdis_runtime::{AccountId, SessionKeys};

pub type VerdisChainSpec =
    sc_service::GenericChainSpec<verdis_runtime::RuntimeGenesisConfig>;

/// Create the development chain spec for Verdis
pub fn chain_spec() -> VerdisChainSpec {
    VerdisChainSpec::from_genesis(
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

fn genesis_config() -> verdis_runtime::RuntimeGenesisConfig {
    use verdis_runtime::{
        BalancesConfig, SudoConfig, BabeConfig, GrandpaConfig, SessionConfig,
    };

    let sudo_account: AccountId = Sr25519Keyring::Alice.to_account_id();

    // BABE authorities
    let babe_authorities: Vec<(BabeId, u64)> = vec![
        (Sr25519Keyring::Alice.public().into(), 1),
        (Sr25519Keyring::Bob.public().into(), 1),
        (Sr25519Keyring::Charlie.public().into(), 1),
    ];

    // GRANDPA authorities
    let grandpa_authorities: Vec<(GrandpaId, u64)> = vec![
        (Ed25519Keyring::Alice.public().into(), 1),
        (Ed25519Keyring::Bob.public().into(), 1),
        (Ed25519Keyring::Charlie.public().into(), 1),
    ];

    // Session keys
    let session_keys: Vec<(AccountId, AccountId, SessionKeys)> = vec![
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
    ];

    verdis_runtime::RuntimeGenesisConfig {
        // Core pallets
        system: Default::default(),
        timestamp: Default::default(),
        balances: BalancesConfig {
            balances: vec![
                (sudo_account.clone(), 100_000_000_000_000_000u128),
                (Sr25519Keyring::Bob.to_account_id(), 50_000_000_000_000_000u128),
                (Sr25519Keyring::Charlie.to_account_id(), 50_000_000_000_000_000u128),
            ],
            dev_accounts: None,
        },
        sudo: SudoConfig {
            key: Some(sudo_account),
        },
        transaction_payment: Default::default(),
        // Consensus
        babe: BabeConfig {
            authorities: babe_authorities,
            epoch_config: sp_consensus_babe::BabeEpochConfiguration {
                c: (1, 4),
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
        // Other pallets with Default
        scheduler: Default::default(),
        preimage: Default::default(),
        contracts: Default::default(),
        // Verdis custom pallets
        dpos: Default::default(),
        amm_dex: Default::default(),
        eco: Default::default(),
        tokenomics: Default::default(),
        vesting: Default::default(),
        storage: Default::default(),
    }
}
