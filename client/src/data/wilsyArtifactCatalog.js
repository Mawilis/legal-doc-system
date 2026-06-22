/* eslint-disable */

export const WILSY_ARTIFACT_CATALOG = Object.freeze([
  { id: 'non-disclosure-agreement', type: 'ndaa-enterprise', title: 'Non-Disclosure Agreement', category: 'Legal Contracts', description: 'One-way enterprise NDA with forensic proof and review controls.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'mutual-non-disclosure-agreement', type: 'mutual-nda', title: 'Mutual Non-Disclosure Agreement', category: 'Legal Contracts', description: 'Two-way confidentiality agreement for commercial evaluation and partnerships.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'master-services-agreement', type: 'master-services-agreement', title: 'Master Services Agreement', category: 'Legal Contracts', description: 'Master commercial services terms with scope, fees, liability and governance clauses.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'statement-of-work', type: 'statement-of-work', title: 'Statement of Work', category: 'Legal Contracts', description: 'Project-specific scope, deliverables, acceptance criteria, timelines and commercials.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'saas-subscription-agreement', type: 'saas-subscription-agreement', title: 'SaaS Subscription Agreement', category: 'Legal Contracts', description: 'Cloud subscription terms for Wilsy OS platform licensing and tenant access.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'service-level-agreement', type: 'service-level-agreement', title: 'Service Level Agreement', category: 'Legal Contracts', description: 'Availability, support, severity, credits, incident and escalation obligations.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'data-processing-agreement', type: 'data-processing-agreement', title: 'Data Processing Agreement', category: 'Privacy & POPIA', description: 'Processor and operator terms for personal information and regulated data handling.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'privacy-policy', type: 'privacy-policy', title: 'Privacy Policy', category: 'Privacy & POPIA', description: 'External privacy notice for data subjects, clients, users and platform visitors.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'paia-manual', type: 'paia-manual', title: 'PAIA Manual', category: 'Privacy & POPIA', description: 'Access to information manual for statutory disclosure and public availability.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'popia-compliance-pack', type: 'popia-compliance-pack', title: 'POPIA Compliance Pack', category: 'Privacy & POPIA', description: 'POPIA governance evidence bundle with roles, notices, risks and controls.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'cookie-policy', type: 'cookie-policy', title: 'Cookie Policy', category: 'Privacy & POPIA', description: 'Cookie and tracking technology disclosure for web and SaaS channels.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'terms-of-service', type: 'terms-of-service', title: 'Terms of Service', category: 'Legal Contracts', description: 'Platform terms for users, tenants, subscriptions, restrictions and liability.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },

  { id: 'employment-contract', type: 'employment-contract', title: 'Employment Contract', category: 'HR Documents', description: 'Employment agreement with role, compensation, duties, confidentiality and termination.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'offer-letter', type: 'offer-letter', title: 'Offer Letter', category: 'HR Documents', description: 'Candidate offer letter with conditions, remuneration and start date controls.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'contractor-agreement', type: 'contractor-agreement', title: 'Independent Contractor Agreement', category: 'HR Documents', description: 'Contractor terms with deliverables, IP, confidentiality and tax independence.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'employee-handbook', type: 'employee-handbook', title: 'Employee Handbook', category: 'HR Documents', description: 'HR policy handbook covering conduct, leave, discipline and workplace rules.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'hr-onboarding-pack', type: 'hr-onboarding-pack', title: 'HR Onboarding Pack', category: 'HR Documents', description: 'New employee onboarding checklist, declarations and acknowledgement records.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'hr-offboarding-pack', type: 'hr-offboarding-pack', title: 'HR Offboarding Pack', category: 'HR Documents', description: 'Exit checklist, asset return, access revocation and final payroll record.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'disciplinary-notice', type: 'disciplinary-notice', title: 'Disciplinary Notice', category: 'HR Documents', description: 'Formal disciplinary notice with allegations, hearing details and rights notice.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'grievance-form', type: 'grievance-form', title: 'Grievance Form', category: 'HR Documents', description: 'Employee grievance record with facts, desired outcome and investigation trail.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'performance-improvement-plan', type: 'performance-improvement-plan', title: 'Performance Improvement Plan', category: 'HR Documents', description: 'Structured PIP with objectives, support, review dates and consequences.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'leave-policy', type: 'leave-policy', title: 'Leave Policy', category: 'HR Documents', description: 'Annual, sick, family responsibility and statutory leave policy artifact.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'remote-work-policy', type: 'remote-work-policy', title: 'Remote Work Policy', category: 'HR Documents', description: 'Remote and hybrid work policy with equipment, security and productivity rules.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'confidentiality-and-ip-assignment', type: 'confidentiality-and-ip-assignment', title: 'Confidentiality and IP Assignment', category: 'HR Documents', description: 'Employee and contractor confidentiality, inventions and IP assignment terms.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },

  { id: 'board-pack', type: 'board-pack', title: 'Board Pack', category: 'Governance', description: 'Board-ready governance pack with agenda, decisions, risks and executive summary.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'board-resolution', type: 'board-resolution', title: 'Board Resolution', category: 'Governance', description: 'Formal board resolution with authority, approvals and execution lines.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'minutes-of-meeting', type: 'minutes-of-meeting', title: 'Minutes of Meeting', category: 'Governance', description: 'Structured meeting minutes with attendees, decisions, actions and proof trail.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'delegation-of-authority', type: 'delegation-of-authority', title: 'Delegation of Authority Matrix', category: 'Governance', description: 'Authority limits, approval thresholds and executive delegation controls.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'shareholder-resolution', type: 'shareholder-resolution', title: 'Shareholder Resolution', category: 'Governance', description: 'Shareholder approval record with voting, authority and corporate action proof.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'risk-register', type: 'risk-register', title: 'Risk Register', category: 'Governance', description: 'Enterprise risk register with owners, ratings, mitigations and review posture.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },

  { id: 'annual-compliance-evidence-pack', type: 'annual-compliance-evidence-pack', title: 'Annual Compliance Evidence Pack', category: 'Compliance', description: 'Annual evidence pack for audits, board review, regulators and investor diligence.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'fica-onboarding-pack', type: 'fica-onboarding-pack', title: 'FICA Onboarding Pack', category: 'Compliance', description: 'Client verification, risk rating, KYC evidence and approval trail.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'compliance-incident-report', type: 'compliance-incident-report', title: 'Compliance Incident Report', category: 'Compliance', description: 'Incident facts, impact, root cause, containment, remediation and approvals.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'audit-evidence-pack', type: 'audit-evidence-pack', title: 'Audit Evidence Pack', category: 'Compliance', description: 'Audit-ready evidence bundle with control ownership and proof records.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'data-retention-policy', type: 'data-retention-policy', title: 'Data Retention Policy', category: 'Compliance', description: 'Retention, deletion, legal hold, archive and disposal policy artifact.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'regulatory-response-letter', type: 'regulatory-response-letter', title: 'Regulatory Response Letter', category: 'Compliance', description: 'Formal response to regulator, auditor or external authority request.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },

  { id: 'tax-invoice-and-credit-note', type: 'tax-invoice-and-credit-note', title: 'Tax Invoice and Credit Note', category: 'Finance', description: 'Tax invoice and credit note artifact with finance proof trail.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'quotation', type: 'quotation', title: 'Quotation', category: 'Finance', description: 'Commercial quotation with pricing, validity, assumptions and approval footer.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'purchase-order', type: 'purchase-order', title: 'Purchase Order', category: 'Finance', description: 'Purchase order with supplier, line items, approvals and delivery controls.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'expense-claim-form', type: 'expense-claim-form', title: 'Expense Claim Form', category: 'Finance', description: 'Employee expense claim with approvals, receipts and reimbursement trail.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'budget-approval-memo', type: 'budget-approval-memo', title: 'Budget Approval Memo', category: 'Finance', description: 'Budget request, commercial justification, approval limits and risk notes.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'financial-control-pack', type: 'financial-control-pack', title: 'Financial Control Pack', category: 'Finance', description: 'Finance control evidence for approval, reconciliation, audit and reporting.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },

  { id: 'vendor-onboarding-pack', type: 'vendor-onboarding-pack', title: 'Vendor Onboarding Pack', category: 'Procurement', description: 'Supplier onboarding, declarations, due diligence and approval controls.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'supplier-due-diligence-report', type: 'supplier-due-diligence-report', title: 'Supplier Due Diligence Report', category: 'Procurement', description: 'Supplier risk assessment with compliance, financial and delivery checks.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'rfp-evaluation-report', type: 'rfp-evaluation-report', title: 'RFP Evaluation Report', category: 'Procurement', description: 'Tender or proposal scoring, recommendation, risks and award proof.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'vendor-termination-letter', type: 'vendor-termination-letter', title: 'Vendor Termination Letter', category: 'Procurement', description: 'Supplier termination notice with obligations, handover and access revocation.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },

  { id: 'sales-proposal', type: 'sales-proposal', title: 'Sales Proposal', category: 'Sales & Customer', description: 'Client proposal with scope, value, timelines, assumptions and commercials.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'customer-success-qbr', type: 'customer-success-qbr', title: 'Customer Success QBR', category: 'Sales & Customer', description: 'Quarterly business review with usage, outcomes, risks and roadmap.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'renewal-letter', type: 'renewal-letter', title: 'Renewal Letter', category: 'Sales & Customer', description: 'Subscription or service renewal notice with revised commercial terms.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'change-order', type: 'change-order', title: 'Change Order', category: 'Sales & Customer', description: 'Scope, price, timeline or delivery change record with approval proof.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'implementation-plan', type: 'implementation-plan', title: 'Implementation Plan', category: 'Sales & Customer', description: 'Client onboarding implementation plan with milestones, owners and dependencies.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },

  { id: 'security-incident-report', type: 'security-incident-report', title: 'Security Incident Report', category: 'Security & IT', description: 'Security incident record with impact, containment, root cause and remediation.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'access-request-form', type: 'access-request-form', title: 'Access Request Form', category: 'Security & IT', description: 'System access request with business justification and approval trail.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'access-revocation-form', type: 'access-revocation-form', title: 'Access Revocation Form', category: 'Security & IT', description: 'Access removal record for offboarding, incident response or privilege reduction.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'change-advisory-record', type: 'change-advisory-record', title: 'Change Advisory Record', category: 'Security & IT', description: 'IT change approval record with risk, rollback and implementation proof.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'backup-restore-evidence', type: 'backup-restore-evidence', title: 'Backup Restore Evidence', category: 'Security & IT', description: 'Backup restoration proof with timing, result, owner and exception notes.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'vulnerability-exception', type: 'vulnerability-exception', title: 'Vulnerability Exception', category: 'Security & IT', description: 'Risk acceptance record for vulnerability remediation exceptions.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },

  { id: 'project-charter', type: 'project-charter', title: 'Project Charter', category: 'Project Delivery', description: 'Project mandate, objectives, stakeholders, governance and delivery controls.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'project-status-report', type: 'project-status-report', title: 'Project Status Report', category: 'Project Delivery', description: 'Executive project status with schedule, cost, risk, issues and actions.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'evm-performance-report', type: 'evm-performance-report', title: 'EVM Performance Report', category: 'Project Delivery', description: 'Earned value management report with SPI, CPI, EAC, ETC and variance controls.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'variation-order', type: 'variation-order', title: 'Variation Order', category: 'Project Delivery', description: 'Approved variation with scope, pricing, schedule and authority trail.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'payment-certificate', type: 'payment-certificate', title: 'Payment Certificate', category: 'Project Delivery', description: 'Payment certification record for project, construction or service milestones.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] },
  { id: 'site-instruction', type: 'site-instruction', title: 'Site Instruction', category: 'Project Delivery', description: 'Site or delivery instruction with responsible parties, action and approval proof.', formats: ['PDF', 'DOCX', 'JSON', 'EMAIL'] }
]);


/**
 * @constant BUSINESS_ARTIFACT_CATALOG
 * @description Compatibility export consumed by the Business Artifact Studio and HMR reloads.
 * @collaboration Stabilizes artifact registry imports across previous and current component versions.
 */
export const BUSINESS_ARTIFACT_CATALOG = WILSY_ARTIFACT_CATALOG;

/**
 * WILSY_R13C0_ARTIFACT_EXPORT_ALIAS_CONTRACT
 * @description Provides backwards-compatible artifact catalog exports expected by BusinessArtifactStudio.
 * @collaboration Keeps artifact studio imports stable while preserving the existing catalog source of truth.
 */
export const WILSY_BUSINESS_ARTIFACT_CATALOG = WILSY_ARTIFACT_CATALOG;
export const ARTIFACT_CATALOG = WILSY_BUSINESS_ARTIFACT_CATALOG;
export const BUSINESS_ARTIFACTS = WILSY_BUSINESS_ARTIFACT_CATALOG;
export default WILSY_BUSINESS_ARTIFACT_CATALOG;
