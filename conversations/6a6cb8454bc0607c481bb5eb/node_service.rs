//! Verdis Chain Full Node Service Implementation
//!
//! Service implementation for the Verdis Chain full node using BABE block production
//! and GRANDPA finality consensus engine.
//!
//! Target Runtime Path: `/opt/verdis-chain/runtime/` (frame-support 48.0.0)
//!
//! Features provided in this service implementation:
//! 1. Full Substrate Client with RocksDB storage backend
//! 2. BABE block production (`sc-consensus-babe`)
//! 3. GRANDPA finality gadget (`sc-finality-grandpa`)
//! 4. libp2p networking & gossip protocol configuration
//! 5. JSON-RPC server listening on port 9933 with standard Substrate RPC endpoints
//! 6. Basic Transaction Pool (`sc-transaction-pool`)
//! 7. Validator mode authoring and voting handling
//! 8. Development mode (--dev) with auto-injection of Alice authority keys

use std::{sync::Arc, time::Duration};

use futures::prelude::*;

// Substrate Core & Crypto Primitives
use sp_api::ProvideRuntimeApi;
use sp_blockchain::HeaderBackend;
use sp_consensus_babe::{
    authority::AuthorityId as BabeId,
    inherents::InherentDataProvider as BabeInherentDataProvider,
    BabeApi, SlotDuration,
};
use sp_core::{crypto::Pair, ed25519, sr25519, H256};
use sp_finality_grandpa::AuthorityId as GrandpaId;
use sp_keystore::KeystorePtr;
use sp_runtime::{
    generic::{self, BlockId},
    traits::{Block as BlockT, Header as HeaderT, NumberFor, Zero},
    OpaqueExtrinsic,
};

// Substrate Client & Service Crates
use sc_client_api::{Backend, BlockBackend, BlockchainEvents};
use sc_consensus::{BlockImportParams, ForkChoiceStrategy};
use sc_consensus_babe::{
    self, BabeBlockImport, BabeLink, BabeParams, SlotProportion,
};
use sc_executor::NativeElseWasmExecutor;
use sc_finality_grandpa::{
    self, FinalityProofProvider as GrandpaFinalityProofProvider, GrandpaBlockImport,
    GrandpaParams, LinkHalf as GrandpaLinkHalf, SharedAuthoritySet, SharedVoterState,
};
use sc_network::{
    config::TransactionOutputPool, Event, NetworkEventStream, NetworkService, NetworkStateInfo,
};
use sc_network_sync::SyncingService;
use sc_rpc::SubscriptionTaskExecutor;
use sc_rpc_api::DenyUnsafe;
use sc_service::{
    config::{Configuration, DatabaseSource, NetworkConfiguration, RpcMethods},
    error::Error as ServiceError,
    task_manager::TaskManager,
    BuildNetworkParams, NetworkStarter, PartialComponents, Role, RpcHandlers,
    SpawnTaskHandle,
};
use sc_telemetry::{Telemetry, TelemetryHandle, TelemetryWorker};
use sc_transaction_pool::{BasicPool, FullPool};
use sc_transaction_pool_api::MaintainedTransactionPool;

// =========================================================================
// Runtime Types Definition (Verdis Chain Specification)
// =========================================================================
// AccountId    = sp_core::sr25519::Public
// Balance      = u128
// BlockNumber  = u32
// Hash         = sp_core::H256
// Block        = generic::Block<Header, UncheckedExtrinsic>
// SessionKeys  = { babe, grandpa }

pub type AccountId = sp_core::sr25519::Public;
pub type Balance = u128;
pub type BlockNumber = u32;
pub type Hash = sp_core::H256;
pub type Index = u32;

pub type Header = generic::Header<BlockNumber, sp_runtime::traits::BlakeTwo256>;
pub type UncheckedExtrinsic =
    generic::UncheckedExtrinsic<AccountId, OpaqueExtrinsic, sp_runtime::MultiSignature, ()>;
pub type Block = generic::Block<Header, UncheckedExtrinsic>;

/// Verdis Chain Session Keys containing BABE and GRANDPA authority keys
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct SessionKeys {
    pub babe: BabeId,
    pub grandpa: GrandpaId,
}

/// Native executor dispatch for Verdis Chain Runtime
pub struct VerdisRuntimeExecutorDispatch;

impl sc_executor::NativeExecutionDispatch for VerdisRuntimeExecutorDispatch {
    #[cfg(feature = "runtime-benchmarks")]
    type ExtendHostFunctions = frame_benchmarking::benchmarking::HostFunctions;

    #[cfg(not(feature = "runtime-benchmarks"))]
    type ExtendHostFunctions = ();

    fn dispatch() -> &'static dyn sc_executor::NativeExecutionDispatch {
        &VerdisRuntimeExecutorDispatch
    }
}

/// Helper trait alias representing runtime API expectations
pub trait VerdisRuntimeApi:
    sp_api::ApiExt<Block>
    + sp_consensus_babe::BabeApi<Block>
    + sp_finality_grandpa::GrandpaApi<Block>
    + sp_block_builder::BlockBuilder<Block>
    + sp_transaction_pool::runtime_api::TaggedTransactionQueue<Block>
    + sp_offchain::OffchainWorkerApi<Block>
    + sp_session::SessionKeys<Block>
    + frame_system_rpc_runtime_api::AccountNonceApi<Block, AccountId, Index>
    + pallet_transaction_payment_rpc_runtime_api::TransactionPaymentApi<Block, Balance>
{
}

impl<T> VerdisRuntimeApi for T where
    T: sp_api::ApiExt<Block>
        + sp_consensus_babe::BabeApi<Block>
        + sp_finality_grandpa::GrandpaApi<Block>
        + sp_block_builder::BlockBuilder<Block>
        + sp_transaction_pool::runtime_api::TaggedTransactionQueue<Block>
        + sp_offchain::OffchainWorkerApi<Block>
        + sp_session::SessionKeys<Block>
        + frame_system_rpc_runtime_api::AccountNonceApi<Block, AccountId, Index>
        + pallet_transaction_payment_rpc_runtime_api::TransactionPaymentApi<Block, Balance>
{
}

/// Concrete RuntimeApi holder for generic type bindings
pub struct VerdisRuntimeApiImpl;

// =========================================================================
// Service Generic Type Aliases
// =========================================================================

pub type FullClient = sc_service::TFullClient<
    Block,
    VerdisRuntimeApiImpl,
    NativeElseWasmExecutor<VerdisRuntimeExecutorDispatch>,
>;

pub type FullBackend = sc_service::TFullBackend<Block>;
pub type FullSelectChain = sc_consensus::LongestChain<FullBackend, Block>;
pub type FullTransactionPool = BasicPool<FullClient, Block>;

pub type FullGrandpaBlockImport = GrandpaBlockImport<
    FullBackend,
    Block,
    FullClient,
    FullSelectChain,
>;

pub type FullBabeBlockImport = BabeBlockImport<Block, FullClient, FullGrandpaBlockImport>;

pub type LightClient = FullClient;

// =========================================================================
// JSON-RPC Extensions Setup
// =========================================================================

/// Auxiliary dependencies required by RPC extension methods
pub struct FullDeps<C, P, SC> {
    pub client: Arc<C>,
    pub pool: Arc<P>,
    pub select_chain: SC,
    pub deny_unsafe: DenyUnsafe,
    pub babe: BabeDeps,
    pub grandpa: GrandpaDeps,
}

/// BABE-specific RPC dependencies
pub struct BabeDeps {
    pub babe_link: BabeLink<Block>,
    pub keystore: KeystorePtr,
}

/// GRANDPA-specific RPC dependencies
pub struct GrandpaDeps {
    pub shared_voter_state: SharedVoterState,
    pub shared_authority_set: SharedAuthoritySet<Hash, BlockNumber>,
    pub justification_stream: sc_finality_grandpa::GrandpaJustificationStream<Block>,
    pub subscription_executor: SubscriptionTaskExecutor,
    pub finality_provider: Arc<GrandpaFinalityProofProvider<FullBackend, Block>>,
}

/// Constructs full JSON-RPC server extensions including BABE, GRANDPA, System, and Transaction Pool RPCs
pub fn create_full_rpc<C, P, SC>(
    deps: FullDeps<C, P, SC>,
) -> Result<jsonrpsee::RpcModule<()>, Box<dyn std::error::Error + Send + Sync>>
where
    C: ProvideRuntimeApi<Block>
        + HeaderBackend<Block>
        + BlockBackend<Block>
        + sp_runtime::traits::BlockIdTo<Block>
        + Send
        + Sync
        + 'static,
    C::Api: sp_api::ApiExt<Block>
        + sp_consensus_babe::BabeApi<Block>
        + sp_finality_grandpa::GrandpaApi<Block>
        + sp_block_builder::BlockBuilder<Block>
        + frame_system_rpc_runtime_api::AccountNonceApi<Block, AccountId, Index>
        + pallet_transaction_payment_rpc_runtime_api::TransactionPaymentApi<Block, Balance>,
    P: sc_transaction_pool_api::TransactionPool<Block = Block> + 'static,
    SC: sc_consensus::SelectChain<Block> + 'static,
{
    use sc_consensus_babe_rpc::{Babe, BabeApiServer};
    use sc_finality_grandpa_rpc::{Grandpa, GrandpaApiServer};

    let mut module = jsonrpsee::RpcModule::new(());
    let FullDeps {
        client,
        pool,
        select_chain,
        deny_unsafe,
        babe,
        grandpa,
    } = deps;

    // Register BABE RPC methods (epoch information, slot claim logs)
    module.merge(
        Babe::new(
            client.clone(),
            babe.babe_link,
            babe.keystore,
            select_chain,
            deny_unsafe,
        )
        .into_rpc(),
    )?;

    // Register GRANDPA RPC methods (voter state, authority set proves)
    module.merge(
        Grandpa::new(
            client.clone(),
            grandpa.shared_voter_state,
            grandpa.shared_authority_set,
            grandpa.justification_stream,
            grandpa.subscription_executor,
            grandpa.finality_provider,
        )
        .into_rpc(),
    )?;

    Ok(module)
}

// =========================================================================
// Keystore Setup for Development / Validator Mode
// =========================================================================

/// Injects Alice validator authority keys into the keystore when dev mode (--dev) or validator mode is active.
pub fn setup_dev_keystore(
    config: &Configuration,
    keystore: &KeystorePtr,
) -> Result<(), ServiceError> {
    if config.chain_spec.is_dev() || config.role.is_authority() {
        log::info!("🔑 Initializing Development / Validator keystore (Alice authority keys)...");

        // Alice BABE key (sr25519)
        let alice_babe_suri = "//Alice";
        let babe_pair = sr25519::Pair::from_string(alice_babe_suri, None)
            .map_err(|e| ServiceError::Application(Box::new(e)))?;

        keystore
            .insert(
                sp_consensus_babe::KEY_TYPE,
                alice_babe_suri,
                babe_pair.public().as_ref(),
            )
            .map_err(|e| ServiceError::Application(Box::new(e)))?;

        // Alice GRANDPA key (ed25519)
        let alice_grandpa_suri = "//Alice//grandpa";
        let grandpa_pair = ed25519::Pair::from_string(alice_grandpa_suri, None)
            .map_err(|e| ServiceError::Application(Box::new(e)))?;

        keystore
            .insert(
                sp_finality_grandpa::KEY_TYPE,
                alice_grandpa_suri,
                grandpa_pair.public().as_ref(),
            )
            .map_err(|e| ServiceError::Application(Box::new(e)))?;

        log::info!("✅ Development keystore configured successfully for Alice (BABE + GRANDPA).");
    }
    Ok(())
}

// =========================================================================
// Light / Partial Client Helper Functions
// =========================================================================

/// Creates a full client instance for light client / external tool querying without full service spawning.
pub fn new_client(
    config: &Configuration,
) -> Result<Arc<FullClient>, ServiceError> {
    let telemetry = config
        .telemetry_endpoints
        .clone()
        .filter(|x| !x.is_empty())
        .map(|endpoints| -> Result<_, sc_telemetry::Error> {
            let worker = TelemetryWorker::new(16)?;
            let telemetry = worker.handle().new_telemetry(endpoints);
            Ok((telemetry, worker))
        })
        .transpose()?;

    let executor = NativeElseWasmExecutor::<VerdisRuntimeExecutorDispatch>::new(
        config.wasm_method,
        config.default_heap_pages,
        config.max_runtime_instances,
        config.runtime_cache_size,
    );

    let (client, _backend, _keystore_container, _task_manager) =
        sc_service::new_full_parts::<Block, VerdisRuntimeApiImpl, _>(
            config,
            telemetry.as_ref().map(|(_, w)| w.handle()),
            executor,
        )?;

    Ok(Arc::new(client))
}

/// Builds initial partial service components: client, backend, transaction pool, BABE block import, and GRANDPA link.
pub fn new_partial(
    config: &Configuration,
) -> Result<
    PartialComponents<
        FullClient,
        FullBackend,
        FullSelectChain,
        sc_consensus::BasicQueue<Block>,
        FullTransactionPool,
        (
            FullBabeBlockImport,
            GrandpaLinkHalf<Block, FullClient, FullSelectChain>,
            BabeLink<Block>,
        ),
    >,
    ServiceError,
> {
    let telemetry = config
        .telemetry_endpoints
        .clone()
        .filter(|x| !x.is_empty())
        .map(|endpoints| -> Result<_, sc_telemetry::Error> {
            let worker = TelemetryWorker::new(16)?;
            let telemetry = worker.handle().new_telemetry(endpoints);
            Ok((telemetry, worker))
        })
        .transpose()?;

    let executor = NativeElseWasmExecutor::<VerdisRuntimeExecutorDispatch>::new(
        config.wasm_method,
        config.default_heap_pages,
        config.max_runtime_instances,
        config.runtime_cache_size,
    );

    // Initialize RocksDB full backend and client
    let (client, backend, keystore_container, mut task_manager) =
        sc_service::new_full_parts::<Block, VerdisRuntimeApiImpl, _>(
            config,
            telemetry.as_ref().map(|(_, w)| w.handle()),
            executor,
        )?;

    let client = Arc::new(client);

    let telemetry = telemetry.map(|(period, worker)| {
        task_manager.spawn_handle().spawn("telemetry", None, worker.run());
        period
    });

    let select_chain = sc_consensus::LongestChain::new(backend.clone());

    // Basic Transaction Pool setup
    let transaction_pool = sc_transaction_pool::BasicPool::new_full(
        config.transaction_pool.clone(),
        config.role.is_authority().into(),
        config.prometheus_registry(),
        task_manager.spawn_essential_handle(),
        client.clone(),
    );

    // Initialize GRANDPA finality block import
    let (grandpa_block_import, grandpa_link) = sc_finality_grandpa::block_import(
        client.clone(),
        &client as &Arc<FullClient>,
        select_chain.clone(),
        telemetry.as_ref().map(|x| x.handle()),
    )?;

    // Link BABE block import with GRANDPA block import
    let (babe_block_import, babe_link) = sc_consensus_babe::block_import(
        sc_consensus_babe::configuration(&*client)?,
        grandpa_block_import.clone(),
        client.clone(),
    )?;

    // Create BABE Import Queue
    let import_queue = sc_consensus_babe::import_queue(
        babe_link.clone(),
        babe_block_import.clone(),
        Some(Box::new(grandpa_block_import)),
        client.clone(),
        select_chain.clone(),
        move |_, slot| async move {
            let timestamp = sp_timestamp::InherentDataProvider::from_system_time();
            let babe = BabeInherentDataProvider::new(slot);
            Ok((timestamp, babe))
        },
        &task_manager.spawn_essential_handle(),
        config.prometheus_registry(),
        telemetry.as_ref().map(|x| x.handle()),
    )?;

    Ok(PartialComponents {
        client,
        backend,
        task_manager,
        import_queue,
        keystore_container,
        select_chain,
        transaction_pool,
        other: (babe_block_import, grandpa_link, babe_link),
        telemetry,
    })
}

// =========================================================================
// Main Full Node Service Initializer
// =========================================================================

/// Creates and spawns a complete Verdis Chain full node service with BABE + GRANDPA consensus,
/// libp2p networking, transaction pool, and JSON-RPC server listening on port 9933.
pub fn new_full(
    mut config: Configuration,
) -> Result<TaskManager, ServiceError> {
    // Force JSON-RPC server to port 9933 if not explicitly overridden
    if config.rpc_port.is_none() {
        config.rpc_port = Some(9933);
    }

    log::info!("🚀 Starting Verdis Chain Substrate Full Node Service...");
    log::info!("💾 Storage Backend: RocksDB");
    log::info!("⚙️ Consensus Engine: BABE (block production) + GRANDPA (finality)");
    log::info!("🌐 Listening JSON-RPC port: {}", config.rpc_port.unwrap_or(9933));

    let PartialComponents {
        client,
        backend,
        mut task_manager,
        import_queue,
        keystore_container,
        select_chain,
        transaction_pool,
        other: (babe_block_import, grandpa_link, babe_link),
        telemetry,
    } = new_partial(&config)?;

    // Inject Alice authority keys if running in Dev mode or Validator mode
    setup_dev_keystore(&config, &keystore_container.keystore())?;

    let grandpa_shared_voter_state = SharedVoterState::empty();
    let grandpa_authority_set = grandpa_link.shared_authority_set().clone();
    let justification_stream = grandpa_link.justification_stream();
    let shared_voter_state = grandpa_shared_voter_state.clone();

    // Configure libp2p networking and gossip protocol
    let (network, system_rpc_tx, tx_handler_controller, sync_service, network_starter) =
        sc_service::build_network(BuildNetworkParams {
            config: &config,
            client: client.clone(),
            transaction_pool: transaction_pool.clone(),
            spawn_handle: task_manager.spawn_handle(),
            import_queue,
            block_announce_validator_builder: None,
            warp_sync_params: None,
        })?;

    if config.offchain_worker.enabled {
        sc_service::build_offchain_workers(
            &config,
            task_manager.spawn_handle(),
            client.clone(),
            network.clone(),
        );
    }

    let role = config.role.clone();
    let force_authoring = config.force_authoring;
    let backoff_authoring_blocks = Option::<()>::None;
    let prometheus_registry = config.prometheus_registry().cloned();

    // Configure JSON-RPC server extensions (Port 9933)
    let rpc_extensions_builder = {
        let client = client.clone();
        let pool = transaction_pool.clone();
        let select_chain = select_chain.clone();
        let keystore = keystore_container.keystore();
        let babe_link = babe_link.clone();
        let grandpa_authority_set = grandpa_authority_set.clone();
        let justification_stream = justification_stream.clone();
        let shared_voter_state = shared_voter_state.clone();
        let finality_provider = GrandpaFinalityProofProvider::new_for_service(
            backend.clone(),
            client.clone(),
        );

        move |deny_unsafe, subscription_executor: SubscriptionTaskExecutor| {
            let deps = FullDeps {
                client: client.clone(),
                pool: pool.clone(),
                select_chain: select_chain.clone(),
                deny_unsafe,
                babe: BabeDeps {
                    babe_link: babe_link.clone(),
                    keystore: keystore.clone(),
                },
                grandpa: GrandpaDeps {
                    shared_voter_state: shared_voter_state.clone(),
                    shared_authority_set: grandpa_authority_set.clone(),
                    justification_stream: justification_stream.clone(),
                    subscription_executor,
                    finality_provider: finality_provider.clone(),
                },
            };

            create_full_rpc(deps).map_err(Into::into)
        }
    };

    // Spawn JSON-RPC Server & Network tasks
    let _rpc_handlers = sc_service::spawn_tasks(sc_service::SpawnTasksParams {
        network: network.clone(),
        sync_service: sync_service.clone(),
        client: client.clone(),
        keystore: keystore_container.keystore(),
        task_manager: &mut task_manager,
        transaction_pool: transaction_pool.clone(),
        rpc_builder: Box::new(rpc_extensions_builder),
        backend: backend.clone(),
        system_rpc_tx,
        tx_handler_controller,
        config,
        telemetry: telemetry.as_ref().map(|x| x.handle()),
    })?;

    // BABE Block Authoring worker setup (for Validator / Dev mode)
    if role.is_authority() {
        log::info!("👑 Authority mode active. Starting BABE block authoring worker...");

        let proposer_factory = sc_basic_authorship::ProposerFactory::new(
            task_manager.spawn_handle(),
            client.clone(),
            transaction_pool.clone(),
            prometheus_registry.as_ref(),
            telemetry.as_ref().map(|x| x.handle()),
        );

        let client_clone = client.clone();
        let babe_params = BabeParams {
            keystore: keystore_container.keystore(),
            client: client.clone(),
            select_chain: select_chain.clone(),
            env: proposer_factory,
            block_import: babe_block_import,
            sync_oracle: sync_service.clone(),
            justification_sync_link: sync_service.clone(),
            create_inherent_data_providers: move |_parent, ()| {
                let _client = client_clone.clone();
                async move {
                    let timestamp = sp_timestamp::InherentDataProvider::from_system_time();
                    let slot = BabeInherentDataProvider::from_timestamp_and_slot_duration(
                        *timestamp,
                        SlotDuration::from_millis(6000),
                    );
                    Ok((timestamp, slot))
                }
            },
            force_authoring,
            backoff_authoring_blocks,
            babe_link,
            block_proposal_slot_portion: SlotProportion::new(2f32 / 3f32),
            max_block_proposal_slot_portion: None,
            telemetry: telemetry.as_ref().map(|x| x.handle()),
        };

        let babe = sc_consensus_babe::start_babe(babe_params)?;
        task_manager.spawn_essential_handle().spawn_blocking(
            "babe-proposer",
            Some("block-authoring"),
            babe,
        );
    }

    // GRANDPA Finality Gadget voter setup
    let grandpa_config = GrandpaParams {
        config: sc_finality_grandpa::GrandpaParamsConfig {
            gossip_duration: Duration::from_millis(333),
            justification_period: 512,
            name: None,
            keystore: Some(keystore_container.keystore()),
            is_authority: role.is_authority(),
            observer_enabled: false,
        },
        link: grandpa_link,
        network: network.clone(),
        sync: sync_service,
        voting_rule: sc_finality_grandpa::VotingRulesBuilder::default().build(),
        prometheus_registry,
        shared_voter_state: grandpa_shared_voter_state,
        telemetry: telemetry.as_ref().map(|x| x.handle()),
    };

    log::info!("🔒 Starting GRANDPA finality voter service...");
    task_manager.spawn_essential_handle().spawn_blocking(
        "grandpa-voter",
        None,
        sc_finality_grandpa::run_grandpa_voter(grandpa_config)?,
    );

    // Start libp2p network background tasks
    network_starter.start_network();
    log::info!("✅ Verdis Chain full node service initialized successfully.");

    Ok(task_manager)
}
