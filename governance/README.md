# Stage 3B governance contract vectors

`fingerprint-v1-vectors.json` fixes the Platform consumer fingerprint for every Finding in the three published Scanner Result Schema `0.1.0` golden reports. The Scanner reports and their SHA-256 files remain unchanged.

Run `python3 scripts/verify_governance_contract.py` from the repository root. The verifier covers dependency, component, artifact, and cycle Findings; it rejects collisions and unsupported rule shapes. It also checks that reordering, line movement, display text, severity, and complexity metric values do not change the Platform identity, while rule version, project identity, violation type, and logical source changes do.

The normative algorithm and API shape belong to the Platform 3B technical design. These vectors are fixed consumer evidence, not a new Scanner Schema or a governance runtime implementation.
