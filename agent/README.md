# Agent 4B synthetic contract vectors

These are synthetic, fixed examples only. They do not invoke a model or alter Scanner golden reports.

`request-vectors.json` binds the first two Findings from `java/java-architecture-violations/expected/report.json` to their actual Evidence IDs and one invented Markdown DocumentVersion. `model-output-vectors.json` covers one supported explanation, one insufficient PR summary, plus unknown/fabricated/cross-Project/stale citation, unknown field, refusal, incomplete response, prompt injection, and idempotency scenarios. `scripts/verify_agent_contract.py` checks the source report digest and all vector expectations. Platform must additionally validate the strict model JSON Schema, semantic reference graph and current Project authorization before publishing a citation.

No customer code, credential, live model call, or production URL is included.

## 4G hardening inventory

`hardening-cases-v1.json` retains 14 fixed synthetic attacks/faults with expected outcomes, frozen caps and exact Platform/Web runtime-test pointers for future Stage 6 evaluation work. Run `python3 scripts/verify_agent_hardening.py` to check inventory completeness and frozen metadata. This command does **not** execute runtime security tests or approve a real provider. Runtime acceptance belongs to the referenced Platform integration tests and Web tests. No formal Evals runtime, Gateway or external model is started.

Compatibility: Agent/Scanner Schema `0.1.0`, Scanner `v0.2.1`; Samples definitions → Platform hardening → Web consumer → Deploy 4H. Rollback disables the Web entry/model first, then reverts apps while preserving migrations, immutable documents, request history and cost reservations.
