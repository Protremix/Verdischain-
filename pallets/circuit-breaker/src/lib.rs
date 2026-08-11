#![allow(clippy::let_unit_value)]
#![allow(deprecated)]
#![allow(clippy::incompatible_msrv)]
#![cfg_attr(not(feature = "std"), no_std)]
//! # Circuit Breaker Pallet
//!
//! Governance-controlled emergency pause for any pallet.
//! When a pallet is paused, the CallFilter blocks all its extrinsics.

use frame_support::pallet_prelude::*;
use frame_system::pallet_prelude::*;
use sp_std::prelude::*;

pub use pallet::*;

#[frame_support::pallet]
pub mod pallet {
    use super::*;

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        /// Max pallet name length
        type MaxPalletNameLen: Get<u32>;
    }

    /// Map of paused pallets. Key = pallet name (e.g. "Ibc", "AmmDex")
    #[pallet::storage]
    pub type PausedPallets<T: Config> =
        StorageMap<_, Blake2_128Concat, BoundedVec<u8, ConstU32<32>>, bool, ValueQuery>;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        PalletPaused { pallet_name: Vec<u8> },
        PalletUnpaused { pallet_name: Vec<u8> },
    }

    #[pallet::error]
    pub enum Error<T> {
        PalletNameTooLong,
        AlreadyPaused,
        NotPaused,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Pause a pallet (governance only). Blocks all extrinsics via CallFilter.
        #[pallet::call_index(0)]
        #[pallet::weight(Weight::from_parts(10_000, 0))]
        pub fn pause_pallet(origin: OriginFor<T>, pallet_name: Vec<u8>) -> DispatchResult {
            ensure_root(origin)?;

            let name_bv: BoundedVec<u8, ConstU32<32>> = pallet_name
                .clone()
                .try_into()
                .map_err(|_| Error::<T>::PalletNameTooLong)?;

            ensure!(
                !PausedPallets::<T>::get(&name_bv),
                Error::<T>::AlreadyPaused
            );
            PausedPallets::<T>::insert(&name_bv, true);

            Self::deposit_event(Event::PalletPaused { pallet_name });
            Ok(())
        }

        /// Unpause a pallet (governance only).
        #[pallet::call_index(1)]
        #[pallet::weight(Weight::from_parts(10_000, 0))]
        pub fn unpause_pallet(origin: OriginFor<T>, pallet_name: Vec<u8>) -> DispatchResult {
            ensure_root(origin)?;

            let name_bv: BoundedVec<u8, ConstU32<32>> = pallet_name
                .clone()
                .try_into()
                .map_err(|_| Error::<T>::PalletNameTooLong)?;

            ensure!(PausedPallets::<T>::get(&name_bv), Error::<T>::NotPaused);
            PausedPallets::<T>::remove(&name_bv);

            Self::deposit_event(Event::PalletUnpaused { pallet_name });
            Ok(())
        }
    }

    impl<T: Config> Pallet<T> {
        /// Check if a pallet is paused. Called by the CallFilter.
        pub fn is_paused(pallet_name: &[u8]) -> bool {
            let name_bv: BoundedVec<u8, ConstU32<32>> = match Vec::from(pallet_name).try_into() {
                Ok(bv) => bv,
                Err(_) => return false, // Name too long — can't be in the map
            };
            PausedPallets::<T>::get(&name_bv)
        }
    }
}

#[cfg(feature = "runtime-benchmarks")]
mod benchmarking;

#[cfg(test)]
mod tests {
    use super::*;
    use frame_support::{assert_noop, assert_ok, construct_runtime, derive_impl, parameter_types};
    use sp_io::TestExternalities;
    use sp_keyring::Sr25519Keyring;
    use sp_runtime::{traits::IdentityLookup, BuildStorage};

    type Block = frame_system::mocking::MockBlock<Test>;

    construct_runtime!(
        pub enum Test {
            System: frame_system,
            CircuitBreaker: crate,
        }
    );

    #[derive_impl(frame_system::config_preludes::TestDefaultConfig as frame_system::DefaultConfig)]
    impl frame_system::Config for Test {
        type AccountId = sp_core::crypto::AccountId32;
        type Lookup = IdentityLookup<Self::AccountId>;
        type Block = Block;
        type AccountData = ();
    }

    parameter_types! {
        pub const MaxPalletNameLen: u32 = 32;
    }

    impl Config for Test {
        type RuntimeEvent = RuntimeEvent;
        type MaxPalletNameLen = MaxPalletNameLen;
    }

    pub fn new_test_ext() -> TestExternalities {
        let t = frame_system::GenesisConfig::<Test>::default()
            .build_storage()
            .unwrap();
        let mut ext = TestExternalities::new(t);
        ext.execute_with(|| System::set_block_number(1));
        ext
    }

    #[test]
    fn test_pause_pallet_works() {
        new_test_ext().execute_with(|| {
            assert_ok!(CircuitBreaker::pause_pallet(
                RuntimeOrigin::root(),
                b"AmmDex".to_vec()
            ));
            assert!(CircuitBreaker::is_paused(b"AmmDex"));
        });
    }

    #[test]
    fn test_pause_pallet_non_root_rejected() {
        new_test_ext().execute_with(|| {
            assert_noop!(
                CircuitBreaker::pause_pallet(
                    RuntimeOrigin::signed(Sr25519Keyring::Alice.to_account_id()),
                    b"AmmDex".to_vec()
                ),
                sp_runtime::DispatchError::BadOrigin
            );
        });
    }

    #[test]
    fn test_pause_pallet_already_paused_rejected() {
        new_test_ext().execute_with(|| {
            assert_ok!(CircuitBreaker::pause_pallet(
                RuntimeOrigin::root(),
                b"AmmDex".to_vec()
            ));
            assert_noop!(
                CircuitBreaker::pause_pallet(RuntimeOrigin::root(), b"AmmDex".to_vec()),
                Error::<Test>::AlreadyPaused
            );
        });
    }

    #[test]
    fn test_pause_pallet_name_too_long_rejected() {
        new_test_ext().execute_with(|| {
            let long_name = vec![b'a'; 33];
            assert_noop!(
                CircuitBreaker::pause_pallet(RuntimeOrigin::root(), long_name),
                Error::<Test>::PalletNameTooLong
            );
        });
    }

    #[test]
    fn test_unpause_pallet_works() {
        new_test_ext().execute_with(|| {
            assert_ok!(CircuitBreaker::pause_pallet(
                RuntimeOrigin::root(),
                b"AmmDex".to_vec()
            ));
            assert!(CircuitBreaker::is_paused(b"AmmDex"));
            assert_ok!(CircuitBreaker::unpause_pallet(
                RuntimeOrigin::root(),
                b"AmmDex".to_vec()
            ));
            assert!(!CircuitBreaker::is_paused(b"AmmDex"));
        });
    }

    #[test]
    fn test_unpause_pallet_non_root_rejected() {
        new_test_ext().execute_with(|| {
            assert_ok!(CircuitBreaker::pause_pallet(
                RuntimeOrigin::root(),
                b"AmmDex".to_vec()
            ));
            assert_noop!(
                CircuitBreaker::unpause_pallet(
                    RuntimeOrigin::signed(Sr25519Keyring::Alice.to_account_id()),
                    b"AmmDex".to_vec()
                ),
                sp_runtime::DispatchError::BadOrigin
            );
        });
    }

    #[test]
    fn test_unpause_not_paused_rejected() {
        new_test_ext().execute_with(|| {
            assert_noop!(
                CircuitBreaker::unpause_pallet(RuntimeOrigin::root(), b"AmmDex".to_vec()),
                Error::<Test>::NotPaused
            );
        });
    }

    #[test]
    fn test_unpause_pallet_name_too_long_rejected() {
        new_test_ext().execute_with(|| {
            let long_name = vec![b'a'; 33];
            assert_noop!(
                CircuitBreaker::unpause_pallet(RuntimeOrigin::root(), long_name),
                Error::<Test>::PalletNameTooLong
            );
        });
    }

    #[test]
    fn test_is_paused_helper_returns_false_for_unpaused() {
        new_test_ext().execute_with(|| {
            assert!(!CircuitBreaker::is_paused(b"UnpausedPallet"));
        });
    }

    #[test]
    fn test_is_paused_helper_returns_true_after_pause() {
        new_test_ext().execute_with(|| {
            assert_ok!(CircuitBreaker::pause_pallet(
                RuntimeOrigin::root(),
                b"Ibc".to_vec()
            ));
            assert!(CircuitBreaker::is_paused(b"Ibc"));
        });
    }

    #[test]
    fn test_is_paused_helper_returns_false_for_long_name() {
        new_test_ext().execute_with(|| {
            let long_name = vec![b'a'; 33];
            assert!(!CircuitBreaker::is_paused(&long_name));
        });
    }

    #[test]
    fn test_pause_unpause_cycle() {
        new_test_ext().execute_with(|| {
            assert_ok!(CircuitBreaker::pause_pallet(
                RuntimeOrigin::root(),
                b"Dex".to_vec()
            ));
            assert!(CircuitBreaker::is_paused(b"Dex"));

            assert_ok!(CircuitBreaker::unpause_pallet(
                RuntimeOrigin::root(),
                b"Dex".to_vec()
            ));
            assert!(!CircuitBreaker::is_paused(b"Dex"));

            assert_ok!(CircuitBreaker::pause_pallet(
                RuntimeOrigin::root(),
                b"Dex".to_vec()
            ));
            assert!(CircuitBreaker::is_paused(b"Dex"));
        });
    }

    #[test]
    fn test_multiple_pallets_paused() {
        new_test_ext().execute_with(|| {
            assert_ok!(CircuitBreaker::pause_pallet(
                RuntimeOrigin::root(),
                b"PalletA".to_vec()
            ));
            assert_ok!(CircuitBreaker::pause_pallet(
                RuntimeOrigin::root(),
                b"PalletB".to_vec()
            ));
            assert!(CircuitBreaker::is_paused(b"PalletA"));
            assert!(CircuitBreaker::is_paused(b"PalletB"));

            assert_ok!(CircuitBreaker::unpause_pallet(
                RuntimeOrigin::root(),
                b"PalletA".to_vec()
            ));
            assert!(!CircuitBreaker::is_paused(b"PalletA"));
            assert!(CircuitBreaker::is_paused(b"PalletB"));
        });
    }

    #[test]
    fn test_pause_empty_name_works() {
        new_test_ext().execute_with(|| {
            assert_ok!(CircuitBreaker::pause_pallet(RuntimeOrigin::root(), vec![]));
            assert!(CircuitBreaker::is_paused(b""));
        });
    }

    #[test]
    fn test_unpause_empty_name_not_paused_rejected() {
        new_test_ext().execute_with(|| {
            assert_noop!(
                CircuitBreaker::unpause_pallet(RuntimeOrigin::root(), vec![]),
                Error::<Test>::NotPaused
            );
        });
    }
}
