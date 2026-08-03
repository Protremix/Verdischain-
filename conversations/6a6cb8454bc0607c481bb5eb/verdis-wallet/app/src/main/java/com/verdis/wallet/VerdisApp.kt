package com.verdis.wallet

import android.app.Application
import com.verdis.wallet.net.RpcClient
import com.verdis.wallet.net.SubstrateApi
import com.verdis.wallet.security.CrashHandler
import com.verdis.wallet.security.SecurityHelper

/**
 * Network configuration model holding chain and node connection settings.
 */
data class NetworkConfig(
    var rpcUrl: String = DEFAULT_RPC_URL,
    val chainName: String = CHAIN_NAME,
    val tokenSymbol: String = TOKEN_SYMBOL,
    val tokenDecimals: Int = TOKEN_DECIMALS,
    val ss58Format: Int = SS58_FORMAT
) {
    companion object {
        const val DEFAULT_RPC_URL = "http://91.98.160.145:9944"
        const val CHAIN_NAME = "Verdis"
        const val TOKEN_SYMBOL = "VRS"
        const val TOKEN_DECIMALS = 9
        const val SS58_FORMAT = 909
    }
}

/**
 * Main Application class for Verdis Wallet native Android app.
 * Initializes CrashHandler, SecurityHelper, RpcClient, SubstrateApi, and manages global app state.
 */
class VerdisApp : Application() {

    companion object {
        @Volatile
        private var instance: VerdisApp? = null

        /**
         * Global application instance accessor.
         */
        fun getInstance(): VerdisApp {
            return instance ?: throw IllegalStateException("VerdisApp has not been initialized")
        }
    }

    lateinit var networkConfig: NetworkConfig
        private set

    lateinit var rpcClient: RpcClient
        private set

    lateinit var substrateApi: SubstrateApi
        private set

    lateinit var securityHelper: SecurityHelper
        private set

    // Global active account state
    var currentAccountAddress: String? = null
    var currentAccountName: String? = null

    override fun onCreate() {
        super.onCreate()
        instance = this

        // 1. Initialize custom UncaughtExceptionHandler
        CrashHandler.init(this)

        // 2. Initialize Network Configuration with defaults
        networkConfig = NetworkConfig()

        // 3. Initialize RPC Client and Substrate API
        rpcClient = RpcClient(networkConfig.rpcUrl)
        substrateApi = SubstrateApi(rpcClient)

        // 4. Initialize Security Helper
        securityHelper = SecurityHelper(this)
    }

    /**
     * Dynamically update the node RPC URL and reconfigure RpcClient.
     */
    fun updateRpcUrl(newUrl: String) {
        networkConfig.rpcUrl = newUrl
        rpcClient.rpcUrl = newUrl
    }
}
