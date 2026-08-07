"""Unit tests — orchestrator task lifecycle."""

from __future__ import annotations

import asyncio

from sovereign.orchestrator.core import SovereignOrchestrator


def test_submit_and_list_tasks():
    async def _run() -> None:
        orch = SovereignOrchestrator()
        await orch.start()
        task_id = await orch.submit_task("reason", {"input": "hello"}, priority=5)
        tasks = await orch.list_tasks()
        await orch.stop()
        assert task_id.startswith("task_")
        assert len(tasks) == 1
        assert tasks[0].status in ("pending", "running", "completed", "failed")

    asyncio.run(_run())


def test_state_machine_rejects_illegal_transitions():
    from sovereign.orchestrator.state_machine import TaskStateMachine

    sm = TaskStateMachine()
    sm.register("t1")
    sm.transition("t1", "running")
    sm.transition("t1", "completed")
    try:
        sm.transition("t1", "running")
        assert False, "illegal transition allowed"
    except ValueError:
        pass


def test_workflow_topo_sort():
    from sovereign.orchestrator.workflow_engine import WorkflowEngine

    nodes = {
        "a": {"task_type": "t", "depends_on": []},
        "b": {"task_type": "t", "depends_on": ["a"]},
        "c": {"task_type": "t", "depends_on": ["a", "b"]},
    }
    order = WorkflowEngine.topo_sort(nodes)
    assert order.index("a") < order.index("b") < order.index("c")
