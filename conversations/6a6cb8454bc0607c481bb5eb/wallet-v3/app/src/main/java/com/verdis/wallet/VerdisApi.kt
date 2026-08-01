package com.verdis.wallet

import com.google.gson.Gson
import com.google.gson.JsonParser
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.util.concurrent.TimeUnit

object VerdisApi {
    private const val BASE = "https://verdischain.com"
    private val JSON = "application/json; charset=utf-8".toMediaType()
    private val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    private val gson = Gson()

    private suspend fun get(path: String): String? = withContext(Dispatchers.IO) {
        try {
            val req = Request.Builder().url("$BASE$path").get().build()
            client.newCall(req).execute().use { if (it.isSuccessful) it.body?.string() else null }
        } catch (e: Exception) { null }
    }

    private suspend fun post(path: String, body: String): String? = withContext(Dispatchers.IO) {
        try {
            val req = Request.Builder().url("$BASE$path").post(body.toRequestBody(JSON)).build()
            client.newCall(req).execute().use { if (it.isSuccessful) it.body?.string() else null }
        } catch (e: Exception) { null }
    }

    suspend fun getBalance(addr: String): Double {
        val r = get("/api/wallet/$addr/balance") ?: return 0.0
        return try { JsonParser.parseString(r).asJsonObject.get("balance")?.asDouble ?: 0.0 } catch (e: Exception) { 0.0 }
    }

    suspend fun getTokenInfo(): Map<String, Any?> {
        val r = get("/api/token/info") ?: return emptyMap()
        return try { gson.fromJson(r, Map::class.java) as Map<String, Any?> } catch (e: Exception) { emptyMap() }
    }

    suspend fun getBlockchainInfo(): Map<String, Any?> {
        val r = get("/api/blockchain/info") ?: return emptyMap()
        return try { gson.fromJson(r, Map::class.java) as Map<String, Any?> } catch (e: Exception) { emptyMap() }
    }

    suspend fun getNetworkInfo(): Map<String, Any?> {
        val r = get("/api/network/info") ?: return emptyMap()
        return try { gson.fromJson(r, Map::class.java) as Map<String, Any?> } catch (e: Exception) { emptyMap() }
    }

    suspend fun getValidators(): List<Map<String, Any?>> {
        val r = get("/api/validators") ?: return emptyList()
        return try { gson.fromJson(r, List::class.java) as List<Map<String, Any?>> } catch (e: Exception) { emptyList() }
    }

    suspend fun getEcoImpact(): Map<String, Any?> {
        val r = get("/api/eco/impact") ?: return emptyMap()
        return try { gson.fromJson(r, Map::class.java) as Map<String, Any?> } catch (e: Exception) { emptyMap() }
    }

    suspend fun getDexPools(): List<Map<String, Any?>> {
        val r = get("/api/dex/pools") ?: return emptyList()
        return try { gson.fromJson(r, List::class.java) as List<Map<String, Any?>> } catch (e: Exception) { emptyList() }
    }

    suspend fun sendTransaction(from: String, to: String, amount: Double, fee: Double, privateKey: String, publicKey: String): Boolean {
        val body = gson.toJson(mapOf(
            "from" to from, "to" to to, "amount" to amount,
            "fee" to fee, "data" to "",
            "privateKey" to privateKey, "publicKey" to publicKey
        ))
        val r = post("/api/transaction/send", body) ?: return false
        return try {
            val obj = JsonParser.parseString(r).asJsonObject
            obj.get("txId") != null || obj.get("id") != null || obj.get("success")?.asBoolean == true
        } catch (e: Exception) { false }
    }

    suspend fun swap(trader: String, tokenIn: String, tokenOut: String, amountIn: Double): Boolean {
        val body = gson.toJson(mapOf("trader" to trader, "tokenIn" to tokenIn, "tokenOut" to tokenOut, "amountIn" to amountIn))
        val r = post("/api/dex/swap", body) ?: return false
        return try { JsonParser.parseString(r).asJsonObject.get("success")?.asBoolean ?: false } catch (e: Exception) { false }
    }

    suspend fun stake(address: String, amount: Double): Boolean {
        val body = gson.toJson(mapOf("address" to address, "amount" to amount, "action" to "stake"))
        val r = post("/api/stake", body) ?: return false
        return try { JsonParser.parseString(r).asJsonObject.get("success")?.asBoolean ?: false } catch (e: Exception) { false }
    }

    suspend fun unstake(address: String, amount: Double): Boolean {
        val body = gson.toJson(mapOf("address" to address, "amount" to amount, "action" to "unstake"))
        val r = post("/api/stake", body) ?: return false
        return try { JsonParser.parseString(r).asJsonObject.get("success")?.asBoolean ?: false } catch (e: Exception) { false }
    }

    suspend fun claimFaucet(address: String): Boolean {
        val body = gson.toJson(mapOf("address" to address))
        val r = post("/api/faucet/claim", body) ?: return false
        return try { JsonParser.parseString(r).asJsonObject.get("success")?.asBoolean ?: false } catch (e: Exception) { false }
    }

    suspend fun getTransactions(addr: String): List<Map<String, Any?>> {
        val r = get("/api/explorer/address/$addr") ?: return emptyList()
        return try {
            val obj = JsonParser.parseString(r).asJsonObject
            val txs = obj.get("transactions") ?: obj.get("txs")
            if (txs != null) gson.fromJson(txs, List::class.java) as List<Map<String, Any?>> else emptyList()
        } catch (e: Exception) { emptyList() }
    }
}
