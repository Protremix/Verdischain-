package com.verdis.wallet

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.view.animation.AnimationUtils
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat

class SplashActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_splash)

        val logo = findViewById<ImageView>(R.id.splash_logo)
        val title = findViewById<TextView>(R.id.splash_title)
        val tagline = findViewById<TextView>(R.id.splash_tagline)
        val progress = findViewById<ProgressBar>(R.id.splash_progress)

        // Logo fade-in
        logo.alpha = 0f
        logo.animate().alpha(1f).setDuration(600).start()

        // Title fade-in after 400ms
        Handler(Looper.getMainLooper()).postDelayed({
            title.visibility = View.VISIBLE
            title.alpha = 0f
            title.animate().alpha(1f).setDuration(400).start()
        }, 400)

        // Tagline after 800ms
        Handler(Looper.getMainLooper()).postDelayed({
            tagline.visibility = View.VISIBLE
            tagline.alpha = 0f
            tagline.animate().alpha(1f).setDuration(400).start()
        }, 800)

        // Progress after 1200ms
        Handler(Looper.getMainLooper()).postDelayed({
            progress.visibility = View.VISIBLE
        }, 1200)

        // Navigate after 2000ms
        Handler(Looper.getMainLooper()).postDelayed({
            navigateNext()
        }, 2000)
    }

    private fun navigateNext() {
        val wallet = WalletManager.loadWallet(this)

        if (wallet == null) {
            // No wallet → go to MainActivity (shows onboarding)
            goToMainActivity()
        } else if (SecurityManager.isSecurityEnabled(this)) {
            // Wallet exists + security enabled → lock screen
            startActivity(Intent(this, LockActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            })
            overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out)
            finish()
        } else {
            // Wallet exists, no security → go to MainActivity
            goToMainActivity()
        }
    }

    private fun goToMainActivity() {
        startActivity(Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        })
        overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out)
        finish()
    }
}
