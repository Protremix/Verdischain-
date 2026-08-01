package com.verdis.wallet

import android.os.Bundle
import android.view.MenuItem
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import com.google.android.material.bottomnavigation.BottomNavigationView

class MainActivity : AppCompatActivity() {

    private lateinit var bottomNav: BottomNavigationView
    private var currentWalletExists = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Check if wallet exists
        currentWalletExists = WalletManager.loadWallet(this) != null
        if (!currentWalletExists) {
            showOnboarding()
            return
        }

        setContentView(R.layout.activity_main)
        setupBottomNav()
        loadFragment(HomeFragment())
    }

    private fun setupBottomNav() {
        bottomNav = findViewById(R.id.bottom_nav)
        bottomNav.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_home -> { loadFragment(HomeFragment()); true }
                R.id.nav_swap -> { loadFragment(SwapFragment()); true }
                R.id.nav_eco -> { loadFragment(EcoFragment()); true }
                R.id.nav_stake -> { loadFragment(StakeFragment()); true }
                R.id.nav_settings -> { loadFragment(SettingsFragment()); true }
                else -> false
            }
        }
    }

    fun loadFragment(fragment: Fragment) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.fragment_container, fragment)
            .commit()
    }

    fun navigateTo(navId: Int) {
        bottomNav.selectedItemId = navId
    }

    fun showReceive() {
        loadFragment(ReceiveFragment())
    }

    fun showOnboarding() {
        setContentView(R.layout.activity_main)
        loadFragment(OnboardingFragment())
        if (::bottomNav.isInitialized) {
            bottomNav.visibility = View.GONE
        }
    }

    fun onWalletCreated() {
        currentWalletExists = true
        setContentView(R.layout.activity_main)
        setupBottomNav()
        bottomNav.visibility = View.VISIBLE
        loadFragment(HomeFragment())
    }
}
