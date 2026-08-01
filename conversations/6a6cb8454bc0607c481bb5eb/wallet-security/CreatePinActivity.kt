package com.verdis.wallet

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.Vibrator
import android.view.View
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

/**
 * Create PIN flow: enter PIN → confirm PIN → save.
 */
class CreatePinActivity : AppCompatActivity() {

    private lateinit var pinDots: List<View>
    private val firstPin = StringBuilder()
    private val secondPin = StringBuilder()
    private var currentPin = StringBuilder()
    private var isConfirmStep = false
    private val maxPinLength = 6

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_lock)

        val title = findViewById<TextView>(R.id.tv_lock_title)
        title.text = "Create PIN"

        pinDots = listOf(
            findViewById(R.id.pin_dot_1),
            findViewById(R.id.pin_dot_2),
            findViewById(R.id.pin_dot_3),
            findViewById(R.id.pin_dot_4),
            findViewById(R.id.pin_dot_5),
            findViewById(R.id.pin_dot_6)
        )

        // Show keypad immediately
        findViewById<LinearLayout>(R.id.keypad).visibility = View.VISIBLE

        setupKeypad()
    }

    private fun setupKeypad() {
        val buttonIds = listOf(
            R.id.btn_1, R.id.btn_2, R.id.btn_3,
            R.id.btn_4, R.id.btn_5, R.id.btn_6,
            R.id.btn_7, R.id.btn_8, R.id.btn_9,
            R.id.btn_0
        )

        buttonIds.forEach { id ->
            findViewById<LinearLayout>(id).setOnClickListener {
                if (currentPin.length < maxPinLength) {
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
                    currentPin.append(num)
                    updatePinDots()
                    if (currentPin.length == maxPinLength) {
                        onPinComplete()
                    }
                }
                vibrate()
            }
        }

        findViewById<LinearLayout>(R.id.btn_delete).setOnClickListener {
            if (currentPin.isNotEmpty()) {
                currentPin.deleteCharAt(currentPin.length - 1)
                updatePinDots()
            }
            vibrate()
        }
    }

    private fun onPinComplete() {
        Handler(Looper.getMainLooper()).postDelayed({
            if (!isConfirmStep) {
                firstPin.append(currentPin)
                currentPin.clear()
                isConfirmStep = true
                findViewById<TextView>(R.id.tv_lock_title).text = "Confirm PIN"
                updatePinDots()
            } else {
                secondPin.append(currentPin)
                if (firstPin.toString() == secondPin.toString()) {
                    SecurityManager.setPin(this, firstPin.toString())
                    Toast.makeText(this, "PIN set successfully", Toast.LENGTH_SHORT).show()
                    setResult(RESULT_OK)
                    finish()
                } else {
                    Toast.makeText(this, "PINs don't match. Try again.", Toast.LENGTH_SHORT).show()
                    firstPin.clear()
                    secondPin.clear()
                    currentPin.clear()
                    isConfirmStep = false
                    findViewById<TextView>(R.id.tv_lock_title).text = "Create PIN"
                    updatePinDots()
                }
            }
        }, 100)
    }

    private fun updatePinDots() {
        pinDots.forEachIndexed { index, dot ->
            if (index < currentPin.length) {
                dot.setBackgroundResource(R.drawable.pin_dot_filled)
            } else {
                dot.setBackgroundResource(R.drawable.pin_dot_empty)
            }
        }
    }

    private fun vibrate() {
        (getSystemService(VIBRATOR_SERVICE) as? Vibrator)?.vibrate(10)
    }
}
