package com.verdis.wallet.ui

import android.app.Activity
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.os.Bundle
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import com.verdis.wallet.R
import com.verdis.wallet.crypto.KeyManager
import com.verdis.wallet.crypto.Ss58Codec
import java.security.MessageDigest

class ReceiveActivity : Activity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_receive)

        val keyManager = KeyManager(this)
        val address = try {
            keyManager.getAddress("main")
        } catch (e: Exception) {
            "No wallet found"
        }

        findViewById<TextView>(R.id.addressText).text = address
        generateQR(address)

        findViewById<Button>(R.id.copyBtn).setOnClickListener {
            val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            clipboard.setPrimaryClip(ClipData.newPlainText("Verdis Address", address))
            Toast.makeText(this, "Address copied", Toast.LENGTH_SHORT).show()
        }
    }

    private fun generateQR(text: String) {
        // Simple QR-like pattern from SHA-256 hash (visual placeholder)
        val digest = MessageDigest.getInstance("SHA-256")
        val hash = digest.digest(text.toByteArray())
        val size = 240
        val modules = 21
        val cellSize = size / modules

        val bitmap = Bitmap.createBitmap(size, size, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        canvas.drawColor(Color.WHITE)
        val blackPaint = Paint().apply { color = Color.BLACK }

        // Draw pattern based on hash
        for (y in 0 until modules) {
            for (x in 0 until modules) {
                val byteIdx = (y * modules + x) % hash.size
                if ((hash[byteIdx].toInt() and 0xFF) and 1 == 0) {
                    canvas.drawRect(
                        x * cellSize.toFloat(), y * cellSize.toFloat(),
                        (x + 1) * cellSize.toFloat(), (y + 1) * cellSize.toFloat(),
                        blackPaint
                    )
                }
            }
        }

        // Draw finder patterns (corners)
        drawFinderPattern(canvas, 0, 0, cellSize, blackPaint)
        drawFinderPattern(canvas, (modules - 7) * cellSize, 0, cellSize, blackPaint)
        drawFinderPattern(canvas, 0, (modules - 7) * cellSize, cellSize, blackPaint)

        findViewById<ImageView>(R.id.qrImage).setImageBitmap(bitmap)
    }

    private fun drawFinderPattern(canvas: Canvas, x: Int, y: Int, cellSize: Int, paint: Paint) {
        canvas.drawRect(x.toFloat(), y.toFloat(), (x + 7 * cellSize).toFloat(), (y + 7 * cellSize).toFloat(), paint)
        val whitePaint = Paint().apply { color = Color.WHITE }
        canvas.drawRect(
            (x + cellSize).toFloat(), (y + cellSize).toFloat(),
            (x + 6 * cellSize).toFloat(), (y + 6 * cellSize).toFloat(), whitePaint
        )
        canvas.drawRect(
            (x + 2 * cellSize).toFloat(), (y + 2 * cellSize).toFloat(),
            (x + 5 * cellSize).toFloat(), (y + 5 * cellSize).toFloat(), paint
        )
    }
}
