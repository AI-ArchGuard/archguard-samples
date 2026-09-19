#!/usr/bin/env python3
"""Verify the committed S7 sample manifest and golden report integrity."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath


def fail(message: str) -> None:
    raise SystemExit(f"sample verification failed: {message}")


def confined(root: Path, value: str) -> Path:
    relative = PurePosixPath(value)
    if relative.is_absolute() or ".." in relative.parts:
        fail(f"manifest path is not repository relative: {value}")
    resolved = (root / Path(*relative.parts)).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        fail(f"manifest path leaves the repository: {value}")
    return resolved


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_report(root: Path, entry: dict[str, object], contract_version: str) -> None:
    golden_value = entry.get("golden")
    if not isinstance(golden_value, str):
        return
    golden = confined(root, golden_value)
    if not golden.is_file() or golden.is_symlink():
        fail(f"missing regular golden report: {golden_value}")
    digest_file = golden.with_suffix(".sha256")
    if not digest_file.is_file():
        fail(f"missing digest for {golden_value}")
    expected_digest = digest_file.read_text(encoding="utf-8").split()[0]
    if digest(golden) != expected_digest:
        fail(f"digest mismatch for {golden_value}")
    report = json.loads(golden.read_text(encoding="utf-8"))
    if report.get("schemaVersion") != contract_version:
        fail(f"unexpected schema version in {golden_value}")
    findings = report.get("findings")
    if not isinstance(findings, list) or len(findings) != entry.get("expectedFindings"):
        fail(f"unexpected finding count in {golden_value}")
    encoded = golden.read_text(encoding="utf-8")
    if "\\\\" in encoded or ":\\" in encoded:
        fail(f"host path separator found in {golden_value}")
    for collection in ("artifacts", "components", "dependencies", "findings", "metrics", "evidences"):
        values = report.get(collection)
        if not isinstance(values, list):
            fail(f"missing array {collection} in {golden_value}")
        identifiers = [value.get("id") for value in values]
        if identifiers != sorted(identifiers):
            fail(f"array {collection} is not stably sorted in {golden_value}")


def verify_entry(root: Path, entry: dict[str, object], contract_version: str) -> None:
    identifier = entry.get("id")
    if not isinstance(identifier, str) or not identifier:
        fail("case id must be non-empty")
    for key in ("project", "rules"):
        value = entry.get(key)
        if not isinstance(value, str):
            fail(f"{identifier} has no {key} path")
        path = confined(root, value)
        if not path.exists() or path.is_symlink():
            fail(f"{identifier} {key} path is missing or symbolic")
    repeat = entry.get("repeat")
    if not isinstance(repeat, int) or repeat < 1 or repeat > 3:
        fail(f"{identifier} repeat must be between 1 and 3")
    max_seconds = entry.get("maxSeconds")
    if not isinstance(max_seconds, int) or max_seconds < 1 or max_seconds > 60:
        fail(f"{identifier} maxSeconds must be between 1 and 60")
    verify_report(root, entry, contract_version)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    manifest_path = root / "samples.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("formatVersion") != "1.0.0":
        fail("unsupported manifest version")
    if manifest.get("scannerVersion") != "0.2.0":
        fail("manifest must target Scanner 0.2.0")
    contract_version = manifest.get("contractVersion")
    if contract_version != "0.1.0":
        fail("manifest must target Result Schema 0.1.0")
    cases = manifest.get("cases")
    failures = manifest.get("failures")
    if not isinstance(cases, list) or len(cases) < 3:
        fail("at least three valid sample cases are required")
    if not isinstance(failures, list) or len(failures) < 3:
        fail("at least three failure cases are required")
    identifiers: set[str] = set()
    for entry in [*cases, *failures]:
        if not isinstance(entry, dict):
            fail("manifest entries must be objects")
        if entry.get("id") in identifiers:
            fail(f"duplicate case id: {entry.get('id')}")
        identifiers.add(str(entry.get("id")))
        verify_entry(root, entry, contract_version)
    for path in root.rglob("*"):
        if path.is_symlink():
            fail(f"symbolic links are not allowed: {path.relative_to(root).as_posix()}")
    print(f"Verified {len(cases)} golden cases and {len(failures)} failure cases.")


if __name__ == "__main__":
    main()
