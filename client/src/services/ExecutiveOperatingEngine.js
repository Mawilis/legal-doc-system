/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - EXECUTIVE OPERATING ENGINE [V2.0.0-ADAPTIVE-BUSINESS-OS]                                                                   ║
 * ║ [BUSINESS MODEL GRAPH | DAILY DUTY COMMANDS | FUNCTION ENTITLEMENTS | INDUSTRY PLAYBOOKS | NO-FAKE-DATA OPERATING INTELLIGENCE]       ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.0.0-ADAPTIVE-BUSINESS-OS | PRODUCTION READY | TENANT-ADAPTIVE EXECUTIVE OPERATING SYSTEM                                  ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/services/ExecutiveOperatingEngine.js                                 ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Mandated that Wilsy OS stop rendering dashboard theatre and instead guide daily executive work       ║
 * ║   for every tenant class: local bakery, importer, construction firm, solo owner and enterprise boardroom.                              ║
 * ║ • AI Engineering (Codex) - ARCHITECTED: Built deterministic tenant-industry inference, source-aware daily duty generation, role        ║
 * ║   access adjudication and Wilsy AI monetisation surfaces without injecting fake operational records.                                   ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

/**
 * @constant {Array<Object>}
 * @description Universal executive duties researched from executive operating practice and small-business management guidance.
 * @collaboration Gives every tenant a serious operating rhythm before industry overlays are applied.
 */
const UNIVERSAL_EXECUTIVE_DUTIES = Object.freeze([
  {
    key: 'daily_source_pulse',
    lane: 'Executive',
    title: 'Confirm finance, customer, operations and telemetry sources',
    reason: 'No executive decision should move from stale or missing operating evidence.',
    cadence: 'Daily',
    evidenceRequired: ['finance source', 'telemetry stream', 'tenant profile'],
    commandLabel: 'Verify Sources',
    wilsyAiUseCase: 'Executive source pulse'
  },
  {
    key: 'cash_and_margin_guard',
    lane: 'Finance',
    title: 'Review cash runway, margin pressure and urgent payables',
    reason: 'Cash, margin and payment timing determine whether the business can execute today.',
    cadence: 'Daily',
    evidenceRequired: ['bank feed', 'revenue ledger', 'expense ledger'],
    commandLabel: 'Accept Cash Review',
    wilsyAiUseCase: 'Cash gap assistant'
  },
  {
    key: 'customer_revenue_focus',
    lane: 'Sales',
    title: 'Choose the highest-value customer, quote or collection follow-up',
    reason: 'Executive attention must move revenue and retention every day.',
    cadence: 'Daily',
    evidenceRequired: ['CRM pipeline', 'invoice ledger', 'customer messages'],
    commandLabel: 'Accept Revenue Move',
    wilsyAiUseCase: 'Customer follow-up agent'
  },
  {
    key: 'operations_blocker_scan',
    lane: 'Operations',
    title: 'Remove the most expensive delivery, stock or service blocker',
    reason: 'Blocked work silently converts payroll, materials and time into waste.',
    cadence: 'Daily',
    evidenceRequired: ['work queue', 'inventory or project source', 'owner notes'],
    commandLabel: 'Accept Blocker Scan',
    wilsyAiUseCase: 'Operations blocker agent'
  },
  {
    key: 'people_capacity_check',
    lane: 'People',
    title: 'Confirm staffing, attendance and accountability for today',
    reason: 'Execution quality is constrained by who is present, trained and assigned.',
    cadence: 'Daily',
    evidenceRequired: ['employee roster', 'attendance', 'task owners'],
    commandLabel: 'Accept People Check',
    wilsyAiUseCase: 'Roster and accountability assistant'
  },
  {
    key: 'compliance_calendar_guard',
    lane: 'Compliance',
    title: 'Check statutory, tax, license and contract deadlines',
    reason: 'Compliance drift becomes penalties, deregistration, lost licenses and personal liability.',
    cadence: 'Daily',
    evidenceRequired: ['compliance calendar', 'tax profile', 'company registry records'],
    commandLabel: 'Accept Compliance Guard',
    wilsyAiUseCase: 'Compliance evidence collector'
  },
  {
    key: 'risk_resilience_watch',
    lane: 'Risk',
    title: 'Review cyber, safety, supplier and emergency-risk exceptions',
    reason: 'A productive OS protects continuity before an incident becomes a crisis.',
    cadence: 'Daily',
    evidenceRequired: ['security telemetry', 'supplier status', 'incident log'],
    commandLabel: 'Accept Risk Watch',
    wilsyAiUseCase: 'Risk sentinel'
  }
]);

/**
 * @constant {Array<string>}
 * @description Core CEO operating modules every tenant should see before industry-specific overlays.
 * @collaboration Wilson needs CEO onboarding to start with finance, people, customer, governance and AI controls for every industry.
 */
const CORE_EXECUTIVE_FUNCTIONS = Object.freeze([
  'executive_dashboard',
  'billing',
  'crm',
  'hr',
  'reports',
  'documents',
  'wilsy_ai'
]);

/**
 * @constant {Object<string, Object>}
 * @description Industry archetypes mapped to daily executive workflows, operating functions and AI use cases.
 * @collaboration Wilson required one dashboard to adapt from sole proprietor to bakery, construction, logistics and enterprise without new components.
 */
export const INDUSTRY_ARCHETYPES = Object.freeze({
  import_logistics_agri: {
    label: 'Import, Logistics and Agri Supply',
    naicsFamily: 'Wholesale Trade / Transportation / Agriculture Supply',
    keywords: ['royal logistics', 'vehicle', 'motor', 'auto parts', 'spare parts', 'import', 'clearance', 'customs', 'agri', 'sunflower', 'supplies', 'warehouse', 'fleet'],
    functions: ['executive_dashboard', 'billing', 'inventory', 'logistics', 'crm', 'contracts', 'currency_fx', 'wilsy_ai'],
    duties: [
      { key: 'stock_aging', lane: 'Operations', title: 'Review vehicle, parts and agri stock aging', reason: 'Capital is trapped when imported units sit too long without follow-up.', cadence: 'Daily', evidenceRequired: ['inventory aging', 'lead pipeline'], commandLabel: 'Open Stock Aging' },
      { key: 'clearing_pipeline', lane: 'Logistics', title: 'Check customs, port and supplier ETA exceptions', reason: 'Import delays become customer trust and cash-flow risk.', cadence: 'Daily', evidenceRequired: ['shipment register', 'supplier ETA', 'customs status'], commandLabel: 'Accept ETA Exceptions' },
      { key: 'wholesale_quotes', lane: 'Sales', title: 'Approve high-value wholesale and negotiable quotes', reason: 'Vehicles, parts and bulk supplies need disciplined margin control.', cadence: 'Daily', evidenceRequired: ['quote pipeline', 'margin target', 'currency rate'], commandLabel: 'Approve Quote Review' },
      { key: 'agri_supply', lane: 'Supply', title: 'Review agribusiness batch availability and demand', reason: 'Sunflower oil and agricultural supplies need stock and demand alignment.', cadence: 'Weekly', evidenceRequired: ['batch register', 'purchase orders'], commandLabel: 'Accept Supply Review' }
    ],
    wilsyAiUseCases: ['Stock aging command centre', 'Import ETA risk assistant', 'WhatsApp lead triage', 'Wholesale quote margin guard']
  },
  bakery_food_service: {
    label: 'Bakery and Food Service',
    naicsFamily: 'Food Services / Specialty Food Manufacturing',
    keywords: ['bakery', 'oven', 'bread', 'cake', 'restaurant', 'food', 'confectionery', 'catering', 'hygiene', 'quality', 'kitchen'],
    functions: ['executive_dashboard', 'billing', 'inventory', 'recipes', 'quality', 'pos', 'wilsy_ai'],
    duties: [
      { key: 'fresh_stock', lane: 'Operations', title: 'Review fresh stock, wastage and production plan', reason: 'Food businesses lose margin through spoilage and poor batch planning.', cadence: 'Daily', evidenceRequired: ['stock count', 'production plan', 'wastage log'], commandLabel: 'Accept Production Plan' },
      { key: 'food_safety', lane: 'Compliance', title: 'Verify hygiene, quality and food-safety checks', reason: 'Food safety is brand trust, legal risk and customer retention.', cadence: 'Daily', evidenceRequired: ['hygiene checklist', 'temperature log', 'incident log'], commandLabel: 'Accept Safety Check' },
      { key: 'branch_service', lane: 'Customer', title: 'Check service incidents and customer sentiment', reason: 'Repeat purchase depends on quick response to service failures.', cadence: 'Daily', evidenceRequired: ['customer messages', 'refunds', 'complaints'], commandLabel: 'Accept Service Review' },
      { key: 'supplier_prices', lane: 'Finance', title: 'Review ingredient price movement and substitutions', reason: 'Ingredient inflation can destroy product profitability.', cadence: 'Weekly', evidenceRequired: ['supplier invoices', 'recipe costing'], commandLabel: 'Accept Cost Review' }
    ],
    wilsyAiUseCases: ['Production planning assistant', 'Food safety checklist agent', 'Wastage anomaly detector', 'Customer complaint triage']
  },
  construction_projects: {
    label: 'Construction and Projects',
    naicsFamily: 'Construction / Specialty Trade Contractors',
    keywords: ['construction', 'contractor', 'site', 'project', 'materials', 'quantity', 'claims', 'retention', 'safety', 'tender'],
    functions: ['executive_dashboard', 'billing', 'project_management', 'procurement', 'contracts', 'health_safety', 'wilsy_ai'],
    duties: [
      { key: 'site_progress', lane: 'Delivery', title: 'Review milestones, blocked sites and labour plan', reason: 'Schedule drift compounds into penalties and cash-flow pressure.', cadence: 'Daily', evidenceRequired: ['project plan', 'site diary', 'labour roster'], commandLabel: 'Accept Site Review' },
      { key: 'materials', lane: 'Supply', title: 'Check material availability, approvals and variance', reason: 'Missing materials stop work and create idle labour cost.', cadence: 'Daily', evidenceRequired: ['procurement queue', 'BOQ variance'], commandLabel: 'Accept Materials Check' },
      { key: 'claims', lane: 'Finance', title: 'Review progress claims, retention and receivables', reason: 'Construction profit depends on disciplined claim timing.', cadence: 'Weekly', evidenceRequired: ['claim register', 'invoice ledger'], commandLabel: 'Accept Claim Review' },
      { key: 'safety', lane: 'Compliance', title: 'Verify site safety incidents and statutory documentation', reason: 'Safety failures become legal, human and delivery risk.', cadence: 'Daily', evidenceRequired: ['safety file', 'incident log'], commandLabel: 'Accept Safety Review' }
    ],
    wilsyAiUseCases: ['Site delay predictor', 'Materials variance assistant', 'Progress claim drafter', 'Safety evidence collector']
  },
  retail_store: {
    label: 'Retail Store and Point-of-Sale Business',
    naicsFamily: 'Retail Trade',
    keywords: ['retail', 'shop', 'store', 'boutique', 'pos', 'cashier', 'merchandise', 'stockroom'],
    functions: ['executive_dashboard', 'billing', 'inventory', 'pos', 'crm', 'wilsy_ai'],
    duties: [
      { key: 'sellthrough', lane: 'Sales', title: 'Review sell-through, slow movers and basket value', reason: 'Retail margin depends on stock velocity and product mix.', cadence: 'Daily', evidenceRequired: ['POS sales', 'inventory movement'], commandLabel: 'Accept Sell-through Review' },
      { key: 'cashup', lane: 'Finance', title: 'Check cash-up, refunds and exceptions', reason: 'Daily cash control protects owner trust and leakage.', cadence: 'Daily', evidenceRequired: ['till reports', 'refund log'], commandLabel: 'Accept Cash-up Review' },
      { key: 'replenishment', lane: 'Supply', title: 'Approve replenishment and supplier follow-ups', reason: 'Out-of-stock items convert demand into lost sales.', cadence: 'Daily', evidenceRequired: ['stock thresholds', 'supplier orders'], commandLabel: 'Accept Replenishment' }
    ],
    wilsyAiUseCases: ['Retail stock recommender', 'Cash-up anomaly detector', 'Customer basket assistant', 'Supplier reorder agent']
  },
  professional_services: {
    label: 'Professional Services',
    naicsFamily: 'Professional, Scientific and Technical Services',
    keywords: ['consulting', 'agency', 'accounting', 'bookkeeping', 'engineering', 'architecture', 'professional', 'advisory'],
    functions: ['executive_dashboard', 'billing', 'time_tracking', 'projects', 'contracts', 'crm', 'wilsy_ai'],
    duties: [
      { key: 'billable_hours', lane: 'Finance', title: 'Review billable work, write-offs and unbilled time', reason: 'Professional firms leak profit when time is not captured and billed.', cadence: 'Daily', evidenceRequired: ['time ledger', 'project budget'], commandLabel: 'Accept Billable Review' },
      { key: 'client_delivery', lane: 'Delivery', title: 'Review client deliverables and blocked approvals', reason: 'Client trust depends on visible progress and fast unblock decisions.', cadence: 'Daily', evidenceRequired: ['project board', 'approval queue'], commandLabel: 'Accept Delivery Review' },
      { key: 'proposal_pipeline', lane: 'Sales', title: 'Prioritise proposals, renewals and account expansion', reason: 'Services growth requires disciplined pipeline conversion.', cadence: 'Daily', evidenceRequired: ['CRM opportunities', 'proposal status'], commandLabel: 'Accept Pipeline Review' }
    ],
    wilsyAiUseCases: ['Unbilled time hunter', 'Proposal drafting assistant', 'Client delivery summariser', 'Meeting action extractor']
  },
  healthcare_clinic: {
    label: 'Healthcare Clinic and Wellness Practice',
    naicsFamily: 'Healthcare and Social Assistance',
    keywords: ['clinic', 'medical', 'doctor', 'dentist', 'healthcare', 'patient', 'pharmacy', 'wellness', 'therapy'],
    functions: ['executive_dashboard', 'billing', 'appointments', 'clinical_admin', 'compliance', 'wilsy_ai'],
    duties: [
      { key: 'appointment_capacity', lane: 'Operations', title: 'Review appointment capacity, no-shows and urgent bookings', reason: 'Clinical productivity and patient care both depend on schedule control.', cadence: 'Daily', evidenceRequired: ['appointment book', 'no-show log'], commandLabel: 'Accept Capacity Review' },
      { key: 'claims_and_billing', lane: 'Finance', title: 'Review claims, cash payments and rejected billing', reason: 'Healthcare cash flow fails when claims and authorisations drift.', cadence: 'Daily', evidenceRequired: ['claims ledger', 'payment register'], commandLabel: 'Accept Claims Review' },
      { key: 'patient_safety', lane: 'Compliance', title: 'Check patient safety, consent and document exceptions', reason: 'Patient trust and legal protection require daily evidence discipline.', cadence: 'Daily', evidenceRequired: ['consent records', 'incident log'], commandLabel: 'Accept Safety Review' }
    ],
    wilsyAiUseCases: ['Patient no-show assistant', 'Claims rejection resolver', 'Consent evidence collector', 'Clinic capacity forecaster']
  },
  manufacturing_workshop: {
    label: 'Manufacturing and Workshop',
    naicsFamily: 'Manufacturing',
    keywords: ['manufacturing', 'factory', 'workshop', 'production', 'assembly', 'machining', 'plant', 'batch'],
    functions: ['executive_dashboard', 'billing', 'production', 'inventory', 'quality', 'maintenance', 'wilsy_ai'],
    duties: [
      { key: 'production_plan', lane: 'Operations', title: 'Review production plan, bottlenecks and yield', reason: 'Manufacturing profit depends on throughput, quality and waste control.', cadence: 'Daily', evidenceRequired: ['production schedule', 'yield report'], commandLabel: 'Accept Production Review' },
      { key: 'machine_downtime', lane: 'Risk', title: 'Check machine downtime, maintenance and spare constraints', reason: 'Unplanned downtime destroys delivery and margin.', cadence: 'Daily', evidenceRequired: ['maintenance log', 'downtime events'], commandLabel: 'Accept Downtime Review' },
      { key: 'quality_escape', lane: 'Compliance', title: 'Review defects, rework and customer quality claims', reason: 'Quality escapes compound into refunds, warranty and reputation damage.', cadence: 'Daily', evidenceRequired: ['QC log', 'returns'], commandLabel: 'Accept Quality Review' }
    ],
    wilsyAiUseCases: ['Production bottleneck assistant', 'Maintenance predictor', 'Quality anomaly detector', 'Batch costing guard']
  },
  ecommerce_digital: {
    label: 'E-commerce and Digital Commerce',
    naicsFamily: 'Electronic Shopping / Digital Services',
    keywords: ['ecommerce', 'e-commerce', 'online store', 'marketplace', 'shopify', 'digital product', 'subscription'],
    functions: ['executive_dashboard', 'billing', 'orders', 'inventory', 'marketing', 'support', 'wilsy_ai'],
    duties: [
      { key: 'order_exceptions', lane: 'Operations', title: 'Review failed orders, fulfilment exceptions and refunds', reason: 'Digital revenue can collapse through hidden fulfilment and payment exceptions.', cadence: 'Daily', evidenceRequired: ['order feed', 'payment gateway'], commandLabel: 'Accept Order Review' },
      { key: 'conversion_metrics', lane: 'Sales', title: 'Review conversion, abandoned carts and campaign spend', reason: 'E-commerce growth depends on conversion discipline, not vanity traffic.', cadence: 'Daily', evidenceRequired: ['analytics', 'campaign spend'], commandLabel: 'Accept Conversion Review' },
      { key: 'support_backlog', lane: 'Customer', title: 'Clear customer support backlog and high-risk reviews', reason: 'Support delay becomes churn, disputes and brand damage.', cadence: 'Daily', evidenceRequired: ['support inbox', 'review feed'], commandLabel: 'Accept Support Review' }
    ],
    wilsyAiUseCases: ['Abandoned cart assistant', 'Refund risk triage', 'Support reply agent', 'Campaign ROI sentinel']
  },
  agriculture_farm: {
    label: 'Agriculture and Farming',
    naicsFamily: 'Agriculture, Forestry, Fishing and Hunting',
    keywords: ['farm', 'crop', 'livestock', 'agriculture', 'harvest', 'irrigation', 'seed', 'fertilizer'],
    functions: ['executive_dashboard', 'billing', 'inventory', 'field_operations', 'procurement', 'wilsy_ai'],
    duties: [
      { key: 'field_plan', lane: 'Operations', title: 'Review field work, weather-sensitive tasks and labour allocation', reason: 'Agriculture loses value when timing, labour and weather are not aligned.', cadence: 'Daily', evidenceRequired: ['field plan', 'weather source', 'labour roster'], commandLabel: 'Accept Field Review' },
      { key: 'input_stock', lane: 'Supply', title: 'Check seed, feed, fertilizer and fuel constraints', reason: 'Input shortages stop work during narrow production windows.', cadence: 'Daily', evidenceRequired: ['input inventory', 'supplier orders'], commandLabel: 'Accept Input Review' },
      { key: 'market_price', lane: 'Finance', title: 'Review crop, livestock or commodity price exposure', reason: 'Farm income depends on market timing and cost control.', cadence: 'Weekly', evidenceRequired: ['sales contracts', 'market prices'], commandLabel: 'Accept Market Review' }
    ],
    wilsyAiUseCases: ['Field task scheduler', 'Input stock sentinel', 'Commodity exposure assistant', 'Harvest readiness planner']
  },
  nonprofit_organization: {
    label: 'Non-profit and Community Organization',
    naicsFamily: 'Civic / Social / Grant-Funded Organizations',
    keywords: ['nonprofit', 'npo', 'ngo', 'charity', 'foundation', 'donor', 'grant', 'community'],
    functions: ['executive_dashboard', 'donor_management', 'projects', 'compliance', 'reports', 'wilsy_ai'],
    duties: [
      { key: 'program_delivery', lane: 'Delivery', title: 'Review program delivery, beneficiary commitments and blockers', reason: 'Mission execution needs evidence, not only intention.', cadence: 'Daily', evidenceRequired: ['program tracker', 'beneficiary register'], commandLabel: 'Accept Program Review' },
      { key: 'donor_pipeline', lane: 'Finance', title: 'Review donor commitments, grant reports and funding gaps', reason: 'Non-profits fail when funding evidence and reporting drift.', cadence: 'Daily', evidenceRequired: ['donor ledger', 'grant calendar'], commandLabel: 'Accept Donor Review' },
      { key: 'governance_pack', lane: 'Compliance', title: 'Check governance minutes, statutory filings and policy updates', reason: 'Governance protects mission continuity and board trust.', cadence: 'Weekly', evidenceRequired: ['board pack', 'compliance register'], commandLabel: 'Accept Governance Review' }
    ],
    wilsyAiUseCases: ['Grant report drafter', 'Donor follow-up assistant', 'Impact evidence collector', 'Board governance packer']
  },
  general_smb: {
    label: 'General Business',
    naicsFamily: 'General Small Business',
    keywords: ['service', 'owner', 'smb', 'sme', 'small business', 'sole proprietor', 'general'],
    functions: ['executive_dashboard', 'billing', 'crm', 'documents', 'compliance', 'wilsy_ai'],
    duties: [
      { key: 'cash_position', lane: 'Finance', title: 'Review cash position, bank feed and urgent payments', reason: 'Small businesses die from cash surprises before accounting surprises.', cadence: 'Daily', evidenceRequired: ['bank feed', 'invoice ledger'], commandLabel: 'Accept Cash Position' },
      { key: 'customer_followup', lane: 'Sales', title: 'Review open customer follow-ups and high-value opportunities', reason: 'Revenue growth comes from disciplined customer attention.', cadence: 'Daily', evidenceRequired: ['customer inbox', 'CRM pipeline'], commandLabel: 'Accept Follow-up Review' },
      { key: 'work_queue', lane: 'Operations', title: 'Prioritise today’s work queue and blocked commitments', reason: 'Owner attention must move the highest-value work forward.', cadence: 'Daily', evidenceRequired: ['task queue', 'owner notes'], commandLabel: 'Accept Work Queue' },
      { key: 'admin_cleanup', lane: 'Administration', title: 'Clear invoices, receipts, documents and reminders', reason: 'Back-office drift becomes expensive cleanup work.', cadence: 'Weekly', evidenceRequired: ['document inbox', 'compliance calendar'], commandLabel: 'Accept Admin Review' }
    ],
    wilsyAiUseCases: ['Owner inbox triage', 'Cash gap assistant', 'Customer follow-up agent', 'Document capture assistant']
  },
  technology_saas: {
    label: 'Technology, SaaS and Digital Product',
    naicsFamily: 'Software / Information Services',
    keywords: ['saas', 'software', 'platform', 'technology', 'app', 'subscription', 'api', 'cloud'],
    functions: ['executive_dashboard', 'billing', 'subscriptions', 'support', 'security', 'product', 'wilsy_ai'],
    duties: [
      { key: 'arr_churn', lane: 'Finance', title: 'Review ARR, churn, failed payments and expansion risk', reason: 'Subscription businesses are governed by retention and recurring revenue truth.', cadence: 'Daily', evidenceRequired: ['subscription ledger', 'payment failures'], commandLabel: 'Accept ARR Review' },
      { key: 'incident_backlog', lane: 'Risk', title: 'Check incidents, uptime and security exceptions', reason: 'Trust and renewal depend on reliability and security response.', cadence: 'Daily', evidenceRequired: ['incident log', 'security telemetry'], commandLabel: 'Accept Incident Review' },
      { key: 'product_commitments', lane: 'Delivery', title: 'Review product commitments and customer-blocking tickets', reason: 'Roadmap discipline protects revenue and credibility.', cadence: 'Daily', evidenceRequired: ['roadmap', 'support tickets'], commandLabel: 'Accept Product Review' }
    ],
    wilsyAiUseCases: ['Churn sentinel', 'Incident summariser', 'Roadmap promise guard', 'Support escalation agent']
  }
});

/**
 * @function getExecutiveBusinessModels
 * @description Returns the available tenant business-model playbooks for dashboard selection and onboarding.
 * @returns {Array<Object>} Business model options.
 * @collaboration Lets Wilson configure one component for many tenants instead of creating bespoke dashboards.
 */
export const getExecutiveBusinessModels = () => Object.entries(INDUSTRY_ARCHETYPES).map(([key, archetype]) => ({
  key,
  label: archetype.label,
  naicsFamily: archetype.naicsFamily,
  functions: archetype.functions,
  dutyCount: archetype.duties.length
}));

/**
 * @function mergeExecutiveFunctionKeys
 * @description Merges universal CEO modules with tenant-industry modules while preserving order and uniqueness.
 * @param {Array<string>} industryFunctions - Industry-specific function keys.
 * @returns {Array<string>} Complete function key list.
 * @collaboration Ensures every CEO onboarding profile includes HR, CRM, finance, documents and Wilsy AI even when an archetype is narrow.
 */
const mergeExecutiveFunctionKeys = (industryFunctions = []) => (
  [...new Set([
    ...CORE_EXECUTIVE_FUNCTIONS,
    ...(Array.isArray(industryFunctions) ? industryFunctions : [])
  ].map(value => String(value || '').toLowerCase()).filter(Boolean))]
);

/**
 * @function getPermissionedFunctions
 * @description Resolves the tenant-enabled functions for the executive surface from permissions and industry playbook defaults.
 * @param {Object} params - Function inputs.
 * @param {Object} params.activeTenant - Active tenant.
 * @param {Object} params.archetype - Selected archetype.
 * @returns {Array<Object>} Function entitlement rows.
 * @collaboration Shows exactly which operating modules are active, missing or recommended for a tenant.
 */
export const getPermissionedFunctions = ({ activeTenant = {}, archetype = {} } = {}) => {
  const tenant = activeTenant && typeof activeTenant === 'object' ? activeTenant : {};
  const enabled = new Set([
    ...(tenant.permissions || []),
    ...(tenant.enabledPermissions || []),
    ...(tenant.features || []),
    ...(tenant.enabledFeatures || []),
    ...(tenant.modules || [])
  ].map(value => String(value).toLowerCase()));
  const recommended = mergeExecutiveFunctionKeys(archetype.functions || INDUSTRY_ARCHETYPES.general_smb.functions);
  return recommended.map((key, index) => ({
    key,
    label: key.replace(/_/g, ' ').toUpperCase(),
    status: enabled.size === 0
      ? 'RECOMMENDED'
      : enabled.has(key.toLowerCase())
        ? 'ENABLED'
        : 'NOT_GRANTED',
    priority: index + 1,
    sourceStatus: enabled.size === 0 ? 'TENANT_PERMISSION_SOURCE_REQUIRED' : 'TENANT_PERMISSION_SOURCE'
  }));
};

/**
 * @function normalizeText
 * @description Converts optional tenant metadata into a searchable lowercase fingerprint.
 * @param {...unknown} values - Candidate metadata values.
 * @returns {string} Normalized text.
 * @collaboration Keeps industry detection deterministic and explainable instead of opaque AI theatre.
 */
const normalizeText = (...values) => values
  .flatMap(value => {
    if (!value) return [];
    if (Array.isArray(value)) return value;
    if (typeof value === 'object') return Object.values(value);
    return [value];
  })
  .filter(Boolean)
  .join(' ')
  .toLowerCase();

/**
 * @function resolveTenantBusinessProfile
 * @description Builds a source-declared tenant business profile from active tenant metadata and researched prospect hints.
 * @param {Object} params - Profile inputs.
 * @param {Object} params.activeTenant - Current tenant object from TenantContext.
 * @param {Object} params.metrics - Parent dashboard metrics.
 * @param {Object} params.analytics - Parent analytics payload.
 * @returns {Object} Tenant business profile with inferred industry and source status.
 * @collaboration Royal Logistics was researched as a prospect; matching tenants inherit source-tagged import/logistics/agri workflows.
 */
export const resolveTenantBusinessProfile = (input = {}) => {
  const { activeTenant = {}, metrics = {}, analytics = {}, businessModelOverride = '' } = input || {};
  const tenant = activeTenant && typeof activeTenant === 'object' ? activeTenant : {};
  const metricPayload = metrics && typeof metrics === 'object' ? metrics : {};
  const analyticsPayload = analytics && typeof analytics === 'object' ? analytics : {};
  const requestedModel = String(
    businessModelOverride
    || tenant.businessModel
    || tenant.industryKey
    || tenant.industryCode
    || ''
  ).trim();
  const fingerprint = normalizeText(
    requestedModel,
    tenant.name,
    tenant.companyName,
    tenant.legalName,
    tenant.alias,
    tenant.domain,
    tenant.website,
    tenant.industry,
    tenant.businessType,
    tenant.sector,
    tenant.description,
    metricPayload.industry,
    analyticsPayload.industry
  );

  const explicitEntry = requestedModel && INDUSTRY_ARCHETYPES[requestedModel]
    ? [requestedModel, INDUSTRY_ARCHETYPES[requestedModel]]
    : null;
  const scoredEntries = Object.entries(INDUSTRY_ARCHETYPES)
    .map(([key, profile]) => ({
      key,
      profile,
      score: [
        key,
        profile.label,
        profile.naicsFamily,
        ...(profile.keywords || [])
      ].reduce((score, keyword) => (
        fingerprint.includes(String(keyword || '').toLowerCase()) ? score + 1 : score
      ), 0)
    }))
    .sort((left, right) => right.score - left.score);
  const matchedEntry = explicitEntry || (scoredEntries[0]?.score > 0
    ? [scoredEntries[0].key, scoredEntries[0].profile]
    : ['general_smb', INDUSTRY_ARCHETYPES.general_smb]);
  const [industryKey, archetype] = matchedEntry;
  const royalProspect = fingerprint.includes('royal') || fingerprint.includes('royal.co.tz');

  // SOVEREIGN WILSY OS DETECTION: The WILSY OS platform itself is a SaaS/tech company.
  // Any tenant whose id/alias/name contains 'wilsy', 'sovereign', 'wilsy-sovereign-root', or
  // whose profile has no industry metadata at all and is operating as the master account,
  // must be identified as technology_saas — never fall through to general_smb.
  const isSovereignRoot = [
    tenant.tenantId, tenant.id, tenant.alias, tenant.name, tenant.companyName, tenant.legalName
  ].some(value => {
    const normalized = String(value || '').toLowerCase();
    return (
      normalized === 'wilsy' ||
      normalized === 'master' ||
      normalized.includes('wilsy-sovereign') ||
      normalized.includes('wilsy_sovereign') ||
      normalized.includes('wilsy os') ||
      normalized === 'global_root' ||
      normalized === 'wilsy_root'
    );
  });

  const finalIndustryKey = isSovereignRoot && industryKey === 'general_smb'
    ? 'technology_saas'
    : royalProspect && industryKey === 'general_smb'
      ? 'import_logistics_agri'
      : industryKey;
  const finalArchetype = isSovereignRoot && industryKey === 'general_smb'
    ? INDUSTRY_ARCHETYPES.technology_saas
    : royalProspect && industryKey === 'general_smb'
      ? INDUSTRY_ARCHETYPES.import_logistics_agri
      : archetype;
  const sourceStatus = businessModelOverride
    ? 'OPERATOR_DECLARED_BUSINESS_MODEL'
    : tenant.industry || tenant.businessType || tenant.website || royalProspect || isSovereignRoot || requestedModel
      ? 'TENANT_PROFILE_DERIVED'
      : 'TENANT_PROFILE_INCOMPLETE';

  return {
    tenantId: tenant.tenantId || tenant.id || metricPayload.tenantId || analyticsPayload.tenantId || 'UNRESOLVED_TENANT',
    name: tenant.name || tenant.companyName || tenant.legalName || tenant.alias || 'Tenant Executive',
    website: tenant.website || tenant.domain || (royalProspect ? 'https://royal.co.tz/' : ''),
    country: tenant.country || tenant.jurisdiction || metricPayload.country || analyticsPayload.country || '',
    industryKey: finalIndustryKey,
    industryLabel: finalArchetype.label,
    naicsFamily: finalArchetype.naicsFamily,
    sourceStatus,
    sourceEvidence: isSovereignRoot && industryKey === 'general_smb'
      ? 'WILSY OS sovereign root tenant auto-detected as Technology / SaaS. Set tenant.industry = "technology_saas" to make permanent.'
      : royalProspect
        ? 'Royal Logistics public website: used motor vehicles, auto parts, agri-business and general supplies.'
        : businessModelOverride
          ? 'Operator-selected session model. Persist this on the tenant profile to make it permanent.'
          : 'Tenant metadata and live dashboard context.',
    archetype: finalArchetype,
    confidence: explicitEntry || businessModelOverride ? 1 : Math.min(1, (scoredEntries[0]?.score || 0) / 4),
    matchSignals: scoredEntries.slice(0, 3).map(entry => ({
      key: entry.key,
      label: entry.profile.label,
      score: entry.score
    }))
  };
};

/**
 * @function buildExecutiveAccessDecision
 * @description Decides whether the current user can enter the executive dashboard and explains the right channel if denied.
 * @param {Object} access - useSovereignAccess result.
 * @param {Object} activeTenant - Current tenant context.
 * @returns {{allowed:boolean,reason:string,required:string,channel:string}}
 * @collaboration Sales representatives must never see executive controls, while tenant owners of small businesses still need owner-level command.
 */
export const buildExecutiveAccessDecision = (access = {}, activeTenant = {}) => {
  const tenant = activeTenant && typeof activeTenant === 'object' ? activeTenant : {};
  const role = String(access.userRole || '').toLowerCase();
  const activeTenantId = tenant.tenantId || tenant.id || null;
  const userTenantId = access.tenantId || null;
  const omegaAuthority = ['super_admin', 'founder', 'omega'].includes(role);
  const crossTenantAuthority = omegaAuthority || ['executive'].includes(role);
  const tenantMismatch = activeTenantId
    && userTenantId
    && userTenantId !== 'MASTER'
    && userTenantId !== 'GLOBAL_ROOT'
    && userTenantId !== 'WILSY_SOVEREIGN_ROOT'
    && activeTenantId !== userTenantId
    && !crossTenantAuthority;
  const tenantPermissions = tenant.permissions || tenant.enabledPermissions || [];
  const explicitPermission = tenantPermissions.includes('executive_dashboard') || access.hasPermission?.('executive_dashboard');
  const allowed = omegaAuthority || ['executive', 'tenant_owner'].includes(role) || explicitPermission;

  if (tenantMismatch) {
    return {
      allowed: false,
      reason: `Tenant isolation blocked this request. User tenant ${userTenantId} cannot command tenant ${activeTenantId}.`,
      required: 'Requires same-tenant ownership or cross-tenant executive authority.',
      channel: 'Ask the tenant owner or Wilsy OS administrator to switch tenant context or grant the correct tenant permission.'
    };
  }

  if (allowed) {
    return {
      allowed: true,
      reason: 'EXECUTIVE_ACCESS_GRANTED',
      required: 'super_admin, executive, tenant_owner or executive_dashboard permission',
      channel: 'Tenant owner or Wilsy OS administrator'
    };
  }

  return {
    allowed: false,
    reason: role === 'sales_representative'
      ? 'Sales representatives are restricted to sales and customer workflows.'
      : role === 'unauthenticated'
        ? 'Authentication is required before executive operating authority can be evaluated.'
        : 'Your current role does not include executive operating authority.',
    required: 'Requires executive, tenant_owner or explicit executive_dashboard permission.',
    channel: 'Ask the tenant owner or Wilsy OS administrator to grant the executive_dashboard permission.'
  };
};

/**
 * @function buildDailyExecutiveDuties
 * @description Generates daily executive work from tenant industry, source status and finance posture without fabricating records.
 * @param {Object} params - Duty inputs.
 * @param {Object} params.profile - Tenant business profile.
 * @param {Object} params.financialKPIs - Normalized finance metrics.
 * @param {Object} params.sourceSnapshot - Source heartbeat state.
 * @returns {Array<Object>} Source-aware daily duties.
 * @collaboration Converts Wilsy OS into a daily operating assistant rather than a passive KPI wall.
 */
export const buildDailyExecutiveDuties = ({ profile = {}, financialKPIs = {}, sourceSnapshot = {} } = {}) => {
  const financeLive = Boolean(sourceSnapshot.finance?.live);
  const telemetryLive = Boolean(sourceSnapshot.telemetry?.live);
  const arr = Number(financialKPIs.arr || financialKPIs.revenue * 1.2 || 0);
  const profileReady = profile.sourceStatus !== 'TENANT_PROFILE_INCOMPLETE';
  const sourceGateByLane = {
    Executive: financeLive || telemetryLive,
    Finance: financeLive,
    Sales: Boolean(sourceSnapshot.crm?.live || sourceSnapshot.sales?.live || sourceSnapshot.records?.live || financeLive),
    Operations: Boolean(sourceSnapshot.procurement?.live || sourceSnapshot.product?.live || sourceSnapshot.it?.live || profileReady),
    Logistics: profileReady,
    Supply: Boolean(sourceSnapshot.procurement?.live || profileReady),
    Delivery: Boolean(sourceSnapshot.product?.live || sourceSnapshot.customerSuccess?.live || profileReady),
    Customer: Boolean(sourceSnapshot.customerSuccess?.live || sourceSnapshot.crm?.live || sourceSnapshot.records?.live || telemetryLive),
    People: Boolean(sourceSnapshot.hr?.live || profileReady),
    Compliance: profileReady,
    Risk: Boolean(sourceSnapshot.security?.live || sourceSnapshot.it?.live || telemetryLive || profileReady),
    Administration: Boolean(sourceSnapshot.records?.live || profileReady),
    'Wilsy AI': profileReady
  };
  const industryDuties = (profile.archetype?.duties || INDUSTRY_ARCHETYPES.general_smb.duties)
    .map(duty => ({
      ...duty,
      key: `industry_${duty.key}`,
      wilsyAiUseCase: duty.wilsyAiUseCase || profile.archetype?.wilsyAiUseCases?.[0] || 'Tenant adaptive assistant'
    }));
  const duties = [
    ...UNIVERSAL_EXECUTIVE_DUTIES.map(duty => ({
      ...duty,
      title: duty.key === 'cash_and_margin_guard' && arr <= 0
        ? 'Connect revenue source before board claims'
        : duty.title,
      reason: duty.key === 'cash_and_margin_guard' && arr <= 0
        ? 'The dashboard refuses to invent revenue posture; connect finance before strategic claims.'
        : duty.reason
    })),
    ...industryDuties,
    {
      key: 'wilsy_ai_daily_automation',
      lane: 'Wilsy AI',
      title: 'Choose one Wilsy AI automation to remove owner-admin load today',
      reason: 'Wilsy AI earns its license when it reduces daily work and produces measurable receipts.',
      cadence: 'Daily',
      evidenceRequired: ['tenant profile', 'telemetry receipt', 'license entitlement'],
      commandLabel: 'Review Wilsy AI',
      wilsyAiUseCase: profile.archetype?.wilsyAiUseCases?.[0] || 'Owner inbox triage'
    }
  ];

  return duties.map((duty, index) => ({
    ...duty,
    priority: sourceGateByLane[duty.lane] === false ? index + 20 : index + 1,
    status: profile.sourceStatus === 'TENANT_PROFILE_INCOMPLETE' && !['Executive', 'Finance'].includes(duty.lane)
      ? 'PROFILE_REQUIRED'
      : sourceGateByLane[duty.lane] === false
        ? 'SOURCE_REQUIRED'
        : 'READY',
    sourceStatus: duty.lane === 'Finance'
      ? sourceSnapshot.finance?.status || 'SOURCE_SILENT'
      : duty.lane === 'Executive'
        ? `${sourceSnapshot.finance?.status || 'FINANCE_UNKNOWN'} / ${sourceSnapshot.telemetry?.status || 'TELEMETRY_UNKNOWN'}`
        : duty.lane === 'People'
          ? sourceSnapshot.hr?.status || profile.sourceStatus
          : ['Sales', 'Customer'].includes(duty.lane)
            ? sourceSnapshot.crm?.status || sourceSnapshot.customerSuccess?.status || profile.sourceStatus
            : duty.lane === 'Supply'
              ? sourceSnapshot.procurement?.status || profile.sourceStatus
              : duty.lane === 'Risk'
                ? sourceSnapshot.security?.status || sourceSnapshot.it?.status || sourceSnapshot.telemetry?.status || profile.sourceStatus
        : profile.sourceStatus,
    evidenceRequired: duty.evidenceRequired || ['tenant operating evidence'],
    commandLabel: duty.commandLabel || 'Accept Duty',
    impact: ['Finance', 'Operations', 'Delivery', 'Logistics', 'Risk', 'Compliance'].includes(duty.lane) ? 'HIGH' : 'MEDIUM',
    blockedReason: sourceGateByLane[duty.lane] === false
      ? `Connect ${duty.lane.toLowerCase()} evidence before execution.`
      : ''
  })).sort((left, right) => left.priority - right.priority);
};

/**
 * @function buildExecutiveOperatingSystem
 * @description Produces the full adaptive executive operating model consumed by ExecutiveDashboard.
 * @param {Object} params - Operating system inputs.
 * @returns {{profile:Object,dailyDuties:Array,wilsyAiUseCases:Array}}
 * @collaboration This is the dashboard's brain: it adapts the executive workflow without fake persisted records.
 */
export const buildExecutiveOperatingSystem = (params = {}) => {
  const safeParams = params && typeof params === 'object' ? params : {};
  const profile = resolveTenantBusinessProfile(safeParams);
  const dailyDuties = buildDailyExecutiveDuties({
    profile,
    financialKPIs: safeParams.financialKPIs,
    sourceSnapshot: safeParams.sourceSnapshot
  });
  const functionMatrix = getPermissionedFunctions({
    activeTenant: safeParams.activeTenant,
    archetype: profile.archetype
  });
  return {
    profile,
    dailyDuties,
    functionMatrix,
    businessModels: getExecutiveBusinessModels(),
    wilsyAiUseCases: profile.archetype?.wilsyAiUseCases || INDUSTRY_ARCHETYPES.general_smb.wilsyAiUseCases
  };
};

export default {
  INDUSTRY_ARCHETYPES,
  getExecutiveBusinessModels,
  getPermissionedFunctions,
  resolveTenantBusinessProfile,
  buildExecutiveAccessDecision,
  buildDailyExecutiveDuties,
  buildExecutiveOperatingSystem
};
