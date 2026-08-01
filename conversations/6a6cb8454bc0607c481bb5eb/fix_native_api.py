#!/usr/bin/env python3
"""Fix the native wallet's sendTransaction and swap functions to use correct API endpoints"""

import re

# Fix VerdisApi.kt
api_path = "/opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/VerdisApi.kt"
with open(api_path) as f:
    api = f.read()

# 1. Fix sendTransaction to use /api/transaction/send with privateKey
old_send = '''        suspend fun sendTransaction(
            from: String,
            to: String,
            amount: Double,
            fee: Double,
            nonce: Long,
            signature: String,
            publicKey: String
        ): TransactionResult = withContext(Dispatchers.IO) {
            try {
                // Build full transaction object with ID (sha256 of payload)
                val payload = "$from:$to:$amount:$fee:$nonce:"
                val txId = CryptoUtils.sha256Hex(payload)
                val bodyMap = mapOf(
                    "id" to txId,
                    "from" to from,
                    "to" to to,
                    "amount" to amount,
                    "fee" to fee,
                    "nonce" to nonce,
                    "timestamp" to System.currentTimeMillis(),
                    "data" to "",
                    "signature" to signature,
                    "publicKey" to publicKey
                )
                val jsonBody = gson.toJson(bodyMap)
                val jsonResp = executePost("/api/transaction/submit", jsonBody)
                if (jsonResp.isNotEmpty()) {
                    val obj = JsonParser.parseString(jsonResp).asJsonObject
                    TransactionResult(
                        success = obj.get("success")?.asBoolean ?: (obj.get("id") != null || obj.get("txId") != null || obj.get("hash") != null),
                        txId = obj.get("txId")?.asString ?: obj.get("id")?.asString ?: obj.get("hash")?.asString,
                        hash = obj.get("hash")?.asString ?: obj.get("txId")?.asString ?: obj.get("id")?.asString,
                        blockNumber = obj.get("blockNumber")?.asLong ?: obj.get("block")?.asLong ?: 0L,
                        error = if (obj.has("error")) obj.get("error").asString else null
                    )'''

new_send = '''        suspend fun sendTransaction(
            from: String,
            to: String,
            amount: Double,
            fee: Double,
            nonce: Long,
            privateKey: String,
            publicKey: String
        ): TransactionResult = withContext(Dispatchers.IO) {
            try {
                val bodyMap = mapOf(
                    "from" to from,
                    "privateKey" to privateKey,
                    "to" to to,
                    "amount" to amount,
                    "fee" to fee,
                    "data" to ""
                )
                val jsonBody = gson.toJson(bodyMap)
                val jsonResp = executePost("/api/transaction/send", jsonBody)
                if (jsonResp.isNotEmpty()) {
                    val obj = JsonParser.parseString(jsonResp).asJsonObject
                    TransactionResult(
                        success = obj.get("txId") != null || obj.get("success")?.asBoolean == true,
                        txId = obj.get("txId")?.asString ?: obj.get("id")?.asString ?: obj.get("hash")?.asString,
                        hash = obj.get("txId")?.asString ?: obj.get("hash")?.asString,
                        blockNumber = obj.get("blockNumber")?.asLong ?: 0L,
                        error = if (obj.has("error")) obj.get("error").asString else null
                    )'''

if old_send in api:
    api = api.replace(old_send, new_send, 1)
    print("1. Fixed sendTransaction endpoint (submit → send, signature → privateKey)")
else:
    print("1. ERROR: sendTransaction not found")

# 2. Fix the wrapper sendTransaction in the instance class
old_wrapper = '''    suspend fun sendTransaction(
        from: String, to: String, amount: Double, fee: Double, nonce: Long, signature: String, publicKey: String
    ): TransactionResult = Companion.sendTransaction(from, to, amount, fee, nonce, signature, publicKey)'''

new_wrapper = '''    suspend fun sendTransaction(
        from: String, to: String, amount: Double, fee: Double, nonce: Long, privateKey: String, publicKey: String
    ): TransactionResult = Companion.sendTransaction(from, to, amount, fee, nonce, privateKey, publicKey)'''

if old_wrapper in api:
    api = api.replace(old_wrapper, new_wrapper, 1)
    print("2. Fixed sendTransaction wrapper")
else:
    print("2. ERROR: wrapper not found")

with open(api_path, "w") as f:
    f.write(api)

# Fix SendFragment.kt
send_path = "/opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/SendFragment.kt"
with open(send_path) as f:
    send = f.read()

old_send_call = '''                    val nonce = details?.nonce?.toLong() ?: 0L
                    val fee = 0.001
                    val signature = WalletManager.signTransaction(wallet, to, amount, fee, nonce)

                    val result = withContext(Dispatchers.IO) {
                        VerdisApi.sendTransaction(
                            wallet.address, to, amount, fee, nonce, signature, wallet.publicKey
                        )
                    }'''

new_send_call = '''                    val nonce = details?.nonce?.toLong() ?: 0L
                    val fee = 1.0
                    val result = withContext(Dispatchers.IO) {
                        VerdisApi.sendTransaction(
                            wallet.address, to, amount, fee, nonce, wallet.privateKey, wallet.publicKey
                        )
                    }'''

if old_send_call in send:
    send = send.replace(old_send_call, new_send_call, 1)
    print("3. Fixed SendFragment to pass privateKey and use fee=1.0")
else:
    print("3. ERROR: SendFragment send call not found")

with open(send_path, "w") as f:
    f.write(send)

print("\nAll API fixes applied!")
