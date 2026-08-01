
# Remove duplicate IDO methods that are outside companion object and after instance wrappers
with open("/opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/VerdisApi.kt", "r") as f:
    content = f.read()

# Remove the duplicate block - the full IDO method implementations that appear after the swap wrapper
# These start with "        suspend fun getIdoInfo(): IdoInfo? = withContext" and end before the final "}"
import re

# Find and remove the duplicate IDO methods that are OUTSIDE the companion object
# Pattern: these appear after "suspend fun swap(wallet: WalletManager.Wallet" wrapper
# and before the final class closing "}"

# The duplicate block to remove
duplicate_block = """
        suspend fun getIdoInfo(): IdoInfo? = withContext(Dispatchers.IO) {
            try {
                val response = executeGet("/api/ido/info")
                gson.fromJson(response, IdoInfo::class.java)
            } catch (e: Exception) { null }
        }

        suspend fun purchaseIdoTokens(address: String, amountVCO: Double): IdoPurchaseResult? = withContext(Dispatchers.IO) {
            try {
                val body = gson.toJson(mapOf(
                    "address" to address,
                    "amountVCO" to amountVCO.toString()
                ))
                val response = executePost("/api/ido/purchase", body)
                gson.fromJson(response, IdoPurchaseResult::class.java)
            } catch (e: Exception) { null }
        }
"""

# Only remove the LAST occurrence (the duplicate outside companion object)
# Find all occurrences
occurrences = [m.start() for m in re.finditer(re.escape(duplicate_block.strip()), content)]
print(f"Found {len(occurrences)} occurrences of the IDO methods")

if len(occurrences) > 1:
    # Remove the last occurrence (the duplicate)
    last_start = occurrences[-1]
    # Find the exact text to remove (including surrounding whitespace)
    block_end = last_start + len(duplicate_block)
    # Also remove any trailing newlines
    while block_end < len(content) and content[block_end] == '\n':
        block_end += 1
    
    content = content[:last_start] + content[block_end:]
    print("Removed duplicate IDO methods")

# Also clean up any double blank lines
content = re.sub(r'\n\n\n\n+', '\n\n\n', content)

with open("/opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/VerdisApi.kt", "w") as f:
    f.write(content)

print("VerdisApi.kt cleaned - duplicates removed")
