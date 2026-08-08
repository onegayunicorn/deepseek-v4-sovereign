"""Reality Matrix tests — integration + evolution."""

import asyncio
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _engine():
    from quantum.entanglement_engine import EntanglementEngine

    eng = EntanglementEngine()
    eng.initialize()
    eng.generate_pairs()
    return eng


def test_matrix_integrates_engine():
    from matrix.integration import RealityMatrix

    eng = _engine()
    m = RealityMatrix(size=8).from_engine(eng)
    assert m.engine_anchor["pairs"] == 847
    assert m.engine_anchor["mean_fidelity"] > 0.99
    assert len(m.branches) == 1 + 8  # root + 8 seeded nodes
    assert "root" in m.branches
    assert m.coherence() > 0.0


def test_matrix_entropy_bounded():
    from matrix.integration import RealityMatrix

    m = RealityMatrix(size=8).from_engine(_engine())
    h = m.entropy()
    # entropy of a non-degenerate distribution on 9 branches
    assert 0 < h <= 4.0


def test_matrix_sync_council():
    from agi.omega_v3.council_of_10 import CouncilOf10

    from matrix.integration import RealityMatrix

    c = CouncilOf10()
    names = ["Nexus", "Wisdom", "Power", "Harmony", "Creation", "Transcendence",
             "Order", "Freedom", "Evolution", "Forge"]
    for n in names:
        c.seat(n)
    m = RealityMatrix(size=4).from_engine(_engine()).sync_with_council(c)
    assert len(m.council_alignment) == 10


def test_evolution_expands_recursively():
    from matrix.evolution import MatrixEvolution
    from matrix.integration import RealityMatrix

    m = RealityMatrix(size=4).from_engine(_engine())
    ev = MatrixEvolution(m, growth=2, amplitude_floor=0.05)
    r1 = ev.run_epoch(epoch=1)
    assert r1.branches_after > r1.branches_before  # expansion happened
    assert r1.max_depth >= 2
    # lineage hashes unique
    lin = ev.lineage()
    assert len(lin) == len(set(lin))


@pytest.mark.asyncio
async def test_evolution_epochs_report():
    from matrix.evolution import MatrixEvolution
    from matrix.integration import RealityMatrix

    m = RealityMatrix(size=4).from_engine(_engine())
    ev = MatrixEvolution(m, growth=2, amplitude_floor=0.10)
    reports = await ev.evolve(rounds=3)
    assert len(reports) == 3
    assert all(r.entropy > 0 for r in reports)
    assert all(r.coherence > 0 for r in reports)
    # self-optimization: coherence stays bounded, no runaway growth
    assert reports[-1].coherence < 2.0


def test_evolution_depth_cap():
    from matrix.evolution import MatrixEvolution
    from matrix.integration import RealityMatrix

    m = RealityMatrix(size=2).from_engine(_engine())
    ev = MatrixEvolution(m, growth=3, amplitude_floor=0.001)
    for _ in range(8):
        ev.run_epoch()
    assert ev._max_depth() <= 12


def test_matrix_module_registry_entry():
    import yaml

    with open(ROOT / "modules" / "matrix-module.yaml") as f:
        mod = yaml.safe_load(f)
    assert mod["id"] == "matrix"
    assert mod["package"] == "matrix"
    assert "evolution" in str(mod["capabilities"])
