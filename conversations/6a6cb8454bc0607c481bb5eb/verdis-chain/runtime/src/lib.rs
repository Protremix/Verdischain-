//! Verdis Chain Runtime v2.0
//!
//! The world's first fully green, carbon-negative blockchain — built with Substrate
//!
//! Architecture:
//! - Consensus: BABE (block production) + GRANDPA (finality)
//! - Smart Contracts: WASM (pallet-contracts)
//! - Cryptography: BLS (GRANDPA) + Ed25519 (session) + Blake3 (content hashing)
//! - Storage: IPFS/Arweave (pallet-storage)
//! - P2P: libp2p (Substrate native)
//! - Database: RocksDB (Substrate native)
//! - API: gRPC + JSON-RPC
//! - Chain ID: 909

#![cfg_attr(not(feature = "std"), no_std)]

#[cfg(feature = "std")]
include!(concat!(env!("OUT_DIR"), "/wasm_binary.rs"));

use sp_api::impl_runtime_apis;
use sp_core::{crypto::KeyTypeId, OpaqueMetadata};
use sp_runtime::{
    create_runtime_str, generic, traits::{
        AccountIdLookup, BlakeTwo256, Block as BlockT, IdentifyAccount, NumberFor, Verify,
    }, transaction_validity::{TransactionSource, TransactionValidity},
    ApplyExtrinsicResult, BuildStorage, MultiSignature, Permill,
};
use sp_std::prelude::*;
use sp_version::RuntimeVersion;

#[cfg(feature = "std")]
use sp_version::NativeVersion;

// === Pallet Imports ===
use frame_support::{
    construct_runtime, parameter_types,
    traits::{ConstU32, ConstU64, Everything, Randomness},
    weights::{
        constants::{BlockExecutionWeight, ExtrinsicBaseWeight, RocksDbWeight, WEIGHT_REF_TIME_PER_SECOND},
        IdentityFee, Weight,
    },
    PalletId,
};
use frame_system::EnsureRoot;

pub use frame_support::weights::constants as weight_constants;

// === Verdis Custom Pallets ===
pub use pallet_dpos;
pub use pallet_amm_dex;
pub use pallet_eco;
pub use pallet_tokenomics;
pub use pallet_vesting;
pub use pallet_storage;

// === Type Aliases ===
pub type AccountId = sp_core::sr25519::Public;
pub type Balance = u128;
pub type BlockNumber = u32;
pub type Header = generic::Header<BlockNumber, BlakeTwo256>;
pub type Block = generic::Block<Header, UncheckedExtrinsic>;
pub type Index = u32;
pub type Signature = MultiSignature;

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
    authoring_version: 2,
    spec_version: 2,
    impl_version: 2,
    apis: RUNTIME_API_VERSIONS,
    transaction_version: 2,
    state_version: 1,
};

#[cfg(feature = "std")]
pub fn native_version() -> NativeVersion {
    NativeVersion {
        runtime_version: VERSION,
        can_author_with: Default::default(),
    }
}

// === Constants ===
pub const UNITS: Balance = 1_000_000_000; // 1 VRDX = 10^9 base units
pub const TOTAL_SUPPLY: Balance = 100_000_000_000 * UNITS;
pub const CIRCULATING_SUPPLY: Balance = 15_000_000_000 * UNITS;
pub const BLOCK_TIME: u64 = 6000; // 6 second blocks (BABE)
pub const MAX_BLOCK_WEIGHT: Weight = Weight::from_parts(
    WEIGHT_REF_TIME_PER_SECOND.saturating_mul(2),
    weight_constants::MAX_POSSIBLE_PROOF_SIZE,
);

parameter_types! {
    pub const BlockHashCount: BlockNumber = 2400;
    pub const Version: RuntimeVersion = VERSION;
    pub const SS58Prefix: u8 = 909;
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
            weight_constants::NORMAL_DISPATCH_RATIO,
            weight_constants::MAX_POSSIBLE_LENGTH,
        );
}

// === System Pallet ===
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

// === Timestamp ===
impl pallet_timestamp::Config for Runtime {
    type Moment = u64;
    type OnTimestampSet = Babe;
    type MinimumPeriod = ConstU64<{ BLOCK_TIME / 2 }>;
    type WeightInfo = ();
}

// === BABE Consensus (Block Production) ===
impl pallet_babe::Config for Runtime {
    type EpochDuration = ConstU64<600>;
    type ExpectedBlockTime = ConstU64<BLOCK_TIME>;
    type ReportLongRanges = ();
    type EpochChangeTrigger = pallet_babe::ExternalTrigger;
    type DisabledValidators = ();
    type WeightInfo = ();
    type MaxAuthorities = ConstU32<101>;
    type MaxNominatorRewardedPerValidator = ConstU32<64>;
}

// === GRANDPA Finality ===
impl pallet_grandpa::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type WeightInfo = ();
    type MaxAuthorities = ConstU32<101>;
    type MaxSetIdSessionEntries = ConstU64<0>;
    type MaxNominators = ConstU32<256>;
    type KeyOwnerProof = sp_core::Void;
    type EquivocationReportSystem = ();
    type VoterEquivocationReportSystem = ();
}

// === Session (for validator management) ===
parameter_types! {
    pub const Period: BlockNumber = 600;
    pub const Offset: BlockNumber = 0;
}

impl pallet_session::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type ValidatorId = AccountId;
    type ValidatorIdOf = pallet_dpos::ValidatorIdOf<Runtime>;
    type ShouldEndSession = pallet_dpos::ShouldEndSession<Runtime>;
    type NextSessionRotation = pallet_session::PeriodicSessions<Period, Offset>;
    type SessionManager = pallet_dpos::SessionManager<Runtime>;
    type SessionHandler = <pallet_session::PeriodicSessions<Period, Offset> as pallet_session::SessionHandler<AccountId>>::SessionHandler;
    type Keys = pallet_session::Keys;
    type WeightInfo = ();
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
    type FreezeIdentifier = ();
    type MaxFreezes = ConstU32<0>;
    type RuntimeHoldReason = ();
    type MaxHolds = ConstU32<0>;
}

// === Transaction Payment ===
parameter_types! {
    pub const TransactionByteFee: Balance = 100_000;
    pub const OperationalFeeMultiplier: u8 = 5;
}

impl pallet_transaction_payment::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type OnChargeTransaction = pallet_transaction_payment::CurrencyAdapter<Balances, ()>;
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
}

// === Preimage ===
impl pallet_preimage::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type WeightInfo = ();
    type Currency = Balances;
    type ManagerOrigin = EnsureRoot<AccountId>;
    type BaseDeposit = ConstU128<1>;
    type ByteDeposit = ConstU128<1>;
}

// === Randomness (for BABE VRF) ===

// === WASM Smart Contracts (pallet-contracts) ===
parameter_types! {
    pub const DepositPerItem: Balance = 1 * UNITS;
    pub const DepositPerByte: Balance = 1 * UNITS;
    pub const MaxStorageKeyLen: u32 = 128;
    pub Schedule: pallet_contracts::Schedule<Runtime> = Default::default();
}

impl pallet_contracts::Config for Runtime {
    type Time = Timestamp;
    type Randomness = Babe;
    type Currency = Balances;
    type RuntimeEvent = RuntimeEvent;
    type RuntimeCall = RuntimeCall;
    type CallFilter = Everything;
    type DepositPerItem = DepositPerItem;
    type DepositPerByte = DepositPerByte;
    type MaxStorageKeyLen = MaxStorageKeyLen;
    type WeightPrice = pallet_transaction_payment::Pallet<Runtime>;
    type WeightInfo = ();
    type ChainExtension = ();
    type Schedule = Schedule;
    type AddressGenerator = pallet_contracts::DefaultAddressGenerator;
    type MaxCodeLen = ConstU32<{ 256 * 1024 }>;
    type MaxStorageDataLen = ConstU32<{ 16 * 1024 }>;
    type UnsafeUnstableInterface = ();
    type UploadOrigin = frame_system::EnsureSigned<AccountId>;
    type InstantiateOrigin = frame_system::EnsureSigned<AccountId>;
    type RuntimeHoldReason = ();
    type MaxDecorations = ConstU32<64>;
    type CodeHashLockupDepositPercent = Permill::from_percent(30);
    type MaxDelegateDependencies = ConstU32<32>;
    type Environment = ();
    type Debug = ();
    type ApiVersion = ();
    type Migrations = ();
    type Xcm = ();
}

// === Verdis DPoS Pallet ===
parameter_types! {
    pub const DposPalletId: PalletId = PalletId(*b"verdisdp");
    pub const MinValidatorStake: Balance = 10_000 * UNITS;
    pub const MaxValidators: u32 = 101;
    pub const ValidatorCount: u32 = 5;
    pub const BlockReward: Balance = 16 * UNITS;
    pub const EpochLength: BlockNumber = 600;
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

// === Verdis AMM DEX ===
parameter_types! {
    pub const DexPalletId: PalletId = PalletId(*b"verdisdx");
    pub const FeeNumerator: u32 = 3;
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

// === Verdis Eco Tracking ===
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
    type MaxReforestProjects = MaxReforestProjects;
    type MaxGreenValidators = MaxGreenValidators;
    type MinGreenScore = MinGreenScore;
    type MaxGreenScore = MaxGreenScore;
    type WeightInfo = pallet_eco::weights::SubstrateWeight<Runtime>;
}

// === Verdis Tokenomics ===
parameter_types! {
    pub const TokenomicsPalletId: PalletId = PalletId(*b"verdistk");
    pub const TotalSupplyConst: Balance = 100_000_000_000 * UNITS;
    pub const InvestorAllocationConst: Balance = 12_000_000_000 * UNITS;
}

impl pallet_tokenomics::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type RuntimeOrigin = RuntimeOrigin;
    type Currency = Balances;
    type TotalSupply = TotalSupplyConst;
    type InvestorAllocation = InvestorAllocationConst;
    type PalletId = TokenomicsPalletId;
    type WeightInfo = pallet_tokenomics::weights::SubstrateWeight<Runtime>;
}

// === Verdis Vesting ===
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

// === Verdis Storage (IPFS/Arweave) ===
parameter_types! {
    pub const StoragePalletId: PalletId = PalletId(*b"verdisst");
    pub const MaxStorageRecords: u32 = 10_000;
}

impl pallet_storage::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type PalletId = StoragePalletId;
    type MaxRecords = MaxStorageRecords;
    type WeightInfo = pallet_storage::weights::SubstrateWeight<Runtime>;
}

// === Construct Runtime ===
construct_runtime! {
    pub enum Runtime {
        // Core
        System: frame_system = 0,
        Timestamp: pallet_timestamp = 1,
        Babe: pallet_babe = 2,
        Grandpa: pallet_grandpa = 3,
        Balances: pallet_balances = 4,
        TransactionPayment: pallet_transaction_payment = 5,
        Sudo: pallet_sudo = 6,
        Session: pallet_session = 7,
        Scheduler: pallet_scheduler = 8,
        Preimage: pallet_preimage = 9,

        // Smart Contracts (WASM)
        Contracts: pallet_contracts = 20,

        // Verdis Custom Pallets
        Dpos: pallet_dpos = 30,
        AmmDex: pallet_amm_dex = 31,
        Eco: pallet_eco = 32,
        Tokenomics: pallet_tokenomics = 33,
        Vesting: pallet_vesting = 34,
        Storage: pallet_storage = 35,
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

    impl sp_consensus_babe::BabeApi<Block> for Runtime {
        fn configuration() -> sp_consensus_babe::BabeConfiguration {
            let epoch_config = Babe::epoch_config().unwrap_or(Default::default());
            sp_consensus_babe::BabeConfiguration {
                slot_duration: Babe::slot_duration(),
                epoch_length: <Babe as pallet_babe::Config>::EpochDuration::get(),
                c: PRIMARY_PROBABILITY,
                genesis_authorities: Babe::authorities().into_iter().map(|x| x.into()).collect(),
                randomness: Babe::randomness().into(),
                allowed_slots: Babe::allowed_slots(),
                epoch_config,
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
            Babe::generate_key_ownership_proof(&_slot, &authority_id)
        }

        fn submit_report_equivocation_unsigned_extrinsic(
            equivocation_proof: sp_consensus_babe::OpaqueEquivocationProof,
            key_owner_proof: sp_consensus_babe::OpaqueKeyOwnershipProof,
        ) -> Option<()> {
            Babe::submit_unsigned_equivocation_report(
                equivocation_proof,
                key_owner_proof,
            )
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
            equivocation: sp_consensus_grandpa::EquivocationProof<
                <Block as BlockT>::Hash,
                NumberFor<Block>,
            >,
            key_owner: sp_consensus_grandpa::OpaqueKeyOwnershipProof,
        ) -> Option<()> {
            Grandpa::submit_unsigned_equivocation_report(
                equivocation,
                key_owner,
            )
        }

        fn generate_key_ownership_proof(
            _set_id: sp_consensus_grandpa::SetId,
            authority_id: sp_consensus_grandpa::AuthorityId,
        ) -> Option<sp_consensus_grandpa::OpaqueKeyOwnershipProof> {
            Grandpa::generate_key_ownership_proof(&_set_id, &authority_id)
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

// BABE constants
const PRIMARY_PROBABILITY: sp_consensus_babe::SlotProbability = sp_consensus_babe::SlotProbability::from_percent(100);
