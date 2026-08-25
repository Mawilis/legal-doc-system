===============================================================================
WILSY ENGINEERING KERNEL: PATCH ENGINE (The Surgeon)
===============================================================================
Epitome:
    The surgical instrument of Wilsy OS. A high-precision engine designed for 
    atomic, non-destructive codebase modification, hot-patching, and 
    automated system remediation.

Biblical Scale & Architecture:
    This is a billion-dollar, production-ready surgical suite. No child's place.
    It governs the application of patches, ensuring every delta is verified, 
    documented, and cryptographically signed before it touches the production 
    environment.

INTEGRATION: This engine operates as the primary effector for the Forensic 
Engine. When an anomaly is detected, the Patch Engine is triggered to 
generate, validate, and apply the surgical fix.

Collaboration & Maintenance:
    - [Atomic Application]: No partial updates; integrity is binary.
    - [Validation]: Patches are unit-tested against the Sentinel baseline.
    - [Versioning]: Every patch creates a snapshot in the Knowledge Graph.
===============================================================================

## 1. Architectural Pillars
The Patch Engine functions through four critical operational phases:

### I. Analysis & Generation
*   **Diff-Engine:** Calculates the minimal delta between the current state and the desired state.
*   **Generator:** AI-driven synthesis of the surgical patch based on the Forensic Engine's report.

### II. Validation Layer
*   **Sandbox Simulation:** Patches are applied to a virtualized clone of the module to verify zero-regression.
*   **Cryptographic Signature:** Patches are signed by the Wilsy Kernel to ensure authenticity.

### III. Execution (The Surgery)
*   **Atomic Merger:** Applies changes to the file system with transactional safety.
*   **Consistency Check:** Immediately re-scans with the Sentinel daemon to confirm drift removal.

### IV. Rollback Capability
*   **Snapshot Anchor:** Before any patch, a state-snapshot is stored. If the Sentinel detects failure, the system auto-reverts.

## 2. Patch Lifecycle Workflow
The Patch Engine follows a **Detect-Gen-Verify-Apply-Commit** protocol:

1.  **Detection:** Forensic Engine flags a drift or vulnerability.
2.  **Synthesis:** Patch Engine generates the surgical code block.
3.  **Simulated Verification:** Apply patch to sandboxed environment; run unit tests.
4.  **Surgical Application:** Atomically patch the production target.
5.  **Post-Patch Audit:** Sentinel confirms hash validation; update Knowledge Graph.
6.  **Immutable Log:** Archive the patch metadata for audit compliance.

## 3. Operational Commands (CLI)
The Wilsy Patch Engine is invoked via the `wilsy-patch` binary.

# 1. Apply a patch to a specific module
wilsy-patch apply ./tools/payroll/deduction.py --fix "hash-mismatch"

# 2. Simulate a patch without applying (Dry Run)
wilsy-patch simulate ./tools/payroll/deduction.py --source ./patches/v1.0.patch

# 3. Roll back the last applied patch
wilsy-patch revert --last

## 4. Competitive Moat
*   **Zero-Downtime Surgery:** Fixes are applied in memory and on-disk without stopping system services.
*   **Automated Verification:** We never guess; we simulate, verify, and then commit.
*   **Sentinel-Backed Integrity:** Every patch is cryptographically anchored to the system's history.
