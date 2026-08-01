package com.verdis.wallet

import android.animation.ObjectAnimator
import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.view.animation.AnimationUtils
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat

class SplashActivity : AppCompatActivity() {

    private var navigationScheduled = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_splash)

        val logo: ImageView? = findViewById(R.id.splash_logo)
        val lettersContainer: LinearLayout? = findViewById(R.id.letters_container)
        val tagline: TextView? = findViewById(R.id.splash_tagline)

        if (logo == null) {
            // Layout not found — navigate immediately
            navigateToMain()
            return
        }

        // Logo scale-in animation
        val logoAnim = AnimationUtils.loadAnimation(this, R.anim.logo_scale_in)
        logo.startAnimation(logoAnim)

        logoAnim.setAnimationListener(object : android.view.animation.Animation.AnimationListener {
            override fun onAnimationEnd(animation: android.view.animation.Animation?) {
                if (isFinishing || isDestroyed) return
                // Pulse glow on logo
                runCatching {
                    val pulse = AnimationUtils.loadAnimation(this@SplashActivity, R.anim.logo_pulse)
                    logo.startAnimation(pulse)
                }

                // Animate "VERDIS" letters one by one
                val letters = listOf("V", "E", "R", "D", "I", "S")
                lettersContainer?.post {
                    if (isFinishing || isDestroyed) return@post
                    letters.forEachIndexed { index, char ->
                        val letterView = TextView(this@SplashActivity).apply {
                            text = char
                            textSize = 38f
                            setTextColor(ContextCompat.getColor(this@SplashActivity, R.color.verdis_green))
                            typeface = android.graphics.Typeface.DEFAULT_BOLD
                            alpha = 0f
                            val params = LinearLayout.LayoutParams(
                                LinearLayout.LayoutParams.WRAP_CONTENT,
                                LinearLayout.LayoutParams.WRAP_CONTENT
                            )
                            params.setMargins(2, 0, 2, 0)
                            layoutParams = params
                        }
                        lettersContainer.addView(letterView)
                        Handler(Looper.getMainLooper()).postDelayed({
                            if (!isFinishing && !isDestroyed) {
                                letterView.animate()
                                    .alpha(1f)
                                    .translationYBy(-40f)
                                    .setDuration(300)
                                    .setInterpolator(android.view.animation.OvershootInterpolator())
                                    .start()
                            }
                        }, (index * 120).toLong())
                    }

                    // Show tagline after letters finish
                    Handler(Looper.getMainLooper()).postDelayed({
                        if (!isFinishing && !isDestroyed) {
                            tagline?.visibility = View.VISIBLE
                            runCatching {
                                tagline?.startAnimation(
                                    AnimationUtils.loadAnimation(this@SplashActivity, R.anim.tagline_fade_in)
                                )
                            }
                        }
                    }, (letters.size * 120 + 200).toLong())
                }
            }
            override fun onAnimationStart(animation: android.view.animation.Animation?) {}
            override fun onAnimationRepeat(animation: android.view.animation.Animation?) {}
        })

        // Navigate to MainActivity after splash
        Handler(Looper.getMainLooper()).postDelayed({
            navigateToMain()
        }, 2800)
    }

    private fun navigateToMain() {
        if (navigationScheduled || isFinishing || isDestroyed) return
        navigationScheduled = true
        runCatching {
            val fadeOut = AnimationUtils.loadAnimation(this, R.anim.splash_fade_out)
            findViewById<View>(android.R.id.content)?.startAnimation(fadeOut)
        }
        Handler(Looper.getMainLooper()).postDelayed({
            if (!isFinishing && !isDestroyed) {
                startActivity(Intent(this, MainActivity::class.java))
                overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out)
                finish()
            }
        }, 400)
    }

    override fun onDestroy() {
        super.onDestroy()
        // Remove any pending Handler callbacks by using a dedicated runnable is ideal,
        // but finish() prevents double-navigation since we check isFinishing above.
    }
}
