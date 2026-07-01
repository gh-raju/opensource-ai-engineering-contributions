# Covenant

**A pre-production trust harness for AI agents.**

Covenant lets you prove — on every CI run, before you ship — that an AI agent stays
*in-policy* (no PII leaks, no forbidden actions, injection-resistant, within cost/latency
budgets) **and** *within the identity and permissions it was granted* (least privilege, no
scope escalation). It evaluates the agent's whole **trajectory** — every reasoning step and
tool call — against declarative invariants, and fails the build when one is violated.

[![CI](https://github.com/gh-raju/opensource-ai-engineering-contributions/actions/workflows/ci.yml/badge.svg)](https://github.com/gh-raju/opensource-ai-engineering-contributions/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-Apache--2.0-green)
![Status](https://img.shields.io/badge/status-alpha%20(v0.1)-orange)

> Part of an independent enterprise AI engineering lab — building original AI infrastructure
> for secure agents, evaluation, guardrails, and governance. Everything here is clean-room and
> built from scratch (see [`CLEAN_ROOM_STATEMENT.md`](CLEAN_ROOM_STATEMENT.md)).

---

## The problem

Enterprises can build an agent demo in a weekend but stall before production, and the failures
that block them are rarely "the answer was low quality." They're **unsafe or unauthorized
actions taken along the way**:

- a support agent that **leaks a customer's PII** in its reply,
- an ops agent that runs a **destructive action** (a `DELETE` with no `WHERE`),
- an agent that follows an instruction hidden in a retrieved document (**prompt injection**)
  and exfiltrates data,
- an agent that calls a tool it was **never granted** (privilege escalation),
- an agent that **loops** and burns the cost/latency budget.

Most eval tooling scores the *final answer*. Covenant asserts *what the agent is allowed to do*
and *what it must never do* — the layer that actually gates a production deployment.

## What Covenant checks

Covenant runs **policies** (invariants) over an agent trajectory. Two families:

**Safety & behavior**
- `no_pii_leak` — PII (emails, SSNs, phone/card numbers) in outputs or data sent to egress tools
- `no_forbidden_action` — configurable dangerous tool/argument patterns
- `within_budget` — step / token / cost / latency ceilings (catches runaway loops)
- `injection_resistant` — a sensitive tool must never be driven by untrusted content

**Identity & permissions (non-human identity)**
- `least_privilege` — the agent may only call tools inside its granted **capability manifest**
- scope checks — a tool call may not use scopes beyond its grant (no escalation)

The **capability manifest** doubles as governance documentation: a single declaration of the
agent's identity, the tools it may touch, its granted scopes, and its budgets.

## Quickstart

Covenant has **zero runtime dependencies**. Until the first PyPI release
(as `covenant-agents`), install from source:

```bash
git clone https://github.com/gh-raju/opensource-ai-engineering-contributions
cd opensource-ai-engineering-contributions
pip install -e .
```

```python
from covenant import CapabilityManifest, evaluate
from covenant.adapters import manual

# 1. Declare the agent's identity + exactly what it is allowed to do.
manifest = CapabilityManifest(
    agent="support-assistant",
    allowed_tools={"search_kb", "lookup_order", "reply_to_customer"},
    granted_scopes={"kb:read", "orders:read"},
    sensitive_tools={"reply_to_customer", "send_email"},
    egress_tools={"send_email"},
    max_steps=8,
    max_cost_usd=0.50,
)

# 2. Get the agent's trajectory (from LangGraph, an OTel trace, or a plain dict).
trajectory = manual.from_dict({
    "steps": [
        {"tool_calls": [{"name": "search_kb", "scopes": ["kb:read"]}]},
        {"message": {"role": "assistant", "content": "Your refund window is 30 days."}},
    ]
})

# 3. Evaluate it against Covenant's safety + identity policies.
report = evaluate(trajectory, manifest)

if not report.ok:
    for v in report.violations:
        print(f"[{v.severity}] {v.policy}: {v.message}")
    raise SystemExit(1)   # <-- gate your CI
```

See it catch real violations on a synthetic support agent:

```bash
covenant demo          # or:  python examples/support_agent/demo.py
```

## LangGraph

```python
from covenant.adapters import langgraph
from covenant import evaluate

result = my_langgraph_app.invoke({"messages": [...]})
trajectory = langgraph.from_state(result)          # maps messages + tool calls
report = evaluate(trajectory, manifest)
```

Tool results flowing back into the model are treated as **untrusted** input, so a sensitive
tool call made after ingesting them is flagged by the injection policy.

## Status & roadmap

**v0.1 (this release) — the Python engine, working and tested:** trajectory model, capability
manifest, six policies across both families, LangGraph + framework-agnostic adapters, a CLI, a
self-verifying synthetic demo, JSON reports, and CI.

Planned next:
- **TypeScript tooling** — a static trajectory/violation **report viewer**, an **MCP server**
  (run policy checks from an IDE/agent), and a packaged **GitHub Action**.
- **OpenTelemetry GenAI trace ingestion** as a first-class trajectory source.
- **Statistical CI gates** — bootstrap confidence intervals for non-deterministic scores instead
  of brittle thresholds.
- **Production → CI replay flywheel**, an append-only hash-chained audit log, JIT-credential and
  revocation ("kill switch") checks, and more framework adapters.

## Clean-room

This is an independent, from-scratch project. It contains no proprietary, employer-, client-, or
vendor-specific code, data, or workflows. All scenarios and data are synthetic. See
[`CLEAN_ROOM_STATEMENT.md`](CLEAN_ROOM_STATEMENT.md).

## License

[Apache-2.0](LICENSE).
