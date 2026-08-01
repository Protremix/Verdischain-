package com.verdis.wallet

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import androidx.appcompat.app.AppCompatActivity

class SplashActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_splash)

        Handler(Looper.getMainLooper()).postDelayed({
            try {
                val wallet = WalletManager.loadWallet(this)
                val security = SecurityManager.getState(this)

                if (wallet != null && security.shouldLock(this)) {
                    startActivity(Intent(this, LockActivity::class.java))
                } else if (wallet != null) {
                    startActivity(Intent(this, MainActivity::class.java))
                } else {
                    startActivity(Intent(this, MainActivity::class.java))
                }
            } catch (e: Throwable) {
                startActivity(Intent(this, MainActivity::class.java))
            }
            finish()
        }, 1500)
    }
}
