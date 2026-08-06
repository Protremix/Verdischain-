//! Verdis Chain RPC
//! Standard Substrate RPC (System + Transaction Payment)

use std::sync::Arc;

use jsonrpsee::RpcModule;
use sc_client_api::AuxStore;
use sp_api::ProvideRuntimeApi;
use sp_blockchain::HeaderBackend;
use sp_runtime::traits::Block as BlockT;
use substrate_frame_rpc_system::{System as SystemRpc, SystemApiServer};
use pallet_transaction_payment_rpc::{TransactionPayment as TxPaymentRpc, TransactionPaymentApiServer};

use verdis_runtime::{Block, AccountId};

pub struct FullDeps<C, P> {
    pub client: Arc<C>,
    pub pool: Arc<P>,
}

pub fn create_full<C, P>(
    deps: FullDeps<C, P>,
) -> Result<RpcModule<()>, Box<dyn std::error::Error + Send + Sync>>
where
    C: ProvideRuntimeApi<Block>
        + HeaderBackend<Block>
        + AuxStore
        + Send
        + Sync
        + 'static,
    P: sc_transaction_pool_api::TransactionPool<Block = Block> + Send + Sync + 'static,
{
    let mut io = RpcModule::new(());
    let FullDeps { client, pool } = deps;

    // System RPC
    let system = SystemRpc::new(client.clone(), Arc::new(pool));
    io.merge(system.into_rpc())?;

    // Transaction Payment RPC
    let tx_payment = TxPaymentRpc::new(client);
    io.merge(tx_payment.into_rpc())?;

    Ok(io)
}
