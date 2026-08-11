package com.verdis.wallet.security

import androidx.fragment.app.FragmentActivity

/**
 * P1 fix: Biometric gate for all sensitive operations.
 * Forces biometric authentication before Send, Stake, Swap, and Export operations.
 */
object BiometricGate {

    /**
     * Checks if biometric is enabled and device supports it.
     * If enabled, shows BiometricPrompt before proceeding.
     * If not enabled, calls onProceed directly (PIN gate already passed).
     *
     * @param activity Hosting FragmentActivity (required for BiometricPrompt)
     * @param securityHelper SecurityHelper instance
     * @param operationName Human-readable name of the operation (e.g. "Send", "Stake")
     * @param onProceed Callback to execute after biometric verification (or if not enabled)
     * @param onCancel Callback if user cancels biometric prompt
     */
    fun requireAuth(
        activity: FragmentActivity,
        securityHelper: SecurityHelper,
        operationName: String,
        onProceed: () -> Unit,
        onCancel: () -> Unit = {}
    ) {
        // If biometric is not enabled, proceed (PIN already verified at app unlock)
        if (!securityHelper.isBiometricEnabled()) {
            // Biometric not enabled by user — PIN gate already passed, proceed
            onProceed()
            return
        }
        if (!securityHelper.isBiometricHardwareAvailable()) {
            // P0 fix: Biometric enabled but no hardware available.
            // Do NOT silently proceed — require user to confirm they want to continue
            // with PIN-only authentication for this sensitive operation.
            android.util.Log.w("BiometricGate", "Biometric enabled but no hardware available — showing confirmation dialog")
            androidx.appcompat.app.AlertDialog.Builder(activity)
                .setTitle("Biometric Unavailable")
                .setMessage("Biometric authentication is enabled but no biometric hardware was found on this device. Do you want to proceed with PIN-only authentication for this transaction?")
                .setPositiveButton("Proceed with PIN") { _, _ -> onProceed() }
                .setNegativeButton("Cancel") { _, _ -> onCancel() }
                .setCancelable(false)
                .show()
            return
        }

        securityHelper.authenticateBiometric(
            activity = activity,
            title = "Verify $operationName",
            subtitle = "Authenticate to $operationName securely",
            negativeButtonText = "Use PIN",
            onSuccess = { onProceed() },
            onError = { onCancel() }
        )
    }

    /**
     * Convenience method: require auth for Send operations.
     */
    fun requireForSend(activity: FragmentActivity, securityHelper: SecurityHelper, onProceed: () -> Unit, onCancel: () -> Unit = {}) {
        requireAuth(activity, securityHelper, "Send", onProceed, onCancel)
    }

    /**
     * Convenience method: require auth for Stake operations.
     */
    fun requireForStake(activity: FragmentActivity, securityHelper: SecurityHelper, onProceed: () -> Unit, onCancel: () -> Unit = {}) {
        requireAuth(activity, securityHelper, "Stake", onProceed, onCancel)
    }

    /**
     * Convenience method: require auth for Swap operations.
     */
    fun requireForSwap(activity: FragmentActivity, securityHelper: SecurityHelper, onProceed: () -> Unit, onCancel: () -> Unit = {}) {
        requireAuth(activity, securityHelper, "Swap", onProceed, onCancel)
    }

    /**
     * Convenience method: require auth for Export operations (mnemonic/private key).
     */
    fun requireForExport(activity: FragmentActivity, securityHelper: SecurityHelper, onProceed: () -> Unit, onCancel: () -> Unit = {}) {
        requireAuth(activity, securityHelper, "Export", onProceed, onCancel)
    }
}
