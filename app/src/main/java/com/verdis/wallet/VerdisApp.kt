package com.verdis.wallet

import android.app.Application
import android.content.Context
import android.content.SharedPreferences
import com.verdis.wallet.crypto.KeyManager
import com.verdis.wallet.net.RpcClient
import com.verdis.wallet.net.SubstrateApi
import com.verdis.wallet.security.CrashHandler
import com.verdis.wallet.security.SecurityHelper

class VerdisApp : Application() {

    data class NetworkConfig(
        var rpcUrl: String = RpcClient.DEFAULT_RPC_URL,
        val chainName: String = "Verdis",
        val ss58Prefix: Int = 909,
        val tokenSymbol: String = "VRDX",
        val tokenDecimals: Int = 9
    )

    val networkConfig = NetworkConfig()
    val rpcClient by lazy { RpcClient(networkConfig.rpcUrl) }
    val substrateApi by lazy { SubstrateApi(rpcClient) }
    val securityHelper by lazy { SecurityHelper(this) }

    @Volatile
    var sessionPin: String? = null
        private set

    private val sessionPrefs: SharedPreferences by lazy {
        getSharedPreferences("verdis_session", Context.MODE_PRIVATE)
    }

    override fun onCreate() {
        super.onCreate()
        CrashHandler.init(this)
    }

    fun setSessionPin(pin: String) {
        sessionPin = pin
    }

    fun clearSession() {
        sessionPin = null
    }

    fun isUnlocked(): Boolean = sessionPin != null

    fun updateRpcUrl(newUrl: String) {
        networkConfig.rpcUrl = newUrl
    }
}
