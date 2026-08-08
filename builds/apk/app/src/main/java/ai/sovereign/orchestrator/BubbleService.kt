package ai.sovereign.orchestrator

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.graphics.PixelFormat
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.provider.Settings
import android.view.Gravity
import android.view.View
import android.view.WindowManager
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import androidx.core.app.NotificationCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

/**
 * BubbleService — the free-roaming chat head.
 *
 * A floating bubble (SYSTEM_ALERT_WINDOW) with an expandable chat panel.
 * The roaming loop polls the orchestrator every [POLL_MS], refreshes the
 * home-screen widget, and surfaces proactive messages (anomalies, fidelity
 * drift, BCI lock) directly in the bubble and as a notification.
 */
class BubbleService : Service() {

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
    private val mainHandler = Handler(Looper.getMainLooper())
    private var pollJob: Job? = null
    private var windowManager: WindowManager? = null
    private var headView: View? = null
    private var panelView: View? = null
    private var expanded = false
    private var lastMessage: String? = null

    companion object {
        const val CHANNEL_ID = "sovereign_bubble"
        const val NOTIF_ID = 101
        const val POLL_MS = 15000L
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NOTIF_ID, buildNotification())
        ensureChannel()
        startRoamingLoop()
        return START_STICKY
    }

    override fun onDestroy() {
        pollJob?.cancel()
        scope.cancel()
        removeOverlay()
        super.onDestroy()
    }

    // ── notification ────────────────────────────────────────────────────
    private fun ensureChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val nm = getSystemService(NotificationManager::class.java)
            nm.createNotificationChannel(
                NotificationChannel(CHANNEL_ID, "Sovereign companion", NotificationManager.IMPORTANCE_LOW)
            )
        }
    }

    private fun buildNotification(): Notification {
        val open = PendingIntent.getActivity(
            this, 0, Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Sovereign companion")
            .setContentText("Roaming with your pulse — tap to open")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentIntent(open)
            .setOngoing(true)
            .build()
    }

    // ── roaming loop ────────────────────────────────────────────────────
    private fun startRoamingLoop() {
        if (pollJob?.isActive == true) return
        pollJob = scope.launch {
            while (isActive) {
                val snap = RoamingAgentClient.poll(this@BubbleService)
                if (snap.reachable) {
                    SovereignWidget.pushUpdate(this@BubbleService)
                    snap.message?.let { msg ->
                        if (msg != lastMessage) {
                            lastMessage = msg
                            postProactive(msg)
                        }
                    }
                }
                delay(POLL_MS)
            }
        }
    }

    // ── overlay (bubble + panel) ────────────────────────────────────────
    private fun canOverlay(): Boolean =
        Settings.canDrawOverlays(this)

    private fun showOverlay() {
        if (!canOverlay() || headView != null) return
        windowManager = getSystemService(WindowManager::class.java)

        val lp = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL,
            PixelFormat.TRANSLUCENT
        ).apply { gravity = Gravity.TOP or Gravity.END }

        headView = View.inflate(this, R.layout.bubble_head, null)
        headView!!.setOnClickListener { togglePanel() }
        windowManager!!.addView(headView, lp)
    }

    private fun togglePanel() {
        if (panelView != null) {
            removePanel()
            return
        }
        if (!canOverlay()) return
        val lp = WindowManager.LayoutParams(
            dp(280), WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        ).apply { gravity = Gravity.TOP or Gravity.END }

        panelView = View.inflate(this, R.layout.bubble_panel, null)
        panelView!!.findViewById<Button>(R.id.bubble_close).setOnClickListener { removePanel() }
        panelView!!.findViewById<Button>(R.id.bubble_send).setOnClickListener { sendFromPanel() }
        panelView!!.findViewById<EditText>(R.id.bubble_input).setOnEditorActionListener { _, _, _ ->
            sendFromPanel(); true
        }
        windowManager!!.addView(panelView, lp)
        expanded = true
    }

    private fun removePanel() {
        panelView?.let { windowManager?.removeView(it) }
        panelView = null
        expanded = false
    }

    private fun removeOverlay() {
        removePanel()
        headView?.let { windowManager?.removeView(it) }
        headView = null
    }

    private fun sendFromPanel() {
        val input = panelView?.findViewById<EditText>(R.id.bubble_input) ?: return
        val text = input.text.toString().trim()
        if (text.isEmpty()) return
        input.setText("")
        appendMessage("you: $text")
        scope.launch {
            val ok = RoamingAgentClient.sendMessage(this@BubbleService, text)
            appendMessage(if (ok) "orchestrator: received ✓" else "orchestrator: offline (local echo)")
        }
    }

    private fun postProactive(msg: String) {
        appendMessage("◉ $msg")
        val nm = getSystemService(NotificationManager::class.java)
        nm.notify(
            NOTIF_ID + 1,
            NotificationCompat.Builder(this, CHANNEL_ID)
                .setSmallIcon(android.R.drawable.ic_dialog_info)
                .setContentTitle("Sovereign")
                .setContentText(msg)
                .setAutoCancel(true)
                .build()
        )
    }

    private fun appendMessage(line: String) {
        // Views must be touched on the main thread (roaming loop runs on IO).
        mainHandler.post {
            val panel = panelView ?: return@post
            val log = panel.findViewById<LinearLayout>(R.id.bubble_log)
            val tv = TextView(this@BubbleService)
            tv.text = line
            tv.setTextColor(0xFFE8ECF8.toInt())
            tv.textSize = 13f
            log.addView(tv, 0)
            while (log.childCount > 40) {
                log.removeViewAt(log.childCount - 1)
            }
        }
    }

    private fun dp(v: Int): Int = (v * resources.displayMetrics.density).toInt()
}
