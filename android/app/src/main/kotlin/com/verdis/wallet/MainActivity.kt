package com.verdis.wallet

import android.view.WindowManager
import android.content.Context
import java.io.File
import io.flutter.embedding.android.FlutterFragmentActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity: FlutterFragmentActivity() {
    private val CHANNEL = "com.verdis.wallet/security"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        // Prevent screenshots and screen recording (protects mnemonic/seed display)
        window.addFlags(WindowManager.LayoutParams.FLAG_SECURE)
        
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            when (call.method) {
                "setSecureFlag" -> {
                    val enabled = call.argument<Boolean>("enabled") ?: true
                    if (enabled) {
                        window.addFlags(WindowManager.LayoutParams.FLAG_SECURE)
                    } else {
                        window.clearFlags(WindowManager.LayoutParams.FLAG_SECURE)
                    }
                    result.success(null)
                }
                "isDeviceRooted" -> {
                    result.success(checkRoot())
                }
                else -> result.notImplemented()
            }
        }
    }

    private fun checkRoot(): Boolean {
        // Check for common root indicators
        val rootPaths = arrayOf(
            "/system/app/Superuser.apk",
            "/sbin/su",
            "/system/bin/su",
            "/system/xbin/su",
            "/data/local/xbin/su",
            "/data/local/bin/su",
            "/system/sd/xbin/su",
            "/system/bin/failsafe/su",
            "/data/local/su",
            "/su/bin/su"
        )
        for (path in rootPaths) {
            if (File(path).exists()) return true
        }
        // Check for Magisk
        if (File("/sbin/magisk").exists() || File("/system/bin/magisk").exists()) return true
        // Check for rooted apps
        val rootApps = arrayOf(
            "com.topjohnwu.magisk",
            "eu.chainfire.supersu",
            "com.koushikdutta.superuser"
        )
        val pm = packageManager
        for (pkg in rootApps) {
            try {
                pm.getPackageInfo(pkg, 0)
                return true
            } catch (e: Exception) { /* not installed */ }
        }
        // Check build tag
        val buildTag = android.os.Build.TAGS
        if (buildTag != null && buildTag.contains("test-keys")) return true
        return false
    }
}
