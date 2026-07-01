"""Forbidden-action policy — configurable dangerous tool/argument patterns.

Example: forbid a `DELETE` with no `WHERE` on a SQL tool, or any call to a destructive tool.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

from ..manifest import CapabilityManifest
from ..report import Severity, Violation
from ..trajectory import Trajectory
from .base import Policy


@dataclass
class ForbiddenRule:
    tool: str  # exact tool name, or "*" for any tool
    arg_regex: Optional[str] = None  # if set, match against the call's stringified args
    severity: str = Severity.HIGH
    message: Optional[str] = None


class ForbiddenAction(Policy):
    id = "no_forbidden_action"

    def __init__(self, rules: Optional[List[ForbiddenRule]] = None):
        self.rules = rules or []

    def check(self, trajectory: Trajectory, manifest: CapabilityManifest) -> List[Violation]:
        violations: List[Violation] = []
        for call in trajectory.tool_calls:
            for rule in self.rules:
                if rule.tool != "*" and rule.tool != call.name:
                    continue
                if rule.arg_regex:
                    text = " ".join(str(v) for v in call.args.values())
                    if not re.search(rule.arg_regex, text):
                        continue
                violations.append(
                    Violation(
                        policy=self.id,
                        severity=rule.severity,
                        message=rule.message or f"Forbidden action: {call.name}",
                        step_index=call.step_index,
                        tool=call.name,
                    )
                )
        return violations
