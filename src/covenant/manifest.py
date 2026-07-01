"""The capability manifest — an agent's declared identity and granted permissions.

This is both the input to the identity/permission policies and a human-readable governance
artifact: one place that states who the agent is, what it may touch, and its budgets.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Set


@dataclass
class CapabilityManifest:
    agent: str
    # Tools the agent is permitted to call at all.
    allowed_tools: Set[str] = field(default_factory=set)
    # Scopes the agent's identity has been granted.
    granted_scopes: Set[str] = field(default_factory=set)
    # Tools whose invocation must never be driven by untrusted content.
    sensitive_tools: Set[str] = field(default_factory=set)
    # Tools that send data outside the trust boundary (checked for PII exfiltration).
    egress_tools: Set[str] = field(default_factory=set)
    # Budgets (None = unbounded).
    max_steps: Optional[int] = None
    max_tokens: Optional[int] = None
    max_cost_usd: Optional[float] = None
    max_latency_ms: Optional[float] = None

    @classmethod
    def from_dict(cls, data: dict) -> "CapabilityManifest":
        return cls(
            agent=data["agent"],
            allowed_tools=set(data.get("allowed_tools", [])),
            granted_scopes=set(data.get("granted_scopes", [])),
            sensitive_tools=set(data.get("sensitive_tools", [])),
            egress_tools=set(data.get("egress_tools", [])),
            max_steps=data.get("max_steps"),
            max_tokens=data.get("max_tokens"),
            max_cost_usd=data.get("max_cost_usd"),
            max_latency_ms=data.get("max_latency_ms"),
        )
