package com.verdis.wallet.security

import android.content.Context
import android.content.Intent
import android.os.Handler
import android.os.Looper
import android.os.Process
import android.util.Log
import android.widget.Toast
import com.verdis.wallet.ui.SplashActivity
import java.io.File
import java.io.FileWriter
import java.io.PrintWriter
import java.io.StringWriter
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * Custom UncaughtExceptionHandler that catches unhandled crashes, writes detailed stack traces
 * to log files, displays a user-friendly error message, and restarts the app gracefully to the splash screen.
 */
class CrashHandler private constructor(private val context: Context) : Thread.UncaughtExceptionHandler {

    private val defaultHandler: Thread.UncaughtExceptionHandler? =
        Thread.getDefaultUncaughtExceptionHandler()

    companion object {
        private const val TAG = "CrashHandler"

        @Volatile
        private var instance: CrashHandler? = null

        /**
         * Initialize the CrashHandler singleton and set as default UncaughtExceptionHandler.
         */
        fun init(context: Context): CrashHandler {
            return instance ?: synchronized(this) {
                instance ?: CrashHandler(context.applicationContext).also {
                    instance = it
                    Thread.setDefaultUncaughtExceptionHandler(it)
                }
            }
        }

        /**
         * Get initialized instance of CrashHandler.
         */
        fun getInstance(): CrashHandler {
            return instance ?: throw IllegalStateException("CrashHandler must be initialized with CrashHandler.init(context)")
        }
    }

    override fun uncaughtException(thread: Thread, throwable: Throwable) {
        Log.e(TAG, "Uncaught exception in thread '${thread.name}'", throwable)

        try {
            // Write detailed crash log to file storage
            val logFile = saveCrashReport(thread, throwable)
            Log.i(TAG, "Crash report successfully written to ${logFile.absolutePath}")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to write crash log to file", e)
        }

        // Show graceful error message and restart app to splash screen
        try {
            showGracefulErrorAndRestart()
        } catch (e: Exception) {
            Log.e(TAG, "Error performing graceful restart", e)
            defaultHandler?.uncaughtException(thread, throwable)
        }
    }

    /**
     * Writes crash details including stack trace, device info, and timestamp to a log file.
     */
    private fun saveCrashReport(thread: Thread, throwable: Throwable): File {
        val crashDir = File(context.filesDir, "crash_logs")
        if (!crashDir.exists()) {
            crashDir.mkdirs()
        }

        val timestamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date())
        val logFile = File(crashDir, "crash_$timestamp.log")

        val sw = StringWriter()
        val pw = PrintWriter(sw)
        throwable.printStackTrace(pw)
        val stackTraceStr = sw.toString()

        val logContent = buildString {
            append("=================== VERDIS WALLET CRASH REPORT ===================\n")
            append("Timestamp: ").append(SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS", Locale.US).format(Date())).append("\n")
            append("Thread Name: ").append(thread.name).append(" (ID: ").append(thread.id).append(")\n")
            append("Package Name: ").append(context.packageName).append("\n")
            append("Android OS Version: ").append(android.os.Build.VERSION.RELEASE).append(" (API ").append(android.os.Build.VERSION.SDK_INT).append(")\n")
            append("Device Manufacturer: ").append(android.os.Build.MANUFACTURER).append("\n")
            append("Device Model: ").append(android.os.Build.MODEL).append("\n")
            append("Exception Class: ").append(throwable.javaClass.name).append("\n")
            append("Exception Message: ").append(throwable.message ?: "No message provided").append("\n")
            append("------------------------------------------------------------------\n")
            append("Stack Trace:\n")
            append(stackTraceStr)
            append("==================================================================\n")
        }

        FileWriter(logFile, false).use { writer ->
            writer.write(logContent)
        }

        return logFile
    }

    /**
     * Displays a toast error message on main thread and restarts the app to SplashActivity.
     */
    private fun showGracefulErrorAndRestart() {
        // Show Toast message
        Handler(Looper.getMainLooper()).post {
            Toast.makeText(
                context,
                "Verdis Wallet encountered an error and was restarted.",
                Toast.LENGTH_LONG
            ).show()
        }

        // Brief delay to allow Toast to render
        try {
            Thread.sleep(1200)
        } catch (ignored: InterruptedException) {
        }

        // Restart to SplashActivity
        val intent = Intent(context, SplashActivity::class.java).apply {
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
            putExtra("EXTRA_CRASH_RESTART", true)
        }
        context.startActivity(intent)

        // Terminate current process cleanly
        Process.killProcess(Process.myPid())
        System.exit(10)
    }

    /**
     * Get list of saved crash log files.
     */
    fun getCrashLogs(): List<File> {
        val crashDir = File(context.filesDir, "crash_logs")
        return crashDir.listFiles()?.toList()?.sortedByDescending { it.lastModified() } ?: emptyList()
    }

    /**
     * Delete all stored crash log files.
     */
    fun clearCrashLogs() {
        val crashDir = File(context.filesDir, "crash_logs")
        crashDir.listFiles()?.forEach { it.delete() }
    }
}
