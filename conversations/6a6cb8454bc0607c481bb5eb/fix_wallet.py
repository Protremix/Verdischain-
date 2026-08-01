import re

# Fix VerdisApi.kt - ensure IDO methods are inside companion object
with open("/opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/VerdisApi.kt", "r") as f:
    content = f.read()

# Find the companion object and check if IDO methods are inside it
# The companion object starts at "companion object {" and we need to find its closing brace
# Strategy: find the "Instance method wrappers" section and ensure IDO methods are before it but inside companion

# Check if getIdoInfo is already in companion object
if "suspend fun getIdoInfo()" in content and "Companion.getIdoInfo()" not in content:
    # The methods exist but may be outside companion object
    # Find the closing of companion object (look for the pattern: }\n\n    // Instance method)
    
    # Remove any IDO methods that are outside the companion object
    # and re-add them inside
    
    # First, remove the existing IDO methods
    content = re.sub(
        r'\n\s*suspend fun getIdoInfo\(\).*?\}\n',
        '\n',
        content,
        flags=re.DOTALL
    )
    content = re.sub(
        r'\n\s*suspend fun purchaseIdoTokens\(.*?\}\n',
        '\n',
        content,
        flags=re.DOTALL
    )
    
    # Now add them right before the "Instance method wrappers" line (which is inside companion)
    ido_methods = """
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
    
    content = content.replace(
        "    // Instance method wrappers",
        ido_methods + "    // Instance method wrappers"
    )
    
    # Add instance wrappers for IDO
    content = content.replace(
        "suspend fun getBalance(address: String): BalanceResponse = Companion.getBalance(address)",
        "suspend fun getBalance(address: String): BalanceResponse = Companion.getBalance(address)\n    suspend fun getIdoInfo(): IdoInfo? = Companion.getIdoInfo()\n    suspend fun purchaseIdoTokens(address: String, amountVCO: Double): IdoPurchaseResult? = Companion.purchaseIdoTokens(address, amountVCO)"
    )

with open("/opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/VerdisApi.kt", "w") as f:
    f.write(content)
print("VerdisApi.kt fixed - IDO methods in companion object")

# Fix IdoFragment.kt
with open("/opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/IdoFragment.kt", "r") as f:
    content = f.read()

# Fix getBalance to use BalanceResponse
content = content.replace(
    "val balance = withContext(Dispatchers.IO) { VerdisApi.getBalance(wallet.address) }",
    "val balanceResp = withContext(Dispatchers.IO) { VerdisApi.getBalance(wallet.address) }\n                        val balance = balanceResp.balance"
)

# Fix locale formatting
content = content.replace(
    "info.sold.toLong().toLocaleString()",
    'String.format("%,d", info.sold.toLong())'
)
content = content.replace(
    "info.remaining.toLong().toLocaleString()",
    'String.format("%,d", info.remaining.toLong())'
)

with open("/opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/IdoFragment.kt", "w") as f:
    f.write(content)
print("IdoFragment.kt fixed")
