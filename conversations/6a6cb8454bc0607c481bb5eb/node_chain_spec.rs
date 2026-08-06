//! Verdis Chain Specification
//! Genesis config for development and local testnet

use sc_chain_spec::{ChainSpecExtension, ChainSpecGroup, ChainType, Extension, Properties};
use serde::{Deserialize, Serialize};
use sp_consensus_babe::AuthorityId as BabeAuthorityId;
use sp_consensus_grandpa::AuthorityId as GrandpaAuthorityId;
use sp_core::crypto::{Ss58Codec, ByteArray};
use sp_keyring::sr25519::Keyring as Sr25519Keyring;
use sp_runtime::{
    traits::{IdentifyAccount, Verify},
    Perbill,
};
use verdis_runtime::{
    AccountId, Balance, BlockNumber, Signature,
    Runtime, SessionKeys,
    BABE_ENGINE_ID, GRANDPA_ENGINE_ID,
    opaque::SessionKeys as OpaqueSessionKeys,
};

pub type ChainSpec = sc_service::GenericChainSpec<Extensions>;

#[derive(Default, Serialize, Deserialize, ChainSpecExtension, ChainSpecGroup)]
#[serde(deny_unknown_fields)]
pub struct Extensions {
    #[serde(rename = "relay_chain")]
    pub relay_chain: String,
    #[serde(rename = "para_id")]
    pub para_id: u32,
}

impl Extension for Extensions {
    type Default = Self;
}

fn properties() -> Properties {
    let mut props = Properties::new();
    props.insert("tokenSymbol".into(), "VRDX".into());
    props.insert("tokenDecimals".into(), 18.into());
    props.insert("ss58Format".into(), 42.into());
    props
}

fn session_keys(
    babe: BabeAuthorityId,
    grandpa: GrandpaAuthorityId,
) -> OpaqueSessionKeys {
    OpaqueSessionKeys {
        babe,
        grandpa,
    }
}

fn development_config_genesis(
) -> Result<serde_json::Value, String> {
    let genesis_key = Sr25519Keyring::Alice;
    let alice_pub = genesis_key.public();
    let bob_pub = Sr25519Keyring::Bob.public();
    let charlie_pub = Sr25519Keyring::Charlie.public();
    let dave_pub = Sr25519Keyring::Dave.public();
    let eve_pub = Sr25519Keyring::Eve.public();

    // Grandpa keys (Ed25519)
    let alice_grandpa = sp_keyring::ed25519::Keyring::Alice.public();
    let bob_grandpa = sp_keyring::ed25519::Keyring::Bob.public();
    let charlie_grandpa = sp_keyring::ed25519::Keyring::Charlie.public();

    let endowed_accounts: Vec<AccountId> = vec![
        alice_pub.into(),
        bob_pub.into(),
        charlie_pub.into(),
        dave_pub.into(),
        eve_pub.into(),
    ];

    let initial_balance: Balance = 1_000_000_000_000_000_000_000; // 1M VRDX

    let babe_authorities = vec![
        (BabeAuthorityId::from_slice(alice_pub.as_slice()).unwrap(), 1),
        (BabeAuthorityId::from_slice(bob_pub.as_slice()).unwrap(), 1),
        (BabeAuthorityId::from_slice(charlie_pub.as_slice()).unwrap(), 1),
    ];

    let grandpa_authorities = vec![
        (GrandpaAuthorityId::from_slice(alice_grandpa.as_slice()).unwrap(), 1),
        (GrandpaAuthorityId::from_slice(bob_grandpa.as_slice()).unwrap(), 1),
        (GrandpaAuthorityId::from_slice(charlie_grandpa.as_slice()).unwrap(), 1),
    ];

    Ok(serde_json::json!({
        "balances": {
            "balances": endowed_accounts.iter().map(|k| (k.clone(), initial_balance)).collect::<Vec<_>>(),
        },
        "session": {
            "keys": babe_authorities.iter().zip(grandpa_authorities.iter()).map(|((babe, _), (grandpa, _))| {
                let babe_id = babe.clone();
                let grandpa_id = grandpa.clone();
                let session_keys = session_keys(babe_id, grandpa_id);
                let stash = babe_authorities[0].0.clone();
                (stash, session_keys)
            }).collect::<Vec<_>>(),
        },
        "babe": {
            "epochConfig": {
                "c": [1, 4, 3, 4],
                "allowed_slots": "PrimaryAndSecondaryVRFSlots",
            },
            "authorities": babe_authorities,
        },
        "grandpa": {
            "authorities": grandpa_authorities,
        },
        "sudo": {
            "key": alice_pub.to_ss58check(),
        },
        "timestamp": {
            "minimumPeriod": 3000,
        },
        "transactionPayment": {
            "operationalFeeMultiplier": 5,
        },
    }))
}

pub fn development_config() -> Result<ChainSpec, String> {
    Ok(ChainSpec::from_genesis(
        "Verdis Dev",
        "verdis_dev",
        ChainType::Development,
        || development_config_genesis(),
        vec![],
        None,
        None,
        None,
        Some(properties()),
        Extensions {
            relay_chain: "verdis-dev".into(),
            para_id: 0,
        },
    ))
}

pub fn local_testnet_config() -> Result<ChainSpec, String> {
    Ok(ChainSpec::from_genesis(
        "Verdis Local Testnet",
        "verdis_local",
        ChainType::Local,
        || development_config_genesis(),
        vec![
            "/dns4/localhost/tcp/30333/p2p/12D3KooWEyoppNCUx8Yx66oV9fJnqT7E1iikJpKvqZJrJ3qZ3qZ".into(),
        ],
        None,
        None,
        None,
        Some(properties()),
        Extensions {
            relay_chain: "verdis-local".into(),
            para_id: 0,
        },
    ))
}
