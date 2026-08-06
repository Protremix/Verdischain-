//! Verdis Chain RPC
//! Standard Substrate RPC (System + Transaction Payment)

use std::sync::Arc;

use jsonrpsee::RpcModule;
use sc_client_api::AuxStore;
use sp_api::ProvideRuntimeApi;
use sp_blockchain::HeaderBackend;
use substrate_frame_rpc_system::{System, SystemApiServer};
use pallet_transaction_payment_rpc::{TransactionPayment, TransactionPaymentApiServer};

use verdis_runtime::opaque::Block;

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
    C::Api: substrate_frame_rpc_system::AccountNonceApi<Block, verdis_runtime::AccountId, verdis_runtime::Index>
        + pallet_transaction_payment_rpc::TransactionPaymentRuntimeApi<Block, verdis_runtime::Balance>,
    P: sc_transaction_pool_api::TransactionPool<Block = Block> + Send + Sync + 'static,
{
    let mut io = RpcModule::new(());
    let FullDeps { client, pool } = deps;

    let system = System::new(client.clone(), pool);
    io.merge(system.into_rpc())?;

    let tx_payment = TransactionPayment::new(client);
    io.merge(tx_payment.into_rpc())?;

    Ok(io)
}
