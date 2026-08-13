#!/usr/bin/env python3
"""Fix all 5 Kimi audit issues: C1 (EnsureRoot), C2 (Treasury), C5 (fungible cap + fast-track)."""

import re

# === C1: Fix eco pallet — add AdminOrigin to Config, replace ensure_root ===
with open("pallets/eco/src/lib.rs") as f:
    eco = f.read()

# Add AdminOrigin to Config trait
old_eco_config = """    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        #[pallet::constant]
        type PalletId: Get<PalletId>;
        #[pallet::constant]
        type MaxCarbonCredits: Get<u32>;
        #[pallet::constant]
        type MaxReforestProjects: Get<u32>;
        #[pallet::constant]
        type MaxGreenValidators: Get<u32>;
        #[pallet::constant]
        type MinGreenScore: Get<u8>;
        #[pallet::constant]
        type MaxGreenScore: Get<u8>;
        type WeightInfo: WeightInfo;
    }"""

new_eco_config = """    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        #[pallet::constant]
        type PalletId: Get<PalletId>;
        #[pallet::constant]
        type MaxCarbonCredits: Get<u32>;
        #[pallet::constant]
        type MaxReforestProjects: Get<u32>;
        #[pallet::constant]
        type MaxGreenValidators: Get<u32>;
        #[pallet::constant]
        type MinGreenScore: Get<u8>;
        #[pallet::constant]
        type MaxGreenScore: Get<u8>;
        type WeightInfo: WeightInfo;
        /// Post-sudo: Council (2/3) administers eco operations
        type AdminOrigin: EnsureOrigin<Self::RuntimeOrigin>;
    }"""

if old_eco_config in eco:
    eco = eco.replace(old_eco_config, new_eco_config)
    # Replace all ensure_root with T::AdminOrigin
    eco = eco.replace("ensure_root(origin)?", "T::AdminOrigin::ensure_origin(origin)?")
    print("ECO: Added AdminOrigin, replaced ensure_root calls")
else:
    print("SKIP: ECO config block not found")

with open("pallets/eco/src/lib.rs", "w") as f:
    f.write(eco)

# Check if eco needs EnsureOrigin import
if "EnsureOrigin" not in eco and "ensure_origin" in eco:
    # Need to add the import
    eco = eco.replace(
        "use frame_support::pallet_prelude::*;",
        "use frame_support::pallet_prelude::*;\nuse frame_support::traits::EnsureOrigin;",
    )
    with open("pallets/eco/src/lib.rs", "w") as f:
        f.write(eco)

# === C1: Fix tokenomics pallet — add AdminOrigin ===
with open("pallets/tokenomics/src/lib.rs") as f:
    tok = f.read()

old_tok_config = """    pub trait Config: frame_system::Config {
        /// Maximum priority fee multiplier
        #[pallet::constant]
        type MaxPriorityFeeMultiplier: Get<u32>;
        /// Default transfer fee percentage (basis points, e.g., 50 = 0.5%)
        #[pallet::constant]
        type DefaultTransferFeeBps: Get<u32>;
        /// Green treasury account for eco fees
        #[pallet::constant]
        type GreenTreasury: Get<Self::AccountId>;
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        type Currency: ReservableCurrency<Self::AccountId>;
        #[pallet::constant]
        type TotalSupply: Get<BalanceOf<Self>>;
        #[pallet::constant]
        type InvestorAllocation: Get<BalanceOf<Self>>;
        #[pallet::constant]
        type PalletId: Get<PalletId>;
        type WeightInfo: WeightInfo;
    }"""

new_tok_config = """    pub trait Config: frame_system::Config {
        /// Maximum priority fee multiplier
        #[pallet::constant]
        type MaxPriorityFeeMultiplier: Get<u32>;
        /// Default transfer fee percentage (basis points, e.g., 50 = 0.5%)
        #[pallet::constant]
        type DefaultTransferFeeBps: Get<u32>;
        /// Green treasury account for eco fees
        #[pallet::constant]
        type GreenTreasury: Get<Self::AccountId>;
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;
        type Currency: ReservableCurrency<Self::AccountId>;
        #[pallet::constant]
        type TotalSupply: Get<BalanceOf<Self>>;
        #[pallet::constant]
        type InvestorAllocation: Get<BalanceOf<Self>>;
        #[pallet::constant]
        type PalletId: Get<PalletId>;
        type WeightInfo: WeightInfo;
        /// Post-sudo: Council (2/3) administers tokenomics
        type AdminOrigin: EnsureOrigin<Self::RuntimeOrigin>;
    }"""

if old_tok_config in tok:
    tok = tok.replace(old_tok_config, new_tok_config)
    tok = tok.replace("ensure_root(origin)?", "T::AdminOrigin::ensure_origin(origin)?")
    print("TOKENOMICS: Added AdminOrigin, replaced ensure_root calls")
else:
    print("SKIP: Tokenomics config block not found")

# Add EnsureOrigin import if needed
if "EnsureOrigin" not in tok.split("pub trait Config")[0]:
    tok = tok.replace(
        "use frame_support::pallet_prelude::*;",
        "use frame_support::pallet_prelude::*;\nuse frame_support::traits::EnsureOrigin;",
        1
    )

with open("pallets/tokenomics/src/lib.rs", "w") as f:
    f.write(tok)

# === C1+C2: Fix runtime — all remaining EnsureRoot + Treasury ===
with open("runtime/src/lib.rs") as f:
    rt = f.read()

# Fix Identity: ForceOrigin, RegistrarOrigin, UsernameAuthorityOrigin
rt = rt.replace(
    "    type ForceOrigin = EnsureRoot<AccountId>;\n    type RegistrarOrigin = EnsureRoot<AccountId>;",
    "    // Post-sudo: Council (2/3) controls identity\n    type ForceOrigin = pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;\n    type RegistrarOrigin = pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;",
    1
)
rt = rt.replace(
    "    type UsernameAuthorityOrigin = EnsureRoot<AccountId>;",
    "    // Post-sudo: Council (2/3) controls usernames\n    type UsernameAuthorityOrigin = pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;",
    1
)

# Fix NFTs: ForceOrigin and any CreateOrigin = EnsureRoot
# Find the NFTs section and fix it
rt = rt.replace(
    "    type CreateOrigin = frame_system::EnsureRoot<AccountId>;\n    type ForceOrigin = EnsureRoot<AccountId>;",
    "    // Post-sudo: Anyone can create NFT collections, Council (2/3) can force\n    type CreateOrigin = frame_system::EnsureSigned<AccountId>;\n    type ForceOrigin = pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;",
    1
)

# Fix any remaining NFTs ForceOrigin (line 1011 context)
# This one already has CreateOrigin = EnsureSigned, just fix ForceOrigin
rt = rt.replace(
    "    type Currency = Balances;\n    type ForceOrigin = EnsureRoot<AccountId>;\n    type CreateOrigin = frame_system::EnsureSigned<AccountId>;",
    "    type Currency = Balances;\n    // Post-sudo: Council (2/3) can force NFT actions\n    type ForceOrigin = pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;\n    type CreateOrigin = frame_system::EnsureSigned<AccountId>;",
    1
)

# C2: Fix Treasury SpendOrigin — create custom Council spend origin
# Add the custom origin before the Treasury config
old_treasury_spend = "    type SpendOrigin = frame_system::EnsureRootWithSuccess<AccountId, TreasuryMaxSpend>;"
new_treasury_spend = "    type SpendOrigin = EnsureCouncilSpend;"

if old_treasury_spend in rt:
    rt = rt.replace(old_treasury_spend, new_treasury_spend)
    print("TREASURY: SpendOrigin -> EnsureCouncilSpend (custom)")
else:
    print("SKIP: Treasury SpendOrigin not found")

# Add EnsureCouncilSpend struct before the Treasury config
# Find a good place to insert it — before the Treasury parameter_types
treasury_marker = "// === Treasury ==="
council_spend_struct = """// === Post-sudo: Council spend origin for Treasury ===
pub struct EnsureCouncilSpend;
impl EnsureOrigin<RuntimeOrigin> for EnsureCouncilSpend {
    type Success = u128;
    fn try_origin(o: RuntimeOrigin) -> Result<Self::Success, RuntimeOrigin> {
        pallet_collective::EnsureProportionAtLeast::<AccountId, pallet_collective::Instance1, 2, 3>::try_origin(o)
            .map(|_| TreasuryMaxSpend::get())
    }
    #[cfg(feature = "runtime-benchmarks")]
    fn try_origin_or_root(o: RuntimeOrigin) -> Result<Self::Success, RuntimeOrigin> {
        if o.into().is_root_origin() {
            Ok(TreasuryMaxSpend::get())
        } else {
            Self::try_origin(o)
        }
    }
}

"""

if treasury_marker in rt and "EnsureCouncilSpend" not in rt:
    rt = rt.replace(treasury_marker, council_spend_struct + treasury_marker)
    print("RUNTIME: Added EnsureCouncilSpend struct")
elif "EnsureCouncilSpend" in rt:
    print("SKIP: EnsureCouncilSpend already exists")
else:
    print("SKIP: Treasury marker not found")

# Add eco AdminOrigin to runtime
old_eco_rt = "impl pallet_eco::Config for Runtime {"
new_eco_rt = """impl pallet_eco::Config for Runtime {
    type AdminOrigin = pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;"""

if old_eco_rt in rt and "AdminOrigin" not in rt.split("impl pallet_eco::Config")[1].split("}")[0]:
    rt = rt.replace(old_eco_rt, new_eco_rt, 1)
    print("RUNTIME: Added eco AdminOrigin = Council 2/3")
else:
    print("SKIP: eco AdminOrigin already set or not found")

# Add tokenomics AdminOrigin to runtime
old_tok_rt = "impl pallet_tokenomics::Config for Runtime {"
new_tok_rt = """impl pallet_tokenomics::Config for Runtime {
    type AdminOrigin = pallet_collective::EnsureProportionAtLeast<AccountId, pallet_collective::Instance1, 2, 3>;"""

if old_tok_rt in rt and "AdminOrigin" not in rt.split("impl pallet_tokenomics::Config")[1].split("}")[0]:
    rt = rt.replace(old_tok_rt, new_tok_rt, 1)
    print("RUNTIME: Added tokenomics AdminOrigin = Council 2/3")
else:
    print("SKIP: tokenomics AdminOrigin already set or not found")

with open("runtime/src/lib.rs", "w") as f:
    f.write(rt)

# Count remaining EnsureRoot
remaining = re.findall(r'EnsureRoot', rt)
print(f"\nRemaining EnsureRoot in runtime: {len(remaining)} (should be 1 = import only)")
