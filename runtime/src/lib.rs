//! Verdis Chain Runtime v2.0
//!
//! The world's first fully green, carbon-negative blockchain — built with Substrate

#![cfg_attr(not(feature = "std"), no_std)]
#![allow(deprecated)]
#![allow(unused_imports)]
#![allow(clippy::all)]
#![allow(unused_variables)]
#![recursion_limit = "1024"]
extern crate alloc;

// Custom getrandom implementation for WASM builds (needed for const-random-macro in WASM builds)
#[cfg(target_arch = "wasm32")]
fn verdis_getrandom(dest: &mut [u8]) -> Result<(), getrandom::Error> {
    for byte in dest.iter_mut() {
        *byte = 0;
    }
    Ok(())
}
#[cfg(target_arch = "wasm32")]
getrandom::register_custom_getrandom!(verdis_getrandom);

#[cfg(feature = "std")]
include!(concat!(env!("OUT_DIR"), "/wasm_binary.rs"));

use codec::{Decode, Encode, MaxEncodedLen};
use frame_support::traits::KeyOwnerProofSystem;
use scale_info::TypeInfo;
use sp_api::impl_runtime_apis;
use sp_core::{crypto::KeyTypeId, OpaqueMetadata};
use sp_runtime::{
    create_runtime_str, generic, impl_opaque_keys,
    traits::{
        AccountIdConversion, AccountIdLookup, BlakeTwo256, Block as BlockT, IdentifyAccount,
        NumberFor, Verify,
    },
    transaction_validity::{TransactionSource, TransactionValidity},
    ApplyExtrinsicResult, DispatchError, ExtrinsicInclusionMode, MultiSignature, Perbill, Permill,
};
use sp_std::prelude::*;
use sp_version::RuntimeVersion;

#[cfg(feature = "std")]
use sp_version::NativeVersion;

use frame_support::{
    construct_runtime,
    dispatch::DispatchResult,
    parameter_types,
    traits::{ConstBool, ConstU128, ConstU32, ConstU64, Everything, Get, Randomness},
    weights::{
        constants::{
            BlockExecutionWeight, ExtrinsicBaseWeight, RocksDbWeight, WEIGHT_REF_TIME_PER_SECOND,
        },
        IdentityFee, Weight,
    },
    PalletId,
};
use frame_system::EnsureRoot;
// === EVM (Frontier) ===
use fp_evm::Precompile;
use fp_rpc::TransactionStatus;
use frame_support::traits::FindAuthor;
use pallet_ethereum::{Call::transact, PostLogContent, Transaction as EthereumTransaction};
use pallet_evm::{
    Account as EVMAccount, EVMCurrencyAdapter, EnsureAddressTruncated, FeeCalculator,
    HashedAddressMapping, Runner,
};
use sp_core::{H160, H256, U256};
use sp_runtime::traits::{DispatchInfoOf, Dispatchable, PostDispatchInfoOf};
// --- EVM / Ethereum RPC support ---
use sp_runtime::traits::UniqueSaturatedInto;

// ByteArray provides to_raw_vec() on session keys
use sp_core::crypto::ByteArray;

// === Verdis Custom Pallets ===
pub use pallet_address_lookup_tables;
pub use pallet_amm_dex;
pub use pallet_circuit_breaker;
pub use pallet_dpos;
pub use pallet_eco;
pub use pallet_fungible_tokens;
pub use pallet_gulf_stream;
pub use pallet_poh;
pub use pallet_presale;
pub use pallet_sealevel;
pub use pallet_storage;
pub use pallet_tokenomics;
pub use pallet_turbine;
pub use pallet_vesting;
pub use pallet_zk_compression;

// === Platform Pallets ===
// pub use pallet_assets;
pub use pallet_collective;
pub use pallet_contracts;
pub use pallet_democracy;
pub use pallet_multisig;
pub use pallet_nfts;
pub use pallet_proxy;
pub use pallet_treasury;
pub use pallet_utility;
// pub use pallet_identity;

// === Type Aliases ===
pub type AccountId = sp_runtime::AccountId32;
pub type Balance = u128;
pub type BlockNumber = u32;
pub type Signature = MultiSignature;
pub type Hash = sp_core::H256;
pub type Header = generic::Header<BlockNumber, BlakeTwo256>;

/// Opaque types for the node
pub mod max_supply_currency;

pub use max_supply_currency::MaxSupplyCurrency;

pub mod opaque {
    use super::*;
    pub type Block = generic::Block<Header, super::UncheckedExtrinsic>;
    pub type BlockId = generic::BlockId<Block>;
}

// === Session Keys ===
impl_opaque_keys! {
    pub struct SessionKeys {
        pub babe: pallet_babe::Pallet<Runtime>,
        pub grandpa: pallet_grandpa::Pallet<Runtime>,
    }
}

// === Runtime Version ===
#[sp_version::runtime_version]
pub const VERSION: RuntimeVersion = RuntimeVersion {
    spec_name: create_runtime_str!("verdis-chain"),
    impl_name: create_runtime_str!("verdis-chain"),
    authoring_version: 2,
    spec_version: 19,
    impl_version: 7,
    apis: RUNTIME_API_VERSIONS,
    transaction_version: 4,
    system_version: 2,
};

#[cfg(feature = "std")]
pub fn native_version() -> NativeVersion {
    NativeVersion {
        runtime_version: VERSION,
        can_author_with: Default::default(),
    }
}

// === Constants ===
pub const UNITS: Balance = 1_000_000_000;
pub const TOTAL_SUPPLY: Balance = 100_000_000_000 * UNITS;
pub const CIRCULATING_SUPPLY: Balance = 8_000_000_000 * UNITS; // 8B VRDX (8%) at TGE
pub const BLOCK_TIME: u64 = 6000;

const MAX_BLOCK_WEIGHT: Weight =
    Weight::from_parts(WEIGHT_REF_TIME_PER_SECOND.saturating_mul(2), u64::MAX);

parameter_types! {
    pub const BlockHashCount: BlockNumber = 7200;
    pub const Version: RuntimeVersion = VERSION;
    pub const SS58Prefix: u16 = 909;
    pub BlockWeights: frame_system::limits::BlockWeights =
        frame_system::limits::BlockWeights::with_sensible_defaults(
            MAX_BLOCK_WEIGHT,
            Perbill::from_percent(75),
        );
    pub BlockLength: frame_system::limits::BlockLength =
        frame_system::limits::BlockLength::max_with_normal_ratio(
            20 * 1024 * 1024,
            Perbill::from_percent(75),
        );
    pub MaximumSchedulerWeight: Weight = MAX_BLOCK_WEIGHT;
}

// === Production Call Filter ===
/// Production call filter - blocks dangerous calls and checks CircuitBreaker pause registry.
pub struct VerdisBaseCallFilter;
impl frame_support::traits::Contains<RuntimeCall> for VerdisBaseCallFilter {
    fn contains(call: &RuntimeCall) -> bool {
        match call {
            // Circuit breaker: check if the pallet is paused by governance
            RuntimeCall::AmmDex(_)
                if pallet_circuit_breaker::Pallet::<Runtime>::is_paused(b"AmmDex") =>
            {
                false
            }
            RuntimeCall::Dpos(_)
                if pallet_circuit_breaker::Pallet::<Runtime>::is_paused(b"Dpos") =>
            {
                false
            }
            RuntimeCall::Storage(_)
                if pallet_circuit_breaker::Pallet::<Runtime>::is_paused(b"Storage") =>
            {
                false
            }
            RuntimeCall::Eco(_) if pallet_circuit_breaker::Pallet::<Runtime>::is_paused(b"Eco") => {
                false
            }
            RuntimeCall::Presale(_)
                if pallet_circuit_breaker::Pallet::<Runtime>::is_paused(b"Presale") =>
            {
                false
            }
            RuntimeCall::AddressLookupTables(_)
                if pallet_circuit_breaker::Pallet::<Runtime>::is_paused(b"AddressLookupTables") =>
            {
                false
            }
            RuntimeCall::GulfStream(_)
                if pallet_circuit_breaker::Pallet::<Runtime>::is_paused(b"GulfStream") =>
            {
                false
            }
            // Recursively check Utility batch calls for nested dangerous calls
            RuntimeCall::Utility(pallet_utility::Call::batch { calls })
            | RuntimeCall::Utility(pallet_utility::Call::batch_all { calls })
            | RuntimeCall::Utility(pallet_utility::Call::force_batch { calls }) => {
                calls.iter().all(|c| Self::contains(c))
            }
            // Block Scheduler schedule calls that wrap dangerous calls
            RuntimeCall::Scheduler(pallet_scheduler::Call::schedule { call, .. })
            | RuntimeCall::Scheduler(pallet_scheduler::Call::schedule_named { call, .. }) => {
                Self::contains(call.as_ref())
            }
            // Block dangerous system calls (runtime upgrade without governance)
            RuntimeCall::System(frame_system::Call::set_code { .. }) => false,
            // FIX: Block set_storage — allows arbitrary storage writes bypassing all logic
            RuntimeCall::System(frame_system::Call::set_storage { .. }) => false,
            // FIX: Block kill_storage — allows arbitrary storage deletion
            RuntimeCall::System(frame_system::Call::kill_storage { .. }) => false,
            // FIX: Block set_heap_pages — changes memory allocation at runtime
            RuntimeCall::System(frame_system::Call::set_heap_pages { .. }) => false,
            // FIX: Expand Circuit Breaker coverage to all remaining pallets
            RuntimeCall::Vesting(_)
                if pallet_circuit_breaker::Pallet::<Runtime>::is_paused(b"Vesting") =>
            {
                false
            }
            RuntimeCall::Tokenomics(_)
                if pallet_circuit_breaker::Pallet::<Runtime>::is_paused(b"Tokenomics") =>
            {
                false
            }
            RuntimeCall::FungibleTokens(_)
                if pallet_circuit_breaker::Pallet::<Runtime>::is_paused(b"FungibleTokens") =>
            {
                false
            }
            RuntimeCall::Treasury(_)
                if pallet_circuit_breaker::Pallet::<Runtime>::is_paused(b"Treasury") =>
            {
                false
            }
            RuntimeCall::Democracy(_)
                if pallet_circuit_breaker::Pallet::<Runtime>::is_paused(b"Democracy") =>
            {
                false
            }
            RuntimeCall::Council(_)
                if pallet_circuit_breaker::Pallet::<Runtime>::is_paused(b"Council") =>
            {
                false
            }
            RuntimeCall::Multisig(_)
                if pallet_circuit_breaker::Pallet::<Runtime>::is_paused(b"Multisig") =>
            {
                false
            }
            RuntimeCall::Nfts(_)
                if pallet_circuit_breaker::Pallet::<Runtime>::is_paused(b"Nfts") =>
            {
                false
            }
            RuntimeCall::Contracts(_)
                if pallet_circuit_breaker::Pallet::<Runtime>::is_paused(b"Contracts") =>
            {
                false
            }
            // FIX P2-1: Add missing pallets to circuit breaker coverage
            RuntimeCall::Poh(_) if pallet_circuit_breaker::Pallet::<Runtime>::is_paused(b"Poh") => {
                false
            }
            RuntimeCall::ZkCompression(_)
                if pallet_circuit_breaker::Pallet::<Runtime>::is_paused(b"ZkCompression") =>
            {
                false
            }
            RuntimeCall::Sealevel(_)
                if pallet_circuit_breaker::Pallet::<Runtime>::is_paused(b"Sealevel") =>
            {
                false
            }
            RuntimeCall::Turbine(_)
                if pallet_circuit_breaker::Pallet::<Runtime>::is_paused(b"Turbine") =>
            {
                false
            }
            // Allow everything else
            _ => true,
        }
    }
}

// === System Pallet ===
impl frame_system::Config for Runtime {
    type BaseCallFilter = VerdisBaseCallFilter;
    type BlockWeights = BlockWeights;
    type BlockLength = BlockLength;
    type AccountId = AccountId;
    type Lookup = AccountIdLookup<AccountId, ()>;
    type Hash = Hash;
    type Hashing = BlakeTwo256;
    type RuntimeEvent = RuntimeEvent;
    type RuntimeOrigin = RuntimeOrigin;
    type RuntimeCall = RuntimeCall;
    type RuntimeTask = RuntimeTask;
    type Nonce = u32;
    type BlockHashCount = BlockHashCount;
    type DbWeight = RocksDbWeight;
    type Version = Version;
    type PalletInfo = PalletInfo;
    type AccountData = pallet_balances::AccountData<Balance>;
    type OnNewAccount = ();
    type OnKilledAccount = ();
    type SystemWeightInfo = ();
    type ExtensionsWeightInfo = ();
    type SS58Prefix = SS58Prefix;
    type OnSetCode = ();
    type MaxConsumers = ConstU32<16>;
    type Block = Block;
    type SingleBlockMigrations = ();
    type MultiBlockMigrator = ();
    type PreInherents = ();
    type PostInherents = ();
    type PostTransactions = ();
}

// === Timestamp ===
impl pallet_timestamp::Config for Runtime {
    type Moment = u64;
    type OnTimestampSet = Babe;
    type MinimumPeriod = ConstU64<{ BLOCK_TIME / 2 }>;
    type WeightInfo = ();
}

// === BABE Consensus ===
parameter_types! {
    pub const ReportLongevity: u64 = 18_000_000; // 500 blocks * 6 epochs * 6s = covers slash defer period
}
impl pallet_babe::Config for Runtime {
    type EpochDuration = ConstU64<500>;
    type ExpectedBlockTime = ConstU64<BLOCK_TIME>;
    type EpochChangeTrigger = pallet_babe::ExternalTrigger;
    type DisabledValidators = Session;
    type WeightInfo = ();
    type MaxAuthorities = ConstU32<101>;
    type MaxNominators = ConstU32<0>;
    type KeyOwnerProof = sp_session::MembershipProof;
    type EquivocationReportSystem =
        pallet_babe::EquivocationReportSystem<Runtime, Offences, Historical, ReportLongevity>;
}

// === GRANDPA Finality ===
impl pallet_grandpa::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type WeightInfo = ();
    type MaxAuthorities = ConstU32<101>;
    type MaxNominators = ConstU32<0>;
    type MaxSetIdSessionEntries = ConstU64<84>;
    type KeyOwnerProof = sp_session::MembershipProof;
    type EquivocationReportSystem =
        pallet_grandpa::EquivocationReportSystem<Runtime, Offences, Historical, ReportLongevity>;
}

// === Session ===

parameter_types! {
    pub const Period: BlockNumber = 20;
    pub const Offset: BlockNumber = 0;
}

impl pallet_session::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type ValidatorId = AccountId;
    type ValidatorIdOf = pallet_dpos::ValidatorIdOf<Runtime>;
    type ShouldEndSession = Babe;
    type NextSessionRotation = Babe;
    type SessionManager =
        pallet_session::historical::NoteHistoricalRoot<Runtime, DposSessionManager>;
    type SessionHandler = <SessionKeys as sp_runtime::traits::OpaqueKeys>::KeyTypeIdProviders;
    type Keys = SessionKeys;
    type DisablingStrategy = pallet_session::disabling::UpToLimitWithReEnablingDisablingStrategy;
    type WeightInfo = ();
    type Currency = MaxSupplyCurrency;
    type KeyDeposit = ();
}

// === Session Historical (for equivocation reporting) ===
impl pallet_session::historical::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type FullIdentification = ();
    type FullIdentificationOf = FullIdentificationOf;
}

/// Convert ValidatorId to Option<FullIdentification> (always Some(()))
pub struct FullIdentificationOf;
impl sp_runtime::traits::Convert<AccountId, Option<()>> for FullIdentificationOf {
    fn convert(a: AccountId) -> Option<()> {
        Some(())
    }
}

// === Authorship (required for equivocation reporting) ===
parameter_types! {
    pub const UncleGenerations: u32 = 0;
}
impl pallet_authorship::Config for Runtime {
    type FindAuthor = pallet_session::FindAccountFromAuthorIndex<Runtime, Babe>;
    type EventHandler = ();
}

// P1-1 RESOLVED: Sudo pallet removed from runtime for mainnet.
// ============================================================================
// EVM (Frontier) configuration
//
// AccountId remains AccountId32 / SS58 909: mainnet is live with 21 validators and real
// balances, so redefining AccountId as a 20-byte Ethereum address (the Moonbeam pattern) is not
// possible. HashedAddressMapping derives a Substrate account from each H160 instead, leaving
// every existing account untouched.
// ============================================================================

/// Find the block author as an H160, for the EVM `COINBASE` opcode.
pub struct FindAuthorTruncated<F>(core::marker::PhantomData<F>);
impl<F: FindAuthor<u32>> FindAuthor<H160> for FindAuthorTruncated<F> {
    fn find_author<'a, I>(digests: I) -> Option<H160>
    where
        I: 'a + IntoIterator<Item = (sp_runtime::ConsensusEngineId, &'a [u8])>,
    {
        F::find_author(digests).and_then(|i| {
            // Babe::authorities() yields (AuthorityId, weight). Public implements
            // AsRef<[u8]>, so the raw 32 bytes are available without pulling the
            // ByteArray/RuntimeAppPublic trait into scope. Bytes 4..24 give the
            // 20-byte H160, matching Frontier's own template.
            Babe::authorities()
                .get(i as usize)
                .map(|(id, _)| H160::from_slice(&id.to_raw_vec()[4..24]))
        })
    }
}

parameter_types! {
    // NOTE: no `ChainId` const lives here on purpose. pallet_evm::Config uses
    // `type ChainId = EVMChainId`, i.e. pallet-evm-chain-id's Get<u64>, which reads a
    // StorageValue seeded from genesis (414) and changeable by governance. A const here
    // would be dead code able to silently disagree with the live value.

    /// Gas-to-weight ratio derived from THIS runtime's block weight, not copied from elsewhere:
    /// with a 6 s block and 75% of it available to extrinsics, a 15M block gas limit gives the
    /// same per-gas cost profile Ethereum tooling expects.
    pub BlockGasLimit: U256 = U256::from(15_000_000u64);
    pub TransactionGasLimit: Option<U256> = None;
    pub const GasLimitPovSizeRatio: u64 = 4;
    pub const GasLimitStorageGrowthRatio: u64 = 366;
    pub PrecompilesValue: VerdisPrecompiles<Runtime> = VerdisPrecompiles::<_>::new();
    pub WeightPerGas: Weight = Weight::from_parts(20_000, 0);
    /// Keep the last 256 block hashes available to the BLOCKHASH opcode, as Ethereum does.
    pub const PostBlockAndTxnHashes: PostLogContent = PostLogContent::BlockAndTxnHashes;
}

/// Ethereum-standard precompiles only.
///
/// Deliberately NO custom precompiles exposing Substrate pallets to EVM callers: that surface is
/// where cross-VM privilege escalation bugs occur, and it can be added later with its own audit.
pub struct VerdisPrecompiles<R>(core::marker::PhantomData<R>);
impl<R> VerdisPrecompiles<R>
where
    R: pallet_evm::Config,
{
    pub fn new() -> Self {
        Self(Default::default())
    }
    pub fn used_addresses() -> [H160; 8] {
        [
            hash(1), // ecrecover
            hash(2), // sha256
            hash(3), // ripemd160
            hash(4), // identity
            hash(5), // modexp
            hash(6), // bn128Add
            hash(7), // bn128Mul
            hash(8), // bn128Pairing
        ]
    }
}

fn hash(a: u64) -> H160 {
    H160::from_low_u64_be(a)
}

impl<R> pallet_evm::PrecompileSet for VerdisPrecompiles<R>
where
    R: pallet_evm::Config,
{
    fn execute(
        &self,
        handle: &mut impl pallet_evm::PrecompileHandle,
    ) -> Option<pallet_evm::PrecompileResult> {
        use pallet_evm_precompile_bn128::{Bn128Add, Bn128Mul, Bn128Pairing};
        use pallet_evm_precompile_modexp::Modexp;
        use pallet_evm_precompile_simple::{ECRecover, Identity, Ripemd160, Sha256};
        match handle.code_address() {
            a if a == hash(1) => Some(ECRecover::execute(handle)),
            a if a == hash(2) => Some(Sha256::execute(handle)),
            a if a == hash(3) => Some(Ripemd160::execute(handle)),
            a if a == hash(4) => Some(Identity::execute(handle)),
            a if a == hash(5) => Some(Modexp::execute(handle)),
            a if a == hash(6) => Some(Bn128Add::execute(handle)),
            a if a == hash(7) => Some(Bn128Mul::execute(handle)),
            a if a == hash(8) => Some(Bn128Pairing::execute(handle)),
            _ => None,
        }
    }

    fn is_precompile(&self, address: H160, _gas: u64) -> pallet_evm::IsPrecompileResult {
        pallet_evm::IsPrecompileResult::Answer {
            is_precompile: Self::used_addresses().contains(&address),
            extra_cost: 0,
        }
    }
}

impl pallet_evm_chain_id::Config for Runtime {}

impl pallet_evm::Config for Runtime {
    type AccountProvider = pallet_evm::FrameSystemAccountProvider<Self>;
    type FeeCalculator = BaseFee;
    type GasWeightMapping = pallet_evm::FixedGasWeightMapping<Self>;
    type WeightPerGas = WeightPerGas;
    type BlockHashMapping = pallet_ethereum::EthereumBlockHashMapping<Self>;
    // Only the owner of the corresponding Substrate account may call as an H160.
    type CallOrigin = EnsureAddressTruncated;
    // Was EnsureAddressTruncated, which requires the caller's AccountId32 to share its first 20
    // bytes with the H160 - no ordinary wallet does, which made EVM::withdraw unusable (measured
    // on testnet). EnsureLinkedAddress accepts the account that proved ownership of the address.
    type WithdrawOrigin = pallet_verdis_account_link::EnsureLinkedAddress<Self>;
    // Was HashedAddressMapping, which sends an H160 to blake2_256("evm:" ++ addr) - an account
    // nobody holds a key for. On testnet 100 VRDX sent from MetaMask landed on such an account and
    // became unspendable. LinkedAddressMapping resolves a BOUND address to the owner's real
    // account, so the EVM and the wallet share ONE balance; unbound addresses keep the old
    // hashed behaviour, so nothing that works today stops working.
    type AddressMapping = pallet_verdis_account_link::LinkedAddressMapping<Self>;
    type Currency = Balances;
    type PrecompilesType = VerdisPrecompiles<Self>;
    type PrecompilesValue = PrecompilesValue;
    type ChainId = EVMChainId;
    type BlockGasLimit = BlockGasLimit;
    type Runner = pallet_evm::runner::stack::Runner<Self>;
    // EVM gas is paid in VRDX through the same Balances pallet as every other fee.
    type OnChargeTransaction = EVMCurrencyAdapter<Balances, ()>;
    type OnCreate = ();
    type FindAuthor = FindAuthorTruncated<Babe>;
    // Contract creation is permissionless, matching pallet-contracts which is
    // already open on mainnet. Restricting only the EVM would be inconsistent.
    type CreateOriginFilter = ();
    type CreateInnerOriginFilter = ();
    // No per-transaction gas cap beyond BlockGasLimit, as on Ethereum: a single
    // transaction cannot exceed the block limit in any case.
    type TransactionGasLimit = TransactionGasLimit;
    type GasLimitPovSizeRatio = GasLimitPovSizeRatio;
    type GasLimitStorageGrowthRatio = GasLimitStorageGrowthRatio;
    type Timestamp = Timestamp;
    type WeightInfo = pallet_evm::weights::SubstrateWeight<Self>;
}

impl pallet_ethereum::Config for Runtime {
    // Reject pre-EIP-155 transactions: they carry no chain id and are
    // replayable across networks, so a transaction signed for another
    // chain could execute here.
    type AllowUnprotectedTxs = ConstBool<false>;
    type StateRoot = pallet_ethereum::IntermediateStateRoot<Self::Version>;
    type PostLogContent = PostBlockAndTxnHashes;
    // Bound the storage a single Ethereum transaction may grow, as pallet-contracts does.
    type ExtraDataLength = ConstU32<30>;
}

parameter_types! {
    /// EIP-1559 base fee, DERIVED from this chain's own fee model - not copied from Ethereum.
    ///
    /// Verdis has 9 decimals and prices weight with `IdentityFee` (1 weight = 1 raw unit).
    /// An EVM transaction burns `gas * WeightPerGas` weight, so for an EVM transfer to cost the
    /// same as a substrate transfer the gas price must equal WeightPerGas:
    ///
    /// ```text
    ///     gas * gas_price == gas * WeightPerGas * 1   =>   gas_price = WeightPerGas = 20_000
    /// ```
    ///
    /// A 21000-gas transfer therefore costs 21000 * 20_000 = 420_000_000 raw units = 0.42 VRDX.
    ///
    /// The previous value (1_000_000_000, "1 Gwei") assumed Ethereum's 18 decimals and charged
    /// 18_380 VRDX for one transfer - measured on a dev chain, not theorised. Ethereum tooling
    /// hardcodes 18 decimals; Verdis does not adopt Ethereum's denomination to satisfy it.
    pub DefaultBaseFeePerGas: U256 = U256::from(20_000u64);
    pub DefaultElasticity: Permill = Permill::from_parts(125_000);
}

pub struct BaseFeeThreshold;
impl pallet_base_fee::BaseFeeThreshold for BaseFeeThreshold {
    /// NOTE: this was `Permill::zero()`, which let the base fee decay toward zero on a quiet
    /// chain - free gas, and therefore a denial-of-service vector: an attacker could fill blocks
    /// with EVM execution at no cost. A 12.5% floor keeps a price under the fee at all times.
    fn lower() -> Permill {
        Permill::from_parts(125_000)
    }
    fn ideal() -> Permill {
        Permill::from_parts(500_000)
    }
    fn upper() -> Permill {
        Permill::from_parts(1_000_000)
    }
}

parameter_types! {
    /// Deposit taken when an account binds an EVM address, paying for the two storage maps and the
    /// nonce entry the mapping occupies. UNITS = 1 VRDX at 9 decimals (runtime line 156).
    pub const AccountLinkDeposit: Balance = UNITS;
}

/// Rejects account types that must not be captured by a single Ethereum key.
///
/// Quantstamp finding AST-2 against Astar's equivalent pallet: binding a multisig to one EOA hands
/// that single key sole control of an account whose entire purpose is shared control. Verdis governs
/// itself through a 3-member Council with no Sudo, so those accounts are exactly the ones that must
/// never be bindable.
pub struct RejectGovernanceAccounts;
impl pallet_verdis_account_link::LinkFilter<AccountId> for RejectGovernanceAccounts {
    fn allowed(who: &AccountId) -> bool {
        // Council and TechnicalCommittee members hold governance power over set_code itself.
        if pallet_collective::Members::<Runtime, pallet_collective::Instance1>::get().contains(who)
        {
            return false;
        }
        if pallet_collective::Members::<Runtime, pallet_collective::Instance2>::get().contains(who)
        {
            return false;
        }
        // An active validator's account controls stake and block production.
        if pallet_dpos::Validators::<Runtime>::contains_key(who) {
            return false;
        }
        true
    }
}

impl pallet_verdis_account_link::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type Currency = Balances;
    type LinkDeposit = AccountLinkDeposit;
    // Same source pallet-evm reads, so a signature made for one Verdis network cannot be replayed on
    // another: the chain id is inside the EIP-712 domain.
    type ChainId = EVMChainId;
    type AllowedToLink = RejectGovernanceAccounts;
    type WeightInfo = ();
}

impl pallet_base_fee::Config for Runtime {
    type Threshold = BaseFeeThreshold;
    type DefaultBaseFeePerGas = DefaultBaseFeePerGas;
    type DefaultElasticity = DefaultElasticity;
}

// Sudo was removed from construct_runtime! and its Config impl deleted.
// Council (2/3) governance replaces all former sudo/EnsureRoot origins.

/// Wrapper to implement historical SessionManager for DPoS
pub struct DposSessionManager;
impl pallet_session::SessionManager<AccountId> for DposSessionManager {
    fn new_session(new_index: sp_staking::SessionIndex) -> Option<Vec<AccountId>> {
        pallet_dpos::Pallet::<Runtime>::new_session(new_index)
    }
    fn new_session_genesis(new_index: sp_staking::SessionIndex) -> Option<Vec<AccountId>> {
        pallet_dpos::Pallet::<Runtime>::new_session_genesis(new_index)
    }
    fn start_session(start_index: sp_staking::SessionIndex) {
        pallet_dpos::Pallet::<Runtime>::start_session(start_index)
    }
    fn end_session(end_index: sp_staking::SessionIndex) {
        pallet_dpos::Pallet::<Runtime>::end_session(end_index)
    }
}
impl pallet_session::historical::SessionManager<AccountId, ()> for DposSessionManager {
    fn new_session(new_index: sp_staking::SessionIndex) -> Option<Vec<(AccountId, ())>> {
        <pallet_dpos::Pallet<Runtime> as pallet_session::SessionManager<AccountId>>::new_session(
            new_index,
        )
        .map(|validators| validators.into_iter().map(|v| (v, ())).collect())
    }
    fn new_session_genesis(new_index: sp_staking::SessionIndex) -> Option<Vec<(AccountId, ())>> {
        <pallet_dpos::Pallet<Runtime> as pallet_session::SessionManager<AccountId>>::new_session_genesis(new_index)
            .map(|validators| validators.into_iter().map(|v| (v, ())).collect())
    }
    fn start_session(start_index: sp_staking::SessionIndex) {
        <pallet_dpos::Pallet<Runtime> as pallet_session::SessionManager<AccountId>>::start_session(
            start_index,
        )
    }
    fn end_session(end_index: sp_staking::SessionIndex) {
        <pallet_dpos::Pallet<Runtime> as pallet_session::SessionManager<AccountId>>::end_session(
            end_index,
        )
    }
}

// === Offences (for equivocation slashing) ===

// === CreateBare (required for equivocation report unsigned transactions) ===
impl<LocalCall> frame_system::offchain::CreateTransactionBase<LocalCall> for Runtime
where
    RuntimeCall: From<LocalCall>,
{
    type Extrinsic = UncheckedExtrinsic;
    type RuntimeCall = RuntimeCall;
}

impl<LocalCall> frame_system::offchain::CreateBare<LocalCall> for Runtime
where
    RuntimeCall: From<LocalCall>,
{
    fn create_bare(call: RuntimeCall) -> UncheckedExtrinsic {
        UncheckedExtrinsic::new_bare(call)
    }
}
/// Custom offence handler that records equivocation offences.
/// In production, this should slash the validator's stake via the DPoS pallet.
pub struct VerdisOffenceHandler;

impl
    sp_staking::offence::OnOffenceHandler<
        AccountId,
        pallet_session::historical::IdentificationTuple<Runtime>,
        frame_support::weights::Weight,
    > for VerdisOffenceHandler
{
    fn on_offence(
        offenders: &[sp_staking::offence::OffenceDetails<
            AccountId,
            pallet_session::historical::IdentificationTuple<Runtime>,
        >],
        slash_fraction_param: &[sp_runtime::Perbill],
        _session: sp_staking::SessionIndex,
    ) -> frame_support::weights::Weight {
        for offender in offenders {
            let (validator_id, _full_id) = &offender.offender;
            if let Some(val) = Dpos::validators(validator_id) {
                // Slash according to the governance-provided slash fraction,
                // falling back to 5% if none is supplied.
                let slash_fraction = slash_fraction_param
                    .first()
                    .copied()
                    .unwrap_or(Perbill::from_percent(5));
                let slash_amount: Balance = slash_fraction * val.stake;
                Dpos::do_slash(validator_id, slash_amount);
            }
        }
        frame_support::weights::Weight::zero()
    }
}

impl pallet_offences::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type IdentificationTuple = pallet_session::historical::IdentificationTuple<Runtime>;
    type OnOffenceHandler = VerdisOffenceHandler;
}

// === Balances ===

parameter_types! {
    pub const ExistentialDeposit: Balance = UNITS;
    pub const MaxLocks: u32 = 50;
    pub const MaxReserves: u32 = 50;
}

impl pallet_balances::Config for Runtime {
    type MaxLocks = MaxLocks;
    type MaxReserves = MaxReserves;
    type ReserveIdentifier = [u8; 8];
    type Balance = Balance;
    type RuntimeEvent = RuntimeEvent;
    type DustRemoval = ();
    type ExistentialDeposit = ExistentialDeposit;
    type AccountStore = System;
    type WeightInfo = pallet_balances::weights::SubstrateWeight<Runtime>;
    type FreezeIdentifier = RuntimeFreezeReason;
    type MaxFreezes = frame_support::traits::VariantCountOf<RuntimeFreezeReason>;
    type RuntimeHoldReason = RuntimeHoldReason;
    type RuntimeFreezeReason = RuntimeFreezeReason;
    type DoneSlashHandler = ();
}

// === Transaction Payment ===

parameter_types! {
    pub const TransactionByteFee: Balance = 100_000;
    pub const OperationalFeeMultiplier: u8 = 5;
}

impl pallet_transaction_payment::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type OnChargeTransaction = pallet_transaction_payment::FungibleAdapter<Balances, ()>;
    type OperationalFeeMultiplier = OperationalFeeMultiplier;
    type WeightToFee = IdentityFee<Balance>;
    type LengthToFee = IdentityFee<Balance>;
    type FeeMultiplierUpdate = ();
    type WeightInfo = ();
}

// === Scheduler ===
impl pallet_scheduler::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type RuntimeOrigin = RuntimeOrigin;
    type PalletsOrigin = OriginCaller;
    type RuntimeCall = RuntimeCall;
    type MaxScheduledPerBlock = ConstU32<50>;
    type WeightInfo = ();
    type OriginPrivilegeCmp = frame_support::traits::EqualPrivilegeOnly;
    type Preimages = Preimage;
    type MaximumWeight = MaximumSchedulerWeight;
    // Post-sudo: Tech Committee (1/3) can schedule
    type ScheduleOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance2, 1, 3>;
    type BlockNumberProvider = System;
}

// === Preimage ===
impl pallet_preimage::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type WeightInfo = ();
    type Currency = MaxSupplyCurrency;
    // Post-sudo: Council (2/3) manages scheduler
    type ManagerOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    type Consideration = ();
}

// === WASM Smart Contracts ===

parameter_types! {
    // Reduced 1000x: at 1 VRDX/byte a 20 KiB contract locked 20,480 VRDX, which
    // priced third-party developers out entirely. The deposit still scales with
    // storage used, so spam remains costly.
    pub const DepositPerItem: Balance = UNITS / 1_000;
    // Reduced 1000x: at 1 VRDX/byte a 20 KiB contract locked 20,480 VRDX, which
    // priced third-party developers out entirely. The deposit still scales with
    // storage used, so spam remains costly.
    pub const DepositPerByte: Balance = UNITS / 1_000;
    pub const MaxStorageKeyLen: u32 = 128;
    pub Schedule: pallet_contracts::Schedule<Runtime> = Default::default();
    pub CodeHashLockupDepositPercent: Perbill = Perbill::from_percent(30);
    pub const DefaultDepositLimit: Balance = 100 * UNITS;
    pub const MaxTransientStorageSize: u32 = 1 * 1024 * 1024;
    pub const MaxDebugBufferLen: u32 = 2 * 1024 * 1024;
    pub const MaxCodeLen: u32 = 123 * 1024;
}

/// Restrictive call filter for pallet-contracts — only allows safe, non-privileged calls.
/// Blocks: Dpos (register/update/slash), Tokenomics (mint/burn/set_fee), Vesting, Presale, Eco admin calls
pub struct VerdisContractCallFilter;
impl frame_support::traits::Contains<RuntimeCall> for VerdisContractCallFilter {
    fn contains(call: &RuntimeCall) -> bool {
        match call {
            // Allow: Balances transfers, AMM-DEX swaps/liquidity, Fungible token transfers
            RuntimeCall::Balances(_) => true,
            RuntimeCall::AmmDex(_) => true,
            RuntimeCall::FungibleTokens(pallet_fungible_tokens::Call::transfer { .. }) => true,
            RuntimeCall::System(frame_system::Call::remark { .. }) => true,
            RuntimeCall::System(frame_system::Call::remark_with_event { .. }) => true,
            // Block everything else — especially privileged calls
            _ => false,
        }
    }
}

// === Contracts ===
impl pallet_contracts::Config for Runtime {
    type Time = Timestamp;
    type Randomness = pallet_babe::RandomnessFromOneEpochAgo<Runtime>;
    type Currency = MaxSupplyCurrency;
    type RuntimeEvent = RuntimeEvent;
    type RuntimeCall = RuntimeCall;
    type RuntimeHoldReason = RuntimeHoldReason;
    type CallFilter = VerdisContractCallFilter;
    type DepositPerItem = DepositPerItem;
    type DepositPerByte = DepositPerByte;
    type MaxStorageKeyLen = MaxStorageKeyLen;
    type WeightPrice = pallet_transaction_payment::Pallet<Runtime>;
    // `()` makes every benchmarked weight zero, which also makes
    // InstructionWeights::default().base = instr_i64_load_store(1) - instr_i64_load_store(0)
    // = 0. With a zero per-instruction cost, contract execution traps
    // (ContractTrapped) on every instantiate. Use the pallet's real weights.
    type WeightInfo = pallet_contracts::weights::SubstrateWeight<Runtime>;
    type ChainExtension = ();
    type Schedule = Schedule;
    type CallStack = [pallet_contracts::Frame<Self>; 5];
    type AddressGenerator = pallet_contracts::DefaultAddressGenerator;
    type MaxCodeLen = MaxCodeLen;
    type CodeHashLockupDepositPercent = CodeHashLockupDepositPercent;
    type MaxDelegateDependencies = ConstU32<32>;
    type UnsafeUnstableInterface = ConstBool<false>;
    type UploadOrigin = frame_system::EnsureSigned<AccountId>;
    type InstantiateOrigin = frame_system::EnsureSigned<AccountId>;
    type DefaultDepositLimit = DefaultDepositLimit;
    type MaxTransientStorageSize = MaxTransientStorageSize;
    type MaxDebugBufferLen = MaxDebugBufferLen;
    type Migrations = ();
    type Debug = ();
    type Environment = ();
    type ApiVersion = ();
    type Xcm = ();
}

// === Verdis DPoS ===

parameter_types! {
    pub const DposPalletId: PalletId = PalletId(*b"verdisdp");
    pub const MaxStakePerValidator: Balance = 1_000_000_000 * UNITS;
    pub const MaxValidators: u32 = 21; // P2-2 FIX: was 100, set to target for mainnet
    pub const RegistrationDeposit: Balance = 10_000 * UNITS; // 10k VRDX Sybil resistance deposit
    pub const MaxCommission: u8 = 20; // Maximum 20% commission // 1B VRDX (1% of total supply)
    pub const MinGreenScoreDpos: u8 = 0;
    pub const MaxGreenScoreDpos: u8 = 5;
    pub const ReactivationCooldown: u32 = 100; // ~30 days at 6s blocks (7200 blocks/day)
    pub const MinValidatorStake: Balance = 100_000_000 * UNITS; // 100M VRDX minimum (0.1% supply) for sybil resistance
    pub const ValidatorCount: u32 = 21; // 21 active validators for mainnet consensus
    pub const MinimumValidatorCount: u32 = 4; // Below 4 active validators, chain halts
    pub const MaxMissedEpochs: u32 = 50_000; // P0 FIX: was 3, increased to 10 for BABE safety
    pub const BlockReward: Balance = 342 * UNITS; // 342 VRDX per block (1.8B annual, 6% APR at 30% stake)
    pub const EpochLength: BlockNumber = 500;
    pub const UnbondingPeriod: u32 = 201_600; // 14 days at 6s blocks (14*24*3600/6)
}

impl pallet_dpos::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type Currency = MaxSupplyCurrency;
    type BlockReward = BlockReward;
    type MinStake = MinValidatorStake;
    type MaxValidators = MaxValidators;
    type ActiveValidatorCount = ValidatorCount;
    type EpochLength = EpochLength;
    type UnbondingPeriod = UnbondingPeriod;
    type PalletId = DposPalletId;
    /// P1-4: slashed funds route to the unified multisig-gated Treasury pot
    type Treasury = TreasuryAccount;
    type MaxStakePerValidator = MaxStakePerValidator;
    type RegistrationDeposit = RegistrationDeposit;
    type MaxCommission = MaxCommission;
    type MinGreenScore = MinGreenScoreDpos;
    type MaxGreenScore = MaxGreenScoreDpos;
    type ReactivationCooldown = ReactivationCooldown;
    type MaxMissedEpochs = MaxMissedEpochs;
    type MinimumValidatorCount = MinimumValidatorCount;
    type WeightInfo = pallet_dpos::SubstrateWeight<Runtime>;
    /// P1-2: Council 2/3 for admin operations
    type AdminOrigin = EnsureCouncil;
    type FindAuthor = pallet_session::FindAccountFromAuthorIndex<Runtime, Babe>;
}

// === Verdis AMM DEX ===

parameter_types! {
    pub const DexPalletId: PalletId = PalletId(*b"verdisdx");
    pub const MaxPriceImpact: sp_runtime::Permill = sp_runtime::Permill::from_percent(10); // 10% max price impact per swap
    pub const AmmMinimumLiquidity: u128 = 1_000;
    pub const FeeNumerator: u32 = 3;
    pub const FeeDenominator: u32 = 1000;
    pub const MinLiquidity: Balance = 1_000 * UNITS;
    pub const MaxPools: u32 = 50;
}

// === TokenHandler implementation for AmmDex <-> FungibleTokens integration ===
impl pallet_amm_dex::TokenHandler<AccountId, u128> for Runtime {
    fn transfer(
        asset: &pallet_amm_dex::AssetId,
        from: &AccountId,
        to: &AccountId,
        amount: u128,
    ) -> DispatchResult {
        match asset {
            pallet_amm_dex::AssetId::Native => {
                <crate::max_supply_currency::MaxSupplyCurrency as frame_support::traits::Currency<
                    AccountId,
                >>::transfer(
                    from,
                    to,
                    amount,
                    frame_support::traits::ExistenceRequirement::AllowDeath,
                )
            }
            pallet_amm_dex::AssetId::Custom(token_id) => {
                pallet_fungible_tokens::Pallet::<Runtime>::do_transfer(*token_id, from, to, amount)
            }
        }
    }

    fn has_balance(asset: &pallet_amm_dex::AssetId, who: &AccountId, amount: u128) -> bool {
        match asset {
            pallet_amm_dex::AssetId::Native => {
                <crate::max_supply_currency::MaxSupplyCurrency as frame_support::traits::Currency<
                    AccountId,
                >>::free_balance(who)
                    >= amount
            }
            pallet_amm_dex::AssetId::Custom(token_id) => {
                pallet_fungible_tokens::Pallet::<Runtime>::balance_of(*token_id, who) >= amount
            }
        }
    }

    #[cfg(feature = "runtime-benchmarks")]
    fn fund_for_benchmark(asset: &pallet_amm_dex::AssetId, who: &AccountId, amount: u128) {
        match asset {
            pallet_amm_dex::AssetId::Native => {
                let _ = <crate::max_supply_currency::MaxSupplyCurrency as frame_support::traits::Currency<
                    AccountId,
                >>::deposit_creating(who, amount);
            }
            pallet_amm_dex::AssetId::Custom(token_id) => {
                use frame_support::BoundedVec;
                use pallet_fungible_tokens::{TokenBalances, TokenInfo, Tokens};
                if Tokens::<Runtime>::get(token_id).is_none() {
                    let token = TokenInfo {
                        owner: who.clone(),
                        name: BoundedVec::try_from(b"BENCH".to_vec()).unwrap(),
                        symbol: BoundedVec::try_from(b"BCH".to_vec()).unwrap(),
                        decimals: 9,
                        total_supply: amount,
                        max_supply: u128::MAX,
                        is_frozen: false,
                        created_block: 0,
                    };
                    Tokens::<Runtime>::insert(token_id, token);
                }
                let current = TokenBalances::<Runtime>::get(token_id, who);
                TokenBalances::<Runtime>::insert(token_id, who, current + amount);
            }
        }
    }
}

impl pallet_amm_dex::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type Currency = MaxSupplyCurrency;
    type PalletId = DexPalletId;
    type MinimumLiquidity = AmmMinimumLiquidity;
    type MaxPriceImpact = MaxPriceImpact;
    type FeeNumerator = FeeNumerator;
    type FeeDenominator = FeeDenominator;
    type MinLiquidity = MinLiquidity;
    type MaxPools = MaxPools;
    type WeightInfo = pallet_amm_dex::SubstrateWeight<Runtime>;
    type TokenHandler = Runtime;
}

// === Verdis Eco ===

parameter_types! {
    pub const EcoPalletId: PalletId = PalletId(*b"verdisec");
    pub const MaxCarbonCredits: u32 = 1_000;
    pub const MaxReforestProjects: u32 = 500;
    pub const MaxGreenValidators: u32 = 101;
    pub const MinGreenScore: u8 = 1;
    pub const MaxGreenScore: u8 = 5;
    pub const EcoMaxNameLength: u32 = 128;
}

impl pallet_eco::Config for Runtime {
    // P1-4 FIX: Council 2/3 required for mainnet (was EnsureRoot)
    type AdminOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    type RuntimeEvent = RuntimeEvent;
    type PalletId = EcoPalletId;
    type MaxCarbonCredits = MaxCarbonCredits;
    type MaxReforestProjects = MaxReforestProjects;
    type MaxGreenValidators = MaxGreenValidators;
    type MinGreenScore = MinGreenScore;
    type MaxGreenScore = MaxGreenScore;
    type MaxNameLength = EcoMaxNameLength;
    type WeightInfo = pallet_eco::SubstrateWeight<Runtime>;
}

// --- Fungible Tokens Pallet Config ---
parameter_types! {
    pub const FungibleTokensPalletId: PalletId = PalletId(*b"vrdfungs");
    pub const MaxTokensPerAccount: u32 = 100;
    pub const CreateTokenDeposit: u64 = 100_000_000_000; // 100 VRDX (in smallest unit)
    pub const FungibleMaxBalance: u128 = u128::MAX;
}

impl pallet_fungible_tokens::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type Currency = MaxSupplyCurrency;
    type PalletId = FungibleTokensPalletId;
    type MaxTokensPerAccount = MaxTokensPerAccount;
    type CreateTokenDeposit = CreateTokenDeposit;
    type MaxBalance = FungibleMaxBalance;
    type WeightInfo = pallet_fungible_tokens::SubstrateWeight<Runtime>;
}

// === Verdis Tokenomics ===

parameter_types! {
    pub const TokenomicsPalletId: PalletId = PalletId(*b"verdistk");
    pub const TotalSupplyConst: Balance = 100_000_000_000 * UNITS;
    pub const InvestorAllocationConst: Balance = 5_000_000_000 * UNITS;
}

impl pallet_tokenomics::Config for Runtime {
    // FIX P1-2: Council 2/3 required for mainnet (was EnsureRoot/sudo)
    type AdminOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    type RuntimeEvent = RuntimeEvent;
    type Currency = MaxSupplyCurrency;
    type TotalSupply = TotalSupplyConst;
    type InvestorAllocation = InvestorAllocationConst;
    type PalletId = TokenomicsPalletId;
    type MaxPriorityFeeMultiplier = MaxPriorityFeeMultiplier;
    type DefaultTransferFeeBps = DefaultTransferFeeBps;
    type GreenTreasury = GreenTreasuryImpl;
    type WeightInfo = pallet_tokenomics::SubstrateWeight<Runtime>;
}

// === Verdis Vesting ===

parameter_types! {
    pub const VestingPalletId: PalletId = PalletId(*b"verdisvs");
}

impl pallet_vesting::Config for Runtime {
    type MaxSchedulesPerAccount = frame_support::traits::ConstU32<10>;
    type RuntimeEvent = RuntimeEvent;
    type Currency = MaxSupplyCurrency;
    type PalletId = VestingPalletId;
    type WeightInfo = pallet_vesting::SubstrateWeight<Runtime>;
    type BlockTimeMs = ConstU64<5000>;
    /// P1-2: Council 2/3 for admin operations
    type AdminOrigin = EnsureCouncil;
}

// === Verdis Presale ===
parameter_types! {
    pub const PresalePalletId: PalletId = PalletId(*b"verdisps");
}

impl pallet_presale::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type Currency = MaxSupplyCurrency;
    // Payment currency: native VRDX for testnet (bonus-rate presale).
    // For mainnet, change this to a stablecoin or other accepted asset.
    type PaymentCurrency = MaxSupplyCurrency;
    type PalletId = PresalePalletId;
    // FIX P1-3: Council 2/3 required for mainnet (was EnsureRoot/sudo)
    type AdminOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    type Vesting = PresaleVestingHandler;
    type WeightInfo = pallet_presale::SubstrateWeight<Runtime>;
    type Treasury = TreasuryAccount;
    type EnforceUniqueVestingLabels = frame_support::traits::ConstBool<true>;
}

/// Bridge presale → vesting pallet for atomic vesting creation
pub struct PresaleVestingHandler;
impl pallet_presale::VestingHandler<AccountId, u128> for PresaleVestingHandler {
    fn assign_vesting(who: &AccountId, schedule_label: Vec<u8>, amount: u128) -> DispatchResult {
        pallet_vesting::Pallet::<Runtime>::do_assign_vesting(who.clone(), schedule_label, amount)
    }
    fn do_remove_vesting(who: &AccountId, schedule_label: Vec<u8>, amount: u128) -> DispatchResult {
        pallet_vesting::Pallet::<Runtime>::do_remove_vesting(who, schedule_label, amount)
    }
    fn remove_all_vesting_for_label(
        who: &AccountId,
        schedule_label: Vec<u8>,
    ) -> Result<u128, DispatchError> {
        pallet_vesting::Pallet::<Runtime>::remove_all_vesting_for_label(who, schedule_label)
    }
}

// === Verdis Storage ===

parameter_types! {
    pub const StoragePalletId: PalletId = PalletId(*b"verdisst");
    pub const MaxStorageRecords: u32 = 10_000;
    pub const MaxStorageSizeBytes: u64 = 1_000_000_000_000;  // 1 TB max per record
    pub const StorageBaseDeposit: u128 = 1_000_000_000_000;  // 1 VRDX (9 decimals)
    pub const StorageDepositPerByte: u128 = 1_000_000;  // 0.001 VRDX per byte
    pub const StorageExpiryBlocks: u32 = 259_200;  // ~30 days at 10s blocks
}

impl pallet_storage::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type PalletId = StoragePalletId;
    type MaxRecords = MaxStorageRecords;
    type MaxSizeBytes = MaxStorageSizeBytes;
    type ShardCount = StorageShardCount;
    type Currency = MaxSupplyCurrency;
    type BaseDeposit = StorageBaseDeposit;
    type DepositPerByte = StorageDepositPerByte;
    type ExpiryBlocks = StorageExpiryBlocks;
    type WeightInfo = pallet_storage::SubstrateWeight<Runtime>;
}

// === Utility (Batch) ===
impl pallet_utility::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type RuntimeCall = RuntimeCall;
    type PalletsOrigin = OriginCaller;
    type WeightInfo = ();
}

/* // === Identity ===

parameter_types! {
    pub const BasicDeposit: Balance = 10 * UNITS;
    pub const ByteDeposit: Balance = 1 * UNITS;
    pub const UsernameDeposit: Balance = 5 * UNITS;
    pub const SubAccountDeposit: Balance = 5 * UNITS;
    pub const MaxSubAccounts: u32 = 100;
    pub const MaxRegistrars: u32 = 20;
    pub const PendingUsernameExpiration: BlockNumber = 1000;
    pub const UsernameGracePeriod: BlockNumber = 1000;
    pub const MaxSuffixLength: u32 = 32;
    pub const MaxUsernameLength: u32 = 64;
}

impl pallet_identity::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type Currency = MaxSupplyCurrency;
    type BasicDeposit = BasicDeposit;
    type ByteDeposit = ByteDeposit;
    type UsernameDeposit = UsernameDeposit;
    type SubAccountDeposit = SubAccountDeposit;
    type MaxSubAccounts = MaxSubAccounts;
    type IdentityInformation = frame_support::identity::IdentityInfo<MaxAdditionalFields>;
    type MaxRegistrars = MaxRegistrars;
    type Slashed = ();
    // Post-sudo: Council (2/3) controls identity
    type ForceOrigin = pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    type RegistrarOrigin = pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    type OffchainSignature = MultiSignature;
    type SigningPublicKey = AccountId;
    // Post-sudo: Council (2/3) controls usernames
    type UsernameAuthorityOrigin = pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    type PendingUsernameExpiration = PendingUsernameExpiration;
    type UsernameGracePeriod = UsernameGracePeriod;
    type MaxSuffixLength = MaxSuffixLength;
    type MaxUsernameLength = MaxUsernameLength;
    type WeightInfo = ();
} */

// === Multisig ===

parameter_types! {
    pub const MultisigDepositBase: Balance = 5 * UNITS;
    pub const MultisigDepositFactor: Balance = 1 * UNITS;
    pub const MaxSignatories: u32 = 100;
}

impl pallet_multisig::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type RuntimeCall = RuntimeCall;
    type Currency = MaxSupplyCurrency;
    type DepositBase = MultisigDepositBase;
    type DepositFactor = MultisigDepositFactor;
    type MaxSignatories = MaxSignatories;
    type WeightInfo = ();
    type BlockNumberProvider = System;
}

// === Proxy ===

parameter_types! {
    pub const ProxyDepositBase: Balance = 5 * UNITS;
    pub const ProxyDepositFactor: Balance = 1 * UNITS;
    pub const MaxProxies: u32 = 32;
    pub const MaxPending: u32 = 32;
    pub const AnnouncementDepositBase: Balance = 5 * UNITS;
    pub const AnnouncementDepositFactor: Balance = 1 * UNITS;
}

#[derive(
    Encode,
    Decode,
    codec::DecodeWithMemTracking,
    Clone,
    Copy,
    PartialEq,
    Eq,
    Ord,
    PartialOrd,
    Debug,
    MaxEncodedLen,
    TypeInfo,
)]
pub enum ProxyType {
    Any,
    NonTransfer,
    Governance,
    Staking,
    Identity,
    DEX,
    Eco,
}

impl Default for ProxyType {
    fn default() -> Self {
        ProxyType::Any
    }
}

impl frame_support::traits::InstanceFilter<RuntimeCall> for ProxyType {
    fn filter(&self, c: &RuntimeCall) -> bool {
        match self {
            ProxyType::Any => true,
            ProxyType::NonTransfer => {
                !matches!(c, RuntimeCall::Balances(_) | RuntimeCall::AmmDex(_))
            }
            ProxyType::Governance => {
                matches!(c, RuntimeCall::Democracy(_) | RuntimeCall::Council(_))
            }
            ProxyType::Staking => matches!(c, RuntimeCall::Dpos(_)),
            ProxyType::Identity => false,
            ProxyType::DEX => matches!(c, RuntimeCall::AmmDex(_)),
            ProxyType::Eco => matches!(c, RuntimeCall::Eco(_)),
        }
    }
}

impl pallet_proxy::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type RuntimeCall = RuntimeCall;
    type Currency = MaxSupplyCurrency;
    type ProxyType = ProxyType;
    type ProxyDepositBase = ProxyDepositBase;
    type ProxyDepositFactor = ProxyDepositFactor;
    type MaxProxies = MaxProxies;
    type WeightInfo = ();
    type MaxPending = MaxPending;
    type CallHasher = BlakeTwo256;
    type AnnouncementDepositBase = AnnouncementDepositBase;
    type AnnouncementDepositFactor = AnnouncementDepositFactor;
    type BlockNumberProvider = System;
}

/* // === Assets (Fungible Tokens) ===

parameter_types! {
    pub const AssetDeposit: Balance = 100 * UNITS;
    pub const AssetAccountDeposit: Balance = 1 * UNITS;
    pub const MetadataDeposit: Balance = 10 * UNITS;
    pub const ApprovalDeposit: Balance = 1 * UNITS;
    pub const StringLimit: u32 = 64;
    pub const MetadataApprovalsLimit: u32 = 10;
}

impl pallet_assets::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type Balance = Balance;
    type AssetId = u32;
    type AssetIdParameter = u32;
    type ReserveData = ();
    type RemoveItemsLimit = ConstU32<1000>;
    type Currency = MaxSupplyCurrency;
    // Post-sudo: Anyone can create NFT collections, Council (2/3) can force
    type CreateOrigin = frame_system::EnsureSigned<AccountId>;
    type ForceOrigin = pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    type AssetDeposit = AssetDeposit;
    type AssetAccountDeposit = AssetAccountDeposit;
    type MetadataDepositBase = MetadataDeposit;
    type MetadataDepositPerByte = MetadataDeposit;
    type ApprovalDeposit = ApprovalDeposit;
    type StringLimit = StringLimit;
    type Freezer = ();
    type Holder = ();
    type Extra = ();
    type CallbackHandle = ();
    type WeightInfo = ();
}
 */
// Shared parameter (used by NFTs)

parameter_types! {
    pub const StringLimit: u32 = 64;
}

// === NFTs ===

parameter_types! {
    pub NftFeatures: pallet_nfts::PalletFeatures = pallet_nfts::PalletFeatures::all_enabled();

    pub const NftCollectionDeposit: Balance = 100 * UNITS;
    pub const NftItemDeposit: Balance = 1 * UNITS;
    pub const NftMetadataDeposit: Balance = 10 * UNITS;
    pub const NftAttributeDeposit: Balance = 1 * UNITS;
    pub const NftDepositPerByte: Balance = 1 * UNITS;
    pub const NftMaxAttributesPerCall: u32 = 16;
    pub const NftMaxDeadlineDuration: u32 = 201600; // 14 days
}

impl pallet_nfts::Config for Runtime {
    #[cfg(feature = "runtime-benchmarks")]
    type Helper = ();
    type RuntimeEvent = RuntimeEvent;
    type CollectionId = u32;
    type ItemId = u32;
    type Currency = MaxSupplyCurrency;
    // Post-sudo: Council (2/3) can force NFT actions
    type ForceOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    type CreateOrigin = frame_system::EnsureSigned<AccountId>;
    type Locker = ();
    type CollectionDeposit = NftCollectionDeposit;
    type ItemDeposit = NftItemDeposit;
    type MetadataDepositBase = NftMetadataDeposit;
    type AttributeDepositBase = NftAttributeDeposit;
    type DepositPerByte = NftDepositPerByte;
    type StringLimit = StringLimit;
    type KeyLimit = ConstU32<64>;
    type ValueLimit = ConstU32<256>;
    type ApprovalsLimit = ConstU32<20>;
    type ItemAttributesApprovalsLimit = ConstU32<20>;
    type MaxTips = ConstU32<10>;
    type MaxDeadlineDuration = NftMaxDeadlineDuration;
    type MaxAttributesPerCall = NftMaxAttributesPerCall;
    type Features = NftFeatures;
    type OffchainSignature = sp_runtime::MultiSignature;
    type OffchainPublic = sp_runtime::MultiSigner;
    type WeightInfo = ();
    type BlockNumberProvider = System;
}

// === Treasury ===

// P1-2: Council (2/3) origin for admin operations — replaces EnsureRoot/sudo
pub struct EnsureCouncil;
impl frame_support::traits::EnsureOrigin<RuntimeOrigin> for EnsureCouncil {
    type Success = ();
    fn try_origin(o: RuntimeOrigin) -> Result<Self::Success, RuntimeOrigin> {
        pallet_collective::EnsureProportionAtLeast::<AccountId, pallet_collective::Instance1, 2, 3>
            ::try_origin(o)
            .map(|_| ())
    }
    #[cfg(feature = "runtime-benchmarks")]
    fn try_successful_origin() -> Result<RuntimeOrigin, ()> {
        use frame_system::RawOrigin;
        Ok(RawOrigin::Root.into())
    }
}

// Post-sudo: Council (2/3) spend origin for Treasury with success type
pub struct EnsureCouncilSpend;
impl frame_support::traits::EnsureOrigin<RuntimeOrigin> for EnsureCouncilSpend {
    type Success = u128;
    fn try_origin(o: RuntimeOrigin) -> Result<Self::Success, RuntimeOrigin> {
        pallet_collective::EnsureProportionAtLeast::<AccountId, pallet_collective::Instance1, 2, 3>
            ::try_origin(o)
            .map(|_| TreasuryMaxSpend::get())
    }
    #[cfg(feature = "runtime-benchmarks")]
    fn try_successful_origin(o: RuntimeOrigin) -> Result<Option<Self::Success>, RuntimeOrigin> {
        match Self::try_origin(o.clone()) {
            Ok(s) => Ok(Some(s)),
            Err(_) => {
                use frame_support::traits::OriginTrait;
                if frame_system::ensure_root(o.clone()).is_ok() {
                    Ok(Some(TreasuryMaxSpend::get()))
                } else {
                    Err(o)
                }
            }
        }
    }

    #[cfg(feature = "runtime-benchmarks")]
    fn try_successful_origin() -> Result<RuntimeOrigin, ()> {
        // Council majority origin
        use frame_system::RawOrigin;
        Ok(RawOrigin::Root.into())
    }
}

parameter_types! {
    pub const TreasuryPalletId: PalletId = PalletId(*b"verdist0");
    pub const TreasurySpendPeriod: BlockNumber = 600;
    pub const TreasuryBurn: Permill = Permill::from_percent(0);  // 0% burn — preserve 100B supply
    pub const TreasuryMaxApprovals: u32 = 100;
    pub const TreasuryPayoutPeriod: BlockNumber = 600;
    pub TreasuryAccount: AccountId = TreasuryPalletId::get().into_account_truncating();
    pub const TreasuryMaxSpend: Balance = 1_000_000_000_000_000_000;
}

impl pallet_treasury::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type Currency = MaxSupplyCurrency;
    type RejectOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    type SpendPeriod = TreasurySpendPeriod;
    type Burn = TreasuryBurn;
    type PalletId = TreasuryPalletId;
    type BurnDestination = ();
    type WeightInfo = ();
    type SpendFunds = ();
    type MaxApprovals = TreasuryMaxApprovals;
    // Post-sudo: Treasury spending through governance proposals (not direct dispatchable)
    type SpendOrigin = EnsureMultisigOrCouncilSpend; // 3-of-5 multisig (post-ceremony) or council 2/3 (pre-ceremony)
    type AssetKind = ();
    type Beneficiary = AccountId;
    type BeneficiaryLookup = AccountIdLookup<AccountId, ()>;
    type Paymaster = frame_support::traits::tokens::PayFromAccount<Balances, TreasuryAccount>;
    type BalanceConverter = frame_support::traits::tokens::UnityAssetBalanceConversion;
    type PayoutPeriod = TreasuryPayoutPeriod;
    type BlockNumberProvider = System;
}

// === Treasury Multisig (3-of-5 cold storage) ===
// Placeholder signers: None until air-gapped key ceremony completes
// After ceremony: set to 5 signer AccountIds via runtime upgrade
pub struct TreasuryMultisigSigners;
impl frame_support::traits::Get<Option<Vec<AccountId>>> for TreasuryMultisigSigners {
    fn get() -> Option<Vec<AccountId>> {
        // P1-4 ACTIVATED 2026-09-03: 3-of-5 multisig cold-storage signers
        // (mini-ceremony #2, generated fresh — original Sep-2 multisig keys were
        // never backed up and are dead). Council 2/3 remains as emergency
        // fallback only.
        use sp_core::crypto::Ss58Codec;
        let signers = [
            "5FucH479zS8cvWLbcZXSZschp4qswT8zyRepGxe58ddwA9Rt", // multisig-01
            "5CdSGiFi8LM35Bo3UqaGmsr71zCHzGz99SHZdbYsgqJT3vem", // multisig-02
            "5EptohYJnZ2JhPJwAsPHKZMyFA9jyJX6daYB29HBAh3J7NmY", // multisig-03
            "5D5EGs3je2h5d4SbdYvKDLyDHAgWPBWwtxkZNamZXDRouuAL", // multisig-04
            "5DJX32TrU4WGG4MizRDmia5yC4hdp1Q1hCzy16CqgFSUehEy", // multisig-05
        ];
        Some(
            signers
                .iter()
                .map(|s| AccountId::from_ss58check(s).expect("static multisig signer address"))
                .collect(),
        )
    }
}

frame_support::parameter_types! {
    pub const TreasuryMultisigThreshold: u16 = 3;
}

// Treasury spend origin: 3-of-5 multisig (post-ceremony) or Council 2/3 (pre-ceremony)
pub struct EnsureMultisigOrCouncilSpend;
impl frame_support::traits::EnsureOrigin<RuntimeOrigin> for EnsureMultisigOrCouncilSpend {
    type Success = u128;

    fn try_origin(o: RuntimeOrigin) -> Result<Self::Success, RuntimeOrigin> {
        // Try multisig first (post-ceremony)
        if let Some(signers) = TreasuryMultisigSigners::get() {
            if signers.len() >= 5 {
                if let Ok(caller) = frame_system::ensure_signed(o.clone()) {
                    let multisig_account = pallet_multisig::Pallet::<Runtime>::multi_account_id(
                        &signers,
                        TreasuryMultisigThreshold::get(),
                    );
                    if caller == multisig_account {
                        return Ok(TreasuryMaxSpend::get());
                    }
                }
            }
        }

        // Fallback: Council 2/3 (pre-ceremony)
        pallet_collective::EnsureProportionAtLeast::<AccountId, pallet_collective::Instance1, 2, 3>
            ::try_origin(o)
            .map(|_| TreasuryMaxSpend::get())
    }

    #[cfg(feature = "runtime-benchmarks")]
    fn try_successful_origin(o: RuntimeOrigin) -> Result<Option<Self::Success>, RuntimeOrigin> {
        match Self::try_origin(o.clone()) {
            Ok(s) => Ok(Some(s)),
            Err(remaining) => match frame_system::ensure_root(remaining) {
                Ok(()) => Ok(Some(TreasuryMaxSpend::get())),
                Err(_) => Err(o),
            },
        }
    }
}

// === Council (Collective) ===

parameter_types! {
    pub const CouncilMaxMembers: u32 = 21;
    pub const CouncilMotionDuration: BlockNumber = 600;
    pub const CouncilMaxProposals: u32 = 100;
}

impl pallet_collective::Config<pallet_collective::Instance1> for Runtime {
    type RuntimeOrigin = RuntimeOrigin;
    type Proposal = RuntimeCall;
    type RuntimeEvent = RuntimeEvent;
    type MotionDuration = CouncilMotionDuration;
    type MaxProposals = CouncilMaxProposals;
    type MaxMembers = CouncilMaxMembers;
    type DefaultVote = pallet_collective::PrimeDefaultVote;
    type WeightInfo = ();
    type SetMembersOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    type MaxProposalWeight = MaximumSchedulerWeight;
    // Post-sudo: Council self-governs — simple majority disapprove, 2/3 kill
    type DisapproveOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 1, 2>;
    type KillOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    type Consideration = ();
}

// === Technical Committee (emergency upgrades) ===
parameter_types! {
    pub const TechnicalCommitteeMaxMembers: u32 = 3;
    pub const TechnicalCommitteeMotionDuration: BlockNumber = 3600;
    pub const TechnicalCommitteeMaxProposals: u32 = 20;
}

impl pallet_collective::Config<pallet_collective::Instance2> for Runtime {
    type RuntimeOrigin = RuntimeOrigin;
    type Proposal = RuntimeCall;
    type RuntimeEvent = RuntimeEvent;
    type MotionDuration = TechnicalCommitteeMotionDuration;
    type MaxProposals = TechnicalCommitteeMaxProposals;
    type MaxMembers = TechnicalCommitteeMaxMembers;
    type DefaultVote = pallet_collective::PrimeDefaultVote;
    type WeightInfo = ();
    // Post-sudo: Council (2/3) controls tech committee composition
    type SetMembersOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    type MaxProposalWeight = MaximumSchedulerWeight;
    // Council (1/3) can disapprove, Council (2/3) can kill
    type DisapproveOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 1, 3>;
    type KillOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    type Consideration = ();
}

// === Democracy ===

parameter_types! {
    pub const LaunchPeriod: BlockNumber = 600;
    pub const VotingPeriod: BlockNumber = 600;
    pub const FastTrackVotingPeriod: BlockNumber = 300;
    pub const MinimumDeposit: Balance = 1000 * UNITS;
    pub const EnactmentPeriod: BlockNumber = 600;
    pub const CooloffPeriod: BlockNumber = 600;
    pub const MaxVotes: u32 = 100;
    pub const MaxProposals: u32 = 100;
    pub const MaxDeposits: u32 = 100;
    pub const MaxBlacklisted: u32 = 100;
}

impl pallet_democracy::Config for Runtime {
    type WeightInfo = ();
    type RuntimeEvent = RuntimeEvent;
    type Scheduler = Scheduler;
    type Preimages = Preimage;
    type Currency = MaxSupplyCurrency;
    type EnactmentPeriod = EnactmentPeriod;
    type LaunchPeriod = LaunchPeriod;
    type VotingPeriod = VotingPeriod;
    type VoteLockingPeriod = EnactmentPeriod;
    type MinimumDeposit = MinimumDeposit;
    type InstantAllowed = ConstBool<false>;
    type FastTrackVotingPeriod = FastTrackVotingPeriod;
    type CooloffPeriod = CooloffPeriod;
    type MaxVotes = MaxVotes;
    type MaxProposals = MaxProposals;
    type MaxDeposits = MaxDeposits;
    type MaxBlacklisted = MaxBlacklisted;
    type ExternalOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 1, 2>;
    type ExternalMajorityOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    type ExternalDefaultOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 1, 2>;
    type SubmitOrigin = frame_system::EnsureSigned<AccountId>;
    type FastTrackOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    type InstantOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 1, 1>;
    type CancellationOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    // Post-sudo: Council (2/3) can blacklist proposals
    type BlacklistOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    // Post-sudo: Council (2/3) can cancel proposals
    type CancelProposalOrigin =
        pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;
    type VetoOrigin = frame_system::EnsureSigned<AccountId>;
    type PalletsOrigin = OriginCaller;
    type Slash = ();
}

// === Construct Runtime ===
// Green Treasury implementation

// Green Treasury implementation - uses raw AccountId
pub struct GreenTreasuryImpl;
impl Get<AccountId> for GreenTreasuryImpl {
    fn get() -> AccountId {
        TreasuryPalletId::get().into_account_truncating()
    }
}

// === Solana-inspired pallet parameters ===
parameter_types! {
    pub const MaxShardsTurbine: u32 = 64;
    pub const RedundancyFactor: u32 = 2;
    pub const MaxValidatorsPerNode: u32 = 16;
    pub const MaxZkLeaves: u32 = 65536;
    pub const MaxZkDepth: u32 = 20;
    pub const MaxAddressesPerTable: u32 = 256;
    pub const MaxTablesPerAccount: u32 = 32;
    pub const MaxComputeUnits: u64 = 200_000;
    pub const MaxParallelBatches: u32 = 128;
    pub const MaxPendingForwards: u32 = 1000;
    pub const MaxForwardedHistory: u32 = 10000;
    pub const MaxGulfForwardTimeMs: u64 = 60_000;
    pub const StorageShardCount: u32 = 16;
    // Green treasury - uses PalletId for account derivation
pub const GreenTreasuryPalletId: PalletId = PalletId(*b"vrds/trs");
    pub const MaxPriorityFeeMultiplier: u32 = 1000;
    pub const DefaultTransferFeeBps: u32 = 50; // 0.5%
}

// === Solana-inspired Config impls ===
impl pallet_poh::Config for Runtime {
    type WeightInfo = pallet_poh::SubstrateWeight<Runtime>;
    /// P1-2: Council 2/3 for admin operations
    type AdminOrigin = EnsureCouncil;
}
impl pallet_gulf_stream::ValidatorChecker<AccountId> for Runtime {
    fn is_active_validator(who: &AccountId) -> bool {
        pallet_dpos::ActiveValidators::<Runtime>::get().contains(who)
    }
}

impl pallet_gulf_stream::Config for Runtime {
    type MaxPendingForwards = MaxPendingForwards;
    type MaxForwardedHistory = MaxForwardedHistory;
    type MaxForwardTimeMs = MaxGulfForwardTimeMs;
    type ValidatorChecker = Runtime;
}
impl pallet_turbine::Config for Runtime {
    type MaxShards = MaxShardsTurbine;
    type RedundancyFactor = RedundancyFactor;
    type MaxValidatorsPerNode = MaxValidatorsPerNode;
    type WeightInfo = pallet_turbine::SubstrateWeight<Runtime>;
    /// P1-2: Council 2/3 for admin operations
    type AdminOrigin = EnsureCouncil;
}
impl pallet_zk_compression::Config for Runtime {
    type MaxLeaves = MaxZkLeaves;
    type MaxDepth = MaxZkDepth;
    type WeightInfo = pallet_zk_compression::SubstrateWeight<Runtime>;
    /// P1-2: Council 2/3 for admin operations
    type AdminOrigin = EnsureCouncil;
}
impl pallet_address_lookup_tables::Config for Runtime {
    type MaxAddressesPerTable = MaxAddressesPerTable;
    type MaxTablesPerAccount = MaxTablesPerAccount;
    type WeightInfo = pallet_address_lookup_tables::SubstrateWeight<Runtime>;
}
impl pallet_sealevel::Config for Runtime {
    type MaxComputeUnits = MaxComputeUnits;
    type MaxParallelBatches = MaxParallelBatches;
    type WeightInfo = pallet_sealevel::SubstrateWeight<Runtime>;
}

// Update tokenomics config to add new traits
// Note: The tokenomics Config already exists, we need to add the new constants

// Update storage config to add ShardCount
// Note: Storage Config already exists, we need to add ShardCount

parameter_types! {
    pub const CircuitBreakerMaxPalletNameLen: u32 = 32;
}

impl pallet_circuit_breaker::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type MaxPalletNameLen = CircuitBreakerMaxPalletNameLen;
    // FIX H8: Use Council 2/3 as AdminOrigin instead of root
    type AdminOrigin = EnsureCouncilSpend;
}

construct_runtime! {
    pub enum Runtime {
        System: frame_system = 0,
        Timestamp: pallet_timestamp = 1,
        Babe: pallet_babe = 2,
        Grandpa: pallet_grandpa = 3,
        Balances: pallet_balances = 4,
        TransactionPayment: pallet_transaction_payment = 5,
        Dpos: pallet_dpos = 30,
        Session: pallet_session = 7,
        Scheduler: pallet_scheduler = 8,
        Preimage: pallet_preimage = 9,
        Contracts: pallet_contracts = 20,
        AmmDex: pallet_amm_dex = 31,
        Eco: pallet_eco = 32,
        Tokenomics: pallet_tokenomics = 33,
        Vesting: pallet_vesting = 34,
        Presale: pallet_presale = 58,
        Storage: pallet_storage = 35,
        Utility: pallet_utility = 36,
        // Identity: pallet_identity = 37, // deferred — complex IdentityInformation config
        Multisig: pallet_multisig = 38,
        Proxy: pallet_proxy = 39,
        // Assets: pallet_assets = 40, // need compatible version
        Nfts: pallet_nfts = 41,
        Authorship: pallet_authorship = 42,
        Historical: pallet_session::historical = 45,
        Offences: pallet_offences = 46,
        Treasury: pallet_treasury = 47,
        Council: pallet_collective::<Instance1> = 43,
        Democracy: pallet_democracy = 44,
        FungibleTokens: pallet_fungible_tokens = 50,
        Poh: pallet_poh = 51,
        GulfStream: pallet_gulf_stream = 52,
        Turbine: pallet_turbine = 53,
        ZkCompression: pallet_zk_compression = 54,
        AddressLookupTables: pallet_address_lookup_tables = 55,
        Sealevel: pallet_sealevel = 56,
        CircuitBreaker: pallet_circuit_breaker = 60,
        TechnicalCommittee: pallet_collective::<Instance2> = 61,
        // === EVM (Frontier) ===
        Ethereum: pallet_ethereum = 62,
        EVM: pallet_evm = 63,
        EVMChainId: pallet_evm_chain_id = 64,
        BaseFee: pallet_base_fee = 65,
        // Binds ki… and 0x… to one balance. Index 66: 65 is the highest in use.
        AccountLink: pallet_verdis_account_link = 66,
    }
}

// Type aliases that depend on construct_runtime!
pub type Block = generic::Block<Header, UncheckedExtrinsic>;
pub type Address = sp_runtime::MultiAddress<AccountId, ()>;
/// Executive: the main orchestrator of the runtime
/// EVM chain id for Verdis. 414 is unregistered in chainid.network/chains.json, unlike 909 which is
/// held by Portal Fantasy Chain - a collision there would make wallets reject Verdis outright.
pub const VERDIS_EVM_CHAIN_ID: u64 = 414;

/// Writes `EVMChainId::ChainId` during a runtime upgrade.
///
/// A runtime upgrade never executes `GenesisConfig` - genesis runs only at block 0. Pallets added by
/// `set_code` therefore begin with EMPTY storage, so this value reads as its default (0) on any chain
/// that did not START with the EVM runtime. A live EVM answering `eth_chainId = 0` is a transaction
/// replay surface, so the upgrade itself must write the value instead of relying on a follow-up
/// governance call that leaves a window of exposure.
///
/// Idempotent: writes only when unset, so it is safe on a genesis chain, on a chain already
/// corrected by hand, and on repeated runs.
pub struct SetEvmChainId;

impl frame_support::traits::OnRuntimeUpgrade for SetEvmChainId {
    fn on_runtime_upgrade() -> Weight {
        let current = pallet_evm_chain_id::ChainId::<Runtime>::get();
        if current == 0 {
            pallet_evm_chain_id::ChainId::<Runtime>::put(VERDIS_EVM_CHAIN_ID);
            frame_support::__private::log::info!(target: "runtime::migration", "SetEvmChainId: 0 -> {}", VERDIS_EVM_CHAIN_ID);
            <Runtime as frame_system::Config>::DbWeight::get().reads_writes(1, 1)
        } else {
            frame_support::__private::log::info!(target: "runtime::migration", "SetEvmChainId: already {}", current);
            <Runtime as frame_system::Config>::DbWeight::get().reads(1)
        }
    }
}

/// Migrations run by `Executive` on runtime upgrade.
pub type Migrations = (SetEvmChainId,);

pub type Executive = frame_executive::Executive<
    Runtime,
    Block,
    frame_system::ChainContext<Runtime>,
    Runtime,
    AllPalletsWithSystem,
    Migrations,
>;

/// Signed extra data for transactions
pub type SignedExtra = (
    frame_system::CheckNonZeroSender<Runtime>,
    frame_system::CheckSpecVersion<Runtime>,
    frame_system::CheckTxVersion<Runtime>,
    frame_system::CheckGenesis<Runtime>,
    frame_system::CheckMortality<Runtime>,
    frame_system::CheckNonce<Runtime>,
    frame_system::CheckWeight<Runtime>,
    pallet_transaction_payment::ChargeTransactionPayment<Runtime>,
);

/// The UncheckedExtrinsic type.
///
/// Wrapped in fp_self_contained so a raw Ethereum transaction - which carries an Ethereum ECDSA
/// signature rather than a Substrate one - can validate itself and enter the transaction pool.
/// This is required for MetaMask/eth_sendRawTransaction; without it pallet_ethereum::transact
/// is unsubmittable.
///
/// NOTE: this changes the extrinsic encoding, so transaction_version is bumped and clients must
/// refetch metadata.
pub type UncheckedExtrinsic =
    fp_self_contained::UncheckedExtrinsic<Address, RuntimeCall, Signature, SignedExtra>;

/// The checked counterpart, carrying the recovered H160 for self-contained calls.
pub type CheckedExtrinsic =
    fp_self_contained::CheckedExtrinsic<AccountId, RuntimeCall, SignedExtra, H160>;

impl fp_self_contained::SelfContainedCall for RuntimeCall {
    type SignedInfo = H160;

    fn is_self_contained(&self) -> bool {
        match self {
            RuntimeCall::Ethereum(call) => call.is_self_contained(),
            _ => false,
        }
    }

    fn check_self_contained(
        &self,
    ) -> Option<Result<Self::SignedInfo, sp_runtime::transaction_validity::TransactionValidityError>>
    {
        match self {
            RuntimeCall::Ethereum(call) => call.check_self_contained(),
            _ => None,
        }
    }

    fn validate_self_contained(
        &self,
        info: &Self::SignedInfo,
        dispatch_info: &DispatchInfoOf<RuntimeCall>,
        len: usize,
    ) -> Option<sp_runtime::transaction_validity::TransactionValidity> {
        match self {
            RuntimeCall::Ethereum(call) => call.validate_self_contained(info, dispatch_info, len),
            _ => None,
        }
    }

    fn pre_dispatch_self_contained(
        &self,
        info: &Self::SignedInfo,
        dispatch_info: &DispatchInfoOf<RuntimeCall>,
        len: usize,
    ) -> Option<Result<(), sp_runtime::transaction_validity::TransactionValidityError>> {
        match self {
            RuntimeCall::Ethereum(call) => {
                call.pre_dispatch_self_contained(info, dispatch_info, len)
            }
            _ => None,
        }
    }

    fn apply_self_contained(
        self,
        info: Self::SignedInfo,
    ) -> Option<sp_runtime::DispatchResultWithInfo<PostDispatchInfoOf<RuntimeCall>>> {
        match self {
            call @ RuntimeCall::Ethereum(pallet_ethereum::Call::transact { .. }) => {
                Some(call.dispatch(RuntimeOrigin::from(
                    pallet_ethereum::RawOrigin::EthereumTransaction(info),
                )))
            }
            _ => None,
        }
    }
}

// === Custom Runtime API Declaration ===
sp_api::decl_runtime_apis! {
    /// API for querying AmmDex pool data
    pub trait AmmDexApi {
        /// Get a native VRDX pool by ID
        fn get_pool(pool_id: u32) -> Option<pallet_amm_dex::Pool<AccountId, Balance>>;
        /// Get total native pool count
        fn get_pool_count() -> u32;
        /// Get all native pools
        fn get_all_pools() -> Vec<pallet_amm_dex::Pool<AccountId, Balance>>;
        /// Get a token pool by ID
        fn get_token_pool(pool_id: u32) -> Option<pallet_amm_dex::TokenPool<AccountId, Balance>>;
        /// Get total token pool count
        fn get_token_pool_count() -> u32;
        /// Get all token pools
        fn get_all_token_pools() -> Vec<pallet_amm_dex::TokenPool<AccountId, Balance>>;
        /// Get liquidity for an account in a native pool
        fn get_liquidity(pool_id: u32, account: AccountId) -> Balance;
        /// Get liquidity for an account in a token pool
        fn get_token_liquidity(pool_id: u32, account: AccountId) -> Balance;
        /// Get price of a token in a native pool
        /// Get price of a token in a native pool
        fn get_price(pool_id: u32, token: Vec<u8>) -> Option<Balance>;
        /// Get a swap quote (expected output amount for a given input)
        fn get_swap_quote(pool_id: u32, token_in: Vec<u8>, amount_in: Balance) -> Option<Balance>;
    }

    /// The API to interact with the contracts pallet without executing extrinsics.
    pub trait ContractsApi {
        /// Execute a call to a contract.
        fn call(
            origin: AccountId,
            dest: AccountId,
            value: Balance,
            gas_limit: Option<frame_support::weights::Weight>,
            storage_deposit_limit: Option<Balance>,
            input_data: Vec<u8>,
        ) -> pallet_contracts::ContractExecResult<Balance, frame_system::EventRecord<RuntimeEvent, Hash>>;

        /// Instantiate a contract.
        fn instantiate(
            origin: AccountId,
            value: Balance,
            gas_limit: Option<frame_support::weights::Weight>,
            storage_deposit_limit: Option<Balance>,
            code: pallet_contracts::Code<Hash>,
            data: Vec<u8>,
            salt: Vec<u8>,
        ) -> pallet_contracts::ContractInstantiateResult<AccountId, Balance, frame_system::EventRecord<RuntimeEvent, Hash>>;

        /// Upload contract code.
        fn upload_code(
            origin: AccountId,
            code: Vec<u8>,
            storage_deposit_limit: Option<Balance>,
        ) -> pallet_contracts::CodeUploadResult<Hash, Balance>;

        /// Get storage from a contract.
        fn get_storage(
            address: AccountId,
            key: Vec<u8>,
        ) -> pallet_contracts::GetStorageResult;
    }

    /// API for querying DPoS validator state
    pub trait DposApi {
        /// Get active validators
        fn active_validators() -> Vec<AccountId>;
        /// Get all registered validators
        fn all_validators() -> Vec<AccountId>;
        /// Get validator stake
        fn validator_stake(validator: AccountId) -> Balance;
        /// Get current epoch
        fn current_epoch() -> u32;
        /// Get validator name
        fn get_validator_name(validator: AccountId) -> Option<Vec<u8>>;
        /// Get current session index
        fn session_index() -> u32;
        /// Get all validators with full details (stake, name, commission, etc.)
        fn get_all_validators_detailed() -> Vec<pallet_dpos::Validator<AccountId, Balance>>;
    }

    /// Eco tracking API for RPC
    pub trait EcoApi {
        /// Get total CO2 offset in tons
        fn get_total_co2_offset() -> u64;
        /// Get total trees planted
        fn get_total_trees_planted() -> u32;
        /// Get total carbon credits retired
        fn get_total_credits_retired() -> u64;
        /// Get total carbon credit count
        fn get_carbon_credit_count() -> u32;
        /// Get total reforest project count
        fn get_reforest_project_count() -> u32;
        /// Get total green validator count
        fn get_green_validator_count() -> u32;
        /// Get green score for a specific validator
        fn get_green_score(validator: AccountId) -> Option<u8>;
        /// Get all green validators with their scores
        fn get_all_green_validators() -> Vec<(AccountId, u8)>;
        /// Get all carbon credits with full details
        fn get_all_carbon_credits() -> Vec<pallet_eco::CarbonCredit<AccountId>>;
        /// Get all reforestation projects with full details
        fn get_all_reforest_projects() -> Vec<pallet_eco::ReforestProject>;
        /// Get all green validators with full details
        fn get_all_green_validators_detailed() -> Vec<pallet_eco::GreenValidator<AccountId>>;
    }

    /// Tokenomics API for RPC
    pub trait TokenomicsApi {
        /// Get total token supply
        fn get_total_supply() -> Balance;
        /// Get circulating supply
        fn get_circulating_supply() -> Balance;
        /// Get presale price
        fn get_presale_price() -> u32;
        /// Get total presale raised
        fn get_presale_raised() -> Balance;
        /// Get total presale sold
        fn get_presale_sold() -> Balance;
        /// Get transfer fee basis points
        fn get_transfer_fee_bps() -> u32;
        /// Get green treasury collected
        fn get_green_treasury_collected() -> Balance;
        /// Get all distribution categories
        fn get_distribution() -> Vec<pallet_tokenomics::DistributionCategory<Balance>>;
        /// Get investor allocation
        fn get_investor_allocation() -> Balance;
    }

    // SudoApi removed — Sudo pallet no longer in runtime (P1-1)

    /// Democracy API for governance transparency
    pub trait DemocracyApi {
        /// Get the total number of referendums ever created
        fn get_referendum_count() -> u32;
        /// Get the lowest active referendum index
        fn get_active_referendum_start() -> u32;
        /// Get all public proposals (index, proposer)
        fn get_public_proposals() -> Vec<(u32, AccountId)>;
        /// Get the minimum deposit required for a proposal
        fn get_minimum_deposit() -> Balance;
    }

    /// Council API for governance transparency
    pub trait CouncilApi {
        /// Get all council members
        fn get_members() -> Vec<AccountId>;
        /// Get all active proposal hashes
        fn get_proposals() -> Vec<Hash>;
        /// Get the number of active proposals
        fn get_proposal_count() -> u32;
        /// Get the prime member (if any)
        fn get_prime() -> Option<AccountId>;
    }
}

// Register production Verdis pallet benchmarks for the freestanding FRAME bencher.
#[cfg(feature = "runtime-benchmarks")]
frame_benchmarking::define_benchmarks!(
    [pallet_dpos, Dpos]
    [pallet_amm_dex, AmmDex]
    [pallet_eco, Eco]
    [pallet_tokenomics, Tokenomics]
    [pallet_vesting, Vesting]
    [pallet_fungible_tokens, FungibleTokens]
    [pallet_storage, Storage]
    [pallet_circuit_breaker, CircuitBreaker]
    [pallet_gulf_stream, GulfStream]
    [pallet_address_lookup_tables, AddressLookupTables]
    [pallet_presale, Presale]
    [pallet_sealevel, Sealevel]
    [pallet_turbine, Turbine]
    [pallet_zk_compression, ZkCompression]
);

// === Runtime API Implementation ===
/// Converts a raw Ethereum transaction into a Verdis extrinsic.
///
/// fc-rpc needs this to accept eth_sendRawTransaction: the wallet sends RLP-encoded Ethereum
/// bytes, which must become a `pallet_ethereum::transact` call carried by a self-contained
/// extrinsic.
/// NOTE: only ONE ConvertTransaction impl is needed here. `opaque::Block` is built from
/// `super::UncheckedExtrinsic`, i.e. this runtime does not define a separate opaque
/// extrinsic type the way Frontier's template does, so a second impl would be the same
/// type twice (E0119).
#[derive(Clone)]
pub struct TransactionConverter;

impl fp_rpc::ConvertTransaction<UncheckedExtrinsic> for TransactionConverter {
    fn convert_transaction(&self, transaction: ethereum::TransactionV3) -> UncheckedExtrinsic {
        UncheckedExtrinsic::new_bare(
            pallet_ethereum::Call::<Runtime>::transact { transaction }.into(),
        )
    }
}

impl_runtime_apis! {
    impl crate::AmmDexApi<Block> for Runtime {
        fn get_pool(pool_id: u32) -> Option<pallet_amm_dex::Pool<AccountId, Balance>> {
            pallet_amm_dex::Pools::<Runtime>::get(pool_id)
        }
        fn get_pool_count() -> u32 {
            pallet_amm_dex::PoolCount::<Runtime>::get()
        }
        fn get_all_pools() -> Vec<pallet_amm_dex::Pool<AccountId, Balance>> {
            let count = pallet_amm_dex::PoolCount::<Runtime>::get();
            (0..count)
                .filter_map(|i| pallet_amm_dex::Pools::<Runtime>::get(i))
                .collect()
        }
        fn get_token_pool(pool_id: u32) -> Option<pallet_amm_dex::TokenPool<AccountId, Balance>> {
            pallet_amm_dex::TokenPools::<Runtime>::get(pool_id)
        }
        fn get_token_pool_count() -> u32 {
            pallet_amm_dex::TokenPoolCount::<Runtime>::get()
        }
        fn get_all_token_pools() -> Vec<pallet_amm_dex::TokenPool<AccountId, Balance>> {
            let count = pallet_amm_dex::TokenPoolCount::<Runtime>::get();
            (0..count)
                .filter_map(|i| pallet_amm_dex::TokenPools::<Runtime>::get(i))
                .collect()
        }
        fn get_liquidity(pool_id: u32, account: AccountId) -> Balance {
            pallet_amm_dex::Pallet::<Runtime>::user_lp(pool_id, &account)
        }
        fn get_token_liquidity(pool_id: u32, account: AccountId) -> Balance {
            pallet_amm_dex::TokenLiquidityProviders::<Runtime>::get(pool_id, &account).unwrap_or(0)
        }
        fn get_price(pool_id: u32, _token: Vec<u8>) -> Option<Balance> {
            pallet_amm_dex::Pallet::<Runtime>::pool_price(pool_id)
        }
        fn get_swap_quote(pool_id: u32, token_in: Vec<u8>, amount_in: Balance) -> Option<Balance> {
            let pool = pallet_amm_dex::Pools::<Runtime>::get(pool_id)?;
            let token_in_bv: frame_support::BoundedVec<u8, ConstU32<32>> = token_in.try_into().ok()?;
            let (reserve_in, reserve_out) = if token_in_bv == pool.token_a {
                (pool.reserve_a, pool.reserve_b)
            } else if token_in_bv == pool.token_b {
                (pool.reserve_b, pool.reserve_a)
            } else {
                return None;
            };
            let fee_num: u128 = pool.fee_numerator as u128;
            let fee = amount_in.checked_mul(fee_num)? / pool.fee_denominator as u128;
            let amount_in_after_fee = amount_in.checked_sub(fee)?;
            let numerator = reserve_out.checked_mul(amount_in_after_fee)?;
            let denominator = reserve_in.checked_add(amount_in_after_fee)?;
            let amount_out = numerator.checked_div(denominator)?;
            if amount_out == 0 { return None; }
            Some(amount_out)
        }
    }

    impl sp_api::Core<Block> for Runtime {
        fn version() -> RuntimeVersion {
            VERSION
        }
        fn execute_block(block: <Block as BlockT>::LazyBlock) {
            Executive::execute_block(block);
        }
        fn initialize_block(header: &<Block as BlockT>::Header) -> ExtrinsicInclusionMode {
            Executive::initialize_block(header)
        }
    }

    impl sp_api::Metadata<Block> for Runtime {
        fn metadata() -> OpaqueMetadata {
            OpaqueMetadata::new(Runtime::metadata().into())
        }
        fn metadata_at_version(version: u32) -> Option<OpaqueMetadata> {
            Runtime::metadata_at_version(version)
        }
        fn metadata_versions() -> Vec<u32> {
            Runtime::metadata_versions()
        }
    }

    impl sp_block_builder::BlockBuilder<Block> for Runtime {
        fn apply_extrinsic(extrinsic: <Block as BlockT>::Extrinsic) -> ApplyExtrinsicResult {
            Executive::apply_extrinsic(extrinsic)
        }
        fn finalize_block() -> <Block as BlockT>::Header {
            Executive::finalize_block()
        }
        fn inherent_extrinsics(data: sp_inherents::InherentData) -> Vec<<Block as BlockT>::Extrinsic> {
            data.create_extrinsics()
        }
        fn check_inherents(
            block: <Block as BlockT>::LazyBlock,
            data: sp_inherents::InherentData,
        ) -> sp_inherents::CheckInherentsResult {
            data.check_extrinsics(&block)
        }
    }

    impl sp_transaction_pool::runtime_api::TaggedTransactionQueue<Block> for Runtime {
        fn validate_transaction(
            source: TransactionSource,
            tx: <Block as BlockT>::Extrinsic,
            block_hash: <Block as BlockT>::Hash,
        ) -> TransactionValidity {
            Executive::validate_transaction(source, tx, block_hash)
        }
    }

    impl sp_offchain::OffchainWorkerApi<Block> for Runtime {
        fn offchain_worker(header: &<Block as BlockT>::Header) {
            Executive::offchain_worker(header)
        }
    }

    impl sp_session::SessionKeys<Block> for Runtime {
        fn generate_session_keys(owner: Vec<u8>, seed: Option<Vec<u8>>) -> sp_session::OpaqueGeneratedSessionKeys {
            SessionKeys::generate(&owner, seed).into()
        }
        fn decode_session_keys(
            encoded: Vec<u8>,
        ) -> Option<Vec<(Vec<u8>, KeyTypeId)>> {
            SessionKeys::decode_into_raw_public_keys(&encoded)
        }
    }

    impl sp_consensus_babe::BabeApi<Block> for Runtime {
        fn configuration() -> sp_consensus_babe::BabeConfiguration {
            sp_consensus_babe::BabeConfiguration {
                slot_duration: Babe::slot_duration(),
                epoch_length: <Runtime as pallet_babe::Config>::EpochDuration::get(),
                c: (255, 256),
                authorities: Babe::authorities().into_iter().map(|x| x.into()).collect(),
                randomness: Babe::randomness().into(),
                allowed_slots: sp_consensus_babe::AllowedSlots::PrimaryAndSecondaryPlainSlots,
            }
        }
        fn current_epoch_start() -> sp_consensus_babe::Slot {
            Babe::current_epoch_start()
        }
        fn current_epoch() -> sp_consensus_babe::Epoch {
            Babe::current_epoch()
        }
        fn next_epoch() -> sp_consensus_babe::Epoch {
            Babe::next_epoch()
        }
        fn generate_key_ownership_proof(
            _slot: sp_consensus_babe::Slot,
            authority_id: sp_consensus_babe::AuthorityId,
        ) -> Option<sp_consensus_babe::OpaqueKeyOwnershipProof> {
            use codec::Encode;
            use frame_support::traits::KeyOwnerProofSystem;
            Historical::prove((sp_consensus_babe::KEY_TYPE, authority_id))
                .map(|p| p.encode())
                .map(sp_consensus_babe::OpaqueKeyOwnershipProof::new)
        }
        fn submit_report_equivocation_unsigned_extrinsic(
            _equivocation_proof: sp_consensus_babe::EquivocationProof<<Block as BlockT>::Header>,
            _key_owner_proof: sp_consensus_babe::OpaqueKeyOwnershipProof,
        ) -> Option<()> {
            let _ = (_equivocation_proof, _key_owner_proof);
            Some(())
        }
    }

    impl sp_consensus_grandpa::GrandpaApi<Block> for Runtime {
        fn grandpa_authorities() -> sp_consensus_grandpa::AuthorityList {
            Grandpa::grandpa_authorities()
        }
        fn current_set_id() -> sp_consensus_grandpa::SetId {
            Grandpa::current_set_id()
        }
        fn submit_report_equivocation_unsigned_extrinsic(
            _equivocation: sp_consensus_grandpa::EquivocationProof<
                <Block as BlockT>::Hash,
                NumberFor<Block>,
            >,
            _key_owner: sp_consensus_grandpa::OpaqueKeyOwnershipProof,
        ) -> Option<()> {
            let _ = (_equivocation, _key_owner);
            Some(())
        }
        fn generate_key_ownership_proof(
            _set_id: sp_consensus_grandpa::SetId,
            authority_id: sp_consensus_grandpa::AuthorityId,
        ) -> Option<sp_consensus_grandpa::OpaqueKeyOwnershipProof> {
            use codec::Encode;
            use frame_support::traits::KeyOwnerProofSystem;
            Historical::prove((sp_consensus_grandpa::KEY_TYPE, authority_id))
                .map(|p| p.encode())
                .map(sp_consensus_grandpa::OpaqueKeyOwnershipProof::new)
        }
    }

    impl frame_system_rpc_runtime_api::AccountNonceApi<Block, AccountId, u32> for Runtime {
        fn account_nonce(account: AccountId) -> u32 {
            System::account_nonce(account)
        }
    }

    impl pallet_transaction_payment_rpc_runtime_api::TransactionPaymentApi<
        Block,
        Balance,
    > for Runtime {
        fn query_info(
            uxt: <Block as BlockT>::Extrinsic,
            len: u32,
        ) -> pallet_transaction_payment_rpc_runtime_api::RuntimeDispatchInfo<Balance> {
            TransactionPayment::query_info(uxt, len)
        }
        fn query_length_to_fee(length: u32) -> Balance {
            TransactionPayment::length_to_fee(length)
        }
        fn query_weight_to_fee(weight: Weight) -> Balance {
            TransactionPayment::weight_to_fee(weight)
        }
        fn query_fee_details(uxt: <Block as BlockT>::Extrinsic, len: u32) -> pallet_transaction_payment_rpc_runtime_api::FeeDetails<Balance> {
            TransactionPayment::query_fee_details(uxt, len)
        }
    }

    impl crate::ContractsApi<Block>
    for Runtime {
        fn call(
            origin: AccountId,
            dest: AccountId,
            value: Balance,
            gas_limit: Option<frame_support::weights::Weight>,
            storage_deposit_limit: Option<Balance>,
            input_data: Vec<u8>,
        ) -> pallet_contracts::ContractExecResult<Balance, frame_system::EventRecord<RuntimeEvent, Hash>> {
            Contracts::bare_call(
                origin,
                dest,
                value,
                gas_limit.unwrap_or(frame_support::weights::Weight::MAX),
                storage_deposit_limit,
                input_data,
                pallet_contracts::DebugInfo::Skip,
                pallet_contracts::CollectEvents::Skip,
                pallet_contracts::Determinism::Enforced,
            )
        }

        fn instantiate(
            origin: AccountId,
            value: Balance,
            gas_limit: Option<frame_support::weights::Weight>,
            storage_deposit_limit: Option<Balance>,
            code: pallet_contracts::Code<Hash>,
            data: Vec<u8>,
            salt: Vec<u8>,
        ) -> pallet_contracts::ContractInstantiateResult<AccountId, Balance, frame_system::EventRecord<RuntimeEvent, Hash>> {
            Contracts::bare_instantiate(
                origin,
                value,
                gas_limit.unwrap_or(frame_support::weights::Weight::MAX),
                storage_deposit_limit,
                code,
                data,
                salt,
                pallet_contracts::DebugInfo::Skip,
                pallet_contracts::CollectEvents::Skip,
            )
        }

        fn upload_code(
            origin: AccountId,
            code: Vec<u8>,
            storage_deposit_limit: Option<Balance>,
        ) -> pallet_contracts::CodeUploadResult<Hash, Balance> {
            Contracts::bare_upload_code(
                origin,
                code,
                storage_deposit_limit,
                pallet_contracts::Determinism::Enforced,
            )
        }

        fn get_storage(
            address: AccountId,
            key: Vec<u8>,
        ) -> pallet_contracts::GetStorageResult {
            Contracts::get_storage(address, key)
        }
    }

    #[cfg(feature = "runtime-benchmarks")]
    impl frame_benchmarking::Benchmark<Block> for Runtime {
        fn benchmark_metadata(extra: bool) -> (
            Vec<frame_benchmarking::BenchmarkList>,
            Vec<frame_support::traits::StorageInfo>,
        ) {
            use frame_benchmarking::BenchmarkList;
            use frame_support::traits::StorageInfoTrait;

            let mut list = Vec::<BenchmarkList>::new();
            list_benchmarks!(list, extra);
            let storage_info = AllPalletsWithSystem::storage_info();
            (list, storage_info)
        }

        #[allow(non_local_definitions)]
        fn dispatch_benchmark(
            config: frame_benchmarking::BenchmarkConfig,
        ) -> Result<Vec<frame_benchmarking::BenchmarkBatch>, alloc::string::String> {
            use frame_benchmarking::BenchmarkBatch;
            use frame_support::traits::WhitelistedStorageKeys;

            let whitelist = AllPalletsWithSystem::whitelisted_storage_keys();
            let mut batches = Vec::<BenchmarkBatch>::new();
            let params = (&config, &whitelist);
            add_benchmarks!(params, batches);
            Ok(batches)
        }
    }

    impl crate::DposApi<Block> for Runtime {
        fn active_validators() -> Vec<AccountId> {
            pallet_dpos::ActiveValidators::<Runtime>::get().into_inner()
        }

        fn all_validators() -> Vec<AccountId> {
            pallet_dpos::Validators::<Runtime>::iter().map(|(v, _)| v).collect()
        }
        fn validator_stake(validator: AccountId) -> Balance {
            pallet_dpos::Validators::<Runtime>::get(&validator).map(|s| s.stake).unwrap_or(0)
        }
        fn current_epoch() -> u32 {
            pallet_dpos::CurrentEpoch::<Runtime>::get()
        }
        fn get_validator_name(validator: AccountId) -> Option<Vec<u8>> {
            pallet_dpos::ValidatorNames::<Runtime>::get(&validator).map(|n| n.to_vec())
        }
        fn session_index() -> u32 {
            pallet_session::Pallet::<Runtime>::current_index()
        }
        fn get_all_validators_detailed() -> Vec<pallet_dpos::Validator<AccountId, Balance>> {
            pallet_dpos::Validators::<Runtime>::iter()
                .map(|(addr, v)| {
                    let mut v = v;
                    v.address = addr;
                    v
                })
                .collect()
        }
    }

    impl crate::EcoApi<Block> for Runtime {
        fn get_total_co2_offset() -> u64 {
            pallet_eco::TotalCO2Offset::<Runtime>::get()
        }
        fn get_total_trees_planted() -> u32 {
            pallet_eco::TotalTreesPlanted::<Runtime>::get()
        }
        fn get_total_credits_retired() -> u64 {
            pallet_eco::TotalCreditsRetired::<Runtime>::get()
        }
        fn get_carbon_credit_count() -> u32 {
            pallet_eco::CarbonCredits::<Runtime>::iter().count() as u32
        }
        fn get_reforest_project_count() -> u32 {
            pallet_eco::ReforestProjects::<Runtime>::iter().count() as u32
        }
        fn get_green_validator_count() -> u32 {
            pallet_eco::GreenValidators::<Runtime>::iter().count() as u32
        }
        fn get_green_score(validator: AccountId) -> Option<u8> {
            pallet_eco::GreenValidators::<Runtime>::get(&validator).map(|gv| gv.score)
        }
        fn get_all_green_validators() -> Vec<(AccountId, u8)> {
            pallet_eco::GreenValidators::<Runtime>::iter().map(|(addr, gv)| (addr, gv.score)).collect()
        }
        fn get_all_carbon_credits() -> Vec<pallet_eco::CarbonCredit<AccountId>> {
            pallet_eco::CarbonCredits::<Runtime>::iter().map(|(_, cc)| cc).collect()
        }
        fn get_all_reforest_projects() -> Vec<pallet_eco::ReforestProject> {
            pallet_eco::ReforestProjects::<Runtime>::iter().map(|(_, rp)| rp).collect()
        }
        fn get_all_green_validators_detailed() -> Vec<pallet_eco::GreenValidator<AccountId>> {
            pallet_eco::GreenValidators::<Runtime>::iter().map(|(_, gv)| gv).collect()
        }
    }

    impl crate::TokenomicsApi<Block> for Runtime {
        fn get_total_supply() -> Balance {
            pallet_tokenomics::TotalSupply::<Runtime>::get()
        }
        fn get_circulating_supply() -> Balance {
            pallet_tokenomics::CirculatingSupply::<Runtime>::get()
        }
        fn get_presale_price() -> u32 {
            pallet_tokenomics::PresalePrice::<Runtime>::get()
        }
        fn get_presale_raised() -> Balance {
            pallet_tokenomics::PresaleRaised::<Runtime>::get()
        }
        fn get_presale_sold() -> Balance {
            pallet_tokenomics::PresaleSold::<Runtime>::get()
        }
        fn get_transfer_fee_bps() -> u32 {
            pallet_tokenomics::TransferFeeBps::<Runtime>::get()
        }
        fn get_green_treasury_collected() -> Balance {
            pallet_tokenomics::GreenTreasuryCollected::<Runtime>::get()
        }
        fn get_distribution() -> Vec<pallet_tokenomics::DistributionCategory<Balance>> {
            pallet_tokenomics::Distribution::<Runtime>::iter().map(|(_, d)| d).collect()
        }
        fn get_investor_allocation() -> Balance {
            pallet_tokenomics::InvestorAllocationStorage::<Runtime>::get()
        }
    }

    // SudoApi impl removed — Sudo pallet no longer in runtime (P1-1)

    impl crate::DemocracyApi<Block> for Runtime {
        fn get_referendum_count() -> u32 {
            pallet_democracy::ReferendumCount::<Runtime>::get()
        }

        fn get_active_referendum_start() -> u32 {
            pallet_democracy::LastTabledWasExternal::<Runtime>::get()
                .then(|| 0)
                .unwrap_or(0)
        }

        fn get_public_proposals() -> Vec<(u32, AccountId)> {
            pallet_democracy::PublicProps::<Runtime>::get()
                .to_vec()
                .into_iter()
                .map(|(idx, _bounded_call, proposer)| (idx, proposer))
                .collect()
        }

        fn get_minimum_deposit() -> Balance {
            <Runtime as pallet_democracy::Config>::MinimumDeposit::get()
        }
    }

    impl crate::CouncilApi<Block> for Runtime {
        fn get_members() -> Vec<AccountId> {
            pallet_collective::Members::<Runtime, pallet_collective::Instance1>::get().to_vec()
        }

        fn get_proposals() -> Vec<Hash> {
            pallet_collective::Proposals::<Runtime, pallet_collective::Instance1>::get().to_vec()
        }

        fn get_proposal_count() -> u32 {
            pallet_collective::Proposals::<Runtime, pallet_collective::Instance1>::get().to_vec().len() as u32
        }

        fn get_prime() -> Option<AccountId> {
            pallet_collective::Prime::<Runtime, pallet_collective::Instance1>::get()
        }
    }

    impl sp_genesis_builder::GenesisBuilder<Block> for Runtime {
        fn build_state(json: Vec<u8>) -> sp_genesis_builder::Result {
            frame_support::genesis_builder_helper::build_state::<RuntimeGenesisConfig>(json)
        }

        fn get_preset(
            id: &Option<sp_genesis_builder::PresetId>,
        ) -> Option<Vec<u8>> {
            frame_support::genesis_builder_helper::get_preset::<RuntimeGenesisConfig>(
                id,
                |_| None,
            )
        }

        fn preset_names() -> Vec<sp_genesis_builder::PresetId> {
            Default::default()
        }
    }

    impl fp_rpc::EthereumRuntimeRPCApi<Block> for Runtime {
        fn chain_id() -> u64 {
            <Runtime as pallet_evm::Config>::ChainId::get()
        }

        fn account_basic(address: H160) -> pallet_evm::Account {
            let (account, _) = pallet_evm::Pallet::<Runtime>::account_basic(&address);
            account
        }

        fn gas_price() -> U256 {
            let (gas_price, _) = <Runtime as pallet_evm::Config>::FeeCalculator::min_gas_price();
            gas_price
        }

        fn account_code_at(address: H160) -> Vec<u8> {
            pallet_evm::AccountCodes::<Runtime>::get(address)
        }

        fn author() -> H160 {
            <pallet_evm::Pallet<Runtime>>::find_author()
        }

        fn storage_at(address: H160, index: U256) -> H256 {
            let tmp: [u8; 32] = index.to_big_endian();
            pallet_evm::AccountStorages::<Runtime>::get(address, H256::from_slice(&tmp[..]))
        }

        fn call(
            from: H160,
            to: H160,
            data: Vec<u8>,
            value: U256,
            gas_limit: U256,
            max_fee_per_gas: Option<U256>,
            max_priority_fee_per_gas: Option<U256>,
            nonce: Option<U256>,
            estimate: bool,
            access_list: Option<Vec<(H160, Vec<H256>)>>,
            authorization_list: Option<ethereum::AuthorizationList>,
            state_override: fp_evm::StateOverride,
        ) -> Result<pallet_evm::CallInfo, sp_runtime::DispatchError> {
            let config = if estimate {
                let mut config = <Runtime as pallet_evm::Config>::config().clone();
                config.estimate = true;
                Some(config)
            } else {
                None
            };

            let gas_limit = gas_limit.min(u64::MAX.into());
            <Runtime as pallet_evm::Config>::Runner::call(
                from,
                to,
                data,
                value,
                gas_limit.unique_saturated_into(),
                max_fee_per_gas,
                max_priority_fee_per_gas,
                nonce,
                access_list.unwrap_or_default(),
                authorization_list.unwrap_or_default(),
                false,
                true,
                None,
                None,
                state_override,
                config.as_ref().unwrap_or(<Runtime as pallet_evm::Config>::config()),
            )
            .map_err(|err| err.error.into())
        }

        fn create(
            from: H160,
            data: Vec<u8>,
            value: U256,
            gas_limit: U256,
            max_fee_per_gas: Option<U256>,
            max_priority_fee_per_gas: Option<U256>,
            nonce: Option<U256>,
            estimate: bool,
            access_list: Option<Vec<(H160, Vec<H256>)>>,
            authorization_list: Option<ethereum::AuthorizationList>,
        ) -> Result<pallet_evm::CreateInfo, sp_runtime::DispatchError> {
            let config = if estimate {
                let mut config = <Runtime as pallet_evm::Config>::config().clone();
                config.estimate = true;
                Some(config)
            } else {
                None
            };

            let gas_limit = gas_limit.min(u64::MAX.into());
            <Runtime as pallet_evm::Config>::Runner::create(
                from,
                data,
                value,
                gas_limit.unique_saturated_into(),
                max_fee_per_gas,
                max_priority_fee_per_gas,
                nonce,
                access_list.unwrap_or_default(),
                authorization_list.unwrap_or_default(),
                false,
                true,
                None,
                None,
                config.as_ref().unwrap_or(<Runtime as pallet_evm::Config>::config()),
            )
            .map_err(|err| err.error.into())
        }

        fn current_transaction_statuses() -> Option<Vec<TransactionStatus>> {
            pallet_ethereum::CurrentTransactionStatuses::<Runtime>::get()
        }

        fn current_block() -> Option<ethereum::BlockV3> {
            pallet_ethereum::CurrentBlock::<Runtime>::get()
        }

        fn current_receipts() -> Option<Vec<ethereum::ReceiptV4>> {
            pallet_ethereum::CurrentReceipts::<Runtime>::get()
        }

        fn current_all() -> (
            Option<ethereum::BlockV3>,
            Option<Vec<ethereum::ReceiptV4>>,
            Option<Vec<TransactionStatus>>,
        ) {
            (
                pallet_ethereum::CurrentBlock::<Runtime>::get(),
                pallet_ethereum::CurrentReceipts::<Runtime>::get(),
                pallet_ethereum::CurrentTransactionStatuses::<Runtime>::get(),
            )
        }

        fn extrinsic_filter(
            xts: Vec<<Block as BlockT>::Extrinsic>,
        ) -> Vec<ethereum::TransactionV3> {
            xts.into_iter()
                .filter_map(|xt| match xt.0.function {
                    RuntimeCall::Ethereum(pallet_ethereum::Call::transact { transaction }) => {
                        Some(transaction)
                    }
                    _ => None,
                })
                .collect::<Vec<ethereum::TransactionV3>>()
        }

        fn elasticity() -> Option<Permill> {
            Some(pallet_base_fee::Elasticity::<Runtime>::get())
        }

        fn gas_limit_multiplier_support() {}

        fn pending_block(
            xts: Vec<<Block as BlockT>::Extrinsic>,
        ) -> (Option<ethereum::BlockV3>, Option<Vec<TransactionStatus>>) {
            for ext in xts.into_iter() {
                let _ = Executive::apply_extrinsic(ext);
            }
            <pallet_ethereum::Pallet<Runtime> as frame_support::traits::Hooks<BlockNumber>>::on_finalize(
                System::block_number() + 1,
            );
            (
                pallet_ethereum::CurrentBlock::<Runtime>::get(),
                pallet_ethereum::CurrentTransactionStatuses::<Runtime>::get(),
            )
        }

        fn initialize_pending_block(header: &<Block as BlockT>::Header) {
            Executive::initialize_block(header);
        }
    }

    impl fp_rpc::ConvertTransactionRuntimeApi<Block> for Runtime {
        fn convert_transaction(
            transaction: ethereum::TransactionV3,
        ) -> <Block as BlockT>::Extrinsic {
            UncheckedExtrinsic::new_bare(
                pallet_ethereum::Call::<Runtime>::transact { transaction }.into(),
            )
        }
    }
}

#[cfg(all(test, feature = "try-runtime"))]
mod try_runtime_tests {
    use super::*;
    use sp_runtime::BuildStorage;

    fn new_test_ext() -> sp_io::TestExternalities {
        sp_io::TestExternalities::new(sp_runtime::Storage::default())
    }

    #[test]
    fn try_runtime_upgrade_succeeds() {
        new_test_ext().execute_with(|| {
            let weight = Executive::execute_on_runtime_upgrade();
            assert!(
                weight != frame_support::weights::Weight::zero(),
                "Runtime upgrade should consume weight"
            );
        });
    }
}
// Force rebuild 1787380805

#[cfg(test)]
mod evm_integration_tests {
    //! Tests for the EVM layer as configured on THIS chain.
    //!
    //! These do not re-test pallet-evm's internals - upstream Frontier covers that. They test the
    //! decisions specific to adding an EVM to a live Substrate chain, where getting the address
    //! mapping or replay protection wrong would be unrecoverable.

    use super::*;
    use sp_core::{H160, U256};

    #[test]
    fn migration_sets_chain_id_on_upgrade() {
        // Regression test for a bug found live on testnet: after upgrading spec 17 -> 18, the EVM was
        // active and producing blocks but `eth_chainId` answered 0x0.
        //
        // Cause: a runtime upgrade never executes `GenesisConfig` - genesis runs only at block 0. A
        // pallet introduced by `set_code` therefore starts with EMPTY storage, and
        // `pallet-evm-chain-id`'s value read as its default of 0. An EVM answering chain id 0 lets
        // transactions be replayed against any other chain reporting 0, so this is a security bug,
        // not a cosmetic one.
        //
        // `chain_id_is_414` cannot catch it: that test BUILDS genesis, which is the case that already
        // worked. This test starts from empty storage - the upgrade case - and runs the migration.
        use frame_support::traits::OnRuntimeUpgrade;

        let mut ext: sp_io::TestExternalities = Default::default();

        ext.execute_with(|| {
            // upgrade case: nothing in storage, exactly as after set_code
            assert_eq!(
                pallet_evm_chain_id::ChainId::<Runtime>::get(),
                0u64,
                "storage must start empty to reproduce the upgrade case"
            );

            SetEvmChainId::on_runtime_upgrade();

            assert_eq!(
                pallet_evm_chain_id::ChainId::<Runtime>::get(),
                VERDIS_EVM_CHAIN_ID,
                "migration must write the chain id when storage is empty"
            );
            assert_eq!(
                <Runtime as pallet_evm::Config>::ChainId::get(),
                414u64,
                "eth_chainId must report 414 after the migration"
            );
        });
    }

    #[test]
    fn migration_is_idempotent() {
        // Governance can change the chain id through `System::set_storage`. If the migration ever ran
        // again it must NOT overwrite that decision, otherwise a later upgrade would silently revert
        // a governance action.
        use frame_support::traits::OnRuntimeUpgrade;

        let mut ext: sp_io::TestExternalities = Default::default();

        ext.execute_with(|| {
            pallet_evm_chain_id::ChainId::<Runtime>::put(999u64);

            SetEvmChainId::on_runtime_upgrade();

            assert_eq!(
                pallet_evm_chain_id::ChainId::<Runtime>::get(),
                999u64,
                "migration must not overwrite an already-set chain id"
            );
        });
    }

    #[test]
    fn chain_id_is_414() {
        // 414 is unregistered in chainid.network/chains.json - the registry MetaMask, Rabby and
        // Trust all read. 909 belongs to "Portal Fantasy Chain", so a wallet that already has
        // that network would reject Verdis on a chainId clash, and transactions signed for one
        // could be replayed on the other if it ever launches.
        //
        // SS58 stays 909: a DIFFERENT registry with no conflict. Changing it would re-derive
        // every ki... address, every balance storage key and all 21 validator accounts.
        //
        // The chain id lives in pallet-evm-chain-id's STORAGE, seeded from genesis - not in a
        // const. So this test builds genesis and reads it back through the same path
        // eth_chainId uses; a chain_spec/runtime mismatch would fail here.
        use sp_runtime::BuildStorage;

        let genesis = RuntimeGenesisConfig {
            evm_chain_id: EVMChainIdConfig {
                chain_id: 414,
                ..Default::default()
            },
            ..Default::default()
        };
        let storage = genesis.build_storage().expect("genesis builds");
        let mut ext: sp_io::TestExternalities = storage.into();

        ext.execute_with(|| {
            assert_eq!(
                <Runtime as pallet_evm::Config>::ChainId::get(),
                414u64,
                "eth_chainId must report 414"
            );
        });

        // SS58Prefix is a compile-time constant, readable without externalities.
        assert_eq!(<Runtime as frame_system::Config>::SS58Prefix::get(), 909u16);
    }

    #[test]
    fn h160_maps_deterministically_to_account_id32() {
        // The mapping must be a pure function of the address: the same H160 always yields the
        // same AccountId32, or funds sent to an Ethereum address would land in different
        // Substrate accounts on different calls.
        //
        // Runs inside TestExternalities because AddressMapping is now LinkedAddressMapping, which
        // READS the link table. HashedAddressMapping needed no storage; this one does, and a test
        // without externalities panics in sp-io rather than failing an assertion.
        use pallet_evm::AddressMapping;
        let mut ext: sp_io::TestExternalities = Default::default();
        ext.execute_with(|| {
            let addr = H160::from_low_u64_be(0x1234_5678);
            let a = <Runtime as pallet_evm::Config>::AddressMapping::into_account_id(addr);
            let b = <Runtime as pallet_evm::Config>::AddressMapping::into_account_id(addr);
            assert_eq!(a, b, "H160 -> AccountId32 mapping is not deterministic");
        });
    }

    #[test]
    fn unbound_address_keeps_the_hashed_fallback() {
        // Replacing HashedAddressMapping must not change behaviour for addresses nobody has bound,
        // otherwise enabling the pallet would move existing EVM balances. The fallback must stay
        // exactly blake2_256("evm:" ++ address).
        use pallet_evm::AddressMapping;
        let mut ext: sp_io::TestExternalities = Default::default();
        ext.execute_with(|| {
            let addr = H160::from_low_u64_be(0xdead_beef);
            let got = <Runtime as pallet_evm::Config>::AddressMapping::into_account_id(addr);

            let mut data = [0u8; 24];
            data[0..4].copy_from_slice(b"evm:");
            data[4..24].copy_from_slice(&addr[..]);
            let expected = AccountId::from(sp_io::hashing::blake2_256(&data));

            assert_eq!(
                got, expected,
                "an unbound address must keep the historical hashed mapping"
            );
        });
    }

    #[test]
    fn resolves_bound_address_to_owner() {
        // The property the whole pallet exists for: once an account has bound an EVM address, the
        // EVM resolves that address to the OWNER's account, so MetaMask and the Verdis wallet share
        // one balance. Before this, funds sent from MetaMask landed on a hashed account with no
        // private key - measured on testnet, 100 VRDX became unspendable that way.
        use pallet_evm::AddressMapping;
        let mut ext: sp_io::TestExternalities = Default::default();
        ext.execute_with(|| {
            let addr = H160::from_low_u64_be(0xabc_def);
            let owner = AccountId::from([9u8; 32]);

            // Write the mapping directly: this test covers the EVM-side resolution, while signature
            // verification is covered by the pallet's own 17 tests.
            pallet_verdis_account_link::AccountIdOf::<Runtime>::insert(addr, owner.clone());

            let got = <Runtime as pallet_evm::Config>::AddressMapping::into_account_id(addr);
            assert_eq!(got, owner, "a bound address must resolve to its owner");

            let mut data = [0u8; 24];
            data[0..4].copy_from_slice(b"evm:");
            data[4..24].copy_from_slice(&addr[..]);
            let mirror = AccountId::from(sp_io::hashing::blake2_256(&data));
            assert_ne!(
                got, mirror,
                "a bound address must NOT resolve to the hashed mirror"
            );
        });
    }

    #[test]
    fn distinct_h160_give_distinct_accounts() {
        // Two different Ethereum addresses must never share a Substrate account, otherwise one
        // user could spend another's balance.
        use pallet_evm::AddressMapping;
        let mut ext: sp_io::TestExternalities = Default::default();
        ext.execute_with(|| {
            let a = <Runtime as pallet_evm::Config>::AddressMapping::into_account_id(
                H160::from_low_u64_be(1),
            );
            let b = <Runtime as pallet_evm::Config>::AddressMapping::into_account_id(
                H160::from_low_u64_be(2),
            );
            assert_ne!(a, b);
        });
    }

    #[test]
    fn unprotected_transactions_are_rejected() {
        // Pre-EIP-155 transactions carry no chain id and are replayable across networks: a
        // transaction signed for Ethereum mainnet could otherwise execute here.
        assert!(!<<Runtime as pallet_ethereum::Config>::AllowUnprotectedTxs
            as frame_support::traits::Get<bool>>::get(),
                "pre-EIP-155 transactions must not be accepted");
    }

    #[test]
    fn block_gas_limit_is_set_and_finite() {
        let limit = <Runtime as pallet_evm::Config>::BlockGasLimit::get();
        assert!(
            limit > U256::zero(),
            "a zero block gas limit would reject every EVM call"
        );
        assert_eq!(limit, U256::from(15_000_000u64));
    }

    #[test]
    fn no_per_transaction_gas_cap_beyond_the_block() {
        // Ethereum semantics: a transaction is bounded by the block gas limit, not a separate cap.
        assert_eq!(
            <Runtime as pallet_evm::Config>::TransactionGasLimit::get(),
            None
        );
    }

    #[test]
    fn existing_pallets_survived_the_addition() {
        // Adding pallets must not disturb what mainnet already runs. Contracts (ink!) is live on
        // mainnet with a deployed token, so its index must not move.
        use frame_support::traits::PalletInfoAccess;
        assert_eq!(<Contracts as PalletInfoAccess>::index(), 20);
        assert_eq!(<Balances as PalletInfoAccess>::index(), 4);
        assert_eq!(<Council as PalletInfoAccess>::index(), 43);
        assert_eq!(<Democracy as PalletInfoAccess>::index(), 44);
        // and the new ones sit above every existing index
        assert_eq!(<EVM as PalletInfoAccess>::index(), 63);
        assert_eq!(<Ethereum as PalletInfoAccess>::index(), 62);
    }

    #[test]
    fn spec_version_advanced_past_mainnet() {
        // Mainnet runs 17. An upgrade with an equal or lower version is refused by set_code.
        assert!(
            VERSION.spec_version > 17,
            "spec_version must exceed the live mainnet version (17)"
        );
    }

    #[test]
    fn precompiles_cover_the_ethereum_standard_set() {
        // Solidity contracts and tooling assume addresses 1..8 exist.
        use pallet_evm::PrecompileSet;
        let set = VerdisPrecompiles::<Runtime>::new();
        for i in 1u64..=8 {
            let addr = H160::from_low_u64_be(i);
            match set.is_precompile(addr, 0) {
                pallet_evm::IsPrecompileResult::Answer { is_precompile, .. } => {
                    assert!(is_precompile, "precompile {} is missing", i)
                }
                _ => panic!("unexpected IsPrecompileResult for {}", i),
            }
        }
        // and nothing beyond it is silently a precompile
        match set.is_precompile(H160::from_low_u64_be(9), 0) {
            pallet_evm::IsPrecompileResult::Answer { is_precompile, .. } => {
                assert!(!is_precompile, "address 9 must not be a precompile")
            }
            _ => {}
        }
    }
}
