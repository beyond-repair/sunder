"""Hyperspherical FHRR memory for project state.

Compositional, invertible, offline. Not just RAG.
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

DEFAULT_DIM = 4096

def _unit(dim: int, rng: np.random.Generator) -> np.ndarray:
    phases = rng.uniform(0, 2 * np.pi, size=dim)
    v = np.exp(1j * phases).astype(np.complex128)
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else v

def _norm(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=np.complex128)
    n = np.linalg.norm(v)
    return (v / n).astype(np.complex128) if n >= 1e-12 else v

@dataclass
class VSAMemory:
    """Project-level compositional memory."""
    dim: int = DEFAULT_DIM
    seed: Optional[int] = None
    codebook: Dict[str, np.ndarray] = field(default_factory=dict)
    meta: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    _rng: np.random.Generator = field(init=False)

    def __post_init__(self):
        self._rng = np.random.default_rng(self.seed)

    def bind(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        return _norm(a * b)

    def unbind(self, composite: np.ndarray, binder: np.ndarray) -> np.ndarray:
        return _norm(composite * np.conj(binder))

    def similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        return float(np.real(np.vdot(a, b)))

    def register(self, name: str, vec: Optional[np.ndarray] = None, **meta) -> np.ndarray:
        if vec is None:
            vec = _unit(self.dim, self._rng)
        vec = _norm(vec)
        self.codebook[name] = vec
        self.meta[name] = {"ts": time.time(), **meta}
        return vec

    def get(self, name: str) -> Optional[np.ndarray]:
        return self.codebook.get(name)

    def query(self, probe: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        scores = [(n, self.similarity(probe, v)) for n, v in self.codebook.items()]
        scores.sort(key=lambda t: -t[1])
        return scores[:top_k]

    def remember_file(self, path: Path, content: str) -> str:
        """Bind a file into the project memory."""
        key = f"file:{path.as_posix()}"
        h = int(hashlib.sha256(content.encode()).hexdigest()[:16], 16)
        rng = np.random.default_rng(h)
        vec = _unit(self.dim, rng)
        self.register(key, vec, path=str(path), size=len(content))
        return key

    def stats(self) -> Dict[str, Any]:
        return {
            "size": len(self.codebook),
            "dim": self.dim,
            "keys": list(self.codebook.keys())[:20],
        }
