//! Benchmarking for the Verdis FungibleTokens pallet
#![cfg(feature = "runtime-benchmarks")]

use super::*;
use frame_benchmarking::v2::*;
use frame_support::traits::Currency;
use frame_system::RawOrigin;
use sp_runtime::traits::SaturatedConversion;
use sp_runtime::traits::Saturating;
use sp_std::vec;

use crate::Pallet as FungibleTokens;

fn setup_token<T: Config>(owner: &T::AccountId) -> u64 {
    let deposit = T::CreateTokenDeposit::get();
    let _ = T::Currency::deposit_creating(owner, deposit.saturating_mul(100u32.saturated_into()));
    let name = vec![b'A'; MAX_TOKEN_NAME as usize];
    let symbol = vec![b'S'; MAX_TOKEN_SYMBOL as usize];
    FungibleTokens::<T>::create(RawOrigin::Signed(owner.clone()).into(), name, symbol, 18)
        .expect("token creation failed");
    NextTokenId::<T>::get() - 1
}

#[benchmarks]
mod benches {
    use super::*;

    #[benchmark]
    fn create() {
        let caller: T::AccountId = whitelisted_caller();
        let deposit = T::CreateTokenDeposit::get();
        let _ =
            T::Currency::deposit_creating(&caller, deposit.saturating_mul(100u32.saturated_into()));
        let name = vec![b'A'; MAX_TOKEN_NAME as usize];
        let symbol = vec![b'S'; MAX_TOKEN_SYMBOL as usize];

        #[extrinsic_call]
        create(RawOrigin::Signed(caller), name, symbol, 18);

        assert_eq!(NextTokenId::<T>::get(), 1);
    }

    #[benchmark]
    fn mint() {
        let caller: T::AccountId = whitelisted_caller();
        let token_id = setup_token::<T>(&caller);
        let to: T::AccountId = account("recipient", 0, 0);
        let amount: u128 = 100_000;

        #[extrinsic_call]
        mint(RawOrigin::Signed(caller), token_id, to.clone(), amount);

        assert_eq!(FungibleTokens::<T>::balance_of(token_id, &to), amount);
    }

    #[benchmark]
    fn burn() {
        let caller: T::AccountId = whitelisted_caller();
        let token_id = setup_token::<T>(&caller);
        let amount: u128 = 100_000;

        let _ = FungibleTokens::<T>::mint(
            RawOrigin::Signed(caller.clone()).into(),
            token_id,
            caller.clone(),
            amount,
        );

        #[extrinsic_call]
        burn(RawOrigin::Signed(caller.clone()), token_id, amount);

        assert_eq!(FungibleTokens::<T>::balance_of(token_id, &caller), 0);
    }

    #[benchmark]
    fn transfer() {
        let caller: T::AccountId = whitelisted_caller();
        let token_id = setup_token::<T>(&caller);
        let to: T::AccountId = account("recipient", 0, 0);
        let amount: u128 = 100_000;

        let _ = FungibleTokens::<T>::mint(
            RawOrigin::Signed(caller.clone()).into(),
            token_id,
            caller.clone(),
            amount,
        );

        #[extrinsic_call]
        transfer(
            RawOrigin::Signed(caller.clone()),
            token_id,
            to.clone(),
            amount,
        );

        assert_eq!(FungibleTokens::<T>::balance_of(token_id, &to), amount);
    }

    #[benchmark]
    fn approve() {
        let caller: T::AccountId = whitelisted_caller();
        let token_id = setup_token::<T>(&caller);
        let spender: T::AccountId = account("spender", 0, 0);
        let amount: u128 = 100_000;

        #[extrinsic_call]
        approve(
            RawOrigin::Signed(caller.clone()),
            token_id,
            spender.clone(),
            amount,
        );

        assert_eq!(
            FungibleTokens::<T>::allowance(token_id, &caller, &spender),
            amount
        );
    }

    #[benchmark]
    fn transfer_from() {
        let caller: T::AccountId = whitelisted_caller();
        let owner: T::AccountId = account("owner", 0, 0);
        let to: T::AccountId = account("recipient", 0, 0);
        let token_id = setup_token::<T>(&owner);
        let amount: u128 = 100_000;

        let _ = FungibleTokens::<T>::mint(
            RawOrigin::Signed(owner.clone()).into(),
            token_id,
            owner.clone(),
            amount,
        );
        let _ = FungibleTokens::<T>::approve(
            RawOrigin::Signed(owner.clone()).into(),
            token_id,
            caller.clone(),
            amount,
        );

        #[extrinsic_call]
        transfer_from(
            RawOrigin::Signed(caller),
            token_id,
            owner,
            to.clone(),
            amount,
        );

        assert_eq!(FungibleTokens::<T>::balance_of(token_id, &to), amount);
    }

    #[benchmark]
    fn set_metadata(n: Linear<1, 128>) {
        let caller: T::AccountId = whitelisted_caller();
        let token_id = setup_token::<T>(&caller);
        let description = vec![b'D'; n as usize];
        let logo_uri = vec![b'L'; n as usize];

        #[extrinsic_call]
        set_metadata(RawOrigin::Signed(caller), token_id, description, logo_uri);

        assert!(TokenMetadataMap::<T>::contains_key(token_id));
    }

    #[benchmark]
    fn freeze() {
        let caller: T::AccountId = whitelisted_caller();
        let token_id = setup_token::<T>(&caller);

        #[extrinsic_call]
        freeze(RawOrigin::Signed(caller), token_id);

        let token = FungibleTokens::<T>::token_info(token_id).unwrap();
        assert!(token.is_frozen);
    }

    #[benchmark]
    fn thaw() {
        let caller: T::AccountId = whitelisted_caller();
        let token_id = setup_token::<T>(&caller);
        let _ = FungibleTokens::<T>::freeze(RawOrigin::Signed(caller.clone()).into(), token_id);

        #[extrinsic_call]
        thaw(RawOrigin::Signed(caller), token_id);

        let token = FungibleTokens::<T>::token_info(token_id).unwrap();
        assert!(!token.is_frozen);
    }

    #[benchmark]
    fn destroy() {
        let caller: T::AccountId = whitelisted_caller();
        let token_id = setup_token::<T>(&caller);

        #[extrinsic_call]
        destroy(RawOrigin::Signed(caller.clone()), token_id);

        assert!(FungibleTokens::<T>::token_info(token_id).is_none());
    }

    #[benchmark]
    fn batch_transfer(b: Linear<1, 100>) {
        let caller: T::AccountId = whitelisted_caller();
        let token_id = setup_token::<T>(&caller);
        let amount_per_recipient: u128 = 1_000;
        let total_amount = amount_per_recipient.saturating_mul(b as u128);

        let _ = FungibleTokens::<T>::mint(
            RawOrigin::Signed(caller.clone()).into(),
            token_id,
            caller.clone(),
            total_amount,
        );

        let mut recipients = Vec::with_capacity(b as usize);
        for i in 0..b {
            let recipient: T::AccountId = account("recipient", i, 0);
            recipients.push((recipient, amount_per_recipient));
        }

        #[extrinsic_call]
        batch_transfer(RawOrigin::Signed(caller), token_id, recipients);

        let last_recipient: T::AccountId = account("recipient", b - 1, 0);
        assert_eq!(
            FungibleTokens::<T>::balance_of(token_id, &last_recipient),
            amount_per_recipient
        );
    }

    #[benchmark]
    fn transfer_ownership() {
        let caller: T::AccountId = whitelisted_caller();
        let token_id = setup_token::<T>(&caller);
        let new_owner: T::AccountId = account("new_owner", 0, 0);

        #[extrinsic_call]
        transfer_ownership(RawOrigin::Signed(caller), token_id, new_owner.clone());

        let token = FungibleTokens::<T>::token_info(token_id).unwrap();
        assert_eq!(token.owner, new_owner);
    }

    impl_benchmark_test_suite!(
        FungibleTokens,
        crate::tests::new_test_ext(),
        crate::tests::Test,
    );
}
