package com.verdis.wallet

import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import com.google.android.material.bottomnavigation.BottomNavigationView

class MainActivity : AppCompatActivity() {
    private var nav: BottomNavigationView? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        try {
            super.onCreate(savedInstanceState)
            setContentView(R.layout.activity_main)
            nav = findViewById(R.id.bottom_nav)
            val wallet = WalletManager.loadWallet(this)
            if (wallet == null) {
                nav?.visibility = View.GONE
                load(OnboardingFragment())
            } else {
                setupNav()
                load(HomeFragment())
            }
        } catch (e: Throwable) {
            android.util.Log.e("VerdisMain", "onCreate: ${e.message}", e)
            try { load(OnboardingFragment()) } catch (_: Throwable) {}
        }
    }

    private fun setupNav() {
        nav?.visibility = View.VISIBLE
        nav?.setOnItemSelectedListener { item ->
            try {
                when (item.itemId) {
                    R.id.nav_home -> { load(HomeFragment()); true }
                    R.id.nav_swap -> { load(SwapFragment()); true }
                    R.id.nav_eco -> { load(EcoFragment()); true }
                    R.id.nav_stake -> { load(StakeFragment()); true }
                    R.id.nav_settings -> { load(SettingsFragment()); true }
                    else -> false
                }
            } catch (e: Throwable) { false }
        }
    }

    fun load(f: Fragment) {
        try { supportFragmentManager.beginTransaction().replace(R.id.fragment_container, f).commitAllowingStateLoss() }
        catch (e: Throwable) { android.util.Log.e("VerdisMain", "load: ${e.message}", e) }
    }

    fun navigateTo(id: Int) { try { nav?.selectedItemId = id } catch (_: Throwable) {} }
    fun showReceive() { load(ReceiveFragment()) }
    fun showOnboarding() { nav?.visibility = View.GONE; load(OnboardingFragment()) }
    fun onWalletCreated() { setupNav(); load(HomeFragment()) }
}
