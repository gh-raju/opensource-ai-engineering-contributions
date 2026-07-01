"""Framework-agnostic adapter — build a Trajectory from a plain dict.

Useful for tests, for agents built without a supported framework, and as the canonical
serialization shape.

Shape::

    {
      "steps": [
        {
          "message": {"role": "assistant", "content": "...", "trust": "trusted"},
          "tool_calls": [
            {"name": "search_kb", "args": {...}, "influenced_by": "trusted", "scopes": [...]}
          ],
          "tokens": 0, "cost_usd": 0.0, "latency_ms": 0.0
        }
      ],
      "metadata": {}
    }
"""
from __future__ import annotations

from typing import Optional

from ..trajectory import Message, Step, ToolCall, Trajectory, Trust


def _tool_call(data: dict, step_index: int) -> ToolCall:
    return ToolCall(
        name=data["name"],
        args=dict(data.get("args", {})),
        result=data.get("result"),
        influenced_by=Trust.normalize(data.get("influenced_by")),
        scopes=list(data.get("scopes", [])),
        step_index=step_index,
    )


def _message(data: Optional[dict]) -> Optional[Message]:
    if data is None:
        return None
    return Message(
        role=data.get("role", "assistant"),
        content=data.get("content", ""),
        trust=Trust.normalize(data.get("trust")),
    )


def from_dict(data: dict) -> Trajectory:
    steps = []
    for i, step_data in enumerate(data.get("steps", [])):
        index = step_data.get("index", i)
        steps.append(
            Step(
                index=index,
                message=_message(step_data.get("message")),
                tool_calls=[_tool_call(t, index) for t in step_data.get("tool_calls", [])],
                tokens=step_data.get("tokens", 0),
                cost_usd=step_data.get("cost_usd", 0.0),
                latency_ms=step_data.get("latency_ms", 0.0),
            )
        )
    return Trajectory(steps=steps, metadata=dict(data.get("metadata", {})))
