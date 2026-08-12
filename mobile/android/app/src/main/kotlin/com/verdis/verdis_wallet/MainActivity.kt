package com.verdis.verdis_wallet

import android.os.Handler
import android.os.Looper
import android.webkit.WebView
import android.webkit.WebViewClient
import io.flutter.embedding.android.FlutterFragmentActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

/**
 * Native crypto bridge: Flutter <-> hidden WebView running Polkadot WASM
 * (verdis_signer.html / VerdisSigner JS object).
 *
 * THREADING (fixed 2026-08-12): MethodChannel handlers run on the Android
 * platform/UI thread. WebView.evaluateJavascript() results are delivered
 * asynchronously via that same UI thread's Looper. Never block that thread
 * waiting for a callback that needs the thread to be free to fire — this
 * class is fully async (Handler.postDelayed for polling, MethodChannel.Result
 * resolved from within JS callbacks). No Thread.sleep, no CountDownLatch.
 *
 * WASM READINESS (fixed 2026-08-12): first-run WASM compile/instantiate can
 * legitimately take a few seconds on slower devices. Poll generously (20
 * attempts, 1s apart = ~20s ceiling) and pre-warm at engine startup so real
 * user actions usually find it already ready. On genuine exhaustion, query
 * VerdisSigner.getInitError() so the surfaced error is actionable instead of
 * a generic "not initialized yet".
 */
class MainActivity: FlutterFragmentActivity() {
    private val CHANNEL = "com.verdis.verdis_wallet/crypto"
    private var webView: WebView? = null
    @Volatile private var webViewReady = false
    private val mainHandler = Handler(Looper.getMainLooper())
    private val pendingReadyCallbacks = mutableListOf<() -> Unit>()

    // 20 attempts * 1s = ~20s ceiling for first-run WASM compile.
    private val WASM_READY_ATTEMPTS = 20

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)

        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            when (call.method) {
                "initWebView" -> {
                    ensureWebView { result.success(true) }
                }
                "deriveAddress" -> {
                    val mnemonic = call.argument<String>("mnemonic") ?: ""
                    ensureWasmReady(WASM_READY_ATTEMPTS) { ready ->
                        if (!ready) failNotReady(result)
                        else deriveAddressAsync(mnemonic, result)
                    }
                }
                "generateMnemonic" -> {
                    ensureWasmReady(WASM_READY_ATTEMPTS) { ready ->
                        if (!ready) failNotReady(result)
                        else generateMnemonicAsync(result)
                    }
                }
                "validateMnemonic" -> {
                    val mnemonic = call.argument<String>("mnemonic") ?: ""
                    ensureWasmReady(WASM_READY_ATTEMPTS) { ready ->
                        if (!ready) failNotReady(result)
                        else validateMnemonicAsync(mnemonic, result)
                    }
                }
                "signTransfer" -> {
                    val mnemonic = call.argument<String>("mnemonic") ?: ""
                    val destAddress = call.argument<String>("destAddress") ?: ""
                    val amountAtoms = call.argument<Number>("amountAtoms")?.toLong() ?: 0L
                    val nonce = call.argument<Number>("nonce")?.toLong() ?: 0L
                    val genesisHash = call.argument<String>("genesisHash") ?: ""
                    val blockHash = call.argument<String>("blockHash") ?: ""
                    val specVersion = call.argument<Number>("specVersion")?.toInt() ?: 0
                    ensureWasmReady(WASM_READY_ATTEMPTS) { ready ->
                        if (!ready) failNotReady(result)
                        else signTransferAsync(mnemonic, destAddress, amountAtoms, nonce, genesisHash, blockHash, specVersion, result)
                    }
                }
                else -> result.notImplemented()
            }
        }

        // Pre-warm WebView + kick off WASM readiness polling immediately so
        // real user actions (a few seconds later) usually find it ready.
        ensureWebView { ensureWasmReady(WASM_READY_ATTEMPTS) { } }
    }

    /** Resolves [result] with a WASM_NOT_READY error, including the real JS
     * init error/status when available, instead of a generic message. */
    private fun failNotReady(result: MethodChannel.Result) {
        val wv = webView
        if (wv == null) {
            result.error("WASM_NOT_READY", "Polkadot WASM not initialized yet (WebView unavailable)", null)
            return
        }
        wv.evaluateJavascript("VerdisSigner.getInitError ? VerdisSigner.getInitError() : 'unknown'") { value ->
            val detail = cleanJsResult(value) ?: "unknown"
            result.error("WASM_NOT_READY", "Polkadot WASM not initialized yet: $detail", null)
        }
    }

    /**
     * Creates the WebView on first use (idempotent) and invokes [onReady]
     * once the page has finished loading. Never blocks.
     */
    private fun ensureWebView(onReady: () -> Unit) {
        val existing = webView
        if (existing != null && webViewReady) {
            onReady()
            return
        }
        pendingReadyCallbacks.add(onReady)
        if (existing != null) return // init already in flight; callback queued above

        mainHandler.post {
            if (webView != null) return@post // guard against double-init races

            val wv = WebView(this@MainActivity)
            wv.settings.javaScriptEnabled = true
            wv.settings.domStorageEnabled = true
            wv.settings.allowFileAccess = true
            wv.settings.allowFileAccessFromFileURLs = true
            wv.settings.allowUniversalAccessFromFileURLs = true
            wv.webViewClient = object : WebViewClient() {
                override fun onPageFinished(view: WebView?, url: String?) {
                    webViewReady = true
                    drainReadyCallbacks()
                }
            }
            webView = wv
            try {
                wv.loadUrl("file:///android_asset/flutter_assets/assets/verdis_signer.html")
            } catch (e: Exception) {
                android.util.Log.e("VerdisSigner", "Failed to load signer: " + e.message)
                drainReadyCallbacks()
            }
        }
    }

    private fun drainReadyCallbacks() {
        val callbacks = pendingReadyCallbacks.toList()
        pendingReadyCallbacks.clear()
        callbacks.forEach { it() }
    }

    /**
     * Polls VerdisSigner.isReady() with up to [attemptsLeft] tries, 1s apart,
     * fully asynchronously (Handler.postDelayed — never blocks a thread).
     */
    private fun ensureWasmReady(attemptsLeft: Int, callback: (Boolean) -> Unit) {
        ensureWebView {
            checkWasmReady { ready ->
                if (ready) {
                    callback(true)
                } else if (attemptsLeft > 1) {
                    mainHandler.postDelayed({ ensureWasmReady(attemptsLeft - 1, callback) }, 1000)
                } else {
                    callback(false)
                }
            }
        }
    }

    private fun checkWasmReady(callback: (Boolean) -> Unit) {
        val wv = webView
        if (wv == null) { callback(false); return }
        wv.evaluateJavascript("VerdisSigner.isReady()") { value ->
            callback(value?.trim() == "true")
        }
    }

    private fun escapeJs(s: String): String = s.replace("\\", "\\\\").replace("'", "\\'")

    /** Cleans the raw JSON string returned by evaluateJavascript (which
     * comes back as a JS string literal, e.g. "\"{...}\"" or "null"). */
    private fun cleanJsResult(raw: String?): String? {
        if (raw == null || raw == "null") return null
        return raw.trim().removeSurrounding("\"")
            .replace("\\\"", "\"")
            .replace("\\\\", "\\")
            .replace("\\n", "\n")
    }

    /** Runs [block] once, then guarantees exactly one of block/timeout fires — never both. */
    private fun withTimeout(ms: Long, onTimeout: () -> Unit, block: (markDone: () -> Boolean) -> Unit) {
        var done = false
        val markDone: () -> Boolean = {
            synchronized(this) {
                if (done) false else { done = true; true }
            }
        }
        val timeoutRunnable = Runnable {
            if (markDone()) onTimeout()
        }
        mainHandler.postDelayed(timeoutRunnable, ms)
        block {
            val first = markDone()
            if (first) mainHandler.removeCallbacks(timeoutRunnable)
            first
        }
    }

    private fun deriveAddressAsync(mnemonic: String, result: MethodChannel.Result) {
        val wv = webView
        if (wv == null) { result.error("WEBVIEW_ERROR", "WebView not initialized", null); return }
        val js = "VerdisSigner.deriveAddress('${escapeJs(mnemonic)}')"
        withTimeout(10000, { result.error("TIMEOUT", "Derivation timed out", null) }) { markDone ->
            wv.evaluateJavascript(js) { value ->
                if (!markDone()) return@evaluateJavascript
                val cleaned = cleanJsResult(value)
                if (cleaned != null && cleaned.startsWith("{")) {
                    try {
                        val parsed = org.json.JSONObject(cleaned)
                        if (parsed.has("error")) {
                            val errMsg = parsed.getString("error")
                            if (errMsg == "WASM_NOT_READY") result.error("WASM_NOT_READY", "Polkadot WASM not initialized yet", null)
                            else result.error("DERIVE_ERROR", errMsg, null)
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
            }
        }
    }

    private fun generateMnemonicAsync(result: MethodChannel.Result) {
        val wv = webView
        if (wv == null) { result.error("WEBVIEW_ERROR", "WebView not initialized", null); return }
        withTimeout(10000, { result.error("TIMEOUT", "Generation timed out", null) }) { markDone ->
            wv.evaluateJavascript("VerdisSigner.generateMnemonic()") { value ->
                if (!markDone()) return@evaluateJavascript
                val cleaned = cleanJsResult(value)
                if (cleaned != null) result.success(cleaned)
                else result.error("GEN_ERROR", "No mnemonic returned", null)
            }
        }
    }

    private fun validateMnemonicAsync(mnemonic: String, result: MethodChannel.Result) {
        val wv = webView
        if (wv == null) { result.error("WEBVIEW_ERROR", "WebView not initialized", null); return }
        val js = "VerdisSigner.validateMnemonic('${escapeJs(mnemonic)}')"
        withTimeout(10000, { result.error("TIMEOUT", "Validation timed out", null) }) { markDone ->
            wv.evaluateJavascript(js) { value ->
                if (!markDone()) return@evaluateJavascript
                result.success(value?.trim() == "true")
            }
        }
    }

    private fun signTransferAsync(
        mnemonic: String,
        destAddress: String,
        amountAtoms: Long,
        nonce: Long,
        genesisHash: String,
        blockHash: String,
        specVersion: Int,
        result: MethodChannel.Result
    ) {
        val wv = webView
        if (wv == null) { result.error("WEBVIEW_ERROR", "WebView not initialized", null); return }
        val js = "VerdisSigner.signTransfer('${escapeJs(mnemonic)}', '${escapeJs(destAddress)}', " +
            "$amountAtoms, $nonce, '$genesisHash', '$blockHash', $specVersion)"
        withTimeout(15000, { result.error("TIMEOUT", "Signing timed out", null) }) { markDone ->
            wv.evaluateJavascript(js) { value ->
                if (!markDone()) return@evaluateJavascript
                val cleaned = cleanJsResult(value)
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
            }
        }
    }
}
