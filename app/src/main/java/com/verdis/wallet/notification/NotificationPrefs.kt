package com.verdis.wallet.notification

import android.content.Context
import android.content.SharedPreferences

/**
 * Manages notification preferences using SharedPreferences.
 * Controls which notification types the user wants to receive.
 */
class NotificationPrefs(context: Context) {

    private val prefs: SharedPreferences =
        context.getSharedPreferences("verdis_notifications", Context.MODE_PRIVATE)

    companion object {
        const val KEY_MASTER = "notif_master"
        const val KEY_TRANSACTIONS = "notif_transactions"
        const val KEY_STAKING = "notif_staking"
        const val KEY_EPOCH = "notif_epoch"
        const val KEY_VALIDATORS = "notif_validators"
        const val KEY_LAST_BLOCK = "last_block"
        const val KEY_LAST_BALANCE = "last_balance"
        const val KEY_LAST_EPOCH = "last_epoch"
        const val KEY_LAST_VALIDATORS = "last_validators"
        const val KEY_MONITOR_INTERVAL = "monitor_interval"
    }

    var masterEnabled: Boolean
        get() = prefs.getBoolean(KEY_MASTER, true)
        set(value) = prefs.edit().putBoolean(KEY_MASTER, value).apply()

    var transactionsEnabled: Boolean
        get() = prefs.getBoolean(KEY_TRANSACTIONS, true)
        set(value) = prefs.edit().putBoolean(KEY_TRANSACTIONS, value).apply()

    var stakingEnabled: Boolean
        get() = prefs.getBoolean(KEY_STAKING, true)
        set(value) = prefs.edit().putBoolean(KEY_STAKING, value).apply()

    var epochEnabled: Boolean
        get() = prefs.getBoolean(KEY_EPOCH, false)
        set(value) = prefs.edit().putBoolean(KEY_EPOCH, value).apply()

    var validatorsEnabled: Boolean
        get() = prefs.getBoolean(KEY_VALIDATORS, true)
        set(value) = prefs.edit().putBoolean(KEY_VALIDATORS, value).apply()

    var lastBlock: Long
        get() = prefs.getLong(KEY_LAST_BLOCK, 0)
        set(value) = prefs.edit().putLong(KEY_LAST_BLOCK, value).apply()

    var lastBalance: String
        get() = prefs.getString(KEY_LAST_BALANCE, "") ?: ""
        set(value) = prefs.edit().putString(KEY_LAST_BALANCE, value).apply()

    var lastEpoch: Long
        get() = prefs.getLong(KEY_LAST_EPOCH, 0)
        set(value) = prefs.edit().putLong(KEY_LAST_EPOCH, value).apply()

    var lastValidatorCount: Int
        get() = prefs.getInt(KEY_LAST_VALIDATORS, 0)
        set(value) = prefs.edit().putInt(KEY_LAST_VALIDATORS, value).apply()

    var monitorIntervalSec: Int
        get() = prefs.getInt(KEY_MONITOR_INTERVAL, 20)
        set(value) = prefs.edit().putInt(KEY_MONITOR_INTERVAL, value.coerceIn(10, 120)).apply()

    /**
     * Reset all monitoring state (used when wallet changes or service restarts).
     */
    fun resetMonitoringState() {
        prefs.edit()
            .putLong(KEY_LAST_BLOCK, 0)
            .putString(KEY_LAST_BALANCE, "")
            .putLong(KEY_LAST_EPOCH, 0)
            .putInt(KEY_LAST_VALIDATORS, 0)
            .apply()
    }
}
