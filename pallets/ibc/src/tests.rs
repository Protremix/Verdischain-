use crate::*;
use frame_support::{
    assert_ok, construct_runtime, derive_impl, parameter_types,
    traits::{ConstU128, ConstU32},
};

use sp_io::TestExternalities;
use sp_runtime::{traits::IdentityLookup, BuildStorage};

type Block = frame_system::mocking::MockBlock<Test>;

construct_runtime!(
    pub enum Test {
        System: frame_system,
        Balances: pallet_balances,
        Ibc: crate,
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
    pub const IbcMaxPortIdLen: u32 = 128;
    pub const IbcMaxPacketDataLen: u32 = 1024;
    pub const IbcMaxTransferAmount: u128 = 1_000_000_000_000_000;
    pub const IbcMaxHeightJump: u64 = 1_000_000;
}

impl Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type MaxPortIdLen = IbcMaxPortIdLen;
    type MaxPacketDataLen = IbcMaxPacketDataLen;
    type Currency = Balances;
    type MaxTransferAmount = IbcMaxTransferAmount;
        type MaxHeightJump = IbcMaxHeightJump;
}

pub fn new_test_ext() -> TestExternalities {
    let t = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();
    TestExternalities::new(t)
}

/// Helper: set up a full IBC chain (client + connection + channel)
fn setup_chain() {
    use frame_system::RawOrigin;
    assert_ok!(Pallet::<Test>::create_client(
        RawOrigin::Root.into(),
        1,
        100,
        86400
    ));
    assert_ok!(Pallet::<Test>::open_connection(
        RawOrigin::Root.into(),
        0,
        1
    ));
    assert_ok!(Pallet::<Test>::open_channel(
        RawOrigin::Root.into(),
        0,
        0,
        b"transfer".to_vec()
    ));
}

#[test]
fn create_client_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::create_client(
            frame_system::RawOrigin::Root.into(),
            1,
            100,
            86400
        ));
        assert_eq!(IbcClientCounter::<Test>::get(), 1);
        assert!(IbcClients::<Test>::get(0).is_some());
    });
}

#[test]
fn open_connection_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::create_client(
            frame_system::RawOrigin::Root.into(),
            1,
            100,
            86400
        ));
        assert_ok!(Pallet::<Test>::open_connection(
            frame_system::RawOrigin::Root.into(),
            0,
            1
        ));
        assert_eq!(IbcConnectionCounter::<Test>::get(), 1);
        assert!(IbcConnections::<Test>::get(0).is_some());
    });
}

#[test]
fn open_channel_works() {
    new_test_ext().execute_with(|| {
        setup_chain();
        assert_eq!(IbcChannelCounter::<Test>::get(), 1);
        assert!(Pallet::<Test>::is_channel_open(0));
    });
}

#[test]
fn send_packet_works() {
    new_test_ext().execute_with(|| {
        let acct = sp_core::crypto::AccountId32::from([0xff; 32]);
        setup_chain();
        // Send packet
        assert_ok!(Pallet::<Test>::send_packet(
            frame_system::RawOrigin::Signed(acct.clone()).into(),
            0,
            b"transfer".to_vec(),
            b"transfer".to_vec(),
            vec![1, 2, 3],
            10000
        ));
        assert_eq!(IbcNextSequenceSend::<Test>::get(0), 2);
        assert!(IbcPackets::<Test>::get((0, 1)).is_some());
    });
}

#[test]
fn recv_packet_works() {
    new_test_ext().execute_with(|| {
        let acct = sp_core::crypto::AccountId32::from([0xff; 32]);
        setup_chain();
        // Send then receive
        assert_ok!(Pallet::<Test>::send_packet(
            frame_system::RawOrigin::Signed(acct.clone()).into(),
            0,
            b"transfer".to_vec(),
            b"transfer".to_vec(),
            vec![1, 2, 3],
            10000
        ));
        assert_ok!(Pallet::<Test>::recv_packet(
            frame_system::RawOrigin::Signed(acct.clone()).into(),
            0,
            1,
            b"transfer".to_vec(),
            vec![1, 2, 3]
        ));
        assert_eq!(IbcNextSequenceRecv::<Test>::get(0), 2);
    });
}

#[test]
fn transfer_works() {
    new_test_ext().execute_with(|| {
        let acct = sp_core::crypto::AccountId32::from([0xff; 32]);
        setup_chain();
        // Fund account for escrow
        use frame_support::traits::fungible::Mutate;
        pallet_balances::Pallet::<Test>::mint_into(&acct, 1_000_000_000_000_000_000).unwrap();

        // Transfer
        assert_ok!(Pallet::<Test>::transfer(
            frame_system::RawOrigin::Signed(acct.clone()).into(),
            0,
            vec![0xaa; 32],
            1000000,
            b"VRDX".to_vec()
        ));
        assert_eq!(IbcTotalTransfers::<Test>::get(), 1);
        assert_eq!(IbcTotalVolume::<Test>::get(), 1000000);
    });
}

#[test]
fn close_channel_works() {
    new_test_ext().execute_with(|| {
        setup_chain();
        assert!(Pallet::<Test>::is_channel_open(0));
        assert_ok!(Pallet::<Test>::close_channel(
            frame_system::RawOrigin::Root.into(),
            0
        ));
        assert!(!Pallet::<Test>::is_channel_open(0));
    });
}

#[test]
fn update_client_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::create_client(
            frame_system::RawOrigin::Root.into(),
            1,
            100,
            86400
        ));
        // Update height forward
        assert_ok!(Pallet::<Test>::update_client(
            frame_system::RawOrigin::Root.into(),
            0,
            200
        ));
        assert_eq!(IbcClients::<Test>::get(0).unwrap().latest_height, 200);
    });
}

#[test]
fn freeze_client_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::create_client(
            frame_system::RawOrigin::Root.into(),
            1,
            100,
            86400
        ));
        assert_ok!(Pallet::<Test>::freeze_client(
            frame_system::RawOrigin::Root.into(),
            0
        ));
        assert!(IbcClients::<Test>::get(0).unwrap().frozen);
    });
}

#[test]
fn transfer_fails_on_frozen_client() {
    new_test_ext().execute_with(|| {
        let acct = sp_core::crypto::AccountId32::from([0xff; 32]);
        setup_chain();
        // Freeze the client
        assert_ok!(Pallet::<Test>::freeze_client(
            frame_system::RawOrigin::Root.into(),
            0
        ));
        // Fund account
        use frame_support::traits::fungible::Mutate;
        pallet_balances::Pallet::<Test>::mint_into(&acct, 1_000_000_000_000_000_000).unwrap();
        // Transfer should fail with ClientFrozen
        let result = Pallet::<Test>::transfer(
            frame_system::RawOrigin::Signed(acct).into(),
            0,
            vec![0xaa; 32],
            1000000,
            b"VRDX".to_vec()
        );
        assert!(result.is_err());
    });
}

#[test]
fn timeout_packet_works() {
    new_test_ext().execute_with(|| {
        let acct = sp_core::crypto::AccountId32::from([0xff; 32]);
        setup_chain();
        // Fund and transfer
        use frame_support::traits::fungible::Mutate;
        pallet_balances::Pallet::<Test>::mint_into(&acct, 1_000_000_000_000_000_000).unwrap();
        assert_ok!(Pallet::<Test>::transfer(
            frame_system::RawOrigin::Signed(acct.clone()).into(),
            0,
            vec![0xaa; 32],
            1000000,
            b"VRDX".to_vec()
        ));
        // Move block forward past timeout
        frame_system::Pallet::<Test>::set_block_number(2000);
        // Timeout the packet (sequence 1)
        assert_ok!(Pallet::<Test>::timeout_packet(
            frame_system::RawOrigin::Signed(acct).into(),
            0,
            1
        ));
        assert!(IbcPackets::<Test>::get((0, 1)).is_none());
    });
}
