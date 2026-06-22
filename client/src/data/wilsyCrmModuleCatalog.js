/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - CRM MODULE CATALOG [R18AD70-SOVEREIGN-SALES-CRM-OBLITERATION-DOCTRINE]                                           ║
 * ║ SALES | CRM | SDR | SUCCESS | REVENUE | IFRS | COMPLIANCE | FORENSICS | INVESTOR TELEMETRY | AUDIT                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/data/wilsyCrmModuleCatalog.js                          ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION                                                                                                          ║
 * ║ 1. Wilson Khanyezi - Mandated a non-prototype CRM/Sales OS that can operate across any business model and tenant.       ║
 * ║ 2. AI Engineering - Codified CRM modules as governed operating contracts with tenant isolation and source posture.       ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 *
 * @fileoverview Enterprise CRM module catalog for Wilsy OS.
 * This file is the source-of-truth module contract for CRM, Sales, SDR,
 * Customer Success, Support, migration, revenue intelligence and audit surfaces.
 * It does not fabricate records; it describes governed modules, route posture,
 * role posture, source requirements, receipt posture and tenant boundaries.
 */

export const WILSY_CRM_MODULE_CATALOG_VERSION = 'R18AD70-SOVEREIGN-SALES-CRM-OBLITERATION-DOCTRINE';

export const WILSY_CRM_DEFAULT_MODULE_ID = 'leads';

export const WILSY_CRM_DEFAULT_WORKSPACE_ID = 'command';

export const WILSY_CRM_SOURCE_STATUS = Object.freeze({
  sourceRequired: 'SOURCE_REQUIRED',
  sourceLive: 'SOURCE_LIVE',
  sourcePending: 'SOURCE_PENDING',
  sourceStale: 'SOURCE_STALE',
  sourceDegraded: 'SOURCE_DEGRADED',
  sourceError: 'SOURCE_ERROR',
  sourceForbidden: 'SOURCE_FORBIDDEN'
});

export const WILSY_CRM_ROUTE_POSTURE = Object.freeze({
  live: 'ROUTE_LIVE',
  required: 'ROUTE_REQUIRED',
  planned: 'ROUTE_PLANNED',
  degraded: 'ROUTE_DEGRADED',
  forbidden: 'ROUTE_FORBIDDEN'
});

export const WILSY_CRM_TENANT_BOUNDARY = Object.freeze({
  enforcement: 'TENANT_SCOPED_ONLY',
  queryKey: 'tenantId',
  browserHeader: 'X-Tenant-Id',
  sovereignOverride: 'FOUNDER_OMEGA_AUDITED_OVERRIDE',
  noSharedDataDoctrine: 'TENANTS_NEVER_SHARE_DATA',
  dataLeakPosture: 'ZERO_TOLERANCE'
});

export const WILSY_CRM_PERSONAS = Object.freeze({
  founderOmega: 'founder_omega',
  salesLeader: 'sales_leader',
  salesManager: 'sales_manager',
  accountExecutive: 'account_executive',
  salesRepresentative: 'sales_representative',
  sdr: 'sdr',
  crmOperator: 'crm_operator',
  customerSuccess: 'customer_success',
  supportAgent: 'support_agent',
  revenueOperations: 'revenue_operations',
  complianceOfficer: 'compliance_officer',
  tenantAdmin: 'tenant_admin'
});

export const WILSY_CRM_DISCOVERY_ROLE_MAP = Object.freeze({
  sales_representative: 'crm_os',
  account_executive: 'crm_os',
  business_development: 'crm_os',
  sales_manager: 'crm_os',
  sales_director: 'crm_os',
  sdr: 'crm_os',
  crm: 'crm_os',
  crm_operator: 'crm_os',
  customer_success: 'crm_os',
  customer_success_manager: 'crm_os',
  support_agent: 'crm_os',
  revenue_operations: 'crm_os',
  founder: 'founder_override_to_crm_os',
  super_admin: 'sovereign_override_to_crm_os',
  omega: 'omega_override_to_crm_os'
});

export const WILSY_CRM_WORKSPACE_CATALOG = Object.freeze([
  {
    id: 'command',
    label: 'Command',
    detail: 'Executive CRM operating cockpit',
    icon: 'home',
    routePosture: WILSY_CRM_ROUTE_POSTURE.live,
    doctrine: 'One command surface for sales, CRM, success, support and revenue posture.'
  },
  {
    id: 'records',
    label: 'Records',
    detail: 'Tenant-scoped CRM ledgers',
    icon: 'database',
    routePosture: WILSY_CRM_ROUTE_POSTURE.live,
    doctrine: 'Every row is source-postured and tenant-scoped.'
  },
  {
    id: 'pipeline',
    label: 'Pipeline',
    detail: 'Revenue and stage control',
    icon: 'target',
    routePosture: WILSY_CRM_ROUTE_POSTURE.live,
    doctrine: 'Pipeline truth must separate value, probability, stage and evidence.'
  },
  {
    id: 'success',
    label: 'Success',
    detail: 'Customer health, renewal and expansion',
    icon: 'users',
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    doctrine: 'Customer success is a revenue command layer, not a passive support page.'
  },
  {
    id: 'support',
    label: 'Support',
    detail: 'Ticket, SLA and customer issue command',
    icon: 'messageSquare',
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    doctrine: 'Zendesk-class desk, with Wilsy forensic receipts and tenant controls.'
  },
  {
    id: 'automation',
    label: 'Automation',
    detail: 'Workflows, sequences and rule rails',
    icon: 'wand',
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    doctrine: 'Automation can recommend and route; it never silently fabricates source truth.'
  },
  {
    id: 'intelligence',
    label: 'Intelligence',
    detail: 'AI command memo, forecast and next-best-action',
    icon: 'sparkles',
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    doctrine: 'AI command is an evidence-aware recommendation layer, not fake model output.'
  },
  {
    id: 'import',
    label: 'Import',
    detail: 'HubSpot, Zoho, Zendesk, Salesforce and CSV migration intake',
    icon: 'upload',
    routePosture: WILSY_CRM_ROUTE_POSTURE.live,
    doctrine: 'Competitor migration becomes governed intake with dedupe and proof posture.'
  },
  {
    id: 'evidence',
    label: 'Evidence',
    detail: 'Source registry, receipts and audit posture',
    icon: 'shield',
    routePosture: WILSY_CRM_ROUTE_POSTURE.live,
    doctrine: 'Every serious CRM action must be auditable.'
  }
]);

export const WILSY_CRM_IMPORT_VENDOR_CATALOG = Object.freeze([
  {
    id: 'GENERIC_CRM',
    label: 'Generic CRM CSV',
    competitorClass: 'portable_csv',
    intakePosture: 'CSV_PREVIEW_REQUIRED',
    dedupeKeys: Object.freeze(['email', 'name', 'externalId']),
    doctrine: 'No row enters tenant CRM without preview, dedupe and source status.'
  },
  {
    id: 'HUBSPOT',
    label: 'HubSpot',
    competitorClass: 'marketing_sales_crm',
    intakePosture: 'CONNECTOR_OR_CSV_EXPORT',
    dedupeKeys: Object.freeze(['email', 'hubspotId', 'company']),
    doctrine: 'HubSpot exports must map marketing, lifecycle and pipeline evidence separately.'
  },
  {
    id: 'ZOHO',
    label: 'Zoho CRM',
    competitorClass: 'broad_business_crm',
    intakePosture: 'CONNECTOR_OR_CSV_EXPORT',
    dedupeKeys: Object.freeze(['email', 'zohoId', 'accountName']),
    doctrine: 'Zoho migration must preserve account, deal, task and activity ownership.'
  },
  {
    id: 'ZENDESK',
    label: 'Zendesk',
    competitorClass: 'support_ticketing',
    intakePosture: 'CONNECTOR_OR_CSV_EXPORT',
    dedupeKeys: Object.freeze(['ticketId', 'email', 'externalId']),
    doctrine: 'Zendesk migration must distinguish tickets, users, organizations and SLA posture.'
  },
  {
    id: 'SALESFORCE',
    label: 'Salesforce',
    competitorClass: 'enterprise_crm',
    intakePosture: 'CONNECTOR_OR_CSV_EXPORT',
    dedupeKeys: Object.freeze(['salesforceId', 'email', 'accountId']),
    doctrine: 'Salesforce migration must keep leads, contacts, accounts and opportunities governed.'
  },
  {
    id: 'FRESHDESK',
    label: 'Freshdesk',
    competitorClass: 'support_ticketing',
    intakePosture: 'CONNECTOR_OR_CSV_EXPORT',
    dedupeKeys: Object.freeze(['ticketId', 'email', 'externalId']),
    doctrine: 'Freshdesk intake must route SLA, ticket state and requester identity into proofed modules.'
  },
  {
    id: 'INTERCOM',
    label: 'Intercom',
    competitorClass: 'conversation_success',
    intakePosture: 'CONNECTOR_OR_CSV_EXPORT',
    dedupeKeys: Object.freeze(['conversationId', 'email', 'userId']),
    doctrine: 'Intercom migration must separate conversations, customer health and support actions.'
  }
]);

export const WILSY_CRM_MODULE_GROUPS = Object.freeze({
  acquisition: {
    label: 'Acquisition',
    doctrine: 'SDR, lead, campaign and contact capture with source proof.',
    buyerSignal: 'revenue creation'
  },
  relationship: {
    label: 'Relationship Graph',
    doctrine: 'Contacts, accounts, partners and suppliers as a governed business graph.',
    buyerSignal: 'customer intelligence'
  },
  revenue: {
    label: 'Revenue Command',
    doctrine: 'Deals, opportunities, quotes, invoices, forecast and board revenue posture.',
    buyerSignal: 'pipeline truth'
  },
  work: {
    label: 'Work Execution',
    doctrine: 'Tasks, meetings, visits and projects become command queues, not reminders.',
    buyerSignal: 'operator velocity'
  },
  service: {
    label: 'Service and Success',
    doctrine: 'Tickets, cases, conversations, customer health and renewal risk in one command layer.',
    buyerSignal: 'retention and SLA control'
  },
  governance: {
    label: 'Governance',
    doctrine: 'Contracts, authority, risks, audit and source registry proof.',
    buyerSignal: 'regulator-ready CRM'
  },
  automation: {
    label: 'Automation and AI',
    doctrine: 'Workflows, next-best-action, intelligence and migration posture.',
    buyerSignal: 'operating leverage'
  },
  intelligence: {
    label: 'Sales Intelligence',
    doctrine: 'Lead scoring, BANT qualification, predictive win probability and next-best-action.',
    buyerSignal: 'sales inevitability'
  },
  financeEvidence: {
    label: 'Revenue Evidence',
    doctrine: 'Contracts, invoices, receipts, IFRS posture and revenue proof in one command desk.',
    buyerSignal: 'investor-grade revenue trust'
  },
  complianceHud: {
    label: 'Compliance HUD',
    doctrine: 'POPIA, GDPR, SOC2 and customer clauses bound to every customer record.',
    buyerSignal: 'regulator-ready customer ledger'
  },
  forensicFlow: {
    label: 'Forensic Sales Flow',
    doctrine: 'Every lead transfer, pipeline movement, contract and disclosure has chain-of-custody posture.',
    buyerSignal: 'tamper-proof commercial operation'
  },
  investor: {
    label: 'Investor Strip',
    doctrine: 'Sovereign root hash, sealed receipts and live revenue telemetry displayed without fake metrics.',
    buyerSignal: 'investor confidence'
  }
});

const baseReceiptContract = Object.freeze({
  create: 'CRM_CREATE_RECEIPT_REQUIRED',
  update: 'CRM_UPDATE_RECEIPT_REQUIRED',
  delete: 'CRM_DELETE_RECEIPT_REQUIRED',
  import: 'CRM_IMPORT_RECEIPT_REQUIRED',
  export: 'CRM_EXPORT_RECEIPT_REQUIRED',
  routeGap: 'CRM_ROUTE_REQUIRED_RECEIPT',
  sourceError: 'CRM_SOURCE_ERROR_RECEIPT'
});

const baseSourceContract = Object.freeze({
  statusField: 'sourceStatus',
  systemField: 'sourceSystem',
  externalIdField: 'sourceId',
  minimumStatus: WILSY_CRM_SOURCE_STATUS.sourceRequired,
  liveStatus: WILSY_CRM_SOURCE_STATUS.sourceLive,
  missingStatus: WILSY_CRM_SOURCE_STATUS.sourceRequired,
  doctrine: 'Source truth is explicit; missing source posture is never hidden.'
});

const baseTenantContract = Object.freeze({
  ...WILSY_CRM_TENANT_BOUNDARY,
  recordFilter: 'tenantId === activeTenantId',
  founderView: 'Founder/Omega view is audited and tenant-scoped by selected tenant context.',
  employeeView: 'Employee view is restricted to authenticated tenant and permitted role.'
});

export const WILSY_CRM_QUALIFICATION_FRAMEWORKS = Object.freeze({
  bant: Object.freeze(['budget', 'authority', 'need', 'timeline']),
  medicc: Object.freeze(['metrics', 'economicBuyer', 'decisionCriteria', 'decisionProcess', 'identifyPain', 'champion', 'competition']),
  sovereignFit: Object.freeze(['tenantBoundary', 'sourceTrust', 'authorityToBind', 'complianceNeed', 'revenueMateriality']),
  doctrine: 'Lead intelligence must explain score, qualification gaps and next action without inventing customer facts.'
});

export const WILSY_CRM_COMPLIANCE_CLAUSE_CATALOG = Object.freeze({
  popia: Object.freeze(['POPIA_S19_SECURITY_SAFEGUARDS', 'POPIA_S11_PROCESSING_LIMITATION', 'POPIA_S18_NOTIFICATION']),
  gdpr: Object.freeze(['GDPR_ART_5_PRINCIPLES', 'GDPR_ART_6_LAWFUL_BASIS', 'GDPR_ART_32_SECURITY']),
  soc2: Object.freeze(['SOC2_SECURITY', 'SOC2_CONFIDENTIALITY', 'SOC2_AVAILABILITY']),
  ifrs: Object.freeze(['IFRS15_REVENUE_RECOGNITION', 'IFRS9_RECEIVABLE_RISK', 'IAS1_DISCLOSURE_POSTURE']),
  doctrine: 'Customer records, contracts, invoices and support events must carry clause posture when used for regulated decisions.'
});

export const WILSY_CRM_FORENSIC_FLOW_CATALOG = Object.freeze({
  leadEntered: 'LEAD_ENTERED_VERIFIED_SOURCE_RECEIPT',
  qualificationUpdated: 'QUALIFICATION_UPDATED_BANT_RECEIPT',
  pipelineMoved: 'PIPELINE_STAGE_MOVED_CHAIN_OF_CUSTODY',
  dealClosed: 'DEAL_CLOSED_CONTRACT_IFRS_RECEIPT',
  invoiceIssued: 'INVOICE_ISSUED_REVENUE_LEDGER_RECEIPT',
  supportEscalated: 'SUPPORT_ESCALATION_CUSTOMER_RISK_RECEIPT',
  disclosureExported: 'REGULATOR_DISCLOSURE_EXPORT_RECEIPT',
  sovereignRootAnchored: 'SOVEREIGN_ROOT_HASH_ANCHORED',
  doctrine: 'Every material CRM action must become a receipt-capable forensic event.'
});

export const WILSY_CRM_CONNECTOR_CONTRACTS = Object.freeze({
  email: Object.freeze({
    id: 'email_connector',
    vendors: Object.freeze(['GMAIL', 'OUTLOOK', 'IMAP']),
    requiredEvidence: Object.freeze(['messageId', 'threadId', 'sentAt', 'operatorId', 'tenantId']),
    posture: WILSY_CRM_SOURCE_STATUS.sourceRequired
  }),
  linkedin: Object.freeze({
    id: 'linkedin_connector',
    vendors: Object.freeze(['LINKEDIN_EXPORT', 'SALES_NAVIGATOR_EXPORT']),
    requiredEvidence: Object.freeze(['profileUrl', 'engagementType', 'capturedAt', 'operatorId', 'tenantId']),
    posture: WILSY_CRM_SOURCE_STATUS.sourceRequired
  }),
  finance: Object.freeze({
    id: 'finance_connector',
    vendors: Object.freeze(['WILSY_BILLING', 'XERO', 'QUICKBOOKS', 'SAGE']),
    requiredEvidence: Object.freeze(['contractId', 'invoiceId', 'receiptId', 'ledgerEntryId', 'tenantId']),
    posture: WILSY_CRM_SOURCE_STATUS.sourceRequired
  }),
  hr: Object.freeze({
    id: 'hr_connector',
    vendors: Object.freeze(['WILSY_HR', 'CSV_EMPLOYEE_LEDGER']),
    requiredEvidence: Object.freeze(['employeeId', 'role', 'sessionId', 'performancePeriod', 'tenantId']),
    posture: WILSY_CRM_SOURCE_STATUS.sourceRequired
  }),
  doctrine: 'Connectors are not decorative integrations; they are source-truth rails with evidence requirements.'
});

export const WILSY_CRM_BACKEND_SERVICE_CONTRACTS = Object.freeze({
  authentication: 'MULTI_TENANT_LOGIN_SHA3_512_RECEIPTS',
  telemetry: 'LIVE_CRM_METRIC_STREAMS',
  audit: 'CRYPTOGRAPHIC_ACTION_RECEIPTS_CHAINED_TO_SOVEREIGN_ROOT',
  governance: 'CHAIN_OF_CUSTODY_FOR_LEAD_TRANSFER_PROOF_MOVEMENT_AND_CONTRACTS',
  evidenceLedger: 'CRM_ACTIVITY_TO_REGULATOR_READY_EVIDENCE_MAPPING',
  exportApi: 'ONE_CLICK_DISCLOSURE_PACKAGE_ZIP',
  doctrine: 'Backend CRM services must prove identity, action, revenue and compliance movement.'
});

export const WILSY_CRM_INVESTOR_TELEMETRY_CONTRACT = Object.freeze({
  sovereignRootHash: 'SOURCE_REQUIRED',
  sealedReceipts: 'SOURCE_REQUIRED',
  revenueTelemetry: 'SOURCE_REQUIRED',
  pipelineTelemetry: 'SOURCE_REQUIRED',
  complianceReadiness: 'SOURCE_REQUIRED',
  disclosureBundleReadiness: 'SOURCE_REQUIRED',
  noFakeMetrics: true,
  doctrine: 'Investor telemetry must show live source posture or SOURCE_REQUIRED, never invented progress.'
});

export const WILSY_CRM_MODULE_CATALOG = Object.freeze([
  {
    id: 'leads',
    label: 'Leads',
    singular: 'Lead',
    icon: 'users',
    group: 'acquisition',
    route: 'leads',
    workspace: 'records',
    primary: 'name',
    secondary: 'company',
    money: null,
    boardBy: 'stage',
    lanes: Object.freeze(['new', 'contacted', 'qualified', 'converted', 'lost']),
    fields: Object.freeze(['name', 'company', 'email', 'phone', 'source', 'stage', 'owner', 'createdAt']),
    personas: Object.freeze(['sdr', 'sales_representative', 'account_executive', 'sales_manager', 'founder_omega']),
    serviceMethods: Object.freeze(['getLeads', 'createLead', 'updateLead', 'deleteLead']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.live,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Score lead quality, surface next outreach, detect missing source and route conversion.',
    migrationPosture: Object.freeze(['HUBSPOT', 'ZOHO', 'SALESFORCE', 'GENERIC_CRM']),
    competitiveWedge: 'Lead intake is source-proofed, tenant-scoped and conversion-ready.'
  },
  {
    id: 'contacts',
    label: 'Contacts',
    singular: 'Contact',
    icon: 'contacts',
    group: 'relationship',
    route: 'contacts',
    workspace: 'records',
    primary: 'name',
    secondary: 'accountName',
    money: null,
    boardBy: 'status',
    lanes: Object.freeze(['new', 'active', 'at_risk', 'inactive']),
    fields: Object.freeze(['name', 'accountName', 'email', 'phone', 'title', 'consentStatus', 'status']),
    personas: Object.freeze(['sales_representative', 'account_executive', 'customer_success', 'support_agent', 'founder_omega']),
    serviceMethods: Object.freeze(['getContacts', 'createContact', 'updateContact', 'deleteContact']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.live,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Build relationship context, consent posture and account influence graph.',
    migrationPosture: Object.freeze(['HUBSPOT', 'ZOHO', 'ZENDESK', 'SALESFORCE', 'INTERCOM', 'GENERIC_CRM']),
    competitiveWedge: 'Contact records carry consent and source posture from day one.'
  },
  {
    id: 'accounts',
    label: 'Accounts',
    singular: 'Account',
    icon: 'accounts',
    group: 'relationship',
    route: 'accounts',
    workspace: 'records',
    primary: 'name',
    secondary: 'industry',
    money: 'annualRevenue',
    boardBy: 'status',
    lanes: Object.freeze(['prospect', 'active', 'expansion', 'at_risk', 'churned']),
    fields: Object.freeze(['name', 'industry', 'annualRevenue', 'owner', 'healthScore', 'status']),
    personas: Object.freeze(['account_executive', 'sales_manager', 'customer_success', 'revenue_operations', 'founder_omega']),
    serviceMethods: Object.freeze(['getAccounts', 'createAccount', 'updateAccount', 'deleteAccount']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.live,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Summarize account health, expansion paths, risk and relationship gaps.',
    migrationPosture: Object.freeze(['HUBSPOT', 'ZOHO', 'SALESFORCE', 'GENERIC_CRM']),
    competitiveWedge: 'Account intelligence is a tenant-safe business graph, not a flat company table.'
  },
  {
    id: 'deals',
    label: 'Deals',
    singular: 'Deal',
    icon: 'deals',
    group: 'revenue',
    route: 'deals',
    workspace: 'pipeline',
    primary: 'name',
    secondary: 'accountName',
    money: 'value',
    boardBy: 'stage',
    lanes: Object.freeze(['new', 'qualified', 'proposal', 'negotiation', 'won', 'lost']),
    fields: Object.freeze(['name', 'accountName', 'value', 'probability', 'closingDate', 'owner', 'stage']),
    personas: Object.freeze(['account_executive', 'sales_manager', 'sales_leader', 'revenue_operations', 'founder_omega']),
    serviceMethods: Object.freeze(['getDeals', 'createDeal', 'updateDeal', 'deleteDeal']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.live,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Detect deal risk, next action, missing stakeholder and forecast confidence.',
    migrationPosture: Object.freeze(['HUBSPOT', 'ZOHO', 'SALESFORCE', 'GENERIC_CRM']),
    competitiveWedge: 'Pipeline value is probability-aware, receipt-backed and boardroom readable.'
  },
  {
    id: 'tasks',
    label: 'Tasks',
    singular: 'Task',
    icon: 'tasks',
    group: 'work',
    route: 'tasks',
    workspace: 'records',
    primary: 'subject',
    secondary: 'relatedTo',
    money: null,
    boardBy: 'status',
    lanes: Object.freeze(['open', 'in_progress', 'blocked', 'done', 'overdue']),
    fields: Object.freeze(['subject', 'relatedTo', 'owner', 'dueDate', 'priority', 'status']),
    personas: Object.freeze(['sdr', 'sales_representative', 'account_executive', 'customer_success', 'support_agent']),
    serviceMethods: Object.freeze(['getTasks', 'createTask', 'updateTask', 'deleteTask']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.live,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Prioritize work queue, flag overdue tasks and recommend next action.',
    migrationPosture: Object.freeze(['HUBSPOT', 'ZOHO', 'SALESFORCE', 'GENERIC_CRM']),
    competitiveWedge: 'Tasks become a command queue with SLA and receipt posture.'
  },
  {
    id: 'meetings',
    label: 'Meetings',
    singular: 'Meeting',
    icon: 'calendar',
    group: 'work',
    route: 'meetings',
    workspace: 'records',
    primary: 'subject',
    secondary: 'accountName',
    money: null,
    boardBy: 'status',
    lanes: Object.freeze(['scheduled', 'completed', 'missed', 'rescheduled']),
    fields: Object.freeze(['subject', 'accountName', 'contactName', 'scheduledAt', 'owner', 'status']),
    personas: Object.freeze(['sales_representative', 'account_executive', 'customer_success', 'founder_omega']),
    serviceMethods: Object.freeze(['getMeetings', 'createMeeting', 'updateMeeting', 'deleteMeeting']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.live,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Summarize meeting context and surface missing preparation items.',
    migrationPosture: Object.freeze(['HUBSPOT', 'ZOHO', 'SALESFORCE', 'GENERIC_CRM']),
    competitiveWedge: 'Meetings connect to account context and command receipts.'
  },
  {
    id: 'visits',
    label: 'Visits',
    singular: 'Visit',
    icon: 'visits',
    group: 'work',
    route: 'visits',
    workspace: 'records',
    primary: 'subject',
    secondary: 'location',
    money: null,
    boardBy: 'status',
    lanes: Object.freeze(['planned', 'completed', 'missed']),
    fields: Object.freeze(['subject', 'accountName', 'location', 'scheduledAt', 'status']),
    personas: Object.freeze(['sales_representative', 'account_executive', 'customer_success']),
    serviceMethods: Object.freeze(['getVisits', 'createVisit', 'updateVisit', 'deleteVisit']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.live,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Connect field visits to deal, account and customer health posture.',
    migrationPosture: Object.freeze(['ZOHO', 'SALESFORCE', 'GENERIC_CRM']),
    competitiveWedge: 'Field activity is visible inside CRM source truth.'
  },
  {
    id: 'tickets',
    label: 'Tickets',
    singular: 'Ticket',
    icon: 'tickets',
    group: 'service',
    route: 'tickets',
    workspace: 'support',
    primary: 'subject',
    secondary: 'accountName',
    money: null,
    boardBy: 'status',
    lanes: Object.freeze(['new', 'open', 'waiting', 'escalated', 'resolved']),
    fields: Object.freeze(['subject', 'accountName', 'priority', 'slaStatus', 'owner', 'status']),
    personas: Object.freeze(['support_agent', 'customer_success', 'crm_operator', 'founder_omega']),
    serviceMethods: Object.freeze(['getTickets', 'createTicket', 'updateTicket', 'deleteTicket']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Classify SLA risk, escalation route and customer impact.',
    migrationPosture: Object.freeze(['ZENDESK', 'FRESHDESK', 'INTERCOM', 'ZOHO', 'GENERIC_CRM']),
    competitiveWedge: 'Zendesk-class support with forensic CRM receipts and account intelligence.'
  },
  {
    id: 'cases',
    label: 'Cases',
    singular: 'Case',
    icon: 'cases',
    group: 'service',
    route: 'cases',
    workspace: 'support',
    primary: 'subject',
    secondary: 'accountName',
    money: null,
    boardBy: 'status',
    lanes: Object.freeze(['new', 'open', 'escalated', 'resolved']),
    fields: Object.freeze(['subject', 'accountName', 'priority', 'owner', 'status']),
    personas: Object.freeze(['support_agent', 'customer_success', 'compliance_officer', 'founder_omega']),
    serviceMethods: Object.freeze(['getCases', 'createCase', 'updateCase', 'deleteCase']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Separate support case, compliance case and account risk posture.',
    migrationPosture: Object.freeze(['ZENDESK', 'FRESHDESK', 'SALESFORCE', 'GENERIC_CRM']),
    competitiveWedge: 'Cases carry compliance, SLA and source posture.'
  },
  {
    id: 'conversations',
    label: 'Inbox',
    singular: 'Conversation',
    icon: 'conversations',
    group: 'service',
    route: 'conversations',
    workspace: 'support',
    primary: 'subject',
    secondary: 'contactName',
    money: null,
    boardBy: 'status',
    lanes: Object.freeze(['new', 'open', 'waiting', 'closed']),
    fields: Object.freeze(['subject', 'contactName', 'accountName', 'channel', 'lastMessageAt', 'status']),
    personas: Object.freeze(['sdr', 'sales_representative', 'support_agent', 'customer_success']),
    serviceMethods: Object.freeze(['getConversations', 'createConversation', 'updateConversation', 'deleteConversation']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Summarize thread, sentiment, urgency and next response recommendation.',
    migrationPosture: Object.freeze(['INTERCOM', 'ZENDESK', 'FRESHDESK', 'HUBSPOT', 'GENERIC_CRM']),
    competitiveWedge: 'Omni-channel conversation command without losing tenant evidence.'
  },
  {
    id: 'customer_success',
    label: 'Success',
    singular: 'Success Record',
    icon: 'success',
    group: 'service',
    route: 'customer-success',
    workspace: 'success',
    primary: 'accountName',
    secondary: 'healthStatus',
    money: 'renewalValue',
    boardBy: 'healthStatus',
    lanes: Object.freeze(['healthy', 'watch', 'at_risk', 'churn_risk', 'expansion']),
    fields: Object.freeze(['accountName', 'healthScore', 'renewalDate', 'renewalValue', 'owner', 'healthStatus']),
    personas: Object.freeze(['customer_success', 'sales_manager', 'revenue_operations', 'founder_omega']),
    serviceMethods: Object.freeze(['getCustomerSuccess', 'createCustomerSuccess', 'updateCustomerSuccess', 'deleteCustomerSuccess']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Predict churn risk, renewal blockers and expansion routes.',
    migrationPosture: Object.freeze(['INTERCOM', 'HUBSPOT', 'SALESFORCE', 'GENERIC_CRM']),
    competitiveWedge: 'Customer success is revenue intelligence, not a static health score.'
  },
  {
    id: 'projects',
    label: 'Projects',
    singular: 'Project',
    icon: 'projects',
    group: 'work',
    route: 'projects',
    workspace: 'records',
    primary: 'name',
    secondary: 'accountName',
    money: null,
    boardBy: 'status',
    lanes: Object.freeze(['planned', 'active', 'at_risk', 'completed']),
    fields: Object.freeze(['name', 'accountName', 'owner', 'percentComplete', 'status']),
    personas: Object.freeze(['customer_success', 'account_executive', 'crm_operator', 'founder_omega']),
    serviceMethods: Object.freeze(['getProjects', 'createProject', 'updateProject', 'deleteProject']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.live,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Connect delivery risk to customer health and expansion posture.',
    migrationPosture: Object.freeze(['ZOHO', 'SALESFORCE', 'GENERIC_CRM']),
    competitiveWedge: 'Project delivery links directly to account retention and revenue risk.'
  },
  {
    id: 'quotes',
    label: 'Quotes',
    singular: 'Quote',
    icon: 'quotes',
    group: 'revenue',
    route: 'quotes',
    workspace: 'pipeline',
    primary: 'number',
    secondary: 'accountName',
    money: 'amount',
    boardBy: 'status',
    lanes: Object.freeze(['draft', 'sent', 'approved', 'rejected']),
    fields: Object.freeze(['number', 'accountName', 'amount', 'validUntil', 'status']),
    personas: Object.freeze(['account_executive', 'sales_manager', 'revenue_operations']),
    serviceMethods: Object.freeze(['getQuotes', 'createQuote', 'updateQuote', 'deleteQuote']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.live,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Surface quote risk, expiry, account context and approval posture.',
    migrationPosture: Object.freeze(['ZOHO', 'SALESFORCE', 'GENERIC_CRM']),
    competitiveWedge: 'Quotes are not isolated documents; they are part of CRM revenue truth.'
  },
  {
    id: 'invoices',
    label: 'Invoices',
    singular: 'Invoice',
    icon: 'invoices',
    group: 'revenue',
    route: 'invoices',
    workspace: 'pipeline',
    primary: 'number',
    secondary: 'accountName',
    money: 'amount',
    boardBy: 'status',
    lanes: Object.freeze(['draft', 'sent', 'paid', 'overdue']),
    fields: Object.freeze(['number', 'accountName', 'amount', 'dueDate', 'status']),
    personas: Object.freeze(['revenue_operations', 'sales_manager', 'founder_omega']),
    serviceMethods: Object.freeze(['getInvoices', 'createInvoice', 'updateInvoice', 'deleteInvoice']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.live,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Connect invoice status to account health and revenue risk.',
    migrationPosture: Object.freeze(['ZOHO', 'SALESFORCE', 'GENERIC_CRM']),
    competitiveWedge: 'Invoice posture feeds customer success and boardroom revenue controls.'
  },
  {
    id: 'contracts',
    label: 'Contracts',
    singular: 'Contract',
    icon: 'contracts',
    group: 'governance',
    route: 'contracts',
    workspace: 'evidence',
    primary: 'name',
    secondary: 'accountName',
    money: null,
    boardBy: 'contractStatus',
    lanes: Object.freeze(['drafting', 'approved', 'signed', 'active', 'expired']),
    fields: Object.freeze(['name', 'accountName', 'contractStatus', 'authorityStatus', 'effectiveDate']),
    personas: Object.freeze(['account_executive', 'customer_success', 'compliance_officer', 'founder_omega']),
    serviceMethods: Object.freeze(['getContracts', 'createContract', 'updateContract', 'deleteContract']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.live,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Expose contract gaps, authority status and renewal posture.',
    migrationPosture: Object.freeze(['SALESFORCE', 'ZOHO', 'GENERIC_CRM']),
    competitiveWedge: 'Contracts sit inside CRM proof posture, not outside the customer record.'
  },
  {
    id: 'authorities',
    label: 'Authority',
    singular: 'Authority',
    icon: 'authorities',
    group: 'governance',
    route: 'authorities',
    workspace: 'evidence',
    primary: 'contactName',
    secondary: 'accountName',
    money: null,
    boardBy: 'authorityStatus',
    lanes: Object.freeze(['missing', 'pending', 'validated', 'verified']),
    fields: Object.freeze(['contactName', 'accountName', 'authorityStatus', 'evidenceType', 'verifiedAt']),
    personas: Object.freeze(['compliance_officer', 'account_executive', 'customer_success', 'founder_omega']),
    serviceMethods: Object.freeze(['getAuthorities', 'createAuthority', 'updateAuthority', 'deleteAuthority']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.live,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Find missing authority, stale mandate and evidence gaps.',
    migrationPosture: Object.freeze(['SALESFORCE', 'ZOHO', 'GENERIC_CRM']),
    competitiveWedge: 'Authority verification is native to CRM, not hidden in compliance back office.'
  },
  {
    id: 'risks',
    label: 'Risks',
    singular: 'Risk',
    icon: 'risks',
    group: 'governance',
    route: 'risks',
    workspace: 'evidence',
    primary: 'title',
    secondary: 'accountName',
    money: null,
    boardBy: 'severity',
    lanes: Object.freeze(['low', 'medium', 'high', 'critical', 'mitigated']),
    fields: Object.freeze(['title', 'accountName', 'severity', 'owner', 'status']),
    personas: Object.freeze(['sales_manager', 'customer_success', 'compliance_officer', 'founder_omega']),
    serviceMethods: Object.freeze(['getRisks', 'createRisk', 'updateRisk', 'deleteRisk']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.live,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Classify deal, account, compliance and retention risk.',
    migrationPosture: Object.freeze(['GENERIC_CRM']),
    competitiveWedge: 'CRM risk is operational, revenue and compliance risk together.'
  },
  {
    id: 'opportunities',
    label: 'Opportunities',
    singular: 'Opportunity',
    icon: 'opportunities',
    group: 'revenue',
    route: 'opportunities',
    workspace: 'pipeline',
    primary: 'name',
    secondary: 'accountName',
    money: 'value',
    boardBy: 'stage',
    lanes: Object.freeze(['identified', 'qualified', 'proposal', 'won']),
    fields: Object.freeze(['name', 'accountName', 'value', 'probability', 'stage']),
    personas: Object.freeze(['account_executive', 'sales_manager', 'revenue_operations', 'founder_omega']),
    serviceMethods: Object.freeze(['getOpportunities', 'createOpportunity', 'updateOpportunity', 'deleteOpportunity']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.live,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Separate opportunity from active deal and route strategic growth.',
    migrationPosture: Object.freeze(['SALESFORCE', 'ZOHO', 'HUBSPOT', 'GENERIC_CRM']),
    competitiveWedge: 'Opportunity intelligence supports expansion before deal creation.'
  },
  {
    id: 'forecast',
    label: 'Forecast',
    singular: 'Forecast',
    icon: 'forecast',
    group: 'revenue',
    route: 'forecast',
    workspace: 'intelligence',
    primary: 'period',
    secondary: 'confidence',
    money: 'forecastValue',
    boardBy: 'confidence',
    lanes: Object.freeze(['low_confidence', 'committed', 'best_case', 'board_review']),
    fields: Object.freeze(['period', 'forecastValue', 'pipelineValue', 'confidence', 'owner', 'status']),
    personas: Object.freeze(['sales_manager', 'sales_leader', 'revenue_operations', 'founder_omega']),
    serviceMethods: Object.freeze(['getForecasts', 'createForecast', 'updateForecast', 'deleteForecast']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Generate evidence-aware forecast posture from deals, activities and source freshness.',
    migrationPosture: Object.freeze(['SALESFORCE', 'HUBSPOT', 'ZOHO', 'GENERIC_CRM']),
    competitiveWedge: 'Forecasts show confidence, evidence and route gaps, not optimistic guesses.'
  },
  {
    id: 'campaigns',
    label: 'Campaigns',
    singular: 'Campaign',
    icon: 'campaigns',
    group: 'acquisition',
    route: 'campaigns',
    workspace: 'records',
    primary: 'name',
    secondary: 'channel',
    money: 'budget',
    boardBy: 'status',
    lanes: Object.freeze(['draft', 'active', 'paused', 'completed']),
    fields: Object.freeze(['name', 'channel', 'budget', 'leadsGenerated', 'conversionRate', 'status']),
    personas: Object.freeze(['sdr', 'sales_manager', 'revenue_operations']),
    serviceMethods: Object.freeze(['getCampaigns', 'createCampaign', 'updateCampaign', 'deleteCampaign']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Tie campaigns to lead quality, source reliability and conversion evidence.',
    migrationPosture: Object.freeze(['HUBSPOT', 'ZOHO', 'SALESFORCE', 'GENERIC_CRM']),
    competitiveWedge: 'Campaigns are measured by governed revenue posture, not vanity metrics.'
  },
  {
    id: 'workflows',
    label: 'Workflows',
    singular: 'Workflow',
    icon: 'workflows',
    group: 'automation',
    route: 'workflows',
    workspace: 'automation',
    primary: 'name',
    secondary: 'trigger',
    money: null,
    boardBy: 'status',
    lanes: Object.freeze(['draft', 'active', 'paused', 'failed']),
    fields: Object.freeze(['name', 'trigger', 'targetModule', 'lastRunAt', 'owner', 'status']),
    personas: Object.freeze(['sales_manager', 'revenue_operations', 'tenant_admin', 'founder_omega']),
    serviceMethods: Object.freeze(['getWorkflows', 'createWorkflow', 'updateWorkflow', 'deleteWorkflow']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Recommend workflows based on source gaps, overdue tasks and lifecycle posture.',
    migrationPosture: Object.freeze(['HUBSPOT', 'ZOHO', 'SALESFORCE', 'GENERIC_CRM']),
    competitiveWedge: 'Automation is evidence-aware and tenant-safe by design.'
  },
  {
    id: 'connectors',
    label: 'Connectors',
    singular: 'Connector',
    icon: 'connectors',
    group: 'automation',
    route: 'connectors',
    workspace: 'evidence',
    primary: 'name',
    secondary: 'vendor',
    money: null,
    boardBy: 'status',
    lanes: Object.freeze(['missing', 'configured', 'degraded', 'live']),
    fields: Object.freeze(['name', 'vendor', 'lastSyncAt', 'recordsSynced', 'sourceStatus', 'status']),
    personas: Object.freeze(['tenant_admin', 'revenue_operations', 'compliance_officer', 'founder_omega']),
    serviceMethods: Object.freeze(['getConnectors', 'createConnector', 'updateConnector', 'deleteConnector']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Detect stale integrations, source mismatch and migration readiness.',
    migrationPosture: Object.freeze(['HUBSPOT', 'ZOHO', 'ZENDESK', 'SALESFORCE', 'FRESHDESK', 'INTERCOM', 'GENERIC_CRM']),
    competitiveWedge: 'Connector status is first-class CRM evidence.'
  },
  {
    id: 'audit',
    label: 'Audit',
    singular: 'Audit Event',
    icon: 'audit',
    group: 'governance',
    route: 'audit',
    workspace: 'evidence',
    primary: 'action',
    secondary: 'moduleId',
    money: null,
    boardBy: 'status',
    lanes: Object.freeze(['recorded', 'sealed', 'failed', 'review']),
    fields: Object.freeze(['action', 'moduleId', 'receiptId', 'operatorId', 'createdAt', 'status']),
    personas: Object.freeze(['compliance_officer', 'tenant_admin', 'founder_omega']),
    serviceMethods: Object.freeze(['getAuditEvents', 'createAuditEvent', 'updateAuditEvent', 'deleteAuditEvent']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Summarize CRM audit posture and route unsealed material actions.',
    migrationPosture: Object.freeze(['GENERIC_CRM']),
    competitiveWedge: 'Audit is not an afterthought; it is part of the CRM operating model.'
  },
  {
    id: 'suppliers',
    label: 'Suppliers',
    singular: 'Supplier',
    icon: 'suppliers',
    group: 'relationship',
    route: 'suppliers',
    workspace: 'records',
    primary: 'name',
    secondary: 'category',
    money: null,
    boardBy: 'status',
    lanes: Object.freeze(['prospect', 'approved', 'active', 'blocked']),
    fields: Object.freeze(['name', 'category', 'contactName', 'contractStatus', 'status']),
    personas: Object.freeze(['crm_operator', 'tenant_admin', 'founder_omega']),
    serviceMethods: Object.freeze(['getSuppliers', 'createSupplier', 'updateSupplier', 'deleteSupplier']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.live,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Expose supplier readiness, contract posture and account dependency.',
    migrationPosture: Object.freeze(['ZOHO', 'GENERIC_CRM']),
    competitiveWedge: 'CRM can model business relationships beyond customers.'
  },
  {
    id: 'partners',
    label: 'Partners',
    singular: 'Partner',
    icon: 'partners',
    group: 'relationship',
    route: 'partners',
    workspace: 'records',
    primary: 'name',
    secondary: 'category',
    money: null,
    boardBy: 'status',
    lanes: Object.freeze(['prospect', 'active', 'strategic', 'inactive']),
    fields: Object.freeze(['name', 'category', 'contactName', 'contractStatus', 'status']),
    personas: Object.freeze(['account_executive', 'sales_manager', 'tenant_admin', 'founder_omega']),
    serviceMethods: Object.freeze(['getPartners', 'createPartner', 'updatePartner', 'deletePartner']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.live,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Identify strategic partner leverage, gaps and customer impact.',
    migrationPosture: Object.freeze(['ZOHO', 'SALESFORCE', 'GENERIC_CRM']),
    competitiveWedge: 'Partner networks become part of the revenue command graph.'
  },
  {
    id: 'calls',
    label: 'Calls',
    singular: 'Call',
    icon: 'messageSquare',
    group: 'work',
    route: 'calls',
    workspace: 'records',
    primary: 'subject',
    secondary: 'contactName',
    money: null,
    boardBy: 'outcome',
    lanes: Object.freeze(['scheduled', 'completed', 'missed', 'follow_up']),
    fields: Object.freeze(['subject', 'phone', 'contactName', 'outcome', 'completedAt', 'owner', 'status']),
    personas: Object.freeze(['sdr', 'sales_representative', 'account_executive', 'customer_success']),
    serviceMethods: Object.freeze(['getCalls', 'createCall', 'updateCall', 'deleteCall']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    sourceContract: baseSourceContract,
    receiptContract: baseReceiptContract,
    tenantContract: baseTenantContract,
    aiCommand: 'Summarize call outcome, next action, sentiment and pipeline impact.',
    migrationPosture: Object.freeze(['HUBSPOT', 'ZOHO', 'SALESFORCE', 'INTERCOM', 'GENERIC_CRM']),
    competitiveWedge: 'Calls become traceable customer evidence, not forgotten activity notes.'
  },
  {
    id: 'lead_intelligence',
    label: 'Lead Intelligence',
    singular: 'Lead Intelligence Packet',
    icon: 'sparkles',
    group: 'intelligence',
    route: 'lead-intelligence',
    workspace: 'intelligence',
    primary: 'leadName',
    secondary: 'qualificationPosture',
    money: 'estimatedValue',
    boardBy: 'qualificationPosture',
    lanes: Object.freeze(['unqualified', 'bant_gap', 'qualified', 'sales_ready', 'board_review']),
    fields: Object.freeze(['leadName', 'company', 'score', 'qualificationPosture', 'budget', 'authority', 'need', 'timeline', 'winProbability', 'nextBestAction']),
    personas: Object.freeze(['sdr', 'sales_representative', 'account_executive', 'sales_manager', 'founder_omega']),
    serviceMethods: Object.freeze(['getLeadIntelligence', 'createLeadIntelligence', 'updateLeadIntelligence', 'deleteLeadIntelligence']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    sourceContract: Object.freeze({ ...baseSourceContract, minimumStatus: WILSY_CRM_SOURCE_STATUS.sourceRequired, framework: WILSY_CRM_QUALIFICATION_FRAMEWORKS.bant }),
    receiptContract: Object.freeze({ ...baseReceiptContract, score: 'CRM_LEAD_SCORE_RECEIPT_REQUIRED', qualification: 'CRM_BANT_QUALIFICATION_RECEIPT_REQUIRED' }),
    tenantContract: baseTenantContract,
    aiCommand: 'Score lead quality, expose BANT gaps, predict win probability and recommend next action from source-backed signals.',
    migrationPosture: Object.freeze(['HUBSPOT', 'ZOHO', 'SALESFORCE', 'LINKEDIN_EXPORT', 'GENERIC_CRM']),
    competitiveWedge: 'HubSpot scores leads; Wilsy proves why the score exists and receipts every qualification movement.',
    qualificationFrameworks: WILSY_CRM_QUALIFICATION_FRAMEWORKS,
    forensicFlow: Object.freeze([WILSY_CRM_FORENSIC_FLOW_CATALOG.leadEntered, WILSY_CRM_FORENSIC_FLOW_CATALOG.qualificationUpdated])
  },
  {
    id: 'pipeline_cockpit',
    label: 'Pipeline Cockpit',
    singular: 'Pipeline Cockpit',
    icon: 'target',
    group: 'revenue',
    route: 'pipeline-cockpit',
    workspace: 'pipeline',
    primary: 'period',
    secondary: 'pipelinePosture',
    money: 'weightedPipeline',
    boardBy: 'pipelinePosture',
    lanes: Object.freeze(['source_required', 'building', 'forecastable', 'at_risk', 'board_ready']),
    fields: Object.freeze(['period', 'leadCount', 'accountCount', 'dealCount', 'weightedPipeline', 'churnRisk', 'forecastConfidence', 'pipelinePosture']),
    personas: Object.freeze(['sales_manager', 'sales_leader', 'revenue_operations', 'founder_omega']),
    serviceMethods: Object.freeze(['getPipelineCockpit', 'createPipelineSnapshot', 'updatePipelineSnapshot', 'deletePipelineSnapshot']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    sourceContract: baseSourceContract,
    receiptContract: Object.freeze({ ...baseReceiptContract, stageMove: 'CRM_PIPELINE_STAGE_MOVE_RECEIPT_REQUIRED', forecast: 'CRM_FORECAST_RECEIPT_REQUIRED' }),
    tenantContract: baseTenantContract,
    aiCommand: 'Collapse leads, accounts, deals, churn and expansion into one weighted revenue cockpit.',
    migrationPosture: Object.freeze(['HUBSPOT', 'ZOHO', 'SALESFORCE', 'GENERIC_CRM']),
    competitiveWedge: 'Competitors show scattered panels; Wilsy shows weighted revenue inevitability with evidence.',
    forensicFlow: Object.freeze([WILSY_CRM_FORENSIC_FLOW_CATALOG.pipelineMoved])
  },
  {
    id: 'customer_success_telemetry',
    label: 'Success Telemetry',
    singular: 'Success Telemetry Packet',
    icon: 'success',
    group: 'service',
    route: 'customer-success-telemetry',
    workspace: 'success',
    primary: 'accountName',
    secondary: 'healthPosture',
    money: 'expansionRevenue',
    boardBy: 'healthPosture',
    lanes: Object.freeze(['source_required', 'healthy', 'expansion', 'adoption_risk', 'churn_risk']),
    fields: Object.freeze(['accountName', 'adoptionScore', 'sessionCount', 'employeeOwner', 'expansionRevenue', 'renewalDate', 'churnRisk', 'healthPosture']),
    personas: Object.freeze(['customer_success', 'sales_manager', 'revenue_operations', 'founder_omega']),
    serviceMethods: Object.freeze(['getCustomerSuccessTelemetry', 'createCustomerSuccessTelemetry', 'updateCustomerSuccessTelemetry', 'deleteCustomerSuccessTelemetry']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    sourceContract: Object.freeze({ ...baseSourceContract, connectors: Object.freeze(['hr', 'product', 'support', 'billing']) }),
    receiptContract: Object.freeze({ ...baseReceiptContract, healthChange: 'CRM_CUSTOMER_HEALTH_RECEIPT_REQUIRED', churnRisk: 'CRM_CHURN_RISK_RECEIPT_REQUIRED' }),
    tenantContract: baseTenantContract,
    aiCommand: 'Tie adoption, expansion, churn, tickets and employee performance into one success telemetry view.',
    migrationPosture: Object.freeze(['INTERCOM', 'ZENDESK', 'FRESHDESK', 'HUBSPOT', 'SALESFORCE', 'GENERIC_CRM']),
    competitiveWedge: 'Customer Success becomes measurable revenue telemetry, not a colour-coded health badge.',
    connectorContract: Object.freeze([WILSY_CRM_CONNECTOR_CONTRACTS.hr, WILSY_CRM_CONNECTOR_CONTRACTS.finance])
  },
  {
    id: 'revenue_desk',
    label: 'Revenue Desk',
    singular: 'Revenue Desk Entry',
    icon: 'invoices',
    group: 'financeEvidence',
    route: 'revenue-desk',
    workspace: 'pipeline',
    primary: 'contractNumber',
    secondary: 'revenuePosture',
    money: 'recognizedRevenue',
    boardBy: 'revenuePosture',
    lanes: Object.freeze(['contract_pending', 'invoice_issued', 'receipt_sealed', 'ifrs_review', 'board_ready']),
    fields: Object.freeze(['contractNumber', 'accountName', 'contractValue', 'invoiceNumber', 'recognizedRevenue', 'receiptId', 'ifrsClause', 'revenuePosture']),
    personas: Object.freeze(['revenue_operations', 'sales_manager', 'sales_leader', 'compliance_officer', 'founder_omega']),
    serviceMethods: Object.freeze(['getRevenueDesk', 'createRevenueDeskEntry', 'updateRevenueDeskEntry', 'deleteRevenueDeskEntry']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    sourceContract: Object.freeze({ ...baseSourceContract, minimumStatus: WILSY_CRM_SOURCE_STATUS.sourceRequired, clauses: WILSY_CRM_COMPLIANCE_CLAUSE_CATALOG.ifrs }),
    receiptContract: Object.freeze({ ...baseReceiptContract, ledger: 'CRM_IFRS_LEDGER_RECEIPT_REQUIRED', invoice: 'CRM_INVOICE_RECEIPT_REQUIRED', contract: 'CRM_CONTRACT_REVENUE_RECEIPT_REQUIRED' }),
    tenantContract: baseTenantContract,
    aiCommand: 'Connect contracts signed, invoices issued, receipts sealed and IFRS posture into one revenue command desk.',
    migrationPosture: Object.freeze(['SALESFORCE', 'ZOHO', 'HUBSPOT', 'XERO', 'QUICKBOOKS', 'SAGE', 'GENERIC_CRM']),
    competitiveWedge: 'Salesforce can forecast; Wilsy ties revenue to contracts, invoices, receipts and IFRS posture.',
    connectorContract: Object.freeze([WILSY_CRM_CONNECTOR_CONTRACTS.finance]),
    complianceClauses: WILSY_CRM_COMPLIANCE_CLAUSE_CATALOG.ifrs,
    forensicFlow: Object.freeze([WILSY_CRM_FORENSIC_FLOW_CATALOG.dealClosed, WILSY_CRM_FORENSIC_FLOW_CATALOG.invoiceIssued])
  },
  {
    id: 'compliance_hud',
    label: 'Compliance HUD',
    singular: 'Compliance HUD Entry',
    icon: 'shield',
    group: 'complianceHud',
    route: 'compliance-hud',
    workspace: 'evidence',
    primary: 'customerName',
    secondary: 'clausePosture',
    money: null,
    boardBy: 'clausePosture',
    lanes: Object.freeze(['source_required', 'clause_gap', 'consent_gap', 'receipt_gap', 'regulator_ready']),
    fields: Object.freeze(['customerName', 'moduleId', 'popiaClause', 'gdprClause', 'soc2Clause', 'authorityStatus', 'receiptId', 'clausePosture']),
    personas: Object.freeze(['compliance_officer', 'customer_success', 'sales_manager', 'tenant_admin', 'founder_omega']),
    serviceMethods: Object.freeze(['getComplianceHud', 'createComplianceHudEntry', 'updateComplianceHudEntry', 'deleteComplianceHudEntry']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    sourceContract: Object.freeze({ ...baseSourceContract, clauses: WILSY_CRM_COMPLIANCE_CLAUSE_CATALOG }),
    receiptContract: Object.freeze({ ...baseReceiptContract, clauseBinding: 'CRM_COMPLIANCE_CLAUSE_BINDING_RECEIPT_REQUIRED' }),
    tenantContract: baseTenantContract,
    aiCommand: 'Bind POPIA, GDPR, SOC2 and authority posture to customer, deal, support and revenue events.',
    migrationPosture: Object.freeze(['SALESFORCE', 'ZENDESK', 'HUBSPOT', 'GENERIC_CRM']),
    competitiveWedge: 'Competitors store notes; Wilsy binds customer movement to compliance clauses and receipts.',
    complianceClauses: WILSY_CRM_COMPLIANCE_CLAUSE_CATALOG
  },
  {
    id: 'forensic_sales_flow',
    label: 'Forensic Flow',
    singular: 'Forensic Sales Event',
    icon: 'audit',
    group: 'forensicFlow',
    route: 'forensic-sales-flow',
    workspace: 'evidence',
    primary: 'eventType',
    secondary: 'chainOfCustodyPosture',
    money: 'eventValue',
    boardBy: 'chainOfCustodyPosture',
    lanes: Object.freeze(['captured', 'receipt_pending', 'sealed', 'sovereign_anchored', 'review_required']),
    fields: Object.freeze(['eventType', 'leadId', 'dealId', 'contractId', 'operatorId', 'timestamp', 'receiptId', 'sovereignRootHash', 'chainOfCustodyPosture']),
    personas: Object.freeze(['sales_manager', 'compliance_officer', 'revenue_operations', 'founder_omega']),
    serviceMethods: Object.freeze(['getForensicSalesFlow', 'createForensicSalesEvent', 'updateForensicSalesEvent', 'deleteForensicSalesEvent']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    sourceContract: Object.freeze({ ...baseSourceContract, forensicFlow: WILSY_CRM_FORENSIC_FLOW_CATALOG }),
    receiptContract: Object.freeze({ ...baseReceiptContract, chain: 'CRM_CHAIN_OF_CUSTODY_RECEIPT_REQUIRED', root: 'CRM_SOVEREIGN_ROOT_ANCHOR_REQUIRED' }),
    tenantContract: baseTenantContract,
    aiCommand: 'Explain the full chain of custody from lead entry to contract, invoice, receipt and regulator disclosure.',
    migrationPosture: Object.freeze(['GENERIC_CRM']),
    competitiveWedge: 'No competitor turns sales operations into regulator-ready forensic evidence.',
    forensicFlow: WILSY_CRM_FORENSIC_FLOW_CATALOG
  },
  {
    id: 'connector_command',
    label: 'Connector Command',
    singular: 'Connector Command',
    icon: 'connectors',
    group: 'automation',
    route: 'connector-command',
    workspace: 'evidence',
    primary: 'connectorName',
    secondary: 'connectorPosture',
    money: null,
    boardBy: 'connectorPosture',
    lanes: Object.freeze(['missing', 'configured', 'syncing', 'degraded', 'live']),
    fields: Object.freeze(['connectorName', 'vendor', 'lastSyncAt', 'recordsSynced', 'evidenceFields', 'sourceStatus', 'connectorPosture']),
    personas: Object.freeze(['tenant_admin', 'revenue_operations', 'compliance_officer', 'founder_omega']),
    serviceMethods: Object.freeze(['getConnectorCommand', 'createConnectorCommand', 'updateConnectorCommand', 'deleteConnectorCommand']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    sourceContract: Object.freeze({ ...baseSourceContract, connectorContract: WILSY_CRM_CONNECTOR_CONTRACTS }),
    receiptContract: Object.freeze({ ...baseReceiptContract, sync: 'CRM_CONNECTOR_SYNC_RECEIPT_REQUIRED' }),
    tenantContract: baseTenantContract,
    aiCommand: 'Expose Gmail, Outlook, LinkedIn, finance, HR and support connector readiness without fake sync claims.',
    migrationPosture: Object.freeze(['GMAIL', 'OUTLOOK', 'LINKEDIN_EXPORT', 'HUBSPOT', 'ZOHO', 'ZENDESK', 'SALESFORCE', 'GENERIC_CRM']),
    competitiveWedge: 'Connectors are source evidence rails, not checkbox integrations.',
    connectorContract: WILSY_CRM_CONNECTOR_CONTRACTS
  },
  {
    id: 'investor_strip',
    label: 'Investor Strip',
    singular: 'Investor Telemetry Strip',
    icon: 'forecast',
    group: 'investor',
    route: 'investor-strip',
    workspace: 'intelligence',
    primary: 'sovereignRootHash',
    secondary: 'investorPosture',
    money: 'liveRevenueMovement',
    boardBy: 'investorPosture',
    lanes: Object.freeze(['source_required', 'telemetry_live', 'receipts_sealed', 'board_ready', 'investor_review']),
    fields: Object.freeze(['sovereignRootHash', 'sealedReceipts', 'liveRevenueMovement', 'pipelineMovement', 'complianceReadiness', 'disclosureBundleReadiness', 'investorPosture']),
    personas: Object.freeze(['founder_omega', 'sales_leader', 'revenue_operations', 'compliance_officer']),
    serviceMethods: Object.freeze(['getInvestorStrip', 'createInvestorTelemetrySnapshot', 'updateInvestorTelemetrySnapshot', 'deleteInvestorTelemetrySnapshot']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    sourceContract: Object.freeze({ ...baseSourceContract, telemetryContract: WILSY_CRM_INVESTOR_TELEMETRY_CONTRACT }),
    receiptContract: Object.freeze({ ...baseReceiptContract, investorSnapshot: 'CRM_INVESTOR_TELEMETRY_RECEIPT_REQUIRED' }),
    tenantContract: baseTenantContract,
    aiCommand: 'Show sovereign root hash, sealed receipts, revenue movement and compliance readiness with no fake investor metrics.',
    migrationPosture: Object.freeze(['GENERIC_CRM']),
    competitiveWedge: 'Investors see tamper-proof commercial telemetry instead of a decorative SaaS dashboard.',
    investorTelemetry: WILSY_CRM_INVESTOR_TELEMETRY_CONTRACT,
    forensicFlow: Object.freeze([WILSY_CRM_FORENSIC_FLOW_CATALOG.sovereignRootAnchored])
  },
  {
    id: 'governance_ledger',
    label: 'Governance Ledger',
    singular: 'Governance Ledger Entry',
    icon: 'evidence',
    group: 'governance',
    route: 'governance-ledger',
    workspace: 'evidence',
    primary: 'governanceEvent',
    secondary: 'custodyPosture',
    money: null,
    boardBy: 'custodyPosture',
    lanes: Object.freeze(['captured', 'custody_pending', 'verified', 'sealed', 'review_required']),
    fields: Object.freeze(['governanceEvent', 'moduleId', 'recordId', 'operatorId', 'sourceSystem', 'receiptId', 'custodyPosture']),
    personas: Object.freeze(['compliance_officer', 'tenant_admin', 'revenue_operations', 'founder_omega']),
    serviceMethods: Object.freeze(['getGovernanceLedger', 'createGovernanceLedgerEntry', 'updateGovernanceLedgerEntry', 'deleteGovernanceLedgerEntry']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    sourceContract: Object.freeze({ ...baseSourceContract, backendServiceContracts: WILSY_CRM_BACKEND_SERVICE_CONTRACTS }),
    receiptContract: Object.freeze({ ...baseReceiptContract, governance: 'CRM_GOVERNANCE_LEDGER_RECEIPT_REQUIRED' }),
    tenantContract: baseTenantContract,
    aiCommand: 'Map CRM actions to governance events, custody posture and evidence ledger readiness.',
    migrationPosture: Object.freeze(['GENERIC_CRM']),
    competitiveWedge: 'Wilsy makes CRM governance native, not a compliance afterthought.',
    backendServiceContracts: WILSY_CRM_BACKEND_SERVICE_CONTRACTS
  },
  {
    id: 'evidence_exports',
    label: 'Evidence Exports',
    singular: 'Evidence Export',
    icon: 'upload',
    group: 'forensicFlow',
    route: 'evidence-exports',
    workspace: 'evidence',
    primary: 'bundleName',
    secondary: 'disclosurePosture',
    money: null,
    boardBy: 'disclosurePosture',
    lanes: Object.freeze(['source_required', 'assembling', 'sealed', 'exported', 'regulator_ready']),
    fields: Object.freeze(['bundleName', 'customerName', 'clauseCount', 'receiptCount', 'zipHash', 'exportedAt', 'disclosurePosture']),
    personas: Object.freeze(['compliance_officer', 'tenant_admin', 'founder_omega']),
    serviceMethods: Object.freeze(['getEvidenceExports', 'createEvidenceExport', 'updateEvidenceExport', 'deleteEvidenceExport']),
    routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
    sourceContract: Object.freeze({ ...baseSourceContract, exportApi: WILSY_CRM_BACKEND_SERVICE_CONTRACTS.exportApi }),
    receiptContract: Object.freeze({ ...baseReceiptContract, disclosure: 'CRM_DISCLOSURE_EXPORT_RECEIPT_REQUIRED' }),
    tenantContract: baseTenantContract,
    aiCommand: 'Prepare one-click regulator disclosure packages with customer records, clauses, receipts and sovereign hashes.',
    migrationPosture: Object.freeze(['GENERIC_CRM']),
    competitiveWedge: 'Regulator-ready exports make competitor CRMs look ungoverned.',
    forensicFlow: Object.freeze([WILSY_CRM_FORENSIC_FLOW_CATALOG.disclosureExported])
  }
]);

export const WILSY_CRM_MODULE_IDS = Object.freeze(WILSY_CRM_MODULE_CATALOG.map(moduleConfig => moduleConfig.id));

export const WILSY_CRM_MODULE_GROUP_SUMMARY = Object.freeze(
  Object.keys(WILSY_CRM_MODULE_GROUPS).reduce((summary, groupId) => ({
    ...summary,
    [groupId]: WILSY_CRM_MODULE_CATALOG.filter(moduleConfig => moduleConfig.group === groupId).length
  }), {})
);

/**
 * @function normalizeWilsyCrmCatalogKey
 * @description Normalizes role, module, vendor and workspace keys for CRM catalog lookup.
 * @param {string} value - Candidate lookup value.
 * @returns {string} Normalized catalog key.
 * @collaboration Lets Discovery UI, dashboards and future backend command routes share one CRM lookup language.
 */
export const normalizeWilsyCrmCatalogKey = value => String(value || '')
  .trim()
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, '_')
  .replace(/^_+|_+$/g, '');

/**
 * @function getWilsyCrmModuleById
 * @description Retrieves a CRM module contract by id.
 * @param {string} moduleId - CRM module id.
 * @param {string} fallbackId - Fallback module id.
 * @returns {Object} CRM module contract.
 * @collaboration Keeps CRMDashboard, services and future backend route contracts aligned on one module source of truth.
 */
export const getWilsyCrmModuleById = (moduleId, fallbackId = WILSY_CRM_DEFAULT_MODULE_ID) => {
  const normalizedId = normalizeWilsyCrmCatalogKey(moduleId);
  const directMatch = WILSY_CRM_MODULE_CATALOG.find(moduleConfig => moduleConfig.id === normalizedId);
  if (directMatch) return directMatch;

  return WILSY_CRM_MODULE_CATALOG.find(moduleConfig => moduleConfig.id === fallbackId) || WILSY_CRM_MODULE_CATALOG[0];
};

/**
 * @function listWilsyCrmModulesByGroup
 * @description Lists CRM modules assigned to a governed CRM module group.
 * @param {string} groupId - CRM module group id.
 * @returns {Array<Object>} Matching CRM modules.
 * @collaboration Lets the CRM shell render acquisition, revenue, service, governance and automation rails without duplicate arrays.
 */
export const listWilsyCrmModulesByGroup = groupId => {
  const normalizedGroup = normalizeWilsyCrmCatalogKey(groupId);
  return WILSY_CRM_MODULE_CATALOG.filter(moduleConfig => moduleConfig.group === normalizedGroup);
};

/**
 * @function listWilsyCrmModulesByPersona
 * @description Lists CRM modules available for a role/persona.
 * @param {string} persona - CRM persona or application role.
 * @returns {Array<Object>} Matching CRM modules.
 * @collaboration Keeps Sales, CRM, Customer Success, SDR and Founder/Omega entry points aligned without data leakage.
 */
export const listWilsyCrmModulesByPersona = persona => {
  const normalizedPersona = normalizeWilsyCrmCatalogKey(persona);
  const mappedPersona = WILSY_CRM_PERSONAS[normalizedPersona] || normalizedPersona;

  return WILSY_CRM_MODULE_CATALOG.filter(moduleConfig => (
    moduleConfig.personas || []
  ).some(candidate => normalizeWilsyCrmCatalogKey(candidate) === normalizeWilsyCrmCatalogKey(mappedPersona)));
};

/**
 * @function listWilsyCrmRoleEntryModules
 * @description Resolves the CRM module set for a Discovery UI role.
 * @param {string} role - User role from discovery/auth context.
 * @returns {Array<Object>} Role-appropriate CRM modules.
 * @collaboration Directs Sales, CRM, SDR and Customer Success employees into the same CRM OS while preserving tenant boundaries.
 */
export const listWilsyCrmRoleEntryModules = role => {
  const normalizedRole = normalizeWilsyCrmCatalogKey(role);
  const entry = WILSY_CRM_DISCOVERY_ROLE_MAP[normalizedRole];

  if (entry === 'founder_override_to_crm_os' || entry === 'sovereign_override_to_crm_os' || entry === 'omega_override_to_crm_os') {
    return listWilsyCrmModulesByPersona('founder_omega');
  }

  if (entry === 'crm_os') {
    return listWilsyCrmModulesByPersona(normalizedRole);
  }

  return WILSY_CRM_MODULE_CATALOG;
};

/**
 * @function buildWilsyCrmRouteContract
 * @description Builds the route contract for a CRM module and action.
 * @param {string} moduleId - CRM module id.
 * @param {string} action - CRUD or command action.
 * @returns {Object} Route contract.
 * @collaboration Makes missing backend routes visible as posture rather than silently pretending CRM is live.
 */
export const buildWilsyCrmRouteContract = (moduleId, action = 'list') => {
  const moduleConfig = getWilsyCrmModuleById(moduleId);
  const safeAction = normalizeWilsyCrmCatalogKey(action || 'list');

  return Object.freeze({
    moduleId: moduleConfig.id,
    action: safeAction,
    route: `/api/crm/${moduleConfig.route}`,
    tenantHeader: WILSY_CRM_TENANT_BOUNDARY.browserHeader,
    posture: moduleConfig.routePosture || WILSY_CRM_ROUTE_POSTURE.required,
    requiredSourceStatus: moduleConfig.sourceContract?.minimumStatus || WILSY_CRM_SOURCE_STATUS.sourceRequired,
    receiptRequired: ['create', 'update', 'delete', 'import', 'export'].includes(safeAction),
    noFakeData: true
  });
};

/**
 * @function buildWilsyCrmModuleEnvelope
 * @description Builds a source-safe module envelope for UI and service contracts.
 * @param {string} moduleId - CRM module id.
 * @param {Object} options - Envelope options.
 * @returns {Object} Source-safe CRM module envelope.
 * @collaboration Gives the CRM dashboard a deterministic no-fake-data module packet before backend routes are wired.
 */
export const buildWilsyCrmModuleEnvelope = (moduleId, options = {}) => {
  const moduleConfig = getWilsyCrmModuleById(moduleId);
  const sourceStatus = options.sourceStatus || moduleConfig.sourceContract?.minimumStatus || WILSY_CRM_SOURCE_STATUS.sourceRequired;

  return Object.freeze({
    module: moduleConfig,
    tenant: Object.freeze({
      tenantId: options.tenantId || 'TENANT_SOURCE_REQUIRED',
      boundary: moduleConfig.tenantContract || baseTenantContract
    }),
    source: Object.freeze({
      status: sourceStatus,
      sourceSystem: options.sourceSystem || 'SOURCE_REQUIRED',
      route: buildWilsyCrmRouteContract(moduleConfig.id, options.action || 'list'),
      noFakeData: true
    }),
    receipt: Object.freeze({
      required: true,
      contract: moduleConfig.receiptContract || baseReceiptContract,
      latestReceiptId: options.latestReceiptId || null
    }),
    command: Object.freeze({
      aiCommand: moduleConfig.aiCommand,
      competitiveWedge: moduleConfig.competitiveWedge,
      migrationPosture: moduleConfig.migrationPosture
    })
  });
};

/**
 * @function validateWilsyCrmModule
 * @description Validates one CRM module contract against the Wilsy OS CRM quality gate.
 * @param {Object} moduleConfig - CRM module contract.
 * @returns {Array<string>} Validation issues.
 * @collaboration Prevents skeletal CRM modules from entering the governed Sales/CRM operating system.
 */
export const validateWilsyCrmModule = moduleConfig => {
  const issues = [];
  const requiredFields = [
    'id',
    'label',
    'singular',
    'icon',
    'group',
    'route',
    'workspace',
    'primary',
    'secondary',
    'boardBy',
    'lanes',
    'fields',
    'personas',
    'serviceMethods',
    'routePosture',
    'sourceContract',
    'receiptContract',
    'tenantContract',
    'aiCommand',
    'migrationPosture',
    'competitiveWedge'
  ];

  requiredFields.forEach(field => {
    if (moduleConfig?.[field] === undefined || moduleConfig?.[field] === null || moduleConfig?.[field] === '') {
      issues.push(`${moduleConfig?.id || 'UNKNOWN_MODULE'} missing field ${field}`);
    }
  });

  if (!Array.isArray(moduleConfig?.lanes) && !Object.isFrozen(moduleConfig?.lanes)) {
    issues.push(`${moduleConfig?.id || 'UNKNOWN_MODULE'} lanes must be an immutable array contract`);
  }

  if (!Array.isArray(moduleConfig?.fields) && !Object.isFrozen(moduleConfig?.fields)) {
    issues.push(`${moduleConfig?.id || 'UNKNOWN_MODULE'} fields must be an immutable array contract`);
  }

  if (moduleConfig?.tenantContract?.noSharedDataDoctrine !== WILSY_CRM_TENANT_BOUNDARY.noSharedDataDoctrine) {
    issues.push(`${moduleConfig?.id || 'UNKNOWN_MODULE'} tenant boundary doctrine mismatch`);
  }

  return issues;
};

/**
 * @function assertWilsyCrmModuleCatalog
 * @description Validates the full CRM module catalog.
 * @returns {Object} CRM catalog health report.
 * @collaboration Provides a deterministic guard that proves the CRM catalog is enterprise-grade before dashboard wiring.
 */
export const assertWilsyCrmModuleCatalog = () => {
  const ids = WILSY_CRM_MODULE_CATALOG.map(moduleConfig => moduleConfig.id);
  const duplicateIds = ids.filter((id, index) => ids.indexOf(id) !== index);
  const issues = WILSY_CRM_MODULE_CATALOG.flatMap(validateWilsyCrmModule);

  duplicateIds.forEach(id => issues.push(`duplicate CRM module id ${id}`));

  if (WILSY_CRM_MODULE_CATALOG.length < 20) {
    issues.push('CRM catalog must contain at least 20 governed modules');
  }

  return Object.freeze({
    ok: issues.length === 0,
    version: WILSY_CRM_MODULE_CATALOG_VERSION,
    moduleCount: WILSY_CRM_MODULE_CATALOG.length,
    workspaceCount: WILSY_CRM_WORKSPACE_CATALOG.length,
    vendorCount: WILSY_CRM_IMPORT_VENDOR_CATALOG.length,
    groupSummary: WILSY_CRM_MODULE_GROUP_SUMMARY,
    noFakeData: true,
    tenantBoundary: WILSY_CRM_TENANT_BOUNDARY.noSharedDataDoctrine,
    issues: Object.freeze(issues)
  });
};

/**
 * @function buildWilsyCrmCatalogReadiness
 * @description Builds an investor-grade readiness packet from CRM catalog health and route posture.
 * @returns {Object} CRM catalog readiness packet.
 * @collaboration Lets the dashboard show catalog maturity without inventing live customer metrics.
 */
export const buildWilsyCrmCatalogReadiness = () => {
  const health = assertWilsyCrmModuleCatalog();
  const liveRoutes = WILSY_CRM_MODULE_CATALOG.filter(moduleConfig => moduleConfig.routePosture === WILSY_CRM_ROUTE_POSTURE.live).length;
  const plannedRoutes = WILSY_CRM_MODULE_CATALOG.filter(moduleConfig => moduleConfig.routePosture === WILSY_CRM_ROUTE_POSTURE.planned).length;

  return Object.freeze({
    ...health,
    liveRoutes,
    plannedRoutes,
    sourceRequiredRoutes: WILSY_CRM_MODULE_CATALOG.length - liveRoutes,
    posture: health.ok ? 'CRM_CATALOG_READY' : 'CRM_CATALOG_REVIEW_REQUIRED',
    investorSignal: health.ok
      ? 'Wilsy CRM has a governed tenant-safe module control plane.'
      : 'Wilsy CRM catalog requires issue remediation before wiring.',
    competitorDelta: Object.freeze({
      hubspot: 'Wilsy adds tenant boundary, receipts and source posture to module operations.',
      zoho: 'Wilsy adds sovereign OS chrome and compliance-grade evidence contracts.',
      zendesk: 'Wilsy unifies tickets, CRM, success and revenue proof in one surface.',
      salesforce: 'Wilsy keeps the operating shell lighter while preserving enterprise governance.'
    })
  });
};

/**
 * @function listWilsyCrmSovereignSalesModules
 * @description Lists the obliteration-grade sovereign Sales CRM modules that turn CRM from a ledger into a forensic revenue operating system.
 * @returns {Array<Object>} Sovereign Sales CRM modules.
 * @collaboration Feeds CRMDashboard investor strip, forensic flow, compliance HUD and sales intelligence workspaces without duplicate config.
 */
export const listWilsyCrmSovereignSalesModules = () => (
  WILSY_CRM_MODULE_CATALOG.filter(moduleConfig => (
    ['lead_intelligence', 'pipeline_cockpit', 'customer_success_telemetry', 'revenue_desk', 'compliance_hud', 'forensic_sales_flow', 'connector_command', 'investor_strip', 'governance_ledger', 'evidence_exports']
      .includes(moduleConfig.id)
  ))
);

/**
 * @function buildWilsyCrmSovereignSalesBlueprint
 * @description Builds the frontend-safe blueprint for the investor-grade Sales CRM operating doctrine.
 * @returns {Object} Sovereign Sales CRM blueprint.
 * @collaboration Gives CRM UI and backend routes a single doctrine packet for lead intelligence, pipeline, revenue, compliance and forensic evidence.
 */
export const buildWilsyCrmSovereignSalesBlueprint = () => {
  const sovereignModules = listWilsyCrmSovereignSalesModules();

  return Object.freeze({
    version: WILSY_CRM_MODULE_CATALOG_VERSION,
    doctrine: 'SOVEREIGN_SALES_CRM_OBLITERATION_GRADE',
    tenantBoundary: WILSY_CRM_TENANT_BOUNDARY.noSharedDataDoctrine,
    noFakeData: true,
    moduleCount: sovereignModules.length,
    modules: Object.freeze(sovereignModules.map(moduleConfig => moduleConfig.id)),
    qualificationFrameworks: WILSY_CRM_QUALIFICATION_FRAMEWORKS,
    complianceClauses: WILSY_CRM_COMPLIANCE_CLAUSE_CATALOG,
    forensicFlow: WILSY_CRM_FORENSIC_FLOW_CATALOG,
    connectorContracts: WILSY_CRM_CONNECTOR_CONTRACTS,
    backendServices: WILSY_CRM_BACKEND_SERVICE_CONTRACTS,
    investorTelemetry: WILSY_CRM_INVESTOR_TELEMETRY_CONTRACT,
    investorSignal: 'Wilsy CRM proves revenue movement, customer evidence, compliance posture and sovereign root integrity.'
  });
};

/**
 * @function buildWilsyCrmForensicSalesFlow
 * @description Builds a source-required forensic sales flow packet that can be rendered before backend receipts are wired.
 * @returns {Object} Forensic sales flow contract.
 * @collaboration Lets the CRM dashboard show chain-of-custody requirements without pretending receipts already exist.
 */
export const buildWilsyCrmForensicSalesFlow = () => Object.freeze({
  version: WILSY_CRM_MODULE_CATALOG_VERSION,
  noFakeData: true,
  sourceStatus: WILSY_CRM_SOURCE_STATUS.sourceRequired,
  routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
  events: WILSY_CRM_FORENSIC_FLOW_CATALOG,
  requiredBackendServices: WILSY_CRM_BACKEND_SERVICE_CONTRACTS,
  tenantBoundary: WILSY_CRM_TENANT_BOUNDARY.noSharedDataDoctrine
});

/**
 * @function buildWilsyCrmInvestorTelemetryStrip
 * @description Builds the source-required investor strip contract for sovereign root hash, sealed receipts and revenue telemetry.
 * @returns {Object} Investor telemetry strip contract.
 * @collaboration Keeps investor-grade CRM telemetry honest until live backend receipts and revenue streams are connected.
 */
export const buildWilsyCrmInvestorTelemetryStrip = () => Object.freeze({
  version: WILSY_CRM_MODULE_CATALOG_VERSION,
  noFakeMetrics: true,
  sourceStatus: WILSY_CRM_SOURCE_STATUS.sourceRequired,
  routePosture: WILSY_CRM_ROUTE_POSTURE.planned,
  telemetry: WILSY_CRM_INVESTOR_TELEMETRY_CONTRACT,
  modules: Object.freeze(['investor_strip', 'revenue_desk', 'forensic_sales_flow', 'compliance_hud', 'governance_ledger']),
  displayDoctrine: 'Show source-required posture instead of fabricated investor metrics.'
});

export const WILSY_CRM_SOVEREIGN_SALES_BLUEPRINT = buildWilsyCrmSovereignSalesBlueprint();

export const WILSY_CRM_FORENSIC_SALES_FLOW = buildWilsyCrmForensicSalesFlow();

export const WILSY_CRM_INVESTOR_TELEMETRY_STRIP = buildWilsyCrmInvestorTelemetryStrip();

export const WILSY_CRM_MODULE_CATALOG_HEALTH = assertWilsyCrmModuleCatalog();

export const WILSY_CRM_CATALOG_READINESS = buildWilsyCrmCatalogReadiness();

export default WILSY_CRM_MODULE_CATALOG;
