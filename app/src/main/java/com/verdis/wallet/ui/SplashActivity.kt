package com.verdis.wallet.ui

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.widget.ProgressBar
import android.widget.TextView
import com.verdis.wallet.R
import com.verdis.wallet.crypto.KeyManager

class SplashActivity : Activity() {
    // P1 fix: Store handler as field so we can clean it up in onDestroy
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_splash)

        val progressText = findViewById<TextView>(R.id.status_text)
        val progressBar = findViewById<ProgressBar>(R.id.splash_progress)

        handler.postDelayed({
            val keyManager = KeyManager(this)
            val hasWallet = keyManager.hasAccount()

            val intent = if (hasWallet) {
                Intent(this, DashboardActivity::class.java)
            } else {
                Intent(this, OnboardingActivity::class.java)
            }
            startActivity(intent)
            finish()
        }, 2000)
    }
    override fun onDestroy() {
        super.onDestroy()
        // P1 fix: Remove any pending handler callbacks
        handler.removeCallbacksAndMessages(null)
    }
}
