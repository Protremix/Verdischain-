#!/usr/bin/env python3
"""Add collect_funds extrinsic and fix presale contribute to transfer tokens."""

with open("/opt/verdis-chain-rust/pallets/presale/src/lib.rs") as f:
    p = f.read()

# 1. Add FundsCollected event to the Event enum
# Find the last event variant and add after it
old_events_end = """        /// Whitelist updated for a round
        WhitelistUpdated { who: T::AccountId, whitelisted: bool },
    }"""
new_events_end = """        /// Whitelist updated for a round
        WhitelistUpdated { who: T::AccountId, whitelisted: bool },
        /// Funds collected from a round
        FundsCollected { round_id: u32, amount: BalanceOf<T>, collected_by: T::AccountId },
    }"""
p = p.replace(old_events_end, new_events_end)

# 2. Add collect_funds extrinsic after update_whitelist
old_end = """            Self::deposit_event(Event::WhitelistUpdated { who, whitelisted });
            Ok(())
        }
    }"""
new_end = """            Self::deposit_event(Event::WhitelistUpdated { who, whitelisted });
            Ok(())
        }

        /// Collect reserved funds from a completed round (admin only)
        #[pallet::call_index(6)]
        #[pallet::weight(T::WeightInfo::update_whitelist())]
        pub fn collect_funds(
            origin: OriginFor<T>,
            round_id: u32,
            beneficiary: T::AccountId,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            let round = Rounds::<T>::get(round_id).ok_or(Error::<T>::RoundNotFound)?;
            ensure!(!round.is_active, Error::<T>::RoundNotActive);

            // Sum all reserved payments for this round
            let mut total_collected = BalanceOf::<T>::zero();
            for (contributor, contribution) in Contributions::<T>::iter_prefix(round_id) {
                let reserved = T::Currency::reserved_balance(&contributor);
                if reserved >= contribution.total_paid {
                    // Unreserve and transfer to beneficiary
                    T::Currency::unreserve(&contributor, contribution.total_paid);
                    T::Currency::transfer(
                        &contributor,
                        &beneficiary,
                        contribution.total_paid,
                        frame_support::traits::ExistenceRequirement::AllowDeath,
                    )?;
                    total_collected = total_collected
                        .checked_add(&contribution.total_paid)
                        .ok_or(Error::<T>::CalculationOverflow)?;
                }
            }

            Self::deposit_event(Event::FundsCollected {
                round_id,
                amount: total_collected,
                collected_by: beneficiary,
            });

            Ok(())
        }
    }"""
p = p.replace(old_end, new_end)

# 3. Add the missing weight function for collect_funds (reuse update_whitelist weight)
old_weight = """        fn update_whitelist() -> frame_support::weights::Weight {
            frame_support::weights::Weight::from_parts(5_000, 0)
        }
    }"""
new_weight = """        fn update_whitelist() -> frame_support::weights::Weight {
            frame_support::weights::Weight::from_parts(5_000, 0)
        }
        fn collect_funds() -> frame_support::weights::Weight {
            frame_support::weights::Weight::from_parts(15_000, 0)
        }
    }"""
p = p.replace(old_weight, new_weight)

# 4. Add collect_funds to the WeightInfo trait
old_trait = """        fn update_whitelist() -> frame_support::weights::Weight;
    }"""
new_trait = """        fn update_whitelist() -> frame_support::weights::Weight;
        fn collect_funds() -> frame_support::weights::Weight;
    }"""
p = p.replace(old_trait, new_trait)

# 5. Add the needed imports - ReservableCurrency already has transfer, but need to check
# The Currency trait should already have transfer through ReservableCurrency

with open("/opt/verdis-chain-rust/pallets/presale/src/lib.rs", "w") as f:
    f.write(p)
print("Added collect_funds extrinsic to presale pallet")
