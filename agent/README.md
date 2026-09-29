# Agent 4B synthetic contract vectors

These are synthetic, fixed examples only. They do not invoke a model or alter Scanner golden reports.

`request-vectors.json` binds the first two Findings from `java/java-architecture-violations/expected/report.json` to their actual Evidence IDs and one invented Markdown DocumentVersion. `model-output-vectors.json` covers one supported explanation, one insufficient PR summary, plus unknown/fabricated/cross-Project/stale citation, unknown field, refusal, incomplete response, prompt injection, and idempotency scenarios. `scripts/verify_agent_contract.py` checks the source report digest and all vector expectations. Platform must additionally validate the strict model JSON Schema, semantic reference graph and current Project authorization before publishing a citation.

No customer code, credential, live model call, or production URL is included.
