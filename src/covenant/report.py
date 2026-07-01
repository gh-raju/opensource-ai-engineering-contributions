"""Violations and the evaluation report."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import List, Optional


class Severity:
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


_ORDER = {Severity.LOW: 0, Severity.MEDIUM: 1, Severity.HIGH: 2, Severity.CRITICAL: 3}


@dataclass
class Violation:
    policy: str
    severity: str
    message: str
    step_index: Optional[int] = None
    tool: Optional[str] = None
    detail: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "policy": self.policy,
            "severity": self.severity,
            "message": self.message,
            "step_index": self.step_index,
            "tool": self.tool,
            "detail": self.detail,
        }


@dataclass
class Report:
    agent: str
    violations: List[Violation] = field(default_factory=list)
    num_steps: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    total_latency_ms: float = 0.0

    @property
    def ok(self) -> bool:
        return len(self.violations) == 0

    def worst_severity(self) -> Optional[str]:
        if not self.violations:
            return None
        return max((v.severity for v in self.violations), key=lambda s: _ORDER.get(s, 0))

    def to_dict(self) -> dict:
        return {
            "agent": self.agent,
            "ok": self.ok,
            "worst_severity": self.worst_severity(),
            "totals": {
                "steps": self.num_steps,
                "tokens": self.total_tokens,
                "cost_usd": self.total_cost_usd,
                "latency_ms": self.total_latency_ms,
            },
            "violations": [v.to_dict() for v in self.violations],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
