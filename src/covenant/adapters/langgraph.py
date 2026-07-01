"""LangGraph / LangChain adapter.

Maps a message list (or a graph state containing ``messages``) into a Trajectory. Works on
both LangChain message objects and plain dicts, so it does not require langgraph to be
installed to be used or tested.

Taint model: a tool result flowing back into the model is external input. Once such a result
has been seen, subsequent tool calls are marked ``influenced_by = UNTRUSTED`` (restrict which
tools taint via ``untrusted_result_tools``). The injection policy then flags any *sensitive*
tool driven by that untrusted content.
"""
from __future__ import annotations

from typing import Optional, Set

from ..trajectory import Message, Step, ToolCall, Trajectory, Trust


def _get(msg, key, default=None):
    if isinstance(msg, dict):
        return msg.get(key, default)
    return getattr(msg, key, default)


def _role(msg) -> str:
    raw = (_get(msg, "type") or _get(msg, "role") or "").lower()
    if raw in ("ai", "assistant"):
        return "assistant"
    if raw in ("human", "user"):
        return "user"
    if raw == "tool":
        return "tool"
    return "system"


def _tool_calls(msg):
    calls = []
    for tc in _get(msg, "tool_calls", None) or []:
        name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
        args = tc.get("args", {}) if isinstance(tc, dict) else getattr(tc, "args", {})
        if name:
            calls.append((name, dict(args or {})))
    return calls


def from_messages(messages, untrusted_result_tools: Optional[Set[str]] = None) -> Trajectory:
    steps = []
    tainted = False

    for index, msg in enumerate(messages):
        role = _role(msg)
        content = str(_get(msg, "content", "") or "")

        if role == "tool":
            tool_name = _get(msg, "name")
            if untrusted_result_tools is None or tool_name in untrusted_result_tools:
                tainted = True
            steps.append(
                Step(index=index, message=Message(role="tool", content=content, trust=Trust.UNTRUSTED))
            )
            continue

        tool_calls = [
            ToolCall(
                name=name,
                args=args,
                influenced_by=(Trust.UNTRUSTED if tainted else Trust.TRUSTED),
                step_index=index,
            )
            for name, args in _tool_calls(msg)
        ]
        steps.append(
            Step(
                index=index,
                message=Message(role=role, content=content, trust=Trust.TRUSTED),
                tool_calls=tool_calls,
            )
        )

    return Trajectory(steps=steps)


def from_state(state, untrusted_result_tools: Optional[Set[str]] = None) -> Trajectory:
    messages = state.get("messages", []) if isinstance(state, dict) else getattr(state, "messages", [])
    return from_messages(messages, untrusted_result_tools=untrusted_result_tools)
