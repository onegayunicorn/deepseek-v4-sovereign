package ai.sovereign.orchestrator

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import android.content.Intent
import android.widget.RemoteViews

/**
 * SovereignWidget — home-screen telemetry widget.
 *
 * Shows the last-known fidelity / pairs / BCI snapshot cached by
 * [BubbleService] (via [RoamingAgentClient.poll]); tapping it opens the
 * dashboard. Values update on widget refresh and whenever the companion
 * service polls the orchestrator.
 */
class SovereignWidget : AppWidgetProvider() {

    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        for (id in appWidgetIds) {
            appWidgetManager.updateAppWidget(id, buildViews(context))
        }
    }

    companion object {
        fun buildViews(context: Context): RemoteViews {
            val prefs = context.getSharedPreferences(RoamingAgentClient.PREFS, Context.MODE_PRIVATE)
            val fid = prefs.getFloat(RoamingAgentClient.KEY_FIDELITY, 0f)
            val pairs = prefs.getLong(RoamingAgentClient.KEY_PAIRS, 0L)
            val bci = prefs.getInt(RoamingAgentClient.KEY_BCI, 0)
            val lastSeen = prefs.getLong(RoamingAgentClient.KEY_LAST_SEEN, 0L)

            val views = RemoteViews(context.packageName, R.layout.sovereign_widget)
            views.setTextViewText(
                R.id.widget_fidelity,
                if (fid > 0f) "F ${"%.6f".format(fid)}" else "F —"
            )
            views.setTextViewText(R.id.widget_pairs, "$pairs pairs")
            views.setTextViewText(R.id.widget_bci, if (bci > 0) "$bci Hz" else "BCI —")

            val open = PendingIntent.getActivity(
                context, 0,
                Intent(context, MainActivity::class.java),
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
            views.setOnClickPendingIntent(R.id.widget_root, open)
            return views
        }

        /** Called by the companion service after each successful poll. */
        fun pushUpdate(context: Context) {
            val mgr = AppWidgetManager.getInstance(context)
            val ids = mgr.getAppWidgetIds(
                android.content.ComponentName(context, SovereignWidget::class.java)
            )
            if (ids.isNotEmpty()) {
                for (id in ids) mgr.updateAppWidget(id, buildViews(context))
            }
        }
    }
}
