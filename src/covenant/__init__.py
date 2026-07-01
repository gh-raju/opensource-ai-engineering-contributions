"""Covenant — a pre-production trust harness for AI agents.

Evaluate an agent's full trajectory (reasoning steps + tool calls) against declarative
safety, policy, and identity/permission invariants, and gate CI on the result.
"""
from __future__ import annotations

from .trajectory import Trajectory, Step, ToolCall, Message, Trust
from .manifest import CapabilityManifest
from .report import Report, Violation, Severity
from .engine import evaluate, default_policies
from . import adapters, policies

__version__ = "0.1.0"

__all__ = [
    "Trajectory",
    "Step",
    "ToolCall",
    "Message",
    "Trust",
    "CapabilityManifest",
    "Report",
    "Violation",
    "Severity",
    "evaluate",
    "default_policies",
    "adapters",
    "policies",
    "__version__",
]
