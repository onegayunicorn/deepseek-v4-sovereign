package ai.sovereign.orchestrator

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL

/**
 * RoamingAgentClient — the free-roaming orchestrator link on the phone.
 *
 * Polls the local Sovereign orchestrator (Termux or LAN host) for telemetry
 * and PERO state, caches the last snapshot in SharedPreferences, and
 * surfaces proactive messages when the system needs attention (e.g. a
 * fidelity drop below target).
 *
 * Default endpoint: http://127.0.0.1:8000  (orchestrator running on the
 * phone via scripts/install-termux.sh). Overridable in Settings.
 */
object RoamingAgentClient {

    const val PREFS = "sovereign_telemetry"
    const val KEY_FIDELITY = "fidelity"
    const val KEY_PAIRS = "pairs"
    const val KEY_BCI = "bci"
    const val KEY_LAST_SEEN = "last_seen"
    const val KEY_URL = "orchestrator_url"

    const val DEFAULT_URL = "http://127.0.0.1:8000"
    private const val TIMEOUT_MS = 4000

    data class Snapshot(
        val fidelity: Double,
        val pairs: Long,
        val bciHertz: Int,
        val reachable: Boolean,
        val message: String?
    )

    /** Fetch telemetry from the orchestrator (blocking; call on IO). */
    private fun fetchRaw(baseUrl: String): JSONObject? {
        val endpoints = listOf(
            "$baseUrl/api/v1/pero/state",
            "$baseUrl/api/v1/telemetry",
            "$baseUrl/api/v1/system/status"
        )
        for (ep in endpoints) {
            try {
                val conn = URL(ep).openConnection() as HttpURLConnection
                conn.connectTimeout = TIMEOUT_MS
                conn.readTimeout = TIMEOUT_MS
                conn.requestMethod = "GET"
                if (conn.responseCode == 200) {
                    val body = BufferedReader(InputStreamReader(conn.inputStream)).use { it.readText() }
                    return JSONObject(body)
                }
                conn.disconnect()
            } catch (_: Exception) {
                // try next endpoint
            }
        }
        return null
    }

    private fun parseState(json: JSONObject?): Snapshot {
        if (json == null) {
            return Snapshot(0.0, 0L, 0, reachable = false, message = null)
        }
        val fid: Double = try {
            json.optJSONObject("frame")?.optDouble("bell_fidelity", 0.0) ?: 0.0
        } catch (_: Exception) { 0.0 }
        val pairs: Long = json.optLong("pairs_total", 0L)
        val bci = 432 // carrier fixed at 432 Hz by the orchestrator
        val message = if (fid > 0.0 && fid < 0.999) {
            "Fidelity ${"%.4f".format(fid)} — below target 0.999423, tuning loop active."
        } else if (fid >= 0.999) {
            "Pulse steady. Fidelity ${"%.6f".format(fid)} at target."
        } else {
            null
        }
        return Snapshot(fid, pairs, bci, reachable = true, message = message)
    }

    /** Poll once and persist the snapshot. Returns the snapshot. */
    suspend fun poll(context: Context): Snapshot = withContext(Dispatchers.IO) {
        val base = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .getString(KEY_URL, DEFAULT_URL) ?: DEFAULT_URL
        val snap = parseState(fetchRaw(base))
        if (snap.reachable) {
            context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
                .putFloat(KEY_FIDELITY, snap.fidelity.toFloat())
                .putLong(KEY_PAIRS, snap.pairs)
                .putInt(KEY_BCI, snap.bciHertz)
                .putLong(KEY_LAST_SEEN, System.currentTimeMillis())
                .apply()
        }
        snap
    }

    /** Send a user message to the orchestrator chat endpoint (best-effort). */
    suspend fun sendMessage(context: Context, text: String): Boolean = withContext(Dispatchers.IO) {
        val base = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .getString(KEY_URL, DEFAULT_URL) ?: DEFAULT_URL
        try {
            val conn = URL("$base/api/v1/chat").openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.doOutput = true
            conn.setRequestProperty("Content-Type", "application/json")
            conn.connectTimeout = TIMEOUT_MS
            conn.readTimeout = TIMEOUT_MS
            conn.outputStream.use { it.write(JSONObject().put("message", text).toString().toByteArray()) }
            val ok = conn.responseCode in 200..299
            conn.disconnect()
            ok
        } catch (_: Exception) {
            false
        }
    }
}
