#!/usr/bin/env python3
"""Patch the DPoS pallet with all 10 security fixes."""

import re

LIB_RS = '/opt/verdis-chain-rust/pallets/dpos/src/lib.rs'

with open(LIB_RS, 'r') as f:
    content = f.read()

original = content

# ============================================================
# FIX 1: Add error variants
# ============================================================
old_errors = """        UnbondingPeriodNotElapsed,
        NoUnbondingRequest,
        StakeExceedsCap,
    }"""

new_errors = """        UnbondingPeriodNotElapsed,
        NoUnbondingRequest,
        StakeExceedsCap,
        ActiveDelegations,
        AlreadyVoted,
        VoteStorageFull,
        UnbondingQueueFull,
    }"""

assert old_errors in content, "FIX 1: Could not find error enum end"
content = content.replace(old_errors, new_errors)
print("FIX 1: Added error variants")

# ============================================================
# FIX 2: Genesis build - fix try_push .ok() and ActiveValidators
# ============================================================
old_genesis_push = """                Validators::<T>::insert(addr, validator);
                list.try_push(addr.clone()).ok();
                total = total.saturating_add(*stake);"""

new_genesis_push = """                Validators::<T>::insert(addr, validator);
                list.try_push(addr.clone()).expect("validator list overflow at genesis");
                total = total.saturating_add(*stake);"""

assert old_genesis_push in content, "FIX 2a: Could not find genesis try_push"
content = content.replace(old_genesis_push, new_genesis_push)

# Fix ActiveValidators in genesis - only put up to ActiveValidatorCount
old_genesis_active = """            ActiveValidators::<T>::put(list);
            CurrentEpoch::<T>::put(1);"""

new_genesis_active = """            let mut active_list: BoundedVec<T::AccountId, ConstU32<101>> = BoundedVec::default();
            for addr in list.iter().take(T::ActiveValidatorCount::get() as usize) {
                let _ = active_list.try_push(addr.clone());
            }
            ActiveValidators::<T>::put(active_list);
            CurrentEpoch::<T>::put(1);"""

assert old_genesis_active in content, "FIX 2b: Could not find genesis ActiveValidators"
content = content.replace(old_genesis_active, new_genesis_active)
print("FIX 2: Genesis build fixed")

# ============================================================
# FIX 3: Validator stake cap in register_validator
# ============================================================
old_stake_cap = """            let total_staked = TotalStaked::<T>::get();
            ensure!(
                total_staked.saturating_add(stake) <= T::MaxStakePerValidator::get()
                    || stake <= T::MaxStakePerValidator::get(),
                Error::<T>::StakeExceedsCap
            );"""

new_stake_cap = """            ensure!(
                stake <= T::MaxStakePerValidator::get(),
                Error::<T>::StakeExceedsCap
            );"""

assert old_stake_cap in content, "FIX 3: Could not find stake cap"
content = content.replace(old_stake_cap, new_stake_cap)
print("FIX 3: Stake cap fixed")

# ============================================================
# FIX 4: register_validator - fix try_push .ok()
# ============================================================
old_reg_push = """            Validators::<T>::insert(&who, validator);
            ValidatorList::<T>::mutate(|v| v.try_push(who.clone()).ok());
            TotalStaked::<T>::mutate(|t| *t = t.saturating_add(stake));"""

new_reg_push = """            Validators::<T>::insert(&who, validator);
            ValidatorList::<T>::try_mutate(|v| {
                v.try_push(who.clone()).map_err(|_| Error::<T>::MaxValidatorsReached)
            })?;
            TotalStaked::<T>::mutate(|t| *t = t.saturating_add(stake));"""

assert old_reg_push in content, "FIX 4: Could not find register try_push"
content = content.replace(old_reg_push, new_reg_push)
print("FIX 4: Register try_push fixed")

# ============================================================
# FIX 5: unregister_validator - add active delegations check
# ============================================================
old_unreg = """            let validator = Validators::<T>::get(&who).ok_or(Error::<T>::ValidatorNotFound)?;
            ensure!(validator.active, Error::<T>::NotActiveValidator);

            T::Currency::unreserve(&who, validator.stake);"""

new_unreg = """            let validator = Validators::<T>::get(&who).ok_or(Error::<T>::ValidatorNotFound)?;
            ensure!(validator.active, Error::<T>::NotActiveValidator);
            ensure!(
                validator.total_votes <= validator.stake,
                Error::<T>::ActiveDelegations
            );

            T::Currency::unreserve(&who, validator.stake);"""

assert old_unreg in content, "FIX 5: Could not find unregister"
content = content.replace(old_unreg, new_unreg)
print("FIX 5: Unregister delegations check added")

# ============================================================
# FIX 6: vote() - add zero check, duplicate check, fix storage overflow
# ============================================================
old_vote_start = """        pub fn vote(
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
            });"""

new_vote_start = """        pub fn vote(
            origin: OriginFor<T>,
            validator: T::AccountId,
            amount: BalanceOf<T>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            ensure!(amount > BalanceOf::<T>::zero(), Error::<T>::InsufficientStake);
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

            // Prevent duplicate votes to the same validator
            let mut existing_votes = Votes::<T>::get(&who).unwrap_or_default();
            ensure!(
                !existing_votes.iter().any(|v| v.validator == validator),
                Error::<T>::AlreadyVoted
            );

            T::Currency::reserve(&who, amount)?;

            let vote = VoteRecord {
                voter: who.clone(),
                validator: validator.clone(),
                amount,
            };

            existing_votes
                .try_push(vote)
                .map_err(|_| Error::<T>::VoteStorageFull)?;
            Votes::<T>::insert(&who, existing_votes);"""

assert old_vote_start in content, "FIX 6: Could not find vote function start"
content = content.replace(old_vote_start, new_vote_start)
print("FIX 6: Vote function fixed (zero check, duplicate check, storage overflow)")

# ============================================================
# FIX 7: unvote() - fix unbonding queue overflow
# ============================================================
old_unbond = """            UnbondingQueue::<T>::mutate(&who, |queue| {
                queue
                    .get_or_insert_with(BoundedVec::default)
                    .try_push(request.clone())
                    .ok();
            });"""

new_unbond = """            UnbondingQueue::<T>::try_mutate(&who, |queue| {
                queue
                    .get_or_insert_with(BoundedVec::default)
                    .try_push(request.clone())
                    .map_err(|_| Error::<T>::UnbondingQueueFull)
            })?;"""

assert old_unbond in content, "FIX 7: Could not find unbonding queue push"
content = content.replace(old_unbond, new_unbond)
print("FIX 7: Unbonding queue overflow fixed")

# ============================================================
# FIX 8: slash_validator - fix accounting, handle errors, deactivate
# ============================================================
old_slash = """            let slash_amount = penalty.min(val.stake);

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
            TotalStaked::<T>::mutate(|t| *t = t.saturating_sub(slash_amount));"""

new_slash = """            let slash_amount = penalty.min(val.stake);
            ensure!(
                slash_amount > BalanceOf::<T>::zero(),
                Error::<T>::SlashingFailed
            );

            // Unreserve the slash amount, then transfer to treasury (not burned)
            let unreserved = T::Currency::unreserve(&validator, slash_amount);
            ensure!(unreserved == slash_amount, Error::<T>::SlashingFailed);
            let treasury = T::PalletId::get().into_account_truncating();
            T::Currency::transfer(
                &validator,
                &treasury,
                slash_amount,
                ExistenceRequirement::AllowDeath,
            )?;

            Validators::<T>::mutate(&validator, |v| {
                if let Some(v) = v {
                    v.stake = v.stake.saturating_sub(slash_amount);
                    v.total_votes = v.total_votes.saturating_sub(slash_amount);
                    v.slashed = true;
                    v.active = false;
                }
            });

            SlashingEvents::<T>::mutate(&validator, |c| *c += 1);
            TotalStaked::<T>::mutate(|t| *t = t.saturating_sub(slash_amount));
            ActiveValidators::<T>::mutate(|v| v.retain(|a| a != &validator));"""

assert old_slash in content, "FIX 8: Could not find slash_validator block"
content = content.replace(old_slash, new_slash)
print("FIX 8: Slash validator fixed")

# ============================================================
# FIX 9: do_slash() internal - same fixes
# ============================================================
old_do_slash = """            if let Some(val) = Validators::<T>::get(validator) {
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
                TotalStaked::<T>::mutate(|t| *t = t.saturating_sub(slash_amount));"""

new_do_slash = """            if let Some(val) = Validators::<T>::get(validator) {
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
                        v.total_votes = v.total_votes.saturating_sub(slash_amount);
                        v.slashed = true;
                        v.active = false;
                    }
                });
                SlashingEvents::<T>::mutate(validator, |c| *c += 1);
                TotalStaked::<T>::mutate(|t| *t = t.saturating_sub(slash_amount));
                ActiveValidators::<T>::mutate(|v| v.retain(|a| a != validator));"""

assert old_do_slash in content, "FIX 9: Could not find do_slash block"
content = content.replace(old_do_slash, new_do_slash)
print("FIX 9: do_slash internal fixed")

# ============================================================
# FIX 10: Epoch rotation - deterministic sorting
# ============================================================
old_sort = """            // Sort by votes descending
            all_validators.sort_by(|a, b| b.1.cmp(&a.1));"""

new_sort = """            // Sort by votes descending, break ties by account ID for determinism
            all_validators.sort_by(|a, b| {
                b.1.cmp(&a.1).then_with(|| a.0.cmp(&b.0))
            });"""

assert old_sort in content, "FIX 10: Could not find epoch sort"
content = content.replace(old_sort, new_sort)
print("FIX 10: Epoch rotation deterministic sorting")

# ============================================================
# FIX 11: rotate_epoch - fix try_push .ok()
# ============================================================
old_rotate_push = """            for addr in new_active.iter().take(101) {
                bounded_active.try_push(addr.clone()).ok();
            }"""

new_rotate_push = """            for addr in new_active.iter().take(101) {
                let _ = bounded_active.try_push(addr.clone());
            }"""

assert old_rotate_push in content, "FIX 11: Could not find rotate_epoch push"
content = content.replace(old_rotate_push, new_rotate_push)
print("FIX 11: rotate_epoch push fixed")

# ============================================================
# FIX 12: Green score - root only with validator param
# ============================================================
old_green = """        /// Update green score (self-reported by validator)
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
        }"""

new_green = """        /// Update green score (root only - prevents self-reporting)
        #[pallet::call_index(5)]
        #[pallet::weight(T::WeightInfo::update_green_score())]
        pub fn update_green_score(
            origin: OriginFor<T>,
            validator: T::AccountId,
            score: u8,
        ) -> DispatchResult {
            ensure_root(origin)?;

            ensure!(
                Validators::<T>::contains_key(&validator),
                Error::<T>::NotValidator
            );

            Validators::<T>::mutate(&validator, |v| {
                if let Some(v) = v {
                    v.green_score = score;
                }
            });

            Self::deposit_event(Event::GreenScoreUpdated {
                validator,
                score,
            });
            Ok(())
        }"""

assert old_green in content, "FIX 12: Could not find green score function"
content = content.replace(old_green, new_green)
print("FIX 12: Green score changed to root-only")

# ============================================================
# FIX 13: Update existing test_update_green_score
# ============================================================
old_green_test = """    #[test]
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
    }"""

new_green_test = """    #[test]
    fn test_update_green_score() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let charlie = Sr25519Keyring::Charlie.to_account_id();

            // Root can update any validator's green score
            assert_ok!(Dpos::update_green_score(
                RuntimeOrigin::root(),
                alice.clone(),
                95
            ));
            assert_eq!(Validators::<Test>::get(&alice).unwrap().green_score, 95);

            // Non-root origin is rejected
            assert_noop!(
                Dpos::update_green_score(
                    RuntimeOrigin::signed(charlie),
                    alice.clone(),
                    95
                ),
                sp_runtime::DispatchError::BadOrigin
            );
        });
    }"""

assert old_green_test in content, "FIX 13: Could not find green score test"
content = content.replace(old_green_test, new_green_test)
print("FIX 13: Green score test updated")

# ============================================================
# FIX 14: Update test_slash_validator_success to check new behavior
# ============================================================
old_slash_test = """    #[test]
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
    }"""

new_slash_test = """    #[test]
    fn test_slash_validator_success() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let treasury: sp_core::crypto::AccountId32 =
                PalletId(*b"v/dposps").into_account_truncating();
            let treasury_before = Balances::free_balance(&treasury);
            let total_staked_before = TotalStaked::<Test>::get();

            assert_ok!(Dpos::slash_validator(
                RuntimeOrigin::root(),
                alice.clone(),
                1000,
                b"double signing".to_vec()
            ));

            let val = Validators::<Test>::get(&alice).unwrap();
            assert_eq!(val.stake, 4000);
            assert_eq!(val.total_votes, 4000, "total_votes must be updated");
            assert!(val.slashed);
            assert!(!val.active, "Slashed validator must be deactivated");
            assert_eq!(SlashingEvents::<Test>::get(&alice), 1);
            assert_eq!(
                TotalStaked::<Test>::get(),
                total_staked_before - 1000,
                "TotalStaked must decrease by slash amount"
            );
            assert!(
                !ActiveValidators::<Test>::get().contains(&alice),
                "Slashed validator must be removed from ActiveValidators"
            );

            // Slashed funds should go to treasury, not burned
            let treasury_after = Balances::free_balance(&treasury);
            assert_eq!(
                treasury_after - treasury_before,
                1000,
                "Treasury should receive slashed funds"
            );
        });
    }"""

assert old_slash_test in content, "FIX 14: Could not find slash test"
content = content.replace(old_slash_test, new_slash_test)
print("FIX 14: Slash test updated")

# ============================================================
# FIX 15: Add regression tests before the closing brace
# ============================================================
new_tests = """
    #[test]
    fn test_unregister_with_delegations_fails() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let charlie = Sr25519Keyring::Charlie.to_account_id();

            // Charlie votes for Alice
            assert_ok!(Dpos::vote(
                RuntimeOrigin::signed(charlie.clone()),
                alice.clone(),
                2000
            ));

            // Alice cannot unregister while she has delegated votes
            assert_noop!(
                Dpos::unregister_validator(RuntimeOrigin::signed(alice)),
                Error::<Test>::ActiveDelegations
            );
        });
    }

    #[test]
    fn test_duplicate_vote_fails() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let charlie = Sr25519Keyring::Charlie.to_account_id();

            assert_ok!(Dpos::vote(
                RuntimeOrigin::signed(charlie.clone()),
                alice.clone(),
                1000
            ));

            // Second vote to same validator must fail
            assert_noop!(
                Dpos::vote(
                    RuntimeOrigin::signed(charlie.clone()),
                    alice,
                    1000
                ),
                Error::<Test>::AlreadyVoted
            );
        });
    }

    #[test]
    fn test_vote_above_validator_cap_fails() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let charlie = Sr25519Keyring::Charlie.to_account_id();

            // Alice has 5000 stake, MaxStakePerValidator is 100_000
            // Voting 96_000 would make total_votes = 101_000 > 100_000
            assert_noop!(
                Dpos::vote(
                    RuntimeOrigin::signed(charlie),
                    alice,
                    96_000
                ),
                Error::<Test>::StakeExceedsCap
            );
        });
    }

    #[test]
    fn test_zero_vote_fails() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let charlie = Sr25519Keyring::Charlie.to_account_id();

            assert_noop!(
                Dpos::vote(
                    RuntimeOrigin::signed(charlie),
                    alice,
                    0
                ),
                Error::<Test>::InsufficientStake
            );
        });
    }

    #[test]
    fn test_unbonding_queue_overflow() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let charlie = Sr25519Keyring::Charlie.to_account_id();

            // Fill unbonding queue to capacity (16)
            for _ in 0..16 {
                assert_ok!(Dpos::vote(
                    RuntimeOrigin::signed(charlie.clone()),
                    alice.clone(),
                    100
                ));
                assert_ok!(Dpos::unvote(
                    RuntimeOrigin::signed(charlie.clone()),
                    alice.clone()
                ));
            }

            let queue = UnbondingQueue::<Test>::get(&charlie).unwrap_or_default();
            assert_eq!(queue.len(), 16, "Queue should be at capacity");

            // 17th unbonding request must fail
            assert_ok!(Dpos::vote(
                RuntimeOrigin::signed(charlie.clone()),
                alice.clone(),
                100
            ));
            assert_noop!(
                Dpos::unvote(
                    RuntimeOrigin::signed(charlie.clone()),
                    alice
                ),
                Error::<Test>::UnbondingQueueFull
            );
        });
    }

    #[test]
    fn test_slashing_updates_accounting() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            let treasury: sp_core::crypto::AccountId32 =
                PalletId(*b"v/dposps").into_account_truncating();
            let treasury_before = Balances::free_balance(&treasury);
            let total_staked_before = TotalStaked::<Test>::get();

            assert_ok!(Dpos::slash_validator(
                RuntimeOrigin::root(),
                alice.clone(),
                1000,
                b"double signing".to_vec()
            ));

            let val = Validators::<Test>::get(&alice).unwrap();
            assert_eq!(val.stake, 4000, "Stake must decrease");
            assert_eq!(val.total_votes, 4000, "total_votes must decrease");
            assert!(val.slashed, "Must be marked slashed");
            assert!(!val.active, "Must be deactivated");
            assert_eq!(
                TotalStaked::<Test>::get(),
                total_staked_before - 1000,
                "TotalStaked must decrease"
            );
            assert!(
                !ActiveValidators::<Test>::get().contains(&alice),
                "Must be removed from ActiveValidators"
            );
            assert_eq!(
                Balances::free_balance(&treasury) - treasury_before,
                1000,
                "Treasury must receive slashed funds"
            );
        });
    }

    #[test]
    fn test_genesis_active_validator_count() {
        new_test_ext().execute_with(|| {
            let active = ActiveValidators::<Test>::get();
            // Genesis has 2 validators (Alice + Bob), ActiveValidatorCount is 3
            // So active should be min(2, 3) = 2
            assert_eq!(
                active.len(),
                2,
                "Active validators should be min(validator_count, ActiveValidatorCount)"
            );
        });
    }

    #[test]
    fn test_deterministic_epoch_rotation() {
        new_test_ext().execute_with(|| {
            let charlie = Sr25519Keyring::Charlie.to_account_id();

            // Register Charlie (stake = 1000 = MinStake)
            assert_ok!(Dpos::register_validator(
                RuntimeOrigin::signed(charlie.clone()),
                0,
                b"Solar".to_vec()
            ));

            // Rotate epoch at block 11
            System::set_block_number(11);
            Dpos::on_initialize(11);

            // Should have 3 active validators (Alice=5000, Bob=3000, Charlie=1000)
            let active = ActiveValidators::<Test>::get();
            assert_eq!(active.len(), 3, "Should have 3 active validators");

            // Run rotation again - should produce same result
            System::set_block_number(21);
            Dpos::on_initialize(21);
            let active2 = ActiveValidators::<Test>::get();
            assert_eq!(
                active, active2,
                "Epoch rotation must be deterministic"
            );
        });
    }

    #[test]
    fn test_session_returns_active_set() {
        new_test_ext().execute_with(|| {
            let session_result = Dpos::new_session(1);
            assert!(session_result.is_some(), "Session must return validator set");
            let validators = session_result.unwrap();
            assert_eq!(
                validators.len(),
                2,
                "Session must return active validators"
            );
        });
    }
"""

# Insert new tests before the last closing brace of the test module
# Find the last `}` in the file
last_brace = content.rfind('}')
assert last_brace > 0, "Could not find last brace"

# Insert before the final closing brace
content = content[:last_brace] + new_tests + "\n}" 
print("FIX 15: Added 9 regression tests")

# ============================================================
# Write the patched file
# ============================================================
with open(LIB_RS, 'w') as f:
    f.write(content)

print(f"\nAll 15 patches applied successfully!")
print(f"Original size: {len(original)} chars")
print(f"Patched size: {len(content)} chars")
print(f"Changes: {len(content) - len(original)} chars added")
