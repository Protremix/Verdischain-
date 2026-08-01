package com.verdis.wallet

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
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
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_receive, container, false)

        val qrImage = view.findViewById<ImageView>(R.id.qr_image)
        val tvAddress = view.findViewById<TextView>(R.id.tv_full_address)
        val btnCopy = view.findViewById<Button>(R.id.btn_copy)

        val wallet = WalletManager.loadWallet(requireContext())
        if (wallet != null) {
            tvAddress.text = wallet.address

            // Generate native QR code with ZXing
            try {
                val barcodeEncoder = BarcodeEncoder()
                val bitmap = barcodeEncoder.encodeBitmap(
                    wallet.address,
                    BarcodeFormat.QR_CODE,
                    400, 400
                )
                qrImage.setImageBitmap(bitmap)
            } catch (e: Exception) {
                // Fallback
            }

            btnCopy.setOnClickListener {
                val clipboard = requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                clipboard.setPrimaryClip(ClipData.newPlainText("Verdis Address", wallet.address))
                Toast.makeText(requireContext(), "Address copied ✓", Toast.LENGTH_SHORT).show()
            }
        }

        return view
    }
}
