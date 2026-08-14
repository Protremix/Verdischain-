#![allow(clippy::incompatible_msrv)]
#![allow(
    clippy::let_unit_value,
    deprecated,
    clippy::clone_on_copy,
    clippy::type_complexity,
    clippy::needless_borrow,
    clippy::collapsible_if,
    clippy::redundant_closure,
    clippy::manual_saturating_arithmetic,
    clippy::unnecessary_cast,
    clippy::derivable_impls,
    clippy::manual_checked_ops,
    clippy::needless_borrows_for_generic_args
)]
//! # Verdis Eco Tracking Pallet
//!
//! On-chain ecological impact tracking with:
//! - Carbon credit minting, verification, trading, and retirement
//! - Reforestation project registration and verification
//! - Green validator scoring with energy source tracking
//! - Aggregate eco-impact metrics (CO2 offset, trees planted)

#![cfg_attr(not(feature = "std"), no_std)]

use codec::{Decode, Encode, MaxEncodedLen};
use frame_support::{
    dispatch::DispatchResult, ensure, pallet_prelude::*, traits::Get, DefaultNoBound, PalletId,
};
use frame_system::pallet_prelude::*;
use scale_info::TypeInfo;
use sp_std::prelude::*;

pub use pallet::*;
pub mod weights;
pub use weights::WeightInfo as SubstrateWeight;

#[frame_support::pallet]
pub mod pallet {
    use super::*;

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    // === Carbon Credit ===

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo)]
    pub struct CarbonCredit<AccountId> {
        pub id: BoundedVec<u8, ConstU32<64>>,
        pub project_name: BoundedVec<u8, ConstU32<128>>,
        pub tons_co2: u64,
        pub verified: bool,
        pub retired: bool,
        pub owner: AccountId,
        pub created_at: u64,
    }

    // === Reforestation Project ===

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo)]
    pub struct ReforestProject {
        pub id: BoundedVec<u8, ConstU32<64>>,
        pub name: BoundedVec<u8, ConstU32<128>>,
        pub trees_planted: u32,
        pub location: BoundedVec<u8, ConstU32<64>>,
        pub survival_rate: u8,
        pub verified: bool,
    }

    // === Green Validator ===

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo)]
    pub struct GreenValidator<AccountId> {
        pub address: AccountId,
        pub renewable_energy: bool,
        pub energy_source: BoundedVec<u8, ConstU32<64>>,
        pub carbon_offset: u64,
        pub trees_planted: u32,
        pub score: u8,
        pub last_updated: u64,
    }

    // === Storage ===

    #[pallet::storage]
    #[pallet::getter(fn carbon_credits)]
    pub type CarbonCredits<T: Config> =
        StorageMap<_, Blake2_128Concat, BoundedVec<u8, ConstU32<64>>, CarbonCredit<T::AccountId>>;

    #[pallet::storage]
    #[pallet::getter(fn reforest_projects)]
    pub type ReforestProjects<T: Config> =
        StorageMap<_, Blake2_128Concat, BoundedVec<u8, ConstU32<64>>, ReforestProject>;

    #[pallet::storage]
    #[pallet::getter(fn green_validators)]
    pub type GreenValidators<T: Config> =
        StorageMap<_, Blake2_128Concat, T::AccountId, GreenValidator<T::AccountId>>;

    #[pallet::storage]
    #[pallet::getter(fn last_mint_block)]
    pub type LastMintBlock<T: Config> = StorageValue<_, u32, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn credits_minted_this_block)]
    pub type CreditsMintedThisBlock<T: Config> = StorageValue<_, u32, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn total_co2_offset)]
    pub type TotalCO2Offset<T: Config> = StorageValue<_, u64, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn total_trees_planted)]
    pub type TotalTreesPlanted<T: Config> = StorageValue<_, u32, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn total_credits_retired)]
    pub type TotalCreditsRetired<T: Config> = StorageValue<_, u64, ValueQuery>;

    // === Events ===

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        CarbonCreditMinted {
            id: Vec<u8>,
            tons_co2: u64,
            owner: T::AccountId,
        },
        CarbonCreditVerified {
            id: Vec<u8>,
        },
        CarbonCreditRetired {
            id: Vec<u8>,
            tons_co2: u64,
        },
        CarbonCreditTransferred {
            id: Vec<u8>,
            from: T::AccountId,
            to: T::AccountId,
        },
        ReforestProjectCreated {
            id: Vec<u8>,
            name: Vec<u8>,
            trees: u32,
        },
        ReforestProjectUpdated {
            id: Vec<u8>,
            trees: u32,
            survival_rate: u8,
        },
        ReforestProjectVerified {
            id: Vec<u8>,
        },
        GreenValidatorRegistered {
            address: T::AccountId,
            energy_source: Vec<u8>,
            score: u8,
        },
        GreenScoreUpdated {
            address: T::AccountId,
            score: u8,
        },
    }

    // === Errors ===

    #[pallet::error]
    pub enum Error<T> {
        CreditNotFound,
        CreditAlreadyExists,
        CreditNotVerified,
        CreditAlreadyRetired,
        NotCreditOwner,
        ProjectNotFound,
        ProjectAlreadyExists,
        ValidatorAlreadyRegistered,
        ValidatorNotFound,
        MaxCarbonCreditsReached,
        MaxReforestProjectsReached,
        MaxGreenValidatorsReached,
        InvalidScore,
        AlreadyVerified,
        IdTooLong,
        NameTooLong,
        LocationTooLong,
        PerBlockMintLimitReached,
    }

    // === Config ===

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        #[pallet::constant]
        type PalletId: Get<PalletId>;
        #[pallet::constant]
        type MaxCarbonCredits: Get<u32>;
        #[pallet::constant]
        type MaxReforestProjects: Get<u32>;
        #[pallet::constant]
        type MaxGreenValidators: Get<u32>;
        #[pallet::constant]
        type MinGreenScore: Get<u8>;
        #[pallet::constant]
        type MaxGreenScore: Get<u8>;
        type WeightInfo: WeightInfo;
        /// Post-sudo: Council (2/3) administers eco operations
        type AdminOrigin: EnsureOrigin<Self::RuntimeOrigin>;
    }

    // === Genesis ===

    #[pallet::genesis_config]
    #[derive(DefaultNoBound)]
    pub struct GenesisConfig<T: Config> {
        pub carbon_credits: Vec<(Vec<u8>, Vec<u8>, u64, bool, T::AccountId)>,
        pub reforest_projects: Vec<(Vec<u8>, Vec<u8>, u32, Vec<u8>, u8, bool)>,
        pub green_validators: Vec<(T::AccountId, bool, Vec<u8>, u64, u32, u8)>,
    }

    #[pallet::genesis_build]
    impl<T: Config> BuildGenesisConfig for GenesisConfig<T> {
        fn build(&self) {
            let mut total_co2 = 0u64;
            let mut total_trees = 0u32;

            for (id, name, tons, verified, owner) in &self.carbon_credits {
                let id_bv: BoundedVec<u8, ConstU32<64>> = id.clone().try_into().unwrap_or_default();
                let name_bv: BoundedVec<u8, ConstU32<128>> =
                    name.clone().try_into().unwrap_or_default();
                let credit = CarbonCredit {
                    id: id_bv.clone(),
                    project_name: name_bv,
                    tons_co2: *tons,
                    verified: *verified,
                    retired: false,
                    owner: owner.clone(),
                    created_at: 0,
                };
                CarbonCredits::<T>::insert(id_bv, credit);
                total_co2 = total_co2.saturating_add(*tons);
            }

            for (id, name, trees, location, survival, verified) in &self.reforest_projects {
                let id_bv: BoundedVec<u8, ConstU32<64>> = id.clone().try_into().unwrap_or_default();
                let project = ReforestProject {
                    id: id_bv.clone(),
                    name: name.clone().try_into().unwrap_or_default(),
                    trees_planted: *trees,
                    location: location.clone().try_into().unwrap_or_default(),
                    survival_rate: *survival,
                    verified: *verified,
                };
                ReforestProjects::<T>::insert(id_bv, project);
                total_trees = total_trees.saturating_add(*trees);
            }

            for (address, renewable, energy, co2, trees, score) in &self.green_validators {
                let gv = GreenValidator {
                    address: address.clone(),
                    renewable_energy: *renewable,
                    energy_source: energy.clone().try_into().unwrap_or_default(),
                    carbon_offset: *co2,
                    trees_planted: *trees,
                    score: *score,
                    last_updated: 0,
                };
                GreenValidators::<T>::insert(address.clone(), gv);
            }

            TotalCO2Offset::<T>::put(total_co2);
            TotalTreesPlanted::<T>::put(total_trees);
        }
    }

    // === Extrinsics ===

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Mint a new carbon credit
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::mint_carbon_credit())]
        pub fn mint_carbon_credit(
            origin: OriginFor<T>,
            owner: T::AccountId,
            id: Vec<u8>,
            project_name: Vec<u8>,
            tons_co2: u64,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;
            let who = owner;

            let id_bv: BoundedVec<u8, ConstU32<64>> =
                id.clone().try_into().map_err(|_| Error::<T>::IdTooLong)?;
            let name_bv: BoundedVec<u8, ConstU32<128>> = project_name
                .clone()
                .try_into()
                .map_err(|_| Error::<T>::NameTooLong)?;

            ensure!(
                !CarbonCredits::<T>::contains_key(&id_bv),
                Error::<T>::CreditAlreadyExists
            );
            ensure!(
                (CarbonCredits::<T>::iter().count() as u32) < T::MaxCarbonCredits::get(),
                Error::<T>::MaxCarbonCreditsReached
            );

            // Per-block mint ceiling: max 5 credits per block to prevent governance abuse
            let current_block: u32 = frame_system::Pallet::<T>::block_number()
                .try_into()
                .unwrap_or(0);
            let last_mint_block = LastMintBlock::<T>::get();
            let credits_this_block = CreditsMintedThisBlock::<T>::get();
            ensure!(
                current_block != last_mint_block || credits_this_block < 5,
                Error::<T>::PerBlockMintLimitReached
            );
            if current_block != last_mint_block {
                CreditsMintedThisBlock::<T>::put(1u32);
                LastMintBlock::<T>::put(current_block);
            } else {
                CreditsMintedThisBlock::<T>::put(credits_this_block + 1);
            }

            let credit = CarbonCredit {
                id: id_bv.clone(),
                project_name: name_bv,
                tons_co2,
                verified: false,
                retired: false,
                owner: who.clone(),
                created_at: 0,
            };

            CarbonCredits::<T>::insert(id_bv, credit);
            TotalCO2Offset::<T>::mutate(|t| *t = t.saturating_add(tons_co2));

            Self::deposit_event(Event::CarbonCreditMinted {
                id,
                tons_co2,
                owner: who,
            });
            Ok(())
        }

        /// Verify a carbon credit (authority only)
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::verify_carbon_credit())]
        pub fn verify_carbon_credit(origin: OriginFor<T>, id: Vec<u8>) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            let id_bv: BoundedVec<u8, ConstU32<64>> =
                id.clone().try_into().map_err(|_| Error::<T>::IdTooLong)?;

            CarbonCredits::<T>::mutate(&id_bv, |c| {
                let credit = c.as_mut().ok_or(Error::<T>::CreditNotFound)?;
                ensure!(!credit.verified, Error::<T>::AlreadyVerified);
                credit.verified = true;
                Ok::<(), Error<T>>(())
            })?;

            Self::deposit_event(Event::CarbonCreditVerified { id });
            Ok(())
        }

        /// Retire a carbon credit (owner only)
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::retire_carbon_credit())]
        pub fn retire_carbon_credit(origin: OriginFor<T>, id: Vec<u8>) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let id_bv: BoundedVec<u8, ConstU32<64>> =
                id.clone().try_into().map_err(|_| Error::<T>::IdTooLong)?;

            CarbonCredits::<T>::mutate(&id_bv, |c| {
                let credit = c.as_mut().ok_or(Error::<T>::CreditNotFound)?;
                ensure!(credit.owner == who, Error::<T>::NotCreditOwner);
                ensure!(!credit.retired, Error::<T>::CreditAlreadyRetired);
                credit.retired = true;
                Ok::<(), Error<T>>(())
            })?;

            let credit = CarbonCredits::<T>::get(&id_bv).ok_or(Error::<T>::CreditNotFound)?;
            TotalCreditsRetired::<T>::mutate(|t| *t = t.saturating_add(credit.tons_co2));

            Self::deposit_event(Event::CarbonCreditRetired {
                id,
                tons_co2: credit.tons_co2,
            });
            Ok(())
        }

        /// Transfer a carbon credit to a new owner
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::transfer_carbon_credit())]
        pub fn transfer_carbon_credit(
            origin: OriginFor<T>,
            id: Vec<u8>,
            to: T::AccountId,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let id_bv: BoundedVec<u8, ConstU32<64>> =
                id.clone().try_into().map_err(|_| Error::<T>::IdTooLong)?;

            CarbonCredits::<T>::mutate(&id_bv, |c| {
                let credit = c.as_mut().ok_or(Error::<T>::CreditNotFound)?;
                ensure!(credit.owner == who, Error::<T>::NotCreditOwner);
                ensure!(!credit.retired, Error::<T>::CreditAlreadyRetired);
                credit.owner = to.clone();
                Ok::<(), Error<T>>(())
            })?;

            Self::deposit_event(Event::CarbonCreditTransferred { id, from: who, to });
            Ok(())
        }

        /// Create a reforestation project
        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::create_reforest_project())]
        pub fn create_reforest_project(
            origin: OriginFor<T>,
            id: Vec<u8>,
            name: Vec<u8>,
            trees_planted: u32,
            location: Vec<u8>,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            let id_bv: BoundedVec<u8, ConstU32<64>> =
                id.clone().try_into().map_err(|_| Error::<T>::IdTooLong)?;

            ensure!(
                !ReforestProjects::<T>::contains_key(&id_bv),
                Error::<T>::ProjectAlreadyExists
            );
            ensure!(
                (ReforestProjects::<T>::iter().count() as u32) < T::MaxReforestProjects::get(),
                Error::<T>::MaxReforestProjectsReached
            );

            let project = ReforestProject {
                id: id_bv.clone(),
                name: name.clone().try_into().unwrap_or_default(),
                trees_planted,
                location: location.clone().try_into().unwrap_or_default(),
                survival_rate: 0,
                verified: false,
            };

            ReforestProjects::<T>::insert(id_bv, project);
            TotalTreesPlanted::<T>::mutate(|t| *t = t.saturating_add(trees_planted));

            Self::deposit_event(Event::ReforestProjectCreated {
                id,
                name,
                trees: trees_planted,
            });
            Ok(())
        }

        /// Update a reforestation project
        #[pallet::call_index(5)]
        #[pallet::weight(T::WeightInfo::update_reforest_project())]
        pub fn update_reforest_project(
            origin: OriginFor<T>,
            id: Vec<u8>,
            trees_planted: u32,
            survival_rate: u8,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            let id_bv: BoundedVec<u8, ConstU32<64>> =
                id.clone().try_into().map_err(|_| Error::<T>::IdTooLong)?;

            ReforestProjects::<T>::mutate(&id_bv, |p| {
                let project = p.as_mut().ok_or(Error::<T>::ProjectNotFound)?;
                project.trees_planted = trees_planted;
                project.survival_rate = survival_rate;
                Ok::<(), Error<T>>(())
            })?;

            Self::deposit_event(Event::ReforestProjectUpdated {
                id,
                trees: trees_planted,
                survival_rate,
            });
            Ok(())
        }

        /// Verify a reforestation project
        #[pallet::call_index(6)]
        #[pallet::weight(T::WeightInfo::verify_reforest_project())]
        pub fn verify_reforest_project(origin: OriginFor<T>, id: Vec<u8>) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            let id_bv: BoundedVec<u8, ConstU32<64>> =
                id.clone().try_into().map_err(|_| Error::<T>::IdTooLong)?;

            ReforestProjects::<T>::mutate(&id_bv, |p| {
                let project = p.as_mut().ok_or(Error::<T>::ProjectNotFound)?;
                ensure!(!project.verified, Error::<T>::AlreadyVerified);
                project.verified = true;
                Ok::<(), Error<T>>(())
            })?;

            Self::deposit_event(Event::ReforestProjectVerified { id });
            Ok(())
        }

        /// Register as a green validator
        #[pallet::call_index(7)]
        #[pallet::weight(T::WeightInfo::register_green_validator())]
        pub fn register_green_validator(
            origin: OriginFor<T>,
            energy_source: Vec<u8>,
            carbon_offset: u64,
            trees_planted: u32,
            score: u8,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let energy_bv: BoundedVec<u8, ConstU32<64>> = energy_source
                .clone()
                .try_into()
                .map_err(|_| Error::<T>::IdTooLong)?;

            ensure!(
                !GreenValidators::<T>::contains_key(&who),
                Error::<T>::ValidatorAlreadyRegistered
            );
            ensure!(score >= T::MinGreenScore::get(), Error::<T>::InvalidScore);
            ensure!(score <= T::MaxGreenScore::get(), Error::<T>::InvalidScore);
            ensure!(
                (GreenValidators::<T>::iter().count() as u32) < T::MaxGreenValidators::get(),
                Error::<T>::MaxGreenValidatorsReached
            );

            let gv = GreenValidator {
                address: who.clone(),
                renewable_energy: true,
                energy_source: energy_bv,
                carbon_offset,
                trees_planted,
                score,
                last_updated: 0,
            };

            GreenValidators::<T>::insert(who.clone(), gv);

            Self::deposit_event(Event::GreenValidatorRegistered {
                address: who,
                energy_source,
                score,
            });
            Ok(())
        }

        /// Update green score
        #[pallet::call_index(8)]
        #[pallet::weight(T::WeightInfo::update_green_score())]
        pub fn update_green_score(
            origin: OriginFor<T>,
            validator: T::AccountId,
            score: u8,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;
            let who = validator;

            ensure!(
                GreenValidators::<T>::contains_key(&who),
                Error::<T>::ValidatorNotFound
            );
            ensure!(score >= T::MinGreenScore::get(), Error::<T>::InvalidScore);
            ensure!(score <= T::MaxGreenScore::get(), Error::<T>::InvalidScore);

            GreenValidators::<T>::mutate(&who, |v| {
                if let Some(v) = v {
                    v.score = score;
                    v.last_updated = 0;
                }
            });

            Self::deposit_event(Event::GreenScoreUpdated {
                address: who,
                score,
            });
            Ok(())
        }
    }

    // === WeightInfo ===
    pub trait WeightInfo {
        fn mint_carbon_credit() -> Weight;
        fn verify_carbon_credit() -> Weight;
        fn retire_carbon_credit() -> Weight;
        fn transfer_carbon_credit() -> Weight;
        fn create_reforest_project() -> Weight;
        fn update_reforest_project() -> Weight;
        fn verify_reforest_project() -> Weight;
        fn register_green_validator() -> Weight;
        fn update_green_score() -> Weight;
    }
}

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;

#[cfg(test)]
pub mod tests {
    use super::*;
    use frame_support::{assert_noop, assert_ok, construct_runtime, derive_impl, parameter_types};
    use sp_io::TestExternalities;
    use sp_keyring::Sr25519Keyring;
    use sp_runtime::{traits::IdentityLookup, BuildStorage};

    type Block = frame_system::mocking::MockBlock<Test>;

    construct_runtime!(
        pub enum Test { System: frame_system, Eco: crate }
    );

    #[derive_impl(frame_system::config_preludes::TestDefaultConfig as frame_system::DefaultConfig)]
    impl frame_system::Config for Test {
        type AccountId = sp_core::crypto::AccountId32;
        type Lookup = IdentityLookup<Self::AccountId>;
        type Block = Block;
        type AccountData = ();
    }

    parameter_types! {
        pub const EcoPalletId: PalletId = PalletId(*b"v/ecoess");
        pub const MaxCarbonCredits: u32 = 100;
        pub const MaxReforestProjects: u32 = 50;
        pub const MaxGreenValidators: u32 = 101;
        pub const MinGreenScore: u8 = 0;
        pub const MaxGreenScore: u8 = 100;
    }

    impl Config for Test {
        type RuntimeEvent = RuntimeEvent;
        type PalletId = EcoPalletId;
        type MaxCarbonCredits = MaxCarbonCredits;
        type MaxReforestProjects = MaxReforestProjects;
        type MaxGreenValidators = MaxGreenValidators;
        type MinGreenScore = MinGreenScore;
        type MaxGreenScore = MaxGreenScore;
        type WeightInfo = SubstrateWeight<Test>;
        type AdminOrigin = frame_system::EnsureRoot<Self::AccountId>;
    }

    pub fn new_test_ext() -> TestExternalities {
        let mut t = frame_system::GenesisConfig::<Test>::default()
            .build_storage()
            .unwrap();
        GenesisConfig::<Test> {
            carbon_credits: vec![],
            reforest_projects: vec![],
            green_validators: vec![],
        }
        .assimilate_storage(&mut t)
        .unwrap();
        let mut ext = TestExternalities::new(t);
        ext.execute_with(|| System::set_block_number(1));
        ext
    }

    #[test]
    fn test_genesis_empty() {
        new_test_ext().execute_with(|| {
            assert_eq!(TotalCO2Offset::<Test>::get(), 0);
            assert_eq!(TotalTreesPlanted::<Test>::get(), 0);
        });
    }

    #[test]
    fn test_mint_carbon_credit() {
        new_test_ext().execute_with(|| {
            assert_ok!(Eco::mint_carbon_credit(
                RuntimeOrigin::root(),
                Sr25519Keyring::Alice.to_account_id(),
                b"c1".to_vec(),
                b"Amazon".to_vec(),
                100,
            ));
            assert_eq!(TotalCO2Offset::<Test>::get(), 100);
        });
    }

    #[test]
    fn test_mint_duplicate() {
        new_test_ext().execute_with(|| {
            Eco::mint_carbon_credit(
                RuntimeOrigin::root(),
                Sr25519Keyring::Alice.to_account_id(),
                b"c1".to_vec(),
                b"P".to_vec(),
                50,
            )
            .unwrap();
            assert_noop!(
                Eco::mint_carbon_credit(
                    RuntimeOrigin::root(),
                    Sr25519Keyring::Bob.to_account_id(),
                    b"c1".to_vec(),
                    b"P2".to_vec(),
                    30,
                ),
                Error::<Test>::CreditAlreadyExists
            );
        });
    }

    #[test]
    fn test_verify_credit() {
        new_test_ext().execute_with(|| {
            Eco::mint_carbon_credit(
                RuntimeOrigin::root(),
                Sr25519Keyring::Alice.to_account_id(),
                b"c1".to_vec(),
                b"P".to_vec(),
                50,
            )
            .unwrap();
            assert_ok!(Eco::verify_carbon_credit(
                RuntimeOrigin::root(),
                b"c1".to_vec()
            ));
        });
    }

    #[test]
    fn test_verify_nonexistent() {
        new_test_ext().execute_with(|| {
            assert_noop!(
                Eco::verify_carbon_credit(RuntimeOrigin::root(), b"nope".to_vec()),
                Error::<Test>::CreditNotFound
            );
        });
    }

    #[test]
    fn test_create_reforest() {
        new_test_ext().execute_with(|| {
            assert_ok!(Eco::create_reforest_project(
                RuntimeOrigin::root(),
                b"p1".to_vec(),
                b"Amazon".to_vec(),
                5000,
                b"Brazil".to_vec(),
            ));
            assert_eq!(TotalTreesPlanted::<Test>::get(), 5000);
        });
    }

    #[test]
    fn test_register_green_validator() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_ok!(Eco::register_green_validator(
                RuntimeOrigin::signed(alice.clone()),
                b"Solar".to_vec(),
                500,
                100,
                90,
            ));
            assert_eq!(GreenValidators::<Test>::get(&alice).unwrap().score, 90);
        });
    }

    #[test]
    fn test_update_green_score() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            Eco::register_green_validator(
                RuntimeOrigin::signed(alice.clone()),
                b"Solar".to_vec(),
                500,
                100,
                90,
            )
            .unwrap();
            assert_ok!(Eco::update_green_score(
                RuntimeOrigin::root(),
                alice.clone(),
                95
            ));
            assert_eq!(GreenValidators::<Test>::get(&alice).unwrap().score, 95);
        });
    }

    #[test]
    fn test_mint_carbon_credit_non_root_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_noop!(
                Eco::mint_carbon_credit(
                    RuntimeOrigin::signed(alice.clone()),
                    alice,
                    b"c1".to_vec(),
                    b"Amazon".to_vec(),
                    100,
                ),
                sp_runtime::DispatchError::BadOrigin
            );
        });
    }

    #[test]
    fn test_verify_carbon_credit_non_root_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_noop!(
                Eco::verify_carbon_credit(RuntimeOrigin::signed(alice), b"c1".to_vec(),),
                sp_runtime::DispatchError::BadOrigin
            );
        });
    }

    #[test]
    fn test_retire_nonexistent_credit_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_noop!(
                Eco::retire_carbon_credit(RuntimeOrigin::signed(alice), b"nonexistent".to_vec(),),
                Error::<Test>::CreditNotFound
            );
        });
    }

    #[test]
    fn test_transfer_nonexistent_credit_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let bob = Sr25519Keyring::Bob.to_account_id();
            assert_noop!(
                Eco::transfer_carbon_credit(
                    RuntimeOrigin::signed(alice),
                    b"nonexistent".to_vec(),
                    bob,
                ),
                Error::<Test>::CreditNotFound
            );
        });
    }

    #[test]
    fn test_transfer_retired_credit_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let bob = Sr25519Keyring::Bob.to_account_id();
            Eco::mint_carbon_credit(
                RuntimeOrigin::root(),
                alice.clone(),
                b"c1".to_vec(),
                b"Amazon".to_vec(),
                100,
            )
            .unwrap();
            Eco::retire_carbon_credit(RuntimeOrigin::signed(alice.clone()), b"c1".to_vec())
                .unwrap();
            assert_noop!(
                Eco::transfer_carbon_credit(RuntimeOrigin::signed(alice), b"c1".to_vec(), bob,),
                Error::<Test>::CreditAlreadyRetired
            );
        });
    }

    #[test]
    fn test_transfer_credit_not_owner_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let bob = Sr25519Keyring::Bob.to_account_id();
            let charlie = Sr25519Keyring::Charlie.to_account_id();
            Eco::mint_carbon_credit(
                RuntimeOrigin::root(),
                alice,
                b"c1".to_vec(),
                b"Amazon".to_vec(),
                100,
            )
            .unwrap();
            assert_noop!(
                Eco::transfer_carbon_credit(RuntimeOrigin::signed(bob), b"c1".to_vec(), charlie,),
                Error::<Test>::NotCreditOwner
            );
        });
    }

    #[test]
    fn test_create_reforest_non_root_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_noop!(
                Eco::create_reforest_project(
                    RuntimeOrigin::signed(alice),
                    b"p1".to_vec(),
                    b"Amazon".to_vec(),
                    1000,
                    b"Brazil".to_vec(),
                ),
                sp_runtime::DispatchError::BadOrigin
            );
        });
    }

    #[test]
    fn test_create_duplicate_reforest_rejected() {
        new_test_ext().execute_with(|| {
            Eco::create_reforest_project(
                RuntimeOrigin::root(),
                b"p1".to_vec(),
                b"Amazon".to_vec(),
                1000,
                b"Brazil".to_vec(),
            )
            .unwrap();
            assert_noop!(
                Eco::create_reforest_project(
                    RuntimeOrigin::root(),
                    b"p1".to_vec(),
                    b"Amazon 2".to_vec(),
                    2000,
                    b"Peru".to_vec(),
                ),
                Error::<Test>::ProjectAlreadyExists
            );
        });
    }

    #[test]
    fn test_update_reforest_non_root_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_noop!(
                Eco::update_reforest_project(
                    RuntimeOrigin::signed(alice),
                    b"p1".to_vec(),
                    1000,
                    80,
                ),
                sp_runtime::DispatchError::BadOrigin
            );
        });
    }

    #[test]
    fn test_update_nonexistent_reforest_rejected() {
        new_test_ext().execute_with(|| {
            assert_noop!(
                Eco::update_reforest_project(
                    RuntimeOrigin::root(),
                    b"nonexistent".to_vec(),
                    1000,
                    80,
                ),
                Error::<Test>::ProjectNotFound
            );
        });
    }

    #[test]
    fn test_register_green_validator_duplicate_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            Eco::register_green_validator(
                RuntimeOrigin::signed(alice.clone()),
                b"Solar".to_vec(),
                500,
                100,
                90,
            )
            .unwrap();
            assert_noop!(
                Eco::register_green_validator(
                    RuntimeOrigin::signed(alice),
                    b"Wind".to_vec(),
                    300,
                    50,
                    80,
                ),
                Error::<Test>::ValidatorAlreadyRegistered
            );
        });
    }

    #[test]
    fn test_register_green_validator_invalid_score_high_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_noop!(
                Eco::register_green_validator(
                    RuntimeOrigin::signed(alice),
                    b"Solar".to_vec(),
                    500,
                    100,
                    101,
                ),
                Error::<Test>::InvalidScore
            );
        });
    }

    #[test]
    fn test_update_green_score_non_root_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_noop!(
                Eco::update_green_score(RuntimeOrigin::signed(alice.clone()), alice, 95,),
                sp_runtime::DispatchError::BadOrigin
            );
        });
    }

    #[test]
    fn test_update_nonexistent_validator_score_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_noop!(
                Eco::update_green_score(RuntimeOrigin::root(), alice, 95,),
                Error::<Test>::ValidatorNotFound
            );
        });
    }

    #[test]
    fn test_mint_carbon_credit_id_too_long_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let long_id = vec![0u8; 65];
            assert_noop!(
                Eco::mint_carbon_credit(
                    RuntimeOrigin::root(),
                    alice,
                    long_id,
                    b"Amazon".to_vec(),
                    100,
                ),
                Error::<Test>::IdTooLong
            );
        });
    }

    #[test]
    fn test_mint_carbon_credit_name_too_long_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let long_name = vec![0u8; 129];
            assert_noop!(
                Eco::mint_carbon_credit(
                    RuntimeOrigin::root(),
                    alice,
                    b"c1".to_vec(),
                    long_name,
                    100,
                ),
                Error::<Test>::NameTooLong
            );
        });
    }

    #[test]
    fn test_retire_carbon_credit_works() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_ok!(Eco::mint_carbon_credit(
                RuntimeOrigin::root(),
                alice.clone(),
                b"c1".to_vec(),
                b"Amazon".to_vec(),
                100,
            ));
            assert_ok!(Eco::retire_carbon_credit(
                RuntimeOrigin::signed(alice),
                b"c1".to_vec()
            ));
            let id_bv: frame_support::BoundedVec<u8, frame_support::traits::ConstU32<64>> =
                b"c1".to_vec().try_into().unwrap();
            let credit = CarbonCredits::<Test>::get(&id_bv).unwrap();
            assert!(credit.retired);
            assert_eq!(TotalCreditsRetired::<Test>::get(), 100);
        });
    }

    #[test]
    fn test_transfer_carbon_credit_works() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let bob = Sr25519Keyring::Bob.to_account_id();
            assert_ok!(Eco::mint_carbon_credit(
                RuntimeOrigin::root(),
                alice.clone(),
                b"c1".to_vec(),
                b"Amazon".to_vec(),
                100,
            ));
            assert_ok!(Eco::transfer_carbon_credit(
                RuntimeOrigin::signed(alice),
                b"c1".to_vec(),
                bob.clone(),
            ));
            let id_bv: frame_support::BoundedVec<u8, frame_support::traits::ConstU32<64>> =
                b"c1".to_vec().try_into().unwrap();
            let credit = CarbonCredits::<Test>::get(&id_bv).unwrap();
            assert_eq!(credit.owner, bob);
        });
    }

// ============================================================
// ADDITIONAL EDGE CASE TESTS (Kimi audit additions)
// ============================================================

    #[test]
    fn test_mint_carbon_credit_unauthorized_reverts() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            // Non-root user should not be able to mint
            let result = Eco::mint_carbon_credit(
                RuntimeOrigin::signed(alice.clone()),
                alice.clone(),
                b"c1".to_vec(),
                b"Amazon".to_vec(),
                100,
            );
            assert!(result.is_err(), "Non-admin should not mint carbon credits");
        });
    }

    #[test]
    fn test_mint_carbon_credit_zero_amount_reverts() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let result = Eco::mint_carbon_credit(
                RuntimeOrigin::root(),
                alice,
                b"c1".to_vec(),
                b"Amazon".to_vec(),
                0, // zero amount
            );
            assert!(result.is_err(), "Zero carbon credit should fail");
        });
    }

    #[test]
    fn test_mint_duplicate_carbon_credit_reverts() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_ok!(Eco::mint_carbon_credit(
                RuntimeOrigin::root(),
                alice.clone(),
                b"c1".to_vec(),
                b"Amazon".to_vec(),
                100,
            ));
            // Minting same ID again should fail
            let result = Eco::mint_carbon_credit(
                RuntimeOrigin::root(),
                alice,
                b"c1".to_vec(),
                b"Amazon".to_vec(),
                200,
            );
            assert!(result.is_err(), "Duplicate carbon credit ID should fail");
        });
    }

    #[test]
    fn test_retire_nonexistent_credit_reverts() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let result = Eco::retire_carbon_credit(
                RuntimeOrigin::signed(alice),
                b"nonexistent".to_vec(),
            );
            assert!(result.is_err(), "Retiring nonexistent credit should fail");
        });
    }

    #[test]
    fn test_verify_carbon_credit_unauthorized_reverts() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_ok!(Eco::mint_carbon_credit(
                RuntimeOrigin::root(),
                alice.clone(),
                b"c1".to_vec(),
                b"Amazon".to_vec(),
                100,
            ));
            // Non-admin should not verify
            let result = Eco::verify_carbon_credit(
                RuntimeOrigin::signed(alice),
                b"c1".to_vec(),
            );
            assert!(result.is_err(), "Non-admin should not verify credits");
        });
    }

    #[test]
    fn test_transfer_nonexistent_credit_reverts() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let bob = Sr25519Keyring::Bob.to_account_id();
            let result = Eco::transfer_carbon_credit(
                RuntimeOrigin::signed(alice),
                b"nonexistent".to_vec(),
                bob,
            );
            assert!(result.is_err(), "Transferring nonexistent credit should fail");
        });
    }

    #[test]
    fn test_create_reforest_project_unauthorized_reverts() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let result = Eco::create_reforest_project(
                RuntimeOrigin::signed(alice),
                b"project1".to_vec(),
                b"Amazon".to_vec(),
                1000,
                10,
            );
            assert!(result.is_err(), "Non-admin should not create reforest projects");
        });
    }

    #[test]
    fn test_update_green_score_unauthorized_reverts() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            // Non-admin should not update green score
            let result = Eco::update_green_score(
                RuntimeOrigin::signed(alice.clone()),
                alice,
                50,
            );
            assert!(result.is_err(), "Non-admin should not update green scores");
        });
    }

    #[test]
    fn test_total_co2_increases_on_mint() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let co2_before = TotalCO2Offset::<Test>::get();
            
            assert_ok!(Eco::mint_carbon_credit(
                RuntimeOrigin::root(),
                alice,
                b"c1".to_vec(),
                b"Amazon".to_vec(),
                500,
            ));
            
            let co2_after = TotalCO2Offset::<Test>::get();
            assert!(co2_after > co2_before, "Total CO2 should increase after minting");
            assert_eq!(co2_after - co2_before, 500, "CO2 should increase by exact amount");
        });
    }

    #[test]
    fn test_retire_credit_decreases_supply() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_ok!(Eco::mint_carbon_credit(
                RuntimeOrigin::root(),
                alice.clone(),
                b"c1".to_vec(),
                b"Amazon".to_vec(),
                100,
            ));
            
            let co2_before = TotalCO2Offset::<Test>::get();
            assert_ok!(Eco::retire_carbon_credit(
                RuntimeOrigin::signed(alice),
                b"c1".to_vec(),
            ));
            
            let co2_after = TotalCO2Offset::<Test>::get();
            assert!(co2_after < co2_before, "CO2 should decrease after retirement");
        });
    }

}
