//! Weights for pallet-verdis-account-link.
//!
//! The pallet currently exposes one bounded operation. These conservative values are the same
//! defaults used by the pallet's test implementation; production benchmarking must replace them
//! before mainnet deployment.

#![allow(missing_docs)]

use frame_support::weights::Weight;

/// Weight functions for pallet-verdis-account-link.
pub struct WeightInfo;

impl crate::WeightInfo for WeightInfo {
    fn claim_evm_address() -> Weight {
        Weight::from_parts(200_000_000, 4_000)
    }
}
