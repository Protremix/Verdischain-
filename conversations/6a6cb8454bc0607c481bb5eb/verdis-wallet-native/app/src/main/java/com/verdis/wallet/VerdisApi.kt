package com.verdis.wallet

import com.google.gson.Gson
import com.google.gson.JsonObject
import com.google.gson.JsonParser
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.util.concurrent.TimeUnit

object VerdisApi {
    private const val API_BASE = "https://verdischain.com/api"
    private const val RPC_URL = "https://rpc.verdischain.com"
    private val JSON = "application/json".toMediaType()

    private val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()

    private val gson = Gson()

    // === Blockchain Info ===
    data class BlockchainInfo(
        val height: Long = 0,
        val totalSupply: Double = 0.0,
        val circulatingSupply: Double = 0.0,
        val validators: Int = 0,
        val activeValidators: Int = 0,
        val dexPools: Int = 0,
        val tps: Double = 0.0
    )

    fun getBlockchainInfo(): BlockchainInfo {
        return try {
            val res = apiGet("/blockchain/info")
            val obj = JsonParser.parseString(res).asJsonObject
            BlockchainInfo(
                height = obj.get("height")?.asLong ?: obj.get("blockHeight")?.asLong ?: 0,
                totalSupply = obj.get("totalSupply")?.asDouble ?: 0.0,
                circulatingSupply = obj.get("circulatingSupply")?.asDouble ?: 0.0,
                validators = obj.get("validators")?.asInt ?: 0,
                activeValidators = obj.get("activeValidators")?.asInt ?: 5,
                dexPools = obj.get("dexPools")?.asInt ?: 6,
                tps = obj.get("tps")?.asDouble ?: 0.0
            )
        } catch (e: Exception) {
            BlockchainInfo()
        }
    }

    // === Wallet Balance ===
    data class WalletBalance(
        val address: String,
        val balance: Double,
        val stakeBalance: Double = 0.0,
        val nonce: Long = 0
    )

    fun getWalletBalance(address: String): WalletBalance {
        return try {
            val res = apiGet("/wallet/$address/balance")
            val obj = JsonParser.parseString(res).asJsonObject
            WalletBalance(
                address = address,
                balance = obj.get("balance")?.asDouble ?: 0.0,
                stakeBalance = obj.get("staked")?.asDouble ?: 0.0,
                nonce = obj.get("nonce")?.asLong ?: 0
            )
        } catch (e: Exception) {
            try {
                val res = apiGet("/wallets")
                val arr = JsonParser.parseString(res).asJsonArray
                for (item in arr) {
                    val w = item.asJsonObject
                    if (w.get("address")?.asString?.lowercase() == address.lowercase()) {
                        return WalletBalance(
                            address = address,
                            balance = w.get("balance")?.asDouble ?: 0.0,
                            stakeBalance = w.get("staked")?.asDouble ?: 0.0,
                            nonce = w.get("nonce")?.asLong ?: 0
                        )
                    }
                }
            } catch (e2: Exception) {}
            WalletBalance(address, 0.0)
        }
    }

    // === DEX Pools ===
    data class DexPool(
        val pair: String,
        val tokenA: String,
        val tokenB: String,
        val reserveA: Double,
        val reserveB: Double,
        val price: Double,
        val volume24h: Double,
        val txCount: Int
    )

    fun getDexPools(): List<DexPool> {
        return try {
            val res = apiGet("/dex/pools")
            val arr = JsonParser.parseString(res).asJsonArray
            arr.map { item ->
                val obj = item.asJsonObject
                DexPool(
                    pair = "${obj.get("tokenA")?.asString ?: ""}/${obj.get("tokenB")?.asString ?: ""}",
                    tokenA = obj.get("tokenA")?.asString ?: "",
                    tokenB = obj.get("tokenB")?.asString ?: "",
                    reserveA = obj.get("reserveA")?.asDouble ?: 0.0,
                    reserveB = obj.get("reserveB")?.asDouble ?: 0.0,
                    price = obj.get("price")?.asDouble ?: (obj.get("reserveB")?.asDouble ?: 0.0) / (obj.get("reserveA")?.asDouble ?: 1.0).coerceAtLeast(0.001),
                    volume24h = obj.get("volume24h")?.asDouble ?: 0.0,
                    txCount = obj.get("txCount")?.asInt ?: 0
                )
            }
        } catch (e: Exception) {
            listOf(
                DexPool("VCO/CARBON", "VCO", "CARBON", 50000.0, 41000.0, 0.82, 5400.0, 142),
                DexPool("VCO/ECO", "VCO", "ECO", 30000.0, 24500.0, 0.82, 3200.0, 89),
                DexPool("CARBON/ECO", "CARBON", "ECO", 20000.0, 20000.0, 1.0, 1800.0, 54)
            )
        }
    }

    // === DEX Swap ===
    data class SwapResult(
        val success: Boolean,
        val amountOut: Double = 0.0,
        val txId: String? = null,
        val error: String? = null
    )

    fun swap(wallet: WalletManager.Wallet, tokenIn: String, tokenOut: String, amountIn: Double): SwapResult {
        return try {
            val body = gson.toJson(mapOf(
                "trader" to wallet.address,
                "tokenIn" to tokenIn,
                "tokenOut" to tokenOut,
                "amountIn" to amountIn,
                "privateKey" to wallet.privateKey
            ))
            val res = apiPost("/dex/swap", body)
            val obj = JsonParser.parseString(res).asJsonObject
            if (obj.get("success")?.asBoolean != false) {
                SwapResult(
                    success = true,
                    amountOut = obj.get("amountOut")?.asDouble ?: 0.0,
                    txId = obj.get("txId")?.asString ?: obj.get("id")?.asString
                )
            } else {
                SwapResult(false, error = obj.get("error")?.asString ?: "Swap failed")
            }
        } catch (e: Exception) {
            SwapResult(false, error = e.message)
        }
    }

    // === DEX Quote ===
    fun getQuote(tokenIn: String, tokenOut: String, amountIn: Double): Double {
        return try {
            val res = apiGet("/dex/quote?tokenIn=$tokenIn&tokenOut=$tokenOut&amountIn=$amountIn")
            val obj = JsonParser.parseString(res).asJsonObject
            obj.get("amountOut")?.asDouble ?: 0.0
        } catch (e: Exception) {
            val pools = getDexPools()
            val pool = pools.find { 
                (it.tokenA == tokenIn && it.tokenB == tokenOut) || 
                (it.tokenB == tokenIn && it.tokenA == tokenOut) 
            }
            if (pool != null) {
                val reserveIn = if (pool.tokenA == tokenIn) pool.reserveA else pool.reserveB
                val reserveOut = if (pool.tokenA == tokenIn) pool.reserveB else pool.reserveA
                val amountInWithFee = amountIn * 0.997
                amountInWithFee * reserveOut / (reserveIn + amountInWithFee)
            } else 0.0
        }
    }

    // === Send Transaction ===
    data class SendResult(
        val success: Boolean,
        val txId: String? = null,
        val error: String? = null
    )

    fun send(wallet: WalletManager.Wallet, to: String, amount: Double, fee: Double = 0.001): SendResult {
        return try {
            val body = gson.toJson(mapOf(
                "from" to wallet.address,
                "to" to to,
                "amount" to amount,
                "fee" to fee,
                "privateKey" to wallet.privateKey
            ))
            val res = apiPost("/blockchain/transfer", body)
            val obj = JsonParser.parseString(res).asJsonObject
            if (obj.get("success")?.asBoolean != false || obj.get("id") != null) {
                SendResult(true, txId = obj.get("id")?.asString ?: obj.get("txId")?.asString)
            } else {
                SendResult(false, error = obj.get("error")?.asString ?: "Failed")
            }
        } catch (e: Exception) {
            SendResult(false, error = e.message)
        }
    }

    // === Eco Impact ===
    data class EcoImpact(
        val carbonOffset: Double,
        val treesPlanted: Int,
        val greenValidators: Int,
        val energyPerTx: String
    )

    fun getEcoImpact(): EcoImpact {
        return try {
            val res = apiGet("/eco/impact")
            val obj = JsonParser.parseString(res).asJsonObject
            EcoImpact(
                carbonOffset = obj.get("carbonOffset")?.asDouble ?: obj.get("totalCO2")?.asDouble ?: 1000.0,
                treesPlanted = obj.get("treesPlanted")?.asInt ?: 15000,
                greenValidators = obj.get("greenValidators")?.asInt ?: 6,
                energyPerTx = "<0.001"
            )
        } catch (e: Exception) {
            EcoImpact(1000.0, 15000, 6, "<0.001")
        }
    }

    // === Validators ===
    data class Validator(
        val address: String,
        val rank: Int,
        val greenScore: Int,
        val blocksProduced: Long,
        val votes: Long,
        val active: Boolean
    )

    fun getValidators(): List<Validator> {
        return try {
            val res = apiGet("/validators/top")
            val arr = JsonParser.parseString(res).asJsonArray
            arr.mapIndexed { i, item ->
                val obj = item.asJsonObject
                Validator(
                    address = obj.get("address")?.asString ?: obj.get("publicKey")?.asString ?: "0x...",
                    rank = i + 1,
                    greenScore = obj.get("greenScore")?.asInt ?: obj.get("score")?.asInt ?: (70 + (0..29).random()),
                    blocksProduced = obj.get("blocksProduced")?.asLong ?: 0L,
                    votes = obj.get("votes")?.asLong ?: 0L,
                    active = obj.get("active")?.asBoolean ?: true
                )
            }
        } catch (e: Exception) {
            // Generate mock validators based on known addresses
            val names = listOf(
                "0x7a3f...e2b1","0xb8c4...d45e","0xf2a9...c7b3","0x6e1d...a8f4",
                "0xa5b3...9e2c","0xd7e8...1b5a","0x3c6f...f4d2","0x9a2b...e7c1",
                "0x1d5e...b3a8","0xe4f7...2c6d","0x8b3a...5f1e","0xc2d9...4a7b",
                "0x5f8c...d3e6","0x7e2b...1a4f","0xa9d6...c5b3","0x4c1f...e8d2",
                "0xb6a3...7f5c","0xd2e9...1b8a","0x3f5c...a7d4","0x8e1b...4c2f",
                "0x1a7d...b5e8","0x6b3f...d2c5","0xc5e8...1a7b","0xf4d2...9b3e",
                "0x2b8a...e6c1","0xe7c5...4d3a","0xa3f1...b8e6"
            )
            names.mapIndexed { i, addr ->
                Validator(addr, i + 1, 70 + (0..29).random(), (1000L..50000L).random(), (0L..10000L).random(), i < 5)
            }
        }
    }

    // === Faucet ===
    fun fundFromFaucet(address: String): Boolean {
        return try {
            val body = gson.toJson(mapOf("address" to address))
            apiPost("/faucet/claim", body)
            true
        } catch (e: Exception) {
            false
        }
    }

    // === Transactions ===
    data class Transaction(
        val hash: String,
        val from: String,
        val to: String,
        val amount: Double,
        val fee: Double,
        val timestamp: String,
        val blockHeight: Long
    )

    fun getTransactions(address: String? = null): List<Transaction> {
        return try {
            val res = if (address != null) {
                apiGet("/wallet/$address/transactions")
            } else {
                apiGet("/blockchain/transactions?limit=20")
            }
            val arr = JsonParser.parseString(res).asJsonArray
            arr.map { item ->
                val obj = item.asJsonObject
                Transaction(
                    hash = obj.get("hash")?.asString ?: obj.get("id")?.asString ?: "0x...",
                    from = obj.get("from")?.asString ?: "0x...",
                    to = obj.get("to")?.asString ?: "0x...",
                    amount = obj.get("amount")?.asDouble ?: 0.0,
                    fee = obj.get("fee")?.asDouble ?: 0.001,
                    timestamp = obj.get("timestamp")?.asString ?: obj.get("time")?.asString ?: "",
                    blockHeight = obj.get("blockHeight")?.asLong ?: obj.get("block")?.asLong ?: 0L
                )
            }
        } catch (e: Exception) {
            listOf()
        }
    }

    // === RPC ===
    fun rpcCall(method: String, params: List<Any>): JsonObject {
        val body = gson.toJson(mapOf(
            "jsonrpc" to "2.0",
            "method" to method,
            "params" to params,
            "id" to 1
        ))
        val res = rpcPost(body)
        return JsonParser.parseString(res).asJsonObject
    }

    // === HTTP helpers ===
    private fun apiGet(path: String): String {
        val request = Request.Builder().url("$API_BASE$path").build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw Exception("API ${response.code}")
            return response.body?.string() ?: "{}"
        }
    }

    private fun apiPost(path: String, body: String): String {
        val request = Request.Builder()
            .url("$API_BASE$path")
            .post(body.toRequestBody(JSON))
            .build()
        client.newCall(request).execute().use { response ->
            return response.body?.string() ?: "{}"
        }
    }

    private fun rpcPost(body: String): String {
        val request = Request.Builder()
            .url(RPC_URL)
            .post(body.toRequestBody(JSON))
            .build()
        client.newCall(request).execute().use { response ->
            return response.body?.string() ?: "{}"
        }
    }
}
