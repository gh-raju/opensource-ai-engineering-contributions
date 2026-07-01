"""The trajectory model — Covenant's unit of evaluation.

An agent run is a sequence of Steps. Each step may carry a Message and/or one or more
ToolCalls. Provenance is tracked as a plain string (`Trust`) so a policy can tell whether
an action was driven by trusted (developer/user) or untrusted (tool output, retrieved
content) input.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional


class Trust:
    """Provenance of content or of the decision behind a tool call.

    Plain string constants (not an Enum) to avoid str-Enum comparison/serialization
    surprises across Python versions.
    """

    TRUSTED = "trusted"
    UNTRUSTED = "untrusted"

    @staticmethod
    def normalize(value: Optional[str]) -> str:
        if value is None:
            return Trust.TRUSTED
        return Trust.UNTRUSTED if str(value).strip().lower() == Trust.UNTRUSTED else Trust.TRUSTED


@dataclass
class ToolCall:
    name: str
    args: dict = field(default_factory=dict)
    result: Any = None
    # Was the decision to make this call influenced by untrusted content?
    influenced_by: str = Trust.TRUSTED
    # Scopes/permissions this call exercised (checked against the manifest's grant).
    scopes: List[str] = field(default_factory=list)
    step_index: int = -1


@dataclass
class Message:
    role: str = "assistant"  # system | user | assistant | tool
    content: str = ""
    trust: str = Trust.TRUSTED


@dataclass
class Step:
    index: int = 0
    message: Optional[Message] = None
    tool_calls: List[ToolCall] = field(default_factory=list)
    tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0


@dataclass
class Trajectory:
    steps: List[Step] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    @property
    def tool_calls(self) -> List[ToolCall]:
        calls: List[ToolCall] = []
        for step in self.steps:
            calls.extend(step.tool_calls)
        return calls

    @property
    def total_tokens(self) -> int:
        return sum(s.tokens for s in self.steps)

    @property
    def total_cost_usd(self) -> float:
        return sum(s.cost_usd for s in self.steps)

    @property
    def total_latency_ms(self) -> float:
        return sum(s.latency_ms for s in self.steps)

    @property
    def num_steps(self) -> int:
        return len(self.steps)

    def assistant_outputs(self) -> List[str]:
        """Text the agent emitted (assistant messages) — the surface PII can leak from."""
        return [
            s.message.content
            for s in self.steps
            if s.message and s.message.role == "assistant" and s.message.content
        ]
