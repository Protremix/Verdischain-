//! Verdis Chain Genesis Configuration
//!
//! Uses the Substrate v48 ChainSpec builder pattern with JSON genesis config patches.

use sc_chain_spec::GenericChainSpec;
use serde_json::json;
use sp_core::sr25519;

use verdis_runtime::{
    AccountId, RuntimeGenesisConfig, WASM_BINARY,
    SessionKeys,
};

pub type ChainSpec = GenericChainSpec;

pub struct VerdisChainSpec;

impl VerdisChainSpec {
    pub fn chain_spec() -> ChainSpec {
        let wasm = WASM_BINARY.expect("WASM binary not available. Build with `cargo build`").to_vec();

        // Generate account IDs from seeds
        let root = account_id("//Alice");
        let v1 = account_id("//Validator1");
        let v2 = account_id("//Validator2");
        let v3 = account_id("//Validator3");
        let v4 = account_id("//Validator4");
        let v5 = account_id("//Validator5");

        // Generate session keys (BABE + GRANDPA) for each validator
        let keys: Vec<(String, String, serde_json::Value)> = vec![
            (v1.clone(), v1.clone(), session_keys_json("//Validator1")),
            (v2.clone(), v2.clone(), session_keys_json("//Validator2")),
            (v3.clone(), v3.clone(), session_keys_json("//Validator3")),
            (v4.clone(), v4.clone(), session_keys_json("//Validator4")),
            (v5.clone(), v5.clone(), session_keys_json("//Validator5")),
        ];

        let u = 1_000_000_000u128; // 1 VRDX = 10^9 base units

        let genesis_patch = json!({
            "balances": {
                "balances": [
                    [root.clone(), (15_000_000_000u128 * u).to_string()],
                    [v1.clone(), (2_000_000_000u128 * u).to_string()],
                    [v2.clone(), (2_000_000_000u128 * u).to_string()],
                    [v3.clone(), (2_000_000_000u128 * u).to_string()],
                    [v4.clone(), (2_000_000_000u128 * u).to_string()],
                    [v5.clone(), (2_000_000_000u128 * u).to_string()],
                    [account_id("//Treasury"), (20_000_000_000u128 * u).to_string()],
                    [account_id("//Team"), (15_000_000_000u128 * u).to_string()],
                    [account_id("//Staking"), (10_000_000_000u128 * u).to_string()],
                    [account_id("//Liquidity"), (5_000_000_000u128 * u).to_string()],
                    [account_id("//Advisors"), (3_000_000_000u128 * u).to_string()],
                    [account_id("//Airdrop"), (2_000_000_000u128 * u).to_string()],
                ]
            },
            "sudo": {
                "key": root
            },
            "session": {
                "keys": keys
            },
            "dpos": {
                "validators": [
                    [v1.clone(), (1_000_000_000u128 * u).to_string(), true],
                    [v2.clone(), (1_000_000_000u128 * u).to_string(), true],
                    [v3.clone(), (1_000_000_000u128 * u).to_string(), true],
                    [v4.clone(), (1_000_000_000u128 * u).to_string(), true],
                    [v5.clone(), (1_000_000_000u128 * u).to_string(), true],
                ],
                "validatorCount": 5,
                "blockReward": (16u128 * u).to_string()
            },
            "eco": {
                "carbonCredits": [
                    ["VERDIS-CC-001", "Amazon Reforestation", 5000000, true, root.clone()],
                    ["VERDIS-CC-002", "Solar Farm Offset", 5000000, true, root.clone()],
                    ["VERDIS-CC-003", "Wind Energy Credits", 3000000, true, root.clone()],
                    ["VERDIS-CC-004", "Mangrove Restoration", 2000000, true, root.clone()],
                    ["VERDIS-CC-005", "Geothermal Offset", 2000000, true, root.clone()]
                ],
                "reforestProjects": [
                    ["VERDIS-RF-001", "Amazon Rainforest", 30000, "Brazil", 85, true]
                ],
                "greenValidators": [
                    [v1, true, "Solar", 5000, 10000, 40],
                    [v2, true, "Solar", 5000, 10000, 40],
                    [v3, true, "Solar", 5000, 10000, 40],
                    [v4, true, "Solar", 5000, 10000, 40],
                    [v5, true, "Solar", 5000, 10000, 40]
                ]
            },
            "tokenomics": {
                "totalSupply": (100_000_000_000u128 * u).to_string(),
                "maxSupply": (100_000_000_000u128 * u).to_string(),
                "circulatingSupply": (15_000_000_000u128 * u).to_string(),
                "investorAllocation": (12_000_000_000u128 * u).to_string(),
                "distribution": [
                    ["community", (35_000_000_000u128 * u).to_string(), 35, 2920, 0],
                    ["treasury", (20_000_000_000u128 * u).to_string(), 20, 0, 0],
                    ["team", (15_000_000_000u128 * u).to_string(), 15, 1080, 365],
                    ["investors", (10_000_000_000u128 * u).to_string(), 10, 720, 180],
                    ["staking", (10_000_000_000u128 * u).to_string(), 10, 0, 0],
                    ["liquidity", (5_000_000_000u128 * u).to_string(), 5, 720, 0],
                    ["advisors", (3_000_000_000u128 * u).to_string(), 3, 360, 365],
                    ["airdrop", (2_000_000_000u128 * u).to_string(), 2, 0, 0]
                ],
                "presalePrice": 500
            },
            "vesting": {
                "vestingSchedules": [
                    ["seed", (3_000_000_000u128 * u).to_string(), 60, 180],
                    ["private", (3_000_000_000u128 * u).to_string(), 60, 180],
                    ["public", (2_500_000_000u128 * u).to_string(), 30, 90],
                    ["final", (1_500_000_000u128 * u).to_string(), 30, 90]
                ]
            },
            "ammDex": {
                "initialPools": [
                    ["CARBON", "VRDX", (1_270_000u128 * u).to_string(), (1_580_000u128 * u).to_string(), 30],
                    ["ECO", "VRDX", (1_470_000u128 * u).to_string(), (1_370_000u128 * u).to_string(), 30],
                    ["CARBON", "ECO", (598_000u128 * u).to_string(), (837_000u128 * u).to_string(), 30],
                    ["TREE", "VRDX", (499_000u128 * u).to_string(), (500_000u128 * u).to_string(), 30],
                    ["GREEN", "VRDX", (506_000u128 * u).to_string(), (494_000u128 * u).to_string(), 30],
                    ["REDD", "VRDX", (505_000u128 * u).to_string(), (495_000u128 * u).to_string(), 30],
                    ["ECOGR", "VRDX", (504_000u128 * u).to_string(), (495_000u128 * u).to_string(), 30]
                ]
            }
        });

        GenericChainSpec::builder(&wasm, sc_chain_spec::NoExtension::None)
            .with_name("Verdis Chain")
            .with_id("verdis")
            .with_chain_type(sc_chain_spec::ChainType::Development)
            .with_genesis_config_patch(genesis_patch)
            .with_protocol_id("verdis")
            .build()
    }
}

fn account_id(seed: &str) -> String {
    use sp_core::Pair;
    let pair = sr25519::Pair::from_string(seed, None).unwrap();
    let public: sp_core::sr25519::Public = pair.public();
    let account_id: AccountId = public.into();
    // Return SS58 address
    account_id.to_ss58check()
}

fn session_keys_json(seed: &str) -> serde_json::Value {
    use sp_core::Pair;
    // BABE key
    let babe_pair = sp_consensus_babe::AuthorityPair::from_string(seed, None).unwrap();
    let babe_public = babe_pair.public();
    // GRANDPA key
    let grandpa_pair = sp_consensus_grandpa::AuthorityPair::from_string(seed, None).unwrap();
    let grandpa_public = grandpa_pair.public();

    json!({
        "babe": babe_public.to_raw_vec(),
        "grandpa": grandpa_public.to_raw_vec()
    })
}
