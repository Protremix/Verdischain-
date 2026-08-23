#!/usr/bin/env python3
"""Apply P0 + P1 fixes to presale and vesting pallets."""

# ============================================================
# P0: PER-ROUND ESCROW + P1: PAYMENT CURRENCY
# File: pallets/presale/src/lib.rs
# ============================================================

with open("/opt/verdis-chain-rust/pallets/presale/src/lib.rs") as f:
    presale = f.read()

# --- Fix 1: Add PaymentCurrency to Config trait ---
old_config = """        type Currency: Currency<Self::AccountId>;
        #[pallet::constant]
        type PalletId: Get<PalletId>;"""

new_config = """        /// Token currency - VRDX tokens distributed to buyers.
        type Currency: Currency<Self::AccountId>;
        /// Payment currency - asset buyers pay with.
        /// For testnet, set to the same as Currency (native VRDX bonus-rate presale).
        /// For mainnet, set to a stablecoin or other accepted payment asset.
        type PaymentCurrency: Currency<Self::AccountId>;
        #[pallet::constant]
        type PalletId: Get<PalletId>;"""

presale = presale.replace(old_config, new_config)
print("1. Added PaymentCurrency to Config trait")

# --- Fix 2: Add round_escrow helper ---
old_pallet_struct = "    #[pallet::pallet]\n    pub struct Pallet<T>(_);"

new_pallet_struct = """    #[pallet::pallet]
    pub struct Pallet<T>(_>;

    // Per-Round Escrow: each round gets its own deterministic sub-account
    // derived from PalletId + round_id. This isolates funds per round so
    // collect_funds for one round cannot drain another round's payments.
    fn round_escrow(round_id: u32) -> T::AccountId {
        T::PalletId::get().into_sub_account_truncating(round_id)
    }"""

presale = presale.replace(old_pallet_struct, new_pallet_struct, 1)
print("2. Added round_escrow helper")

# --- Fix 3: Replace all escrow references in contribute() ---
old_contribute_escrow = """            // === Verify escrow has enough VRDX before any state mutation ===
            let escrow = T::PalletId::get().into_account_truncating();
            let escrow_balance = T::Currency::free_balance(&escrow);

            // === All checks passed - now perform state mutations (atomic) ===

            // 1. Transfer payment from buyer to presale escrow
            T::Currency::transfer(
                &who,
                &escrow,
                payment_amount,
                ExistenceRequirement::KeepAlive,
            )
            .map_err(|_| Error::<T>::InsufficientPayment)?;

            // 2. Transfer purchased VRDX from escrow to buyer
            T::Currency::transfer(
                &escrow,
                &who,
                token_amount,
                ExistenceRequirement::AllowDeath,
            )"""

new_contribute_escrow = """            // === Verify escrow has enough VRDX before any state mutation ===
            let escrow = Self::round_escrow(round_id);
            let escrow_balance = T::Currency::free_balance(&escrow);

            // === All checks passed - now perform state mutations (atomic) ===

            // 1. Transfer payment from buyer to per-round escrow (PaymentCurrency)
            T::PaymentCurrency::transfer(
                &who,
                &escrow,
                payment_amount,
                ExistenceRequirement::KeepAlive,
            )
            .map_err(|_| Error::<T>::InsufficientPayment)?;

            // 2. Transfer purchased VRDX from escrow to buyer (Currency = VRDX)
            T::Currency::transfer(
                &escrow,
                &who,
                token_amount,
                ExistenceRequirement::AllowDeath,
            )"""

presale = presale.replace(old_contribute_escrow, new_contribute_escrow)
print("3. Fixed contribute() escrow + PaymentCurrency")

# --- Fix 4: Replace escrow in collect_funds() ---
old_collect = """            // Transfer from escrow to beneficiary (O(1) - no contributor iteration)
            if round_raised > BalanceOf::<T>::zero() {
                let escrow = T::PalletId::get().into_account_truncating();
                T::Currency::transfer(
                    &escrow,
                    &beneficiary,
                    round_raised,
                    ExistenceRequirement::AllowDeath,
                )?;"""

new_collect = """            // Transfer payment tokens from per-round escrow to beneficiary (O(1))
            if round_raised > BalanceOf::<T>::zero() {
                let escrow = Self::round_escrow(round_id);
                T::PaymentCurrency::transfer(
                    &escrow,
                    &beneficiary,
                    round_raised,
                    ExistenceRequirement::AllowDeath,
                )?;"""

presale = presale.replace(old_collect, new_collect)
print("4. Fixed collect_funds() escrow + PaymentCurrency")

# --- Fix 5: Replace escrow in claim_refund() ---
old_refund = """            let refund_amount = contribution.total_paid;
            let tokens_to_return = contribution.total_purchased;
            let escrow = T::PalletId::get().into_account_truncating();"""

new_refund = """            let refund_amount = contribution.total_paid;
            let tokens_to_return = contribution.total_purchased;
            let escrow = Self::round_escrow(round_id);"""

presale = presale.replace(old_refund, new_refund)
print("5. Fixed claim_refund() escrow")

# --- Fix 6: Fix token transfer in claim_refund ---
old_refund_transfer = """            // Now that vesting is removed and tokens are unlocked, transfer them back to escrow
            if tokens_to_return > BalanceOf::<T>::zero() {
                T::Currency::transfer(
                    &who,
                    &escrow,
                    tokens_to_return,
                    ExistenceRequirement::KeepAlive,
                )
                .map_err(|_| Error::<T>::InsufficientPayment)?;
            }

            // Transfer refund from escrow to user
            T::Currency::transfer(
                &escrow,
                &who,
                refund_amount,
                ExistenceRequirement::KeepAlive,
            )?;"""

new_refund_transfer = """            // Transfer VRDX tokens back from user to per-round escrow
            if tokens_to_return > BalanceOf::<T>::zero() {
                T::Currency::transfer(
                    &who,
                    &escrow,
                    tokens_to_return,
                    ExistenceRequirement::KeepAlive,
                )
                .map_err(|_| Error::<T>::InsufficientPayment)?;
            }

            // Transfer refund (payment tokens) from per-round escrow to user
            T::PaymentCurrency::transfer(
                &escrow,
                &who,
                refund_amount,
                ExistenceRequirement::KeepAlive,
            )?;"""

presale = presale.replace(old_refund_transfer, new_refund_transfer)
print("6. Fixed claim_refund() token vs payment transfers")

# --- Fix 7: Update pallet docs ---
presale = presale.replace(
    "//! - **Escrow-based payments**: buyer pays into a deterministic Presale Escrow",
    "//! - **Per-round escrow**: each round has its own deterministic sub-account escrow"
)
presale = presale.replace(
    "//! - **O(1) fund collection** from escrow (no unbounded contributor iteration)",
    "//! - **O(1) fund collection** from per-round escrow (no unbounded contributor iteration)"
)
presale = presale.replace(
    "//! Buyer --payment--> Presale Escrow Account\n//! Presale Escrow Account --VRDX--> Buyer\n//! Presale Escrow Account --vesting--> Vesting Pallet",
    "//! Buyer --payment (PaymentCurrency)--> Per-Round Escrow Account\n//! Per-Round Escrow Account --VRDX (Currency)--> Buyer\n//! Per-Round Escrow Account --vesting--> Vesting Pallet"
)
presale = presale.replace(
    "//!   Presale Escrow --RoundRaised amount--> Beneficiary",
    "//!   Per-Round Escrow --RoundRaised (PaymentCurrency)--> Beneficiary"
)
print("7. Updated pallet docs")

with open("/opt/verdis-chain-rust/pallets/presale/src/lib.rs", "w") as f:
    f.write(presale)
print("\n=== Presale lib.rs updated ===")

# ============================================================
# P1: VESTING WEIGHT FIX
# File: pallets/vesting/src/lib.rs
# ============================================================

with open("/opt/verdis-chain-rust/pallets/vesting/src/lib.rs") as f:
    vesting = f.read()

# Fix weight annotations - use worst case MaxSchedulesPerAccount
vesting = vesting.replace(
    "#[pallet::weight(T::WeightInfo::add_schedule(0))]",
    "#[pallet::weight(T::WeightInfo::add_schedule(64))]"
)
vesting = vesting.replace(
    "#[pallet::weight(T::WeightInfo::assign_vesting(0))]",
    "#[pallet::weight(T::WeightInfo::assign_vesting(T::MaxSchedulesPerAccount::get()))]"
)
# Both release_vested and remove_vesting use release_vested weight
vesting = vesting.replace(
    "#[pallet::weight(T::WeightInfo::release_vested(0))]",
    "#[pallet::weight(T::WeightInfo::release_vested(T::MaxSchedulesPerAccount::get()))]"
)
print("8. Fixed vesting weight annotations (0 -> MaxSchedulesPerAccount)")

with open("/opt/verdis-chain-rust/pallets/vesting/src/lib.rs", "w") as f:
    f.write(vesting)
print("\n=== Vesting lib.rs updated ===")

# ============================================================
# P1: RUNTIME CONFIG UPDATES
# File: runtime/src/lib.rs
# ============================================================

with open("/opt/verdis-chain-rust/runtime/src/lib.rs") as f:
    runtime = f.read()

# Add PaymentCurrency to presale config
old_presale_impl = """impl pallet_presale::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type Currency = MaxSupplyCurrency;
    type PalletId = PresalePalletId;"""

new_presale_impl = """impl pallet_presale::Config for Runtime {
    type RuntimeEvent = RuntimeEvent;
    type Currency = MaxSupplyCurrency;
    // Payment currency: native VRDX for testnet (bonus-rate presale).
    // For mainnet, change this to a stablecoin or other accepted asset.
    type PaymentCurrency = MaxSupplyCurrency;
    type PalletId = PresalePalletId;"""

runtime = runtime.replace(old_presale_impl, new_presale_impl)
print("9. Added PaymentCurrency to runtime presale config")

with open("/opt/verdis-chain-rust/runtime/src/lib.rs", "w") as f:
    f.write(runtime)
print("\n=== Runtime lib.rs updated ===")
print("\nAll fixes applied successfully!")
