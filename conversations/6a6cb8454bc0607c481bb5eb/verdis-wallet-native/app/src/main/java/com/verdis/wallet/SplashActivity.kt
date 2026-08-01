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

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_splash)

        val logo = findViewById<ImageView>(R.id.splash_logo)
        val lettersContainer = findViewById<LinearLayout>(R.id.letters_container)
        val tagline = findViewById<TextView>(R.id.splash_tagline)

        // Start logo scale-in animation
        val logoAnim = AnimationUtils.loadAnimation(this, R.anim.logo_scale_in)
        logo.startAnimation(logoAnim)

        // After logo appears, animate letters one by one
        logoAnim.setAnimationListener(object : android.view.animation.Animation.AnimationListener {
            override fun onAnimationEnd(animation: android.view.animation.Animation?) {
                // Pulse glow effect on logo
                val pulseAnim = AnimationUtils.loadAnimation(this@SplashActivity, R.anim.logo_pulse)
                logo.startAnimation(pulseAnim)

                // Animate "VERDIS" letters one by one
                val letters = listOf("V", "E", "R", "D", "I", "S")
                lettersContainer.post {
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

                        // Slide up + fade in each letter with stagger
                        Handler(Looper.getMainLooper()).postDelayed({
                            letterView.animate()
                                .alpha(1f)
                                .translationYBy(-40f)
                                .setDuration(300)
                                .setInterpolator(android.view.animation.OvershootInterpolator())
                                .start()
                        }, (index * 120).toLong())
                    }

                    // After all letters, show tagline
                    Handler(Looper.getMainLooper()).postDelayed({
                        tagline.visibility = View.VISIBLE
                        val taglineAnim = AnimationUtils.loadAnimation(this@SplashActivity, R.anim.tagline_fade_in)
                        tagline.startAnimation(taglineAnim)
                    }, (letters.size * 120 + 200).toLong())
                }
            }
            override fun onAnimationStart(animation: android.view.animation.Animation?) {}
            override fun onAnimationRepeat(animation: android.view.animation.Animation?) {}
        })

        // Navigate to MainActivity after splash completes
        Handler(Looper.getMainLooper()).postDelayed({
            // Fade out
            val fadeOut = AnimationUtils.loadAnimation(this, R.anim.splash_fade_out)
            findViewById<View>(android.R.id.content).startAnimation(fadeOut)

            Handler(Looper.getMainLooper()).postDelayed({
                startActivity(Intent(this, MainActivity::class.java))
                overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out)
                finish()
            }, 400)
        }, 2800)
    }
}
