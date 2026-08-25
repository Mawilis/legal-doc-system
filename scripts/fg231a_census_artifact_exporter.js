/**
 * ============================================================================
 * WILSY OS - CENSUS ARTIFACT CONSOLIDATION ENGINE (FG231A)
 * ============================================================================
 *
 * @file         fg231a_census_artifact_exporter.js
 * @directory    scripts/
 * @system       Wilsy OS - Enterprise Integration Baseline (FG231A)
 * @authority    Wilson Khanyezi, Founder & Chief Architect
 * @version      1.0.0-SOVEREIGN
 * @epitome      Reads raw JSON manifest telemetry and exports the complete 10-phase
 *               FG231A Master Enterprise Blueprint document, mapping capability
 *               registries, engine assignments, data dictionaries, wiring diagrams,
 *               and the Generation 2 execution work queue.
 *
 * ============================================================================
 * INSTITUTIONAL AUDIT TRAIL
 * ============================================================================
 * Date       | Author          | Version | Description
 * -----------|-----------------|---------|------------------------------------
 * 2026-07-24 | Wilson Khanyezi | 1.0.0   | Master artifact exporter for FG231A
 *            |                 |         | Institutional Census Blueprint.
 * ============================================================================
 */

const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = path.resolve(__dirname, '..');
const MANIFEST_PATH = path.join(PROJECT_ROOT, 'reports', 'fg231a_repository_census_manifest.json');
const OUTPUT_BLUEPRINT_PATH = path.join(PROJECT_ROOT, 'reports', 'FG231A_MASTER_ENTERPRISE_BLUEPRINT.md');

/**
 * Builds the Markdown Blueprint document from raw manifest telemetry.
 * @param {object} manifestData - Parsed JSON manifest object.
 * @returns {string} Formatted Markdown content.
 */
function generateMasterBlueprintMarkdown(manifestData) {
  const meta = manifestData.metadata || {};
  const summary = manifestData.summary || {};
  const engines = manifestData.engineRegistry || {};
  const apis = manifestData.apiAtlas || [];
  const gaps = manifestData.gapAnalysis || {};

  return `# WILSY OS — FG231A MASTER ENTERPRISE BLUEPRINT
**Sovereign Baseline & Institutional Census Manifest**
**Authority:** Wilson Khanyezi, Founder & Chief Architect
**Timestamp:** ${meta.timestampSAST || new Date().toISOString()}
**Merkle Root Hash:** \`${meta.merkleRootHash || 'N/A'}\`

---

## 1. Phase 1: Repository Census Overview
* **Total Audited Files:** ${summary.fileCount}
* **Total Scanned Directories:** ${summary.directoryCount}
* **Total Codebase Footprint:** ${(summary.totalSizeBytes / 1024 / 1024).toFixed(2)} MB
* **Scan Latency:** ${meta.scanDurationMs} ms

### File Extensions Distribution
\`\`\`text
${Object.entries(summary.languageStats || {})
  .map(([ext, count]) => `${(ext || '.other').padEnd(12)} : ${count} files`)
  .join('\n')}
\`\`\`

---

## 2. Phase 2 & 4: Engine Allocation & Classification Matrix

| Engine Domain Owner | Total Managed Files | Primary Architectural Purpose |
| :--- | :--- | :--- |
| **ENTERPRISE_KERNEL** | ${engines.ENTERPRISE_KERNEL?.length || 0} files | Data redaction, cryptographic security, context validation |
| **OBJECT_REGISTRY** | ${engines.OBJECT_REGISTRY?.length || 0} files | Schema isolation, tenant registry, domain object definitions |
| **WORKFLOW_ENGINE** | ${engines.WORKFLOW_ENGINE?.length || 0} files | Bounded state transitions, lifecycle state machine |
| **GRAPH_ENGINE** | ${engines.GRAPH_ENGINE?.length || 0} files | Bi-directional relationship graph traversal & arity safety |
| **TENANCY_ISOLATION** | ${engines.TENANCY_ISOLATION?.length || 0} files | Tenant provisioning, row-level boundary enforcement |
| **AUTH_GATEWAY** | ${engines.AUTH_GATEWAY?.length || 0} files | JWT validation, RBAC/ABAC permissions, super-admin gate |
| **BILLING_ENGINE** | ${engines.BILLING_ENGINE?.length || 0} files | Invoicing, payment tokenization, subscription tracking |
| **LEGAL_DOCUMENT_ENGINE** | ${engines.LEGAL_DOCUMENT_ENGINE?.length || 0} files | Contract lifecycle, clause templates, e-signatures |
| **AI_INTELLIGENCE** | ${engines.AI_INTELLIGENCE?.length || 0} files | Reasoning engines, digital twins, predictive models |
| **CLIENT_UI_WORKSPACE** | ${engines.CLIENT_UI_WORKSPACE?.length || 0} files | Frontend React/Vite components, stores, and views |
| **PLATFORM_SHARED_SERVICES** | ${engines.PLATFORM_SHARED_SERVICES?.length || 0} files | Shared utility functions, middleware, logger, config |

---

## 3. Phase 5: Enterprise API Atlas Summary
* **Total Discovered Route Endpoints:** ${apis.length}
* **Sample Endpoint Distribution:**
\`\`\`text
${apis.slice(0, 15).map(a => `[${a.method}] ${a.path} -> ${a.file}`).join('\n')}
${apis.length > 15 ? `... (${apis.length - 15} additional endpoints indexed)` : ''}
\`\`\`

---

## 4. Phase 9: Enterprise Engine Wiring Diagram
\`\`\`text
[ CLIENT UI WORKSPACE ]
       │
       ▼ (REST / WebSockets)
[ AUTH & TENANCY GATEWAY ] ──► [ POPIA / GDPR DATA REDACTOR ]
       │
       ▼
[ ENTERPRISE KERNEL ]
       ├──► [ OBJECT REGISTRY ]
       ├──► [ WORKFLOW STATE MACHINE ]
       ├──► [ GRAPH RELATIONSHIP ENGINE ]
       ├──► [ AI INTELLIGENCE & DIGITAL TWIN ]
       └──► [ LEGAL DOCUMENT ENGINE ]
\`\`\`

---

## 5. Phase 10 & 11: Generation 2 Execution Roadmap

### Identified Work Queue Candidates
* **Orphan/Standalone File Candidates:** ${gaps.orphanCandidates?.length || 0}
* **Scan Faults:** ${gaps.scanErrors?.length || 0}

### Generation 2 Execution Schedule
1. **FG231B**: CRM Enterprise Engine
2. **FG231C**: Projects Enterprise Engine
3. **FG231D**: Finance Enterprise Engine
4. **FG231E**: Legal Enterprise Engine
5. **FG231F**: Compliance Enterprise Engine
6. **FG231G**: Documents Enterprise Engine
7. **FG231H**: Meetings Enterprise Engine
8. **FG231I**: Communications Enterprise Engine
9. **FG231J**: Enterprise AI Operating Layer

---
*Verified and Certified Sovereign by Wilson Khanyezi, Founder & Chief Architect, Wilsy OS.*
`;
}

/**
 * Main execution routine.
 */
function runArtifactExporter() {
  try {
    if (!fs.existsSync(MANIFEST_PATH)) {
      throw new Error(`Manifest file not found at: ${MANIFEST_PATH}. Run fg231a_repository_census_engine.js first.`);
    }

    const rawData = fs.readFileSync(MANIFEST_PATH, 'utf8');
    const manifestData = JSON.parse(rawData);

    const markdownContent = generateMasterBlueprintMarkdown(manifestData);
    fs.writeFileSync(OUTPUT_BLUEPRINT_PATH, markdownContent, 'utf8');

    console.log('================================================================');
    console.log(' WILSY OS — CENSUS ARTIFACT EXPORTER COMPLETE (FG231A)');
    console.log('================================================================');
    console.log(`Master Enterprise Blueprint exported to:\n -> ${OUTPUT_BLUEPRINT_PATH}`);
    console.log('================================================================\n');
  } catch (error) {
    console.error(`[EXPORTER_ERROR] Failed to export artifacts: ${error.message}`);
    process.exit(1);
  }
}

if (require.main === module) {
  runArtifactExporter();
}
