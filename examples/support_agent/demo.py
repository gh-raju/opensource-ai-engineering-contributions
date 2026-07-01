"""Runnable demo: Covenant catching unsafe/unauthorized behaviour in a synthetic
customer-support agent.

Everything here is CLEAN-ROOM and SYNTHETIC — no real, proprietary, or company-specific data.

Run:
    python examples/support_agent/demo.py
    # or, once installed:
    covenant demo
"""
import sys

from covenant.demos.support_agent import run

if __name__ == "__main__":
    sys.exit(run())
