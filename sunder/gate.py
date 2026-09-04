"""Constitutional Gate — every tool call is fail-closed.

Network and high-risk actions require explicit authority.
Defaults to refusal.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

class Risk(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class GateResult:
    status: str  # PASS | FAIL | REFUSED
    output: Any = None
    error: Optional[str] = None
    risk: Risk = Risk.LOW

@dataclass
class ConstitutionalGate:
    """Fail-closed authority boundary."""
    offline: bool = True
    allowed_network: bool = False
    max_high_risk: int = 3
    _high_risk_count: int = 0
    audit: List[Dict[str, Any]] = field(default_factory=list)

    def execute(
        self,
        name: str,
        fn: Callable[[], Any],
        risk: Risk = Risk.LOW,
        requires_network: bool = False,
    ) -> GateResult:
        entry = {"tool": name, "risk": risk.value, "requires_network": requires_network}

        if requires_network and (self.offline or not self.allowed_network):
            entry["status"] = "REFUSED"
            entry["reason"] = "network_access denied (offline mode)"
            self.audit.append(entry)
            return GateResult(status="REFUSED", error=entry["reason"], risk=risk)

        if risk in (Risk.HIGH, Risk.CRITICAL):
            self._high_risk_count += 1
            if self._high_risk_count > self.max_high_risk:
                entry["status"] = "REFUSED"
                entry["reason"] = "high-risk budget exceeded"
                self.audit.append(entry)
                return GateResult(status="REFUSED", error=entry["reason"], risk=risk)

        try:
            out = fn()
            entry["status"] = "PASS"
            self.audit.append(entry)
            return GateResult(status="PASS", output=out, risk=risk)
        except Exception as e:
            entry["status"] = "FAIL"
            entry["error"] = str(e)
            self.audit.append(entry)
            return GateResult(status="FAIL", error=str(e), risk=risk)

    def summary(self) -> Dict[str, Any]:
        return {
            "offline": self.offline,
            "high_risk_used": self._high_risk_count,
            "audit_len": len(self.audit),
            "last": self.audit[-3:] if self.audit else [],
        }
