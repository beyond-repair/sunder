"""SUNDER — local-first autonomous coding agent."""

from sunder.agent import Agent
from sunder.fork import VersionFork
from sunder.gate import ConstitutionalGate
from sunder.vsa import VSAMemory

__version__ = "0.1.0"
__all__ = ["Agent", "VSAMemory", "ConstitutionalGate", "VersionFork"]
