//! AmmDex RPC module — exposes pool queries via JSON-RPC

use jsonrpsee::core::RpcResult;
use jsonrpsee::proc_macros::rpc;
use jsonrpsee::types::error::{ErrorObject, INTERNAL_ERROR_CODE};
use pallet_amm_dex::{Pool, TokenPool};
use sp_api::ProvideRuntimeApi;
use sp_blockchain::HeaderBackend;
use std::sync::Arc;
use verdis_runtime::opaque::Block;
use verdis_runtime::AmmDexApi as AmmDexRuntimeApi;
use verdis_runtime::{AccountId, Balance};

/// Pool with token names decoded as UTF-8 strings (fixes SCALE BoundedVec<u8> encoding)
#[derive(Clone, serde::Serialize, serde::Deserialize)]
pub struct PoolDetailed<AccountId, Balance> {
    pub id: u32,
    pub token_a: String,
    pub token_b: String,
    pub reserve_a: Balance,
    pub reserve_b: Balance,
    pub total_lp: Balance,
    pub fee_numerator: u32,
    pub fee_denominator: u32,
    pub creator: AccountId,
}

/// Distribution category with name decoded as UTF-8 string (fixes SCALE BoundedVec<u8> encoding)
#[derive(Clone, serde::Serialize, serde::Deserialize)]
pub struct DistributionCategoryDetailed<Balance> {
    pub name: String,
    pub amount: Balance,
    pub percentage: u8,
    pub vesting_days: u32,
    pub cliff_days: u32,
    pub released: Balance,
}

fn rpc_err(e: impl std::fmt::Display) -> ErrorObject<'static> {
    ErrorObject::owned(INTERNAL_ERROR_CODE, e.to_string(), None::<()>)
}

#[rpc(server)]
pub trait AmmDexRpc {
    #[method(name = "amm_dex_getPool")]
    fn get_pool(&self, pool_id: u32) -> RpcResult<Option<PoolDetailed<AccountId, Balance>>>;

    #[method(name = "amm_dex_getPoolCount")]
    fn get_pool_count(&self) -> RpcResult<u32>;

    /// Alias for amm_getPoolCount — returns the number of DEX pools.
    #[method(name = "amm_getPoolCount")]
    fn amm_pool_count(&self) -> RpcResult<u32>;

    #[method(name = "amm_dex_getAllPools")]
    fn get_all_pools(&self) -> RpcResult<Vec<PoolDetailed<AccountId, Balance>>>;

    #[method(name = "amm_dex_getTokenPool")]
    fn get_token_pool(&self, pool_id: u32) -> RpcResult<Option<TokenPool<AccountId, Balance>>>;

    #[method(name = "amm_dex_getTokenPoolCount")]
    fn get_token_pool_count(&self) -> RpcResult<u32>;

    #[method(name = "amm_dex_getAllTokenPools")]
    fn get_all_token_pools(&self) -> RpcResult<Vec<TokenPool<AccountId, Balance>>>;

    #[method(name = "amm_dex_getLiquidity")]
    fn get_liquidity(&self, pool_id: u32, account: AccountId) -> RpcResult<Balance>;

    #[method(name = "amm_dex_getTokenLiquidity")]
    fn get_token_liquidity(&self, pool_id: u32, account: AccountId) -> RpcResult<Balance>;

    #[method(name = "amm_dex_getPrice")]
    fn get_price(&self, pool_id: u32, token: Vec<u8>) -> RpcResult<Option<Balance>>;

    #[method(name = "amm_dex_getSwapQuote")]
    fn get_swap_quote(
        &self,
        pool_id: u32,
        token_in: Vec<u8>,
        amount_in: Balance,
    ) -> RpcResult<Option<Balance>>;
}

pub struct AmmDexRpcImpl<C> {
    client: Arc<C>,
}

impl<C> AmmDexRpcImpl<C> {
    pub fn new(client: Arc<C>) -> Self {
        Self { client }
    }
}

impl<C> AmmDexRpcServer for AmmDexRpcImpl<C>
where
    C: ProvideRuntimeApi<Block> + HeaderBackend<Block> + 'static,
    C::Api: AmmDexRuntimeApi<Block>,
{
    fn get_pool(&self, pool_id: u32) -> RpcResult<Option<PoolDetailed<AccountId, Balance>>> {
        let at = self.client.info().best_hash;
        let pool = self
            .client
            .runtime_api()
            .get_pool(at, pool_id)
            .map_err(rpc_err)?;
        Ok(pool.map(|p| PoolDetailed {
            id: p.id,
            token_a: String::from_utf8_lossy(&p.token_a).to_string(),
            token_b: String::from_utf8_lossy(&p.token_b).to_string(),
            reserve_a: p.reserve_a,
            reserve_b: p.reserve_b,
            total_lp: p.total_lp,
            fee_numerator: p.fee_numerator,
            fee_denominator: p.fee_denominator,
            creator: p.creator,
        }))
    }

    fn get_pool_count(&self) -> RpcResult<u32> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_pool_count(at)
            .map_err(rpc_err)
    }

    fn amm_pool_count(&self) -> RpcResult<u32> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_pool_count(at)
            .map_err(rpc_err)
    }

    fn get_all_pools(&self) -> RpcResult<Vec<PoolDetailed<AccountId, Balance>>> {
        let at = self.client.info().best_hash;
        let pools = self
            .client
            .runtime_api()
            .get_all_pools(at)
            .map_err(rpc_err)?;
        Ok(pools
            .into_iter()
            .map(|p| PoolDetailed {
                id: p.id,
                token_a: String::from_utf8_lossy(&p.token_a).to_string(),
                token_b: String::from_utf8_lossy(&p.token_b).to_string(),
                reserve_a: p.reserve_a,
                reserve_b: p.reserve_b,
                total_lp: p.total_lp,
                fee_numerator: p.fee_numerator,
                fee_denominator: p.fee_denominator,
                creator: p.creator,
            })
            .collect())
    }

    fn get_token_pool(&self, pool_id: u32) -> RpcResult<Option<TokenPool<AccountId, Balance>>> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_token_pool(at, pool_id)
            .map_err(rpc_err)
    }

    fn get_token_pool_count(&self) -> RpcResult<u32> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_token_pool_count(at)
            .map_err(rpc_err)
    }

    fn get_all_token_pools(&self) -> RpcResult<Vec<TokenPool<AccountId, Balance>>> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_all_token_pools(at)
            .map_err(rpc_err)
    }

    fn get_liquidity(&self, pool_id: u32, account: AccountId) -> RpcResult<Balance> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_liquidity(at, pool_id, account)
            .map_err(rpc_err)
    }

    fn get_token_liquidity(&self, pool_id: u32, account: AccountId) -> RpcResult<Balance> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_token_liquidity(at, pool_id, account)
            .map_err(rpc_err)
    }

    fn get_price(&self, pool_id: u32, token: Vec<u8>) -> RpcResult<Option<Balance>> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_price(at, pool_id, token)
            .map_err(rpc_err)
    }

    fn get_swap_quote(
        &self,
        pool_id: u32,
        token_in: Vec<u8>,
        amount_in: Balance,
    ) -> RpcResult<Option<Balance>> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_swap_quote(at, pool_id, token_in, amount_in)
            .map_err(rpc_err)
    }
}

// === DposApi RPC ===
use verdis_runtime::DposApi as DposRuntimeApi;

/// Validator with name decoded as UTF-8 string (fixes SCALE BoundedVec<u8> encoding)
#[derive(Clone, serde::Serialize, serde::Deserialize)]
pub struct ValidatorDetailed<AccountId, Balance> {
    pub address: AccountId,
    pub stake: Balance,
    pub total_votes: Balance,
    pub blocks_produced: u64,
    pub rewards_earned: Balance,
    pub active: bool,
    pub slashed: bool,
    pub registration_deposit: Balance,
    pub green_score: u8,
    pub energy_source: String,
    pub commission: u8,
    pub name: String,
}

#[rpc(server)]
pub trait DposRpc {
    #[method(name = "dpos_activeValidators")]
    fn active_validators(&self) -> RpcResult<Vec<AccountId>>;

    #[method(name = "dpos_allValidators")]
    fn all_validators(&self) -> RpcResult<Vec<AccountId>>;

    #[method(name = "dpos_validatorStake")]
    fn validator_stake(&self, validator: AccountId) -> RpcResult<Balance>;

    #[method(name = "dpos_currentEpoch")]
    fn current_epoch(&self) -> RpcResult<u32>;

    #[method(name = "dpos_validatorName")]
    fn get_validator_name(&self, validator: AccountId) -> RpcResult<Option<Vec<u8>>>;

    #[method(name = "session_sessionIndex")]
    fn session_index(&self) -> RpcResult<u32>;

    #[method(name = "dpos_getAllValidatorsDetailed")]
    fn get_all_validators_detailed(&self) -> RpcResult<Vec<ValidatorDetailed<AccountId, Balance>>>;
}

pub struct DposRpcImpl<C> {
    client: Arc<C>,
}

impl<C> DposRpcImpl<C> {
    pub fn new(client: Arc<C>) -> Self {
        Self { client }
    }
}

impl<C> DposRpcServer for DposRpcImpl<C>
where
    C: ProvideRuntimeApi<Block> + HeaderBackend<Block> + 'static,
    C::Api: DposRuntimeApi<Block>,
{
    fn active_validators(&self) -> RpcResult<Vec<AccountId>> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .active_validators(at)
            .map_err(rpc_err)
    }

    fn all_validators(&self) -> RpcResult<Vec<AccountId>> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .all_validators(at)
            .map_err(rpc_err)
    }

    fn validator_stake(&self, validator: AccountId) -> RpcResult<Balance> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .validator_stake(at, validator)
            .map_err(rpc_err)
    }

    fn current_epoch(&self) -> RpcResult<u32> {
        let at = self.client.info().best_hash;
        self.client.runtime_api().current_epoch(at).map_err(rpc_err)
    }

    fn get_validator_name(&self, validator: AccountId) -> RpcResult<Option<Vec<u8>>> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_validator_name(at, validator)
            .map_err(rpc_err)
    }

    fn session_index(&self) -> RpcResult<u32> {
        let at = self.client.info().best_hash;
        self.client.runtime_api().session_index(at).map_err(rpc_err)
    }

    fn get_all_validators_detailed(&self) -> RpcResult<Vec<ValidatorDetailed<AccountId, Balance>>> {
        let at = self.client.info().best_hash;
        let validators = self
            .client
            .runtime_api()
            .get_all_validators_detailed(at)
            .map_err(rpc_err)?;
        let result: Vec<ValidatorDetailed<AccountId, Balance>> = validators
            .into_iter()
            .map(|v| {
                let name = self
                    .client
                    .runtime_api()
                    .get_validator_name(at, v.address.clone())
                    .unwrap_or(None)
                    .map(|n| String::from_utf8_lossy(&n).to_string())
                    .unwrap_or_default();
                let energy_source = String::from_utf8_lossy(&v.energy_source).to_string();
                ValidatorDetailed {
                    address: v.address,
                    stake: v.stake,
                    total_votes: v.total_votes,
                    blocks_produced: v.blocks_produced,
                    rewards_earned: v.rewards_earned,
                    active: v.active,
                    slashed: v.slashed,
                    registration_deposit: v.registration_deposit,
                    green_score: v.green_score,
                    energy_source,
                    commission: v.commission,
                    name,
                }
            })
            .collect();
        Ok(result)
    }
}

// === GrandpaRpc ===
/// Simplified GRANDPA round state for monitoring
#[derive(Clone, serde::Serialize, serde::Deserialize)]
pub struct GrandpaRoundState {
    pub best_hash: String,
    pub best_number: u32,
    pub finalized_hash: String,
    pub finalized_number: u32,
    pub round: u32,
}

#[rpc(server)]
pub trait GrandpaRpc {
    #[method(name = "grandpa_roundState")]
    fn round_state(&self) -> RpcResult<GrandpaRoundState>;
}

pub struct GrandpaRpcImpl<C> {
    client: Arc<C>,
}

impl<C> GrandpaRpcImpl<C> {
    pub fn new(client: Arc<C>) -> Self {
        Self { client }
    }
}

impl<C> GrandpaRpcServer for GrandpaRpcImpl<C>
where
    C: ProvideRuntimeApi<Block> + HeaderBackend<Block> + 'static,
{
    fn round_state(&self) -> RpcResult<GrandpaRoundState> {
        let info = self.client.info();
        let best_number: u32 = info.best_number.try_into().unwrap_or(0);
        let finalized_number: u32 = info.finalized_number.try_into().unwrap_or(0);
        Ok(GrandpaRoundState {
            best_hash: format!("{:?}", info.best_hash),
            best_number,
            finalized_hash: format!("{:?}", info.finalized_hash),
            finalized_number,
            round: best_number,
        })
    }
}

// === EcoApi RPC ===
use verdis_runtime::EcoApi as EcoRuntimeApi;

/// Combined eco metrics returned by eco_getEcoMetrics.
#[derive(Clone, serde::Serialize, serde::Deserialize)]
pub struct EcoMetrics {
    /// Total CO2 offset in tons
    pub total_co2_offset: u64,
    /// Total trees planted
    pub total_trees_planted: u32,
    /// Total carbon credits retired
    pub total_credits_retired: u64,
    /// Total carbon credit count
    pub carbon_credit_count: u32,
    /// Total reforest project count
    pub reforest_project_count: u32,
    /// Total green validator count
    pub green_validator_count: u32,
}

/// Carbon credit with byte arrays decoded as UTF-8 strings (fixes SCALE encoding)
#[derive(Clone, serde::Serialize, serde::Deserialize)]
pub struct CarbonCreditDetailed<AccountId> {
    pub id: String,
    pub project_name: String,
    pub tons_co2: u64,
    pub verified: bool,
    pub retired: bool,
    pub owner: AccountId,
    pub created_at: u64,
}

/// Reforestation project with byte arrays decoded as UTF-8 strings (fixes SCALE encoding)
#[derive(Clone, serde::Serialize, serde::Deserialize)]
pub struct ReforestProjectDetailed {
    pub id: String,
    pub name: String,
    pub trees_planted: u32,
    pub location: String,
    pub survival_rate: u8,
    pub verified: bool,
}

#[rpc(server)]
pub trait EcoRpc {
    /// Get combined eco metrics (CO2 offset, trees, carbon credits, etc.)
    #[method(name = "eco_getEcoMetrics")]
    fn get_eco_metrics(&self) -> RpcResult<EcoMetrics>;

    #[method(name = "eco_getTotalCO2Offset")]
    fn get_total_co2_offset(&self) -> RpcResult<u64>;

    #[method(name = "eco_getTotalTreesPlanted")]
    fn get_total_trees_planted(&self) -> RpcResult<u32>;

    #[method(name = "eco_getTotalCreditsRetired")]
    fn get_total_credits_retired(&self) -> RpcResult<u64>;

    #[method(name = "eco_getCarbonCreditCount")]
    fn get_carbon_credit_count(&self) -> RpcResult<u32>;

    #[method(name = "eco_getReforestProjectCount")]
    fn get_reforest_project_count(&self) -> RpcResult<u32>;

    #[method(name = "eco_getGreenValidatorCount")]
    fn get_green_validator_count(&self) -> RpcResult<u32>;

    #[method(name = "eco_getGreenScore")]
    fn get_green_score(&self, validator: AccountId) -> RpcResult<Option<u8>>;

    #[method(name = "eco_getAllGreenValidators")]
    fn get_all_green_validators(&self) -> RpcResult<Vec<(AccountId, u8)>>;

    #[method(name = "eco_getAllCarbonCredits")]
    fn get_all_carbon_credits(&self) -> RpcResult<Vec<CarbonCreditDetailed<AccountId>>>;

    #[method(name = "eco_getAllReforestProjects")]
    fn get_all_reforest_projects(&self) -> RpcResult<Vec<ReforestProjectDetailed>>;

    #[method(name = "eco_getAllGreenValidatorsDetailed")]
    fn get_all_green_validators_detailed(
        &self,
    ) -> RpcResult<Vec<pallet_eco::GreenValidator<AccountId>>>;
}

pub struct EcoRpcImpl<C> {
    client: Arc<C>,
}

impl<C> EcoRpcImpl<C> {
    pub fn new(client: Arc<C>) -> Self {
        Self { client }
    }
}

impl<C> EcoRpcServer for EcoRpcImpl<C>
where
    C: ProvideRuntimeApi<Block> + HeaderBackend<Block> + 'static,
    C::Api: EcoRuntimeApi<Block>,
{
    fn get_eco_metrics(&self) -> RpcResult<EcoMetrics> {
        let at = self.client.info().best_hash;
        let api = self.client.runtime_api();
        Ok(EcoMetrics {
            total_co2_offset: api.get_total_co2_offset(at).map_err(rpc_err)?,
            total_trees_planted: api.get_total_trees_planted(at).map_err(rpc_err)?,
            total_credits_retired: api.get_total_credits_retired(at).map_err(rpc_err)?,
            carbon_credit_count: api.get_carbon_credit_count(at).map_err(rpc_err)?,
            reforest_project_count: api.get_reforest_project_count(at).map_err(rpc_err)?,
            green_validator_count: api.get_green_validator_count(at).map_err(rpc_err)?,
        })
    }

    fn get_total_co2_offset(&self) -> RpcResult<u64> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_total_co2_offset(at)
            .map_err(rpc_err)
    }

    fn get_total_trees_planted(&self) -> RpcResult<u32> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_total_trees_planted(at)
            .map_err(rpc_err)
    }

    fn get_total_credits_retired(&self) -> RpcResult<u64> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_total_credits_retired(at)
            .map_err(rpc_err)
    }

    fn get_carbon_credit_count(&self) -> RpcResult<u32> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_carbon_credit_count(at)
            .map_err(rpc_err)
    }

    fn get_reforest_project_count(&self) -> RpcResult<u32> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_reforest_project_count(at)
            .map_err(rpc_err)
    }

    fn get_green_validator_count(&self) -> RpcResult<u32> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_green_validator_count(at)
            .map_err(rpc_err)
    }

    fn get_green_score(&self, validator: AccountId) -> RpcResult<Option<u8>> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_green_score(at, validator)
            .map_err(rpc_err)
    }

    fn get_all_green_validators(&self) -> RpcResult<Vec<(AccountId, u8)>> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_all_green_validators(at)
            .map_err(rpc_err)
    }

    fn get_all_carbon_credits(&self) -> RpcResult<Vec<CarbonCreditDetailed<AccountId>>> {
        let at = self.client.info().best_hash;
        let credits = self
            .client
            .runtime_api()
            .get_all_carbon_credits(at)
            .map_err(rpc_err)?;
        let result: Vec<CarbonCreditDetailed<AccountId>> = credits
            .into_iter()
            .map(|c| CarbonCreditDetailed {
                id: String::from_utf8_lossy(&c.id).to_string(),
                project_name: String::from_utf8_lossy(&c.project_name).to_string(),
                tons_co2: c.tons_co2,
                verified: c.verified,
                retired: c.retired,
                owner: c.owner,
                created_at: c.created_at,
            })
            .collect();
        Ok(result)
    }

    fn get_all_reforest_projects(&self) -> RpcResult<Vec<ReforestProjectDetailed>> {
        let at = self.client.info().best_hash;
        let projects = self
            .client
            .runtime_api()
            .get_all_reforest_projects(at)
            .map_err(rpc_err)?;
        let result: Vec<ReforestProjectDetailed> = projects
            .into_iter()
            .map(|p| ReforestProjectDetailed {
                id: String::from_utf8_lossy(&p.id).to_string(),
                name: String::from_utf8_lossy(&p.name).to_string(),
                trees_planted: p.trees_planted,
                location: String::from_utf8_lossy(&p.location).to_string(),
                survival_rate: p.survival_rate,
                verified: p.verified,
            })
            .collect();
        Ok(result)
    }

    fn get_all_green_validators_detailed(
        &self,
    ) -> RpcResult<Vec<pallet_eco::GreenValidator<AccountId>>> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_all_green_validators_detailed(at)
            .map_err(rpc_err)
    }
}

// === TokenomicsApi RPC ===
#[rpc(server)]
pub trait TokenomicsRpc {
    #[method(name = "tokenomics_getTotalSupply")]
    fn get_total_supply(&self) -> RpcResult<Balance>;

    #[method(name = "tokenomics_getCirculatingSupply")]
    fn get_circulating_supply(&self) -> RpcResult<Balance>;

    #[method(name = "tokenomics_getPresalePrice")]
    fn get_presale_price(&self) -> RpcResult<u32>;

    #[method(name = "tokenomics_getPresaleRaised")]
    fn get_presale_raised(&self) -> RpcResult<Balance>;

    #[method(name = "tokenomics_getPresaleSold")]
    fn get_presale_sold(&self) -> RpcResult<Balance>;

    #[method(name = "tokenomics_getTransferFeeBps")]
    fn get_transfer_fee_bps(&self) -> RpcResult<u32>;

    #[method(name = "tokenomics_getGreenTreasuryCollected")]
    fn get_green_treasury_collected(&self) -> RpcResult<Balance>;

    #[method(name = "tokenomics_getDistribution")]
    fn get_distribution(&self) -> RpcResult<Vec<DistributionCategoryDetailed<Balance>>>;

    #[method(name = "tokenomics_getInvestorAllocation")]
    fn get_investor_allocation(&self) -> RpcResult<Balance>;
}

pub struct TokenomicsRpcImpl<C> {
    client: Arc<C>,
}

impl<C> TokenomicsRpcImpl<C> {
    pub fn new(client: Arc<C>) -> Self {
        Self { client }
    }
}

impl<C> TokenomicsRpcServer for TokenomicsRpcImpl<C>
where
    C: ProvideRuntimeApi<Block> + HeaderBackend<Block> + 'static,
    C::Api: TokenomicsRuntimeApi<Block>,
{
    fn get_total_supply(&self) -> RpcResult<Balance> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_total_supply(at)
            .map_err(rpc_err)
    }
    fn get_circulating_supply(&self) -> RpcResult<Balance> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_circulating_supply(at)
            .map_err(rpc_err)
    }
    fn get_presale_price(&self) -> RpcResult<u32> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_presale_price(at)
            .map_err(rpc_err)
    }
    fn get_presale_raised(&self) -> RpcResult<Balance> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_presale_raised(at)
            .map_err(rpc_err)
    }
    fn get_presale_sold(&self) -> RpcResult<Balance> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_presale_sold(at)
            .map_err(rpc_err)
    }
    fn get_transfer_fee_bps(&self) -> RpcResult<u32> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_transfer_fee_bps(at)
            .map_err(rpc_err)
    }
    fn get_green_treasury_collected(&self) -> RpcResult<Balance> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_green_treasury_collected(at)
            .map_err(rpc_err)
    }
    fn get_distribution(&self) -> RpcResult<Vec<DistributionCategoryDetailed<Balance>>> {
        let at = self.client.info().best_hash;
        let cats = self
            .client
            .runtime_api()
            .get_distribution(at)
            .map_err(rpc_err)?;
        Ok(cats
            .into_iter()
            .map(|c| DistributionCategoryDetailed {
                name: String::from_utf8_lossy(&c.name).to_string(),
                amount: c.amount,
                percentage: c.percentage,
                vesting_days: c.vesting_days,
                cliff_days: c.cliff_days,
                released: c.released,
            })
            .collect())
    }
    fn get_investor_allocation(&self) -> RpcResult<Balance> {
        let at = self.client.info().best_hash;
        self.client
            .runtime_api()
            .get_investor_allocation(at)
            .map_err(rpc_err)
    }
}

// === SudoApi RPC ===
use verdis_runtime::SudoApi as SudoRuntimeApi;

#[rpc(server)]
pub trait SudoRpc {
    #[method(name = "sudo_getKey")]
    fn get_key(&self) -> RpcResult<Option<AccountId>>;
}

pub struct SudoRpcImpl<C> {
    client: Arc<C>,
}

impl<C> SudoRpcImpl<C> {
    pub fn new(client: Arc<C>) -> Self {
        Self { client }
    }
}

impl<C> SudoRpcServer for SudoRpcImpl<C>
where
    C: ProvideRuntimeApi<Block> + HeaderBackend<Block> + 'static,
    C::Api: SudoRuntimeApi<Block>,
{
    fn get_key(&self) -> RpcResult<Option<AccountId>> {
        let at = self.client.info().best_hash;
        self.client.runtime_api().get_key(at).map_err(rpc_err)
    }
}

// === ContractsApi RPC ===
use pallet_dpos::Validator;
use pallet_eco::{CarbonCredit, GreenValidator, ReforestProject};
use pallet_tokenomics::DistributionCategory;
use verdis_runtime::ContractsApi as ContractsRuntimeApi;
use verdis_runtime::Hash;
use verdis_runtime::TokenomicsApi as TokenomicsRuntimeApi;

#[rpc(server)]
pub trait ContractsRpc {
    /// Query a storage entry of a contract.
    #[method(name = "contracts_getStorage")]
    fn get_storage(&self, address: AccountId, key: Vec<u8>) -> RpcResult<Option<Vec<u8>>>;

    /// Simulate a call to a contract (read-only, no state change).
    #[method(name = "contracts_call")]
    fn call(
        &self,
        origin: AccountId,
        dest: AccountId,
        value: Balance,
        gas_limit: Option<u64>,
        storage_deposit_limit: Option<Balance>,
        input_data: Vec<u8>,
    ) -> RpcResult<ContractCallResult>;

    /// Instantiate a new contract (read-only simulation).
    #[method(name = "contracts_instantiate")]
    fn instantiate(
        &self,
        origin: AccountId,
        value: Balance,
        gas_limit: Option<u64>,
        storage_deposit_limit: Option<Balance>,
        code_hash: Hash,
        data: Vec<u8>,
        salt: Vec<u8>,
    ) -> RpcResult<ContractInstantiateResult>;
}

/// Simplified contract call result for JSON-RPC.
#[derive(Clone, serde::Serialize, serde::Deserialize)]
pub struct ContractCallResult {
    pub success: bool,
    pub output: Vec<u8>,
    pub gas_consumed: u64,
    pub error: Option<String>,
}

/// Simplified contract instantiate result for JSON-RPC.
#[derive(Clone, serde::Serialize, serde::Deserialize)]
pub struct ContractInstantiateResult {
    pub success: bool,
    pub address: Option<AccountId>,
    pub gas_consumed: u64,
    pub error: Option<String>,
}

pub struct ContractsRpcImpl<C> {
    client: Arc<C>,
}

impl<C> ContractsRpcImpl<C> {
    pub fn new(client: Arc<C>) -> Self {
        Self { client }
    }
}

impl<C> ContractsRpcServer for ContractsRpcImpl<C>
where
    C: ProvideRuntimeApi<Block> + HeaderBackend<Block> + 'static,
    C::Api: ContractsRuntimeApi<Block>,
{
    fn get_storage(&self, address: AccountId, key: Vec<u8>) -> RpcResult<Option<Vec<u8>>> {
        let at = self.client.info().best_hash;
        let result = self
            .client
            .runtime_api()
            .get_storage(at, address, key)
            .map_err(rpc_err)?;
        result.map_err(|e| rpc_err(format!("{:?}", e)))
    }

    fn call(
        &self,
        origin: AccountId,
        dest: AccountId,
        value: Balance,
        gas_limit: Option<u64>,
        storage_deposit_limit: Option<Balance>,
        input_data: Vec<u8>,
    ) -> RpcResult<ContractCallResult> {
        let at = self.client.info().best_hash;
        let weight =
            gas_limit.map(|ref_time| frame_support::weights::Weight::from_parts(ref_time, 0));
        let result = self
            .client
            .runtime_api()
            .call(
                at,
                origin,
                dest,
                value,
                weight,
                storage_deposit_limit,
                input_data,
            )
            .map_err(rpc_err)?;

        match result.result {
            Ok(exec_result) => Ok(ContractCallResult {
                success: !exec_result.did_revert(),
                output: exec_result.data.clone(),
                gas_consumed: result.gas_consumed.ref_time(),
                error: None,
            }),
            Err(err) => Ok(ContractCallResult {
                success: false,
                output: Vec::new(),
                gas_consumed: result.gas_consumed.ref_time(),
                error: Some(format!("{:?}", err)),
            }),
        }
    }

    fn instantiate(
        &self,
        origin: AccountId,
        value: Balance,
        gas_limit: Option<u64>,
        storage_deposit_limit: Option<Balance>,
        code_hash: Hash,
        data: Vec<u8>,
        salt: Vec<u8>,
    ) -> RpcResult<ContractInstantiateResult> {
        let at = self.client.info().best_hash;
        let weight =
            gas_limit.map(|ref_time| frame_support::weights::Weight::from_parts(ref_time, 0));
        let contract_code = verdis_runtime::pallet_contracts::Code::Existing(code_hash);
        let result = self
            .client
            .runtime_api()
            .instantiate(
                at,
                origin,
                value,
                weight,
                storage_deposit_limit,
                contract_code,
                data,
                salt,
            )
            .map_err(rpc_err)?;

        match result.result {
            Ok(instantiate_result) => Ok(ContractInstantiateResult {
                success: !instantiate_result.result.did_revert(),
                address: Some(instantiate_result.account_id.clone()),
                gas_consumed: result.gas_consumed.ref_time(),
                error: None,
            }),
            Err(err) => Ok(ContractInstantiateResult {
                success: false,
                address: None,
                gas_consumed: result.gas_consumed.ref_time(),
                error: Some(format!("{:?}", err)),
            }),
        }
    }
}
// Force rebuild 1787380805
