"""Adapters that turn framework-specific runs into a Covenant Trajectory."""
from __future__ import annotations

from . import langgraph, manual

__all__ = ["manual", "langgraph"]
