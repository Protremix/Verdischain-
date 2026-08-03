//! Verdis Chain — Full Node Service (Substrate v48)

use std::{sync::Arc, time::Duration};

use sc_basic_authorship::ProposerFactory;
use sc_consensus::LongestChain;
use sc_consensus_babe::{self, BabeParams, ImportQueueParams};
use sc_consensus_grandpa::{
    self, Config as GrandpaConfig, GrandpaParams, SharedVoterState,
    VotingRulesBuilder,
};
use sc_executor::NativeExecutionDispatch;
use sc_service::{
    self, build_network, new_full_parts, spawn_tasks, BuildNetworkParams,
    KeystoreContainer, SpawnTasksParams, TaskManager,
    TFullBackend, TFullClient,
    config::Configuration, Error,
};
use sc_transaction_pool::BasicPool;
use sc_transaction_pool_api::OffchainTransactionPoolFactory;
use sp_api::ProvideRuntimeApi;
use sp_blockchain::HeaderBackend;
use sp_consensus_babe::{BabeApi, SlotDuration};
use sp_runtime::generic::BlockId;
use verdis_runtime::opaque::Block;

pub type FullClient = Arc<TFullClient<Block, verdis_runtime::RuntimeApi, sc_executor::NativeElseWasmExecutor<ExecutorDispatch>>>;
pub type FullBackend = TFullBackend<Block>;

pub struct ExecutorDispatch;

impl NativeExecutionDispatch for ExecutorDispatch {
    type ExtendHostFunctions = sp_io::SubstrateHostFunctions;
    fn dispatch(method: &str, data: &[u8]) -> Option<Vec<u8>> {
        verdis_runtime::api::dispatch(method, data)
    }
    fn native_version() -> sc_executor::NativeVersion {
        verdis_runtime::native_version()
    }
}

/// Partial components for subcommands
pub fn new_partial(
    config: &Configuration,
) -> Result<(FullClient, FullBackend, KeystoreContainer, TaskManager), Error> {
    let executor = sc_service::new_native_or_wasm_executor::<ExecutorDispatch>(config);
    let (client, backend, keystore_container, task_manager) =
        new_full_parts::<Block, verdis_runtime::RuntimeApi, _>(
            config,
            None,
            executor,
            vec![],
        )?;
    Ok((Arc::new(client), backend, keystore_container, task_manager))
}

/// Full node service
#[allow(clippy::type_complexity)]
pub fn new_full(mut config: Configuration) -> Result<TaskManager, Error> {
    let executor = sc_service::new_native_or_wasm_executor::<ExecutorDispatch>(&config);
    let (client, backend, keystore_container, mut task_manager) =
        new_full_parts::<Block, verdis_runtime::RuntimeApi, _>(
            &config,
            None,
            executor,
            vec![],
        )?;
    let client: FullClient = Arc::new(client);
    let keystore = keystore_container.keystore();
    let select_chain = LongestChain::new(backend.clone());

    // Transaction pool
    let transaction_pool = BasicPool::new_full(
        Default::default(),
        config.role.is_authority().into(),
        config.prometheus_config.as_ref().map(|cfg| &cfg.registry),
        task_manager.spawn_essential_handle(),
        client.clone(),
    );
    let transaction_pool = Arc::new(transaction_pool);

    // BABE configuration from runtime API
    let best_hash = client.info().best_hash;
    let babe_config = client
        .runtime_api()
        .configuration(BlockId::Hash(best_hash))
        .map_err(|e| Error::Application(Box::new(e)))?;

    // GRANDPA block import
    let (grandpa_block_import, grandpa_link) = sc_consensus_grandpa::block_import(
        client.clone(),
        0,
        &*client,
        select_chain.clone(),
        None,
    )?;

    // BABE block import wrapping GRANDPA block import
    let (babe_block_import, babe_link) = sc_consensus_babe::block_import(
        babe_config,
        grandpa_block_import,
        client.clone(),
        move |_, _| async move {
            let timestamp = sp_timestamp::InherentDataProvider::from_system_time();
            let slot = sp_consensus_babe::inherents::InherentDataProvider::from_timestamp_and_slot_duration(
                timestamp,
                SlotDuration::from_millis(6000),
            );
            Ok((timestamp, slot))
        },
        select_chain.clone(),
        OffchainTransactionPoolFactory::new(transaction_pool.clone()),
    );

    // BABE import queue
    let (import_queue, _babe_worker_handle) = sc_consensus_babe::import_queue(
        ImportQueueParams {
            link: babe_link.clone(),
            block_import: babe_block_import.clone(),
            justification_import: None,
            client: client.clone(),
            slot_duration: SlotDuration::from_millis(6000),
            spawner: &task_manager.spawn_essential_handle(),
            registry: config.prometheus_config.as_ref().map(|cfg| &cfg.registry),
            telemetry: None,
        },
    )?;

    // Network configuration
    type NetWorker = sc_network::service::NetworkWorker<Block, <Block as sp_runtime::traits::Block>::Hash>;
    let mut net_config = sc_network::config::FullNetworkConfiguration::<
        Block,
        <Block as sp_runtime::traits::Block>::Hash,
        NetWorker,
    >::new(
        &config.network,
        config.prometheus_config.as_ref().map(|cfg| cfg.registry.clone()),
    );

    // GRANDPA notification protocol
    let genesis_hash = client.info().genesis_hash;
    let grandpa_protocol_name =
        sc_consensus_grandpa::protocol_standard_name(&genesis_hash, &config.chain_spec);
    let notification_metrics = sc_network::service::NotificationMetrics::new(
        config.prometheus_config.as_ref().map(|cfg| &cfg.registry),
    );
    let (grandpa_protocol_config, grandpa_notification_service) =
        sc_consensus_grandpa::grandpa_peers_set_config::<Block, NetWorker>(
            grandpa_protocol_name.clone(),
            notification_metrics,
            net_config.peer_store_handle(),
        );
    net_config.add_notification_protocol(grandpa_protocol_config);

    // Build network
    let (network, system_rpc_tx, tx_handler_controller, sync_service) = build_network(
        BuildNetworkParams {
            config: &config,
            net_config,
            client: client.clone(),
            transaction_pool: transaction_pool.clone(),
            spawn_handle: task_manager.spawn_handle(),
            spawn_essential_handle: task_manager.spawn_essential_handle(),
            import_queue,
            block_announce_validator_builder: None,
            warp_sync_config: None,
            block_relay: None,
            metrics: sc_network::service::NotificationMetrics::new(
                config.prometheus_config.as_ref().map(|cfg| &cfg.registry),
            ),
        },
    )?;

    // RPC module builder
    let rpc_builder = {
        let client = client.clone();
        let pool = transaction_pool.clone();
        Box::new(
            move |subscription_executor: sc_rpc::SubscriptionTaskExecutor| {
                let mut module = jsonrpsee::RpcModule::new(());
                let system = substrate_frame_rpc_system::System {
                    client: client.clone(),
                    pool: pool.clone(),
                    _marker: std::marker::PhantomData::<Block>,
                };
                module.merge(
                    substrate_frame_rpc_system::SystemApiServer::into_rpc(system),
                )?;
                let payment = pallet_transaction_payment_rpc::TransactionPayment {
                    client: client.clone(),
                    _marker: std::marker::PhantomData::<Block>,
                };
                module.merge(
                    pallet_transaction_payment_rpc::TransactionPaymentApiServer::into_rpc(payment),
                )?;
                Ok(module)
            },
        )
    };

    // Spawn all tasks
    let _rpc_handlers = spawn_tasks(
        SpawnTasksParams {
            config,
            client: client.clone(),
            backend: backend.clone(),
            task_manager: &mut task_manager,
            keystore: keystore.clone(),
            transaction_pool: transaction_pool.clone(),
            rpc_builder,
            network,
            system_rpc_tx,
            tx_handler_controller,
            sync_service: sync_service.clone(),
            telemetry: None,
            tracing_execute_block: None,
        },
    )?;

    // Start BABE if authority
    if config.role.is_authority() {
        let proposer_factory = ProposerFactory::new(
            task_manager.spawn_handle(),
            client.clone(),
            transaction_pool.clone(),
            None,
            None,
        );

        let babe_worker = sc_consensus_babe::start_babe(
            BabeParams {
                keystore: keystore.clone(),
                client: client.clone(),
                select_chain: select_chain.clone(),
                env: proposer_factory,
                block_import: babe_block_import.clone(),
                sync_oracle: sync_service.clone(),
                justification_sync_link: grandpa_link,
                create_inherent_data_providers: move |_, _| async move {
                    let timestamp =
                        sp_timestamp::InherentDataProvider::from_system_time();
                    let slot =
                        sp_consensus_babe::inherents::InherentDataProvider::from_timestamp_and_slot_duration(
                            timestamp,
                            SlotDuration::from_millis(6000),
                        );
                    Ok((timestamp, slot))
                },
                force_authoring: false,
                backoff_authoring_blocks: None,
                babe_link: babe_link,
                block_proposal_slot_portion:
                    sc_consensus_slots::SlotProportion::new(2f32 / 3f32),
                max_block_proposal_slot_portion: None,
                telemetry: None,
            },
        )?;

        task_manager
            .spawn_essential_handle()
            .spawn("babe", None, babe_worker);
    }

    // Start GRANDPA voter
    if !config.disable_grandpa {
        let grandpa_config = GrandpaConfig {
            gossip_duration: Duration::from_millis(1000),
            justification_generation_period: 512,
            observer_enabled: true,
            local_role: config.role.clone(),
            name: Some(config.network.node_name.clone()),
            keystore: Some(keystore.clone()),
            telemetry: None,
            protocol_name: grandpa_protocol_name,
        };

        let grandpa_future = sc_consensus_grandpa::run_grandpa_voter(
            GrandpaParams {
                config: grandpa_config,
                link: grandpa_link,
                network,
                sync: sync_service.clone(),
                notification_service: grandpa_notification_service,
                voting_rule: VotingRulesBuilder::default().build(),
                prometheus_registry: config
                    .prometheus_config
                    .as_ref()
                    .map(|cfg| cfg.registry.clone()),
                shared_voter_state: SharedVoterState::empty(),
                telemetry: None,
                offchain_tx_pool_factory:
                    OffchainTransactionPoolFactory::new(transaction_pool.clone()),
            },
        )?;

        task_manager
            .spawn_essential_handle()
            .spawn("grandpa", None, grandpa_future);
    }

    Ok(task_manager)
}
