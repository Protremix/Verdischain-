package com.verdis.wallet

import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import com.google.android.material.bottomnavigation.BottomNavigationView

class MainActivity : AppCompatActivity() {

    private var bottomNav: BottomNavigationView? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val walletExists = WalletManager.loadWallet(this) != null
        if (!walletExists) {
            // No wallet yet — show onboarding without bottom nav
            setContentView(R.layout.activity_main)
            bottomNav = findViewById<BottomNavigationView?>(R.id.bottom_nav)?.also {
                it.visibility = View.GONE
            }
            loadFragment(OnboardingFragment())
            return
        }

        setContentView(R.layout.activity_main)
        setupBottomNav()
        loadFragment(HomeFragment())
    }

    private fun setupBottomNav() {
        bottomNav = findViewById(R.id.bottom_nav)
        bottomNav?.visibility = View.VISIBLE
        bottomNav?.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_home     -> { loadFragment(HomeFragment()); true }
                R.id.nav_swap     -> { loadFragment(SwapFragment()); true }
                R.id.nav_eco      -> { loadFragment(EcoFragment()); true }
                R.id.nav_stake    -> { loadFragment(StakeFragment()); true }
                R.id.nav_settings -> { loadFragment(SettingsFragment()); true }
                else -> false
            }
        }
    }

    fun loadFragment(fragment: Fragment) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.fragment_container, fragment)
            .commitAllowingStateLoss()
    }

    fun navigateTo(navId: Int) {
        bottomNav?.selectedItemId = navId
    }

    fun showReceive() {
        loadFragment(ReceiveFragment())
    }

    fun showOnboarding() {
        bottomNav?.visibility = View.GONE
        loadFragment(OnboardingFragment())
    }

    fun onWalletCreated() {
        setupBottomNav()
        loadFragment(HomeFragment())
    }
}
