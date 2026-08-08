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
use frame_support::traits::tokens::ExistenceRequirement;
use frame_support::{
    dispatch::DispatchResult,
    ensure,
    pallet_prelude::*,
    traits::{Currency, Get, ReservableCurrency},
    DefaultNoBound, PalletId,
};
use frame_system::pallet_prelude::*;
use scale_info::TypeInfo;
use sp_runtime::traits::{AccountIdConversion, Saturating};
use sp_std::prelude::*;

#[cfg(feature = "std")]
use serde::{Deserialize, Serialize};

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use super::*;
    type BalanceOf<T> =
        <<T as Config>::Currency as Currency<<T as frame_system::Config>::AccountId>>::Balance;

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

    #[derive(Encode, Decode, Clone, PartialEq, Eq, MaxEncodedLen, TypeInfo)]
    pub struct UnbondingRequest<AccountId, Balance> {
        pub who: AccountId,
        pub validator: AccountId,
        pub amount: Balance,
        pub unlock_block: u32,
    }

    // === Storage ===

    #[pallet::storage]
    #[pallet::getter(fn validators)]
    pub type Validators<T: Config> =
        StorageMap<_, Blake2_128Concat, T::AccountId, Validator<T::AccountId, BalanceOf<T>>>;

    #[pallet::storage]
    #[pallet::getter(fn validator_list)]
    pub type ValidatorList<T: Config> =
        StorageValue<_, BoundedVec<T::AccountId, ConstU32<101>>, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn votes)]
    pub type Votes<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        BoundedVec<VoteRecord<T::AccountId, BalanceOf<T>>, ConstU32<64>>,
    >;

    #[pallet::storage]
    #[pallet::getter(fn active_validators)]
    pub type ActiveValidators<T: Config> =
        StorageValue<_, BoundedVec<T::AccountId, ConstU32<101>>, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn current_epoch)]
    pub type CurrentEpoch<T: Config> = StorageValue<_, u32, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn epoch_start_block)]
    pub type EpochStartBlock<T: Config> = StorageValue<_, u32, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn total_staked)]
    pub type TotalStaked<T: Config> = StorageValue<_, BalanceOf<T>, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn slashing_events)]
    pub type SlashingEvents<T: Config> =
        StorageMap<_, Blake2_128Concat, T::AccountId, u32, ValueQuery>;

    #[pallet::storage]
    #[pallet::getter(fn validator_names)]
    pub type ValidatorNames<T: Config> = StorageMap<_, Blake2_128Concat, T::AccountId, BoundedVec<u8, ConstU32<32>>>;

    #[pallet::storage]
    #[pallet::getter(fn unbonding_queue)]
    pub type UnbondingQueue<T: Config> = StorageMap<
        _,
        Blake2_128Concat,
        T::AccountId,
        BoundedVec<UnbondingRequest<T::AccountId, BalanceOf<T>>, ConstU32<16>>,
    >;

    // === Events ===

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        ValidatorRegistered {
            who: T::AccountId,
            stake: BalanceOf<T>,
        },
        ValidatorUnregistered {
            who: T::AccountId,
        },
        Voted {
            voter: T::AccountId,
            validator: T::AccountId,
            amount: BalanceOf<T>,
        },
        Unvoted {
            voter: T::AccountId,
            validator: T::AccountId,
        },
        BlockReward {
            validator: T::AccountId,
            reward: BalanceOf<T>,
            block: u32,
        },
        ValidatorSlashed {
            who: T::AccountId,
            penalty: BalanceOf<T>,
            reason: Vec<u8>,
        },
        EpochChanged {
            epoch: u32,
            validators: Vec<T::AccountId>,
        },
        GreenScoreUpdated {
            validator: T::AccountId,
            score: u8,
        },
        RewardPoolDepleted {
            remaining: BalanceOf<T>,
        },
        UnbondingStarted {
            who: T::AccountId,
            validator: T::AccountId,
            amount: BalanceOf<T>,
            unlock_block: u32,
        },
        Withdrawn {
            who: T::AccountId,
            amount: BalanceOf<T>,
        },
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
        NameTooLong,
        NameUpdated,
        InvalidSlashReason,
        RewardPoolDepleted,
        UnbondingPeriodNotElapsed,
        NoUnbondingRequest,
        StakeExceedsCap,
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
        #[pallet::constant]
        type UnbondingPeriod: Get<u32>;
        type PalletId: Get<PalletId>;
        #[pallet::constant]
        type MaxStakePerValidator: Get<BalanceOf<Self>>;
        type WeightInfo: WeightInfo;
    }

    // === Genesis Configuration ===

    #[pallet::genesis_config]
    #[derive(DefaultNoBound)]
    pub struct GenesisConfig<T: Config> {
        pub validators: Vec<(T::AccountId, BalanceOf<T>, bool)>,
        pub validator_count: u32,
        pub block_reward: BalanceOf<T>,
        pub validator_names: Vec<(T::AccountId, Vec<u8>)>,
    }

    #[pallet::genesis_build]
    impl<T: Config> BuildGenesisConfig for GenesisConfig<T> {
        fn build(&self) {
            let mut list: BoundedVec<T::AccountId, ConstU32<101>> = BoundedVec::default();
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
                list.try_push(addr.clone()).ok();
                total = total.saturating_add(*stake);
            }
            ValidatorList::<T>::put(list.clone());
            TotalStaked::<T>::put(total);
            // Insert validator names
            for (addr, name) in &self.validator_names {
                if let Ok(bounded) = BoundedVec::<u8, ConstU32<32>>::try_from(name.clone()) {
                    ValidatorNames::<T>::insert(addr.clone(), bounded);
                }
            }
            ActiveValidators::<T>::put(list);
            CurrentEpoch::<T>::put(1);
            EpochStartBlock::<T>::put(0);
        }
    }

    // === Hooks ===

    #[pallet::hooks]
    impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T> {
        fn on_initialize(block: BlockNumberFor<T>) -> Weight {
            let block_num: u32 = block.try_into().unwrap_or(0);

            // Check epoch transition
            let epoch_start = EpochStartBlock::<T>::get();
            let epoch_length = T::EpochLength::get();

            if block_num.saturating_sub(epoch_start) >= epoch_length {
                Self::rotate_epoch(block_num);
            }

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

            let total_staked = TotalStaked::<T>::get();
            ensure!(
                total_staked.saturating_add(stake) <= T::MaxStakePerValidator::get()
                    || stake <= T::MaxStakePerValidator::get(),
                Error::<T>::StakeExceedsCap
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
            ValidatorList::<T>::mutate(|v| v.try_push(who.clone()).ok());
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
        pub fn vote(
            origin: OriginFor<T>,
            validator: T::AccountId,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            ensure!(
                Validators::<T>::contains_key(&validator),
                Error::<T>::ValidatorNotFound
            );
            ensure!(
                T::Currency::can_reserve(&who, amount),
                Error::<T>::InsufficientFunds
            );

            let max_stake = T::MaxStakePerValidator::get();
            let val = Validators::<T>::get(&validator).ok_or(Error::<T>::ValidatorNotFound)?;
            ensure!(
                val.total_votes.saturating_add(amount) <= max_stake,
                Error::<T>::StakeExceedsCap
            );

            T::Currency::reserve(&who, amount)?;

            let vote = VoteRecord {
                voter: who.clone(),
                validator: validator.clone(),
                amount,
            };

            Votes::<T>::mutate(&who, |v| {
                v.get_or_insert_with(BoundedVec::default)
                    .try_push(vote)
                    .ok();
            });

            Validators::<T>::mutate(&validator, |val| {
                if let Some(v) = val {
                    v.total_votes = v.total_votes.saturating_add(amount);
                }
            });

            TotalStaked::<T>::mutate(|t| *t = t.saturating_add(amount));

            Self::deposit_event(Event::Voted {
                voter: who,
                validator,
                amount,
            });
            Ok(())
        }

        /// Remove vote from a validator (starts unbonding period)
        #[pallet::call_index(3)]
        #[pallet::weight(T::WeightInfo::unvote())]
        pub fn unvote(origin: OriginFor<T>, validator: T::AccountId) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let mut votes = Votes::<T>::get(&who).unwrap_or_default();
            let vote = votes
                .iter()
                .find(|v| v.validator == validator)
                .ok_or(Error::<T>::NoVotesForValidator)?;

            let amount = vote.amount;

            // Keep funds reserved during unbonding period (do NOT unreserve yet)
            votes.retain(|v| v.validator != validator);
            Votes::<T>::insert(&who, votes);

            Validators::<T>::mutate(&validator, |val| {
                if let Some(v) = val {
                    v.total_votes = v.total_votes.saturating_sub(amount);
                }
            });

            // Reduce total staked but keep funds locked in unbonding queue
            TotalStaked::<T>::mutate(|t| *t = t.saturating_sub(amount));

            // Queue the unbonding request
            let current_block: u32 = frame_system::Pallet::<T>::block_number()
                .try_into()
                .map_err(|_| Error::<T>::InvalidSlashReason)?;
            let unlock_block = current_block.saturating_add(T::UnbondingPeriod::get());

            let request = UnbondingRequest {
                who: who.clone(),
                validator: validator.clone(),
                amount,
                unlock_block,
            };

            UnbondingQueue::<T>::mutate(&who, |queue| {
                queue
                    .get_or_insert_with(BoundedVec::default)
                    .try_push(request.clone())
                    .ok();
            });

            Self::deposit_event(Event::UnbondingStarted {
                who,
                validator,
                amount,
                unlock_block,
            });
            Ok(())
        }

        /// Withdraw unbonded funds after unbonding period elapses
        #[pallet::call_index(6)]
        #[pallet::weight(T::WeightInfo::unvote())]
        pub fn withdraw_unbonded(origin: OriginFor<T>) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let mut queue = UnbondingQueue::<T>::get(&who).unwrap_or_default();
            ensure!(!queue.is_empty(), Error::<T>::NoUnbondingRequest);

            let current_block: u32 = frame_system::Pallet::<T>::block_number()
                .try_into()
                .map_err(|_| Error::<T>::InvalidSlashReason)?;

            let mut total_withdrawable: BalanceOf<T> = BalanceOf::<T>::zero();
            queue.retain(|req| {
                if current_block >= req.unlock_block {
                    total_withdrawable = total_withdrawable.saturating_add(req.amount);
                    false // remove from queue
                } else {
                    true // keep in queue
                }
            });

            ensure!(
                total_withdrawable > BalanceOf::<T>::zero(),
                Error::<T>::UnbondingPeriodNotElapsed
            );

            // Now actually unreserve and return funds
            T::Currency::unreserve(&who, total_withdrawable);

            if queue.is_empty() {
                UnbondingQueue::<T>::remove(&who);
            } else {
                UnbondingQueue::<T>::insert(&who, queue);
            }

            Self::deposit_event(Event::Withdrawn {
                who,
                amount: total_withdrawable,
            });
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

            let slash_amount = penalty.min(val.stake);

            // Unreserve the slash amount, then transfer to treasury (not burned)
            let _ = T::Currency::unreserve(&validator, slash_amount);
            let treasury = T::PalletId::get().into_account_truncating();
            let _ = T::Currency::transfer(
                &validator,
                &treasury,
                slash_amount,
                ExistenceRequirement::AllowDeath,
            );

            Validators::<T>::mutate(&validator, |v| {
                if let Some(v) = v {
                    v.stake = v.stake.saturating_sub(slash_amount);
                    v.slashed = true;
                }
            });

            SlashingEvents::<T>::mutate(&validator, |c| *c += 1);
            TotalStaked::<T>::mutate(|t| *t = t.saturating_sub(slash_amount));

            Self::deposit_event(Event::ValidatorSlashed {
                who: validator,
                penalty: slash_amount,
                reason,
            });
            Ok(())
        }

        /// Update green score (self-reported by validator)
        #[pallet::call_index(5)]
        #[pallet::weight(T::WeightInfo::update_green_score())]
        pub fn update_green_score(origin: OriginFor<T>, score: u8) -> DispatchResult {
            let who = ensure_signed(origin)?;

            ensure!(
                Validators::<T>::contains_key(&who),
                Error::<T>::NotValidator
            );

            Validators::<T>::mutate(&who, |v| {
                if let Some(v) = v {
                    v.green_score = score;
                }
            });

            Self::deposit_event(Event::GreenScoreUpdated {
                validator: who,
                score,
            });
            Ok(())
        }
    }

    // === Internal Functions ===

    impl<T: Config> Pallet<T> {
        /// Internal slash function callable by the offence handler (no origin check)
        pub fn do_slash(validator: &T::AccountId, slash_amount: BalanceOf<T>) {
            if let Some(val) = Validators::<T>::get(validator) {
                let slash_amount = slash_amount.min(val.stake);
                let _ = T::Currency::unreserve(validator, slash_amount);
                let treasury = T::PalletId::get().into_account_truncating();
                let _ = T::Currency::transfer(
                    validator,
                    &treasury,
                    slash_amount,
                    ExistenceRequirement::AllowDeath,
                );
                Validators::<T>::mutate(validator, |v| {
                    if let Some(v) = v {
                        v.stake = v.stake.saturating_sub(slash_amount);
                        v.slashed = true;
                    }
                });
                SlashingEvents::<T>::mutate(validator, |c| *c += 1);
                TotalStaked::<T>::mutate(|t| *t = t.saturating_sub(slash_amount));
                Self::deposit_event(Event::ValidatorSlashed {
                    who: validator.clone(),
                    penalty: slash_amount,
                    reason: b"equivocation".to_vec(),
                });
            }
        }

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

            let mut bounded_active: BoundedVec<T::AccountId, ConstU32<101>> = BoundedVec::default();
            for addr in new_active.iter().take(101) {
                bounded_active.try_push(addr.clone()).ok();
            }
            ActiveValidators::<T>::put(bounded_active);

            Self::deposit_event(Event::EpochChanged {
                epoch,
                validators: new_active,
            });
        }

        /// Distribute block reward to validator from pre-funded reward pool
        pub fn reward_block_producer(validator: &T::AccountId, block: u32) {
            let reward = T::BlockReward::get();

            if let Some(_val) = Validators::<T>::get(validator) {
                // Transfer from pre-funded reward pool instead of minting
                let reward_pool = T::PalletId::get().into_account_truncating();
                let pool_balance = T::Currency::free_balance(&reward_pool);

                if pool_balance < reward {
                    // Pool depleted — no more rewards
                    Self::deposit_event(Event::RewardPoolDepleted {
                        remaining: pool_balance,
                    });
                    return;
                }

                let _ = T::Currency::transfer(
                    &reward_pool,
                    validator,
                    reward,
                    ExistenceRequirement::AllowDeath,
                );

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

        /// Determine the next validator in rotation based on active validators or validator list
        pub fn get_next_validator(current: Option<&T::AccountId>) -> Option<T::AccountId> {
            let active = ActiveValidators::<T>::get();
            if !active.is_empty() {
                match current {
                    Some(curr) => {
                        if let Some(pos) = active.iter().position(|x| x == curr) {
                            let next_pos = (pos + 1) % active.len();
                            Some(active[next_pos].clone())
                        } else {
                            Some(active[0].clone())
                        }
                    }
                    None => Some(active[0].clone()),
                }
            } else {
                let list = ValidatorList::<T>::get();
                if list.is_empty() {
                    return None;
                }
                match current {
                    Some(curr) => {
                        if let Some(pos) = list.iter().position(|x| x == curr) {
                            let next_pos = (pos + 1) % list.len();
                            Some(list[next_pos].clone())
                        } else {
                            Some(list[0].clone())
                        }
                    }
                    None => Some(list[0].clone()),
                }
            }
        }
    }

    // === Session Manager Implementation ===
    impl<T: Config> pallet_session::SessionManager<T::AccountId> for Pallet<T> {
        fn new_session(_index: u32) -> Option<Vec<T::AccountId>> {
            let active = ActiveValidators::<T>::get();
            if active.is_empty() {
                None
            } else {
                Some(active.into_iter().collect())
            }
        }

        fn start_session(_index: u32) {}

        fn end_session(_index: u32) {}
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

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;

#[cfg(test)]
mod tests {
    use super::*;
    use frame_support::{
        assert_noop, assert_ok, construct_runtime, derive_impl, parameter_types,
        traits::{ConstU128, ConstU32, Hooks},
    };
    use sp_io::TestExternalities;
    use sp_keyring::Sr25519Keyring;
    use sp_runtime::{traits::IdentityLookup, BuildStorage};

    type Block = frame_system::mocking::MockBlock<Test>;

    construct_runtime!(
        pub enum Test {
            System: frame_system,
            Balances: pallet_balances,
            Dpos: crate,
        }
    );

    #[derive_impl(frame_system::config_preludes::TestDefaultConfig as frame_system::DefaultConfig)]
    impl frame_system::Config for Test {
        type AccountId = sp_core::crypto::AccountId32;
        type Lookup = IdentityLookup<Self::AccountId>;
        type Block = Block;
        type AccountData = pallet_balances::AccountData<u128>;
    }

    impl pallet_balances::Config for Test {
        type MaxLocks = ConstU32<50>;
        type MaxReserves = ConstU32<50>;
        type ReserveIdentifier = [u8; 8];
        type Balance = u128;
        type RuntimeEvent = RuntimeEvent;
        type DustRemoval = ();
        type ExistentialDeposit = ConstU128<1>;
        type AccountStore = System;
        type WeightInfo = ();
        type FreezeIdentifier = ();
        type MaxFreezes = ConstU32<0>;
        type RuntimeHoldReason = ();
        type RuntimeFreezeReason = ();
        type DoneSlashHandler = ();
    }

    parameter_types! {
        pub const BlockReward: u128 = 100;
        pub const MinStake: u128 = 1000;
        pub const MaxValidators: u32 = 10;
        pub const ActiveValidatorCount: u32 = 3;
        pub const EpochLength: u32 = 10;
        pub const UnbondingPeriod: u32 = 20;
        pub const DposPalletId: PalletId = PalletId(*b"v/dposps");
        pub const MaxStakePerValidator: u128 = 100_000;
    }

    impl Config for Test {
        type RuntimeEvent = RuntimeEvent;
        type Currency = Balances;
        type BlockReward = BlockReward;
        type MinStake = MinStake;
        type MaxValidators = MaxValidators;
        type ActiveValidatorCount = ActiveValidatorCount;
        type EpochLength = EpochLength;
        type UnbondingPeriod = UnbondingPeriod;
        type PalletId = DposPalletId;
        type MaxStakePerValidator = MaxStakePerValidator;
        type WeightInfo = SubstrateWeight<Test>;
    }

    pub fn new_test_ext() -> TestExternalities {
        let mut t = frame_system::GenesisConfig::<Test>::default()
            .build_storage()
            .unwrap();

        // Fund the DPoS reward pool (PalletId account)
        let reward_pool: sp_core::crypto::AccountId32 =
            PalletId(*b"v/dposps").into_account_truncating();

        pallet_balances::GenesisConfig::<Test> {
            balances: vec![
                (Sr25519Keyring::Alice.to_account_id(), 100_000),
                (Sr25519Keyring::Bob.to_account_id(), 100_000),
                (Sr25519Keyring::Charlie.to_account_id(), 100_000),
                (Sr25519Keyring::Dave.to_account_id(), 500),
                (reward_pool, 10_000_000), // Pre-funded reward pool
            ],
            ..Default::default()
        }
        .assimilate_storage(&mut t)
        .unwrap();

        GenesisConfig::<Test> {
            validators: vec![
                (Sr25519Keyring::Alice.to_account_id(), 5000, true),
                (Sr25519Keyring::Bob.to_account_id(), 3000, true),
            ],
            validator_count: 2,
            block_reward: 100,
        }
        .assimilate_storage(&mut t)
        .unwrap();

        let mut ext = TestExternalities::new(t);
        ext.execute_with(|| System::set_block_number(1));
        ext
    }

    #[test]
    fn test_genesis_initial_state() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let bob = Sr25519Keyring::Bob.to_account_id();

            assert!(Validators::<Test>::contains_key(&alice));
            assert!(Validators::<Test>::contains_key(&bob));

            let alice_val = Validators::<Test>::get(&alice).unwrap();
            assert_eq!(alice_val.stake, 5000);
            assert_eq!(alice_val.active, true);

            assert_eq!(ValidatorList::<Test>::get().len(), 2);
            assert_eq!(ActiveValidators::<Test>::get().len(), 2);
            assert_eq!(TotalStaked::<Test>::get(), 8000);
            assert_eq!(CurrentEpoch::<Test>::get(), 1);
        });
    }

    #[test]
    fn test_register_validator_success() {
        new_test_ext().execute_with(|| {
            let charlie = Sr25519Keyring::Charlie.to_account_id();
            let energy = b"Solar".to_vec();

            assert_ok!(Dpos::register_validator(
                RuntimeOrigin::signed(charlie.clone()),
                85,
                energy
            ));

            assert!(Validators::<Test>::contains_key(&charlie));
            let val = Validators::<Test>::get(&charlie).unwrap();
            assert_eq!(val.stake, 1000);
            assert_eq!(val.green_score, 85);
            assert_eq!(TotalStaked::<Test>::get(), 9000);
        });
    }

    #[test]
    fn test_register_validator_errors() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let dave = Sr25519Keyring::Dave.to_account_id();

            // Already registered
            assert_noop!(
                Dpos::register_validator(RuntimeOrigin::signed(alice), 90, b"Wind".to_vec()),
                Error::<Test>::ValidatorAlreadyRegistered
            );

            // Insufficient funds (Dave only has 500, MinStake is 1000)
            assert_noop!(
                Dpos::register_validator(RuntimeOrigin::signed(dave), 90, b"Wind".to_vec()),
                Error::<Test>::InsufficientFunds
            );
        });
    }

    #[test]
    fn test_unregister_validator_success() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();

            assert_ok!(Dpos::unregister_validator(RuntimeOrigin::signed(
                alice.clone()
            )));
            assert!(!Validators::<Test>::contains_key(&alice));
            assert_eq!(TotalStaked::<Test>::get(), 3000);
        });
    }

    #[test]
    fn test_unregister_validator_errors() {
        new_test_ext().execute_with(|| {
            let charlie = Sr25519Keyring::Charlie.to_account_id();

            assert_noop!(
                Dpos::unregister_validator(RuntimeOrigin::signed(charlie)),
                Error::<Test>::ValidatorNotFound
            );
        });
    }

    #[test]
    fn test_vote_and_unvote_success() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let charlie = Sr25519Keyring::Charlie.to_account_id();

            assert_ok!(Dpos::vote(
                RuntimeOrigin::signed(charlie.clone()),
                alice.clone(),
                2000
            ));
            assert_eq!(TotalStaked::<Test>::get(), 10000);

            let val = Validators::<Test>::get(&alice).unwrap();
            assert_eq!(val.total_votes, 7000);

            // Unvote starts unbonding (funds stay reserved, not immediately returned)
            assert_ok!(Dpos::unvote(
                RuntimeOrigin::signed(charlie.clone()),
                alice.clone()
            ));
            assert_eq!(TotalStaked::<Test>::get(), 8000);

            let val2 = Validators::<Test>::get(&alice).unwrap();
            assert_eq!(val2.total_votes, 5000);

            // Check unbonding queue was created
            let queue = UnbondingQueue::<Test>::get(&charlie).unwrap_or_default();
            assert_eq!(queue.len(), 1);
            assert_eq!(queue[0].amount, 2000);
            assert_eq!(queue[0].unlock_block, 21); // block 0 + UnbondingPeriod 20

            // Cannot withdraw yet (unbonding period not elapsed)
            assert_noop!(
                Dpos::withdraw_unbonded(RuntimeOrigin::signed(charlie.clone())),
                Error::<Test>::UnbondingPeriodNotElapsed
            );

            // Advance past unbonding period
            System::set_block_number(21);
            System::reset_events();

            // Now can withdraw
            let balance_before = Balances::free_balance(&charlie);
            assert_ok!(Dpos::withdraw_unbonded(RuntimeOrigin::signed(
                charlie.clone()
            )));
            let balance_after = Balances::free_balance(&charlie);
            assert_eq!(
                balance_after - balance_before,
                2000,
                "Charlie should get 2000 back"
            );

            // Queue should be empty
            assert!(
                UnbondingQueue::<Test>::get(&charlie).is_none()
                    || UnbondingQueue::<Test>::get(&charlie).unwrap().is_empty()
            );
        });
    }

    #[test]
    fn test_vote_and_unvote_errors() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let charlie = Sr25519Keyring::Charlie.to_account_id();
            let dave = Sr25519Keyring::Dave.to_account_id();

            // Vote for non-existent validator
            assert_noop!(
                Dpos::vote(RuntimeOrigin::signed(charlie.clone()), dave, 500),
                Error::<Test>::ValidatorNotFound
            );

            // Vote with insufficient funds
            assert_noop!(
                Dpos::vote(
                    RuntimeOrigin::signed(charlie.clone()),
                    alice.clone(),
                    200_000
                ),
                Error::<Test>::InsufficientFunds
            );

            // Unvote without prior vote
            assert_noop!(
                Dpos::unvote(RuntimeOrigin::signed(charlie), alice),
                Error::<Test>::NoVotesForValidator
            );
        });
    }

    #[test]
    fn test_slash_validator_success() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let treasury: sp_core::crypto::AccountId32 =
                PalletId(*b"v/dposps").into_account_truncating();
            let treasury_before = Balances::free_balance(&treasury);

            assert_ok!(Dpos::slash_validator(
                RuntimeOrigin::root(),
                alice.clone(),
                1000,
                b"double signing".to_vec()
            ));

            let val = Validators::<Test>::get(&alice).unwrap();
            assert_eq!(val.stake, 4000);
            assert!(val.slashed);
            assert_eq!(SlashingEvents::<Test>::get(&alice), 1);

            // Slashed funds should go to treasury, not burned
            let treasury_after = Balances::free_balance(&treasury);
            assert_eq!(
                treasury_after - treasury_before,
                1000,
                "Treasury should receive slashed funds"
            );
        });
    }

    #[test]
    fn test_slash_validator_errors() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let charlie = Sr25519Keyring::Charlie.to_account_id();

            // Non-root origin
            assert_noop!(
                Dpos::slash_validator(
                    RuntimeOrigin::signed(charlie.clone()),
                    alice.clone(),
                    1000,
                    b"bad behavior".to_vec()
                ),
                sp_runtime::DispatchError::BadOrigin
            );

            // Validator not found
            assert_noop!(
                Dpos::slash_validator(
                    RuntimeOrigin::root(),
                    charlie,
                    1000,
                    b"bad behavior".to_vec()
                ),
                Error::<Test>::ValidatorNotFound
            );

            // Invalid reason (empty)
            assert_noop!(
                Dpos::slash_validator(RuntimeOrigin::root(), alice, 1000, vec![]),
                Error::<Test>::InvalidSlashReason
            );
        });
    }

    #[test]
    fn test_update_green_score() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let charlie = Sr25519Keyring::Charlie.to_account_id();

            assert_ok!(Dpos::update_green_score(
                RuntimeOrigin::signed(alice.clone()),
                95
            ));
            assert_eq!(Validators::<Test>::get(&alice).unwrap().green_score, 95);

            assert_noop!(
                Dpos::update_green_score(RuntimeOrigin::signed(charlie), 95),
                Error::<Test>::NotValidator
            );
        });
    }

    #[test]
    fn test_epoch_rotation() {
        new_test_ext().execute_with(|| {
            assert_eq!(CurrentEpoch::<Test>::get(), 1);
            System::set_block_number(11);
            Dpos::on_initialize(11);
            assert_eq!(CurrentEpoch::<Test>::get(), 2);
            assert_eq!(EpochStartBlock::<Test>::get(), 11);
        });
    }

    #[test]
    fn test_reward_block_producer() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();

            Dpos::reward_block_producer(&alice, 1);
            let val = Validators::<Test>::get(&alice).unwrap();
            assert_eq!(val.blocks_produced, 1);
            assert_eq!(val.rewards_earned, 100);
        });
    }

    #[test]
    fn test_reward_pool_depletion() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let reward_pool: sp_core::crypto::AccountId32 =
                PalletId(*b"v/dposps").into_account_truncating();

            // Pool starts with 10_000_000, reward is 100 per block
            // After 100_000 rewards, pool should be depleted
            for i in 0..100_001 {
                Dpos::reward_block_producer(&alice, i as u32);
            }

            // Pool should be depleted (or very close)
            let pool_balance = pallet_balances::Pallet::<Test>::free_balance(&reward_pool);
            assert!(
                pool_balance < 100,
                "Pool should be depleted, got: {}",
                pool_balance
            );

            // Validator should have earned less than full amount (pool ran out)
            let val = Validators::<Test>::get(&alice).unwrap();
            assert!(
                val.rewards_earned <= 10_000_000,
                "Rewards should not exceed pool"
            );
        });
    }

    #[test]
    fn test_no_new_tokens_minted() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let reward_pool: sp_core::crypto::AccountId32 =
                PalletId(*b"v/dposps").into_account_truncating();

            let total_before = pallet_balances::Pallet::<Test>::total_issuance();
            let pool_before = pallet_balances::Pallet::<Test>::free_balance(&reward_pool);
            let alice_before = pallet_balances::Pallet::<Test>::free_balance(&alice);

            Dpos::reward_block_producer(&alice, 1);

            let total_after = pallet_balances::Pallet::<Test>::total_issuance();
            let pool_after = pallet_balances::Pallet::<Test>::free_balance(&reward_pool);
            let alice_after = pallet_balances::Pallet::<Test>::free_balance(&alice);

            // Total issuance must NOT change (no minting)
            assert_eq!(total_before, total_after, "Total issuance must not change");
            // Pool decreases by reward
            assert_eq!(
                pool_before - pool_after,
                100,
                "Pool should decrease by reward"
            );
            // Alice increases by reward
            assert_eq!(
                alice_after - alice_before,
                100,
                "Alice should receive reward"
            );
        });
    }
}
