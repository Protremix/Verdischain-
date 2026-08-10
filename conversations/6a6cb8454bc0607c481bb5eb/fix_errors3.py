import re

# Fix presale: remove the accidental price_precision function parameter
with open("/opt/verdis-chain-rust/pallets/presale/src/lib.rs", "r") as f:
    content = f.read()

# Remove the line from the function signature
content = content.replace(
    "            token_price: BalanceOf<T>,\n            price_precision: 1u32.into(),\n            total_allocation: BalanceOf<T>,",
    "            token_price: BalanceOf<T>,\n            total_allocation: BalanceOf<T>,"
)

# Now make sure the struct constructions still have price_precision
# Check construction 1 (create_round internal)
if "price_precision: 1u32.into()," in content:
    # These are in struct constructions - keep them
    pass
else:
    # Need to add back to struct constructions
    content = content.replace(
        "                    token_price: *price,\n                    total_allocation:",
        "                    token_price: *price,\n                    price_precision: 1u32.into(),\n                    total_allocation:"
    )
    content = content.replace(
        "                token_price,\n                total_allocation:",
        "                token_price,\n                price_precision: 1u32.into(),\n                total_allocation:"
    )

# Actually, the 1u32.into() in struct construction might also fail
# Let's use a different approach - use From trait explicitly
content = content.replace(
    "price_precision: 1u32.into(),",
    "price_precision: <BalanceOf<T> as From<u32>>::from(1u32),"
)

with open("/opt/verdis-chain-rust/pallets/presale/src/lib.rs", "w") as f:
    f.write(content)
print("Presale: function parameter removed, struct construction fixed")

# Fix vesting: add Underflow error variant and remove duplicate WithdrawReasons import
with open("/opt/verdis-chain-rust/pallets/vesting/src/lib.rs", "r") as f:
    content = f.read()

# Add Underflow error if missing
if "Underflow" not in content.split("pub enum Error")[1].split("}")[0]:
    # Find the error enum and add Underflow
    content = content.replace(
        "Overflow,",
        "Overflow,\n        Underflow,"
    )

# Fix duplicate WithdrawReasons import
# Count occurrences
import_count = content.count("use frame_support::traits::WithdrawReasons;")
if import_count > 1:
    # Remove duplicates - keep only the first
    first = content.find("use frame_support::traits::WithdrawReasons;")
    if first >= 0:
        content = content[:first + len("use frame_support::traits::WithdrawReasons;")] + \
                  content[content.find("use frame_support::traits::WithdrawReasons;", first + 1):].replace(
                      "use frame_support::traits::WithdrawReasons;\n", "", 1
                  )

# Also check if WithdrawReasons is in a combined import
if content.count("WithdrawReasons") > 1:
    # Remove duplicate from combined imports
    lines = content.split("\n")
    seen_withdraw = False
    new_lines = []
    for line in lines:
        if "WithdrawReasons" in line:
            if seen_withdraw:
                # This is a duplicate - remove it
                if "use frame_support::traits::WithdrawReasons;" in line:
                    continue
                elif "WithdrawReasons" in line and "use" in line and "{" in line:
                    # It's in a combined import - remove just the WithdrawReasons part
                    line = line.replace(", WithdrawReasons", "").replace("WithdrawReasons, ", "").replace("WithdrawReasons", "")
                    if line.strip() == "use frame_support::traits::{};" or line.strip() == "use frame_support::traits::{ };":
                        continue
            else:
                seen_withdraw = True
        new_lines.append(line)
    content = "\n".join(new_lines)

with open("/opt/verdis-chain-rust/pallets/vesting/src/lib.rs", "w") as f:
    f.write(content)
print("Vesting: Underflow error added, duplicate imports fixed")
