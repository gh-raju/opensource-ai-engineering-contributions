"""Base policy interface."""
from __future__ import annotations

from typing import List

from ..manifest import CapabilityManifest
from ..report import Violation
from ..trajectory import Trajectory


class Policy:
    """A policy inspects a trajectory against a manifest and returns any violations."""

    id = "policy"

    def check(self, trajectory: Trajectory, manifest: CapabilityManifest) -> List[Violation]:
        raise NotImplementedError
