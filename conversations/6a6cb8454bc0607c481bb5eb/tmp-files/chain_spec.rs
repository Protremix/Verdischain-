//! Verdis Chain Genesis Configuration

use sp_core::sr25519;
use sp_runtime::traits::IdentifyAccount;

use verdis_runtime::{
    AccountId, BalancesConfig, GenesisConfig, DposConfig, EcoConfig,
    TokenomicsConfig, VestingConfig, AmmDexConfig, SudoConfig, SystemConfig,
    SessionConfig, SessionKeys, WASM_BINARY,
};

pub type ChainSpec = sc_service::GenericChainSpec<GenesisConfig>;

pub struct VerdisChainSpec;

impl VerdisChainSpec {
    pub fn chain_spec() -> ChainSpec {
        let wasm = WASM_BINARY.expect("WASM binary not available. Build with `cargo build`").to_vec();
        let root = get_account_id_from_seed::<sr25519::Public>("//Alice");

        // 5 initial validators
        let validator_seeds = ["//Validator1", "//Validator2", "//Validator3", "//Validator4", "//Validator5"];
        let validators: Vec<AccountId> = validator_seeds
            .iter()
            .map(|s| get_account_id_from_seed::<sr25519::Public>(s))
            .collect();

        // Session keys for each validator (BABE + GRANDPA)
        let session_keys: Vec<(AccountId, SessionKeys)> = validator_seeds
            .iter()
            .map(|s| {
                let account = get_account_id_from_seed::<sr25519::Public>(s);
                let babe = get_babe_keypair(s);
                let grandpa = get_grandpa_keypair(s);
                (account, SessionKeys { babe, grandpa })
            })
            .collect();

        ChainSpec::from_genesis(
            "Verdis Chain",
            "verdis",
            ChainSpec::DEFAULT_PROPERTIES,
            move || {
                GenesisConfig {
                    system: SystemConfig {
                        code: wasm.clone(),
                        _config: Default::default(),
                    },
                    balances: BalancesConfig {
                        balances: vec![
                            (root.clone(), 15_000_000_000 * UNITS),
                            (validators[0].clone(), 2_000_000_000 * UNITS),
                            (validators[1].clone(), 2_000_000_000 * UNITS),
                            (validators[2].clone(), 2_000_000_000 * UNITS),
                            (validators[3].clone(), 2_000_000_000 * UNITS),
                            (validators[4].clone(), 2_000_000_000 * UNITS),
                            (get_account_id_from_seed::<sr25519::Public>("//Treasury"),
                             20_000_000_000 * UNITS),
                            (get_account_id_from_seed::<sr25519::Public>("//Team"),
                             15_000_000_000 * UNITS),
                            (get_account_id_from_seed::<sr25519::Public>("//Staking"),
                             10_000_000_000 * UNITS),
                            (get_account_id_from_seed::<sr25519::Public>("//Liquidity"),
                             5_000_000_000 * UNITS),
                            (get_account_id_from_seed::<sr25519::Public>("//Advisors"),
                             3_000_000_000 * UNITS),
                            (get_account_id_from_seed::<sr25519::Public>("//Airdrop"),
                             2_000_000_000 * UNITS),
                        ],
                    },
                    sudo: SudoConfig {
                        key: Some(root.clone()),
                    },
                    session: SessionConfig {
                        keys: session_keys.clone(),
                    },
                    transaction_payment: Default::default(),
                    dpos: DposConfig {
                        validators: validators.iter().map(|v| {
                            (v.clone(), 1_000_000_000 * UNITS, true)
                        }).collect(),
                        validator_count: 5,
                        block_reward: 16 * UNITS,
                    },
                    eco: EcoConfig {
                        carbon_credits: vec![
                            (b"VERDIS-CC-001".to_vec(), b"Amazon Reforestation".to_vec(),
                             5_000_000, true, root.clone()),
                            (b"VERDIS-CC-002".to_vec(), b"Solar Farm Offset".to_vec(),
                             5_000_000, true, root.clone()),
                            (b"VERDIS-CC-003".to_vec(), b"Wind Energy Credits".to_vec(),
                             3_000_000, true, root.clone()),
                            (b"VERDIS-CC-004".to_vec(), b"Mangrove Restoration".to_vec(),
                             2_000_000, true, root.clone()),
                            (b"VERDIS-CC-005".to_vec(), b"Geothermal Offset".to_vec(),
                             2_000_000, true, root.clone()),
                        ],
                        reforest_projects: vec![
                            (b"VERDIS-RF-001".to_vec(), b"Amazon Rainforest".to_vec(),
                             30_000, b"Brazil".to_vec(), 85, true),
                        ],
                        green_validators: validators.iter().map(|v| {
                            (v.clone(), true, b"Solar".to_vec(), 5_000, 10_000, 40u8)
                        }).collect(),
                    },
                    tokenomics: TokenomicsConfig {
                        total_supply: 100_000_000_000 * UNITS,
                        max_supply: 100_000_000_000 * UNITS,
                        circulating_supply: 15_000_000_000 * UNITS,
                        investor_allocation: 12_000_000_000 * UNITS,
                        distribution: vec![
                            (b"community".to_vec(), 35_000_000_000 * UNITS, 35u8, 2920u32, 0u32),
                            (b"treasury".to_vec(), 20_000_000_000 * UNITS, 20u8, 0u32, 0u32),
                            (b"team".to_vec(), 15_000_000_000 * UNITS, 15u8, 1080u32, 365u32),
                            (b"investors".to_vec(), 10_000_000_000 * UNITS, 10u8, 720u32, 180u32),
                            (b"staking".to_vec(), 10_000_000_000 * UNITS, 10u8, 0u32, 0u32),
                            (b"liquidity".to_vec(), 5_000_000_000 * UNITS, 5u8, 720u32, 0u32),
                            (b"advisors".to_vec(), 3_000_000_000 * UNITS, 3u8, 360u32, 365u32),
                            (b"airdrop".to_vec(), 2_000_000_000 * UNITS, 2u8, 0u32, 0u32),
                        ],
                        presale_price: 500,
                    },
                    vesting: VestingConfig {
                        vesting_schedules: vec![
                            (b"seed".to_vec(), 3_000_000_000 * UNITS, 60u32, 180u32),
                            (b"private".to_vec(), 3_000_000_000 * UNITS, 60u32, 180u32),
                            (b"public".to_vec(), 2_500_000_000 * UNITS, 30u32, 90u32),
                            (b"final".to_vec(), 1_500_000_000 * UNITS, 30u32, 90u32),
                        ],
                    },
                    amm_dex: AmmDexConfig {
                        initial_pools: vec![
                            (b"CARBON".to_vec(), b"VRDX".to_vec(),
                             1_270_000 * UNITS, 1_580_000 * UNITS, 30u32),
                            (b"ECO".to_vec(), b"VRDX".to_vec(),
                             1_470_000 * UNITS, 1_370_000 * UNITS, 30u32),
                            (b"CARBON".to_vec(), b"ECO".to_vec(),
                             598_000 * UNITS, 837_000 * UNITS, 30u32),
                            (b"TREE".to_vec(), b"VRDX".to_vec(),
                             499_000 * UNITS, 500_000 * UNITS, 30u32),
                            (b"GREEN".to_vec(), b"VRDX".to_vec(),
                             506_000 * UNITS, 494_000 * UNITS, 30u32),
                            (b"REDD".to_vec(), b"VRDX".to_vec(),
                             505_000 * UNITS, 495_000 * UNITS, 30u32),
                            (b"ECOGR".to_vec(), b"VRDX".to_vec(),
                             504_000 * UNITS, 495_000 * UNITS, 30u32),
                        ],
                    },
                }
            },
            vec![],
            None,
            None,
            None,
            None,
            Default::default(),
        )
    }

    pub fn dev_spec() -> ChainSpec {
        Self::chain_spec()
    }
}

const UNITS: u128 = 1_000_000_000;

fn get_account_id_from_seed<TPublic: sp_core::Public + From<sp_core::sr25519::Public>>(
    seed: &str,
) -> AccountId
where
    TPublic::Pair: sp_core::Pair,
{
    let pair = TPublic::Pair::from_string(seed, None).unwrap();
    let public = pair.public();
    AccountId::from(public.to_raw_vec())
}

fn get_babe_keypair(seed: &str) -> sp_consensus_babe::app::Public {
    use sp_core::Pair;
    let pair = sp_consensus_babe::app::Pair::from_string(seed, None).unwrap();
    pair.public()
}

fn get_grandpa_keypair(seed: &str) -> sp_consensus_grandpa::app::Public {
    use sp_core::Pair;
    let pair = sp_consensus_grandpa::app::Pair::from_string(seed, None).unwrap();
    pair.public()
}
