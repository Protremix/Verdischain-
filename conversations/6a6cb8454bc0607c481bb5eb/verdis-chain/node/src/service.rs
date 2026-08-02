//! Verdis Chain Service — Full node implementation

use std::sync::Arc;

use sc_executor::RuntimeVersionOf;
use sc_network::NetworkBackend;
use sc_service::{
    Configuration, PartialComponents, Role, RpcHandlers, SpawnTasksParams, TaskManager,
};
use sc_telemetry::{Telemetry, TelemetryHandle, TelemetryWorker};

use sp_blockchain::HeaderBackend;
use sp_consensus_aura::sr25519::AuthorityPair as AuraPair;
use sp_runtime::traits::Block as BlockT;

use verdis_runtime::{opaque::Block, RuntimeApi};

pub fn new_partial(
    config: &Configuration,
) -> Result<PartialComponents<Block, Arc<verdis_runtime::RuntimeApi>>, sc_service::Error> {
    let telemetry = config.telemetry_endpoints.clone();
    let wasm = sc_service::new_wasm_partial(config, crate::VERDIS_RUNTIME)?;

    let client = wasm.client;
    let backend = wasm.backend;
    let keystore_container = wasm.keystore_container;
    let task_manager = wasm.task_manager;

    let telemetry_handle = if telemetry.is_some() {
        let worker = TelemetryWorker::new()?;
        let handle = worker.handle();
        task_manager.spawn_handle().spawn("telemetry", None, worker.run());
        Some(handle)
    } else {
        None
    };

    let telemetry = telemetry.and_then(|t| {
        telemetry_handle.map(|handle| {
            Telemetry::new(
                t,
                handle,
                std::time::Duration::from_secs(60),
                None,
            )
        })
    });

    let select_chain = sc_consensus::LongestChain::new(backend.clone());

    let import_queue = sc_consensus_aura::import_queue::<
        AuraPair,
        _,
        _,
        _,
        _,
        _,
    >(
        sc_consensus_aura::slot_duration_from_aura_constants(&client)?,
        &client,
        sc_consensus_aura::AlwaysAllow,
        select_chain.clone(),
        &task_manager,
        &telemetry,
    )?;

    let partial = PartialComponents {
        client: Arc::new(client),
        backend,
        keystore_container,
        task_manager,
        select_chain: Some(select_chain),
        import_queue,
        telemetry: telemetry.map(|t| (t, None)),
    };

    Ok(partial)
}

pub fn new_full(
    config: Configuration,
) -> Result<
    (
        Arc<verdis_runtime::RuntimeApi>,
        TaskManager,
        Option<RpcHandlers>,
    ),
    sc_service::Error,
> {
    let role = config.role.clone();
    let PartialComponents {
        client,
        backend,
        keystore_container,
        mut task_manager,
        select_chain: _,
        import_queue,
        telemetry: mut telemetry,
    } = new_partial(&config)?;

    let net_config = sc_network::config::FullNetworkConfiguration {
        network_backend: NetworkBackend::default(),
        ..Default::default()
    };

    let (network, system_rpc_tx, tx_handler) =
        sc_service::build_network(config, &net_config, client.clone(), backend.clone(), import_queue)?;

    if let Some(telemetry) = telemetry.as_mut() {
        let peer_id = network.peer_id();
        let _ = peer_id;
        let telemetry = telemetry.0.clone();
        task_manager.spawn_handle().spawn(
            "telemetry-connection-worker",
            None,
            async move {
                telemetry.run().await;
            },
        );
    }

    let prometheus = config.prometheus.clone();
    let _ = prometheus;

    let _rpc = RpcHandlers::new();

    if let Role::Authority = role {
        let keystore = keystore_container.local_keystore()?;
        let block_production_delay = std::time::Duration::from_secs(5);

        let proposer = sc_basic_authorship::Proposer::new(
            client.clone(),
            None,
            None,
            task_manager.spawn_handle(),
            None,
        );

        let aura = sc_consensus_aura::start_aura::<
            AuraPair,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
        >(
            sc_consensus_aura::slot_duration_from_aura_constants(client.as_ref())?,
            client.clone(),
            proposer,
            network,
            std::sync::Arc::new(block_production_delay),
            keystore.clone(),
        )?;

        task_manager
            .spawn_handle()
            .spawn("aura", Some("block-production"), aura);
    }

    Ok((client, task_manager, None))
}
