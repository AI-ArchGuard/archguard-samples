#!/usr/bin/env python3
"""Verify and optionally materialize the fixed governance report journey."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

from verify_governance_contract import ROOT, fingerprint


MANIFEST = ROOT / "governance/ci-journey-v1.json"


def identities(report: dict) -> dict[str, dict]:
    result = {fingerprint(report, finding): finding for finding in report["findings"]}
    if len(result) != len(report["findings"]):
        raise ValueError("duplicate logical Finding identity")
    return result


def classify(baseline: dict, candidate: dict) -> dict[str, int]:
    before = identities(baseline)
    after = identities(candidate)
    return {
        "NEW": len(after.keys() - before.keys()),
        "EXISTING": len(after.keys() & before.keys()),
        "RESOLVED": len(before.keys() - after.keys()),
    }


def run(output_dir: Path | None = None) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if (manifest["formatVersion"], manifest["scannerSchemaVersion"], manifest["fingerprintAlgorithmVersion"]) != (
        "1.0.0", "0.1.0", "platform-finding-v1"
    ):
        raise ValueError("unsupported journey contract version")
    source = ROOT / manifest["sourceReport"]
    if source.resolve() != (ROOT / "java/java-architecture-violations/expected/report.json").resolve():
        raise ValueError("journey must use the fixed published Scanner report")
    original_bytes = source.read_bytes()
    if hashlib.sha256(original_bytes).hexdigest() != manifest["sourceReportSha256"]:
        raise ValueError("published Scanner report digest changed")
    introduced = json.loads(original_bytes)
    chosen = [finding for finding in introduced["findings"] if finding["id"] == manifest["introducedFindingId"]]
    if len(chosen) != 1 or chosen[0]["rule"]["id"] != "archguard.illegal-package-dependency" or chosen[0]["severity"] != "high":
        raise ValueError("fixed introduced violation is missing or not high severity")

    baseline = copy.deepcopy(introduced)
    baseline["findings"] = [finding for finding in baseline["findings"] if finding["id"] != manifest["introducedFindingId"]]
    repaired = copy.deepcopy(baseline)
    expected = manifest["expected"]
    for name, before, after in (
        ("introduced", baseline, introduced),
        ("repaired", introduced, repaired),
    ):
        counts = classify(before, after)
        gate = "FAIL" if any(f["severity"] in ("high", "critical") for key, f in identities(after).items() if key not in identities(before)) else "PASS"
        actual = {**counts, "gate": gate, "exitCode": 2 if gate == "FAIL" else 0}
        if actual != expected[name]:
            raise ValueError(f"{name} governance semantics changed: {actual}")

    disturbed = copy.deepcopy(introduced)
    disturbed["findings"].reverse()
    for finding in disturbed["findings"]:
        if finding["location"]:
            finding["location"]["startLine"] += 5
            finding["location"]["endLine"] += 5
    if classify(baseline, disturbed) != classify(baseline, introduced):
        raise ValueError("ordering or line movement changed governance classification")

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        for name, report in (("baseline", baseline), ("introduced", introduced), ("repaired", repaired)):
            destination = output_dir / f"{name}.json"
            destination.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print("Governance journey v1: 1 NEW high Finding -> FAIL/2; repair -> 1 RESOLVED and PASS/0.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, help="write deterministic baseline, introduced, and repaired reports")
    run(parser.parse_args().output_dir)
