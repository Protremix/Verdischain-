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

            let name_bv: BoundedVec<u8, ConstU32<32>> =
                Vec::from(pallet_name.clone()).try_into().map_err(|_| Error::<T>::PalletNameTooLong)?;

            ensure!(!PausedPallets::<T>::get(&name_bv), Error::<T>::AlreadyPaused);
            PausedPallets::<T>::insert(&name_bv, true);

            Self::deposit_event(Event::PalletPaused { pallet_name });
            Ok(())
        }

        /// Unpause a pallet (governance only).
        #[pallet::call_index(1)]
        #[pallet::weight(Weight::from_parts(10_000, 0))]
        pub fn unpause_pallet(origin: OriginFor<T>, pallet_name: Vec<u8>) -> DispatchResult {
            ensure_root(origin)?;

            let name_bv: BoundedVec<u8, ConstU32<32>> =
                Vec::from(pallet_name.clone()).try_into().map_err(|_| Error::<T>::PalletNameTooLong)?;

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
