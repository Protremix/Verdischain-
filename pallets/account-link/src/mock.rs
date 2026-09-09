//! Test runtime for `pallet-verdis-account-link`.
//!
//! Deliberately mirrors Verdis's real configuration where it matters: `AccountId32`, an existential
//! deposit of 1 VRDX at 9 decimals, and EVM chain id 414. A mock with different values would let a
//! bug through - for instance the AST-1 reaping case only shows up when the existential deposit is
//! non-zero.

use frame_support::{
    derive_impl, parameter_types,
    traits::{ConstU32, ConstU64},
};
use sp_runtime::{traits::IdentityLookup, AccountId32, BuildStorage};

use crate as pallet_account_link;

type Block = frame_system::mocking::MockBlock<Test>;
pub type Balance = u128;

/// 9 decimals, as on Verdis. Not 18: the difference is what makes the deposit and existential
/// deposit numbers realistic.
pub const VRDX: Balance = 1_000_000_000;

/// Verdis mainnet's existential deposit.
pub const EXISTENTIAL_DEPOSIT: Balance = 1 * VRDX;

/// Verdis's EVM chain id. 909 is taken by Portal Fantasy Chain in chainid.network, so signatures are
/// domain-separated on 414 - a signature made for another chain id will not verify here.
pub const CHAIN_ID: u64 = 414;

frame_support::construct_runtime!(
    pub enum Test {
        System: frame_system,
        Balances: pallet_balances,
        AccountLink: pallet_account_link,
    }
);

#[derive_impl(frame_system::config_preludes::TestDefaultConfig)]
impl frame_system::Config for Test {
    type Block = Block;
    type AccountId = AccountId32;
    type Lookup = IdentityLookup<Self::AccountId>;
    type AccountData = pallet_balances::AccountData<Balance>;
}

#[derive_impl(pallet_balances::config_preludes::TestDefaultConfig)]
impl pallet_balances::Config for Test {
    type Balance = Balance;
    type ExistentialDeposit = ConstU128<EXISTENTIAL_DEPOSIT>;
    type AccountStore = System;
}

parameter_types! {
    /// Deposit for one mapping. Two storage maps plus a nonce entry.
    pub const LinkDeposit: Balance = 1 * VRDX;
}

/// Rejects accounts that must not be captured by a single Ethereum key.
///
/// This is the runtime-side answer to Quantstamp finding AST-2 against Astar's pallet: binding a
/// multisig or a contract account to one EOA would give that key sole control of an account whose
/// purpose is shared control. In the mock, any account whose first byte is 0xFF stands in for such an
/// account so the rejection path is exercised.
pub struct RejectSpecialAccounts;
impl pallet_account_link::LinkFilter<AccountId32> for RejectSpecialAccounts {
    fn allowed(who: &AccountId32) -> bool {
        let bytes: &[u8; 32] = who.as_ref();
        bytes[0] != 0xFF
    }
}

impl pallet_account_link::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type Currency = Balances;
    type LinkDeposit = LinkDeposit;
    type ChainId = ConstU64<CHAIN_ID>;
    type AllowedToLink = RejectSpecialAccounts;
    type WeightInfo = ();
}

use frame_support::traits::ConstU128;

pub fn account(seed: u8) -> AccountId32 {
    AccountId32::new([seed; 32])
}

/// An account the filter rejects, standing in for a multisig or contract account.
pub fn special_account() -> AccountId32 {
    let mut bytes = [7u8; 32];
    bytes[0] = 0xFF;
    AccountId32::new(bytes)
}

pub fn new_test_ext() -> sp_io::TestExternalities {
    let mut t = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();

    pallet_balances::GenesisConfig::<Test> {
        balances: vec![
            (account(1), 1_000 * VRDX),
            (account(2), 1_000 * VRDX),
            (special_account(), 1_000 * VRDX),
            // Deliberately just above the existential deposit: paying the link deposit from here
            // would reap the account, which is what AST-1 was about.
            (account(3), EXISTENTIAL_DEPOSIT + LinkDeposit::get() - 1),
        ],
        ..Default::default()
    }
    .assimilate_storage(&mut t)
    .unwrap();

    let mut ext = sp_io::TestExternalities::new(t);
    ext.execute_with(|| System::set_block_number(1));
    ext
}
