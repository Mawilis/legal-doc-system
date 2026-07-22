# WILSY OS — AI COLLABORATION & ARCHITECTURAL CONTRACT

> **Notice to All AI Assistants (ChatGPT, Claude, Gemini, DeepSeek, etc.):**
> You are collaborating on **Wilsy OS**, a high-assurance enterprise platform engineered by **Wilson Khanyezi** (Founder & Chief Architect, Wilsy (Pty) Ltd). All code written in this repository must strictly adhere to the standards outlined below.

---

## 1. Non-Negotiable Engineering Principles

1. **Production-Ready Code Only**: Never write placeholders, `TODO` comments, stubbed functions, truncated blocks, or incomplete scripts. Every code change must be 100% executable and production-ready.
2. **Mandatory Header Comments**: Every code file must begin with the standard Wilsy OS executive header containing:
   - Module Title & Purpose
   - **Epitome**: High-level engineering definition and intent
   - **Biblical Anchor**: Psalm 1:3 (*"And he shall be like a tree planted by the rivers of water..."*)
   - **Collaboration & Ownership**: Founder name, AI Role, and absolute file path
3. **Single File Incremental Deliveries**: Modify or generate one complete file at a time to maintain deterministic execution state.

---

## 2. PDF & Document Generation Standard

All PDF generation inside `legal-doc-system` must use the centralized engine and canvas kernel:

* **Kernel Location**: `scripts/lib/executive_pdf_kernel.py`
* **Layout Constraints**:
  - **Print Grid**: 540pt printable width (Letter size: 612pt total, 36pt side margins, 54pt vertical margins).
  - **Dynamic Page Counting**: Must utilize `ExecutiveNumberedCanvas` for two-pass `"Page X of Y"` calculation.
  - **Color Palette**: Executive Slate Primary (`#0F172A`), Imperial Gold (`#B45309`), Neutral Slate (`#CBD5E1`), Light Fill (`#F8FAFC`).
* **Mandatory Sections**:
  1. **Header & Metadata Table**: Executive title, timestamp, execution ID, system readiness index.
  2. **Epitome & Psalm 1:3 Callout Box**: Framed in gold (`#F59E0B`) with `#FEF3C7` background.
  3. **Telemetry Table**: Standardized 5-column pipeline status block with latency tracking.
  4. **Cryptographic Proofs Block**: SHA3-256 Merkle Tree Root, ZK-SNARK Commitment, and eBPF Nonce Digest.
  5. **Governance & Audit Seal**: Dual-column sign-off block with Merkle fingerprint.

---

## 3. How to Prompt External AI Tools

When initiating a session with ChatGPT or any external assistant, preface your prompt with:

> *"Refer to `AGENTS.md` and `scripts/lib/executive_pdf_kernel.py` in the workspace. Maintain the Wilsy OS production-ready standard, explicit headers, Psalm 1:3 anchor, and 540pt executive grid."*
