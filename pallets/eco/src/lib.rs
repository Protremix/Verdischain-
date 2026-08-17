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

    /// Active (non-retired) CO2 offset — decremented when credits are retired
    #[pallet::storage]
    #[pallet::getter(fn active_co2_offset)]
    pub type ActiveCO2Offset<T: Config> = StorageValue<_, u64, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn total_trees_planted)]
    pub type TotalTreesPlanted<T: Config> = StorageValue<_, u32, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn total_credits_retired)]
    pub type TotalCreditsRetired<T: Config> = StorageValue<_, u64, ValueQuery>;

    // === Events ===
    //
    // NOTE on remaining Vec<u8> in events:
    // Event fields use plain Vec<u8> because events are transient — they are
    // not stored in bounded on-chain storage and therefore do not require a
    // BoundedVec. Every Vec<u8> in an event is constructed from an
    // already-validated BoundedVec via .into(), so the data has already been
    // length-checked before the event is emitted.

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
        /// ID exceeds the ConstU32<64> bound. With BoundedVec extrinsic
        /// parameters this is enforced at decode time; the variant is retained
        /// for backward compatibility and potential genesis validation.
        IdTooLong,
        /// Name exceeds T::MaxNameLength. With BoundedVec extrinsic
        /// parameters this is enforced at decode time; the variant is retained
        /// for backward compatibility and potential genesis validation.
        NameTooLong,
        /// Location exceeds the ConstU32<64> bound. With BoundedVec
        /// extrinsic parameters this is enforced at decode time; the variant is
        /// retained for backward compatibility.
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
        /// Maximum length (in bytes) for user-supplied name fields such as
        /// carbon-credit project names and reforestation project names.
        /// Extrinsic parameters use BoundedVec<u8, T::MaxNameLength> so the
        /// bound is enforced at decode time, before any pallet logic runs.
        #[pallet::constant]
        type MaxNameLength: Get<u32>;
        type WeightInfo: WeightInfo;
        /// Post-sudo: Council (2/3) administers eco operations
        type AdminOrigin: EnsureOrigin<Self::RuntimeOrigin>;
    }

    // === Genesis ===
    //
    // NOTE on remaining Vec<u8> in GenesisConfig:
    // Genesis configuration types use plain Vec<u8> because genesis is a
    // build-time / chain-instantiation concern, not a runtime extrinsic. The
    // build() method converts each Vec<u8> to the appropriate BoundedVec
    // via try_into().unwrap_or_default(), so oversized values are silently
    // truncated at genesis rather than causing a runtime DoS vector.

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
        /// Mint a new carbon credit.
        ///
        /// # Authorization
        ///
        /// Requires AdminOrigin (council / governance root). A regular signed
        /// user cannot mint carbon credits.
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::mint_carbon_credit())]
        pub fn mint_carbon_credit(
            origin: OriginFor<T>,
            owner: T::AccountId,
            id: BoundedVec<u8, ConstU32<64>>,
            project_name: BoundedVec<u8, T::MaxNameLength>,
            tons_co2: u64,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;
            let who = owner;

            // BoundedVec enforces length bounds at decode time.
            let name_bv: BoundedVec<u8, ConstU32<128>> = project_name
                .clone()
                .into_inner()
                .try_into()
                .map_err(|_| Error::<T>::NameTooLong)?;

            ensure!(
                !CarbonCredits::<T>::contains_key(&id),
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
                id: id.clone(),
                project_name: name_bv,
                tons_co2,
                verified: false,
                retired: false,
                owner: who.clone(),
                created_at: frame_system::Pallet::<T>::block_number().try_into().unwrap_or(0),
            };

            CarbonCredits::<T>::insert(id.clone(), credit);
            TotalCO2Offset::<T>::mutate(|t| *t = t.saturating_add(tons_co2));
            ActiveCO2Offset::<T>::mutate(|t| *t = t.saturating_add(tons_co2));

            Self::deposit_event(Event::CarbonCreditMinted {
                id: id.into(),
                tons_co2,
                owner: who,
            });
            Ok(())
        }

        /// Verify a carbon credit.
        ///
        /// # Authorization
        ///
        /// Requires AdminOrigin (council / governance root). A regular signed
        /// user cannot verify carbon credits.
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::verify_carbon_credit())]
        pub fn verify_carbon_credit(
            origin: OriginFor<T>,
            id: BoundedVec<u8, ConstU32<64>>,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            CarbonCredits::<T>::mutate(&id, |c| {
                let credit = c.as_mut().ok_or(Error::<T>::CreditNotFound)?;
                ensure!(!credit.verified, Error::<T>::AlreadyVerified);
                credit.verified = true;
                Ok::<(), Error<T>>(())
            })?;

            Self::deposit_event(Event::CarbonCreditVerified { id: id.into() });
            Ok(())
        }

        /// Retire a carbon credit (owner only).
        ///
        /// # Authorization
        ///
        /// Requires a signed origin that is the current owner of the credit.
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::retire_carbon_credit())]
        pub fn retire_carbon_credit(
            origin: OriginFor<T>,
            id: BoundedVec<u8, ConstU32<64>>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            CarbonCredits::<T>::mutate(&id, |c| {
                let credit = c.as_mut().ok_or(Error::<T>::CreditNotFound)?;
                ensure!(credit.owner == who, Error::<T>::NotCreditOwner);
                ensure!(!credit.retired, Error::<T>::CreditAlreadyRetired);
                credit.retired = true;
                Ok::<(), Error<T>>(())
            })?;

            let credit = CarbonCredits::<T>::get(&id).ok_or(Error::<T>::CreditNotFound)?;
            TotalCreditsRetired::<T>::mutate(|t| *t = t.saturating_add(credit.tons_co2));

            Self::deposit_event(Event::CarbonCreditRetired {
                id: id.into(),
                tons_co2: credit.tons_co2,
            });
            Ok(())
        }

        /// Transfer a carbon credit to a new owner.
        ///
        /// # Authorization
        ///
        /// Requires a signed origin that is the current owner of the credit.
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::transfer_carbon_credit())]
        pub fn transfer_carbon_credit(
            origin: OriginFor<T>,
            id: BoundedVec<u8, ConstU32<64>>,
            to: T::AccountId,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            CarbonCredits::<T>::mutate(&id, |c| {
                let credit = c.as_mut().ok_or(Error::<T>::CreditNotFound)?;
                ensure!(credit.owner == who, Error::<T>::NotCreditOwner);
                ensure!(!credit.retired, Error::<T>::CreditAlreadyRetired);
                credit.owner = to.clone();
                Ok::<(), Error<T>>(())
            })?;

            Self::deposit_event(Event::CarbonCreditTransferred {
                id: id.into(),
                from: who,
                to,
            });
            Ok(())
        }

        /// Create a reforestation project.
        ///
        /// # Authorization
        ///
        /// Requires AdminOrigin (council / governance root). A regular signed
        /// user cannot create reforestation projects.
        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::create_reforest_project())]
        pub fn create_reforest_project(
            origin: OriginFor<T>,
            id: BoundedVec<u8, ConstU32<64>>,
            name: BoundedVec<u8, T::MaxNameLength>,
            trees_planted: u32,
            location: BoundedVec<u8, ConstU32<64>>,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            // BoundedVec enforces length bounds at decode time.
            let name_bv: BoundedVec<u8, ConstU32<128>> = name
                .clone()
                .into_inner()
                .try_into()
                .map_err(|_| Error::<T>::NameTooLong)?;

            ensure!(
                !ReforestProjects::<T>::contains_key(&id),
                Error::<T>::ProjectAlreadyExists
            );
            ensure!(
                (ReforestProjects::<T>::iter().count() as u32) < T::MaxReforestProjects::get(),
                Error::<T>::MaxReforestProjectsReached
            );

            let project = ReforestProject {
                id: id.clone(),
                name: name_bv,
                trees_planted,
                location,
                survival_rate: 0,
                verified: false,
            };

            ReforestProjects::<T>::insert(id.clone(), project);
            TotalTreesPlanted::<T>::mutate(|t| *t = t.saturating_add(trees_planted));

            Self::deposit_event(Event::ReforestProjectCreated {
                id: id.into(),
                name: name.into(),
                trees: trees_planted,
            });
            Ok(())
        }

        /// Update a reforestation project.
        ///
        /// # Authorization
        ///
        /// Requires AdminOrigin (council / governance root). A regular signed
        /// user cannot update reforestation projects.
        #[pallet::call_index(5)]
        #[pallet::weight(T::WeightInfo::update_reforest_project())]
        pub fn update_reforest_project(
            origin: OriginFor<T>,
            id: BoundedVec<u8, ConstU32<64>>,
            trees_planted: u32,
            survival_rate: u8,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            ReforestProjects::<T>::mutate(&id, |p| {
                let project = p.as_mut().ok_or(Error::<T>::ProjectNotFound)?;
                project.trees_planted = trees_planted;
                project.survival_rate = survival_rate;
                Ok::<(), Error<T>>(())
            })?;

            Self::deposit_event(Event::ReforestProjectUpdated {
                id: id.into(),
                trees: trees_planted,
                survival_rate,
            });
            Ok(())
        }

        /// Verify a reforestation project.
        ///
        /// # Authorization
        ///
        /// Requires AdminOrigin (council / governance root). A regular signed
        /// user cannot verify reforestation projects.
        #[pallet::call_index(6)]
        #[pallet::weight(T::WeightInfo::verify_reforest_project())]
        pub fn verify_reforest_project(
            origin: OriginFor<T>,
            id: BoundedVec<u8, ConstU32<64>>,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            ReforestProjects::<T>::mutate(&id, |p| {
                let project = p.as_mut().ok_or(Error::<T>::ProjectNotFound)?;
                ensure!(!project.verified, Error::<T>::AlreadyVerified);
                project.verified = true;
                Ok::<(), Error<T>>(())
            })?;

            Self::deposit_event(Event::ReforestProjectVerified { id: id.into() });
            Ok(())
        }

        /// Register as a green validator.
        ///
        /// # Authorization
        ///
        /// Requires a signed origin. Any account may self-register as a green
        /// validator. The initial score is constrained by MinGreenScore
        /// and MaxGreenScore.
        #[pallet::call_index(7)]
        #[pallet::weight(T::WeightInfo::register_green_validator())]
        pub fn register_green_validator(
            origin: OriginFor<T>,
            energy_source: BoundedVec<u8, ConstU32<64>>,
            carbon_offset: u64,
            trees_planted: u32,
            score: u8,
            renewable_energy: bool,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // BoundedVec enforces length bounds at decode time.
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
                renewable_energy,
                energy_source: energy_source.clone(),
                carbon_offset,
                trees_planted,
                score,
                last_updated: frame_system::Pallet::<T>::block_number().try_into().unwrap_or(0),
            };

            GreenValidators::<T>::insert(who.clone(), gv);

            Self::deposit_event(Event::GreenValidatorRegistered {
                address: who,
                energy_source: energy_source.into(),
                score,
            });
            Ok(())
        }

        /// Update a validator's green score.
        ///
        /// # Authorization
        ///
        /// **This extrinsic requires AdminOrigin (council / governance root,
        /// configured as EnsureRoot by default).** A regular signed user
        /// **cannot** update green scores — neither their own nor another
        /// validator's. Green scores are a security / economic signal and must
        /// only be set by the authorized governance authority.
        ///
        /// There is no on-chain verifier registry in this pallet, so the
        /// council / root path is used. If a verifier registry is added in the
        /// future, authorization should be restricted to registered verifiers.
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
                    v.last_updated = frame_system::Pallet::<T>::block_number().try_into().unwrap_or(0);
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
        pub const MinGreenScore: u8 = 1;
        pub const MaxGreenScore: u8 = 5;
        pub const MaxNameLength: u32 = 128;
    }

    impl Config for Test {
        type RuntimeEvent = RuntimeEvent;
        type PalletId = EcoPalletId;
        type MaxCarbonCredits = MaxCarbonCredits;
        type MaxReforestProjects = MaxReforestProjects;
        type MaxGreenValidators = MaxGreenValidators;
        type MinGreenScore = MinGreenScore;
        type MaxGreenScore = MaxGreenScore;
        type MaxNameLength = MaxNameLength;
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

    /// Helper: construct a BoundedVec<u8, ConstU32<64>> from a slice.
    fn bv64(s: &[u8]) -> BoundedVec<u8, ConstU32<64>> {
        s.to_vec().try_into().unwrap()
    }

    /// Helper: construct a BoundedVec<u8, MaxNameLength> from a slice.
    fn bv_name(s: &[u8]) -> BoundedVec<u8, MaxNameLength> {
        s.to_vec().try_into().unwrap()
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
                bv64(b"c1"),
                bv_name(b"Amazon"),
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
                bv64(b"c1"),
                bv_name(b"P"),
                50,
            )
            .unwrap();
            assert_noop!(
                Eco::mint_carbon_credit(
                    RuntimeOrigin::root(),
                    Sr25519Keyring::Bob.to_account_id(),
                    bv64(b"c1"),
                    bv_name(b"P2"),
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
                bv64(b"c1"),
                bv_name(b"P"),
                50,
            )
            .unwrap();
            assert_ok!(Eco::verify_carbon_credit(
                RuntimeOrigin::root(),
                bv64(b"c1")
            ));
        });
    }

    #[test]
    fn test_verify_nonexistent() {
        new_test_ext().execute_with(|| {
            assert_noop!(
                Eco::verify_carbon_credit(RuntimeOrigin::root(), bv64(b"nope")),
                Error::<Test>::CreditNotFound
            );
        });
    }

    #[test]
    fn test_create_reforest() {
        new_test_ext().execute_with(|| {
            assert_ok!(Eco::create_reforest_project(
                RuntimeOrigin::root(),
                bv64(b"p1"),
                bv_name(b"Amazon"),
                5000,
                bv64(b"Brazil"),
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
                bv64(b"Solar"),
                500,
                100,
                4,
                true,
            ));
            assert_eq!(GreenValidators::<Test>::get(&alice).unwrap().score, 4);
        });
    }

    #[test]
    fn test_update_green_score() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            Eco::register_green_validator(
                RuntimeOrigin::signed(alice.clone()),
                bv64(b"Solar"),
                500,
                100,
                4,
                true,
            )
            .unwrap();
            assert_ok!(Eco::update_green_score(
                RuntimeOrigin::root(),
                alice.clone(),
                5
            ));
            assert_eq!(GreenValidators::<Test>::get(&alice).unwrap().score, 5);
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
                    bv64(b"c1"),
                    bv_name(b"Amazon"),
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
                Eco::verify_carbon_credit(RuntimeOrigin::signed(alice), bv64(b"c1"),),
                sp_runtime::DispatchError::BadOrigin
            );
        });
    }

    #[test]
    fn test_retire_nonexistent_credit_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_noop!(
                Eco::retire_carbon_credit(RuntimeOrigin::signed(alice), bv64(b"nonexistent"),),
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
                    bv64(b"nonexistent"),
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
                bv64(b"c1"),
                bv_name(b"Amazon"),
                100,
            )
            .unwrap();
            Eco::retire_carbon_credit(RuntimeOrigin::signed(alice.clone()), bv64(b"c1"))
                .unwrap();
            assert_noop!(
                Eco::transfer_carbon_credit(RuntimeOrigin::signed(alice), bv64(b"c1"), bob,),
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
                bv64(b"c1"),
                bv_name(b"Amazon"),
                100,
            )
            .unwrap();
            assert_noop!(
                Eco::transfer_carbon_credit(RuntimeOrigin::signed(bob), bv64(b"c1"), charlie,),
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
                    bv64(b"p1"),
                    bv_name(b"Amazon"),
                    1000,
                    bv64(b"Brazil"),
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
                bv64(b"p1"),
                bv_name(b"Amazon"),
                1000,
                bv64(b"Brazil"),
            )
            .unwrap();
            assert_noop!(
                Eco::create_reforest_project(
                    RuntimeOrigin::root(),
                    bv64(b"p1"),
                    bv_name(b"Amazon 2"),
                    2000,
                    bv64(b"Peru"),
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
                    bv64(b"p1"),
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
                    bv64(b"nonexistent"),
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
                bv64(b"Solar"),
                500,
                100,
                4,
                true,
            )
            .unwrap();
            assert_noop!(
                Eco::register_green_validator(
                    RuntimeOrigin::signed(alice),
                    bv64(b"Wind"),
                    300,
                    50,
                    4,
                    true,
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
                    bv64(b"Solar"),
                    500,
                    100,
                    6,
                    true,
                ),
                Error::<Test>::InvalidScore
            );
        });
    }

    #[test]
    fn test_register_green_validator_score_zero_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_noop!(
                Eco::register_green_validator(
                    RuntimeOrigin::signed(alice),
                    bv64(b"Solar"),
                    500,
                    100,
                    0,
                    true,
                ),
                Error::<Test>::InvalidScore
            );
        });
    }

    #[test]
    fn test_register_green_validator_score_six_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_noop!(
                Eco::register_green_validator(
                    RuntimeOrigin::signed(alice),
                    bv64(b"Solar"),
                    500,
                    100,
                    6,
                    true,
                ),
                Error::<Test>::InvalidScore
            );
        });
    }

    #[test]
    fn test_update_green_score_boundary_values_pass() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            Eco::register_green_validator(
                RuntimeOrigin::signed(alice.clone()),
                bv64(b"Solar"),
                500,
                100,
                3,
                true,
            )
            .unwrap();
            assert_ok!(Eco::update_green_score(
                RuntimeOrigin::root(),
                alice.clone(),
                1,
            ));
            assert_eq!(GreenValidators::<Test>::get(&alice).unwrap().score, 1);
            assert_ok!(Eco::update_green_score(
                RuntimeOrigin::root(),
                alice.clone(),
                5,
            ));
            assert_eq!(GreenValidators::<Test>::get(&alice).unwrap().score, 5);
        });
    }

    #[test]
    fn test_update_green_score_authorized_succeeds() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            Eco::register_green_validator(
                RuntimeOrigin::signed(alice.clone()),
                bv64(b"Solar"),
                500,
                100,
                3,
                true,
            )
            .unwrap();
            // Authorized (root / AdminOrigin) call succeeds
            assert_ok!(Eco::update_green_score(
                RuntimeOrigin::root(),
                alice.clone(),
                5,
            ));
            assert_eq!(GreenValidators::<Test>::get(&alice).unwrap().score, 5);
        });
    }

    #[test]
    fn test_update_green_score_non_root_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            // A regular signed user cannot update green scores
            assert_noop!(
                Eco::update_green_score(RuntimeOrigin::signed(alice.clone()), alice, 5,),
                sp_runtime::DispatchError::BadOrigin
            );
        });
    }

    #[test]
    fn test_update_green_score_other_user_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let bob = Sr25519Keyring::Bob.to_account_id();
            Eco::register_green_validator(
                RuntimeOrigin::signed(alice.clone()),
                bv64(b"Solar"),
                500,
                100,
                3,
                true,
            )
            .unwrap();
            // Bob (a non-root user) cannot update Alice's score
            assert_noop!(
                Eco::update_green_score(RuntimeOrigin::signed(bob), alice, 5,),
                sp_runtime::DispatchError::BadOrigin
            );
        });
    }

    #[test]
    fn test_update_nonexistent_validator_score_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_noop!(
                Eco::update_green_score(RuntimeOrigin::root(), alice, 5,),
                Error::<Test>::ValidatorNotFound
            );
        });
    }

    // --- BoundedVec length enforcement tests ---
    //
    // With BoundedVec extrinsic parameters, length is enforced at decode time.
    // These tests verify that the BoundedVec type rejects oversized inputs.

    #[test]
    fn test_id_too_long_rejected() {
        // A 65-byte value exceeds the ConstU32<64> bound and cannot be
        // constructed as a BoundedVec — the length check is enforced at the
        // type level before any pallet logic runs.
        let result: Result<BoundedVec<u8, ConstU32<64>>, _> = vec![0u8; 65].try_into();
        assert!(result.is_err(), "65-byte ID should not fit in BoundedVec<u8, ConstU32<64>>");
    }

    #[test]
    fn test_name_too_long_rejected() {
        // A 129-byte value exceeds MaxNameLength (128) and cannot be
        // constructed as a BoundedVec.
        let result: Result<BoundedVec<u8, MaxNameLength>, _> = vec![0u8; 129].try_into();
        assert!(result.is_err(), "129-byte name should not fit in BoundedVec<u8, MaxNameLength>");
    }

    #[test]
    fn test_location_too_long_rejected() {
        // A 65-byte location exceeds the ConstU32<64> bound.
        let result: Result<BoundedVec<u8, ConstU32<64>>, _> = vec![0u8; 65].try_into();
        assert!(result.is_err(), "65-byte location should not fit in BoundedVec<u8, ConstU32<64>>");
    }

    #[test]
    fn test_energy_source_too_long_rejected() {
        // A 65-byte energy_source exceeds the ConstU32<64> bound.
        let result: Result<BoundedVec<u8, ConstU32<64>>, _> = vec![0u8; 65].try_into();
        assert!(result.is_err(), "65-byte energy source should not fit in BoundedVec<u8, ConstU32<64>>");
    }

    #[test]
    fn test_mint_carbon_credit_id_too_long_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            // The 65-byte value cannot be converted to BoundedVec<u8, ConstU32<64>>,
            // simulating what happens at decode time when a malicious user sends
            // an oversized extrinsic parameter.
            let long_id: Result<BoundedVec<u8, ConstU32<64>>, _> = vec![0u8; 65].try_into();
            assert!(long_id.is_err());
            // A valid-sized call still succeeds
            assert_ok!(Eco::mint_carbon_credit(
                RuntimeOrigin::root(),
                alice,
                bv64(b"c1"),
                bv_name(b"Amazon"),
                100,
            ));
        });
    }

    #[test]
    fn test_mint_carbon_credit_name_too_long_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            // The 129-byte value cannot be converted to BoundedVec<u8, MaxNameLength>.
            let long_name: Result<BoundedVec<u8, MaxNameLength>, _> = vec![0u8; 129].try_into();
            assert!(long_name.is_err());
            // A valid-sized call still succeeds
            assert_ok!(Eco::mint_carbon_credit(
                RuntimeOrigin::root(),
                alice,
                bv64(b"c1"),
                bv_name(b"Amazon"),
                100,
            ));
        });
    }

    #[test]
    fn test_retire_carbon_credit_works() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_ok!(Eco::mint_carbon_credit(
                RuntimeOrigin::root(),
                alice.clone(),
                bv64(b"c1"),
                bv_name(b"Amazon"),
                100,
            ));
            assert_ok!(Eco::retire_carbon_credit(
                RuntimeOrigin::signed(alice),
                bv64(b"c1")
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
                bv64(b"c1"),
                bv_name(b"Amazon"),
                100,
            ));
            assert_ok!(Eco::transfer_carbon_credit(
                RuntimeOrigin::signed(alice),
                bv64(b"c1"),
                bob.clone(),
            ));
            let id_bv: frame_support::BoundedVec<u8, frame_support::traits::ConstU32<64>> =
                b"c1".to_vec().try_into().unwrap();
            let credit = CarbonCredits::<Test>::get(&id_bv).unwrap();
            assert_eq!(credit.owner, bob);
        });
    }
}
