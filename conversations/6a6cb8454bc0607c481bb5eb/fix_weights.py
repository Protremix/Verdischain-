import re

with open("/opt/verdis-chain/runtime/src/lib.rs", "r") as f:
    content = f.read()

# Fix 1: ChainContext needs Runtime generic
content = content.replace(
    "frame_system::ChainContext,",
    "frame_system::ChainContext<Runtime>,"
)

with open("/opt/verdis-chain/runtime/src/lib.rs", "w") as f:
    f.write(content)
print("Fixed ChainContext generics")

# Fix 2: Add WeightInfo impl for () in custom pallets
pallets = ["dpos", "eco", "tokenomics", "vesting", "storage"]

for pallet in pallets:
    lib_path = f"/opt/verdis-chain/pallets/{pallet}/src/lib.rs"
    try:
        with open(lib_path, "r") as f:
            pallet_content = f.read()
        
        # Check if WeightInfo trait is defined
        if "trait WeightInfo" in pallet_content:
            # Check if () impl already exists
            if "impl WeightInfo for ()" not in pallet_content:
                # Find all method signatures in the WeightInfo trait
                # Add a blanket impl for () that returns Weight::zero() or default weights
                # Add at the end of the file, before the last closing bracket or at module level
                
                # Find the WeightInfo trait definition to get method names
                trait_match = re.search(r'trait WeightInfo\s*\{([^}]+)\}', pallet_content)
                if trait_match:
                    trait_body = trait_match.group(1)
                    methods = re.findall(r'fn (\w+)\([^)]*\)\s*->\s*Weight', trait_body)
                    
                    impl_code = "\nimpl WeightInfo for () {\n"
                    for method in methods:
                        impl_code += f"    fn {method}() -> Weight {{ Weight::zero() }}\n"
                    impl_code += "}\n"
                    
                    # Add before the last closing bracket of the module or at end
                    pallet_content += impl_code
                else:
                    # Simple blanket impl
                    pallet_content += "\nimpl WeightInfo for () {}\n"
                
                with open(lib_path, "w") as f:
                    f.write(pallet_content)
                print(f"Added WeightInfo impl for () in pallet-{pallet}")
            else:
                print(f"pallet-{pallet} already has WeightInfo impl for ()")
        else:
            print(f"pallet-{pallet} has no WeightInfo trait")
    except FileNotFoundError:
        print(f"pallet-{pallet} lib.rs not found")

print("Done fixing WeightInfo")
