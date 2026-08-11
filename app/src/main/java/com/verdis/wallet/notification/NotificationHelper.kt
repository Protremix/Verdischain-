package com.verdis.wallet.notification

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import com.verdis.wallet.R
import com.verdis.wallet.ui.DashboardActivity

/**
 * Manages notification channels and builds/displays push notifications for the Verdis wallet.
 * Handles Android 8.0+ notification channels and backwards compatibility.
 */
object NotificationHelper {

    const val CHANNEL_TX = "verdis_tx"
    const val CHANNEL_STAKING = "verdis_staking"
    const val CHANNEL_EPOCH = "verdis_epoch"
    const val CHANNEL_VALIDATOR = "verdis_validator"
    const val CHANNEL_FOREGROUND = "verdis_foreground"

    const val NOTIF_ID_FOREGROUND = 1
    const val NOTIF_ID_TX_BASE = 100
    const val NOTIF_ID_STAKING = 200
    const val NOTIF_ID_EPOCH = 300
    const val NOTIF_ID_VALIDATOR = 400

    private var nextTxId = NOTIF_ID_TX_BASE

    /**
     * Create all notification channels. Must be called from Application.onCreate().
     */
    fun createChannels(context: Context) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return

        val nm = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        val channels = listOf(
            NotificationChannel(
                CHANNEL_TX,
                "Transactions",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Incoming and outgoing transaction alerts"
                enableVibration(true)
                enableLights(true)
                lightColor = 0xFF00d97e.toInt()
            },
            NotificationChannel(
                CHANNEL_STAKING,
                "Staking Rewards",
                NotificationManager.IMPORTANCE_DEFAULT
            ).apply {
                description = "Staking reward notifications"
                enableVibration(true)
            },
            NotificationChannel(
                CHANNEL_EPOCH,
                "Epoch Updates",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Epoch transition and block production alerts"
            },
            NotificationChannel(
                CHANNEL_VALIDATOR,
                "Validator Status",
                NotificationManager.IMPORTANCE_DEFAULT
            ).apply {
                description = "Validator status and slashing alerts"
                enableVibration(true)
            },
            NotificationChannel(
                CHANNEL_FOREGROUND,
                "Background Monitor",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Background blockchain monitoring service"
                setShowBadge(false)
            }
        )

        for (ch in channels) {
            nm.createNotificationChannel(ch)
        }
    }

    /**
     * Build the persistent foreground service notification.
     */
    fun buildForegroundNotification(context: Context, blockNumber: Long, peers: Int): Notification {
        val intent = Intent(context, DashboardActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        return NotificationCompat.Builder(context, CHANNEL_FOREGROUND)
            .setSmallIcon(android.R.drawable.stat_sys_download_done)
            .setContentTitle("Verdis Wallet")
            .setContentText("Block #$blockNumber · $peers peers connected")
            .setOngoing(true)
            .setSilent(true)
            .setContentIntent(pendingIntent)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }

    /**
     * Show a transaction notification (incoming or outgoing).
     */
    fun showTransactionNotification(
        context: Context,
        amount: String,
        isIncoming: Boolean,
        counterparty: String,
        txHash: String? = null
    ) {
        val nm = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        val intent = Intent(context, DashboardActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val title = if (isIncoming) "Incoming Transaction" else "Outgoing Transaction"
        val text = if (isIncoming) {
            "+$amount VRDX from ${counterparty.take(12)}…"
        } else {
            "-$amount VRDX to ${counterparty.take(12)}…"
        }

        val notifId = nextTxId++
        if (nextTxId > NOTIF_ID_TX_BASE + 50) nextTxId = NOTIF_ID_TX_BASE

        val builder = NotificationCompat.Builder(context, CHANNEL_TX)
            .setSmallIcon(android.R.drawable.stat_notify_chat)
            .setContentTitle(title)
            .setContentText(text)
            .setStyle(NotificationCompat.BigTextStyle().bigText(text))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .setColor(0xFF00d97e.toInt())

        txHash?.let { builder.setSubText("Tx: ${it.take(20)}…") }

        nm.notify(notifId, builder.build())
    }

    /**
     * Show a staking reward notification.
     */
    fun showStakingRewardNotification(context: Context, amount: String, epoch: Long) {
        val nm = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        val intent = Intent(context, DashboardActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val text = "You received $amount VRDX in staking rewards (Epoch $epoch)"

        val notif = NotificationCompat.Builder(context, CHANNEL_STAKING)
            .setSmallIcon(android.R.drawable.stat_notify_sync)
            .setContentTitle("Staking Reward")
            .setContentText(text)
            .setStyle(NotificationCompat.BigTextStyle().bigText(text))
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .setColor(0xFF00d97e.toInt())
            .build()

        nm.notify(NOTIF_ID_STAKING, notif)
    }

    /**
     * Show an epoch transition notification.
     */
    fun showEpochNotification(context: Context, newEpoch: Long, validatorCount: Int) {
        val nm = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        val intent = Intent(context, DashboardActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val text = "Epoch $newEpoch started · $validatorCount active validators"

        val notif = NotificationCompat.Builder(context, CHANNEL_EPOCH)
            .setSmallIcon(android.R.drawable.ic_menu_recent_history)
            .setContentTitle("Epoch Transition")
            .setContentText(text)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .setColor(0xFF00d97e.toInt())
            .build()

        nm.notify(NOTIF_ID_EPOCH, notif)
    }

    /**
     * Show a validator status notification (going offline, slashing, etc).
     */
    fun showValidatorNotification(context: Context, validatorName: String, event: String) {
        val nm = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        val intent = Intent(context, DashboardActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val text = "$validatorName: $event"

        val notif = NotificationCompat.Builder(context, CHANNEL_VALIDATOR)
            .setSmallIcon(android.R.drawable.stat_sys_warning)
            .setContentTitle("Validator Alert")
            .setContentText(text)
            .setStyle(NotificationCompat.BigTextStyle().bigText(text))
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .setColor(0xFFFF9800.toInt())
            .build()

        nm.notify(NOTIF_ID_VALIDATOR, notif)
    }

    /**
     * Cancel all non-foreground notifications.
     */
    fun cancelAll(context: Context) {
        val nm = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        nm.cancelAll()
    }
}
