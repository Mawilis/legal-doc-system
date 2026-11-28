/**
 * TITLE: WILSY OS Multi-Sector Department Suggestion Catalog
 * VERSION: v1.1.0-M03-HR03-MULTISECTOR-SUGGESTION-CATALOG
 * AUTHORITY: WILSY OS Core Governance
 * EPITOME: Versioned optional department vocabulary for many business models; not canonical tenant or staffing state.
 * ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/hr/organizationDepartmentCatalog.js
 * COLLABORATION / OWNERSHIP: WILSY OS HR Organization / Python EOS engineering
 * CERTIFICATION / UPDATE DATE: 2026-11-28
 * CHANGELOG: v1.1.0-M03-HR03-MULTISECTOR-SUGGESTION-CATALOG adds governed source, consumer and evidence contracts without expanding IAM grants.
 * COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
 * SECURITY / PRIVACY POSTURE: Bounded readback and event labels; no personnel/financial secrets, no fabricated external entity verification.
 * TENANT BOUNDARY: Exact authenticated EOS tenant; no root or Owner fallback.
 * AUTHORITY BOUNDARY: EOS source grants are separately required; maker and checker cannot be the same principal.
 * FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS exclusively.
 */
export const ORGANIZATION_CATALOG_VERSION = '2026-11-28.1';

export const ORGANIZATION_BUSINESS_MODELS = Object.freeze([
  {id:'general', label:'General business', departments:['Administration','Finance & Accounting','Human Resources','Operations','Sales & Marketing','Customer Service','Procurement','Information Technology','Risk & Compliance']},
  {id:'legal', label:'Law firm & legal services', departments:['Legal Practice','Litigation','Conveyancing','Commercial Law','Legal Research','Client Intake','Trust Accounting','Compliance & Risk','Practice Operations']},
  {id:'medical', label:'Medical practice & clinic', departments:['Clinical Services','Patient Administration','Nursing','Reception & Scheduling','Pharmacy Coordination','Medical Records','Revenue Cycle','Quality & Patient Safety','Facilities']},
  {id:'dental', label:'Dental practice', departments:['Dental Clinical Services','Dental Hygiene','Patient Reception','Treatment Coordination','Sterilisation','Dental Laboratory','Billing & Collections','Practice Management']},
  {id:'veterinary',label:'Veterinary practice',departments:['Veterinary Clinical Services','Animal Nursing','Surgery','Reception & Appointments','Diagnostics','Pharmacy & Supplies','Animal Care','Practice Administration']},
  {id:'import_export',label:'Import, export & international trade',departments:['International Procurement','Customs & Trade Compliance','Freight Forwarding','Warehousing','Trade Documentation','Inventory Control','Supplier Relations','Sales & Distribution','Finance']},
  {id:'auto_parts',label:'Automotive parts & accessories',departments:['Parts Procurement','Parts Inventory','Counter Sales','Wholesale Distribution','Warehouse & Dispatch','Customer Support','Workshop Supply','Finance & Administration']},
  {id:'mechanical',label:'Vehicle workshop & maintenance',departments:['Workshop Operations','Vehicle Diagnostics','Mechanical Repairs','Service Advisory','Parts & Stores','Quality Control','Fleet Servicing','Customer Reception']},
  {id:'dealership',label:'Vehicle dealership',departments:['New Vehicle Sales','Used Vehicle Sales','Vehicle Finance & Insurance','Aftersales Service','Parts & Accessories','Vehicle Preparation','Customer Relations','Dealer Operations']},
  {id:'agriculture',label:'Agriculture & farming',departments:['Crop Production','Livestock Operations','Farm Equipment','Irrigation','Harvest & Packing','Agricultural Procurement','Storage & Distribution','Food Safety & Quality']},
  {id:'manufacturing',label:'Manufacturing & production',departments:['Production','Maintenance & Reliability','Quality Assurance','Engineering','Materials Planning','Procurement','Health & Safety','Warehousing & Logistics']},
  {id:'construction',label:'Construction & contracting',departments:['Project Delivery','Site Operations','Quantity Surveying','Engineering & Design','Procurement','Health & Safety','Plant & Equipment','Contract Administration']},
  {id:'retail',label:'Retail & commerce',departments:['Store Operations','Merchandising','Inventory Management','Customer Service','E-commerce','Supplier Purchasing','Distribution','Finance & Administration']},
  {id:'hospitality',label:'Hospitality & accommodation',departments:['Front Office','Housekeeping','Food & Beverage','Kitchen','Guest Experience','Reservations','Maintenance','Events & Banqueting']},
  {id:'education',label:'Education & training',departments:['Academic Affairs','Teaching & Learning','Student Services','Admissions','Assessment','Library & Learning Resources','Facilities','Finance & Administration']},
  {id:'technology',label:'Software & technology services',departments:['Product Management','Software Engineering','Quality Engineering','Security & Compliance','Infrastructure & Operations','Customer Success','Technical Support','Sales & Partnerships']},
  {id:'professional',label:'Consulting & professional services',departments:['Client Delivery','Advisory','Research & Insights','Business Development','Engagement Management','Quality & Compliance','People Operations','Finance']},
  {id:'financial',label:'Financial & insurance services',departments:['Client Advisory','Underwriting','Claims Operations','Credit & Risk','Compliance','Finance','Client Onboarding','Operations']},
  {id:'logistics',label:'Logistics & transport',departments:['Fleet Operations','Dispatch & Routing','Warehousing','Freight Operations','Transport Safety','Maintenance','Customer Logistics','Trade Compliance']},
  {id:'property',label:'Property & facilities',departments:['Property Management','Leasing','Facilities Maintenance','Tenant Services','Valuation','Portfolio Operations','Compliance & Safety','Finance']},
  {id:'energy',label:'Energy & utilities',departments:['Field Operations','Engineering','Asset Management','Health Safety & Environment','Grid & Distribution','Customer Operations','Procurement','Regulatory Compliance']},
  {id:'nonprofit',label:'Nonprofit & community organisation',departments:['Programme Delivery','Community Outreach','Grants & Funding','Monitoring & Evaluation','Volunteer Coordination','Safeguarding','Administration','Finance']},
  {id:'public',label:'Public & municipal services',departments:['Public Administration','Service Delivery','Community Services','Infrastructure','Public Finance','Procurement','Records Management','Governance & Compliance']},
]);

export function getDepartmentSuggestions(modelId, query = '', approvedRecords = []) {
  const model = ORGANIZATION_BUSINESS_MODELS.find(item => item.id === modelId)
    || ORGANIZATION_BUSINESS_MODELS[0];
  const normalizedQuery = query.trim().toLocaleLowerCase();
  const existingNames = new Set(
    approvedRecords.filter(row => row?.kind === 'DEPARTMENT')
      .map(row => String(row.name || '').trim().toLocaleLowerCase())
  );
  return model.departments
    .filter(name => !existingNames.has(name.toLocaleLowerCase()))
    .filter(name => !normalizedQuery || name.toLocaleLowerCase().includes(normalizedQuery));
}

/**
 * ARTIFACT: client/src/components/hr/organizationDepartmentCatalog.js
 * VERSION: v1.1.0-M03-HR03-MULTISECTOR-SUGGESTION-CATALOG
 * AUTHORITY BOUNDARY: Presentation/projection only; Python EOS owns authorizations and decisions.
 * TENANT POSTURE: Exact authorized tenant only; no cross-tenant records, Owner or root fallback.
 * FAIL-CLOSED POSTURE: Missing or contradictory evidence is denied/unavailable, never approved.
 * FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
 * END OF WILSY OS SOVEREIGN ARTIFACT
 */
