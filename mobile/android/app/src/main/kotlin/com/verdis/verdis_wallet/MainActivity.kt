package com.verdis.verdis_wallet

import android.webkit.WebView
import android.webkit.WebViewClient
import android.webkit.ValueCallback
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

class MainActivity: FlutterActivity() {
    private val CHANNEL = "com.verdis.verdis_wallet/crypto"
    private var webView: WebView? = null
    private var webViewReady = false

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            when (call.method) {
                "initWebView" -> {
                    initWebView()
                    result.success(true)
                }
                "deriveAddress" -> {
                    val mnemonic = call.argument<String>("mnemonic") ?: ""
                    if (!webViewReady) initWebView()
                    deriveAddress(mnemonic, result)
                }
                "generateMnemonic" -> {
                    if (!webViewReady) initWebView()
                    generateMnemonic(result)
                }
                "validateMnemonic" -> {
                    val mnemonic = call.argument<String>("mnemonic") ?: ""
                    if (!webViewReady) initWebView()
                    validateMnemonic(mnemonic, result)
                }
                "signTransfer" -> {
                    val mnemonic = call.argument<String>("mnemonic") ?: ""
                    val destAddress = call.argument<String>("destAddress") ?: ""
                    val amountAtoms = call.argument<Number>("amountAtoms")?.toLong() ?: 0L
                    val nonce = call.argument<Number>("nonce")?.toLong() ?: 0L
                    val genesisHash = call.argument<String>("genesisHash") ?: ""
                    val blockHash = call.argument<String>("blockHash") ?: ""
                    val specVersion = call.argument<Number>("specVersion")?.toInt() ?: 0
                    if (!webViewReady) initWebView()
                    signTransfer(mnemonic, destAddress, amountAtoms, nonce, genesisHash, blockHash, specVersion, result)
                }
                else -> result.notImplemented()
            }
        }
    }

    private fun initWebView() {
        runOnUiThread {
            webView = WebView(this@MainActivity).apply {
                settings.javaScriptEnabled = true
                settings.domStorageEnabled = true
                settings.allowFileAccess = true
                settings.allowFileAccessFromFileURLs = true
                settings.allowUniversalAccessFromFileURLs = true
                webViewClient = object : WebViewClient() {
                    override fun onPageFinished(view: WebView?, url: String?) {
                        webViewReady = true
                    }
                }
                try {
                    // Load from file:///android_asset/ so relative script tags resolve correctly
                    // Flutter assets are under flutter_assets/assets/ inside the APK
                    val htmlPath = "file:///android_asset/flutter_assets/assets/verdis_signer.html"
                    loadUrl(htmlPath)
                } catch (e: Exception) {
                    android.util.Log.e("VerdisSigner", "Failed to load signer: " + e.message)
                }
            }
        }
        // Allow page load + WASM init (typically <500ms, give 2s to be safe)
        Thread.sleep(2000)
    }

    private fun waitForWasm(): Boolean {
        val latch = CountDownLatch(1)
        var ready = false
        runOnUiThread {
            val wv = webView
            if (wv != null) {
                wv.evaluateJavascript("VerdisSigner.isReady()", object : ValueCallback<String> {
                    override fun onReceiveValue(value: String?) {
                        ready = value?.trim() == "true"
                        latch.countDown()
                    }
                })
            } else {
                latch.countDown()
            }
        }
        latch.await(5, TimeUnit.SECONDS)
        return ready
    }

    private fun deriveAddress(mnemonic: String, result: MethodChannel.Result) {
        // Wait for WASM to be ready (retry up to 3 times with 1s delay)
        var wasmReady = waitForWasm()
        if (!wasmReady) {
            Thread.sleep(1000)
            wasmReady = waitForWasm()
        }
        if (!wasmReady) {
            Thread.sleep(1000)
            wasmReady = waitForWasm()
        }

        val latch = CountDownLatch(1)
        var resultJson: String? = null

        // Escape single quotes in mnemonic for JS string
        val safeMnemonic = mnemonic.replace("\\", "\\\\").replace("'", "\\'")

        runOnUiThread {
            val wv = webView
            if (wv != null) {
                val js = "VerdisSigner.deriveAddress('$safeMnemonic')"
                wv.evaluateJavascript(js, object : ValueCallback<String> {
                    override fun onReceiveValue(value: String?) {
                        resultJson = value
                        latch.countDown()
                    }
                })
            } else {
                result.error("WEBVIEW_ERROR", "WebView not initialized", null)
                latch.countDown()
            }
        }

        if (latch.await(10, TimeUnit.SECONDS)) {
            val cleaned = resultJson?.trim()?.removeSurrounding("\"")
                ?.replace("\\\"", "\"")
                ?.replace("\\\\", "\\")
                ?.replace("\\n", "\n")

            if (cleaned != null && cleaned.startsWith("{")) {
                try {
                    val parsed = org.json.JSONObject(cleaned)
                    if (parsed.has("error")) {
                        val errMsg = parsed.getString("error")
                        if (errMsg == "WASM_NOT_READY") {
                            result.error("WASM_NOT_READY", "Polkadot WASM not initialized yet", null)
                        } else {
                            result.error("DERIVE_ERROR", errMsg, null)
                        }
                    } else {
                        result.success(mapOf(
                            "address" to parsed.getString("address"),
                            "publicKey" to parsed.optString("publicKey", ""),
                            "secretKey" to parsed.optString("secretKey", "")
                        ))
                    }
                } catch (e: Exception) {
                    result.error("PARSE_ERROR", e.message, null)
                }
            } else {
                result.error("DERIVE_ERROR", "Invalid response: $cleaned", null)
            }
        } else {
            result.error("TIMEOUT", "Derivation timed out", null)
        }
    }

    private fun generateMnemonic(result: MethodChannel.Result) {
        val latch = CountDownLatch(1)
        var resultStr: String? = null

        runOnUiThread {
            val wv = webView
            if (wv != null) {
                wv.evaluateJavascript("VerdisSigner.generateMnemonic()", object : ValueCallback<String> {
                    override fun onReceiveValue(value: String?) {
                        resultStr = value
                        latch.countDown()
                    }
                })
            } else {
                result.error("WEBVIEW_ERROR", "WebView not initialized", null)
                latch.countDown()
            }
        }

        if (latch.await(10, TimeUnit.SECONDS)) {
            val cleaned = resultStr?.trim()?.removeSurrounding("\"")
            if (cleaned != null) {
                result.success(cleaned)
            } else {
                result.error("GEN_ERROR", "No mnemonic returned", null)
            }
        } else {
            result.error("TIMEOUT", "Generation timed out", null)
        }
    }

    private fun signTransfer(mnemonic: String, destAddress: String, amountAtoms: Long, nonce: Long, genesisHash: String, blockHash: String, specVersion: Int, result: MethodChannel.Result) {
        var wasmReady = waitForWasm()
        if (!wasmReady) { Thread.sleep(1000); wasmReady = waitForWasm() }
        if (!wasmReady) { Thread.sleep(1000); wasmReady = waitForWasm() }

        val latch = CountDownLatch(1)
        var resultJson: String? = null

        val safeMnemonic = mnemonic.replace("\\", "\\\\").replace("'", "\\'")
        val safeDest = destAddress.replace("\\", "\\\\").replace("'", "\\'")

        runOnUiThread {
            val wv = webView
            if (wv != null) {
                val js = "VerdisSigner.signTransfer('" + safeMnemonic + "', '" + safeDest + "', " + amountAtoms + ", " + nonce + ", '" + genesisHash + "', '" + blockHash + "', " + specVersion + ")"
                wv.evaluateJavascript(js, object : ValueCallback<String> {
                    override fun onReceiveValue(value: String?) {
                        resultJson = value
                        latch.countDown()
                    }
                })
            } else {
                result.error("WEBVIEW_ERROR", "WebView not initialized", null)
                latch.countDown()
            }
        }

        if (latch.await(15, TimeUnit.SECONDS)) {
            val cleaned = resultJson?.trim()?.removeSurrounding("\"")
                ?.replace("\\\"", "\"")
                ?.replace("\\\\", "\\")
                ?.replace("\\n", "\n")
            if (cleaned != null && cleaned.startsWith("{")) {
                try {
                    val parsed = org.json.JSONObject(cleaned)
                    if (parsed.has("error")) {
                        result.error("SIGN_ERROR", parsed.getString("error"), null)
                    } else {
                        result.success(mapOf(
                            "extrinsic" to parsed.getString("extrinsic"),
                            "signer" to parsed.optString("signer", "")
                        ))
                    }
                } catch (e: Exception) {
                    result.error("PARSE_ERROR", e.message, null)
                }
            } else {
                result.error("SIGN_ERROR", "Invalid response: $cleaned", null)
            }
        } else {
            result.error("TIMEOUT", "Signing timed out", null)
        }
    }

    private fun validateMnemonic(mnemonic: String, result: MethodChannel.Result) {
        val latch = CountDownLatch(1)
        var resultStr: String? = null

        val safeMnemonic = mnemonic.replace("\\", "\\\\").replace("'", "\\'")

        runOnUiThread {
            val wv = webView
            if (wv != null) {
                val js = "VerdisSigner.validateMnemonic('$safeMnemonic')"
                wv.evaluateJavascript(js, object : ValueCallback<String> {
                    override fun onReceiveValue(value: String?) {
                        resultStr = value
                        latch.countDown()
                    }
                })
            } else {
                result.error("WEBVIEW_ERROR", "WebView not initialized", null)
                latch.countDown()
            }
        }

        if (latch.await(10, TimeUnit.SECONDS)) {
            val valid = resultStr?.trim() == "true"
            result.success(valid)
        } else {
            result.error("TIMEOUT", "Validation timed out", null)
        }
    }
}
