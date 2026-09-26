#!/usr/bin/env python3
"""Scan fixed synthetic source revisions and verify the governance transition."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from verify_governance_contract import ROOT, fingerprint


FIXTURE = ROOT / "governance/java-ci-journey"
EXPECTED_DIGESTS = {
    "baseline": "459476dfab63b78ab40fb5e1845b129999290d1f164bf978b86ff65cfb4e44bf",
    "introduced": "2b9b3e72f891f3174fb188b9903b9a58f21d93f291872358199d3725f07caaba",
}


def scan(scanner_jar: Path, source: str, output: Path, exit_code: int) -> dict:
    root = FIXTURE / source
    process = subprocess.run(
        ["java", "-jar", str(scanner_jar), "scan", str(root),
         "--rules", str(root / "archguard-rules.yaml"), "--output", str(output)],
        capture_output=True, text=True, check=False,
    )
    if process.returncode != exit_code:
        raise ValueError(f"{source} Scanner exit {process.returncode}, expected {exit_code}")
    data = output.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_DIGESTS[source]:
        raise ValueError(f"{source} Scanner report changed: {digest}")
    report = json.loads(data)
    if report["schemaVersion"] != "0.1.0" or report["project"]["identity"] != "samples:java-ci-journey":
        raise ValueError("Scanner contract or project identity changed")
    return report


def finding_keys(report: dict) -> set[str]:
    keys = {fingerprint(report, finding) for finding in report["findings"]}
    if len(keys) != len(report["findings"]):
        raise ValueError("logical Finding identity collided")
    return keys


def run(scanner_jar: Path) -> None:
    if not scanner_jar.is_file():
        raise ValueError("pinned Scanner JAR is missing")
    with tempfile.TemporaryDirectory(prefix="archguard-ci-journey-") as directory:
        output = Path(directory)
        baseline = scan(scanner_jar, "baseline", output / "baseline.json", 0)
        introduced = scan(scanner_jar, "introduced", output / "introduced.json", 2)
        repaired = scan(scanner_jar, "baseline", output / "repaired.json", 0)
        if (output / "baseline.json").read_bytes() != (output / "repaired.json").read_bytes():
            raise ValueError("repaired source did not reproduce the baseline report")
    before, candidate, after = map(finding_keys, (baseline, introduced, repaired))
    if len(before) != 0 or len(candidate - before) != 1 or len(candidate & before) != 0:
        raise ValueError("introduced source did not produce exactly one NEW Finding")
    if len(after - candidate) != 0 or len(candidate - after) != 1:
        raise ValueError("repair did not RESOLVE the Finding")
    finding = introduced["findings"][0]
    if finding["rule"]["id"] != "archguard.illegal-package-dependency" or finding["severity"] != "high":
        raise ValueError("introduced Finding is not the fixed blocking violation")
    print("Source journey: baseline PASS/0, introduced NEW=1 FAIL/2, repaired RESOLVED=1 PASS/0.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scanner-jar", required=True, type=Path)
    run(parser.parse_args().scanner_jar)
