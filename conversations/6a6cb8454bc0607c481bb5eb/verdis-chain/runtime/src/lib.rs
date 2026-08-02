//! Verdis Chain Runtime — The world's first fully green, carbon-negative blockchain
//!
//! Built with Substrate FRAME, featuring:
//! - Native DPoS consensus (pallet-dpos)
//! - AMM-based DEX (pallet-amm-dex)
//! - Eco-tracking: carbon credits, reforestation, green validator scoring (pallet-eco)
//! - Protocol-level vesting enforcement (pallet-vesting)
//! - Tokenomics with 100B supply and 8-category distribution (pallet-tokenomics)

#![cfg_attr(not(feature = "std"), no_std)]

#[cfg(feature = "std")]
include!(concat!(env!("OUT_DIR"), "/wasm_binary.rs"));

use sp_api::impl_runtime_apis;
use sp_core::{crypto::KeyTypeId, OpaqueMetadata};
use sp_runtime::{
    create_runtime_str, generic, ApplyExtrinsicResult, traits::{
        AccountIdLookup, BlakeTwo256, Block as BlockT, IdentifyAccount, NumberFor, Verify,
    }, transaction_validity::{TransactionSource, TransactionValidity},
    BuildStorage, MultiSignature,
};
use sp_std::prelude::*;
use sp_version::RuntimeVersion;

#[cfg(feature = "std")]
use sp_version::NativeVersion;

// === Pallet Imports ===
use frame_support::{
    construct_runtime, parameter_types,
    traits::{ConstU32, ConstU64, ConstU8, Everything, Randomness},
    weights::{
        constants::{BlockExecutionWeight, ExtrinsicBaseWeight, RocksDbWeight, WEIGHT_REF_TIME_PER_SECOND},
        IdentityFee, Weight, WeightToFee as _,
    },
    PalletId,
};
use frame_system::EnsureRoot;

use pallet_balances::Call as BalancesCall;
use pallet_transaction_payment::CurrencyAdapter;

pub use frame_support::{
    traits::{ConstU128, ConstU32 as C32},
    weights::constants,
};

// === Verdis Custom Pallets ===
pub use pallet_dpos;
pub use pallet_amm_dex;
pub use pallet_eco;
pub use pallet_tokenomics;
pub use pallet_vesting;

// === Type Aliases ===
pub type AccountId = AccountId32;
pub type Balance = u128;
pub type BlockNumber = u32;
pub type Header = generic::Header<BlockNumber, BlakeTwo256>;
pub type Block = generic::Block<Header, UncheckedExtrinsic>;
pub type Index = u32;
pub type Signature = MultiSignature;
pub type AccountId32 = sp_core::sr25519::Public;

use sp_core::sr25519::Signature as Sr25519Signature;

/// Opaque types for the node
pub mod opaque {
    use super::*;
    pub type Block = generic::Block<Header, super::UncheckedExtrinsic>;
    pub type BlockId = generic::BlockId<Block>;
    impl sp_api::BlockT for Block {
        type Extrinsic = UncheckedExtrinsic;
        type Header = Header;
        type Hash = sp_core::H256;
    }
}

// === Runtime Version ===
#[sp_version::runtime_version]
pub const VERSION: RuntimeVersion = RuntimeVersion {
    spec_name: create_runtime_str!("verdis-chain"),
    impl_name: create_runtime_str!("verdis-chain"),
    authoring_version: 1,
    spec_version: 1,
    impl_version: 1,
    apis: RUNTIME_API_VERSIONS,
    transaction_version: 1,
    state_version: 1,
};

/// Native version of the runtime
#[cfg(feature = "std")]
pub fn native_version() -> NativeVersion {
    NativeVersion {
        runtime_version: VERSION,
        can_author_with: Default::default(),
    }
}

// === Constants ===
/// 1 VRDX = 10^9 base units (nano)
pub const UNITS: Balance = 1_000_000_000;
/// Total supply: 100,000,000,000 VRDX
pub const TOTAL_SUPPLY: Balance = 100_000_000_000 * UNITS;
/// Circulating supply: 15,000,000,000 VRDX (15% of total)
pub const CIRCULATING_SUPPLY: Balance = 15_000_000_000 * UNITS;
/// Block time: 5 seconds
pub const BLOCK_TIME: u64 = 5000;
/// Max block weight: 50% of block time for computation
pub const MAX_BLOCK_WEIGHT: Weight = Weight::from_parts(
    WEIGHT_REF_TIME_PER_SECOND.saturating_mul(2),
    constants::MAX_POSSIBLE_PROOF_SIZE,
);

parameter_types! {
    pub const BlockHashCount: BlockNumber = 2400;
    pub const Version: RuntimeVersion = VERSION;
    pub BlockWeights: frame_system::limits::BlockWeights =
        frame_system::limits::BlockWeights::builder()
            .base_block(BlockExecutionWeight::get())
            .for_class(All::get(), |weights| {
                weights.base_block = BlockExecutionWeight::get();
                weights.for_class(All::get(), |weights| {
                    weights.base_extrinsic = ExtrinsicBaseWeight::get();
                });
                weights.max_block = MAX_BLOCK_WEIGHT;
            })
            .build_or_panic();
    pub BlockLength: frame_system::limits::BlockLength =
        frame_system::limits::BlockLength::max_with_normal_noise_ratio(
            constants::NORMAL_DISPATCH_RATIO,
            constants::MAX_POSSIBLE_LENGTH,
        );
    pub const SS58Prefix: u8 = 909; // Chain ID 909
}

// === System Pallet Configuration ===
impl frame_system::Config for Runtime {
    type BaseCallFilter = Everything;
    type BlockWeights = BlockWeights;
    type BlockLength = BlockLength;
    type AccountId = AccountId;
    type Lookup = AccountIdLookup<AccountId, ()>;
    type Index = Index;
    type BlockNumber = BlockNumber;
    type Hash = sp_core::H256;
    type Hashing = BlakeTwo256;
    type Header = Header;
    type RuntimeEvent = RuntimeEvent;
    type RuntimeOrigin = RuntimeOrigin;
    type RuntimeCall = RuntimeCall;
    type BlockHashCount = BlockHashCount;
    type DbWeight = RocksDbWeight;
    type Version = Version;
    type PalletInfo = PalletInfo;
    type AccountData = pallet_balances::AccountData<Balance>;
    type OnNewAccount = ();
    type OnKilledAccount = ();
    type SystemWeightInfo = ();
    type SS58Prefix = SS58Prefix;
    type OnSetCode = ();
    type MaxConsumers = ConstU32<16>;
    type Block = Block;
}

// === Timestamp Pallet ===
impl pallet_timestamp::Config for Runtime {
    type Moment = u64;
    type OnTimestampSet = Aura;
    type MinimumPeriod = ConstU64<{ BLOCK_TIME / 2 }>;
    type WeightInfo = ();
}

// === Aura Consensus (Block Production) ===
impl pallet_aura::Config for Runtime {
    type AuthorityId = pallet_aura::sr25519::AuthorityId;
    type DisabledValidators = ();
    type MaxAuthorities = ConstU32<101>; // Max 101 validators
    type AllowMultipleBlocksPerSlot = frame_support::traits::ConstBool<false>;
    type SlotDuration = ConstU64<BLOCK_TIME>;
}

// === Balances Pallet ===
parameter_types! {
    pub const ExistentialDeposit: Balance = UNITS; // 1 nano minimum
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
    type FreezeIdentifier = ();
    type MaxFreezes = ConstU32<0>;
    type RuntimeHoldReason = ();
    type MaxHolds = ConstU32<0>;
}

// === Transaction Payment ===
parameter_types! {
    pub const TransactionByteFee: Balance = 100_000; // 0.0001 VRDX per byte
    pub const OperationalFeeMultiplier: u8 = 5;
}

impl pallet_transaction_payment::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type OnChargeTransaction = CurrencyAdapter<Balances, ()>;
    type OperationalFeeMultiplier = OperationalFeeMultiplier;
    type WeightToFee = IdentityFee<Balance>;
    type LengthToFee = IdentityFee<Balance>;
    type FeeMultiplierChangeTarget = ();
    type FeeMultiplierUpdate = ();
}

// === Sudo ===
impl pallet_sudo::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type RuntimeCall = RuntimeCall;
    type WeightInfo = pallet_sudo::weights::SubstrateWeight<Runtime>;
}

// === Verdis DPoS Pallet ===
parameter_types! {
    pub const DposPalletId: PalletId = PalletId(*b"verdisdp");
    pub const MinValidatorStake: Balance = 10_000 * UNITS;
    pub const MaxValidators: u32 = 101;
    pub const ValidatorCount: u32 = 5;
    pub const BlockReward: Balance = 16 * UNITS;
    pub const EpochLength: BlockNumber = 100;
    pub const MaxValidatorsPerEpoch: u32 = 5;
}

impl pallet_dpos::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type RuntimeOrigin = RuntimeOrigin;
    type Currency = Balances;
    type BlockReward = BlockReward;
    type MinStake = MinValidatorStake;
    type MaxValidators = MaxValidators;
    type ActiveValidatorCount = ValidatorCount;
    type EpochLength = EpochLength;
    type PalletId = DposPalletId;
    type WeightInfo = pallet_dpos::weights::SubstrateWeight<Runtime>;
}

// === Verdis AMM DEX Pallet ===
parameter_types! {
    pub const DexPalletId: PalletId = PalletId(*b"verdisdx");
    pub const FeeNumerator: u32 = 3; // 0.3%
    pub const FeeDenominator: u32 = 1000;
    pub const MinLiquidity: Balance = 1_000 * UNITS;
    pub const MaxPools: u32 = 50;
}

impl pallet_amm_dex::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type RuntimeOrigin = RuntimeOrigin;
    type Currency = Balances;
    type PalletId = DexPalletId;
    type FeeNumerator = FeeNumerator;
    type FeeDenominator = FeeDenominator;
    type MinLiquidity = MinLiquidity;
    type MaxPools = MaxPools;
    type WeightInfo = pallet_amm_dex::weights::SubstrateWeight<Runtime>;
}

// === Verdis Eco Tracking Pallet ===
parameter_types! {
    pub const EcoPalletId: PalletId = PalletId(*b"verdisec");
    pub const MaxCarbonCredits: u32 = 1_000;
    pub const MaxReforestProjects: u32 = 500;
    pub const MaxGreenValidators: u32 = 101;
    pub const MinGreenScore: u8 = 0;
    pub const MaxGreenScore: u8 = 100;
}

impl pallet_eco::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type RuntimeOrigin = RuntimeOrigin;
    type PalletId = EcoPalletId;
    type MaxCarbonCredits = MaxCarbonCredits;
    pub const MaxReforestProjects = MaxReforestProjects;
    pub const MaxGreenValidators = MaxGreenValidators;
    type MinGreenScore = MinGreenScore;
    type MaxGreenScore = MaxGreenScore;
    type WeightInfo = pallet_eco::weights::SubstrateWeight<Runtime>;
}

// === Verdis Tokenomics Pallet ===
parameter_types! {
    pub const TokenomicsPalletId: PalletId = PalletId(*b"verdistk");
    pub const TotalSupply: Balance = 100_000_000_000 * UNITS;
    pub const InvestorAllocation: Balance = 12_000_000_000 * UNITS;
}

impl pallet_tokenomics::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type RuntimeOrigin = RuntimeOrigin;
    type Currency = Balances;
    type TotalSupply = TotalSupply;
    type InvestorAllocation = InvestorAllocation;
    type PalletId = TokenomicsPalletId;
    type WeightInfo = pallet_tokenomics::weights::SubstrateWeight<Runtime>;
}

// === Verdis Vesting Pallet ===
parameter_types! {
    pub const VestingPalletId: PalletId = PalletId(*b"verdisvs");
}

impl pallet_vesting::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type RuntimeOrigin = RuntimeOrigin;
    type Currency = Balances;
    type PalletId = VestingPalletId;
    type WeightInfo = pallet_vesting::weights::SubstrateWeight<Runtime>;
}

// === Session Keys ===
impl pallet_session::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type ValidatorId = AccountId;
    type ValidatorIdOf = pallet_dpos::ValidatorIdOf;
    type ShouldEndSession = pallet_dpos::ShouldEndSession;
    type NextSessionRotation = pallet_dpos::NextSessionRotation;
    type SessionManager = pallet_dpos::SessionManager;
    type SessionHandler = pallet_session::PeriodicSessions<EpochLength, ()>;
    type Keys = pallet_session::Keys;
    type WeightInfo = pallet_session::weights::SubstrateWeight<Runtime>;
}

// === Construct Runtime ===
construct_runtime! {
    pub enum Runtime {
        System: frame_system,
        Timestamp: pallet_timestamp,
        Aura: pallet_aura,
        Balances: pallet_balances,
        TransactionPayment: pallet_transaction_payment,
        Sudo: pallet_sudo,
        Session: pallet_session,
        // Verdis custom pallets
        Dpos: pallet_dpos,
        AmmDex: pallet_amm_dex,
        Eco: pallet_eco,
        Tokenomics: pallet_tokenomics,
        Vesting: pallet_vesting,
    }
}

// === Runtime API Implementation ===
impl_runtime_apis! {
    impl sp_api::Core<Block> for Runtime {
        fn version() -> RuntimeVersion {
            VERSION
        }
        fn execute_block(block: Block) {
            Executive::execute_block(block);
        }
        fn initialize_block(header: &<Block as BlockT>::Header) {
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
            block: Block,
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
        fn generate_session_keys(seed: Option<Vec<u8>>) -> Vec<u8> {
            pallet_session::Keys::generate(seed)
        }
        fn decode_session_keys(
            encoded: Vec<u8>,
        ) -> Option<Vec<(Vec<u8>, KeyTypeId)>> {
            pallet_session::Keys::decode_into_raw_public_keys(&encoded)
        }
    }

    impl sp_consensus_aura::AuraApi<Block, pallet_aura::sr25519::AuthorityId> for Runtime {
        fn authorities() -> Vec<pallet_aura::sr25519::AuthorityId> {
            Aura::authorities().into_iter().map(|x| x.into()).collect()
        }
        fn slot_duration() -> sp_consensus_aura::SlotDuration {
            sp_consensus_aura::SlotDuration::from_millis(BLOCK_TIME)
        }
    }

    impl frame_system_rpc_runtime_api::AccountNonceApi<Block, AccountId, Index> for Runtime {
        fn account_nonce(account: AccountId) -> Index {
            System::account_nonce(account)
        }
    }

    impl pallet_transaction_payment_rpc_runtime_api::TransactionPaymentApi<Block, Balance> for Runtime {
        fn query_info(
            utx: <Block as BlockT>::Extrinsic,
            len: u32,
        ) -> pallet_transaction_payment_rpc_runtime_api::RuntimeDispatchInfo<Balance> {
            TransactionPayment::query_info(utx, len)
        }
        fn query_length_fee(len: u32) -> Balance {
            TransactionPayment::query_length_fee(len)
        }
        fn query_weight_to_fee(weight: Weight) -> Balance {
            TransactionPayment::weight_to_fee(weight)
        }
    }
}
