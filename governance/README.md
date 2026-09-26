# Stage 3B governance contract vectors

`fingerprint-v1-vectors.json` fixes the Platform consumer fingerprint for every Finding in the three published Scanner Result Schema `0.1.0` golden reports. The Scanner reports and their SHA-256 files remain unchanged.

Run `python3 scripts/verify_governance_contract.py` from the repository root. The verifier covers dependency, component, artifact, and cycle Findings; it rejects collisions and unsupported rule shapes. It also checks that reordering, line movement, display text, severity, and complexity metric values do not change the Platform identity, while rule version, project identity, violation type, and logical source changes do.

The normative algorithm and API shape belong to the Platform 3B technical design. These vectors are fixed consumer evidence, not a new Scanner Schema or a governance runtime implementation.

`ci-journey-v1.json` pins one high-severity illegal dependency from the published architecture-violations report. `python3 scripts/verify_governance_journey.py` checks a deterministic baseline (the published report without that Finding), the introduced violation, and its repaired state. The expected transition is `NEW=1`, `EXISTING=12`, `FAIL`/exit `2`, followed by `RESOLVED=1`, `EXISTING=12`, `PASS`/exit `0`. Ordering and line changes must not alter classification. Run with `--output-dir <temporary-directory>` to materialize the three Scanner Schema `0.1.0` reports for integration tests; no generated report is committed.

These are derived report-level fixtures, not separate Git source revisions or a claim that Scanner `0.2.1` generated them. End-to-end CI must still run the pinned Scanner against real synthetic source revisions.
