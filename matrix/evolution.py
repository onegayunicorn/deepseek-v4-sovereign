"""MatrixEvolution — recursive expansion of the reality matrix.

Evolution protocol per epoch:
  1. expand  — every branch spawns children with quantum-evolved amplitude
              (Hadamard-style superposition: (a + b) / sqrt(2))
  2. evolve  — apply a quantum phase rotation to amplitudes
  3. select  — prune branches below the entropy-weighted amplitude floor
  4. optimize— report coherence/entropy so callers can tune the floor

The result is a self-optimizing recursive structure that grows while
staying coherent.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List

from .integration import RealityBranch, RealityMatrix


@dataclass
class EpochReport:
    epoch: int
    branches_before: int
    branches_after: int
    entropy: float
    coherence: float
    pruned: int
    max_depth: int
    meta: Dict[str, object] = field(default_factory=dict)


class MatrixEvolution:
    def __init__(
        self,
        matrix: RealityMatrix,
        growth: int = 2,
        amplitude_floor: float = 0.05,
        phase_step: float = 0.35,
    ) -> None:
        self.matrix = matrix
        self.growth = growth
        self.amplitude_floor = amplitude_floor
        self.phase_step = phase_step
        self.history: List[EpochReport] = []

    # ── protocol steps ──────────────────────────────────────────────────
    def _expand(self) -> None:
        new: Dict[str, RealityBranch] = {}
        for b in list(self.matrix.branches.values()):
            for i in range(self.growth):
                if b.depth >= 12:  # depth cap keeps the grid bounded
                    continue
                # Hadamard-style superposition of parent + sibling
                a = (b.amplitude + 1.0) / math.sqrt(2.0) * 0.85
                child = b.child(f"{b.name}:{i}", amplitude=max(0.01, a), depth=b.depth + 1)
                new[child.name] = child
        for name, br in new.items():
            if name not in self.matrix.branches:
                self.matrix.branches[name] = br

    def _evolve(self) -> None:
        for b in self.matrix.branches.values():
            # quantum phase rotation: amplitude wobbles but never collapses
            b.amplitude *= 0.5 + 0.5 * math.cos(b.depth * self.phase_step)
            b.amplitude = max(0.001, b.amplitude)

    def _select(self) -> int:
        before = len(self.matrix.branches)
        # entropy-scaled floor: more disorder → keep more branches
        ent = self.matrix.entropy()
        floor = self.amplitude_floor * (1.0 + ent * 0.05)
        keep = {n: b for n, b in self.matrix.branches.items() if b.depth == 0 or b.amplitude >= floor}
        self.matrix.branches = keep
        return before - len(keep)

    def _max_depth(self) -> int:
        return max((b.depth for b in self.matrix.branches.values()), default=0)

    # ── entry points ────────────────────────────────────────────────────
    def run_epoch(self, epoch: int = 1) -> EpochReport:
        before = len(self.matrix.branches)
        self._expand()
        self._evolve()
        pruned = self._select()
        report = EpochReport(
            epoch=epoch,
            branches_before=before,
            branches_after=len(self.matrix.branches),
            entropy=round(self.matrix.entropy(), 4),
            coherence=round(self.matrix.coherence(), 4),
            pruned=pruned,
            max_depth=self._max_depth(),
        )
        self.history.append(report)
        return report

    async def evolve(self, rounds: int = 3) -> List[EpochReport]:
        reports = []
        for i in range(1, rounds + 1):
            reports.append(self.run_epoch(epoch=i))
        return reports

    def lineage(self) -> List[str]:
        """Branch lineage hashes ordered by depth."""
        return [b.lineage_hash for b in sorted(self.matrix.branches.values(), key=lambda x: (x.depth, x.name))]
