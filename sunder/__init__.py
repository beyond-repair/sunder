"""SUNDER — local-first coding-agent sketch (no supervisor model)."""

from sunder.agent import Agent
from sunder.fork import ForkManager, VersionFork
from sunder.gate import ConstitutionalGate
from sunder.vsa import VSAMemory

__version__ = "0.1.1"
__all__ = [
    "Agent",
    "VSAMemory",
    "ConstitutionalGate",
    "VersionFork",
    "ForkManager",
]
