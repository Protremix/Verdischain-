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
                else -> result.notImplemented()
            }
        }
    }

    private fun initWebView() {
        runOnUiThread {
            webView = WebView(this@MainActivity).apply {
                settings.javaScriptEnabled = true
                settings.domStorageEnabled = true
                webViewClient = object : WebViewClient() {
                    override fun onPageFinished(view: WebView?, url: String?) {
                        webViewReady = true
                    }
                }
                try {
                    val html = assets.open("flutter_assets/assets/verdis_signer.html").bufferedReader().use { it.readText() }
                    loadDataWithBaseURL("about:blank", html, "text/html", "UTF-8", null)
                } catch (e: Exception) {
                    try {
                        val html = assets.open("flutter_assets/verdis_signer.html").bufferedReader().use { it.readText() }
                        loadDataWithBaseURL("about:blank", html, "text/html", "UTF-8", null)
                    } catch (e2: Exception) {
                        android.util.Log.e("VerdisSigner", "Failed to load signer: " + e2.message)
                    }
                }
            }
        }
        Thread.sleep(500)
    }

    private fun deriveAddress(mnemonic: String, result: MethodChannel.Result) {
        val latch = CountDownLatch(1)
        var resultJson: String? = null

        runOnUiThread {
            val wv = webView
            if (wv != null) {
                wv.evaluateJavascript("VerdisSigner.deriveAddress('" + mnemonic.replace("'", "\\'") + "')", object : ValueCallback<String> {
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
            val cleaned = resultJson?.trim()
                ?.removeSurrounding("\"")
                ?.replace("\\\"", "\"")
                ?.replace("\\\\", "\\")
                ?.replace("\\n", "\n")

            if (cleaned != null && cleaned.startsWith("{")) {
                try {
                    val parsed = org.json.JSONObject(cleaned)
                    if (parsed.has("error")) {
                        result.error("DERIVE_ERROR", parsed.getString("error"), null)
                    } else {
                        result.success(mapOf(
                            "address" to parsed.getString("address"),
                            "publicKey" to parsed.getString("publicKey"),
                            "secretKey" to parsed.getString("secretKey")
                        ))
                    }
                } catch (e: Exception) {
                    result.error("PARSE_ERROR", e.message, null)
                }
            } else {
                result.error("DERIVE_ERROR", "Invalid response", null)
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

    private fun validateMnemonic(mnemonic: String, result: MethodChannel.Result) {
        val latch = CountDownLatch(1)
        var resultStr: String? = null

        runOnUiThread {
            val wv = webView
            if (wv != null) {
                wv.evaluateJavascript("VerdisSigner.validateMnemonic('" + mnemonic.replace("'", "\\'") + "')", object : ValueCallback<String> {
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
