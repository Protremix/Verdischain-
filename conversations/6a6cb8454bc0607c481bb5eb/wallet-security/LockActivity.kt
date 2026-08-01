package com.verdis.wallet

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.Vibrator
import android.view.View
import android.view.animation.Animation
import android.view.animation.AnimationUtils
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.activity.OnBackPressedCallback
import androidx.appcompat.app.AppCompatActivity
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat

class LockActivity : AppCompatActivity() {

    private lateinit var pinDots: List<View>
    private val pinBuilder = StringBuilder()
    private val maxPinLength = 6

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_lock)

        pinDots = listOf(
            findViewById(R.id.pin_dot_1),
            findViewById(R.id.pin_dot_2),
            findViewById(R.id.pin_dot_3),
            findViewById(R.id.pin_dot_4),
            findViewById(R.id.pin_dot_5),
            findViewById(R.id.pin_dot_6)
        )

        val state = SecurityManager.getState(this)

        if (state.biometricEnabled && canUseBiometric()) {
            showBiometricPrompt()
        }

        setupKeypad()

        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() { /* must authenticate */ }
        })
    }

    private fun canUseBiometric(): Boolean {
        return BiometricManager.from(this).canAuthenticate(
            BiometricManager.Authenticators.BIOMETRIC_STRONG
        ) == BiometricManager.BIOMETRIC_SUCCESS
    }

    private fun showBiometricPrompt() {
        val executor = ContextCompat.getMainExecutor(this)
        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Unlock Verdis")
            .setSubtitle("Authenticate to access your wallet")
            .setNegativeButtonText("Use PIN")
            .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
            .build()

        val biometricPrompt = BiometricPrompt(this, executor, object : BiometricPrompt.AuthenticationCallback() {
            override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                unlockSuccess()
            }

            override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                findViewById<TextView>(R.id.tv_lock_title).text = "Enter PIN"
                findViewById<LinearLayout>(R.id.keypad).visibility = View.VISIBLE
            }
        })

        biometricPrompt.authenticate(promptInfo)
    }

    private fun setupKeypad() {
        val keypad = findViewById<LinearLayout>(R.id.keypad)
        val state = SecurityManager.getState(this)

        if (!state.biometricEnabled || !canUseBiometric()) {
            keypad.visibility = View.VISIBLE
        }

        val buttonIds = listOf(
            R.id.btn_1, R.id.btn_2, R.id.btn_3,
            R.id.btn_4, R.id.btn_5, R.id.btn_6,
            R.id.btn_7, R.id.btn_8, R.id.btn_9,
            R.id.btn_0
        )

        buttonIds.forEach { id ->
            findViewById<LinearLayout>(id).setOnClickListener {
                if (pinBuilder.length < maxPinLength) {
                    val num = when(id) {
                        R.id.btn_0 -> "0"
                        R.id.btn_1 -> "1"
                        R.id.btn_2 -> "2"
                        R.id.btn_3 -> "3"
                        R.id.btn_4 -> "4"
                        R.id.btn_5 -> "5"
                        R.id.btn_6 -> "6"
                        R.id.btn_7 -> "7"
                        R.id.btn_8 -> "8"
                        R.id.btn_9 -> "9"
                        else -> "0"
                    }
                    pinBuilder.append(num)
                    updatePinDots()
                    if (pinBuilder.length == maxPinLength) {
                        verifyPin()
                    }
                }
                vibrate()
            }
        }

        findViewById<LinearLayout>(R.id.btn_delete).setOnClickListener {
            if (pinBuilder.isNotEmpty()) {
                pinBuilder.deleteCharAt(pinBuilder.length - 1)
                updatePinDots()
            }
            vibrate()
        }
    }

    private fun updatePinDots() {
        pinDots.forEachIndexed { index, dot ->
            if (index < pinBuilder.length) {
                dot.setBackgroundResource(R.drawable.pin_dot_filled)
            } else {
                dot.setBackgroundResource(R.drawable.pin_dot_empty)
            }
        }
    }

    private fun verifyPin() {
        if (SecurityManager.verifyPin(this, pinBuilder.toString())) {
            unlockSuccess()
        } else {
            val shake = AnimationUtils.loadAnimation(this, android.R.anim.fade_in)
            pinDots.forEach { it.startAnimation(shake) }
            pinBuilder.clear()
            Handler(Looper.getMainLooper()).postDelayed({ updatePinDots() }, 100)
            Toast.makeText(this, "Wrong PIN", Toast.LENGTH_SHORT).show()
            vibrate()
        }
    }

    private fun unlockSuccess() {
        startActivity(Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        })
        overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out)
        finish()
    }

    private fun vibrate() {
        (getSystemService(VIBRATOR_SERVICE) as? Vibrator)?.vibrate(10)
    }
}
