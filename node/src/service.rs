//! Verdis Chain — Full Node Service (Substrate v48, BABE+GRANDPA)

#![allow(deprecated, unused_imports, unused_variables, clippy::all, dead_code)]
use std::{sync::Arc, time::Duration};

use sc_basic_authorship::ProposerFactory;
use sc_consensus::LongestChain;
use sc_consensus_babe::{self, BabeParams, ImportQueueParams, SlotProportion};
use sc_consensus_grandpa::{
    self, Config as GrandpaConfig, GrandpaParams, SharedVoterState, VotingRulesBuilder,
};
use sc_executor::NativeExecutionDispatch;
use sc_service::{
    self, build_network, config::Configuration, new_full_parts, spawn_tasks, BuildNetworkParams,
    Error, SpawnTasksParams, TFullBackend, TFullClient, TaskManager,
};
use sc_transaction_pool_api::OffchainTransactionPoolFactory;
use sp_api::ProvideRuntimeApi;
use sp_blockchain::HeaderBackend;
use sp_consensus_babe::BabeApi;

#[path = "rpc.rs"]
mod rpc;
use sp_session;
use verdis_runtime::opaque::Block;

/// The minimum period of blocks on which justifications will be
/// imported and generated.
const GRANDPA_JUSTIFICATION_PERIOD: u32 = 512;

pub type FullClient = Arc<
    TFullClient<
        Block,
        verdis_runtime::RuntimeApi,
        sc_executor::NativeElseWasmExecutor<ExecutorDispatch>,
    >,
>;
pub type FullBackend = TFullBackend<Block>;
pub type FullSelectChain = LongestChain<FullBackend, Block>;

pub struct ExecutorDispatch;

impl NativeExecutionDispatch for ExecutorDispatch {
    // pallet-evm's stack runner calls cumulus's get_proof_size(), which is a
    // #[runtime_interface] host function that the plain Substrate set does not
    // register. Without it the node refuses to instantiate the runtime:
    //   "runtime requires function imports which are not present on the host:
    //    'env:ext_storage_proof_size_storage_proof_size_version_1'"
    // On a solo chain it returns PROOF_RECORDING_DISABLED, so get_proof_size()
    // yields None and pallet-evm uses its unwrap_or_default() path - correct here,
    // since there is no PoV to meter.
    type ExtendHostFunctions = (
        sp_io::SubstrateHostFunctions,
        cumulus_primitives_proof_size_hostfunction::storage_proof_size::HostFunctions,
    );
    fn dispatch(method: &str, data: &[u8]) -> Option<Vec<u8>> {
        verdis_runtime::api::dispatch(method, data)
    }
    fn native_version() -> sc_executor::NativeVersion {
        verdis_runtime::native_version()
    }
}

/// Full node service
#[allow(clippy::type_complexity)]
pub fn new_full<
    N: sc_network::NetworkBackend<Block, <Block as sp_runtime::traits::Block>::Hash>,
>(
    mut config: Configuration,
) -> Result<TaskManager, Error> {
    // Inject dev key seed ONLY for --dev mode (single-node dev chain)
    // For multi-node testnet, keys are inserted manually via keystore
    if config.dev_key_seed.is_none()
        && config.role.is_authority()
        && config.chain_spec.chain_type() == sc_chain_spec::ChainType::Development
        && config.chain_spec.id() == "dev"
    {
        config.dev_key_seed = Some("//Alice".to_string());
    }

    #[allow(deprecated)]
    let executor = sc_service::new_native_or_wasm_executor::<ExecutorDispatch>(&config);

    let (client, backend, keystore_container, mut task_manager) =
        new_full_parts::<Block, verdis_runtime::RuntimeApi, _>(&config, None, executor, vec![])?;
    let client: FullClient = Arc::new(client);
    let keystore = keystore_container.keystore();

    // Generate initial session keys from dev key seed
    if let Some(ref seed) = config.dev_key_seed {
        log::info!("Dev key seed: {}", seed);
        sp_session::generate_initial_session_keys(
            client.clone(),
            client.info().best_hash,
            vec![seed.clone()],
            keystore.clone(),
        )
        .map_err(|e| Error::Application(Box::new(e)))?;
        log::info!("Session keys generated");
    }

    let select_chain = LongestChain::new(backend.clone());

    // Transaction pool
    let transaction_pool = Arc::from(
        sc_transaction_pool::Builder::new(
            task_manager.spawn_essential_handle(),
            client.clone(),
            config.role.is_authority().into(),
        )
        .with_options(config.transaction_pool.clone())
        .with_prometheus(config.prometheus_registry())
        .build(),
    );

    // GRANDPA block import
    let (grandpa_block_import, grandpa_link) = sc_consensus_grandpa::block_import(
        client.clone(),
        GRANDPA_JUSTIFICATION_PERIOD,
        &client,
        select_chain.clone(),
        None,
    )?;

    // BABE configuration from runtime API
    let best_hash = client.info().best_hash;
    let babe_config = client
        .runtime_api()
        .configuration(best_hash)
        .map_err(|e| Error::Application(Box::new(e)))?;

    // BABE block import wrapping GRANDPA block import
    let (babe_block_import, babe_link) = sc_consensus_babe::block_import(
        babe_config,
        grandpa_block_import,
        client.clone(),
        move |_, ()| {
            let timestamp = sp_timestamp::InherentDataProvider::from_system_time();
            let slot = sp_consensus_babe::inherents::InherentDataProvider::from_timestamp_and_slot_duration(
                *timestamp,
                sp_consensus_babe::SlotDuration::from_millis(6000),
            );
            async move { Ok((slot, timestamp)) }
        },
        select_chain.clone(),
        OffchainTransactionPoolFactory::new(transaction_pool.clone()),
    ).map_err(|e| Error::Application(Box::new(e)))?;

    // BABE import queue
    let (import_queue, babe_worker_handle) = sc_consensus_babe::import_queue(ImportQueueParams {
        link: babe_link.clone(),
        block_import: babe_block_import.clone(),
        justification_import: None,
        client: client.clone(),
        slot_duration: sp_consensus_babe::SlotDuration::from_millis(6000),
        spawner: &task_manager.spawn_essential_handle(),
        registry: config.prometheus_registry(),
        telemetry: None,
    })
    .map_err(|e| Error::Application(Box::new(e)))?;

    // Network configuration
    let mut net_config = sc_network::config::FullNetworkConfiguration::<
        Block,
        <Block as sp_runtime::traits::Block>::Hash,
        N,
    >::new(&config.network, config.prometheus_registry().cloned());

    // Solana-grade peer limits: 200 in + 200 out = 400 max peers
    net_config.network_config.default_peers_set.in_peers = 200;
    net_config.network_config.default_peers_set.out_peers = 200;

    // GRANDPA notification protocol
    let genesis_hash = client.info().genesis_hash;
    let grandpa_protocol_name =
        sc_consensus_grandpa::protocol_standard_name(&genesis_hash, &config.chain_spec);
    let metrics = N::register_notification_metrics(config.prometheus_registry());
    let peer_store_handle = net_config.peer_store_handle();
    let (grandpa_protocol_config, grandpa_notification_service) =
        sc_consensus_grandpa::grandpa_peers_set_config::<_, N>(
            grandpa_protocol_name.clone(),
            metrics.clone(),
            peer_store_handle,
        );
    net_config.add_notification_protocol(grandpa_protocol_config);

    // Build network
    let (network, system_rpc_tx, tx_handler_controller, sync_service) =
        build_network(BuildNetworkParams {
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
            metrics,
        })?;

    // ===================== Frontier (EVM) =====================
    // Built before the RPC builder because the closure captures these.
    let frontier_backend = Arc::new(
        crate::eth::open_frontier_backend(client.clone(), &config)
            .map_err(|e| Error::Application(Box::new(std::io::Error::other(e))))?,
    );
    let crate::eth::FrontierPartial {
        filter_pool,
        fee_history_cache,
        fee_history_cache_limit,
    } = crate::eth::new_frontier_partial();
    let storage_override = Arc::new(fc_rpc::StorageOverrideHandler::<Block, _, _>::new(
        client.clone(),
    ));
    let pubsub_notification_sinks: Arc<
        fc_mapping_sync::EthereumBlockNotificationSinks<
            fc_mapping_sync::EthereumBlockNotification<Block>,
        >,
    > = Default::default();
    // Match the node's real pruning depth; a wrong value makes the ethereum view stall behind
    // pruned state instead of failing loudly.
    let state_pruning_blocks = match config.state_pruning {
        Some(sc_service::PruningMode::Constrained(ref c)) => c.max_blocks.map(|b| b as u64),
        _ => None,
    };

    let prometheus_registry_for_eth = config.prometheus_registry().cloned();

    // GRANDPA shared voter state — created here so both RPC and voter share it
    let shared_voter_state = SharedVoterState::empty();

    // RPC builder
    let rpc_builder = {
        let client = client.clone();
        let pool = transaction_pool.clone();
        let shared_voter_state = shared_voter_state.clone();
        let frontier_backend = frontier_backend.clone();
        let storage_override = storage_override.clone();
        let filter_pool = filter_pool.clone();
        let fee_history_cache = fee_history_cache.clone();
        let sync = sync_service.clone();
        let eth_network = network.clone();
        let pubsub_sinks = pubsub_notification_sinks.clone();
        let is_authority = config.role.is_authority();
        let max_past_logs: u32 = 10_000;
        let max_block_range: u32 = 1_000;
        let babe_slot_duration = babe_link.config().slot_duration();
        let block_data_cache = Arc::new(fc_rpc::EthBlockDataCacheTask::new(
            task_manager.spawn_handle(),
            storage_override.clone(),
            50,
            50,
            prometheus_registry_for_eth.clone(),
        ));
        Box::new(
            move |_subscription_executor: sc_rpc::SubscriptionTaskExecutor| {
                let mut module = jsonrpsee::RpcModule::new(());
                let system = substrate_frame_rpc_system::System::new(client.clone(), pool.clone());
                module
                    .merge(substrate_frame_rpc_system::SystemApiServer::into_rpc(
                        system,
                    ))
                    .map_err(|e| Error::Application(Box::new(e)))?;
                let payment =
                    pallet_transaction_payment_rpc::TransactionPayment::new(client.clone());
                module
                    .merge(
                        pallet_transaction_payment_rpc::TransactionPaymentApiServer::into_rpc(
                            payment,
                        ),
                    )
                    .map_err(|e| Error::Application(Box::new(e)))?;

                // AmmDex RPC
                let amm_dex = rpc::AmmDexRpcImpl::new(client.clone());
                module
                    .merge(rpc::AmmDexRpcServer::into_rpc(amm_dex))
                    .map_err(|e| Error::Application(Box::new(e)))?;

                // DposApi RPC
                let dpos = rpc::DposRpcImpl::new(client.clone());
                module
                    .merge(rpc::DposRpcServer::into_rpc(dpos))
                    .map_err(|e| Error::Application(Box::new(e)))?;

                // GrandpaApi RPC
                let grandpa = rpc::GrandpaRpcImpl::new(client.clone());
                module
                    .merge(rpc::GrandpaRpcServer::into_rpc(grandpa))
                    .map_err(|e| Error::Application(Box::new(e)))?;

                // TokenomicsApi RPC
                let tokenomics = rpc::TokenomicsRpcImpl::new(client.clone());
                module
                    .merge(rpc::TokenomicsRpcServer::into_rpc(tokenomics))
                    .map_err(|e| Error::Application(Box::new(e)))?;

                // Democracy RPC
                let democracy = rpc::DemocracyRpcImpl::new(client.clone());
                module
                    .merge(rpc::DemocracyRpcServer::into_rpc(democracy))
                    .map_err(|e| Error::Application(Box::new(e)))?;

                // Council RPC
                let council = rpc::CouncilRpcImpl::new(client.clone());
                module
                    .merge(rpc::CouncilRpcServer::into_rpc(council))
                    .map_err(|e| Error::Application(Box::new(e)))?;

                // EcoApi RPC
                let eco = rpc::EcoRpcImpl::new(client.clone());
                module
                    .merge(rpc::EcoRpcServer::into_rpc(eco))
                    .map_err(|e| Error::Application(Box::new(e)))?;

                // Contracts RPC
                let contracts = rpc::ContractsRpcImpl::new(client.clone());
                module
                    .merge(rpc::ContractsRpcServer::into_rpc(contracts))
                    .map_err(|e| Error::Application(Box::new(e)))?;

                // ===================== Ethereum JSON-RPC =====================
                // eth_*, net_*, web3_* so MetaMask and Solidity tooling can reach Verdis.
                //
                // No dev signer is constructed: signing stays in the user's wallet. A node able to
                // sign is a node that can move other people's funds if it is compromised.
                //
                // Pending-block inherents are BABE's, not Aura's as in Frontier's template - this
                // chain runs BABE. Only eth_call/eth_estimateGas against the *pending* block
                // consume them.
                let pending_create_inherent_data_providers = move |_, ()| {
                    let slot_duration = babe_slot_duration;
                    async move {
                        let current = sp_timestamp::InherentDataProvider::from_system_time();
                        let next_slot = current.timestamp().as_millis() + slot_duration.as_millis();
                        let timestamp = sp_timestamp::InherentDataProvider::new(next_slot.into());
                        let slot = sp_consensus_babe::inherents::InherentDataProvider::from_timestamp_and_slot_duration(
                            *timestamp,
                            slot_duration,
                        );
                        Ok((slot, timestamp))
                    }
                };

                let eth = fc_rpc::Eth::<Block, _, _, _, _, _, ()>::new(
                    client.clone(),
                    pool.clone(),
                    Some(verdis_runtime::TransactionConverter),
                    sync.clone(),
                    Vec::new(),
                    storage_override.clone(),
                    frontier_backend.clone(),
                    is_authority,
                    block_data_cache.clone(),
                    fee_history_cache.clone(),
                    fee_history_cache_limit,
                    // eth_call/eth_estimateGas may use at most 10x the block gas limit.
                    10,
                    // Matches the runtime's AllowUnprotectedTxs = false: pre-EIP-155
                    // transactions carry no chain id and replay across chains.
                    false,
                    None,
                    pending_create_inherent_data_providers,
                    None,
                );
                module
                    .merge(fc_rpc::EthApiServer::into_rpc(eth))
                    .map_err(|e| Error::Application(Box::new(e)))?;

                let net = fc_rpc::Net::<Block, _>::new(client.clone(), eth_network.clone(), true);
                module
                    .merge(fc_rpc::NetApiServer::into_rpc(net))
                    .map_err(|e| Error::Application(Box::new(e)))?;

                let web3 = fc_rpc::Web3::<Block, _>::new(client.clone());
                module
                    .merge(fc_rpc::Web3ApiServer::into_rpc(web3))
                    .map_err(|e| Error::Application(Box::new(e)))?;

                let logs_journal = Arc::new(fc_rpc::LogsJournal::new(
                    _subscription_executor.clone(),
                    storage_override.clone(),
                    pubsub_sinks.clone(),
                ));
                let filter = fc_rpc::EthFilter::<Block, _, _, _>::new(
                    client.clone(),
                    frontier_backend.clone(),
                    pool.clone(),
                    filter_pool.clone(),
                    500_usize,
                    max_past_logs,
                    max_block_range,
                    block_data_cache.clone(),
                    logs_journal,
                );
                module
                    .merge(fc_rpc::EthFilterApiServer::into_rpc(filter))
                    .map_err(|e| Error::Application(Box::new(e)))?;

                Ok(module)
            },
        )
    };

    // Save config values before moving config into spawn_tasks
    let role = config.role.clone();
    let disable_grandpa = config.disable_grandpa;
    let prom_registry = config.prometheus_registry().cloned();
    let config_name = config.network.node_name.clone();
    let force_authoring = config.force_authoring;

    // Spawn all tasks
    let _rpc_handlers = spawn_tasks(SpawnTasksParams {
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
    })?;

    // Frontier background tasks: keep the ethereum view of the chain current.
    crate::eth::spawn_frontier_tasks(
        &task_manager,
        client.clone(),
        backend.clone(),
        frontier_backend.clone(),
        filter_pool.clone(),
        storage_override.clone(),
        fee_history_cache.clone(),
        fee_history_cache_limit,
        sync_service.clone(),
        pubsub_notification_sinks.clone(),
        state_pruning_blocks,
    );

    // Start BABE if authority
    if role.is_authority() {
        let proposer_factory = ProposerFactory::new(
            task_manager.spawn_handle(),
            client.clone(),
            transaction_pool.clone(),
            prom_registry.as_ref(),
            None,
        );

        let babe_worker = sc_consensus_babe::start_babe::<_, _, _, _, _, _, _, _, _, sp_blockchain::Error>(
            BabeParams {
                keystore: keystore.clone(),
                client: client.clone(),
                select_chain: select_chain.clone(),
                env: proposer_factory,
                block_import: babe_block_import,
                sync_oracle: sync_service.clone(),
                justification_sync_link: (),
                create_inherent_data_providers: move |_, ()| {
                    let timestamp = sp_timestamp::InherentDataProvider::from_system_time();
                    let slot = sp_consensus_babe::inherents::InherentDataProvider::from_timestamp_and_slot_duration(
                        *timestamp,
                        sp_consensus_babe::SlotDuration::from_millis(6000),
                    );
                    async move { Ok((slot, timestamp)) }
                },
                force_authoring: force_authoring,
                backoff_authoring_blocks: None::<()>,
                babe_link: babe_link.clone(),
                block_proposal_slot_portion: SlotProportion::new(0.5),
                max_block_proposal_slot_portion: None,
                telemetry: None,
            },
        ).map_err(|e| Error::Application(Box::new(e)))?;

        log::info!("Spawning BABE authorship worker");
        task_manager
            .spawn_essential_handle()
            .spawn("babe", None, babe_worker);
    }

    // Start GRANDPA voter
    if !disable_grandpa {
        let grandpa_config = GrandpaConfig {
            gossip_duration: Duration::from_millis(1000),
            justification_generation_period: GRANDPA_JUSTIFICATION_PERIOD,
            observer_enabled: false,
            local_role: role.clone(),
            name: Some(config_name),
            keystore: if role.is_authority() {
                Some(keystore.clone())
            } else {
                None
            },
            telemetry: None,
            protocol_name: grandpa_protocol_name,
        };

        let grandpa_future = sc_consensus_grandpa::run_grandpa_voter(GrandpaParams {
            config: grandpa_config,
            link: grandpa_link,
            network: network.clone(),
            sync: sync_service.clone(),
            notification_service: grandpa_notification_service,
            voting_rule: VotingRulesBuilder::default().build(),
            prometheus_registry: prom_registry,
            shared_voter_state,
            telemetry: None,
            offchain_tx_pool_factory: OffchainTransactionPoolFactory::new(transaction_pool.clone()),
        })
        .map_err(|e| Error::Application(Box::new(e)))?;

        task_manager
            .spawn_essential_handle()
            .spawn("grandpa", None, grandpa_future);
    }

    // Keep babe_worker_handle alive for the lifetime of the service
    // Dropping it would close the channel and kill the babe-worker background task
    std::mem::forget(babe_worker_handle);

    Ok(task_manager)
}
