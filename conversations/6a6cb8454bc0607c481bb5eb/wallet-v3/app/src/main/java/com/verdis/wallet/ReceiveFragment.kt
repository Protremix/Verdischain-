package com.verdis.wallet

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.graphics.Bitmap
import android.graphics.Color
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import com.google.zxing.BarcodeFormat
import com.journeyapps.barcodescanner.BarcodeEncoder

class ReceiveFragment : Fragment() {
    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        val v = inflater.inflate(R.layout.fragment_receive, container, false)
        val tvAddr = v.findViewById<TextView>(R.id.tv_receive_address)
        val imgQr = v.findViewById<ImageView>(R.id.img_qr_code)
        val btnCopy = v.findViewById<Button>(R.id.btn_copy_address)
        val btnBack = v.findViewById<Button>(R.id.btn_back)

        val wallet = WalletManager.loadWallet(requireContext())
        if (wallet == null) {
            Toast.makeText(context, "No wallet", Toast.LENGTH_SHORT).show()
            (activity as? MainActivity)?.showOnboarding()
            return v
        }

        tvAddr.text = wallet.address

        // Generate QR code
        try {
            val encoder = BarcodeEncoder()
            val bitmap = encoder.encodeBitmap(wallet.address, BarcodeFormat.QR_CODE, 400, 400)
            imgQr.setImageBitmap(bitmap)
            imgQr.visibility = View.VISIBLE
        } catch (e: Exception) {
            // Fallback: try without zxing
            try {
                val hints = mapOf(
                    com.google.zxing.EncodeHintType.MARGIN to 1,
                    com.google.zxing.EncodeHintType.COLOR_FOREGROUND to 0xFF0B1410.toInt(),
                    com.google.zxing.EncodeHintType.COLOR_BACKGROUND to Color.WHITE.toInt()
                )
                val matrix = com.google.zxing.MultiFormatWriter()
                    .encode(wallet.address, BarcodeFormat.QR_CODE, 400, 400, hints)
                val bmp = Bitmap.createBitmap(400, 400, Bitmap.Config.RGB_565)
                for (x in 0 until 400) {
                    for (y in 0 until 400) {
                        bmp.setPixel(x, y, if (matrix[x, y]) Color.BLACK else Color.WHITE)
                    }
                }
                imgQr.setImageBitmap(bmp)
                imgQr.visibility = View.VISIBLE
            } catch (e2: Exception) {
                imgQr.visibility = View.GONE
            }
        }

        btnCopy.setOnClickListener {
            (requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager)
                .setPrimaryClip(ClipData.newPlainText("address", wallet.address))
            Toast.makeText(context, "Address copied!", Toast.LENGTH_SHORT).show()
        }

        btnBack.setOnClickListener { (activity as? MainActivity)?.navigateTo(R.id.nav_home) }
        return v
    }
}
