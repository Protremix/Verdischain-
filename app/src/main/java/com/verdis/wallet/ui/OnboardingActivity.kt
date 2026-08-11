package com.verdis.wallet.ui

import android.app.Activity
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import com.verdis.wallet.R
import com.verdis.wallet.crypto.KeyManager

class OnboardingActivity : Activity() {

    private var keyManager: KeyManager? = null
    private var currentMnemonic: String? = null
    private var isCreateMode = true

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_onboarding)
        keyManager = KeyManager(this)

        // Views from layout
        val btnModeCreate = findViewById<Button>(R.id.btn_mode_create)
        val btnModeImport = findViewById<Button>(R.id.btn_mode_import)
        val sectionCreate = findViewById<LinearLayout>(R.id.section_create)
        val sectionImport = findViewById<LinearLayout>(R.id.section_import)
        val tvSeedPhrase = findViewById<TextView>(R.id.tv_seed_phrase)
        val btnCopySeed = findViewById<Button>(R.id.btn_copy_seed)
        val etImportSeed = findViewById<EditText>(R.id.et_import_seed)
        val etPin = findViewById<EditText>(R.id.et_pin)
        val etPinConfirm = findViewById<EditText>(R.id.et_pin_confirm)
        val btnFinishSetup = findViewById<Button>(R.id.btn_finish_setup)

        // Generate mnemonic immediately on load for create mode
        generateAndShowMnemonic(tvSeedPhrase)

        // Create mode button
        btnModeCreate.setOnClickListener {
            isCreateMode = true
            sectionCreate.visibility = View.VISIBLE
            sectionImport.visibility = View.GONE
            btnModeCreate.setBackgroundResource(R.drawable.btn_primary)
            btnModeCreate.setTextColor(0xFF000000.toInt())
            btnModeImport.setBackgroundResource(android.R.color.transparent)
            btnModeImport.setTextColor(0xFF8B8B8F.toInt())
            generateAndShowMnemonic(tvSeedPhrase)
        }

        // Import mode button
        btnModeImport.setOnClickListener {
            isCreateMode = false
            sectionCreate.visibility = View.GONE
            sectionImport.visibility = View.VISIBLE
            btnModeImport.setBackgroundResource(R.drawable.btn_primary)
            btnModeImport.setTextColor(0xFF000000.toInt())
            btnModeCreate.setBackgroundResource(android.R.color.transparent)
            btnModeCreate.setTextColor(0xFF8B8B8F.toInt())
        }

        // Copy seed button
        btnCopySeed.setOnClickListener {
            currentMnemonic?.let { mnemonic ->
                val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                clipboard.setPrimaryClip(ClipData.newPlainText("Verdis Seed Phrase", mnemonic))
                Toast.makeText(this, "Seed phrase copied to clipboard", Toast.LENGTH_SHORT).show()
            }
        }

        // Finish setup button
        btnFinishSetup.setOnClickListener {
            val pin = etPin.text.toString().trim()
            val pinConfirm = etPinConfirm.text.toString().trim()

            if (pin.length != 6 || !pin.all { it.isDigit() }) {
                Toast.makeText(this, "PIN must be 6 digits", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            if (pin != pinConfirm) {
                Toast.makeText(this, "PINs do not match", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            try {
                val address = if (isCreateMode) {
                    val mnemonic = currentMnemonic
                    if (mnemonic.isNullOrEmpty()) {
                        Toast.makeText(this, "Generating seed phrase, please wait...", Toast.LENGTH_SHORT).show()
                        return@setOnClickListener
                    }
                    keyManager?.importFromMnemonic("main", mnemonic, pin)!!
                } else {
                    val seed = etImportSeed.text.toString().trim()
                    if (seed.isEmpty()) {
                        Toast.makeText(this, "Enter seed phrase or private key", Toast.LENGTH_SHORT).show()
                        return@setOnClickListener
                    }
                    keyManager?.importAccount("main", seed, pin)!!
                }

                Toast.makeText(this, "Wallet ready: $address", Toast.LENGTH_LONG).show()
                startActivity(Intent(this, DashboardActivity::class.java))
                finish()
            } catch (e: Exception) {
                Toast.makeText(this, "Error: ${e.message}", Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun generateAndShowMnemonic(tvSeedPhrase: TextView) {
        try {
            currentMnemonic = com.verdis.wallet.crypto.Bip39Mnemonic.generate()
            // Format with word numbers for readability
            val words = currentMnemonic!!.split(" ")
            val formatted = words.mapIndexed { i, word ->
                "${i + 1}. $word"
            }.joinToString("\n")
            tvSeedPhrase.text = formatted
        } catch (e: Exception) {
            tvSeedPhrase.text = "Error generating seed: ${e.message}"
        }
    }
}
