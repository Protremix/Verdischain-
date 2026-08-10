import re

path = "/opt/verdis-chain-rust/pallets/presale/src/lib.rs"
with open(path, "r") as f:
    content = f.read()

# 1. Remove RefundClaimed from errors (it should be an event)
content = content.replace("        RefundClaimed,\n        RoundNotRefundable,", "        RoundNotRefundable,")

# 2. Add RefundClaimed event after FundsCollected
content = content.replace(
    """        /// Funds collected from escrow to beneficiary (O(1) operation)
        FundsCollected {
            round_id: u32,
            amount: BalanceOf<T>,
            collected_by: T::AccountId,
        },""",
    """        /// Funds collected from escrow to beneficiary (O(1) operation)
        FundsCollected {
            round_id: u32,
            amount: BalanceOf<T>,
            collected_by: T::AccountId,
        },
        /// Refund claimed by a contributor from a failed/cancelled round
        RefundClaimed {
            round_id: u32,
            account: T::AccountId,
            amount: BalanceOf<T>,
        },"""
)

# 3. Add set_whitelist_required and claim_refund extrinsics after collect_funds
# Find the end of collect_funds (the closing brace before the WeightInfo trait)
old_end = """            Self::deposit_event(Event::FundsCollected {
                round_id,
                amount: round_raised,
                collected_by: beneficiary,
            });

            Ok(())
        }
    }

    pub trait WeightInfo {"""

new_end = """            Self::deposit_event(Event::FundsCollected {
                round_id,
                amount: round_raised,
                collected_by: beneficiary,
            });

            Ok(())
        }

        /// Set whitelist enforcement for a round (admin only)
        #[pallet::call_index(7)]
        #[pallet::weight(T::WeightInfo::update_whitelist())]
        pub fn set_whitelist_required(
            origin: OriginFor<T>,
            round_id: u32,
            required: bool,
        ) -> DispatchResult {
            T::AdminOrigin::ensure_origin(origin)?;

            Rounds::<T>::try_mutate(round_id, |round_opt| {
                let round = round_opt.as_mut().ok_or(Error::<T>::RoundNotFound)?;
                round.whitelist_required = required;
                Ok(())
            })?;

            Self::deposit_event(Event::WhitelistUpdated {
                who: T::AccountId::default(),
                whitelisted: required,
            });

            Ok(())
        }

        /// Claim a refund for a failed/cancelled presale round.
        /// Only works when the round is inactive AND past its end block.
        #[pallet::call_index(8)]
        #[pallet::weight(T::WeightInfo::collect_funds())]
        pub fn claim_refund(
            origin: OriginFor<T>,
            round_id: u32,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            let round = Rounds::<T>::get(round_id).ok_or(Error::<T>::RoundNotFound)?;

            // Round must be inactive and past its end block
            ensure!(!round.is_active, Error::<T>::RoundNotRefundable);
            let current_block = frame_system::Pallet::<T>::block_number();
            ensure!(current_block >= round.end_block, Error::<T>::RoundNotRefundable);

            // Get user's contribution
            let contribution = Contributions::<T>::get(round_id, &who)
                .ok_or(Error::<T>::NoContribution)?;
            ensure!(
                contribution.payment_amount > BalanceOf::<T>::zero(),
                Error::<T>::NoContribution
            );

            let refund_amount = contribution.payment_amount;

            // Clear contribution record
            Contributions::<T>::remove(round_id, &who);

            // Transfer refund from escrow to user
            let escrow = T::PalletId::get().into_account_truncating();
            T::Currency::transfer(
                &escrow,
                &who,
                refund_amount,
                ExistenceRequirement::KeepAlive,
            )?;

            Self::deposit_event(Event::RefundClaimed {
                round_id,
                account: who,
                amount: refund_amount,
            });

            Ok(())
        }
    }

    pub trait WeightInfo {"""

content = content.replace(old_end, new_end)

# 4. Add weight functions for the new extrinsics
content = content.replace(
    """        fn collect_funds() -> frame_support::weights::Weight;
    }""",
    """        fn collect_funds() -> frame_support::weights::Weight;
        fn set_whitelist_required() -> frame_support::weights::Weight;
        fn claim_refund() -> frame_support::weights::Weight;
    }"""
)

# Add weights in SubstrateWeight impl
content = content.replace(
    """        fn collect_funds() -> frame_support::weights::Weight {
            // O(1) — no contributor iteration
            frame_support::weights::Weight::from_parts(15_000, 0)
        }
    }

    impl<T: Config> Pallet<T> {""",
    """        fn collect_funds() -> frame_support::weights::Weight {
            // O(1) — no contributor iteration
            frame_support::weights::Weight::from_parts(15_000, 0)
        }
        fn set_whitelist_required() -> frame_support::weights::Weight {
            frame_support::weights::Weight::from_parts(5_000, 0)
        }
        fn claim_refund() -> frame_support::weights::Weight {
            frame_support::weights::Weight::from_parts(15_000, 0)
        }
    }

    impl<T: Config> Pallet<T> {"""
)

# Add weights in the () impl too
content = content.replace(
    """    fn collect_funds() -> frame_support::weights::Weight {
        frame_support::weights::Weight::from_parts(15_000, 0)
    }
}

#[cfg(test)]""",
    """    fn collect_funds() -> frame_support::weights::Weight {
        frame_support::weights::Weight::from_parts(15_000, 0)
    }
    fn set_whitelist_required() -> frame_support::weights::Weight {
        frame_support::weights::Weight::from_parts(5_000, 0)
    }
    fn claim_refund() -> frame_support::weights::Weight {
        frame_support::weights::Weight::from_parts(15_000, 0)
    }
}

#[cfg(test)]"""
)

# 5. Fix the WhitelistUpdated event — it needs `who` field, but set_whitelist_required doesn't have a specific user
# Let me check the event structure
# Actually, the event already has `who: T::AccountId` — but we're passing default. That's a bit ugly but works.
# Better: let's just use the pallet account as a placeholder, or better yet, skip the event for set_whitelist_required

# Actually, let me not emit WhitelistUpdated for set_whitelist_required. It's a different operation.
content = content.replace(
    """            Self::deposit_event(Event::WhitelistUpdated {
                who: T::AccountId::default(),
                whitelisted: required,
            });

            Ok(())
        }

        /// Claim a refund""",
    """            Ok(())
        }

        /// Claim a refund"""
)

with open(path, "w") as f:
    f.write(content)
print("Fixed: set_whitelist_required (call_index 7) and claim_refund (call_index 8) extrinsics added")
