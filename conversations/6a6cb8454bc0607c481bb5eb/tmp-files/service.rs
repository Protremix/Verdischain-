//! Verdis Chain Service — Full Substrate node with BABE + GRANDPA
//!
//! Block production: BABE (VRF-based slot leader election)
//! Finality: GRANDPA (BFT finality gadget)
//! Networking: libp2p
//! RPC: JSON-RPC (port 9933)

use std::sync::Arc;
use std::time::Duration;

use futures::FutureExt;
use sc_client_api::Backend;
use sc_consensus_babe::{BabeLink, BabeParams, SlotDuration};
use sc_consensus_grandpa::{
    GrandpaParams, SharedVoterState, VotingRule,
};
use sc_service::config::Configuration;
use sc_service::{
    build_full, new_full, PartialComponents, TaskManager, TransactionPoolOptions,
    RpcHandlers, KeepRuntimeOffline,
};
use sc_telemetry::TelemetryHandle;
use sc_transaction_pool_api::OffchainTransactionPoolFactory;
use sp_consensus::Error as ConsensusError;
use sp_consensus_grandpa::AuthorityId;

use verdis_runtime::opaque::Block;
use verdis_runtime::{self, RuntimeApi};

type FullBackend = sc_service::FullBackend<Block>;
type FullClient = sc_service::FullClient<Block, RuntimeApi>;
type FullSelectChain = sc_consensus::LongestChain<FullBackend, Block>;

pub fn new_partial(
    config: &Configuration,
) -> Result<
    PartialComponents<
        FullClient,
        FullBackend,
        FullSelectChain,
        sc_consensus_babe::BabeBlockImport<Block, FullClient, FullBackend>,
        sc_consensus_grandpa::GrandpaBlockImport<
            FullBackend,
            Block,
            FullClient,
            FullSelectChain,
        >,
        BabeLink<Block>,
    >,
    sc_service::Error,
> {
    let PartialComponents {
        client,
        backend,
        keystore,
        task_manager,
        transaction_pool,
        import_queue,
        select_chain,
        other,
    } = build_full(config, TaskManager::new(config.prometheus_config.as_ref().map(|cfg| cfg.registry.clone()).expect("Prometheus registry required"), None))?;

    let client = client;
    let select_chain = select_chain.ok_or_else(|| sc_service::Error::Other("select_chain required".into()))?;

    let (block_import, babe_link) = sc_consensus_babe::BabeBlockImport::new(
        client.clone(),
        backend.clone(),
        client.clone(),
        select_chain.clone(),
    );

    let grandpa_block_import = sc_consensus_grandpa::GrandpaBlockImport::new(
        backend.clone(),
        client.clone(),
        select_chain.clone(),
    );

    Ok(PartialComponents {
        client,
        backend,
        keystore,
        task_manager,
        transaction_pool,
        import_queue,
        select_chain,
        other: (babe_link, block_import, grandpa_block_import),
    })
}

pub fn new_full(
    config: Configuration,
) -> sc_service::error::Result<TaskManager> {
    let PartialComponents {
        client,
        backend,
        keystore,
        mut task_manager,
        transaction_pool,
        import_queue,
        select_chain,
        other: (babe_link, block_import, grandpa_block_import),
    } = new_partial(&config)?;

    let (network, system_rpc_tx, tx_handler, network_starter) =
        sc_service::build_network(sc_service::BuildNetworkParams {
            config: &config,
            client: client.clone(),
            transaction_pool: transaction_pool.clone(),
            spawn_handle: task_manager.spawn_handle(),
            import_queue,
            block_announce_validator_builder: None,
            warping_sync: None,
        })?;

    if config.offchain_worker.enabled {
        sc_service::build_offchain_worker(
            &task_manager.spawn_handle(),
            config.offchain_worker.clone(),
            task_manager.spawn_handle(),
            client.clone(),
            network.clone(),
        );
    }

    let rpc_setup = sc_service::spawn_rpc_server(
        &config,
        client.clone(),
        transaction_pool.clone(),
        keystore.clone(),
        backend.clone(),
        system_rpc_tx,
    )?;

    let role = config.role.clone();
    let force_authoring = config.force_authoring;
    let backoff_authoring_blocks = None::<()>;
    let name = config.network.node_name.clone();

    let (grandpa_setup, grandpa_link) = sc_consensus_grandpa::grandpa_params(
        GrandpaParams {
            config: sc_consensus_grandpa::GrandpaParams {
                gossip_duration: Duration::from_millis(333),
                justification_period: 512,
                name: name.clone(),
                observer_enabled: false,
                keystore: keystore.clone(),
                is_authority: role.is_authority(),
                voting_rule: VotingRule::Always,
                max_set_id_session_entries: 0,
                keypair: None,
            },
            telemetry: None,
            link: grandpa_block_import.clone(),
            network: network.clone(),
            voting_rule: VotingRule::Always,
            prometheus: None,
            shared_voter_state: SharedVoterState::empty(),
        },
    )?;

    let grandpa_link_clone = grandpa_link.clone();
    let babe_fut = sc_consensus_babe::run_babe(
        BabeParams {
            block_import: block_import.clone(),
            select_chain: select_chain.clone(),
            client: client.clone(),
            keystore: keystore.clone(),
            env: sc_consensus_babe::BabeEnvironment {
                slot_duration: SlotDuration::from_millis(6000).unwrap(),
                epoch_duration: 600,
                c: (1, 4),
                force_authoring,
                backoff_authoring_blocks,
                babe_link: babe_link.clone(),
                block_proposal_port: sc_consensus_babe::BlockProposalPort::new(
                    client.clone(),
                    transaction_pool.clone(),
                    select_chain.clone(),
                    None,
                ),
            },
        },
    );

    task_manager.spawn_essential_handle().spawn("babe", babe_fut);
    task_manager.spawn_essential_handle().spawn("grandpa", grandpa_setup);

    network_starter.start_network();

    Ok(task_manager)
}
