package ai.sovereign.orchestrator

import android.annotation.SuppressLint
import android.content.Intent
import android.graphics.Color
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.KeyEvent
import android.view.Menu
import android.view.MenuItem
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.activity.OnBackPressedCallback
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.WindowCompat

/**
 * MainActivity — dark-themed WebView shell for the Sovereign Orchestrator
 * dashboard.
 *
 * Brand palette:
 *   - Background : #0A0A10 (near-black)
 *   - Accent     : #00E5FF (cyan)
 *   - Highlight  : #00FFCC (mint)
 *
 * The dashboard URL is resolved from the string resource
 * [R.string.dashboard_url] (see res/values/strings.xml) so builds can point
 * at staging or production without touching code.
 */
class MainActivity : AppCompatActivity() {

    /** The single WebView that renders the dashboard for the session. */
    private lateinit var webView: WebView

    /** Brand background used by the window, the WebView and error surfaces. */
    private val brandBackground: Int = Color.parseColor("#0A0A10")

    /** Brand accent used for status-bar and UI chrome where supported. */
    @Suppress("unused")
    private val brandAccent: Int = Color.parseColor("#00E5FF")

    @SuppressLint("SetJavaScriptEnabled") // The dashboard is first-party code.
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        configureChrome()
        setupWebView()
        wireBackHandling()

        // Load the configured dashboard URL (defaults to production).
        webView.loadUrl(getString(R.string.dashboard_url))

        startCompanionIfPermitted()
    }

    // ── Free-roaming companion (bubble + widget) ────────────────────────
    private fun startCompanionIfPermitted() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            requestPermissions(arrayOf(android.Manifest.permission.POST_NOTIFICATIONS), 100)
        }
        if (!Settings.canDrawOverlays(this)) {
            // Ask once at launch; the user can also grant via the menu.
            Toast.makeText(this, R.string.overlay_hint, Toast.LENGTH_LONG).show()
        } else {
            startBubble()
        }
    }

    private fun startBubble() {
        val intent = Intent(this, BubbleService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
        Toast.makeText(this, R.string.bubble_started, Toast.LENGTH_SHORT).show()
    }

    private fun requestOverlay() {
        val uri = Uri.parse("package:$packageName")
        startActivity(
            Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, uri)
        )
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.main_menu, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            R.id.action_start_bubble -> {
                startBubble(); true
            }
            R.id.action_request_overlay -> {
                requestOverlay(); true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }

    override fun onResume() {
        super.onResume()
        // If the user granted overlay permission via Settings, start now.
        if (Settings.canDrawOverlays(this)) startBubble()
    }

    /** Tint the system chrome with the Sovereign dark palette. */
    private fun configureChrome() {
        // Draw edge-to-edge with the decor fitting the system windows.
        WindowCompat.setDecorFitsSystemWindows(window, true)
        window.statusBarColor = brandBackground
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            window.navigationBarColor = brandBackground
        }
        // Light icons on the dark background (false = light icons).
        WindowCompat.getInsetsController(window, window.decorView).apply {
            isAppearanceLightStatusBars = false
            isAppearanceLightNavigationBars = false
        }
    }

    /** Create and configure the dark WebView that hosts the dashboard. */
    private fun setupWebView() {
        webView = WebView(this)
        // Paint the canvas with the brand background to avoid white flashes.
        webView.setBackgroundColor(brandBackground)
        webView.settings.apply {
            javaScriptEnabled = true              // Dashboard SPA needs JS.
            domStorageEnabled = true              // localStorage for auth state.
            cacheMode = WebSettings.LOAD_DEFAULT  // Respect HTTP cache headers.
            mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
        }
        webView.webViewClient = object : WebViewClient() {
            // Keep every navigation inside this WebView (no external browser).
            override fun shouldOverrideUrlLoading(
                view: WebView?,
                request: WebResourceRequest?
            ): Boolean = false

            // Surface load failures with a brand-styled toast.
            override fun onReceivedError(
                view: WebView?,
                request: WebResourceRequest?,
                error: WebResourceError?
            ) {
                Toast.makeText(
                    this@MainActivity,
                    getString(R.string.dashboard_load_error),
                    Toast.LENGTH_SHORT
                ).show()
            }
        }
        setContentView(webView)
    }

    /**
     * Back-button handling: navigate the WebView history first; when the
     * history is exhausted, fall back to the default (finish) behaviour.
     */
    private fun wireBackHandling() {
        onBackPressedDispatcher.addCallback(
            this,
            object : OnBackPressedCallback(true) {
                override fun handleOnBackPressed() {
                    if (webView.canGoBack()) {
                        webView.goBack()
                    } else {
                        // Disable so the dispatcher performs the default.
                        isEnabled = false
                        onBackPressedDispatcher.onBackPressed()
                    }
                }
            }
        )
    }

    /** Physical back-key support (same semantics as the system back). */
    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {
        if (keyCode == KeyEvent.KEYCODE_BACK && webView.canGoBack()) {
            webView.goBack()
            return true
        }
        return super.onKeyDown(keyCode, event)
    }

    /** Release WebView resources on destroy to avoid leaks. */
    override fun onDestroy() {
        webView.destroy()
        super.onDestroy()
    }
}
