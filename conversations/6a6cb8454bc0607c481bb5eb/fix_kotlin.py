#!/usr/bin/env python3
"""Fix MainActivity.kt signTransfer function - string escaping issues"""

filepath = "/opt/verdis-wallet/mobile/android/app/src/main/kotlin/com/verdis/verdis_wallet/MainActivity.kt"

with open(filepath, "r") as f:
    content = f.read()

# The broken signTransfer function - find it and replace entirely
# Find from "private fun signTransfer" to the next "private fun"
start_marker = "    private fun signTransfer("
end_marker = "    private fun validateMnemonic("

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx < 0:
    print("ERROR: Could not find signTransfer function")
    exit(1)
if end_idx < 0:
    print("ERROR: Could not find validateMnemonic function")
    exit(1)

# Build the correct signTransfer function
correct_sign_transfer = '''    private fun signTransfer(mnemonic: String, destAddress: String, amountAtoms: Long, nonce: Long, genesisHash: String, blockHash: String, specVersion: Int, result: MethodChannel.Result) {
        var wasmReady = waitForWasm()
        if (!wasmReady) { Thread.sleep(1000); wasmReady = waitForWasm() }
        if (!wasmReady) { Thread.sleep(1000); wasmReady = waitForWasm() }

        val latch = CountDownLatch(1)
        var resultJson: String? = null

        val safeMnemonic = mnemonic.replace("\\\\", "\\\\\\\\").replace("'", "\\\\'")
        val safeDest = destAddress.replace("\\\\", "\\\\\\\\").replace("'", "\\\\'")

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
            val cleaned = resultJson?.trim()?.removeSurrounding("\\\"")
                ?.replace("\\\\\"", "\\\"")
                ?.replace("\\\\\\\\", "\\\\")
                ?.replace("\\\\n", "\\n")
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

'''

content = content[:start_idx] + correct_sign_transfer + content[end_idx:]

with open(filepath, "w") as f:
    f.write(content)

print("Fixed signTransfer function in MainActivity.kt")
