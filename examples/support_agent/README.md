# Example: synthetic customer-support agent

A fully **synthetic, clean-room** example (no real or proprietary data) showing Covenant
evaluating an agent's trajectory across six scenarios:

| scenario | expected | what Covenant catches |
|---|---|---|
| `benign` | PASS | in-policy, in-scope run |
| `pii_leak` | BLOCK | SSN + email in the agent's reply |
| `prompt_injection` | BLOCK | a sensitive tool driven by untrusted tool output |
| `privilege_escalation` | BLOCK | a tool call outside the granted capability manifest |
| `runaway_loop` | BLOCK | step/token budget exceeded |
| `destructive_sql` | BLOCK | a `DELETE` with no `WHERE` clause |

Run it:

```bash
python examples/support_agent/demo.py     # or: covenant demo
```

Exit code is `0` only if Covenant's verdict matched the expectation on every scenario
(benign passes, all unsafe runs are blocked), so this doubles as an integration test in CI.

The scenario definitions live in
[`src/covenant/demos/support_agent.py`](../../src/covenant/demos/support_agent.py).
