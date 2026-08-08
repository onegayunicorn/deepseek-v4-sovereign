"""Sovereign autonomous loop — Sense → Resonate → Entangle → Remember → Reason → Act.

PDF activation API::

    from sovereign.autonomous import AutonomousLoop
    loop = AutonomousLoop()
    loop.initialize()
    loop.start()
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

LOOP_PIPELINE = ["sense", "resonate", "entangle", "remember", "reason", "act"]


@dataclass
class LoopStep:
    name: str
    handler: Optional[Callable[[Dict[str, object]], Dict[str, object]]] = None


class AutonomousLoop:
    """Continuous sense-reason-act loop with pluggable step handlers."""

    def __init__(self) -> None:
        self.initialized = False
        self.running = False
        self.iterations = 0
        self.steps: List[LoopStep] = [LoopStep(name=name) for name in LOOP_PIPELINE]
        self.state: Dict[str, object] = {}
        self.period_s = 1.0
        self.max_iterations: Optional[int] = None

    def initialize(self) -> "AutonomousLoop":
        self.initialized = True
        self.state = {"pipeline": LOOP_PIPELINE[:], "continuous": True}
        return self

    def register(self, name: str, handler: Callable[[Dict[str, object]], Dict[str, object]]) -> None:
        for step in self.steps:
            if step.name == name:
                step.handler = handler

    def step_once(self) -> Dict[str, object]:
        """Run a single pass through the pipeline."""
        self.iterations += 1
        results: Dict[str, object] = {"iteration": self.iterations}
        for step in self.steps:
            if step.handler is not None:
                results[step.name] = step.handler(self.state)
            else:
                results[step.name] = {"status": "ok"}
        return results

    def start(self) -> None:
        """Run the loop (bounded by ``max_iterations`` when set)."""
        if not self.initialized:
            self.initialize()
        self.running = True
        try:
            while self.running:
                self.step_once()
                if self.max_iterations is not None and self.iterations >= self.max_iterations:
                    self.running = False
                    break
                time.sleep(self.period_s)
        except KeyboardInterrupt:
            self.running = False

    def stop(self) -> None:
        self.running = False

    def summary(self) -> Dict[str, object]:
        return {
            "initialized": self.initialized,
            "running": self.running,
            "iterations": self.iterations,
            "pipeline": LOOP_PIPELINE,
        }
