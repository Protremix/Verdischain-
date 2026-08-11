package com.verdis.wallet.notification

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.os.Build

/**
 * Restarts the notification monitoring service after device reboot.
 */
class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            val prefs = NotificationPrefs(context)
            if (prefs.masterEnabled) {
                NotificationMonitorService.start(context)
            }
        }
    }
}
