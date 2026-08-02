#!/usr/bin/env bash
set -e

# 1. Fix MainActivity.kt — complete navigateTo and add History/DApp access
cat > /opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/MainActivity.kt << 'KOTLIN_EOF'
package com.verdis.wallet

import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment

class MainActivity : AppCompatActivity() {
    private var bottomNav: LinearLayout? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        Log.d("VerdisMain", "onCreate")
        super.onCreate(savedInstanceState)

        try {
            setContentView(R.layout.activity_main)
            Log.d("VerdisMain", "setContentView OK")
        } catch (e: Throwable) {
            Log.e("VerdisMain", "setContentView FAILED: ${e.message}", e)
            val tv = TextView(this).apply {
                text = "Layout error: ${e.message}"
                setTextColor(0xFFECFDF5.toInt()); textSize = 14f
                gravity = android.view.Gravity.CENTER; setPadding(32, 200, 32, 32)
            }
            setContentView(tv)
            return
        }

        bottomNav = findViewById(R.id.bottom_nav)
        setupNav()

        try {
            val wallet = WalletManager.loadWallet(this)
            Log.d("VerdisMain", "wallet=${wallet?.address}")
            if (wallet == null) {
                bottomNav?.visibility = View.GONE
                loadFragment(OnboardingFragment())
            } else {
                bottomNav?.visibility = View.VISIBLE
                loadFragment(HomeFragment())
            }
        } catch (e: Throwable) {
            Log.e("VerdisMain", "wallet check FAILED: ${e.message}", e)
            try { WalletManager.clearWallet(this) } catch (_: Throwable) {}
            bottomNav?.visibility = View.GONE
            loadFragment(OnboardingFragment())
        }
    }

    private fun setupNav() {
        setNavActive(R.id.nav_btn_home)
        listOf(
            R.id.nav_btn_home to { loadFragment(HomeFragment()); setNavActive(R.id.nav_btn_home) },
            R.id.nav_btn_swap to { loadFragment(SwapFragment()); setNavActive(R.id.nav_btn_swap) },
            R.id.nav_btn_eco  to { loadFragment(EcoFragment());  setNavActive(R.id.nav_btn_eco)  },
            R.id.nav_btn_stake to { loadFragment(StakeFragment()); setNavActive(R.id.nav_btn_stake) },
            R.id.nav_btn_ido  to { loadFragment(IdoFragment());  setNavActive(R.id.nav_btn_ido)  },
            R.id.nav_btn_settings to { loadFragment(SettingsFragment()); setNavActive(R.id.nav_btn_settings) }
        ).forEach { (id, action) ->
            findViewById<LinearLayout>(id)?.setOnClickListener {
                try { action() } catch (e: Throwable) { Log.e("VerdisMain","nav: ${e.message}") }
            }
        }
    }

    private fun setNavActive(activeId: Int) {
        listOf(R.id.nav_btn_home, R.id.nav_btn_swap, R.id.nav_btn_eco,
               R.id.nav_btn_stake, R.id.nav_btn_ido, R.id.nav_btn_settings).forEach { id ->
            val container = findViewById<LinearLayout>(id) ?: return@forEach
            val label = container.getChildAt(1) as? TextView ?: return@forEach
            label.setTextColor(if (id == activeId) 0xFF10B981.toInt() else 0xFF4A6B5A.toInt())
        }
    }

    fun loadFragment(f: Fragment) {
        try {
            supportFragmentManager.beginTransaction()
                .replace(R.id.fragment_container, f)
                .commitAllowingStateLoss()
        } catch (e: Throwable) { Log.e("VerdisMain", "loadFragment FAILED: ${e.message}", e) }
    }

    fun load(f: Fragment) = loadFragment(f)
    fun navigateTo(id: Int) {
        when(id) {
            R.id.nav_home     -> { loadFragment(HomeFragment());     setNavActive(R.id.nav_btn_home) }
            R.id.nav_swap     -> { loadFragment(SwapFragment());     setNavActive(R.id.nav_btn_swap) }
            R.id.nav_eco      -> { loadFragment(EcoFragment());      setNavActive(R.id.nav_btn_eco) }
            R.id.nav_stake    -> { loadFragment(StakeFragment());    setNavActive(R.id.nav_btn_stake) }
            R.id.nav_ido      -> { loadFragment(IdoFragment());      setNavActive(R.id.nav_btn_ido) }
            R.id.nav_settings -> { loadFragment(SettingsFragment()); setNavActive(R.id.nav_btn_settings) }
        }
    }
    fun showReceive() { loadFragment(ReceiveFragment()) }
    fun showHistory() { loadFragment(HistoryFragment()) }
    fun showDapps() { loadFragment(DappFragment()) }
    fun showOnboarding() { bottomNav?.visibility = View.GONE; loadFragment(OnboardingFragment()) }
    fun onWalletCreated() { bottomNav?.visibility = View.VISIBLE; loadFragment(HomeFragment()) }
}
KOTLIN_EOF

# 2. Add History and DApp buttons to fragment_home.xml
# Find the action buttons row and add History + DApp buttons
python3 << 'PYEOF'
with open("/opt/verdis-wallet-native/app/src/main/res/layout/fragment_home.xml", "r") as f:
    content = f.read()

# Add btn_history and btn_dapp after btn_stake
old_btn_stake = '''<LinearLayout
                    android:layout_width="0dp" android:layout_height="wrap_content"
                    android:layout_weight="1" android:orientation="vertical"
                    android:gravity="center" android:padding="12dp" android:clickable="true" android:focusable="true"
                    android:background="@drawable/card_bg" android:id="@+id/btn_stake">'''

new_buttons = old_btn_stake + '''
                <LinearLayout
                    android:layout_width="0dp" android:layout_height="wrap_content"
                    android:layout_weight="1" android:orientation="vertical"
                    android:gravity="center" android:padding="12dp" android:clickable="true" android:focusable="true"
                    android:background="@drawable/card_bg" android:id="@+id/btn_history">
                    <ImageView android:layout_width="24dp" android:layout_height="24dp"
                        android:src="@drawable/ic_nav_settings" android:tint="#00FF88"
                        android:scaleType="centerInside" />
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:text="History" android:textSize="10sp" android:textColor="#8BA898"
                        android:layout_marginTop="4dp" />
                </LinearLayout>
                <LinearLayout
                    android:layout_width="0dp" android:layout_height="wrap_content"
                    android:layout_weight="1" android:orientation="vertical"
                    android:gravity="center" android:padding="12dp" android:clickable="true" android:focusable="true"
                    android:background="@drawable/card_bg" android:id="@+id/btn_dapps">
                    <ImageView android:layout_width="24dp" android:layout_height="24dp"
                        android:src="@drawable/ic_contract" android:tint="#00FF88"
                        android:scaleType="centerInside" />
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:text="DApps" android:textSize="10sp" android:textColor="#8BA898"
                        android:layout_marginTop="4dp" />
                </LinearLayout>'''

content = content.replace(old_btn_stake, new_buttons, 1)

with open("/opt/verdis-wallet-native/app/src/main/res/layout/fragment_home.xml", "w") as f:
    f.write(content)
print("fragment_home.xml updated")
PYEOF

# 3. Wire up new buttons in HomeFragment.kt
python3 << 'PYEOF'
with open("/opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/HomeFragment.kt", "r") as f:
    content = f.read()

# Add history and dapps button listeners after the stake button listener
old_line = 'v.findViewById<View>(R.id.btn_stake).setOnClickListener { (activity as? MainActivity)?.navigateTo(R.id.nav_stake) }'
new_lines = old_line + '\n        v.findViewById<View>(R.id.btn_history)?.setOnClickListener { (activity as? MainActivity)?.showHistory() }\n        v.findViewById<View>(R.id.btn_dapps)?.setOnClickListener { (activity as? MainActivity)?.showDapps() }'

content = content.replace(old_line, new_lines, 1)

with open("/opt/verdis-wallet-native/app/src/main/java/com/verdis/wallet/HomeFragment.kt", "w") as f:
    f.write(content)
print("HomeFragment.kt updated")
PYEOF

# 4. Update build.gradle to v2.5.2
sed -i 's/versionCode 6/versionCode 8/' /opt/verdis-wallet-native/app/build.gradle
sed -i 's/versionName = "2.5.1"/versionName = "2.5.2"/' /opt/verdis-wallet-native/app/build.gradle

echo "=== Verify build.gradle ==="
grep 'versionCode\|versionName' /opt/verdis-wallet-native/app/build.gradle

echo "All fixes applied"
