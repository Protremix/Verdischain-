package com.verdis.wallet

import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat

class LockActivity : AppCompatActivity() {
    private var pinAttempts = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_lock)

        val tvPrompt = findViewById<TextView>(R.id.tv_lock_prompt)
        val tvPinDisplay = findViewById<TextView>(R.id.tv_pin_display)
        val btnBio = findViewById<Button>(R.id.btn_biometric)
        val keypad = listOf(
            R.id.btn_0, R.id.btn_1, R.id.btn_2, R.id.btn_3, R.id.btn_4,
            R.id.btn_5, R.id.btn_6, R.id.btn_7, R.id.btn_8, R.id.btn_9
        )

        val pinBuilder = StringBuilder()
        val hasPin = SecurityManager.hasPin(this)
        val canBiometric = SecurityManager.isBiometric(this) &&
            BiometricManager.from(this).canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG) == BiometricManager.BIOMETRIC_SUCCESS

        // Keypad
        for (i in 0..9) {
            val btn = findViewById<Button>(keypad[i])
            btn?.setOnClickListener {
                if (pinBuilder.length < 6) {
                    pinBuilder.append(i.toString())
                    tvPinDisplay.text = "•".repeat(pinBuilder.length)
                    if (pinBuilder.length == 4 || (pinBuilder.length == 6 && hasPin)) {
                        verifyPin(pinBuilder.toString())
                        pinBuilder.clear()
                        tvPinDisplay.text = ""
                    }
                }
            }
        }

        // Backspace
        findViewById<Button>(R.id.btn_backspace)?.setOnClickListener {
            if (pinBuilder.isNotEmpty()) {
                pinBuilder.deleteCharAt(pinBuilder.length - 1)
                tvPinDisplay.text = "•".repeat(pinBuilder.length)
            }
        }

        // Biometric
        if (canBiometric) {
            btnBio.visibility = View.VISIBLE
            btnBio.setOnClickListener { showBiometric() }
            showBiometric()
        } else {
            btnBio.visibility = View.GONE
        }
    }

    private fun verifyPin(pin: String) {
        if (SecurityManager.verifyPin(this, pin)) {
            startActivity(android.content.Intent(this, MainActivity::class.java))
            finish()
        } else {
            pinAttempts++
            if (pinAttempts >= 5) {
                Toast.makeText(this, "Too many attempts. Closing.", Toast.LENGTH_LONG).show()
                finishAffinity()
            } else {
                Toast.makeText(this, "Wrong PIN ($pinAttempts/5)", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun showBiometric() {
        val executor = ContextCompat.getMainExecutor(this)
        val prompt = BiometricPrompt(this, executor, object : BiometricPrompt.AuthenticationCallback() {
            override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                startActivity(android.content.Intent(this@LockActivity, MainActivity::class.java))
                finish()
            }
        })
        val info = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Unlock Verdis Wallet")
            .setSubtitle("Use your fingerprint to unlock")
            .setNegativeButtonText("Use PIN")
            .build()
        prompt.authenticate(info)
    }
}
