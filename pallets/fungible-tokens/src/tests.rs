#![allow(unused_imports, dead_code)]
//! Tests for the Verdis Fungible Tokens pallet

use crate::*;
use frame_support::{
    assert_noop, assert_ok, construct_runtime, derive_impl, parameter_types,
    traits::{ConstU128, ConstU32},
};
use sp_io::TestExternalities;
use sp_runtime::{traits::IdentityLookup, BuildStorage};

type Block = frame_system::mocking::MockBlock<Test>;

construct_runtime!(
    pub enum Test {
        System: frame_system,
        Balances: pallet_balances,
        FungibleTokens: crate,
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
    pub const FungibleTokensPalletId: PalletId = PalletId(*b"vrdfungs");
    pub const MaxTokensPerAccount: u32 = 100;
    pub const CreateTokenDeposit: u128 = 100;
    pub const FungibleMaxBalance: u128 = u128::MAX;
}

impl Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type Currency = Balances;
    type PalletId = FungibleTokensPalletId;
    type MaxTokensPerAccount = MaxTokensPerAccount;
    type CreateTokenDeposit = CreateTokenDeposit;
    type MaxBalance = FungibleMaxBalance;
    type WeightInfo = ();
}

pub fn new_test_ext() -> TestExternalities {
    let mut t = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();
    use sp_core::crypto::AccountId32;
    let alice: AccountId32 = sp_keyring::Sr25519Keyring::Alice.to_account_id();
    let bob: AccountId32 = sp_keyring::Sr25519Keyring::Bob.to_account_id();
    let charlie: AccountId32 = sp_keyring::Sr25519Keyring::Charlie.to_account_id();
    pallet_balances::GenesisConfig::<Test> {
        dev_accounts: Default::default(),
        balances: vec![
            (alice.clone(), 1_000_000_000_000),
            (bob.clone(), 1_000_000_000_000),
            (charlie.clone(), 1_000_000_000_000),
        ],
    }
    .assimilate_storage(&mut t)
    .unwrap();
    let mut ext = TestExternalities::new(t);
    ext.execute_with(|| System::set_block_number(1));
    ext
}

use sp_core::crypto::AccountId32;

fn alice() -> AccountId32 {
    sp_keyring::Sr25519Keyring::Alice.to_account_id()
}
fn bob() -> AccountId32 {
    sp_keyring::Sr25519Keyring::Bob.to_account_id()
}
fn charlie() -> AccountId32 {
    sp_keyring::Sr25519Keyring::Charlie.to_account_id()
}

#[test]
fn create_token_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"Verdis Carbon".to_vec(),
            b"VCARB".to_vec(),
            18,
        ));
        assert_eq!(NextTokenId::<Test>::get(), 1);
        let token = Tokens::<Test>::get(0).unwrap();
        assert_eq!(token.owner, alice());
        assert_eq!(token.name.as_slice(), b"Verdis Carbon");
        assert_eq!(token.symbol.as_slice(), b"VCARB");
        assert_eq!(token.decimals, 18);
        assert_eq!(token.total_supply, 0u128);
        assert!(!token.is_frozen);
        assert_eq!(TokensByOwner::<Test>::get(alice()).unwrap().len(), 1);
    });
}

#[test]
fn create_token_validations() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            FungibleTokens::create(RuntimeOrigin::signed(alice()), vec![], b"SYM".to_vec(), 18),
            Error::<Test>::EmptyName
        );
        assert_noop!(
            FungibleTokens::create(RuntimeOrigin::signed(alice()), b"Name".to_vec(), vec![], 18),
            Error::<Test>::EmptySymbol
        );
    });
}

#[test]
fn mint_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"Test Token".to_vec(),
            b"TST".to_vec(),
            6,
        ));
        assert_ok!(FungibleTokens::mint(
            RuntimeOrigin::signed(alice()),
            0,
            bob(),
            1000,
        ));
        assert_eq!(TokenBalances::<Test>::get(0, &bob()), 1000);
        assert_eq!(FungibleTokens::total_supply(0), Some(1000));
    });
}

#[test]
fn mint_non_owner_fails() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"Test".to_vec(),
            b"TST".to_vec(),
            6,
        ));
        assert_noop!(
            FungibleTokens::mint(RuntimeOrigin::signed(bob()), 0, charlie(), 1000),
            Error::<Test>::NotTokenOwner
        );
    });
}

#[test]
fn burn_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"Test".to_vec(),
            b"TST".to_vec(),
            6,
        ));
        assert_ok!(FungibleTokens::mint(
            RuntimeOrigin::signed(alice()),
            0,
            alice(),
            1000
        ));
        assert_ok!(FungibleTokens::burn(RuntimeOrigin::signed(alice()), 0, 500));
        assert_eq!(TokenBalances::<Test>::get(0, &alice()), 500);
        assert_eq!(FungibleTokens::total_supply(0), Some(500));
    });
}

#[test]
fn burn_insufficient_fails() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"Test".to_vec(),
            b"TST".to_vec(),
            6,
        ));
        assert_ok!(FungibleTokens::mint(
            RuntimeOrigin::signed(alice()),
            0,
            alice(),
            100
        ));
        assert_noop!(
            FungibleTokens::burn(RuntimeOrigin::signed(alice()), 0, 200),
            Error::<Test>::InsufficientBalance
        );
    });
}

#[test]
fn transfer_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"Test".to_vec(),
            b"TST".to_vec(),
            6,
        ));
        assert_ok!(FungibleTokens::mint(
            RuntimeOrigin::signed(alice()),
            0,
            alice(),
            1000
        ));
        assert_ok!(FungibleTokens::transfer(
            RuntimeOrigin::signed(alice()),
            0,
            bob(),
            400
        ));
        assert_eq!(TokenBalances::<Test>::get(0, &alice()), 600);
        assert_eq!(TokenBalances::<Test>::get(0, &bob()), 400);
        assert_eq!(FungibleTokens::total_supply(0), Some(1000));
    });
}

#[test]
fn transfer_insufficient_fails() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"Test".to_vec(),
            b"TST".to_vec(),
            6,
        ));
        assert_ok!(FungibleTokens::mint(
            RuntimeOrigin::signed(alice()),
            0,
            alice(),
            100
        ));
        assert_noop!(
            FungibleTokens::transfer(RuntimeOrigin::signed(alice()), 0, bob(), 200),
            Error::<Test>::InsufficientBalance
        );
    });
}

#[test]
fn approve_and_transfer_from_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"Test".to_vec(),
            b"TST".to_vec(),
            6,
        ));
        assert_ok!(FungibleTokens::mint(
            RuntimeOrigin::signed(alice()),
            0,
            alice(),
            1000
        ));

        assert_ok!(FungibleTokens::approve(
            RuntimeOrigin::signed(alice()),
            0,
            bob(),
            500
        ));
        assert_eq!(FungibleTokens::allowance(0, &alice(), &bob()), 500);

        assert_ok!(FungibleTokens::transfer_from(
            RuntimeOrigin::signed(bob()),
            0,
            alice(),
            charlie(),
            300
        ));
        assert_eq!(TokenBalances::<Test>::get(0, &alice()), 700);
        assert_eq!(TokenBalances::<Test>::get(0, &charlie()), 300);
        assert_eq!(FungibleTokens::allowance(0, &alice(), &bob()), 200);
    });
}

#[test]
fn transfer_from_exceeds_allowance_fails() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"Test".to_vec(),
            b"TST".to_vec(),
            6,
        ));
        assert_ok!(FungibleTokens::mint(
            RuntimeOrigin::signed(alice()),
            0,
            alice(),
            1000
        ));
        assert_ok!(FungibleTokens::approve(
            RuntimeOrigin::signed(alice()),
            0,
            bob(),
            500
        ));

        assert_noop!(
            FungibleTokens::transfer_from(RuntimeOrigin::signed(bob()), 0, alice(), charlie(), 600),
            Error::<Test>::InsufficientAllowance
        );
    });
}

#[test]
fn freeze_and_thaw_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"Test".to_vec(),
            b"TST".to_vec(),
            6,
        ));
        assert_ok!(FungibleTokens::mint(
            RuntimeOrigin::signed(alice()),
            0,
            alice(),
            1000
        ));

        assert_ok!(FungibleTokens::freeze(RuntimeOrigin::signed(alice()), 0));
        assert!(Tokens::<Test>::get(0).unwrap().is_frozen);

        assert_noop!(
            FungibleTokens::transfer(RuntimeOrigin::signed(alice()), 0, bob(), 100),
            Error::<Test>::TokenFrozen
        );

        assert_ok!(FungibleTokens::thaw(RuntimeOrigin::signed(alice()), 0));
        assert!(!Tokens::<Test>::get(0).unwrap().is_frozen);

        assert_ok!(FungibleTokens::transfer(
            RuntimeOrigin::signed(alice()),
            0,
            bob(),
            100
        ));
    });
}

#[test]
fn destroy_token_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"Test".to_vec(),
            b"TST".to_vec(),
            6,
        ));
        assert_ok!(FungibleTokens::mint(
            RuntimeOrigin::signed(alice()),
            0,
            alice(),
            100
        ));

        assert_noop!(
            FungibleTokens::destroy(RuntimeOrigin::signed(alice()), 0),
            Error::<Test>::TokenStillHasSupply
        );

        assert_ok!(FungibleTokens::burn(RuntimeOrigin::signed(alice()), 0, 100));
        assert_ok!(FungibleTokens::destroy(RuntimeOrigin::signed(alice()), 0));
        assert!(Tokens::<Test>::get(0).is_none());
    });
}

#[test]
fn set_metadata_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"Test".to_vec(),
            b"TST".to_vec(),
            6,
        ));
        assert_ok!(FungibleTokens::set_metadata(
            RuntimeOrigin::signed(alice()),
            0,
            b"Carbon credit token".to_vec(),
            b"https://verdischain.com/logo.png".to_vec(),
        ));
        let meta = TokenMetadataMap::<Test>::get(0).unwrap();
        assert_eq!(meta.description.as_slice(), b"Carbon credit token");
    });
}

#[test]
fn multiple_tokens_created() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"Token A".to_vec(),
            b"TKA".to_vec(),
            6
        ));
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"Token B".to_vec(),
            b"TKB".to_vec(),
            18
        ));
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(bob()),
            b"Token C".to_vec(),
            b"TKC".to_vec(),
            8
        ));

        assert_eq!(NextTokenId::<Test>::get(), 3);
        assert_eq!(TokensByOwner::<Test>::get(alice()).unwrap().len(), 2);
        assert_eq!(TokensByOwner::<Test>::get(bob()).unwrap().len(), 1);

        assert_ok!(FungibleTokens::mint(
            RuntimeOrigin::signed(alice()),
            0,
            alice(),
            100
        ));
        assert_ok!(FungibleTokens::mint(
            RuntimeOrigin::signed(alice()),
            1,
            bob(),
            200
        ));
        assert_ok!(FungibleTokens::mint(
            RuntimeOrigin::signed(bob()),
            2,
            charlie(),
            300
        ));

        assert_eq!(FungibleTokens::total_supply(0), Some(100));
        assert_eq!(FungibleTokens::total_supply(1), Some(200));
        assert_eq!(FungibleTokens::total_supply(2), Some(300));
    });
}

#[test]
fn zero_amount_fails() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"Test".to_vec(),
            b"TST".to_vec(),
            6,
        ));
        assert_noop!(
            FungibleTokens::mint(RuntimeOrigin::signed(alice()), 0, bob(), 0),
            Error::<Test>::ZeroAmount
        );
    });
}

#[test]
fn overflow_protection() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"Test".to_vec(),
            b"TST".to_vec(),
            6,
        ));
        assert_ok!(FungibleTokens::mint(
            RuntimeOrigin::signed(alice()),
            0,
            alice(),
            u128::MAX
        ));
        assert_noop!(
            FungibleTokens::mint(RuntimeOrigin::signed(alice()), 0, alice(), 1),
            Error::<Test>::Overflow
        );
    });
}

#[test]
fn token_not_found_fails() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            FungibleTokens::mint(RuntimeOrigin::signed(alice()), 999, bob(), 100),
            Error::<Test>::TokenNotFound
        );
    });
}

#[test]
fn batch_transfer_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"Test".to_vec(),
            b"TST".to_vec(),
            6,
        ));
        assert_ok!(FungibleTokens::mint(
            RuntimeOrigin::signed(alice()),
            0,
            alice(),
            1000
        ));

        assert_ok!(FungibleTokens::batch_transfer(
            RuntimeOrigin::signed(alice()),
            0,
            vec![(bob(), 300), (charlie(), 200)],
        ));
        assert_eq!(TokenBalances::<Test>::get(0, &alice()), 500);
        assert_eq!(TokenBalances::<Test>::get(0, &bob()), 300);
        assert_eq!(TokenBalances::<Test>::get(0, &charlie()), 200);
        assert_eq!(FungibleTokens::total_supply(0), Some(1000));
    });
}

#[test]
fn batch_transfer_insufficient_fails() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"Test".to_vec(),
            b"TST".to_vec(),
            6,
        ));
        assert_ok!(FungibleTokens::mint(
            RuntimeOrigin::signed(alice()),
            0,
            alice(),
            500
        ));

        assert_noop!(
            FungibleTokens::batch_transfer(
                RuntimeOrigin::signed(alice()),
                0,
                vec![(bob(), 300), (charlie(), 300)],
            ),
            Error::<Test>::InsufficientBalance
        );
    });
}

#[test]
fn transfer_ownership_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"Test".to_vec(),
            b"TST".to_vec(),
            6,
        ));

        // Transfer ownership to bob
        assert_ok!(FungibleTokens::transfer_ownership(
            RuntimeOrigin::signed(alice()),
            0,
            bob(),
        ));

        let token = Tokens::<Test>::get(0).unwrap();
        assert_eq!(token.owner, bob());
        assert!(TokensByOwner::<Test>::get(alice()).is_none());
        assert_eq!(TokensByOwner::<Test>::get(bob()).unwrap().len(), 1);

        // Bob can now mint, alice cannot
        assert_ok!(FungibleTokens::mint(
            RuntimeOrigin::signed(bob()),
            0,
            charlie(),
            100
        ));
        assert_noop!(
            FungibleTokens::mint(RuntimeOrigin::signed(alice()), 0, charlie(), 100),
            Error::<Test>::NotTokenOwner
        );
    });
}

#[test]
fn transfer_ownership_non_owner_fails() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"Test".to_vec(),
            b"TST".to_vec(),
            6,
        ));
        assert_noop!(
            FungibleTokens::transfer_ownership(RuntimeOrigin::signed(bob()), 0, charlie()),
            Error::<Test>::NotTokenOwner
        );
    });
}

#[test]
fn set_max_supply_decrease_succeeds() {
    new_test_ext().execute_with(|| {
        // Create token with max_supply via mint
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"TestToken".to_vec(),
            b"TST".to_vec(),
            6,
        ));
        // Check what max_supply was set
        let token = FungibleTokens::token_info(0).unwrap();
        let original_max = token.max_supply;
        // Mint some tokens
        assert_ok!(FungibleTokens::mint(
            RuntimeOrigin::signed(alice()),
            0,
            alice(),
            100,
        ));
        // Decrease max_supply to a value >= total_supply but < original
        let new_max = 200u128.min(original_max);
        if original_max > 200 {
            assert_ok!(FungibleTokens::set_max_supply(
                RuntimeOrigin::signed(alice()),
                0,
                new_max,
            ));
            let updated = FungibleTokens::token_info(0).unwrap();
            assert_eq!(updated.max_supply, new_max);
        }
    });
}

#[test]
fn set_max_supply_increase_fails() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"FixedSupply".to_vec(),
            b"FIX".to_vec(),
            6,
        ));
        // Default max is u128::MAX. First decrease to 1000.
        assert_ok!(FungibleTokens::set_max_supply(
            RuntimeOrigin::signed(alice()),
            0,
            1000,
        ));
        // Now try to increase back to 2000 - should fail
        assert_noop!(
            FungibleTokens::set_max_supply(RuntimeOrigin::signed(alice()), 0, 2000,),
            Error::<Test>::MaxSupplyCannotIncrease
        );
        // Verify it stayed at 1000
        let token = FungibleTokens::token_info(0).unwrap();
        assert_eq!(token.max_supply, 1000);
    });
}

#[test]
fn set_max_supply_below_total_supply_fails() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"TestToken2".to_vec(),
            b"TST2".to_vec(),
            6,
        ));
        // Mint some tokens
        assert_ok!(FungibleTokens::mint(
            RuntimeOrigin::signed(alice()),
            0,
            alice(),
            500,
        ));
        // Try to set max_supply below total_supply - should fail
        assert_noop!(
            FungibleTokens::set_max_supply(RuntimeOrigin::signed(alice()), 0, 499,),
            Error::<Test>::MaxBalanceExceeded
        );
    });
}

#[test]
fn set_max_supply_non_owner_fails() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"TestToken3".to_vec(),
            b"TST3".to_vec(),
            6,
        ));
        let token = FungibleTokens::token_info(0).unwrap();
        let target = token.max_supply / 2;
        assert_noop!(
            FungibleTokens::set_max_supply(RuntimeOrigin::signed(bob()), 0, target,),
            Error::<Test>::NotTokenOwner
        );
    });
}

#[test]
fn mint_at_max_supply_succeeds() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"MaxTest".to_vec(),
            b"MAXT".to_vec(),
            6,
        ));
        // Set max_supply to 1000
        assert_ok!(FungibleTokens::set_max_supply(
            RuntimeOrigin::signed(alice()),
            0,
            1000,
        ));
        // Mint exactly to max_supply — should succeed
        assert_ok!(FungibleTokens::mint(
            RuntimeOrigin::signed(alice()),
            0,
            alice(),
            1000,
        ));
        let token = FungibleTokens::token_info(0).unwrap();
        assert_eq!(token.total_supply, 1000);
        assert_eq!(token.max_supply, 1000);
    });
}

#[test]
fn mint_above_max_supply_fails() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"MaxTest2".to_vec(),
            b"MAX2".to_vec(),
            6,
        ));
        // Set max_supply to 1000
        assert_ok!(FungibleTokens::set_max_supply(
            RuntimeOrigin::signed(alice()),
            0,
            1000,
        ));
        // Mint 1000 — succeeds
        assert_ok!(FungibleTokens::mint(
            RuntimeOrigin::signed(alice()),
            0,
            alice(),
            1000,
        ));
        // Try to mint 1 more above max_supply — should fail
        assert_noop!(
            FungibleTokens::mint(RuntimeOrigin::signed(alice()), 0, alice(), 1,),
            Error::<Test>::MaxBalanceExceeded
        );
        // Verify supply didn't change
        let token = FungibleTokens::token_info(0).unwrap();
        assert_eq!(token.total_supply, 1000);
    });
}

// === Missing tests: overflow and ratchet ===

#[test]
fn mint_u128_overflow_fails() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"Overflow".to_vec(),
            b"OVR".to_vec(),
            6,
        ));
        assert_ok!(FungibleTokens::set_max_supply(
            RuntimeOrigin::signed(alice()),
            0,
            u128::MAX,
        ));
        assert_ok!(FungibleTokens::mint(
            RuntimeOrigin::signed(alice()),
            0,
            alice(),
            u128::MAX - 1,
        ));
        assert_noop!(
            FungibleTokens::mint(RuntimeOrigin::signed(alice()), 0, alice(), 2),
            Error::<Test>::Overflow
        );
    });
}

#[test]
fn set_max_supply_cannot_increase_ratchet() {
    new_test_ext().execute_with(|| {
        assert_ok!(FungibleTokens::create(
            RuntimeOrigin::signed(alice()),
            b"Ratchet".to_vec(),
            b"RCH".to_vec(),
            6,
        ));
        assert_ok!(FungibleTokens::set_max_supply(
            RuntimeOrigin::signed(alice()),
            0,
            1000,
        ));
        assert_noop!(
            FungibleTokens::set_max_supply(RuntimeOrigin::signed(alice()), 0, 2000),
            Error::<Test>::MaxSupplyCannotIncrease
        );
    });
}
