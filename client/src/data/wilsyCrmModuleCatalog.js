/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - CRM MODULE CATALOG [R18AD65-SALES-CRM-OBLITERATION-CONTROL-PLANE]                                           ║
 * ║ SALES | CRM | SDR | CUSTOMER SUCCESS | SUPPORT | REVENUE | FORECAST | AUTOMATION | MIGRATION | AUDIT                    ║
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

export const WILSY_CRM_MODULE_CATALOG_VERSION = 'R18AD65-SALES-CRM-OBLITERATION-CONTROL-PLANE';

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

export const WILSY_CRM_MODULE_CATALOG_HEALTH = assertWilsyCrmModuleCatalog();

export const WILSY_CRM_CATALOG_READINESS = buildWilsyCrmCatalogReadiness();

export default WILSY_CRM_MODULE_CATALOG;
