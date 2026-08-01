
# Fix the mangled VerdisApi.kt
with open("/opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/VerdisApi.kt", "r") as f:
    lines = f.readlines()

# Find the swap function's closing brace
# Then fix the companion object closing
# Then remove leftover IDO references

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Skip the extra closing braces between swap close and Instance method wrappers
    # The pattern is: after "return executeSwap(...)" and "}" (swap close), 
    # there should be exactly one "}" for companion close, then blank line, then "    // Instance method"
    
    if "return executeSwap" in line:
        new_lines.append(line)
        i += 1
        # Next line should be "        }" (swap function close)
        if i < len(lines) and lines[i].strip() == "}":
            new_lines.append(lines[i])  # swap close
            i += 1
        # Skip any extra "}" lines until we hit the Instance method wrappers comment
        # But we need exactly one "    }" for the companion object close
        found_comp_close = False
        while i < len(lines) and "Instance method" not in lines[i]:
            if lines[i].strip() == "}" and not found_comp_close:
                # This is the companion object close
                new_lines.append("    }\n")
                found_comp_close = True
            i += 1
        # Add a blank line before Instance method wrappers
        new_lines.append("\n")
        continue
    
    # Remove leftover IDO references on instance wrapper lines
    if "purchaseIdoTokens" in line and "Companion" in line:
        # Remove this line - no longer needed
        i += 1
        continue
    
    if "getIdoInfo" in line and "Companion" in line:
        i += 1
        continue
    
    # Also remove any leftover IdoInfo or IdoPurchaseResult references
    if "IdoInfo" in line or "IdoPurchaseResult" in line:
        # Skip this line
        i += 1
        continue
    
    new_lines.append(line)
    i += 1

# Also remove the data class definitions if they still exist
content = "".join(new_lines)
import re
content = re.sub(r'\ndata class IdoInfo\(.*?\n\n', '', content, flags=re.DOTALL)
content = re.sub(r'\ndata class IdoPurchaseResult\(.*?\n\n', '', content, flags=re.DOTALL)

# Clean up multiple consecutive blank lines
content = re.sub(r'\n\n\n\n+', '\n\n', content)

# Fix the getBalance line that got merged with purchaseIdoTokens
content = content.replace(
    "suspend fun getBalance(address: String): BalanceResponse = Companion.getBalance(address)    ",
    "suspend fun getBalance(address: String): BalanceResponse = Companion.getBalance(address)\n    "
)

with open("/opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/VerdisApi.kt", "w") as f:
    f.write(content)

print("VerdisApi.kt fixed")
