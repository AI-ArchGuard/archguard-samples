"""Verify synthetic Agent 4B vectors against the immutable Scanner golden report."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
request = json.loads((ROOT / "agent/request-vectors.json").read_text(encoding="utf-8"))
vectors = json.loads((ROOT / "agent/model-output-vectors.json").read_text(encoding="utf-8"))
report_path = ROOT / request["sourceReport"]
assert hashlib.sha256(report_path.read_bytes()).hexdigest() == request["reportSha256"]
report = json.loads(report_path.read_text(encoding="utf-8"))
assert report["schemaVersion"] == "0.1.0"
assert request["schemaVersion"] == vectors["schemaVersion"] == "0.1.0"
findings = {finding["id"]: finding for finding in report["findings"]}
evidences = {evidence["id"] for evidence in report["evidences"]}
refs = {finding["findingRef"] for finding in request["findings"]}
citations = {citation["citationId"]: citation for citation in request["citations"]}
assert len(refs) == len(request["findings"])
assert len(citations) == len(request["citations"])
for finding in request["findings"]:
    actual = findings[finding["findingId"]]
    for citation_id in finding["citationIds"]:
        citation = citations[citation_id]
        assert citation["source"] == "SCANNER_EVIDENCE"
        assert citation["evidenceId"] in evidences
        assert citation["evidenceId"] in actual["evidenceIds"]
for citation in citations.values():
    assert citation["projectId"] == request["projectId"]
    if citation["source"] == "SCANNER_EVIDENCE":
        assert citation["scanJobId"] == request["scanJobId"]
    else:
        assert citation["source"] == "PROJECT_DOCUMENT"
        assert citation["documentVersionId"] and citation["fragmentIndex"] >= 0
        assert citation["text"]
        assert hashlib.sha256(citation["text"].encode("utf-8")).hexdigest() == citation["contentSha256"]
cases = {case["name"]: case for case in vectors["cases"]}
assert len(cases) == len(vectors["cases"])
assert cases["supported-explanation"]["expected"] == "SUCCEEDED"
assert set(cases["supported-explanation"]["findingRefs"]) <= refs
assert set(cases["supported-explanation"]["citationIds"]) <= citations.keys()
supported = cases["supported-explanation"]["output"]
assert supported["purpose"] == "FINDING_EXPLANATION"
assert supported["conclusion"]["kind"] == "SUPPORTED"
assert supported["conclusion"]["citationIds"]
for claim in supported["claims"] + supported["ruleBasis"]:
    assert claim["findingRef"] in cases["supported-explanation"]["findingRefs"]
    assert claim["citationIds"] and set(claim["citationIds"]) <= citations.keys()
for suggestion in supported["suggestions"]:
    assert suggestion["requiresHumanReview"] is True
    assert set(suggestion["findingRefs"]) <= refs
    assert suggestion["citationIds"] and set(suggestion["citationIds"]) <= citations.keys()
assert cases["insufficient-summary"]["purpose"] == "PR_SUMMARY"
assert set(cases["insufficient-summary"]["findingRefs"]) == refs
assert cases["insufficient-summary"]["citationIds"] == []
insufficient = cases["insufficient-summary"]["output"]
assert insufficient["conclusion"] == {"kind": "INSUFFICIENT", "text": None, "citationIds": []}
assert insufficient["claims"] == insufficient["ruleBasis"] == insufficient["suggestions"] == []
for name in ("fabricated-citation", "cross-project-citation", "stale-document-version"):
    assert cases[name]["expected"] == "CITATION_INVALID"
    assert not set(cases[name]["citationIds"]) <= citations.keys()
assert cases["unknown-finding"]["findingRefs"] == ["not-selected"]
assert cases["unknown-field"]["payloadExtra"] == "unexpected"
assert cases["refusal"]["providerStatus"] == "refusal"
assert cases["incomplete"]["providerStatus"] == "incomplete"
assert request[cases["document-prompt-injection"]["document"]].startswith("Ignore prior instructions")
assert cases["same-key-same-digest"]["expected"] == "SAME_REQUEST"
assert cases["same-key-different-digest"]["expected"] == "CONFLICT"
print("Agent 4B synthetic vectors verified")
