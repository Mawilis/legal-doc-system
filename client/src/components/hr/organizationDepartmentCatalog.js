/**
 * WILSY OS — Versioned multi-sector department suggestion catalog.
 * These are OPTIONAL starting points, never tenant records, approved departments,
 * automatic entitlements, staffing permissions, employee assignments or legal facts.
 * Choice is explicit. EOS is the sole authority for creating and approving records.
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
