//! Max Supply Currency Wrapper
//!
//! A wrapper that enforces a hard cap (TOTAL_SUPPLY) on total token issuance.
//! Intercepts every minting path in both the old `Currency` trait family
//! AND the new `fungible` trait family.
//!
//! Protocol Invariant: TOTAL_ISSUANCE <= TOTAL_SUPPLY
//! Enforced at runtime, checked atomically before any state change.

use crate::{AccountId, Balance, Balances, RuntimeHoldReason, TOTAL_SUPPLY};
use frame_support::traits::{
    tokens::{
        currency::{Currency, ReservableCurrency},
        fungible,
        imbalance::SignedImbalance,
        BalanceStatus, DepositConsequence, ExistenceRequirement,
        Fortitude, Preservation, Provenance, WithdrawConsequence,
    },
    LockableCurrency, LockIdentifier, WithdrawReasons,
};
use sp_runtime::{
    traits::{CheckedAdd, CheckedSub, Zero},
    DispatchError, DispatchResult,
};

// Type aliases for readability
type PosImb = <Balances as Currency<AccountId>>::PositiveImbalance;
type NegImb = <Balances as Currency<AccountId>>::NegativeImbalance;

// ─── Wrapper Type ────────────────────────────────────────────────────────────

pub struct MaxSupplyCurrency;

impl MaxSupplyCurrency {
    /// Check that minting `amount` would not exceed TOTAL_SUPPLY.
    #[inline]
    fn check_mint(amount: Balance) -> Result<(), DispatchError> {
        if amount.is_zero() {
            return Ok(());
        }
        let current = <Balances as Currency<AccountId>>::total_issuance();
        let new_total = current
            .checked_add(amount)
            .ok_or(DispatchError::Other("MaxSupply: overflow"))?;
        if new_total > TOTAL_SUPPLY {
            return Err(DispatchError::Other("MaxSupply: cap exceeded"));
        }
        Ok(())
    }

    /// Check that increasing `current_balance` to `new_balance` would not exceed cap.
    #[inline]
    fn check_increase(current_balance: Balance, new_balance: Balance) -> Result<(), DispatchError> {
        if new_balance <= current_balance {
            return Ok(());
        }
        let increase = new_balance
            .checked_sub(current_balance)
            .ok_or(DispatchError::Other("MaxSupply: underflow"))?;
        Self::check_mint(increase)
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Currency trait family (old API — used by dpos, vesting, presale, etc.)
// ═══════════════════════════════════════════════════════════════════════════════

impl Currency<AccountId> for MaxSupplyCurrency {
    type Balance = Balance;
    type PositiveImbalance = PosImb;
    type NegativeImbalance = NegImb;

    // ── Read-only: delegate ──────────────────────────────────────────────────
    #[inline] fn total_balance(who: &AccountId) -> Self::Balance { <Balances as Currency<AccountId>>::total_balance(who) }
    #[inline] fn can_slash(who: &AccountId, v: Self::Balance) -> bool { <Balances as Currency<AccountId>>::can_slash(who, v) }
    #[inline] fn total_issuance() -> Self::Balance { <Balances as Currency<AccountId>>::total_issuance() }
    #[inline] fn active_issuance() -> Self::Balance { <Balances as Currency<AccountId>>::active_issuance() }
    #[inline] fn minimum_balance() -> Self::Balance { <Balances as Currency<AccountId>>::minimum_balance() }
    #[inline] fn free_balance(who: &AccountId) -> Self::Balance { <Balances as Currency<AccountId>>::free_balance(who) }

    // ── Non-minting: delegate ────────────────────────────────────────────────
    #[inline] fn burn(amount: Self::Balance) -> Self::PositiveImbalance { <Balances as Currency<AccountId>>::burn(amount) }
    #[inline] fn pair(amount: Self::Balance) -> (Self::PositiveImbalance, Self::NegativeImbalance) { <Balances as Currency<AccountId>>::pair(amount) }
    #[inline]
    fn ensure_can_withdraw(who: &AccountId, amount: Self::Balance, reasons: WithdrawReasons, new_balance: Self::Balance) -> DispatchResult {
        <Balances as Currency<AccountId>>::ensure_can_withdraw(who, amount, reasons, new_balance)
    }
    #[inline]
    fn transfer(src: &AccountId, dest: &AccountId, v: Self::Balance, er: ExistenceRequirement) -> DispatchResult {
        <Balances as Currency<AccountId>>::transfer(src, dest, v, er)
    }
    #[inline]
    fn slash(who: &AccountId, v: Self::Balance) -> (Self::NegativeImbalance, Self::Balance) {
        <Balances as Currency<AccountId>>::slash(who, v)
    }
    #[inline]
    fn withdraw(who: &AccountId, v: Self::Balance, reasons: WithdrawReasons, er: ExistenceRequirement) -> Result<Self::NegativeImbalance, DispatchError> {
        <Balances as Currency<AccountId>>::withdraw(who, v, reasons, er)
    }
    #[inline]
    fn settle(who: &AccountId, v: Self::PositiveImbalance, reasons: WithdrawReasons, er: ExistenceRequirement) -> Result<(), Self::PositiveImbalance> {
        <Balances as Currency<AccountId>>::settle(who, v, reasons, er)
    }
    #[inline]
    fn resolve_into_existing(who: &AccountId, v: Self::NegativeImbalance) -> Result<(), Self::NegativeImbalance> {
        <Balances as Currency<AccountId>>::resolve_into_existing(who, v)
    }
    #[inline]
    fn resolve_creating(who: &AccountId, v: Self::NegativeImbalance) {
        <Balances as Currency<AccountId>>::resolve_creating(who, v)
    }

    // ── Minting: cap-enforced ────────────────────────────────────────────────
    fn issue(amount: Self::Balance) -> Self::NegativeImbalance {
        // FIX H2: Return zero imbalance instead of panicking when cap is exceeded.
        // Panicking in runtime causes block-level DoS — any tx that triggers the
        // cap would reject the entire block. Returning a zero imbalance is safe
        // because the caller will see no actual mint occurred.
        if Self::check_mint(amount).is_err() {
            return <Balances as Currency<AccountId>>::issue(0);
        }
        <Balances as Currency<AccountId>>::issue(amount)
    }

    fn deposit_into_existing(who: &AccountId, value: Self::Balance) -> Result<Self::PositiveImbalance, DispatchError> {
        Self::check_mint(value)?;
        <Balances as Currency<AccountId>>::deposit_into_existing(who, value)
    }

    fn deposit_creating(who: &AccountId, value: Self::Balance) -> Self::PositiveImbalance {
        // FIX H1: Return zero imbalance instead of panicking when cap is exceeded.
        // The caller will see a zero PositiveImbalance, meaning no mint occurred.
        // This prevents block-level DoS while preserving the supply cap invariant.
        if Self::check_mint(value).is_err() {
            return <Balances as Currency<AccountId>>::deposit_creating(who, 0);
        }
        <Balances as Currency<AccountId>>::deposit_creating(who, value)
    }

    fn make_free_balance_be(who: &AccountId, value: Self::Balance) -> SignedImbalance<Self::Balance, Self::PositiveImbalance> {
        let current = <Balances as Currency<AccountId>>::free_balance(who);
        if Self::check_increase(current, value).is_err() {
            let max_increase = TOTAL_SUPPLY.checked_sub(<Balances as Currency<AccountId>>::total_issuance()).unwrap_or(Balance::zero());
            let capped = current.checked_add(max_increase).unwrap_or(current);
            if capped <= current {
                return <Balances as Currency<AccountId>>::make_free_balance_be(who, current);
            }
            return <Balances as Currency<AccountId>>::make_free_balance_be(who, capped);
        }
        <Balances as Currency<AccountId>>::make_free_balance_be(who, value)
    }
}

// ─── ReservableCurrency ──────────────────────────────────────────────────────

impl ReservableCurrency<AccountId> for MaxSupplyCurrency {
    #[inline] fn can_reserve(who: &AccountId, v: Self::Balance) -> bool { Balances::can_reserve(who, v) }
    #[inline] fn slash_reserved(who: &AccountId, v: Self::Balance) -> (Self::NegativeImbalance, Self::Balance) { Balances::slash_reserved(who, v) }
    #[inline] fn reserved_balance(who: &AccountId) -> Self::Balance { Balances::reserved_balance(who) }
    #[inline] fn reserve(who: &AccountId, v: Self::Balance) -> DispatchResult { Balances::reserve(who, v) }
    #[inline] fn unreserve(who: &AccountId, v: Self::Balance) -> Self::Balance { Balances::unreserve(who, v) }
    #[inline]
    fn repatriate_reserved(slashed: &AccountId, beneficiary: &AccountId, v: Self::Balance, s: BalanceStatus) -> Result<Self::Balance, DispatchError> {
        Balances::repatriate_reserved(slashed, beneficiary, v, s)
    }
}

// ─── LockableCurrency ────────────────────────────────────────────────────────

impl LockableCurrency<AccountId> for MaxSupplyCurrency {
    type Moment = <Balances as LockableCurrency<AccountId>>::Moment;
    type MaxLocks = <Balances as LockableCurrency<AccountId>>::MaxLocks;

    #[inline]
    fn set_lock(id: LockIdentifier, who: &AccountId, amount: Self::Balance, reasons: WithdrawReasons) {
        Balances::set_lock(id, who, amount, reasons)
    }
    #[inline]
    fn extend_lock(id: LockIdentifier, who: &AccountId, amount: Self::Balance, reasons: WithdrawReasons) {
        Balances::extend_lock(id, who, amount, reasons)
    }
    #[inline]
    fn remove_lock(id: LockIdentifier, who: &AccountId) {
        Balances::remove_lock(id, who)
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// fungible trait family (new API — used by pallet_contracts)
// ═══════════════════════════════════════════════════════════════════════════════

impl fungible::Inspect<AccountId> for MaxSupplyCurrency {
    type Balance = Balance;

    #[inline] fn total_issuance() -> Self::Balance { <Balances as fungible::Inspect<AccountId>>::total_issuance() }
    #[inline] fn active_issuance() -> Self::Balance { <Balances as fungible::Inspect<AccountId>>::active_issuance() }
    #[inline] fn minimum_balance() -> Self::Balance { <Balances as fungible::Inspect<AccountId>>::minimum_balance() }
    #[inline] fn total_balance(who: &AccountId) -> Self::Balance { <Balances as fungible::Inspect<AccountId>>::total_balance(who) }
    #[inline] fn balance(who: &AccountId) -> Self::Balance { <Balances as fungible::Inspect<AccountId>>::balance(who) }

    #[inline]
    fn reducible_balance(who: &AccountId, preservation: Preservation, force: Fortitude) -> Self::Balance {
        <Balances as fungible::Inspect<AccountId>>::reducible_balance(who, preservation, force)
    }

    #[inline]
    fn can_deposit(who: &AccountId, amount: Self::Balance, provenance: Provenance) -> DepositConsequence {
        if provenance == Provenance::Minted {
            if Self::check_mint(amount).is_err() {
                return DepositConsequence::Overflow;
            }
        }
        <Balances as fungible::Inspect<AccountId>>::can_deposit(who, amount, provenance)
    }

    #[inline]
    fn can_withdraw(who: &AccountId, amount: Self::Balance) -> WithdrawConsequence<Self::Balance> {
        <Balances as fungible::Inspect<AccountId>>::can_withdraw(who, amount)
    }
}

impl fungible::Unbalanced<AccountId> for MaxSupplyCurrency {
    fn handle_dust(dust: fungible::Dust<AccountId, Self>) {
        // Dust is already removed from the account — just drop it
        // (Same as Balances' default which calls DustRemoval)
        drop(dust);
    }

    fn write_balance(who: &AccountId, amount: Self::Balance) -> Result<Option<Self::Balance>, DispatchError> {
        let current = <Balances as fungible::Inspect<AccountId>>::balance(who);
        if amount > current {
            Self::check_increase(current, amount)?;
        }
        Balances::write_balance(who, amount)
    }

    fn set_total_issuance(amount: Self::Balance) {
        if amount > TOTAL_SUPPLY {
            panic!("MaxSupplyCurrency::set_total_issuance: {} exceeds cap {}", amount, TOTAL_SUPPLY);
        }
        Balances::set_total_issuance(amount);
    }

    #[inline] fn deactivate(amount: Self::Balance) { <Balances as fungible::Unbalanced<AccountId>>::deactivate(amount) }
    #[inline] fn reactivate(amount: Self::Balance) { <Balances as fungible::Unbalanced<AccountId>>::reactivate(amount) }
}

impl fungible::Mutate<AccountId> for MaxSupplyCurrency {}

impl fungible::InspectHold<AccountId> for MaxSupplyCurrency {
    type Reason = RuntimeHoldReason;

    #[inline] fn total_balance_on_hold(who: &AccountId) -> Self::Balance { Balances::total_balance_on_hold(who) }
    #[inline] fn reducible_total_balance_on_hold(who: &AccountId, force: Fortitude) -> Self::Balance { Balances::reducible_total_balance_on_hold(who, force) }
    #[inline] fn balance_on_hold(reason: &Self::Reason, who: &AccountId) -> Self::Balance { Balances::balance_on_hold(reason, who) }
    #[inline] fn hold_available(reason: &Self::Reason, who: &AccountId) -> bool { Balances::hold_available(reason, who) }
}

impl fungible::UnbalancedHold<AccountId> for MaxSupplyCurrency {
    #[inline]
    fn set_balance_on_hold(reason: &Self::Reason, who: &AccountId, amount: Self::Balance) -> DispatchResult {
        Balances::set_balance_on_hold(reason, who, amount)
    }
}

impl fungible::MutateHold<AccountId> for MaxSupplyCurrency {}
