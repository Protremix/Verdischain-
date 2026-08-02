//! # Verdis DPoS Consensus Pallet
//!
//! Delegated Proof of Stake consensus with:
//! - Validator registration and staking
//! - Voter delegation
//! - Block reward distribution
//! - Validator slashing for misbehavior
//! - Green validator scoring integration
//! - Epoch-based validator rotation

#![cfg_attr(not(feature = "std"), no_std)]

use codec::{Decode, Encode, MaxEncodedLen};
use frame_support::{DefaultNoBound,
    dispatch::DispatchResult,
    ensure,
    pallet_prelude::*,
    traits::{Currency, Get, ReservableCurrency, tokens::ExistenceRequirement},
    PalletId,
};
use frame_system::pallet_prelude::*;
use scale_info::TypeInfo;
use sp_runtime::traits::{AccountIdConversion, Saturating};
use sp_std::{collections::btree_map::BTreeMap, prelude::*};

#[cfg(feature = "std")]
use serde::{Deserialize, Serialize};

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use super::*;
    type BalanceOf<T> = <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    // === Types ===

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo)]
    #[cfg_attr(feature = "std", derive(Serialize, Deserialize))]
    pub struct Validator<AccountId, Balance> {
        pub address: AccountId,
        pub stake: Balance,
        pub total_votes: Balance,
        pub blocks_produced: u64,
        pub rewards_earned: Balance,
        pub active: bool,
        pub slashed: bool,
        pub green_score: u8,
        pub energy_source: BoundedVec<u8, ConstU32<64>>,
    }

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo)]
    pub struct VoteRecord<AccountId, Balance> {
        pub voter: AccountId,
        pub validator: AccountId,
        pub amount: Balance,
    }

    // === Storage ===

    #[pallet::storage]
    #[pallet::getter(fn validators)]
    pub type Validators<T: Config> =
        StorageMap<_, Blake2_128Concat, T::AccountId, Validator<T::AccountId, BalanceOf<T>>>;

    #[pallet::storage]
    #[pallet::getter(fn validator_list)]
    pub type ValidatorList<T: Config> = StorageValue<_, Vec<T::AccountId>, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn votes)]
    pub type Votes<T: Config> =
        StorageMap<_, Blake2_128Concat, T::AccountId, BoundedVec<VoteRecord<T::AccountId, BalanceOf<T>>, ConstU32<64>>>;

    #[pallet::storage]
    #[pallet::getter(fn active_validators)]
    pub type ActiveValidators<T: Config> = StorageValue<_, Vec<T::AccountId>, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn current_epoch)]
    pub type CurrentEpoch<T: Config> = StorageValue<_, u32, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter fn epoch_start_block]
    pub type EpochStartBlock<T: Config> = StorageValue<_, u32, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn total_staked)]
    pub type TotalStaked<T: Config> = StorageValue<_, BalanceOf<T>, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn slashing_events)]
    pub type SlashingEvents<T: Config> =
        StorageMap<_, Blake2_128Concat, T::AccountId, u32, ValueQuery>;

    // === Events ===

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        ValidatorRegistered { who: T::AccountId, stake: BalanceOf<T> },
        ValidatorUnregistered { who: T::AccountId },
        Voted { voter: T::AccountId, validator: T::AccountId, amount: BalanceOf<T> },
        Unvoted { voter: T::AccountId, validator: T::AccountId },
        BlockReward { validator: T::AccountId, reward: BalanceOf<T>, block: u32 },
        ValidatorSlashed { who: T::AccountId, penalty: BalanceOf<T>, reason: Vec<u8> },
        EpochChanged { epoch: u32, validators: Vec<T::AccountId> },
        GreenScoreUpdated { validator: T::AccountId, score: u8 },
    }

    // === Errors ===

    #[pallet::error]
    pub enum Error<T> {
        InsufficientStake,
        ValidatorNotFound,
        ValidatorAlreadyRegistered,
        NotActiveValidator,
        MaxValidatorsReached,
        InsufficientFunds,
        NoVotesForValidator,
        SlashingFailed,
        NotValidator,
        InvalidSlashReason,
    }

    // === Config ===

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        type Currency: ReservableCurrency<Self::AccountId>;
        #[pallet::constant]
        type BlockReward: Get<BalanceOf<Self>>;
        #[pallet::constant]
        type MinStake: Get<BalanceOf<Self>>;
        #[pallet::constant]
        type MaxValidators: Get<u32>;
        #[pallet::constant]
        type ActiveValidatorCount: Get<u32>;
        #[pallet::constant]
        type EpochLength: Get<u32>;
        type PalletId: Get<PalletId>;
        type WeightInfo: WeightInfo;
    }

    // === Genesis Configuration ===

    #[pallet::genesis_config]
    #[derive(DefaultNoBound)]
    pub struct GenesisConfig<T: Config> {
        pub validators: Vec<(T::AccountId, BalanceOf<T>, bool)>,
        pub validator_count: u32,
        pub block_reward: BalanceOf<T>,
    }

    #[pallet::genesis_build]
    impl<T: Config> BuildGenesisConfig for GenesisConfig<T> {
        fn build(&self) {
            let mut list = Vec::new();
            let mut total = BalanceOf::<T>::zero();
            for (addr, stake, active) in &self.validators {
                let validator = Validator {
                    address: addr.clone(),
                    stake: *stake,
                    total_votes: *stake,
                    blocks_produced: 0,
                    rewards_earned: BalanceOf::<T>::zero(),
                    active: *active,
                    slashed: false,
                    green_score: 0,
                    energy_source: b"Unknown".to_vec().try_into().unwrap_or_default(),
                };
                Validators::<T>::insert(addr, validator);
                list.push(addr.clone());
                total = total.saturating_add(*stake);
            }
            ValidatorList::<T>::put(list.clone());
            TotalStaked::<T>::put(total);
            ActiveValidators::<T>::put(list);
            CurrentEpoch::<T>::put(1);
            EpochStartBlock::<T>::put(0);
        }
    }

    // === Hooks ===

    #[pallet::hooks]
    impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T> {
        fn on_initialize(block: T::BlockNumber) -> Weight {
            let block_num: u32 = block.try_into().unwrap_or(0);

            // Check epoch transition
            let epoch_start = EpochStartBlock::<T>::get();
            let epoch_length = T::EpochLength::get();

            if block_num.saturating_sub(epoch_start) >= epoch_length {
                Self::rotate_epoch(block_num);
            }

            // Reward the block producer
            let block_author = frame_system::Pallet::<T>::events()
                .last()
                .map(|e| {
                    // In production, block author is determined by Aura
                    T::AccountId::decode(&mut &[][..]).unwrap_or_default()
                });

            Weight::zero()
        }
    }

    // === Extrinsics ===

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Register as a validator with a minimum stake
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::register_validator())]
        pub fn register_validator(
            origin: OriginFor<T>,
            green_score: u8,
            energy_source: Vec<u8>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            ensure!(
                !Validators::<T>::contains_key(&who),
                Error::<T>::ValidatorAlreadyRegistered
            );

            let stake = T::MinStake::get();
            ensure!(
                T::Currency::can_reserve(&who, stake),
                Error::<T>::InsufficientFunds
            );

            let validator_count = ValidatorList::<T>::get().len() as u32;
            ensure!(
                validator_count < T::MaxValidators::get(),
                Error::<T>::MaxValidatorsReached
            );

            T::Currency::reserve(&who, stake)?;

            let validator = Validator {
                address: who.clone(),
                stake,
                total_votes: stake,
                blocks_produced: 0,
                rewards_earned: BalanceOf::<T>::zero(),
                active: true,
                slashed: false,
                green_score,
                energy_source: energy_source.clone().try_into().unwrap_or_default(),
            };

            Validators::<T>::insert(&who, validator);
            ValidatorList::<T>::mutate(|v| v.push(who.clone()));
            TotalStaked::<T>::mutate(|t| *t = t.saturating_add(stake));

            Self::deposit_event(Event::ValidatorRegistered { who, stake });
            Ok(())
        }

        /// Unregister as a validator (releases stake)
        #[pallet::call_index(1)]
        #[pallet::weight(T::WeightInfo::unregister_validator())]
        pub fn unregister_validator(origin: OriginFor<T>) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let validator = Validators::<T>::get(&who).ok_or(Error::<T>::ValidatorNotFound)?;
            ensure!(validator.active, Error::<T>::NotActiveValidator);

            T::Currency::unreserve(&who, validator.stake);
            Validators::<T>::remove(&who);
            ValidatorList::<T>::mutate(|v| v.retain(|a| a != &who));
            ActiveValidators::<T>::mutate(|v| v.retain(|a| a != &who));
            TotalStaked::<T>::mutate(|t| *t = t.saturating_sub(validator.stake));

            Self::deposit_event(Event::ValidatorUnregistered { who });
            Ok(())
        }

        /// Vote for a validator by delegating stake
        #[pallet::call_index(2)]
        #[pallet::weight(T::WeightInfo::vote())]
        pub fn vote(origin: OriginFor<T>, validator: T::AccountId, amount: BalanceOf<T>) -> DispatchResult {
            let who = ensure_signed(origin)?;

            ensure!(Validators::<T>::contains_key(&validator), Error::<T>::ValidatorNotFound);
            ensure!(T::Currency::can_reserve(&who, amount), Error::<T>::InsufficientFunds);

            T::Currency::reserve(&who, amount)?;

            let vote = VoteRecord {
                voter: who.clone(),
                validator: validator.clone(),
                amount,
            };

            Votes::<T>::mutate(&who, |v| {
                v.get_or_insert_with(BoundedVec::default).try_push(vote).ok();
            });

            Validators::<T>::mutate(&validator, |val| {
                if let Some(v) = val {
                    v.total_votes = v.total_votes.saturating_add(amount);
                }
            });

            TotalStaked::<T>::mutate(|t| *t = t.saturating_add(amount));

            Self::deposit_event(Event::Voted { who, validator, amount });
            Ok(())
        }

        /// Remove vote from a validator
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::unvote())]
        pub fn unvote(origin: OriginFor<T>, validator: T::AccountId) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let mut votes = Votes::<T>::get(&who).unwrap_or_default();
            let vote = votes.iter().find(|v| v.validator == validator)
                .ok_or(Error::<T>::NoVotesForValidator)?;

            let amount = vote.amount;
            T::Currency::unreserve(&who, amount);
            votes.retain(|v| v.validator != validator);
            Votes::<T>::insert(&who, votes);

            Validators::<T>::mutate(&validator, |val| {
                if let Some(v) = val {
                    v.total_votes = v.total_votes.saturating_sub(amount);
                }
            });

            TotalStaked::<T>::mutate(|t| *t = t.saturating_sub(amount));

            Self::deposit_event(Event::Unvoted { who, validator });
            Ok(())
        }

        /// Slash a validator for misbehavior (governance only)
        #[pallet::call_index(4)]
        #[pallet::weight(T::WeightInfo::slash_validator())]
        pub fn slash_validator(
            origin: OriginFor<T>,
            validator: T::AccountId,
            penalty: BalanceOf<T>,
            reason: Vec<u8>,
        ) -> DispatchResult {
            ensure_root(origin)?;

            let val = Validators::<T>::get(&validator).ok_or(Error::<T>::ValidatorNotFound)?;
            ensure!(!reason.is_empty(), Error::<T>::InvalidSlashReason);

            let slashed = T::Currency::slash(&validator, penalty.min(val.stake)).0;

            Validators::<T>::mutate(&validator, |v| {
                if let Some(v) = v {
                    v.stake = v.stake.saturating_sub(slashed);
                    v.slashed = true;
                }
            });

            SlashingEvents::<T>::mutate(&validator, |c| *c += 1);
            TotalStaked::<T>::mutate(|t| *t = t.saturating_sub(slashed));

            Self::deposit_event(Event::ValidatorSlashed {
                who: validator,
                penalty: slashed,
                reason,
            });
            Ok(())
        }

        /// Update green score (self-reported by validator)
        #[pallet::call_index(5)]
        #[pallet::weight(T::WeightInfo::update_green_score())]
        pub fn update_green_score(origin: OriginFor<T>, score: u8) -> DispatchResult {
            let who = ensure_signed(origin)?;

            ensure!(Validators::<T>::contains_key(&who), Error::<T>::NotValidator);

            Validators::<T>::mutate(&who, |v| {
                if let Some(v) = v {
                    v.green_score = score;
                }
            });

            Self::deposit_event(Event::GreenScoreUpdated { who, score });
            Ok(())
        }
    }

    // === Internal Functions ===

    impl<T: Config> Pallet<T> {
        /// Rotate epoch — select top validators by votes
        fn rotate_epoch(block: u32) {
            let mut all_validators: Vec<(T::AccountId, BalanceOf<T>)> = ValidatorList::<T>::get()
                .into_iter()
                .filter_map(|addr| {
                    Validators::<T>::get(&addr)
                        .filter(|v| v.active && !v.slashed)
                        .map(|v| (addr, v.total_votes))
                })
                .collect();

            // Sort by votes descending
            all_validators.sort_by(|a, b| b.1.cmp(&a.1));

            let active_count = T::ActiveValidatorCount::get() as usize;
            let new_active: Vec<T::AccountId> = all_validators
                .into_iter()
                .take(active_count)
                .map(|(addr, _)| addr)
                .collect();

            let epoch = CurrentEpoch::<T>::get() + 1;
            CurrentEpoch::<T>::put(epoch);
            EpochStartBlock::<T>::put(block);
            ActiveValidators::<T>::put(new_active.clone());

            Self::deposit_event(Event::EpochChanged {
                epoch,
                validators: new_active,
            });
        }

        /// Distribute block reward to validator
        pub fn reward_block_producer(validator: &T::AccountId, block: u32) {
            let reward = T::BlockReward::get();

            if let Some(val) = Validators::<T>::get(validator) {
                let _ = T::Currency::deposit_creating(validator, reward);
                Validators::<T>::mutate(validator, |v| {
                    if let Some(v) = v {
                        v.blocks_produced += 1;
                        v.rewards_earned = v.rewards_earned.saturating_add(reward);
                    }
                });

                Self::deposit_event(Event::BlockReward {
                    validator: validator.clone(),
                    reward,
                    block,
                });
            }
        }
    }

    // === Session Manager Implementation ===
    impl<T: Config> pallet_session::SessionManager<T::AccountId> for Pallet<T> {
        fn new_session(index: u32) -> Option<Vec<T::AccountId>> {
            let active = ActiveValidators::<T>::get();
            if active.is_empty() {
                None
            } else {
                Some(active)
            }
        }

        fn end_session(index: u32) {}
        fn before_session_start() {}
    }

    // === WeightInfo Trait ===
    pub trait WeightInfo {
        fn register_validator() -> Weight;
        fn unregister_validator() -> Weight;
        fn vote() -> Weight;
        fn unvote() -> Weight;
        fn slash_validator() -> Weight;
        fn update_green_score() -> Weight;
    }

    pub struct SubstrateWeight<T>(PhantomData<T>);
    impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
        fn register_validator() -> Weight {
            Weight::from_parts(100_000_000, 0)
        }
        fn unregister_validator() -> Weight {
            Weight::from_parts(80_000_000, 0)
        }
        fn vote() -> Weight {
            Weight::from_parts(60_000_000, 0)
        }
        fn unvote() -> Weight {
            Weight::from_parts(50_000_000, 0)
        }
        fn slash_validator() -> Weight {
            Weight::from_parts(90_000_000, 0)
        }
        fn update_green_score() -> Weight {
            Weight::from_parts(20_000_000, 0)
        }
    }
}

// === Type Aliases ===

pub struct ValidatorIdOf<T>(PhantomData<T>);
impl<T: Config> sp_runtime::traits::Convert<T::AccountId, Option<T::AccountId>>
    for ValidatorIdOf<T>
{
    fn convert(a: T::AccountId) -> Option<T::AccountId> {
        if Validators::<T>::contains_key(&a) {
            Some(a)
        } else {
            None
        }
    }
}

pub struct ShouldEndSession<T>(PhantomData<T>);
impl<T: Config> pallet_session::ShouldEndSession<u32> for ShouldEndSession<T> {
    fn should_end_session(now: u32) -> bool {
        let epoch_length = T::EpochLength::get();
        now % epoch_length == 0
    }
}

pub struct NextSessionRotation<T>(PhantomData<T>);
impl<T: Config> pallet_session::EstimateNextSessionRotation<u32> for NextSessionRotation<T> {
    fn average_session_length() -> u32 {
        T::EpochLength::get()
    }
    fn estimate_current_session_progress(now: u32) -> (Option<sp_runtime::Percent>, Weight) {
        let epoch_length = T::EpochLength::get();
        let epoch_start = EpochStartBlock::<T>::get();
        let progress = now.saturating_sub(epoch_start);
        let percent = sp_runtime::Percent::from_rational(progress, epoch_length);
        (Some(percent), Weight::zero())
    }
    fn estimate_next_session_rotation(now: u32) -> (Option<u32>, Weight) {
        let epoch_length = T::EpochLength::get();
        let next = (now / epoch_length + 1) * epoch_length;
        (Some(next), Weight::zero())
    }
}
