// Add these data classes and methods to VerdisApi.kt

data class IdoInfo(
    val priceUSD: Double = 0.001,
    val totalAllocation: Double = 0.0,
    val sold: Double = 0.0,
    val remaining: Double = 0.0,
    val progressPct: Double = 0.0,
    val purchasers: Int = 0,
    val minPurchase: Double = 100.0,
    val maxPurchase: Double = 1000000.0,
    val active: Boolean = true,
    val acceptedPayments: List<String> = emptyList(),
    val tokenSymbol: String = "VCO",
    val tokenName: String = "Verdis Coin",
    val chainId: Int = 909
)

data class IdoPurchaseResult(
    val success: Boolean = false,
    val txId: String? = null,
    val address: String = "",
    val amountVCO: Double = 0.0,
    val priceUSD: Double = 0.0,
    val totalCostUSD: String = "",
    val newBalance: Double = 0.0,
    val remaining: Double = 0.0,
    val error: String? = null
)

// Companion object methods:
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

        suspend fun getBalance(address: String): Double = withContext(Dispatchers.IO) {
            try {
                val response = executeGet("/api/wallet/$address/balance")
                val obj = gson.fromJson(response, BalanceResponse::class.java)
                obj.balance
            } catch (e: Exception) { 0.0 }
        }
