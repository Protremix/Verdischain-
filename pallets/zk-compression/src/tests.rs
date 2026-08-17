use crate::*;
use frame_support::{assert_noop, assert_ok, construct_runtime, derive_impl, parameter_types};
use sp_io::TestExternalities;
use sp_runtime::{traits::IdentityLookup, BuildStorage, DispatchError};

type Block = frame_system::mocking::MockBlock<Test>;

construct_runtime!(
    pub enum Test {
        System: frame_system,
        ZkCompression: crate,
    }
);

#[derive_impl(frame_system::config_preludes::TestDefaultConfig as frame_system::DefaultConfig)]
impl frame_system::Config for Test {
    type AccountId = sp_core::crypto::AccountId32;
    type Lookup = IdentityLookup<Self::AccountId>;
    type Block = Block;
}

parameter_types! {
    pub const MaxLeaves: u32 = 1024;
    pub const MaxDepth: u32 = 20;
}

impl Config for Test {
    type MaxLeaves = MaxLeaves;
    type MaxDepth = MaxDepth;
    type WeightInfo = crate::SubstrateWeight<Test>;
}

pub fn new_test_ext() -> TestExternalities {
    let t = frame_system::GenesisConfig::<Test>::default()
        .build_storage()
        .unwrap();
    TestExternalities::new(t)
}

#[test]
fn create_tree_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::create_tree(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            10
        ));
        assert_eq!(ZkTotalTrees::<Test>::get(), 1);
    });
}

#[test]
fn compress_account_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::create_tree(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            10
        ));
        assert_ok!(Pallet::<Test>::compress_account(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            0,
            256
        ));
        assert_eq!(ZkTotalCompressed::<Test>::get(), 1);
    });
}

#[test]
fn verify_proof_works() {
    new_test_ext().execute_with(|| {
        // Must create a tree first so MerkleRoots[0] exists
        assert_ok!(Pallet::<Test>::create_tree(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            10
        ));
        assert_ok!(Pallet::<Test>::verify_proof(
            frame_system::RawOrigin::Root.into(),
            0,
            0,
            [0u8; 32]
        ));
    });
}

#[test]
fn max_depth_exceeded() {
    new_test_ext().execute_with(|| {
        assert!(Pallet::<Test>::create_tree(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            999
        )
        .is_err());
    });
}

#[test]
fn create_tree_max_depth_exceeded_rejected() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Pallet::<Test>::create_tree(
                frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32]))
                    .into(),
                21
            ),
            Error::<Test>::MaxDepthExceeded
        );
    });
}

#[test]
fn create_tree_unsigned_rejected() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Pallet::<Test>::create_tree(frame_system::RawOrigin::None.into(), 10),
            DispatchError::BadOrigin
        );
    });
}

#[test]
fn compress_account_nonexistent_tree_works() {
    new_test_ext().execute_with(|| {
        assert_ok!(Pallet::<Test>::compress_account(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            999,
            256
        ));
        assert_eq!(ZkTotalCompressed::<Test>::get(), 1);
    });
}

#[test]
fn compress_account_unsigned_rejected() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Pallet::<Test>::compress_account(frame_system::RawOrigin::None.into(), 0, 256),
            DispatchError::BadOrigin
        );
    });
}

#[test]
fn verify_proof_non_root_rejected() {
    new_test_ext().execute_with(|| {
        assert_noop!(
            Pallet::<Test>::verify_proof(
                frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32]))
                    .into(),
                0,
                0,
                [0u8; 32]
            ),
            DispatchError::BadOrigin
        );
    });
}

#[test]
fn verify_proof_root_works() {
    new_test_ext().execute_with(|| {
        System::set_block_number(1);
        // Must create a tree first so MerkleRoots[0] exists
        assert_ok!(Pallet::<Test>::create_tree(
            frame_system::RawOrigin::Signed(sp_core::crypto::AccountId32::from([0xff; 32])).into(),
            10
        ));
        // Get the actual root from the TreeCreated event
        let root = crate::MerkleRoots::<Test>::get(0).unwrap();
        assert_ok!(Pallet::<Test>::verify_proof(
            frame_system::RawOrigin::Root.into(),
            0,
            0,
            root
        ));
        System::assert_has_event(RuntimeEvent::ZkCompression(crate::Event::ProofVerified {
            tree_id: 0,
            leaf_index: 0,
            verified: true,
        }));
    });
}
