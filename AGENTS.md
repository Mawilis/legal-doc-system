# WILSY OS - SOVEREIGN CODEX GOVERNANCE CONTRACT

VERSION: v1.0.0-CRITICAL-STAGE
AUTHORITY: Wilsy OS Core Governance
SCOPE: Entire repository tree rooted at this file
STATUS: MANDATORY / FAIL-CLOSED
CANONICAL REPOSITORY: /Users/wilsonkhanyezi/legal-doc-system

===============================================================================
1. ABSOLUTE GOVERNANCE RULE
===============================================================================

Every file created, modified, rewritten, certified, migrated, or otherwise
touched by Codex inside this repository is an institutional artifact.

This contract applies automatically.

The user MUST NOT be required to repeat these rules in individual prompts.

Task-specific instructions may add stricter requirements but MUST NOT silently
weaken this contract.

If a requested change conflicts with this contract, Codex MUST identify the
conflict and fail closed.

===============================================================================
2. FORENSIC PREFLIGHT BEFORE ANY FILE CHANGE
===============================================================================

Before authoring or modifying a file, Codex MUST perform bounded relationship
discovery and establish the primary file, dependencies, callers, consumers,
persisted schemas, tests, transaction/session boundaries, tenant-isolation
implications, financial-authority implications, evidence surfaces, and blast
radius.

Codex MUST establish a connection matrix before editing.

===============================================================================
3. ONE PRIMARY FILE PER CERTIFIED DELIVERY
===============================================================================

Unless the user explicitly authorizes otherwise:

- modify exactly ONE primary file per certified delivery;
- related files are READ-ONLY;
- do not opportunistically modify unrelated files;
- do not modify server/manifest.txt;
- do not weaken tests merely to make production behavior pass;
- do not modify production merely to satisfy a defective test.

===============================================================================
4. FULL-FILE AUTHORING CONTRACT
===============================================================================

For a certified Wilsy OS source-file update:

- perform a full-file overwrite;
- preserve verified runtime semantics unless explicitly changing them;
- do not leave partial structural migrations;
- do not leave structural debt;
- do not use fragments unless explicitly authorized;
- do not leave TODO, FIXME, placeholders, or stubs.

Existing structural noncompliance is NOT grandfathered.

===============================================================================
5. MANDATORY SOVEREIGN SOURCE-FILE HEADER
===============================================================================

Every Wilsy OS production source file created or structurally certified MUST
contain a sovereign module header containing, where relevant:

TITLE
VERSION
AUTHORITY
EPITOME
ABSOLUTE CANONICAL PATH
COLLABORATION / OWNERSHIP
CERTIFICATION OR UPDATE DATE
CHANGELOG
COMPLIANCE
SECURITY / PRIVACY POSTURE
TENANT BOUNDARY
AUTHORITY BOUNDARY
FINANCIAL AUTHORITY BOUNDARY

A one-line module description is NOT sufficient.

===============================================================================
6. MANDATORY SOVEREIGN END SEAL
===============================================================================

Every Wilsy OS production source file created or structurally certified MUST
end with an explicit non-runtime sovereign artifact seal containing:

ARTIFACT
VERSION
AUTHORITY BOUNDARY
TENANT POSTURE, where relevant
FAIL-CLOSED POSTURE
FINANCIAL EXECUTION AUTHORITY, where relevant
END OF WILSY OS SOVEREIGN ARTIFACT

ABSENCE OF THE END SEAL IS A CERTIFICATION FAILURE.

===============================================================================
7. VERSIONING AND CHANGELOG
===============================================================================

Every certified behavioral or structural change MUST receive an appropriate
semantic version increment.

The sovereign header version, current changelog version, and sovereign end-seal
version MUST agree exactly.

A version mismatch is a certification failure.

===============================================================================
8. PUBLIC API DOCUMENTATION
===============================================================================

Every exported or public class, exception, enum, dataclass, result object,
function, registry method, and service method must have accurate institutional
documentation covering relevant authority, tenant scope, mutation semantics,
idempotency semantics, transaction ownership, fail-closed behavior, and
financial boundary.

===============================================================================
9. FAIL-CLOSED ENGINEERING
===============================================================================

No TODO, FIXME, placeholder, stub, arbitrary exception swallowing, silent
integrity downgrade, invented persisted truth, invented execution truth, or
invented settlement truth.

Structured errors are mandatory at institutional boundaries.

===============================================================================
10. TENANT ISOLATION
===============================================================================

Every persistence lookup, mutation, replay reconciliation, receipt lookup,
authorization lookup, projection, and conflict classification MUST preserve
tenant scope.

Cross-tenant absence MUST NOT disclose another tenant's existence.

Tenant isolation aligns with POPIA section 19, GDPR Article 32, and SOC 2 CC7.2.

===============================================================================
11. FINANCIAL AUTHORITY CONSTITUTION
===============================================================================

APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED

Approval is not release authorization.
Release authorization is not execution.
Execution is not settlement.
Settlement is not inferred from authorization or execution attempts.

Kennel EOS is the exclusive financial execution authority.

No non-Kennel component may invent bank execution truth, provider execution
truth, payment destination truth, settlement truth, paid truth, or settled
truth.

===============================================================================
12. ACCOUNTS PAYABLE SEMANTIC CONTRACT
===============================================================================

Canonical AP chain:

Vendor
-> VendorBill
-> Approval
-> Release Authorization
-> Kennel EOS Execution Truth
-> Settlement Allocation

Canonical payable entity: VendorBill
Canonical payable identifier: payable_id

Release authorization is immutable authority or reservation evidence and does
not move money, prove a payment destination, mark paid/settled state, or
decrement settlement/outstanding truth.

===============================================================================
13. CRYPTOGRAPHIC EVIDENCE
===============================================================================

For financial, forensic, command, authorization, and certification evidence:

- SHA3-512 is preferred;
- canonical serialization MUST be deterministic;
- fingerprints MUST cover the defined semantic payload;
- intentionally excluded metadata MUST be documented;
- cryptographic claims MUST NOT exceed implementation truth.

===============================================================================
14. DATABASE AND TRANSACTION CONTRACT
===============================================================================

Financial persistence SHOULD use majority write concern, journaling, majority
read concern, deterministic unique indexes, and caller-owned transaction/session
boundaries where applicable.

Session parameters MUST propagate through all participating reads and writes.

Where MongoDB transient transaction retry is required for correctness, the
WHOLE transaction MUST restart from fresh state.

===============================================================================
15. IDEMPOTENCY
===============================================================================

Where a surface promises durable idempotency:

same idempotency key
+ same canonical command fingerprint
= exact replay

Same idempotency key + different canonical command fingerprint MUST fail closed.

Durable command evidence outranks inference from coincidentally equal state.

===============================================================================
16. TEST GOVERNANCE
===============================================================================

Do not weaken a test merely because a real system produced an unexpected
result.

First classify a failure as production defect, test defect, environment defect,
or contract ambiguity.

Concurrency tests SHOULD use deterministic synchronization primitives rather
than arbitrary sleeps.

Local infrastructure unavailability MUST NOT be represented as passing
certification.

===============================================================================
17. REQUIRED VERIFICATION
===============================================================================

After every file modification, Codex MUST run all relevant available checks.

For Python surfaces, this normally includes:

1. python3 -m py_compile;
2. Pyright;
3. directly relevant unit tests;
4. directly relevant integration tests when infrastructure is available;
5. git diff --check;
6. git status --short.

Codex MUST state exactly which checks did not run and why.

===============================================================================
18. STRUCTURAL SELF-AUDIT BEFORE COMPLETION
===============================================================================

BEFORE claiming completion, Codex MUST re-open the FINAL primary file and
inspect the actual resulting artifact.

Codex MUST NOT rely on memory of what it intended to write.

Verify all relevant sovereign header fields, current public API documentation,
absence of TODO/FIXME/placeholders/stubs, presence of the sovereign end seal,
exact version agreement between header/changelog/seal, and absence of unrelated
file modifications.

IF ANY REQUIRED ITEM FAILS:

DO NOT CLAIM COMPLETION.

Correct the primary file and rerun verification.

===============================================================================
19. CERTIFICATION SCORING
===============================================================================

A Wilsy OS artifact may receive 10/10 ONLY when every relevant requirement is
satisfied.

Any known gap limits the artifact to at most 9/10.

Static checks alone do not constitute operational certification.
Unit tests alone do not constitute real-database certification.
A failed or partially executed CI job MUST NOT be represented as sealed
operational evidence.

===============================================================================
20. REQUIRED COMPLETION REPORT
===============================================================================

Every certified modification report MUST include the primary artifact,
previous version -> new version, relationship and blast-radius findings,
behavioral change, structural/governance change, authority boundaries,
security and tenant implications, verification evidence, checks not run,
exact changed files, certification scores, remaining failure conditions, and
this table:

| | Action | File / surface | Why (blast radius) | Priority | Done? |
|---|---|---|---|---|---|

===============================================================================
21. ABSOLUTE COMPLETION CONDITION
===============================================================================

Working code is NOT sufficient.
Passing tests are NOT sufficient.

A Wilsy OS artifact is complete only when BOTH are true:

1. runtime contract passes;
2. sovereign artifact contract passes.

Codex MUST dynamically apply this contract without requiring the user to
repeat it.

===============================================================================
WILSY OS SOVEREIGN GOVERNANCE SEAL
===============================================================================

CONTRACT: WILSY OS - SOVEREIGN CODEX GOVERNANCE CONTRACT
VERSION: v1.0.0-CRITICAL-STAGE
SCOPE: Entire repository tree
POSTURE: FAIL-CLOSED
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
STRUCTURAL MANDATE: HEADER + VERSION + CHANGELOG + END SEAL REQUIRED
END OF WILSY OS SOVEREIGN GOVERNANCE CONTRACT
