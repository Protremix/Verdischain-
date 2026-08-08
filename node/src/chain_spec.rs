//! Verdis Chain — Chain Specification (Substrate v48)

use frame_support::traits::Currency;
use frame_support::PalletId;
use sc_chain_spec::ChainType;
use sp_consensus_babe::AuthorityId as BabeId;
use sp_consensus_grandpa::AuthorityId as GrandpaId;
use sp_keyring::{Ed25519Keyring, Sr25519Keyring};
use sp_runtime::traits::AccountIdConversion;
use verdis_runtime::{
    pallet_amm_dex, pallet_collective, pallet_dpos, pallet_eco, pallet_treasury, AccountId,
    SessionKeys,
};

pub type VerdisChainSpec = sc_service::GenericChainSpec;

/// Create the development chain spec for Verdis
pub fn chain_spec() -> VerdisChainSpec {
    let genesis = genesis_config();
    let patch = serde_json::to_value(&genesis).expect("Failed to serialize genesis config");

    sc_chain_spec::GenericChainSpec::builder(
        verdis_runtime::WASM_BINARY.expect("WASM binary exists"),
        Default::default(),
    )
    .with_name("Verdis")
    .with_id("verdis")
    .with_chain_type(ChainType::Development)
    .with_properties({
        let mut props = serde_json::Map::new();
        props.insert("tokenSymbol".into(), "VRDX".into());
        props.insert("tokenDecimals".into(), 9.into());
        props.insert("ss58Format".into(), 909.into());
        props
    })
    .with_genesis_config_patch(patch)
    .build()
}

fn genesis_config() -> verdis_runtime::RuntimeGenesisConfig {
    use verdis_runtime::{BabeConfig, BalancesConfig, GrandpaConfig, SessionConfig, SudoConfig};

    // === Token Distribution (100B VRS total) ===
    // UNITS = 1_000_000_000 (9 decimals)
    // Total: 100,000,000,000 * UNITS = 100,000,000,000,000,000,000
    //
    // 8-Category Distribution:
    //   Community  (35%) = 35B  → EcoPalletId (community grants)
    //   Treasury   (20%) = 20B  → DposPalletId (treasury + staking rewards)
    //   Team       (15%) = 15B  → Alice (sudo key)
    //   Investors  (10%) = 10B  → TokenomicsPalletId (IDO allocations)
    //   Staking    (10%) = 10B  → DposPalletId (block reward pool)
    //   Liquidity  (5%)  = 5B   → DexPalletId (AMM liquidity provision)
    //   Advisors   (3%)  = 3B   → VestingPalletId (advisor vesting)
    //   Airdrop    (2%)  = 2B   → VestingPalletId (airdrop vesting)
    //
    // DposPalletId holds Treasury (20B) + Staking (10B) = 30B
    // VestingPalletId holds Advisors (3B) + Airdrop (2B) = 5B

    let sudo_account: AccountId = Sr25519Keyring::Alice.to_account_id();
    let dpos_pool: AccountId = PalletId(*b"verdisdp").into_account_truncating();
    let tokenomics_pool: AccountId = PalletId(*b"verdistk").into_account_truncating();
    let dex_pool: AccountId = PalletId(*b"verdisdx").into_account_truncating();
    let eco_pool: AccountId = PalletId(*b"verdisec").into_account_truncating();
    let vesting_pool: AccountId = PalletId(*b"verdisvs").into_account_truncating();

    let units: u128 = 1_000_000_000;
    let billion: u128 = 1_000_000_000 * units; // 1B VRS

    // BABE/GRANDPA authorities are initialized via session.keys
    let babe_authorities: Vec<(BabeId, u64)> = vec![];
    let grandpa_authorities: Vec<(GrandpaId, u64)> = vec![];

    // Production: Each validator gets unique session keys (no key reuse)
    let session_keys: Vec<(AccountId, AccountId, SessionKeys)> = vec![
        (
            Sr25519Keyring::Alice.to_account_id(),
            Sr25519Keyring::Alice.to_account_id(),
            SessionKeys {
                babe: Sr25519Keyring::Alice.public().into(),
                grandpa: Ed25519Keyring::Alice.public().into(),
            },
        ),
    ];

    verdis_runtime::RuntimeGenesisConfig {
        system: Default::default(),
        balances: BalancesConfig {
            balances: vec![
                // Team (14B) — Alice is the sudo/founder
                (sudo_account.clone(), 13_350 * units), // ~13.35B (team allocation after validator stakes)
                // Validator stakes (split from team allocation)
                (Sr25519Keyring::Bob.to_account_id(), billion / 4),
                (Sr25519Keyring::Charlie.to_account_id(), billion / 4),
                (Sr25519Keyring::Dave.to_account_id(), billion / 4),
                (Sr25519Keyring::Eve.to_account_id(), billion / 4),
                (Sr25519Keyring::Ferdie.to_account_id(), billion / 4),
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
            validators: vec![
                (
                    Sr25519Keyring::Alice.to_account_id(),
                    10_000 * 1_000_000_000,
                    true,
                ),
                (
                    Sr25519Keyring::Bob.to_account_id(),
                    10_000 * 1_000_000_000,
                    true,
                ),
                (
                    Sr25519Keyring::Charlie.to_account_id(),
                    10_000 * 1_000_000_000,
                    true,
                ),
                (
                    Sr25519Keyring::Dave.to_account_id(),
                    10_000 * 1_000_000_000,
                    true,
                ),
                (
                    Sr25519Keyring::Eve.to_account_id(),
                    10_000 * 1_000_000_000,
                    true,
                ),
                (
                    Sr25519Keyring::Ferdie.to_account_id(),
                    10_000 * 1_000_000_000,
                    true,
                ),
                (
                    AccountId::from(hex_literal::hex!(
                        "e02d26312eb4ab76028ae99ff55ce7d70e9657e31218880bc4b1f39a3aabe866"
                    )),
                    10_000 * 1_000_000_000,
                    true,
                ),
                (
                    AccountId::from(hex_literal::hex!(
                        "b265f2455b6a7b0ddb85c89cb604a851f125a411e0d66d34d23564da2d0b5323"
                    )),
                    10_000 * 1_000_000_000,
                    true,
                ),
                (
                    AccountId::from(hex_literal::hex!(
                        "28b50591557804cdfb041ecc82104db4eb4429a44e822763fea504dfbcd93e7c"
                    )),
                    10_000 * 1_000_000_000,
                    true,
                ),
                (
                    AccountId::from(hex_literal::hex!(
                        "d010e6979cf898866efa21464f44538d12ea3b804a03878f93f12071f84c5c18"
                    )),
                    10_000 * 1_000_000_000,
                    true,
                ),
                (
                    AccountId::from(hex_literal::hex!(
                        "989979834b681814ddb5f95ffc1943e0dc810e8edb090cbf2a524e7975c6f76d"
                    )),
                    10_000 * 1_000_000_000,
                    true,
                ),
                (
                    AccountId::from(hex_literal::hex!(
                        "642aad74ec10b27fc15a77449e67492650e0f96e151812eb4cf2fa9f3609031f"
                    )),
                    10_000 * 1_000_000_000,
                    true,
                ),
                (
                    AccountId::from(hex_literal::hex!(
                        "706db647c9361b782d47ad35028f86fb6d9480737bc9a8c798dd5fa76fc65a7e"
                    )),
                    10_000 * 1_000_000_000,
                    true,
                ),
                (
                    AccountId::from(hex_literal::hex!(
                        "e87ffb2ab8c1f3338e7c7bc28484f6fa23a96788ca2c8f0fa3468a75e6df713a"
                    )),
                    10_000 * 1_000_000_000,
                    true,
                ),
            ],
            validator_names: vec![
                (Sr25519Keyring::Alice.to_account_id(), b"Alice".to_vec()),
                (Sr25519Keyring::Bob.to_account_id(), b"Bob".to_vec()),
                (Sr25519Keyring::Charlie.to_account_id(), b"Charlie".to_vec()),
                (Sr25519Keyring::Dave.to_account_id(), b"Dave".to_vec()),
                (Sr25519Keyring::Eve.to_account_id(), b"Eve".to_vec()),
                (Sr25519Keyring::Ferdie.to_account_id(), b"Ferdie".to_vec()),
                (AccountId::from(hex_literal::hex!("e02d26312eb4ab76028ae99ff55ce7d70e9657e31218880bc4b1f39a3aabe866")), b"GreenNode".to_vec()),
                (AccountId::from(hex_literal::hex!("b265f2455b6a7b0ddb85c89cb604a851f125a411e0d66d34d23564da2d0b5323")), b"EcoValidator".to_vec()),
                (AccountId::from(hex_literal::hex!("28b50591557804cdfb041ecc82104db4eb4429a44e822763fea504dfbcd93e7c")), b"VerdisRanger".to_vec()),
                (AccountId::from(hex_literal::hex!("d010e6979cf898866efa21464f44538d12ea3b804a03878f93f12071f84c5c18")), b"CarbonNode".to_vec()),
                (AccountId::from(hex_literal::hex!("706db647c9361b782d47ad350286fb6d9480737bc9a8c798dd5fa76fc65a7a7e")), b"ForestGuard".to_vec()),
                (AccountId::from(hex_literal::hex!("e87ffb2ab8c1f3338e7c7bc28484f6fa23a96788ca2c8f0fa3468a75e6df713a")), b"SolarStake".to_vec()),
                (AccountId::from(hex_literal::hex!("8eaf04151687736326c9fea17e25fc5287613693c912909cb226aa4794f26a48")), b"WindValidator".to_vec()),
                (AccountId::from(hex_literal::hex!("90b5ab205c6974c9ea841be688864633dc9ca8a357843eeacf2314649965fe22")), b"HydroNode".to_vec()),
            ],

            validator_count: 14,
            block_reward: 16 * 1_000_000_000,
        },
        tokenomics: Default::default(),
        vesting: Default::default(),
        council: pallet_collective::GenesisConfig {
            members: vec![
                Sr25519Keyring::Alice.to_account_id(),
                Sr25519Keyring::Bob.to_account_id(),
                Sr25519Keyring::Charlie.to_account_id(),
                Sr25519Keyring::Dave.to_account_id(),
                Sr25519Keyring::Eve.to_account_id(),
                Sr25519Keyring::Ferdie.to_account_id(),
                AccountId::from(hex_literal::hex!(
                    "e02d26312eb4ab76028ae99ff55ce7d70e9657e31218880bc4b1f39a3aabe866"
                )),
                AccountId::from(hex_literal::hex!(
                    "b265f2455b6a7b0ddb85c89cb604a851f125a411e0d66d34d23564da2d0b5323"
                )),
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
                    500_000 * units,
                    500_000 * units,
                    3,
                ),
                (
                    b"VRDX".to_vec(),
                    b"CARBON".to_vec(),
                    300_000 * units,
                    300_000 * units,
                    3,
                ),
                (
                    b"VRDX".to_vec(),
                    b"TREE".to_vec(),
                    200_000 * units,
                    200_000 * units,
                    3,
                ),
                (
                    b"VRDX".to_vec(),
                    b"GREEN".to_vec(),
                    200_000 * units,
                    200_000 * units,
                    3,
                ),
                (
                    b"ECO".to_vec(),
                    b"CARBON".to_vec(),
                    100_000 * units,
                    100_000 * units,
                    3,
                ),
                (
                    b"VRDX".to_vec(),
                    b"REDD".to_vec(),
                    100_000 * units,
                    100_000 * units,
                    3,
                ),
            ],
            _phantom: Default::default(),
        },
        eco: pallet_eco::GenesisConfig {
            carbon_credits: vec![
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
            ],
            reforest_projects: vec![
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
            ],
            green_validators: vec![
                (
                    Sr25519Keyring::Alice.to_account_id(),
                    true,
                    b"Solar".to_vec(),
                    998,
                    95,
                    1,
                ),
                (
                    Sr25519Keyring::Bob.to_account_id(),
                    true,
                    b"Wind".to_vec(),
                    995,
                    92,
                    2,
                ),
                (
                    Sr25519Keyring::Charlie.to_account_id(),
                    true,
                    b"Hydro".to_vec(),
                    989,
                    88,
                    3,
                ),
                (
                    Sr25519Keyring::Dave.to_account_id(),
                    true,
                    b"Solar".to_vec(),
                    992,
                    85,
                    1,
                ),
                (
                    Sr25519Keyring::Eve.to_account_id(),
                    true,
                    b"Geothermal".to_vec(),
                    997,
                    90,
                    4,
                ),
                (
                    Sr25519Keyring::Ferdie.to_account_id(),
                    true,
                    b"Wind".to_vec(),
                    990,
                    87,
                    2,
                ),
                (
                    AccountId::from(hex_literal::hex!(
                        "e02d26312eb4ab76028ae99ff55ce7d70e9657e31218880bc4b1f39a3aabe866"
                    )),
                    true,
                    b"Solar".to_vec(),
                    985,
                    83,
                    1,
                ),
                (
                    AccountId::from(hex_literal::hex!(
                        "b265f2455b6a7b0ddb85c89cb604a851f125a411e0d66d34d23564da2d0b5323"
                    )),
                    true,
                    b"Hydro".to_vec(),
                    988,
                    86,
                    3,
                ),
                (
                    AccountId::from(hex_literal::hex!(
                        "28b50591557804cdfb041ecc82104db4eb4429a44e822763fea504dfbcd93e7c"
                    )),
                    true,
                    b"Geothermal".to_vec(),
                    993,
                    89,
                    4,
                ),
                (
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
}
