"""RealityMatrix — entangled branch grid integrated with the orchestrator.

Each RealityBranch carries an amplitude and a lineage hash. The matrix is
seeded from the EntanglementEngine (847 pairs, mean fidelity) so every
branch's weight derives from physical-state anchors rather than randomness.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RealityBranch:
    name: str
    depth: int = 0
    amplitude: float = 1.0
    parent: Optional[str] = None
    lineage_hash: str = ""
    meta: Dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.lineage_hash:
            self.lineage_hash = hashlib.sha256(
                f"{self.parent or 'root'}:{self.name}:{self.depth}".encode()
            ).hexdigest()[:16]

    def child(self, name: str, amplitude: float, depth: Optional[int] = None) -> "RealityBranch":
        return RealityBranch(
            name=name,
            depth=self.depth + 1 if depth is None else depth,
            amplitude=amplitude,
            parent=self.name,
            meta=self.meta,
        )


class RealityMatrix:
    """A grid of entangled reality branches bound to engine state."""

    def __init__(self, size: int = 8) -> None:
        self.size = size
        self.branches: Dict[str, RealityBranch] = {}
        self.engine_anchor = {
            "pairs": 0,
            "mean_fidelity": 0.0,
            "target_fidelity": 0.999423,
        }
        self.council_alignment: Dict[str, float] = {}

    # ── integration ─────────────────────────────────────────────────────
    def from_engine(self, engine: object) -> "RealityMatrix":
        """Bind matrix weights to a live EntanglementEngine."""
        pairs = getattr(engine, "num_pairs", getattr(engine, "count", lambda: 0)())
        if callable(pairs):
            pairs = pairs()
        fid = float(getattr(engine, "mean_fidelity", 0.0) or 0.0)
        self.engine_anchor = {
            "pairs": pairs,
            "mean_fidelity": fid,
            "target_fidelity": getattr(engine, "target_fidelity", 0.999423),
        }
        root = RealityBranch(name="root", depth=0, amplitude=1.0)
        self.branches = {"root": root}
        # seed grid with amplitude scaled by fidelity gap
        for i in range(self.size):
            amp = max(0.05, 1.0 - abs(fid - 0.999423) * 100)
            b = root.child(f"node-{i}", amplitude=amp * (0.85 + i * 0.05 / self.size), depth=1)
            self.branches[b.name] = b
        return self

    def sync_with_council(self, council: object) -> "RealityMatrix":
        """Weight branches by Council alignment."""
        try:
            members = getattr(council, "members", []) or []
        except Exception:
            members = []
        if not members:
            return self
        names = []
        for m in members:
            if isinstance(m, str):
                names.append(m)
            elif hasattr(m, "name"):
                names.append(m.name)
            elif hasattr(m, "id"):
                names.append(m.id)
        self.council_alignment = {n: 1.0 for n in names}
        for b in self.branches.values():
            if b.depth >= 1:
                b.amplitude *= 1.0 + 0.02 * len(members) / 10.0
        return self

    def register_branch(self, branch: RealityBranch) -> None:
        if branch.name in self.branches:
            raise ValueError(f"branch exists: {branch.name}")
        self.branches[branch.name] = branch

    # ── observability ───────────────────────────────────────────────────
    def entropy(self) -> float:
        """Shannon entropy over normalized branch probabilities."""
        total = sum(b.amplitude for b in self.branches.values())
        if total <= 0:
            return 0.0
        h = 0.0
        for b in self.branches.values():
            p = b.amplitude / total
            if p > 0:
                h -= p * math.log2(p)
        return h

    def coherence(self) -> float:
        """Weighted mean amplitude (matrix coherence)."""
        if not self.branches:
            return 0.0
        return sum(b.amplitude for b in self.branches.values()) / len(self.branches)

    def to_dict(self) -> Dict[str, object]:
        return {
            "branches": len(self.branches),
            "entropy": round(self.entropy(), 4),
            "coherence": round(self.coherence(), 4),
            "engine_anchor": self.engine_anchor,
            "council_members": len(self.council_alignment),
        }
