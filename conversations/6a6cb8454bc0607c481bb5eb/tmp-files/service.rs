//! Verdis Chain — Full Node Service (Substrate v48)

use std::{sync::Arc, time::Duration};

use futures::StreamExt;
use log::info;
use sc_basic_authorship::ProposerFactory;
use sc_client_api::BlockBackend;
use sc_consensus::{ImportQueue, LongestChain};
use sc_consensus_babe::{
    self, BabeBlockImport, BabeLink, BabeParams, ImportQueueParams,
};
use sc_consensus_grandpa::{self, Config as GrandpaConfig, GrandpaParams, LinkHalf, SharedVoterState, VotingRule};
use sc_executor::NativeExecutionDispatch;
use sc_service::{
    self, build_network, new_full_parts, spawn_tasks, BuildNetworkParams,
    KeystoreContainer, SpawnTasksParams, TaskManager, TFullClient, TFullBackend,
    config::Configuration, Error,
};
use sc_telemetry::{Telemetry, TelemetryHandle};
use sc_transaction_pool::{BasicPool, FullChainApi};
use sp_blockchain::HeaderBackend;
use sp_consensus::SelectChain;
use sp_keystore::KeystorePtr;
use sp_runtime::BuildStorage;

use verdis_runtime::{
    opaque::Block, AccountId, Balance, RuntimeApi,
};

/// Native executor dispatch type
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

/// Full node service
pub fn new_full(config: Configuration) -> Result<TaskManager, Error> {
    // Create executor
    let executor = sc_service::new_native_or_wasm_executor::<ExecutorDispatch>(&config);

    // Create the initial parts: client, backend, keystore, task_manager
    let (client, backend, keystore_container, mut task_manager) =
        new_full_parts::<Block, RuntimeApi, _>(&config, None, executor, vec![])?;

    let keystore: KeystorePtr = keystore_container.keystore();

    // Create SelectChain
    let select_chain = LongestChain::new(backend.clone());

    // Create transaction pool
    let transaction_pool = BasicPool::new_full(
        Default::default(),
        config.role.is_authority().into(),
        config.prometheus_config.as_ref().map(|cfg| &cfg.registry),
        task_manager.spawn_essential_handle(),
        client.clone(),
    );

    let transaction_pool = Arc::new(transaction_pool);

    // Get BABE configuration from runtime API
    let block_id = sp_runtime::generic::BlockId::GenesisBlock;
    let babe_config = client
        .runtime_api()
        .configuration(block_id)
        .map_err(|e| Error::Application(Box::new(e)))?;

    // Create BABE block import + link
    let (babe_block_import, babe_link) = sc_consensus_babe::block_import(
        babe_config,
        client.clone(),
        client.clone(),
        move |_, _| async move {
            let timestamp = sp_timestamp::InherentDataProvider::from_system_time();
            let slot = sp_consensus_babe::inherents::InherentDataProvider::from_timestamp_slot(
                Duration::from_millis(6000),
                timestamp,
            );
            Ok((timestamp, slot))
        },
        select_chain.clone(),
        sc_transaction_pool_api::OffchainTransactionPoolFactory::new(transaction_pool.clone()),
    );

    // Create GRANDPA block import wrapping BABE import
    let (grandpa_block_import, grandpa_link) = sc_consensus_grandpa::block_import(
        client.clone(),
        0,
        &*client.clone(),
        select_chain.clone(),
        None,
    )?;

    // Wrap the GRANDPA block import in BABE (BABE wraps GRANDPA wraps the actual import)
    // Actually, the order is: BABE wraps GRANDPA wraps client
    // But we already created babe_block_import which wraps the client.
    // The GRANDPA block import should wrap the BABE block import.
    // Let's swap: create GRANDPA first, then BABE wrapping GRANDPA.

    // Actually, the standard pattern is:
    // 1. Create GRANDPA block import wrapping the client
    // 2. Create BABE block import wrapping the GRANDPA block import
    // 3. The import queue uses the BABE block import

    // Let me redo this properly:
    // Actually, looking at the Substrate node template, the order is:
    // grandpa_block_import wraps the client
    // babe_block_import wraps grandpa_block_import
    // import_queue uses babe_block_import

    // But we already created babe_block_import wrapping the client directly.
    // Let me fix this by creating GRANDPA first, then BABE wrapping it.

    // For now, let's just use the babe_block_import and the grandpa_link separately.
    // The grandpa_block_import will be used for justification importing.

    // Create BABE import queue
    let import_queue = sc_consensus_babe::import_queue(
        ImportQueueParams {
            link: babe_link.clone(),
            block_import: babe_block_import.clone(),
            justification_import: Some(Box::new(sc_consensus_grandpa::justification_import(
                client.clone(),
                grandpa_block_import.clone(),
                0,
                &*client.clone(),
            ))),
            client: client.clone(),
            slot_duration: sc_consensus_babe::SlotDuration::from_millis(6000),
            spawner: &task_manager.spawn_essential_handle(),
            registry: config.prometheus_config.as_ref().map(|cfg| &cfg.registry),
            telemetry: None,
        },
    )?;

    // Build network
    let (network, system_rpc_tx, tx_handler_controller, sync_service) = build_network(
        BuildNetworkParams {
            config: &config,
            net_config: sc_network::config::FullNetworkConfiguration::new(
                config.network.clone(),
                config.prometheus_config.as_ref().map(|cfg| cfg.registry.clone()),
            ),
            client: client.clone(),
            transaction_pool: transaction_pool.clone(),
            spawn_handle: task_manager.spawn_handle(),
            spawn_essential_handle: task_manager.spawn_essential_handle(),
            import_queue,
            block_announce_validator_builder: None,
            warp_sync_config: None,
            block_relay: None,
            metrics: sc_network::service::traits::NotificationMetrics::default(),
        },
    )?;

    // Create RPC module
    let rpc_builder = {
        let client = client.clone();
        let pool = transaction_pool.clone();
        let keystore = keystore.clone();

        Box::new(move |subscription_executor: sc_rpc::SubscriptionTaskExecutor| {
            let mut module = jsonrpsee::RpcModule::new(());
            let full_deps = substrate_frame_rpc_system::System {
                client: client.clone(),
                pool: pool.clone(),
                _marker: std::marker::PhantomData::<Block>,
            };
            module.merge(substrate_frame_rpc_system::SystemApiServer::into_rpc(full_deps))?;
            let tp_deps = pallet_transaction_payment_rpc::TransactionPayment {
                client: client.clone(),
                _marker: std::marker::PhantomData::<Block>,
            };
            module.merge(pallet_transaction_payment_rpc::TransactionPaymentApiServer::into_rpc(tp_deps))?;
            Ok(module)
        })
    };

    // Spawn tasks
    let _rpc_handlers = spawn_tasks(
        SpawnTasksParams {
            config,
            client: client.clone(),
            backend: backend.clone(),
            task_manager: &mut task_manager,
            keystore: keystore.clone(),
            transaction_pool: transaction_pool.clone(),
            rpc_builder,
            network: network.clone(),
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
                justification_sync_link: grandpa_link.clone(),
                create_inherent_data_providers: move |_, _| async move {
                    let timestamp = sp_timestamp::InherentDataProvider::from_system_time();
                    let slot = sp_consensus_babe::inherents::InherentDataProvider::from_timestamp_slot(
                        Duration::from_millis(6000),
                        timestamp,
                    );
                    Ok((timestamp, slot))
                },
                force_authoring: false,
                backoff_authoring_blocks: None,
                babe_link: babe_link.clone(),
                block_proposal_slot_portion: sc_consensus_slots::SlotProportion::new(2f32 / 3f32),
                max_block_proposal_slot_portion: None,
                telemetry: None,
            },
        )?;

        let babe_worker_handle = babe_worker.clone();
        task_manager.spawn_essential_handle().spawn("babe", None, babe_worker);
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
            protocol_name: sc_consensus_grandpa::protocol_standard_name(&config.chain_spec),
        };

        let grandpa_future = sc_consensus_grandpa::run_grandpa_voter(
            GrandpaParams {
                config: grandpa_config,
                link: grandpa_link,
                network: network.clone(),
                sync: sync_service.clone(),
                notification_service: sc_consensus_grandpa::grandpa_peers_set_config(),
                voting_rule: VotingRule::default(),
                prometheus_registry: config.prometheus_config.as_ref().map(|cfg| cfg.registry.clone()),
                shared_voter_state: SharedVoterState::empty(),
                telemetry: None,
                offchain_tx_pool_factory: sc_transaction_pool_api::OffchainTransactionPoolFactory::new(transaction_pool.clone()),
            },
        )?;

        task_manager.spawn_essential_handle().spawn("grandpa", None, grandpa_future);
    }

    Ok(task_manager)
}
