#!/usr/bin/env python3
"""Fix eco + tokenomics test mock Configs to add AdminOrigin."""

# === Fix eco test mock ===
with open("pallets/eco/src/lib.rs") as f:
    eco = f.read()

# The eco test mock Config impl needs AdminOrigin
# Find the test Config impl and add AdminOrigin
old_eco_test_cfg = """    impl Config for Test {
        type RuntimeEvent = RuntimeEvent;
        type PalletId = EcoPalletId;
        type MaxCarbonCredits = MaxCarbonCredits;
        type MaxReforestProjects = MaxReforestProjects;
        type MaxGreenValidators = MaxGreenValidators;
        type MinGreenScore = MinGreenScore;
        type MaxGreenScore = MaxGreenScore;
        type WeightInfo = SubstrateWeight<Test>;
    }"""

new_eco_test_cfg = """    impl Config for Test {
        type RuntimeEvent = RuntimeEvent;
        type PalletId = EcoPalletId;
        type MaxCarbonCredits = MaxCarbonCredits;
        type MaxReforestProjects = MaxReforestProjects;
        type MaxGreenValidators = MaxGreenValidators;
        type MinGreenScore = MinGreenScore;
        type MaxGreenScore = MaxGreenScore;
        type WeightInfo = SubstrateWeight<Test>;
        type AdminOrigin = frame_system::EnsureRoot<Self::AccountId>;
    }"""

if old_eco_test_cfg in eco:
    eco = eco.replace(old_eco_test_cfg, new_eco_test_cfg)
    print("ECO: Added AdminOrigin to test mock Config")
else:
    print("SKIP: eco test Config not found")

with open("pallets/eco/src/lib.rs", "w") as f:
    f.write(eco)

# === Fix tokenomics test mock ===
with open("pallets/tokenomics/src/lib.rs") as f:
    tok = f.read()

old_tok_test_cfg = """    impl Config for Test {
        type MaxPriorityFeeMultiplier = ConstU32<1000>;
        type DefaultTransferFeeBps = ConstU32<50>;
        type GreenTreasury = TestGreenTreasury;
        type RuntimeEvent = RuntimeEvent;
        type Currency = Balances;
        type TotalSupply = TotalSupply;
        type InvestorAllocation = InvestorAllocation;
        type PalletId = TokPalletId;
        type WeightInfo = SubstrateWeight<Test>;
    }"""

new_tok_test_cfg = """    impl Config for Test {
        type MaxPriorityFeeMultiplier = ConstU32<1000>;
        type DefaultTransferFeeBps = ConstU32<50>;
        type GreenTreasury = TestGreenTreasury;
        type RuntimeEvent = RuntimeEvent;
        type Currency = Balances;
        type TotalSupply = TotalSupply;
        type InvestorAllocation = InvestorAllocation;
        type PalletId = TokPalletId;
        type WeightInfo = SubstrateWeight<Test>;
        type AdminOrigin = frame_system::EnsureRoot<Self::AccountId>;
    }"""

if old_tok_test_cfg in tok:
    tok = tok.replace(old_tok_test_cfg, new_tok_test_cfg)
    print("TOKENOMICS: Added AdminOrigin to test mock Config")
else:
    print("SKIP: tokenomics test Config not found")

with open("pallets/tokenomics/src/lib.rs", "w") as f:
    f.write(tok)
