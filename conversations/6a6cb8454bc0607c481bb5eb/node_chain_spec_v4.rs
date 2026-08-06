//! Verdis Chain Specification
//! Genesis config for development and local testnet

use sc_chain_spec::{ChainSpecExtension, ChainSpecGroup, ChainType, Properties};
use serde::{Deserialize, Serialize};
use sp_consensus_babe::AuthorityId as BabeAuthorityId;
use sp_consensus_grandpa::AuthorityId as GrandpaAuthorityId;
use sp_core::crypto::{Ss58Codec, ByteArray};
use sp_keyring::sr25519::Keyring as Sr25519Keyring;
use verdis_runtime::{
    AccountId, Balance,
};

pub type ChainSpec = sc_chain_spec::ChainSpec<Extensions>;

#[derive(Default, Clone, Serialize, Deserialize, ChainSpecExtension, ChainSpecGroup)]
#[serde(deny_unknown_fields)]
pub struct Extensions {
    #[serde(rename = "relay_chain")]
    pub relay_chain: String,
    #[serde(rename = "para_id")]
    pub para_id: u32,
}

fn properties() -> Properties {
    let mut props = Properties::new();
    props.insert("tokenSymbol".into(), "VRDX".into());
    props.insert("tokenDecimals".into(), 18.into());
    props.insert("ss58Format".into(), 42.into());
    props
}

fn development_genesis() -> serde_json::Value {
    let alice_pub = Sr25519Keyring::Alice.public();
    let bob_pub = Sr25519Keyring::Bob.public();
    let charlie_pub = Sr25519Keyring::Charlie.public();
    let dave_pub = Sr25519Keyring::Dave.public();
    let eve_pub = Sr25519Keyring::Eve.public();

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

    let initial_balance: Balance = 1_000_000_000_000_000_000_000u128; // 1M VRDX

    let babe_authorities: Vec<(BabeAuthorityId, u64)> = vec![
        (BabeAuthorityId::from_slice(alice_pub.as_slice()).unwrap(), 1),
        (BabeAuthorityId::from_slice(bob_pub.as_slice()).unwrap(), 1),
        (BabeAuthorityId::from_slice(charlie_pub.as_slice()).unwrap(), 1),
    ];

    let grandpa_authorities: Vec<(GrandpaAuthorityId, u64)> = vec![
        (GrandpaAuthorityId::from_slice(alice_grandpa.as_slice()).unwrap(), 1),
        (GrandpaAuthorityId::from_slice(bob_grandpa.as_slice()).unwrap(), 1),
        (GrandpaAuthorityId::from_slice(charlie_grandpa.as_slice()).unwrap(), 1),
    ];

    serde_json::json!({
        "balances": {
            "balances": endowed_accounts.iter().map(|k| (k.clone(), initial_balance)).collect::<Vec<_>>(),
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
    })
}

pub fn development_config() -> Result<ChainSpec, String> {
    Ok(
        ChainSpec::builder(&[], Extensions::default())
            .with_name("Verdis Dev")
            .with_id("verdis_dev")
            .with_chain_type(ChainType::Development)
            .with_genesis_config(development_genesis())
            .with_properties(properties())
            .build(),
    )
}

pub fn local_testnet_config() -> Result<ChainSpec, String> {
    Ok(
        ChainSpec::builder(&[], Extensions::default())
            .with_name("Verdis Local Testnet")
            .with_id("verdis_local")
            .with_chain_type(ChainType::Local)
            .with_genesis_config(development_genesis())
            .with_properties(properties())
            .build(),
    )
}
