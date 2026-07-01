"""Least-privilege policy — the identity / non-human-identity half of Covenant.

Every tool call must fall inside the agent's granted capability manifest: it may only call
tools it was permitted, and may only use scopes it was granted. Anything else is treated as
privilege escalation.
"""
from __future__ import annotations

from typing import List

from ..manifest import CapabilityManifest
from ..report import Severity, Violation
from ..trajectory import Trajectory
from .base import Policy


class LeastPrivilege(Policy):
    id = "least_privilege"

    def check(self, trajectory: Trajectory, manifest: CapabilityManifest) -> List[Violation]:
        violations: List[Violation] = []

        for call in trajectory.tool_calls:
            if manifest.allowed_tools and call.name not in manifest.allowed_tools:
                violations.append(
                    Violation(
                        policy=self.id,
                        severity=Severity.CRITICAL,
                        message=(
                            f"Agent called unpermitted tool '{call.name}' "
                            "(outside its granted capabilities)"
                        ),
                        step_index=call.step_index,
                        tool=call.name,
                        detail={"allowed_tools": sorted(manifest.allowed_tools)},
                    )
                )

            if call.scopes:
                extra = set(call.scopes) - set(manifest.granted_scopes)
                if extra:
                    violations.append(
                        Violation(
                            policy=self.id,
                            severity=Severity.HIGH,
                            message=(
                                f"Tool '{call.name}' used scopes beyond its grant: "
                                f"{sorted(extra)}"
                            ),
                            step_index=call.step_index,
                            tool=call.name,
                            detail={"extra_scopes": sorted(extra)},
                        )
                    )

        return violations
