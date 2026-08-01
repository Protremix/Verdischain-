package com.verdis.wallet

import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class CreatePinActivity : AppCompatActivity() {
    private var firstPin: String? = null
    private val pinBuilder = StringBuilder()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_lock)

        val tvPrompt = findViewById<TextView>(R.id.tv_lock_prompt)
        val tvPinDisplay = findViewById<TextView>(R.id.tv_pin_display)
        val btnBio = findViewById<Button>(R.id.btn_biometric)
        btnBio.visibility = View.GONE
        tvPrompt.text = "Create a 4-digit PIN"

        val keypad = listOf(
            R.id.btn_0, R.id.btn_1, R.id.btn_2, R.id.btn_3, R.id.btn_4,
            R.id.btn_5, R.id.btn_6, R.id.btn_7, R.id.btn_8, R.id.btn_9
        )

        for (i in 0..9) {
            val btn = findViewById<Button>(keypad[i])
            btn?.setOnClickListener {
                if (pinBuilder.length < 4) {
                    pinBuilder.append(i.toString())
                    tvPinDisplay.text = "•".repeat(pinBuilder.length)
                    if (pinBuilder.length == 4) {
                        handlePin(pinBuilder.toString())
                        pinBuilder.clear()
                        tvPinDisplay.text = ""
                    }
                }
            }
        }

        findViewById<Button>(R.id.btn_backspace)?.setOnClickListener {
            if (pinBuilder.isNotEmpty()) {
                pinBuilder.deleteCharAt(pinBuilder.length - 1)
                tvPinDisplay.text = "•".repeat(pinBuilder.length)
            }
        }
    }

    private fun handlePin(pin: String) {
        if (firstPin == null) {
            firstPin = pin
            findViewById<TextView>(R.id.tv_lock_prompt).text = "Confirm your PIN"
        } else {
            if (firstPin == pin) {
                SecurityManager.setPin(this, pin)
                Toast.makeText(this, "PIN set!", Toast.LENGTH_SHORT).show()
                finish()
            } else {
                Toast.makeText(this, "PINs don't match. Try again.", Toast.LENGTH_SHORT).show()
                firstPin = null
                findViewById<TextView>(R.id.tv_lock_prompt).text = "Create a 4-digit PIN"
            }
        }
    }
}
