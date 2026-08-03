package com.verdis.wallet.net

import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicLong

/**
 * Custom Exception representing a JSON-RPC 2.0 error response.
 */
class RpcException(
    val code: Int,
    override val message: String,
    val data: Any? = null
) : Exception("JSON-RPC Error ($code): $message")

/**
 * Lightweight, zero-dependency JSON-RPC 2.0 client for Substrate/Verdis node interaction.
 * Uses java.net.HttpURLConnection for HTTP requests and Java's ExecutorService for async execution.
 */
class RpcClient(
    var rpcUrl: String = DEFAULT_RPC_URL,
    private val connectTimeoutMs: Int = 15000,
    private val readTimeoutMs: Int = 15000
) {
    companion object {
        const val DEFAULT_RPC_URL = "http://91.98.160.145:9944"
    }

    private val idGenerator = AtomicLong(1)
    private val executor: ExecutorService = Executors.newCachedThreadPool()

    /**
     * Synchronous JSON-RPC 2.0 request.
     *
     * @param method JSON-RPC method name (e.g. "system_chain")
     * @param params List of method parameters
     * @return JSONObject containing the JSON-RPC response (including "result" or "error")
     * @throws RpcException when the node returns a JSON-RPC error payload
     * @throws Exception on HTTP or connection errors
     */
    @Throws(Exception::class)
    fun request(method: String, params: List<Any> = emptyList()): JSONObject {
        val requestId = idGenerator.getAndIncrement()
        val payload = JSONObject().apply {
            put("jsonrpc", "2.0")
            put("method", method)
            put("params", buildJsonArray(params))
            put("id", requestId)
        }

        val responseString = sendHttpPost(payload.toString())
        val responseJson = JSONObject(responseString)

        if (responseJson.has("error") && !responseJson.isNull("error")) {
            val errorObj = responseJson.getJSONObject("error")
            val code = errorObj.optInt("code", -32603)
            val message = errorObj.optString("message", "Unknown RPC error")
            val data = errorObj.opt("data")
            throw RpcException(code, message, data)
        }

        return responseJson
    }

    /**
     * Asynchronous JSON-RPC 2.0 request using ExecutorService with callback.
     *
     * @param method JSON-RPC method name
     * @param params List of method parameters
     * @param callback Result callback invoked on completion with Result<JSONObject>
     */
    fun requestAsync(
        method: String,
        params: List<Any> = emptyList(),
        callback: (Result<JSONObject>) -> Unit
    ) {
        executor.execute {
            try {
                val result = request(method, params)
                callback(Result.success(result))
            } catch (e: Exception) {
                callback(Result.failure(e))
            }
        }
    }

    /**
     * Synchronous JSON-RPC 2.0 batch request.
     *
     * @param requests List of Pair(method, params)
     * @return JSONArray of JSON-RPC response objects
     */
    @Throws(Exception::class)
    fun batchRequest(requests: List<Pair<String, List<Any>>>): JSONArray {
        if (requests.isEmpty()) return JSONArray()

        val batchArray = JSONArray()
        for ((method, params) in requests) {
            val requestId = idGenerator.getAndIncrement()
            val reqObj = JSONObject().apply {
                put("jsonrpc", "2.0")
                put("method", method)
                put("params", buildJsonArray(params))
                put("id", requestId)
            }
            batchArray.put(reqObj)
        }

        val responseString = sendHttpPost(batchArray.toString())
        return JSONArray(responseString)
    }

    /**
     * Asynchronous JSON-RPC 2.0 batch request with callback.
     */
    fun batchRequestAsync(
        requests: List<Pair<String, List<Any>>>,
        callback: (Result<JSONArray>) -> Unit
    ) {
        executor.execute {
            try {
                val result = batchRequest(requests)
                callback(Result.success(result))
            } catch (e: Exception) {
                callback(Result.failure(e))
            }
        }
    }

    /**
     * Sends HTTP POST request using HttpURLConnection.
     */
    private fun sendHttpPost(jsonBody: String): String {
        val url = URL(rpcUrl)
        val conn = url.openConnection() as HttpURLConnection
        try {
            conn.requestMethod = "POST"
            conn.setRequestProperty("Content-Type", "application/json; charset=UTF-8")
            conn.setRequestProperty("Accept", "application/json")
            conn.connectTimeout = connectTimeoutMs
            conn.readTimeout = readTimeoutMs
            conn.doOutput = true
            conn.doInput = true

            OutputStreamWriter(conn.outputStream, Charsets.UTF_8).use { writer ->
                writer.write(jsonBody)
                writer.flush()
            }

            val statusCode = conn.responseCode
            val inputStream = if (statusCode in 200..299) {
                conn.inputStream
            } else {
                conn.errorStream ?: conn.inputStream
            }

            val responseText = BufferedReader(InputStreamReader(inputStream, Charsets.UTF_8)).use { reader ->
                val builder = StringBuilder()
                var line: String?
                while (reader.readLine().also { line = it } != null) {
                    builder.append(line)
                }
                builder.toString()
            }

            if (statusCode !in 200..299 && responseText.isBlank()) {
                throw java.io.IOException("HTTP $statusCode: ${conn.responseMessage}")
            }

            return responseText
        } finally {
            conn.disconnect()
        }
    }

    /**
     * Converts Kotlin List to org.json.JSONArray recursively.
     */
    private fun buildJsonArray(list: List<Any?>): JSONArray {
        val array = JSONArray()
        for (item in list) {
            array.put(wrapValue(item))
        }
        return array
    }

    /**
     * Normalizes values for org.json compatibility.
     */
    private fun wrapValue(value: Any?): Any? {
        return when (value) {
            null -> JSONObject.NULL
            is JSONObject, is JSONArray -> value
            is List<*> -> buildJsonArray(value)
            is Map<*, *> -> {
                val obj = JSONObject()
                for ((k, v) in value) {
                    obj.put(k.toString(), wrapValue(v))
                }
                obj
            }
            is Boolean, is Number, is String -> value
            is ByteArray -> "0x" + value.joinToString("") { "%02x".format(it) }
            else -> value.toString()
        }
    }

    /**
     * Shuts down background executor thread pool.
     */
    fun shutdown() {
        if (!executor.isShutdown) {
            executor.shutdown()
        }
    }
}
