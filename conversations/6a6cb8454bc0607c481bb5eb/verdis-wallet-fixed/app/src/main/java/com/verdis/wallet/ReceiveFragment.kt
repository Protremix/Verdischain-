package com.verdis.wallet

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.Spinner
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import com.google.zxing.BarcodeFormat
import com.journeyapps.barcodescanner.BarcodeEncoder

class ReceiveFragment : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_receive, container, false)

        val tvAddress = view.findViewById<TextView>(R.id.tv_address)
        val ivQr = view.findViewById<android.widget.ImageView>(R.id.iv_qr_code)
        val btnCopy = view.findViewById<Button>(R.id.btn_copy)
        val btnShare = view.findViewById<Button>(R.id.btn_share)

        val wallet = WalletManager.loadWallet(requireContext())
        if (wallet == null) {
            Toast.makeText(context, "No wallet found", Toast.LENGTH_SHORT).show()
            return view
        }

        tvAddress.text = wallet.address

        // Generate QR code
        try {
            val barcodeEncoder = BarcodeEncoder()
            val bitmap = barcodeEncoder.encodeBitmap(wallet.address, BarcodeFormat.QR_CODE, 400, 400)
            ivQr.setImageBitmap(bitmap)
        } catch (e: Exception) {
            Toast.makeText(context, "QR generation failed", Toast.LENGTH_SHORT).show()
        }

        btnCopy.setOnClickListener {
            val clipboard = requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            clipboard.setPrimaryClip(ClipData.newPlainText("address", wallet.address))
            Toast.makeText(context, "Address copied!", Toast.LENGTH_SHORT).show()
        }

        btnShare.setOnClickListener {
            val shareIntent = Intent().apply {
                action = Intent.ACTION_SEND
                type = "text/plain"
                putExtra(Intent.EXTRA_TEXT, "My Verdis address: ${wallet.address}")
            }
            startActivity(Intent.createChooser(shareIntent, "Share Address"))
        }

        return view
    }
}
