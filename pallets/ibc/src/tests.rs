use crate::*;
use frame_support::{assert_ok, construct_runtime, derive_impl, parameter_types};
use sp_io::TestExternalities;
use sp_runtime::{traits::IdentityLookup, BuildStorage};

type Block = frame_system::mocking::MockBlock<Test>;

construct_runtime!(
    pub enum Test {
        System: frame_system,
        Ibc: crate,
    }
);

#[derive_impl(frame_system::config_preludes::TestDefaultConfig as frame_system::DefaultConfig)]
impl frame_system::Config for Test {
    type AccountId = sp_core::crypto::AccountId32;
    type Lookup = IdentityLookup<Self::AccountId>;
    type Block = Block;
}

parameter_types! {
    pub const IbcMaxPortIdLen: u32 = 128;
    pub const IbcMaxPacketDataLen: u32 = 1024;
}

impl Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type MaxPortIdLen = IbcMaxPortIdLen;
    type MaxPacketDataLen = IbcMaxPacketDataLen;
}

pub fn new_test_ext() -> TestExternalities {
    let t = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();
    TestExternalities::new(t)
}

#[test]
fn create_client_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::create_client(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
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
        let acct = sp_core::crypto::AccountId32::from([0xff; 32]);
        assert_ok!(Pallet::<Test>::create_client(
            frame_system::RawOrigin::Signed(acct.clone()).into(),
            1,
            100,
            86400
        ));
        assert_ok!(Pallet::<Test>::open_connection(
            frame_system::RawOrigin::Signed(acct.clone()).into(),
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
        let acct = sp_core::crypto::AccountId32::from([0xff; 32]);
        assert_ok!(Pallet::<Test>::create_client(
            frame_system::RawOrigin::Signed(acct.clone()).into(),
            1,
            100,
            86400
        ));
        assert_ok!(Pallet::<Test>::open_connection(
            frame_system::RawOrigin::Signed(acct.clone()).into(),
            0,
            1
        ));
        assert_ok!(Pallet::<Test>::open_channel(
            frame_system::RawOrigin::Signed(acct.clone()).into(),
            0,
            0,
            b"transfer".to_vec()
        ));
        assert_eq!(IbcChannelCounter::<Test>::get(), 1);
        assert!(Pallet::<Test>::is_channel_open(0));
    });
}

#[test]
fn send_packet_works() {
    new_test_ext().execute_with(|| {
        let acct = sp_core::crypto::AccountId32::from([0xff; 32]);
        // Setup: create client, connection, channel
        assert_ok!(Pallet::<Test>::create_client(
            frame_system::RawOrigin::Signed(acct.clone()).into(),
            1,
            100,
            86400
        ));
        assert_ok!(Pallet::<Test>::open_connection(
            frame_system::RawOrigin::Signed(acct.clone()).into(),
            0,
            1
        ));
        assert_ok!(Pallet::<Test>::open_channel(
            frame_system::RawOrigin::Signed(acct.clone()).into(),
            0,
            0,
            b"transfer".to_vec()
        ));
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
        // Setup chain
        assert_ok!(Pallet::<Test>::create_client(
            frame_system::RawOrigin::Signed(acct.clone()).into(),
            1,
            100,
            86400
        ));
        assert_ok!(Pallet::<Test>::open_connection(
            frame_system::RawOrigin::Signed(acct.clone()).into(),
            0,
            1
        ));
        assert_ok!(Pallet::<Test>::open_channel(
            frame_system::RawOrigin::Signed(acct.clone()).into(),
            0,
            0,
            b"transfer".to_vec()
        ));
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
        // Setup chain
        assert_ok!(Pallet::<Test>::create_client(
            frame_system::RawOrigin::Signed(acct.clone()).into(),
            1,
            100,
            86400
        ));
        assert_ok!(Pallet::<Test>::open_connection(
            frame_system::RawOrigin::Signed(acct.clone()).into(),
            0,
            1
        ));
        assert_ok!(Pallet::<Test>::open_channel(
            frame_system::RawOrigin::Signed(acct.clone()).into(),
            0,
            0,
            b"transfer".to_vec()
        ));
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
        let acct = sp_core::crypto::AccountId32::from([0xff; 32]);
        assert_ok!(Pallet::<Test>::create_client(
            frame_system::RawOrigin::Signed(acct.clone()).into(),
            1,
            100,
            86400
        ));
        assert_ok!(Pallet::<Test>::open_connection(
            frame_system::RawOrigin::Signed(acct.clone()).into(),
            0,
            1
        ));
        assert_ok!(Pallet::<Test>::open_channel(
            frame_system::RawOrigin::Signed(acct.clone()).into(),
            0,
            0,
            b"transfer".to_vec()
        ));
        assert!(Pallet::<Test>::is_channel_open(0));
        assert_ok!(Pallet::<Test>::close_channel(
            frame_system::RawOrigin::Root.into(),
            0
        ));
        assert!(!Pallet::<Test>::is_channel_open(0));
    });
}
