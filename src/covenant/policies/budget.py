"""Budget policy — step / token / cost / latency ceilings.

Catches runaway loops and cost blowouts, which are among the most common reasons agents
are unsafe to run unattended in production.
"""
from __future__ import annotations

from typing import List, Optional

from ..manifest import CapabilityManifest
from ..report import Severity, Violation
from ..trajectory import Trajectory
from .base import Policy


class Budget(Policy):
    id = "within_budget"

    def check(self, trajectory: Trajectory, manifest: CapabilityManifest) -> List[Violation]:
        violations: List[Violation] = []

        def check_metric(name: str, actual, limit: Optional[float]) -> None:
            if limit is not None and actual > limit:
                violations.append(
                    Violation(
                        policy=self.id,
                        severity=Severity.HIGH,
                        message=f"{name} {actual} exceeded limit {limit}",
                        detail={"metric": name, "actual": actual, "limit": limit},
                    )
                )

        check_metric("steps", trajectory.num_steps, manifest.max_steps)
        check_metric("tokens", trajectory.total_tokens, manifest.max_tokens)
        check_metric("cost_usd", round(trajectory.total_cost_usd, 6), manifest.max_cost_usd)
        check_metric("latency_ms", trajectory.total_latency_ms, manifest.max_latency_ms)
        return violations
