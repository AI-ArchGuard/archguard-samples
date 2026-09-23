#!/usr/bin/env python3
"""Verify Platform Finding fingerprint v1 against published Scanner 0.1.0 reports."""

from __future__ import annotations

import copy
import hashlib
import json
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VECTORS = ROOT / "governance/fingerprint-v1-vectors.json"
REPORTS = (
    ROOT / "java/java-architecture-violations/expected/report.json",
    ROOT / "java/java-dependency-cycle/expected/report.json",
    ROOT / "java/java-clean-layered/expected/report.json",
)
EDGE_RULES = {
    "archguard.forbidden-component",
    "archguard.illegal-package-dependency",
    "archguard.internal-module-access",
    "archguard.layered-architecture",
    "spring.controller-repository-access",
}


def normalized(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("expected a non-empty identity string")
    return unicodedata.normalize("NFC", value)


def one_extension(finding: dict, key: str) -> str:
    values = finding["extensions"].get(key)
    if not isinstance(values, list) or len(values) != 1:
        raise ValueError(f"{finding['rule']['id']} requires one {key} value")
    return normalized(values[0])


def index(report: dict) -> dict[str, dict]:
    entities = [report["project"]]
    for collection in ("artifacts", "components", "dependencies", "evidences"):
        entities.extend(report[collection])
    result = {entity["id"]: entity for entity in entities}
    if len(result) != len(entities):
        raise ValueError("duplicate report identity")
    return result


def artifact_identity(artifact: dict) -> dict:
    return {
        "kind": normalized(artifact["kind"]),
        "language": normalized(artifact["language"]),
        "path": normalized(artifact["repositoryPath"]),
        "qualifiedName": normalized(artifact["qualifiedName"]),
    }


def component_identity(component: dict, entities: dict[str, dict]) -> dict:
    return {
        "artifact": artifact_identity(entities[component["artifactId"]]),
        "kind": normalized(component["kind"]),
        "language": normalized(component["language"]),
        "qualifiedName": normalized(component["qualifiedName"]),
    }


def dependency_identity(dependency: dict, entities: dict[str, dict]) -> dict:
    return {
        "kind": normalized(dependency["kind"]),
        "source": component_identity(entities[dependency["sourceId"]], entities),
        "target": component_identity(entities[dependency["targetId"]], entities),
    }


def cycle_identity(report: dict, finding: dict, entities: dict[str, dict]) -> dict:
    finding_evidence = set(finding["evidenceIds"])
    dependencies = [
        dependency
        for dependency in report["dependencies"]
        if set(dependency["evidenceIds"]).issubset(finding_evidence)
    ]
    if not dependencies or set().union(*(set(d["evidenceIds"]) for d in dependencies)) != finding_evidence:
        raise ValueError("cycle evidence does not identify a closed dependency set")
    vertices = {vertex for edge in dependencies for vertex in (edge["sourceId"], edge["targetId"])}
    if finding["subjectId"] not in {edge["id"] for edge in dependencies}:
        raise ValueError("cycle subject is outside its dependency set")
    canonical_vertices = [component_identity(entities[vertex], entities) for vertex in vertices]
    return {
        "graphScope": one_extension(finding, "archguard.graph-scope"),
        "vertices": sorted(canonical_vertices, key=canonical_json),
    }


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def payload(report: dict, finding: dict, entities: dict[str, dict]) -> dict:
    rule = finding["rule"]
    rule_id = normalized(rule["id"])
    subject = entities[finding["subjectId"]]
    if rule_id in EDGE_RULES:
        if not finding["subjectId"].startswith("dependency_"):
            raise ValueError("edge rule must reference a dependency")
        identity = {"edge": dependency_identity(subject, entities)}
        discriminator = {"violation": one_extension(finding, "archguard.violation")}
    elif rule_id == "archguard.dependency-cycle":
        identity = {"cycle": cycle_identity(report, finding, entities)}
        discriminator = {}
    elif rule_id == "archguard.complexity-threshold":
        if finding["subjectId"].startswith("component_"):
            identity = {"component": component_identity(subject, entities)}
        elif finding["subjectId"].startswith("artifact_"):
            identity = {"artifact": artifact_identity(subject)}
        else:
            raise ValueError("complexity rule must reference a component or artifact")
        discriminator = {"metric": one_extension(finding, "archguard.metric")}
    elif rule_id == "archguard.required-annotation":
        if not finding["subjectId"].startswith("component_"):
            raise ValueError("annotation rule must reference a component")
        identity = {"component": component_identity(subject, entities)}
        discriminator = {"requiredAnnotation": one_extension(finding, "archguard.required-annotation")}
    else:
        raise ValueError(f"unsupported Finding rule: {rule_id}")
    return {
        "projectIdentity": normalized(report["project"]["identity"]),
        "ruleId": rule_id,
        "ruleVersion": normalized(rule["version"]),
        "subject": identity,
        "discriminator": discriminator,
    }


def fingerprint(report: dict, finding: dict) -> str:
    canonical = canonical_json(payload(report, finding, index(report)))
    return hashlib.sha256(("archguard-finding-v1\n" + canonical).encode("utf-8")).hexdigest()


def check_report(report: dict, expected: dict[str, str]) -> None:
    expected_count = len(expected)
    if report["schemaVersion"] != "0.1.0" or len(report["findings"]) != expected_count:
        raise ValueError("unexpected fixed Scanner report")
    original = {finding["id"]: fingerprint(report, finding) for finding in report["findings"]}
    if len(original) != expected_count or len(set(original.values())) != expected_count:
        raise ValueError("Finding identities collide in a fixed report")
    if original != expected:
        raise ValueError("Finding fingerprint v1 differs from committed vectors")

    reordered = copy.deepcopy(report)
    for collection in ("artifacts", "components", "dependencies", "evidences", "findings"):
        reordered[collection].reverse()
    for finding in reordered["findings"]:
        finding["evidenceIds"].reverse()
        finding["severity"] = "low"
        finding["message"] = "Presentation changed"
        if finding["location"]:
            finding["location"]["startLine"] += 3
            finding["location"]["endLine"] += 3
    for collection in ("components", "evidences"):
        for entity in reordered[collection]:
            if entity["location"]:
                entity["location"]["startLine"] += 3
                entity["location"]["endLine"] += 3
    for metric in reordered["metrics"]:
        metric["value"] += 1
    for finding in reordered["findings"]:
        if fingerprint(reordered, finding) != original[finding["id"]]:
            raise ValueError("fingerprint changed after order, line, metric or presentation perturbation")

    if report["findings"]:
        changed = copy.deepcopy(report)
        finding = changed["findings"][0]
        before = fingerprint(changed, finding)
        finding["rule"]["version"] = "0.1.1"
        if fingerprint(changed, finding) == before:
            raise ValueError("rule version did not affect identity")
        finding["rule"]["version"] = report["findings"][0]["rule"]["version"]
        changed["project"]["identity"] += ":other"
        if fingerprint(changed, finding) == before:
            raise ValueError("project identity did not affect identity")

    edge = next((f for f in report["findings"] if f["rule"]["id"] in EDGE_RULES), None)
    if edge:
        changed = copy.deepcopy(report)
        finding = next(f for f in changed["findings"] if f["id"] == edge["id"])
        before = fingerprint(changed, finding)
        finding["extensions"]["archguard.violation"][0] += "-changed"
        if fingerprint(changed, finding) == before:
            raise ValueError("violation type did not affect identity")
        finding["extensions"]["archguard.violation"] = edge["extensions"]["archguard.violation"]
        dependency = next(d for d in changed["dependencies"] if d["id"] == finding["subjectId"])
        source = next(c for c in changed["components"] if c["id"] == dependency["sourceId"])
        source["qualifiedName"] += "Changed"
        if fingerprint(changed, finding) == before:
            raise ValueError("logical source entity did not affect identity")

    cycle = next((f for f in report["findings"] if f["rule"]["id"] == "archguard.dependency-cycle"), None)
    if cycle:
        changed = copy.deepcopy(report)
        finding = next(f for f in changed["findings"] if f["id"] == cycle["id"])
        before = fingerprint(changed, finding)
        dependency = next(d for d in changed["dependencies"] if d["id"] == finding["subjectId"])
        vertex = next(c for c in changed["components"] if c["id"] == dependency["sourceId"])
        vertex["qualifiedName"] += "Changed"
        if fingerprint(changed, finding) == before:
            raise ValueError("cycle vertex did not affect identity")


def main() -> None:
    vectors = json.loads(VECTORS.read_text(encoding="utf-8"))
    if vectors["formatVersion"] != "1.0.0" or vectors["algorithmVersion"] != "platform-finding-v1":
        raise ValueError("unsupported governance vector format")
    if vectors["scannerSchemaVersion"] != "0.1.0":
        raise ValueError("unsupported Scanner schema")
    if set(vectors["reports"]) != {path.relative_to(ROOT).as_posix() for path in REPORTS}:
        raise ValueError("governance vectors do not cover every fixed report")
    for path in REPORTS:
        report = json.loads(path.read_text(encoding="utf-8"))
        check_report(report, vectors["reports"][path.relative_to(ROOT).as_posix()])
    print("Governance fingerprint v1: 15 findings across 3 fixed Scanner 0.1.0 reports verified.")


if __name__ == "__main__":
    main()
