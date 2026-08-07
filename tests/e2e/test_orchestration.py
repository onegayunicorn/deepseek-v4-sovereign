"""End-to-end — full orchestration loop over the real stack."""

from __future__ import annotations

import asyncio

from sovereign.orchestrator.core import SovereignOrchestrator


def test_full_loop():
    async def _run() -> None:
        orch = SovereignOrchestrator()
        await orch.start()

        # Submit a task and wait for terminal state.
        task_id = await orch.submit_task("reason", {"input": "e2e"}, max_retries=1)
        for _ in range(100):
            task = await orch.get_task(task_id)
            assert task is not None
            if task.status in ("completed", "failed", "cancelled"):
                break
            await asyncio.sleep(0.05)
        assert task.status in ("completed", "failed")

        # Audit trail recorded startup + task events.
        records = orch.audit_logger.tail(20)
        types = {r["event_type"] for r in records}
        assert "system.startup" in types
        assert any(t.startswith("task.") for t in types)

        await orch.stop()

    asyncio.run(_run())
