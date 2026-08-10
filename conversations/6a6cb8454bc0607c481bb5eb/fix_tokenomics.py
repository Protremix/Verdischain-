import re

# Fix C-06: Tokenomics purchase safety
with open("/opt/verdis-chain-rust/pallets/tokenomics/src/lib.rs", "r") as f:
    content = f.read()

# Add zero-check and fix saturating arithmetic in purchase
old_purchase = """        pub fn purchase(origin: OriginFor<T>, amount: BalanceOf<T>) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // Enforce consent gating
            ensure!(
                ConsentGiven::<T>::get(&who).unwrap_or(false),
                Error::<T>::ConsentRequired
            );

            // Enforce investor allocation limit (12B)
            let sold = PresaleSold::<T>::get();
            let max = T::InvestorAllocation::get();
            ensure!(
                sold.saturating_add(amount) <= max,
                Error::<T>::MaxInvestorAllocationReached
            );

            // Calculate price (price_bps is in basis points)
            let price_bps = PresalePrice::<T>::get();
            let price_bal: BalanceOf<T> = price_bps.saturated_into();
            let divisor: BalanceOf<T> = 10_000u32.saturated_into();
            let cost = amount.saturating_mul(price_bal) / divisor;"""

new_purchase = """        pub fn purchase(origin: OriginFor<T>, amount: BalanceOf<T>) -> DispatchResult {
            let who = ensure_signed(origin)?;

            // Zero-check: prevent zero-amount purchases
            ensure!(amount > BalanceOf::<T>::zero(), Error::<T>::ZeroAmount);

            // Enforce consent gating
            ensure!(
                ConsentGiven::<T>::get(&who).unwrap_or(false),
                Error::<T>::ConsentRequired
            );

            // Enforce investor allocation limit
            let sold = PresaleSold::<T>::get();
            let max = T::InvestorAllocation::get();
            let new_sold = sold
                .checked_add(&amount)
                .ok_or(Error::<T>::CalculationOverflow)?;
            ensure!(
                new_sold <= max,
                Error::<T>::MaxInvestorAllocationReached
            );

            // Calculate price (price_bps is in basis points)
            let price_bps = PresalePrice::<T>::get();
            let price_bal: BalanceOf<T> = price_bps.saturated_into();
            let divisor: BalanceOf<T> = 10_000u32.saturated_into();
            let gross = amount
                .checked_mul(&price_bal)
                .ok_or(Error::<T>::CalculationOverflow)?;
            let cost = gross
                .checked_div(&divisor)
                .ok_or(Error::<T>::CalculationOverflow)?;
            ensure!(cost > BalanceOf::<T>::zero(), Error::<T>::ZeroPrice);"""

content = content.replace(old_purchase, new_purchase)

# Also fix the saturating updates after purchase
content = content.replace(
    "PresaleRaised::<T>::mutate(|r| *r = r.saturating_add(cost));",
    "PresaleRaised::<T>::mutate(|r| *r = r.checked_add(&cost).ok_or(Error::<T>::CalculationOverflow)?);"
)
content = content.replace(
    "PresaleSold::<T>::mutate(|s| *s = s.saturating_add(amount));",
    "PresaleSold::<T>::mutate(|s| *s = s.checked_add(&amount).ok_or(Error::<T>::CalculationOverflow)?);"
)
content = content.replace(
    "CirculatingSupply::<T>::mutate(|c| *c = c.saturating_add(amount));",
    "CirculatingSupply::<T>::mutate(|c| *c = c.checked_add(&amount).ok_or(Error::<T>::CalculationOverflow)?);"
)

# Add missing error variants if they don't exist
if "ZeroAmount" not in content:
    content = content.replace(
        "ConsentRequired,",
        "ConsentRequired,\n        ZeroAmount,\n        ZeroPrice,\n        CalculationOverflow,"
    )

with open("/opt/verdis-chain-rust/pallets/tokenomics/src/lib.rs", "w") as f:
    f.write(content)

print("Done: tokenomics purchase fixed")
