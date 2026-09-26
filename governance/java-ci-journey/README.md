# Fixed Java CI source journey

This is synthetic source, with no external code or runtime dependency. `baseline` and `introduced` are separate fixed source revisions under the same project identity and rule set. `introduced` adds a forbidden dependency from `com.archguard.samples.governance.app.App` to `com.archguard.samples.governance.internal.InternalRepository`. The repaired revision is exactly `baseline` again.

Scanner `0.2.1`, Result Schema `0.1.0`, and Platform Finding fingerprint `platform-finding-v1` are fixed. A baseline scan has no Finding and exits `0`; the introduced scan has one `high` `archguard.illegal-package-dependency` Finding and exits `2`; rescanning the repaired source exits `0` and resolves that Finding. The Platform gate must therefore move `PASS/0` → `FAIL/2` → `PASS/0` when that successful baseline is selected. Scanner's exit `2` on the middle scan only says its report is valid and violates `failOn`; the CI adapter must still submit the report and use Platform's final gate response.

From the repository root, run `python3 scripts/verify_governance_source_journey.py --scanner-jar /path/to/archguard-scanner.jar`. The verifier executes the pinned Scanner three times, checks fixed report digests and the stable Finding identity, and keeps reports in a temporary directory. It requires only Java, Python, and the already-published Scanner JAR. CI builds the Scanner from a pinned commit; no Scanner source, Schema, or Platform code is changed here.

CI adds the pinned `actions/setup-java` action (MIT) to select JDK 21 reproducibly; relying on the runner's preinstalled JDK would be a less stable alternative. The pinned Scanner is Apache-2.0 and is built only for verification, not published as a new dependency of the sample source.
