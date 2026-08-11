package com.verdis.verdis_wallet

import android.util.Base64
import android.util.Log
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity: FlutterActivity() {
    private val CHANNEL = "com.verdis.verdis_wallet/sr25519"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)

        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            when (call.method) {
                "deriveAddress" -> {
                    val seedBase64 = call.argument<String>("seed")
                    if (seedBase64 == null) {
                        result.error("INVALID", "Missing seed parameter", null)
                        return@setMethodCallHandler
                    }
                    try {
                        val seed = Base64.decode(seedBase64, Base64.NO_WRAP)
                        if (seed.size != 32) {
                            result.error("INVALID", "Seed must be 32 bytes, got ${seed.size}", null)
                            return@setMethodCallHandler
                        }
                        val publicKey = Sr25519Service.derivePublicKey(seed)
                        if (publicKey == null) {
                            result.error("DERIVE_FAILED", "Failed to derive public key", null)
                            return@setMethodCallHandler
                        }
                        val address = Sr25519Service.encodeSs58(publicKey)
                        result.success(address)
                    } catch (e: Exception) {
                        Log.e("MainActivity", "deriveAddress error", e)
                        result.error("ERROR", e.message, null)
                    }
                }

                "signPayload" -> {
                    val seedBase64 = call.argument<String>("seed")
                    val payloadBase64 = call.argument<String>("payload")
                    if (seedBase64 == null || payloadBase64 == null) {
                        result.error("INVALID", "Missing seed or payload", null)
                        return@setMethodCallHandler
                    }
                    try {
                        val seed = Base64.decode(seedBase64, Base64.NO_WRAP)
                        val payload = Base64.decode(payloadBase64, Base64.NO_WRAP)
                        val signature = Sr25519Service.signMessage(seed, payload)
                        if (signature == null) {
                            result.error("SIGN_FAILED", "Failed to sign payload", null)
                            return@setMethodCallHandler
                        }
                        result.success(Base64.encodeToString(signature, Base64.NO_WRAP))
                    } catch (e: Exception) {
                        Log.e("MainActivity", "signPayload error", e)
                        result.error("ERROR", e.message, null)
                    }
                }

                "mnemonicToSeed" -> {
                    val mnemonic = call.argument<String>("mnemonic")
                    if (mnemonic == null) {
                        result.error("INVALID", "Missing mnemonic", null)
                        return@setMethodCallHandler
                    }
                    try {
                        val seed = Sr25519Service.mnemonicToSeed(mnemonic)
                        result.success(Base64.encodeToString(seed, Base64.NO_WRAP))
                    } catch (e: Exception) {
                        Log.e("MainActivity", "mnemonicToSeed error", e)
                        result.error("ERROR", e.message, null)
                    }
                }

                "validateAddress" -> {
                    val address = call.argument<String>("address")
                    if (address == null) {
                        result.error("INVALID", "Missing address", null)
                        return@setMethodCallHandler
                    }
                    try {
                        val publicKey = Sr25519Service.decodeSs58(address)
                        result.success(publicKey != null)
                    } catch (e: Exception) {
                        result.success(false)
                    }
                }

                else -> result.notImplemented()
            }
        }
    }
}
