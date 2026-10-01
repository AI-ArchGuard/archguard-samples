"""Validate the fixed synthetic case inventory, not a production model or Evals runtime."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
cases = json.loads((ROOT / "agent/hardening-cases-v1.json").read_text(encoding="utf-8"))
assert cases["formatVersion"] == "1.0.0"
assert cases["agentSchemaVersion"] == cases["scannerSchemaVersion"] == "0.1.0"
assert cases["scope"] == "SYNTHETIC_ONLY" and cases["runtime"] == "NO_FORMAL_EVALS"
assert cases["sourceRequest"] == "agent/request-vectors.json"
assert cases["limits"] == {"inputTokens": 8000, "outputTokens": 1500, "requestMicrousd": 100000,
                           "projectDailyMicrousd": 5000000, "deploymentDailyMicrousd": 20000000}
assert cases["invariants"] == {"liveProviderCalls": 0, "automaticRetries": 0, "gateChanges": 0, "scannerSchemaChanges": 0}
assert {case["id"] for case in cases["cases"]} == {f"AG-{i:03}" for i in range(1, 15)}
assert len(cases["cases"]) == 14
assert {case["category"] for case in cases["cases"]} == {"injection", "authorization", "validation", "idempotency",
                                                       "timeout", "quota", "recovery", "audit", "isolation", "web"}
for case in cases["cases"]:
    assert set(case) == {"id", "category", "input", "expected", "runtimeTest"}
    assert all(isinstance(value, str) and value for value in case.values())
    assert case["runtimeTest"].startswith(("Platform:", "Web:"))
print("14 synthetic Agent hardening case definitions verified; runtime tests remain in Platform/Web; no live calls")
