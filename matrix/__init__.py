"""Reality Matrix — integration + evolution modules.

The matrix is the reality-simulation grid: entangled branches that mirror
the quantum engine, evolve recursively, and self-optimize by entropy
selection. Integration binds the matrix to live orchestrator state;
evolution drives recursive expansion.
"""

from .evolution import MatrixEvolution
from .integration import RealityBranch, RealityMatrix

__all__ = ["RealityMatrix", "RealityBranch", "MatrixEvolution"]
