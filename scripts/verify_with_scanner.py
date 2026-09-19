#!/usr/bin/env python3
"""Run the published sample contract against an ArchGuard Scanner JAR."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
import time
from pathlib import Path, PurePosixPath


def fail(message: str) -> None:
    raise SystemExit(f"scanner sample verification failed: {message}")


def confined(root: Path, value: str) -> Path:
    relative = PurePosixPath(value)
    if relative.is_absolute() or ".." in relative.parts:
        fail(f"unsafe manifest path: {value}")
    result = (root / Path(*relative.parts)).resolve()
    try:
        result.relative_to(root)
    except ValueError:
        fail(f"manifest path leaves sample root: {value}")
    return result


def run_case(jar: Path, root: Path, entry: dict[str, object]) -> dict[str, object]:
    identifier = str(entry["id"])
    project = confined(root, str(entry["project"]))
    rules = confined(root, str(entry["rules"]))
    golden_value = entry.get("golden")
    golden = confined(root, str(golden_value)).read_bytes() if isinstance(golden_value, str) else None
    repeat = int(entry["repeat"])
    max_seconds = int(entry["maxSeconds"])
    expected_exit = int(entry["expectedExit"])
    expected_report = bool(entry.get("reportExpected", golden is not None))
    outputs: list[bytes] = []
    durations: list[float] = []
    with tempfile.TemporaryDirectory(prefix=f"archguard-{identifier}-") as directory:
        temporary = Path(directory)
        for run in range(repeat):
            output = temporary / f"report-{run}.json"
            command = [
                "java", "-jar", str(jar), "scan", str(project),
                "--rules", str(rules), "--output", str(output),
            ]
            started = time.monotonic()
            try:
                completed = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=max_seconds,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                fail(f"{identifier} exceeded {max_seconds} seconds")
            duration = time.monotonic() - started
            durations.append(duration)
            if completed.returncode != expected_exit:
                fail(f"{identifier} returned {completed.returncode}, expected {expected_exit}")
            stderr_code = entry.get("expectedStderrCode")
            if isinstance(stderr_code, str) and stderr_code not in completed.stderr:
                fail(f"{identifier} did not emit {stderr_code}")
            for stream in (completed.stdout, completed.stderr):
                if str(root) in stream or str(root.parent) in stream:
                    fail(f"{identifier} leaked an absolute sample path")
            if output.exists() != expected_report:
                fail(f"{identifier} report presence did not match the manifest")
            if output.exists():
                report_bytes = output.read_bytes()
                outputs.append(report_bytes)
                report = json.loads(report_bytes)
                findings = report.get("findings", [])
                expected_findings = entry.get("expectedFindings")
                if isinstance(expected_findings, int) and len(findings) != expected_findings:
                    fail(f"{identifier} finding count changed")
                if golden is not None and report_bytes != golden:
                    fail(f"{identifier} report differs from the committed golden bytes")
        if outputs and any(value != outputs[0] for value in outputs[1:]):
            fail(f"{identifier} reports are not byte deterministic")
    return {
        "id": identifier,
        "runs": repeat,
        "maxSeconds": max_seconds,
        "maximumObservedSeconds": round(max(durations), 6),
        "reportSha256": hashlib.sha256(outputs[0]).hexdigest() if outputs else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jar", required=True)
    parser.add_argument("--samples", required=True)
    parser.add_argument("--results")
    args = parser.parse_args()
    jar = Path(args.jar).resolve()
    root = Path(args.samples).resolve()
    if not jar.is_file() or jar.is_symlink():
        fail("scanner JAR must be a regular file")
    manifest = json.loads((root / "samples.json").read_text(encoding="utf-8"))
    version = subprocess.run(
        ["java", "-jar", str(jar), "--version"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=15,
        check=False,
    )
    if version.returncode != 0 or version.stdout.strip() != manifest["scannerVersion"]:
        fail("scanner version does not match the sample manifest")
    results = [run_case(jar, root, entry) for entry in [*manifest["cases"], *manifest["failures"]]]
    document = {
        "formatVersion": "1.0.0",
        "scannerVersion": manifest["scannerVersion"],
        "contractVersion": manifest["contractVersion"],
        "cases": results,
    }
    encoded = json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.results:
        output = Path(args.results)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8", newline="\n")
    print(f"Verified Scanner {manifest['scannerVersion']} against {len(results)} sample cases.")


if __name__ == "__main__":
    main()
