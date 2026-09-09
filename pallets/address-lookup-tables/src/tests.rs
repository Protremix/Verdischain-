use crate::*;
use frame_support::{assert_ok, construct_runtime, derive_impl, parameter_types};
use sp_io::TestExternalities;
use sp_runtime::{traits::IdentityLookup, BuildStorage};

type Block = frame_system::mocking::MockBlock<Test>;

construct_runtime!(
    pub enum Test {
        System: frame_system,
        AddressLookupTables: crate,
    }
);

#[derive_impl(frame_system::config_preludes::TestDefaultConfig as frame_system::DefaultConfig)]
impl frame_system::Config for Test {
    type AccountId = sp_core::crypto::AccountId32;
    type Lookup = IdentityLookup<Self::AccountId>;
    type Block = Block;
}

parameter_types! {
    pub const MaxAddressesPerTable: u32 = 256;
    pub const MaxTablesPerAccount: u32 = 16;
}

impl Config for Test {
    type MaxAddressesPerTable = MaxAddressesPerTable;
    type MaxTablesPerAccount = MaxTablesPerAccount;
    type WeightInfo = crate::SubstrateWeight<Test>;
}

pub fn new_test_ext() -> TestExternalities {
    let t = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();
    TestExternalities::new(t)
}

#[test]
fn create_table_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::create_table(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into()
        ));
        assert_eq!(AltTotalTables::<Test>::get(), 1);
    });
}

#[test]
fn add_address_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::create_table(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into()
        ));
        assert_ok!(Pallet::<Test>::add_address(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            0
        ));
        assert_eq!(AltTotalAddresses::<Test>::get(), 1);
    });
}

#[test]
fn deactivate_table_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::create_table(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into()
        ));
        assert_ok!(Pallet::<Test>::deactivate_table(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            0
        ));
        assert!(!TableActive::<Test>::get(0));
    });
}

#[test]
fn add_to_inactive_table_fails() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::create_table(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into()
        ));
        assert_ok!(Pallet::<Test>::deactivate_table(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            0
        ));
        assert!(Pallet::<Test>::add_address(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            0
        )
        .is_err());
    });
}
