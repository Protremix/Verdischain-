package com.verdis.wallet

import android.app.Application
import android.util.Log
import java.io.File
import java.io.PrintWriter
import java.io.StringWriter

class VerdisApp : Application() {
    override fun onCreate() {
        super.onCreate()
        // Global crash handler — write to file and restart cleanly
        val previousHandler = Thread.getDefaultUncaughtExceptionHandler()
        Thread.setDefaultUncaughtExceptionHandler { thread, throwable ->
            try {
                val sw = StringWriter()
                throwable.printStackTrace(PrintWriter(sw))
                val crashLog = "CRASH on ${thread.name} at ${System.currentTimeMillis()}\n${sw}\n\n"
                val file = File(getExternalFilesDir(null), "verdis_crash.log")
                file.appendText(crashLog)
                Log.e("VerdisCrash", crashLog)
            } catch (e: Throwable) {
                Log.e("VerdisCrash", "Failed to write crash log: ${e.message}")
            }
            android.os.Process.killProcess(android.os.Process.myPid())
        }
    }
}
