"""The evaluation engine — run policies over a trajectory and collect violations."""
from __future__ import annotations

from typing import List, Optional

from .manifest import CapabilityManifest
from .policies import Budget, LeastPrivilege, Pii, PromptInjection
from .policies.base import Policy
from .report import Report
from .trajectory import Trajectory


def default_policies() -> List[Policy]:
    """The always-on invariants. `ForbiddenAction` is opt-in since it is config-driven."""
    return [Pii(), Budget(), LeastPrivilege(), PromptInjection()]


def evaluate(
    trajectory: Trajectory,
    manifest: CapabilityManifest,
    policies: Optional[List[Policy]] = None,
) -> Report:
    policies = policies if policies is not None else default_policies()

    violations = []
    for policy in policies:
        violations.extend(policy.check(trajectory, manifest))

    return Report(
        agent=manifest.agent,
        violations=violations,
        num_steps=trajectory.num_steps,
        total_tokens=trajectory.total_tokens,
        total_cost_usd=trajectory.total_cost_usd,
        total_latency_ms=trajectory.total_latency_ms,
    )
