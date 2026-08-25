/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN HR OPERATING SUITE [V2.2.0-OS-CHROME]                                                                       ║
 * ║ [WORKFORCE COMMAND | HIRING PIPELINE | PAYROLL CONTROL | BENEFITS | PERFORMANCE | ABSENCE COMMAND | LIVE LEDGER]                    ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 2.2.0-OS-CHROME | PRODUCTION READY | PEOPLE OPERATING SYSTEM                                                           ║
 * ║ ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/client/src/components/hr/HrDashboard.jsx                                        ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ COLLABORATION & SOVEREIGN SIGN-OFF:                                                                                                    ║
 * ║ • Wilson Khanyezi (Founder/CEO) - Rejected table-only HR prototypes and mandated a real HR operating cockpit for daily leadership.  ║
 * ║ • AI Engineering (Codex) - REBUILT: Connected HR to a live backend ledger, added workforce KPIs, hiring/payroll/performance/absence ║
 * ║   workflows, source feedback, mutation forms, exports and telemetry without fake placeholder records.                                ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Activity,
  Briefcase,
  Calendar,
  CheckCircle,
  CreditCard,
  Download,
  Edit,
  Globe2,
  Heart,
  MapPin,
  PanelLeftClose,
  PanelLeftOpen,
  Plus,
  RefreshCw,
  Search,
  ShieldCheck,
  FileText,
  Star,
  Trash2,
  UserCircle,
  UserPlus,
  Users,
  X
} from 'lucide-react';
import { useAuth } from '../../contexts/authContext';
import { useTenants } from '../../contexts/tenantContext';
import { useTelemetryFeed } from '../../hooks/useTelemetryFeed';
import api from '../../services/api';
import * as hrService from '../../services/hrService';
import { resolveCountryOption, searchSovereignCountries } from '../../data/sovereignCountryRegistry';
import { exportCSV } from '../../utils/exportHelpers';
import WilsyProfilePanel, { hydrateWilsyProfileRuntime } from '../shared/WilsyProfilePanel';
import WilsyOSDashboardChrome from '../os/WilsyOSDashboardChrome';
import WilsyAccountCommandCenter from '../account/WilsyAccountCommandCenter';
import wilsyLogo from '../../assets/logo/wilsy.jpeg';
import styles from './HrDashboard.module.css';

const DEFAULT_TENANT_ID = 'MASTER';
const DEFAULT_PAGE = Object.freeze({ offset: 0, limit: 12 });

const HR_TABS = Object.freeze([
  { id: 'employees', label: 'Workforce', icon: Users, modalType: 'employee' },
  { id: 'candidates', label: 'Hiring Pipeline', icon: UserPlus, modalType: 'candidate' },
  { id: 'jobOpenings', label: 'Open Roles', icon: Briefcase, modalType: 'jobOpening' },
  { id: 'payroll', label: 'Payroll', icon: CreditCard, modalType: 'payroll' },
  { id: 'benefits', label: 'Benefits', icon: Heart, modalType: 'benefit' },
  { id: 'performance', label: 'Performance', icon: Star, modalType: 'performanceReview' },
  { id: 'activity', label: 'Activity', icon: Activity, modalType: 'employeeWorkLog' },
  { id: 'relations', label: 'Relations', icon: ShieldCheck, modalType: 'employeeRelations' },
  { id: 'timeoff', label: 'Time Off', icon: Calendar, modalType: 'timeOff' },
  { id: 'artifacts', label: 'HR Artifacts', icon: FileText, modalType: 'hrArtifact' }
]);

const EMPTY_DATASET = Object.freeze({ items: [], total: 0, limit: DEFAULT_PAGE.limit, offset: 0, hasMore: false });

const DATASET_DEFAULTS = Object.freeze({
  employees: EMPTY_DATASET,
  candidates: EMPTY_DATASET,
  jobOpenings: EMPTY_DATASET,
  payroll: EMPTY_DATASET,
  benefits: EMPTY_DATASET,
  performance: EMPTY_DATASET,
  activity: EMPTY_DATASET,
  relations: EMPTY_DATASET,
  timeoff: EMPTY_DATASET,
  artifacts: EMPTY_DATASET
});

const HR_ARTIFACT_TYPES = Object.freeze([
  { id: 'employment_contract', label: 'Employment Contract' },
  { id: 'appointment_letter', label: 'Appointment Letter' },
  { id: 'remuneration_addendum', label: 'Remuneration Addendum' },
  { id: 'onboarding_pack', label: 'Onboarding Pack' },
  { id: 'warning_notice', label: 'Warning Notice' },
  { id: 'verbal_warning_record', label: 'Verbal Warning' },
  { id: 'written_warning', label: 'Written Warning' },
  { id: 'final_written_warning', label: 'Final Written Warning' },
  { id: 'suspension_notice', label: 'Suspension Notice' },
  { id: 'disciplinary_hearing_notice', label: 'Disciplinary Hearing' },
  { id: 'dismissal_notice', label: 'Dismissal Notice' },
  { id: 'performance_improvement_plan', label: 'Performance Plan' },
  { id: 'leave_approval_letter', label: 'Leave Approval Letter' },
  { id: 'exit_acceptance_letter', label: 'Exit Acceptance Letter' }
]);

const ARTIFACT_TEMPLATE_GUIDANCE = Object.freeze({
  employment_contract: {
    kicker: 'Employment Contract',
    title: 'Contract Pack',
    intent: 'Locks identity, reporting line, remuneration, probation and workplace into one reviewable employment contract.',
    controls: ['Identity verified', 'Role and department selected', 'Salary reviewed', 'Signature block prepared']
  },
  appointment_letter: {
    kicker: 'Appointment Letter',
    title: 'Appointment Command',
    intent: 'Confirms the appointment, start date, reporting line and acceptance language before the employee receives access.',
    controls: ['Start date selected', 'Manager selected', 'Employment type confirmed', 'Acceptance terms ready']
  },
  remuneration_addendum: {
    kicker: 'Remuneration Addendum',
    title: 'Compensation Review',
    intent: 'Focuses HR on salary, pay cadence, benefits, allowances, commission and effective date before print.',
    controls: ['Base pay captured', 'Benefits selected', 'Variable pay reviewed', 'Effective date selected']
  },
  onboarding_pack: {
    kicker: 'Onboarding Pack',
    title: 'First-Day Runway',
    intent: 'Builds the first-day checklist: documents, manager handoff, workplace model, systems access and policy acknowledgement.',
    controls: ['Employee identity ready', 'Department assigned', 'Manager handoff set', 'Workplace model selected']
  },
  warning_notice: {
    kicker: 'Warning Notice',
    title: 'Disciplinary Control',
    intent: 'Creates a controlled warning notice so HR records incident context, corrective action and follow-up governance.',
    controls: ['Employee identified', 'Reporting line selected', 'Review date selected', 'Authorized signatory ready']
  },
  verbal_warning_record: {
    kicker: 'Verbal Warning',
    title: 'Coaching Record',
    intent: 'Records verbal coaching, the incident, expected correction and the employee response before escalation.',
    controls: ['Incident captured', 'Manager confirmed', 'Employee response recorded', 'Follow-up date selected']
  },
  written_warning: {
    kicker: 'Written Warning',
    title: 'Formal Warning',
    intent: 'Issues a written warning with evidence, policy breach, corrective action and review governance.',
    controls: ['Evidence attached', 'Policy breach selected', 'Corrective action clear', 'Employee acknowledgement ready']
  },
  final_written_warning: {
    kicker: 'Final Warning',
    title: 'Final Control',
    intent: 'Records the final warning before possible suspension or dismissal with consequence language and proof.',
    controls: ['Prior warnings reviewed', 'Final consequence stated', 'Hearing path clear', 'HR authorization ready']
  },
  suspension_notice: {
    kicker: 'Suspension Notice',
    title: 'Suspension Control',
    intent: 'Issues a suspension notice with investigation posture, effective dates, pay status and hearing path.',
    controls: ['Suspension reason captured', 'Dates selected', 'Pay posture reviewed', 'Access restriction ready']
  },
  disciplinary_hearing_notice: {
    kicker: 'Disciplinary Hearing',
    title: 'Hearing Command',
    intent: 'Notifies the employee of allegations, evidence, representation rights and hearing schedule.',
    controls: ['Allegations listed', 'Evidence referenced', 'Hearing date selected', 'Representation rights visible']
  },
  dismissal_notice: {
    kicker: 'Dismissal Notice',
    title: 'Exit Enforcement',
    intent: 'Issues dismissal documentation with findings, effective date, appeal path, final pay and access revocation.',
    controls: ['Outcome recorded', 'Final pay reviewed', 'Appeal path included', 'Access revocation queued']
  },
  performance_improvement_plan: {
    kicker: 'Performance Plan',
    title: 'Performance Recovery',
    intent: 'Frames measurable improvement targets, manager support, review cadence and HR proof for performance governance.',
    controls: ['Role context selected', 'Manager selected', 'Milestones dated', 'Support commitments ready']
  },
  leave_approval_letter: {
    kicker: 'Leave Approval',
    title: 'Absence Decision',
    intent: 'Confirms approved leave dates, coverage accountability and employee acknowledgement for the absence ledger.',
    controls: ['Employee selected', 'Dates selected', 'Manager coverage selected', 'Decision proof ready']
  },
  exit_acceptance_letter: {
    kicker: 'Exit Acceptance',
    title: 'Exit Control',
    intent: 'Prepares final handover, asset return, final pay and access removal controls before the employee exits.',
    controls: ['Identity verified', 'Reporting line selected', 'Final date selected', 'Exit obligations ready']
  }
});

const ARTIFACT_FORM_DEFAULTS = Object.freeze({
  artifactType: 'employment_contract',
  firstName: '',
  surname: '',
  cellphone: '',
  nationality: '',
  nationalityCode: '',
  address: '',
  addressLatitude: '',
  addressLongitude: '',
  addressMapUrl: '',
  addressVerifiedAt: '',
  identityNumber: '',
  personalEmail: '',
  employeeName: '',
  roleTitle: '',
  department: '',
  startDate: '',
  employmentType: 'Permanent',
  baseSalary: '',
  payrollCountry: 'ZA',
  payDay: 25,
  payFrequency: 'Monthly',
  benefits: '',
  taxableBenefits: '',
  benefitDeductions: '',
  otherDeductions: '',
  employerBenefits: '',
  variablePay: '',
  reportingLine: '',
  workplace: '',
  probation: '3 months',
  effectiveDate: '',
  signatoryName: 'Wilson Khanyezi',
  relationsActionType: '',
  incidentDate: '',
  incidentSummary: '',
  policyBreach: '',
  correctiveAction: '',
  employeeResponse: '',
  hearingDate: '',
  reviewDate: '',
  outcome: ''
});

const DATE_FIELD_NAMES = Object.freeze(['startDate', 'endDate', 'effectiveDate', 'dueDate', 'visaExpiry', 'interviewDate', 'incidentDate', 'hearingDate', 'reviewDate', 'workDate', 'renewalDate', 'plannedPayDate', 'periodDate']);

const ROLE_OPTIONS = Object.freeze([
  'Chief Executive Officer',
  'Chief Financial Officer',
  'Chief Operating Officer',
  'Chief Technology Officer',
  'HR Manager',
  'People Operations Lead',
  'Finance Manager',
  'Sales Consultant',
  'Sales Executive',
  'Marketing Manager',
  'Digital Marketing Specialist',
  'Customer Success Manager',
  'Mechanic',
  'Senior Mechanic',
  'Workshop Manager',
  'Software Engineer',
  'Frontend Engineer',
  'Backend Engineer',
  'Data Engineer',
  'Product Manager',
  'Legal Counsel',
  'Operations Coordinator',
  'Executive Assistant',
  'Chief People Officer',
  'Recruitment Specialist',
  'Payroll Administrator',
  'Benefits Administrator',
  'Compliance Officer',
  'Risk Analyst',
  'Data Analyst',
  'Business Analyst',
  'Product Designer',
  'QA Engineer',
  'DevOps Engineer',
  'Customer Support Lead',
  'Account Executive',
  'Procurement Manager',
  'Office Administrator',
  'Security Officer',
  'Warehouse Supervisor',
  'Field Technician',
  'General Manager',
  'Branch Manager',
  'Office Manager',
  'Accountant',
  'Bookkeeper',
  'Accounts Payable Clerk',
  'Accounts Receivable Clerk',
  'Tax Specialist',
  'Internal Auditor',
  'Treasury Analyst',
  'Financial Controller',
  'Business Development Manager',
  'Key Account Manager',
  'Retail Sales Associate',
  'Store Manager',
  'Call Centre Agent',
  'Customer Support Specialist',
  'Implementation Specialist',
  'Service Desk Analyst',
  'Technical Support Engineer',
  'Network Engineer',
  'Systems Administrator',
  'Cloud Engineer',
  'Cybersecurity Analyst',
  'Machine Learning Engineer',
  'Database Administrator',
  'UX Designer',
  'UI Designer',
  'Content Strategist',
  'SEO Specialist',
  'Social Media Manager',
  'Brand Manager',
  'Campaign Manager',
  'Supply Chain Manager',
  'Logistics Coordinator',
  'Fleet Manager',
  'Driver',
  'Forklift Operator',
  'Inventory Controller',
  'Production Supervisor',
  'Manufacturing Operator',
  'Quality Control Inspector',
  'Health And Safety Officer',
  'Facilities Manager',
  'Electrician',
  'Plumber',
  'Civil Engineer',
  'Construction Project Manager',
  'Quantity Surveyor',
  'Architect',
  'Nurse',
  'Doctor',
  'Clinical Administrator',
  'Pharmacist',
  'Caregiver',
  'Teacher',
  'Lecturer',
  'Training Facilitator',
  'Learning And Development Specialist',
  'Research Analyst',
  'Laboratory Technician',
  'Compliance Manager',
  'Legal Secretary',
  'Paralegal',
  'Contract Manager',
  'Data Protection Officer',
  'Procurement Officer',
  'Buyer',
  'Receptionist',
  'Personal Assistant',
  'Cleaner',
  'Chef',
  'Waiter',
  'Hotel Manager',
  'Travel Consultant',
  'Real Estate Agent',
  'Property Manager',
  'Insurance Broker'
]);

const DEPARTMENT_OPTIONS = Object.freeze([
  'Executive',
  'Human Resources',
  'Finance',
  'Legal',
  'Engineering',
  'Product',
  'Sales',
  'Marketing',
  'Customer Success',
  'Operations',
  'Compliance',
  'Security',
  'Administration'
]);

const EMPLOYMENT_TYPE_OPTIONS = Object.freeze([
  'Permanent',
  'Fixed-term',
  'Probationary',
  'Part-time',
  'Internship',
  'Contractor',
  'Consultant',
  'Executive appointment'
]);

const PAY_FREQUENCY_OPTIONS = Object.freeze(['Monthly', 'Fortnightly', 'Weekly', 'Hourly', 'Commission-based', 'Milestone-based']);
const PAYROLL_COUNTRY_OPTIONS = Object.freeze(['ZA', 'US', 'UK', 'NG', 'KE', 'GH', 'BW']);
const ADDRESS_INTELLIGENCE_ANCHORS = Object.freeze([
  { city: 'Midrand', province: 'Gauteng', country: 'South Africa', lat: -25.9992, lng: 28.1263 },
  { city: 'Sandton', province: 'Gauteng', country: 'South Africa', lat: -26.1076, lng: 28.0567 },
  { city: 'Johannesburg', province: 'Gauteng', country: 'South Africa', lat: -26.2041, lng: 28.0473 },
  { city: 'Pretoria', province: 'Gauteng', country: 'South Africa', lat: -25.7479, lng: 28.2293 },
  { city: 'Cape Town', province: 'Western Cape', country: 'South Africa', lat: -33.9249, lng: 18.4241 },
  { city: 'Durban', province: 'KwaZulu-Natal', country: 'South Africa', lat: -29.8587, lng: 31.0218 },
  { city: 'Bloemfontein', province: 'Free State', country: 'South Africa', lat: -29.0852, lng: 26.1596 },
  { city: 'Gqeberha', province: 'Eastern Cape', country: 'South Africa', lat: -33.9608, lng: 25.6022 },
  { city: 'Polokwane', province: 'Limpopo', country: 'South Africa', lat: -23.9045, lng: 29.4689 },
  { city: 'Mbombela', province: 'Mpumalanga', country: 'South Africa', lat: -25.4753, lng: 30.9694 },
  { city: 'Mahikeng', province: 'North West', country: 'South Africa', lat: -25.8652, lng: 25.6442 },
  { city: 'Kimberley', province: 'Northern Cape', country: 'South Africa', lat: -28.7282, lng: 24.7499 }
]);
const PAYROLL_STATUS_OPTIONS = Object.freeze(['DRAFT', 'READY', 'APPROVED', 'PAID', 'HELD_IDENTITY_REVIEW', 'HELD_EXCEPTION']);
const BENEFIT_OPTIONS = Object.freeze([
  'Sovereign Founder Pack',
  'Executive Retention Pack',
  'Standard Employee Pack',
  'Field Operations Pack',
  'Remote Work Pack',
  'Medical aid',
  'Pension / retirement',
  'Group life cover',
  'Disability income cover',
  'Funeral cover',
  'Wellness programme',
  'Transport allowance',
  'Housing allowance',
  'Meal allowance',
  'Device allowance',
  'Data allowance',
  'Study assistance',
  'Commission plan',
  'Performance bonus',
  'Share option plan',
  'None'
]);
const WORKPLACE_OPTIONS = Object.freeze(['On-site', 'Hybrid', 'Remote', 'Client site', 'Field operations', 'Executive office']);
const RECRUITING_STAGE_OPTIONS = Object.freeze(['New', 'Screening', 'Interview', 'Technical assessment', 'Reference check', 'Offer', 'Hired', 'Rejected']);
const JOB_STATUS_OPTIONS = Object.freeze(['Draft', 'Approved', 'Open', 'On hold', 'Filled', 'Closed']);
const JOB_PRIORITY_OPTIONS = Object.freeze(['Critical', 'High', 'Normal', 'Low']);
const BENEFIT_STATUS_OPTIONS = Object.freeze(['Active', 'Pending approval', 'Paused', 'Closed']);
const BENEFIT_COVERAGE_OPTIONS = Object.freeze(['Employee only', 'Employee plus spouse', 'Employee plus family', 'Executive only', 'Department plan', 'Company wide']);
const PERFORMANCE_STATUS_OPTIONS = Object.freeze(['Draft', 'Pending employee review', 'Manager review', 'Approved', 'Needs improvement', 'Closed']);
const TIME_OFF_STATUS_OPTIONS = Object.freeze(['Pending', 'Approved', 'Denied', 'Cancelled']);
const LEAVE_TYPE_OPTIONS = Object.freeze(['Annual leave', 'Sick leave', 'Family responsibility', 'Unpaid leave', 'Study leave', 'Maternity leave', 'Paternity leave']);
const ID_TYPE_OPTIONS = Object.freeze(['South African ID', 'Passport', 'Asylum / refugee document', 'Permanent residence permit', 'Work visa']);
const RIGHT_TO_WORK_OPTIONS = Object.freeze(['Pending verification', 'Verified South African citizen', 'Verified permanent resident', 'Verified work visa', 'Expired / blocked']);
const VISA_TYPE_OPTIONS = Object.freeze(['Not applicable', 'Critical skills visa', 'General work visa', 'Intra-company transfer', 'Business visa', 'Permanent residence']);
const WORK_LOG_TYPE_OPTIONS = Object.freeze(['Daily work', 'Achievement', 'Sales activity', 'Customer work', 'Project delivery', 'Training', 'Attendance exception', 'Incident evidence']);
const PERFORMANCE_RISK_OPTIONS = Object.freeze(['None', 'Coaching required', 'Warning possible', 'Formal process active']);

const ZA_PAYROLL_2027 = Object.freeze({
  country: 'ZA',
  taxYear: '2027',
  defaultPayDay: 25,
  primaryRebate: 17820,
  uifMonthlyCeiling: 17712,
  uifRate: 0.01,
  brackets: [
    { upTo: 245100, base: 0, rate: 0.18, threshold: 0 },
    { upTo: 383100, base: 44118, rate: 0.26, threshold: 245100 },
    { upTo: 530200, base: 79998, rate: 0.31, threshold: 383100 },
    { upTo: 695800, base: 125599, rate: 0.36, threshold: 530200 },
    { upTo: 887000, base: 185215, rate: 0.39, threshold: 695800 },
    { upTo: 1878600, base: 259783, rate: 0.41, threshold: 887000 },
    { upTo: Number.POSITIVE_INFINITY, base: 666339, rate: 0.45, threshold: 1878600 }
  ]
});

const ROLE_INTELLIGENCE_LIBRARY = Object.freeze({
  'Chief Executive Officer': {
    department: 'Executive',
    duties: ['Set company strategy', 'Lead capital and stakeholder execution', 'Approve executive operating cadence'],
    kpis: ['Revenue growth', 'Runway', 'Strategic milestones', 'Leadership execution'],
    disciplinaryAnchors: ['Governance breach', 'Material misrepresentation', 'Failure to execute board mandate']
  },
  'HR Manager': {
    department: 'Human Resources',
    duties: ['Own workforce compliance', 'Run hiring and onboarding', 'Administer performance and employee relations'],
    kpis: ['Time to hire', 'Onboarding completion', 'Policy compliance', 'Employee record accuracy'],
    disciplinaryAnchors: ['Breach of confidentiality', 'Failure to follow disciplinary process', 'Unlawful record handling']
  },
  'People Operations Lead': {
    department: 'Human Resources',
    duties: ['Maintain HR operations', 'Coordinate people analytics', 'Improve employee lifecycle processes'],
    kpis: ['HR ticket resolution', 'Employee lifecycle completion', 'Benefits accuracy', 'Data hygiene'],
    disciplinaryAnchors: ['Data negligence', 'Unapproved policy deviation', 'Missed compliance controls']
  },
  'Software Engineer': {
    department: 'Engineering',
    duties: ['Build production software', 'Review code and tests', 'Resolve incidents and technical debt'],
    kpis: ['Delivery quality', 'System reliability', 'Security compliance', 'Cycle time'],
    disciplinaryAnchors: ['Security negligence', 'Repeated delivery failure', 'Unauthorized production change']
  },
  'Finance Manager': {
    department: 'Finance',
    duties: ['Manage financial controls', 'Prepare payroll/ledger reviews', 'Support budget and cash planning'],
    kpis: ['Close accuracy', 'Payroll exception rate', 'Budget variance', 'Audit readiness'],
    disciplinaryAnchors: ['Unauthorized payment', 'Ledger misstatement', 'Control bypass']
  },
  'Sales Executive': {
    department: 'Sales',
    duties: ['Manage pipeline', 'Close qualified deals', 'Maintain CRM evidence and customer handoff'],
    kpis: ['Pipeline value', 'Closed revenue', 'Win rate', 'Forecast accuracy'],
    disciplinaryAnchors: ['Misrepresentation to customer', 'CRM falsification', 'Unapproved discounting']
  },
  'Sales Consultant': {
    department: 'Sales',
    duties: ['Prospect and qualify leads', 'Run product consultations', 'Close sales and maintain CRM evidence'],
    kpis: ['Monthly sales target', 'Qualified pipeline', 'Conversion rate', 'Customer follow-up'],
    disciplinaryAnchors: ['False pipeline reporting', 'Failure to follow up customers', 'Unapproved discounting']
  },
  'Marketing Manager': {
    department: 'Marketing',
    duties: ['Own campaign calendar', 'Generate qualified demand', 'Measure channel performance'],
    kpis: ['Qualified leads', 'Campaign ROI', 'Conversion rate', 'Brand execution'],
    disciplinaryAnchors: ['Misuse of budget', 'Unapproved campaign claims', 'Failure to evidence results']
  },
  Mechanic: {
    department: 'Operations',
    duties: ['Diagnose and repair work orders', 'Record parts and job evidence', 'Maintain safety and quality controls'],
    kpis: ['Jobs completed', 'Comeback rate', 'Safety compliance', 'Turnaround time'],
    disciplinaryAnchors: ['Unsafe work', 'Unrecorded parts usage', 'Repeated comeback repairs']
  },
  'Workshop Manager': {
    department: 'Operations',
    duties: ['Allocate workshop jobs', 'Review mechanic quality', 'Manage parts and customer handover'],
    kpis: ['Workshop throughput', 'Comeback rate', 'Parts variance', 'Customer acceptance'],
    disciplinaryAnchors: ['Safety negligence', 'Inventory control failure', 'Unresolved customer complaints']
  },
  'Operations Coordinator': {
    department: 'Operations',
    duties: ['Coordinate daily operations', 'Track work orders', 'Escalate blockers and service failures'],
    kpis: ['Task completion', 'SLA adherence', 'Escalation speed', 'Operating accuracy'],
    disciplinaryAnchors: ['Negligent handoff', 'Repeated missed SLA', 'Unreported operational risk']
  }
});

const ROLE_FAMILY_PROFILES = Object.freeze([
  {
    match: /sales|account executive|business development|retail/i,
    department: 'Sales',
    duties: ['Build qualified pipeline', 'Manage customer conversations', 'Record CRM evidence and close revenue'],
    kpis: ['Closed revenue', 'Pipeline value', 'Win rate', 'Follow-up SLA'],
    disciplinaryAnchors: ['False pipeline reporting', 'Unapproved discounting', 'Failure to follow up customers']
  },
  {
    match: /marketing|brand|campaign|seo|content|social media/i,
    department: 'Marketing',
    duties: ['Plan campaigns', 'Generate qualified demand', 'Measure channel performance and brand execution'],
    kpis: ['Qualified leads', 'Campaign ROI', 'Conversion rate', 'Content delivery'],
    disciplinaryAnchors: ['Misuse of budget', 'Unapproved public claims', 'Failure to evidence campaign results']
  },
  {
    match: /engineer|developer|devops|cloud|database|qa|cyber|security analyst|machine learning/i,
    department: 'Engineering',
    duties: ['Deliver production systems', 'Maintain secure evidence of work', 'Resolve incidents and technical risk'],
    kpis: ['Delivery quality', 'Defect rate', 'System reliability', 'Security compliance'],
    disciplinaryAnchors: ['Unauthorized production change', 'Security negligence', 'Repeated delivery failure']
  },
  {
    match: /finance|accountant|bookkeeper|payroll|tax|auditor|treasury|controller/i,
    department: 'Finance',
    duties: ['Maintain accurate financial records', 'Operate payroll and controls', 'Prepare audit-ready evidence'],
    kpis: ['Ledger accuracy', 'Payroll exception rate', 'Close timeliness', 'Audit readiness'],
    disciplinaryAnchors: ['Unauthorized payment', 'Ledger misstatement', 'Control bypass']
  },
  {
    match: /hr|people|recruit|benefits|learning|training/i,
    department: 'Human Resources',
    duties: ['Maintain employee lifecycle controls', 'Run hiring and performance evidence', 'Protect HR vault records'],
    kpis: ['Verified records', 'Time to hire', 'Case closure', 'Employee lifecycle completion'],
    disciplinaryAnchors: ['Breach of confidentiality', 'Unlawful record handling', 'Failure to follow process']
  },
  {
    match: /mechanic|technician|workshop|operator|production|quality|field|electrician|plumber|construction|fleet|driver|logistics|warehouse|inventory|supply chain/i,
    department: 'Operations',
    duties: ['Execute work orders', 'Record operational evidence', 'Maintain safety, quality and customer handover'],
    kpis: ['Jobs completed', 'SLA adherence', 'Safety compliance', 'Quality acceptance'],
    disciplinaryAnchors: ['Unsafe work', 'Unrecorded work evidence', 'Repeated service failure']
  },
  {
    match: /customer|support|service desk|implementation|success|call centre/i,
    department: 'Customer Success',
    duties: ['Resolve customer work', 'Maintain service evidence', 'Escalate customer and product risks'],
    kpis: ['Resolution time', 'Customer satisfaction', 'Escalation quality', 'Retention signals'],
    disciplinaryAnchors: ['Customer neglect', 'Unrecorded support outcome', 'Escalation failure']
  },
  {
    match: /legal|compliance|risk|paralegal|contract|data protection/i,
    department: 'Legal',
    duties: ['Protect legal/compliance posture', 'Maintain case and contract evidence', 'Escalate regulatory risk'],
    kpis: ['Case closure', 'Contract turnaround', 'Risk remediation', 'Audit evidence'],
    disciplinaryAnchors: ['Confidentiality breach', 'Missed regulatory control', 'Unapproved legal commitment']
  },
  {
    match: /doctor|nurse|clinical|pharmacist|caregiver|health/i,
    department: 'Clinical Operations',
    duties: ['Deliver compliant care/service', 'Maintain clinical evidence', 'Escalate patient and safety risk'],
    kpis: ['Care quality', 'Clinical documentation', 'Safety compliance', 'Response time'],
    disciplinaryAnchors: ['Unsafe care', 'Missing clinical record', 'Policy breach']
  },
  {
    match: /teacher|lecturer|education|facilitator|research|laboratory/i,
    department: 'Education And Research',
    duties: ['Deliver learning/research outcomes', 'Track learner or research evidence', 'Maintain quality standards'],
    kpis: ['Outcome completion', 'Assessment quality', 'Evidence hygiene', 'Stakeholder feedback'],
    disciplinaryAnchors: ['Assessment negligence', 'Research integrity breach', 'Unrecorded learner evidence']
  },
  {
    match: /chef|waiter|hotel|hospitality|travel|property|real estate|reception|assistant|administrator|cleaner/i,
    department: 'Administration',
    duties: ['Operate assigned service workflow', 'Record service evidence', 'Maintain workplace standards'],
    kpis: ['Task completion', 'Service quality', 'Attendance', 'Customer or internal feedback'],
    disciplinaryAnchors: ['Attendance breach', 'Service negligence', 'Policy non-compliance']
  }
]);

const ROLE_FAMILY_TARGETS = Object.freeze([
  {
    match: /sales|account executive|business development|retail/i,
    targets: ['Closed revenue', 'Qualified pipeline', 'CRM evidence hygiene', 'Customer follow-up SLA'],
    metrics: ['Revenue closed', 'Pipeline value', 'Win rate', 'Follow-up completion'],
    recommendation: 'Use CRM evidence, customer follow-up, pipeline quality and closed revenue to decide coaching, commission or corrective action.'
  },
  {
    match: /mechanic|technician|workshop|operator|field|driver|logistics|warehouse|production/i,
    targets: ['Completed work orders', 'Quality acceptance', 'Safety checklist', 'Turnaround time'],
    metrics: ['Jobs completed', 'Rework rate', 'Safety compliance', 'SLA adherence'],
    recommendation: 'Compare daily work logs, safety evidence, quality acceptance and customer handover before performance action.'
  },
  {
    match: /engineer|developer|devops|cloud|database|qa|cyber|machine learning/i,
    targets: ['Delivered work', 'Defect rate', 'Security compliance', 'Incident response'],
    metrics: ['Cycle time', 'Defect rate', 'Test coverage', 'Production stability'],
    recommendation: 'Review tickets, peer reviews, incident evidence, security posture and production reliability before reward or discipline.'
  },
  {
    match: /finance|accountant|bookkeeper|payroll|tax|auditor|treasury/i,
    targets: ['Ledger accuracy', 'Payroll controls', 'Close timeline', 'Exception resolution'],
    metrics: ['Error rate', 'Close timeliness', 'Payroll holds', 'Audit readiness'],
    recommendation: 'Review ledger accuracy, payroll holds, exception closure and audit evidence before performance or remuneration changes.'
  },
  {
    match: /hr|people|recruit|benefits|learning|training/i,
    targets: ['Verified records', 'Time to hire', 'Employee relations closure', 'Payroll readiness'],
    metrics: ['Record completeness', 'Time to hire', 'Case closure', 'Payroll exceptions'],
    recommendation: 'Prioritize identity vault completeness, hiring cycle time, employee-relations proof and payroll exception reduction.'
  },
  {
    match: /marketing|brand|campaign|seo|content|social media/i,
    targets: ['Qualified demand', 'Campaign ROI', 'Conversion rate', 'Brand quality'],
    metrics: ['Leads generated', 'ROI', 'Conversion rate', 'Delivery cadence'],
    recommendation: 'Review campaign evidence, spend discipline, conversion data and brand-risk posture before reward or corrective action.'
  }
]);

const ROLE_COMPENSATION_BANDS = Object.freeze([
  { match: /chief|director|general manager/i, min: 90000, max: 220000 },
  { match: /manager|lead|head|controller/i, min: 45000, max: 95000 },
  { match: /engineer|developer|architect|data scientist|cyber/i, min: 35000, max: 120000 },
  { match: /sales|account executive|business development/i, min: 18000, max: 65000 },
  { match: /finance|accountant|payroll|tax|auditor/i, min: 22000, max: 80000 },
  { match: /mechanic|technician|operator|driver|warehouse|production/i, min: 12000, max: 45000 },
  { match: /nurse|doctor|clinical|pharmacist/i, min: 25000, max: 140000 },
  { match: /teacher|lecturer|training|facilitator/i, min: 18000, max: 70000 },
  { match: /assistant|administrator|reception|support|clerk/i, min: 10000, max: 35000 }
]);

const WORK_LOG_TYPE_WORKFLOWS = Object.freeze({
  'Daily work': { achievementType: 'Task evidence', impactScore: 50, performanceScore: 50, status: 'RECORDED' },
  Achievement: { achievementType: 'Achievement proof', impactScore: 80, performanceScore: 85, status: 'MANAGER_REVIEW' },
  'Sales activity': { achievementType: 'CRM / revenue evidence', impactScore: 75, performanceScore: 75, status: 'MANAGER_REVIEW' },
  'Customer work': { achievementType: 'Customer outcome', impactScore: 70, performanceScore: 70, status: 'MANAGER_REVIEW' },
  'Project delivery': { achievementType: 'Delivery milestone', impactScore: 85, performanceScore: 80, status: 'MANAGER_REVIEW' },
  Training: { achievementType: 'Learning evidence', impactScore: 55, performanceScore: 60, status: 'RECORDED' },
  'Attendance exception': { achievementType: 'Attendance proof', impactScore: 20, performanceScore: 30, status: 'MANAGER_REVIEW' },
  'Incident evidence': { achievementType: 'Incident record', impactScore: 10, performanceScore: 20, status: 'MANAGER_REVIEW' }
});

const ROLE_TARGET_LIBRARY = Object.freeze({
  'Sales Consultant': {
    targets: ['R monthly closed revenue', 'Qualified pipeline coverage', 'CRM evidence hygiene', 'Customer follow-up SLA'],
    metrics: ['Revenue closed', 'Pipeline value', 'Win rate', 'Follow-up completion'],
    recommendation: 'Review sales target, pipeline quality, customer follow-up and CRM evidence before coaching or commission action.'
  },
  'Sales Executive': {
    targets: ['Closed revenue', 'Forecast accuracy', 'Opportunity quality', 'Customer handoff'],
    metrics: ['Closed revenue', 'Pipeline value', 'Forecast accuracy', 'Win rate'],
    recommendation: 'Coach forecast discipline and insist every opportunity has verified CRM evidence.'
  },
  Mechanic: {
    targets: ['Jobs completed', 'Comeback rate', 'Safety checklist', 'Parts accuracy'],
    metrics: ['Repair quality', 'Turnaround time', 'Safety compliance', 'Customer acceptance'],
    recommendation: 'Compare completed jobs, rework, safety checks and evidence photos before performance action.'
  },
  'Software Engineer': {
    targets: ['Delivered work', 'Defect rate', 'Security compliance', 'Incident response'],
    metrics: ['Cycle time', 'Defect rate', 'Test coverage', 'Production stability'],
    recommendation: 'Review delivered tickets, peer review quality, incident evidence and production reliability.'
  },
  'HR Manager': {
    targets: ['Verified records', 'Hiring cycle', 'Employee relations closure', 'Payroll readiness'],
    metrics: ['Record completeness', 'Time to hire', 'Case closure', 'Payroll exceptions'],
    recommendation: 'Prioritize identity vault completion, payroll exceptions and unresolved employee-relations cases.'
  },
  default: {
    targets: ['Attendance', 'Task completion', 'Quality of work', 'Evidence hygiene'],
    metrics: ['Attendance', 'Task completion', 'Quality of work', 'Manager feedback'],
    recommendation: 'Review daily work evidence, attendance, quality and manager feedback before any HR decision.'
  }
});

const RECRUITING_STAGE_WORKFLOWS = Object.freeze({
  New: {
    title: 'New Applicant Intake',
    evidence: ['CV received', 'Identity reference captured', 'Consent to process information'],
    nextActions: ['Screen minimum requirements', 'Check right-to-work signal', 'Assign recruiter']
  },
  Screening: {
    title: 'Screening Control',
    evidence: ['Phone screen notes', 'Salary expectation', 'Availability', 'Role fit decision'],
    nextActions: ['Score screening', 'Reject or move to interview', 'Record risks']
  },
  Interview: {
    title: 'Interview Evidence',
    evidence: ['Interview date', 'Panel members', 'Scorecard', 'Culture and role-fit notes'],
    nextActions: ['Capture scorecard', 'Compare against role KPIs', 'Move to assessment or offer']
  },
  'Technical assessment': {
    title: 'Assessment Proof',
    evidence: ['Assessment link/result', 'Reviewer score', 'Work sample', 'Evidence file reference'],
    nextActions: ['Record assessment score', 'Attach evidence reference', 'Decide next stage']
  },
  'Reference check': {
    title: 'Reference And Background',
    evidence: ['Reference contact', 'Employment confirmation', 'Integrity notes', 'Background status'],
    nextActions: ['Complete reference call', 'Verify identity/right-to-work', 'Prepare offer pack']
  },
  Offer: {
    title: 'Offer Control',
    evidence: ['Offer amount', 'Benefits package', 'Start date', 'Approval authority'],
    nextActions: ['Generate appointment letter', 'Send offer', 'Prepare onboarding']
  },
  Hired: {
    title: 'Hire Conversion',
    evidence: ['Accepted offer', 'Signed contract', 'Identity verified', 'Onboarding pack'],
    nextActions: ['Create employee record', 'Schedule onboarding', 'Provision access']
  },
  Rejected: {
    title: 'Closed Candidate',
    evidence: ['Decision reason', 'Reviewer notes', 'Communication sent'],
    nextActions: ['Archive record', 'Preserve evidence', 'Close requisition impact']
  }
});

const BENEFIT_PLAN_LIBRARY = Object.freeze({
  'Medical aid': { description: 'Health-cover contribution with eligibility and payroll deduction tracking.', employerDefault: 1800, employeeDefault: 650 },
  'Pension / retirement': { description: 'Retirement contribution plan linked to monthly payroll and employee eligibility.', employerDefault: 1200, employeeDefault: 800 },
  'Group life cover': { description: 'Life insurance benefit linked to employee category, beneficiary record and payroll eligibility.', employerDefault: 220, employeeDefault: 0 },
  'Disability income cover': { description: 'Income-protection benefit for long-term disability risk and workforce continuity.', employerDefault: 340, employeeDefault: 80 },
  'Funeral cover': { description: 'Funeral assistance plan with beneficiary controls and payroll-linked eligibility.', employerDefault: 140, employeeDefault: 35 },
  'Wellness programme': { description: 'Employee assistance, counselling and wellness benefit with utilization governance.', employerDefault: 180, employeeDefault: 0 },
  'Transport allowance': { description: 'Monthly commute support for approved roles, shifts or field operations.', employerDefault: 750, employeeDefault: 0 },
  'Housing allowance': { description: 'Housing support allowance with role eligibility and tax visibility.', employerDefault: 1500, employeeDefault: 0 },
  'Meal allowance': { description: 'Meal support for shifts, travel or field operations with monthly exposure tracking.', employerDefault: 450, employeeDefault: 0 },
  'Device allowance': { description: 'Device or laptop support for approved work equipment obligations.', employerDefault: 500, employeeDefault: 0 },
  'Data allowance': { description: 'Connectivity allowance for remote, hybrid or field employees.', employerDefault: 350, employeeDefault: 0 },
  'Study assistance': { description: 'Education support with completion evidence, clawback rules and manager approval.', employerDefault: 1000, employeeDefault: 0 },
  'Commission plan': { description: 'Variable pay plan tied to role KPIs, targets and payout rules.', employerDefault: 0, employeeDefault: 0 },
  'Performance bonus': { description: 'Performance incentive linked to documented scorecards and approved targets.', employerDefault: 0, employeeDefault: 0 },
  'Share option plan': { description: 'Long-term incentive plan with vesting, eligibility, governance and board approval controls.', employerDefault: 0, employeeDefault: 0 },
  None: { description: 'No benefit plan selected.', employerDefault: 0, employeeDefault: 0 }
});

const BENEFIT_PACKAGE_LIBRARY = Object.freeze({
  'Sovereign Founder Pack': {
    description: 'Founder-grade retention package with healthcare, retirement, life cover, disability protection, wellness and connectivity.',
    provider: 'Wilsy OS Benefits Vault',
    coverage: 'Executive only',
    eligibilityRule: 'Executives only',
    waitingPeriod: 'None',
    taxable: 'Payroll review required',
    payrollDeductionCode: 'BEN-SOV-FOUNDER',
    items: ['Medical aid', 'Pension / retirement', 'Group life cover', 'Disability income cover', 'Wellness programme', 'Data allowance']
  },
  'Executive Retention Pack': {
    description: 'Executive benefit bundle for senior leadership continuity and auditable payroll value.',
    provider: 'Wilsy OS Benefits Vault',
    coverage: 'Executive only',
    eligibilityRule: 'Executives only',
    waitingPeriod: 'None',
    taxable: 'Payroll review required',
    payrollDeductionCode: 'BEN-EXEC-RET',
    items: ['Medical aid', 'Pension / retirement', 'Group life cover', 'Disability income cover']
  },
  'Standard Employee Pack': {
    description: 'Default employee package with medical, retirement, life cover and wellness support.',
    provider: 'Wilsy OS Benefits Vault',
    coverage: 'Employee only',
    eligibilityRule: 'All active employees',
    waitingPeriod: 'After probation',
    taxable: 'Payroll review required',
    payrollDeductionCode: 'BEN-STD-EMP',
    items: ['Medical aid', 'Pension / retirement', 'Group life cover', 'Wellness programme']
  },
  'Field Operations Pack': {
    description: 'Field-worker package with transport, meal, data, device and funeral coverage for operational continuity.',
    provider: 'Wilsy OS Benefits Vault',
    coverage: 'Department plan',
    eligibilityRule: 'Department only',
    waitingPeriod: '30 days',
    taxable: 'Payroll review required',
    payrollDeductionCode: 'BEN-FIELD-OPS',
    items: ['Transport allowance', 'Meal allowance', 'Data allowance', 'Device allowance', 'Funeral cover']
  },
  'Remote Work Pack': {
    description: 'Remote-work productivity bundle with data, device, wellness and study assistance controls.',
    provider: 'Wilsy OS Benefits Vault',
    coverage: 'Company wide',
    eligibilityRule: 'All active employees',
    waitingPeriod: 'None',
    taxable: 'Payroll review required',
    payrollDeductionCode: 'BEN-REMOTE-WORK',
    items: ['Data allowance', 'Device allowance', 'Wellness programme', 'Study assistance']
  }
});

/**
 * @function uniqueOptions
 * @description Merges option sources into a stable searchable list.
 * @param {...Array<string>} groups - Option groups.
 * @returns {Array<string>} Unique options.
 * @collaboration HR controls should make good selections easy instead of forcing fragile free typing.
 */
const uniqueOptions = (...groups) => [...new Set(groups.flat().map(option => String(option || '').trim()).filter(Boolean))];

/**
 * @function findEmployeeByDisplay
 * @description Resolves an employee row from a display name, email or id.
 * @param {Array<Object>} employees - Employee rows.
 * @param {string} value - Selected field value.
 * @returns {Object|null} Matching employee.
 * @collaboration HR forms should inherit employee department, role and identity data from the ledger when a person is selected.
 */
const findEmployeeByDisplay = (employees = [], value = '') => {
  const needle = String(value || '').trim().toLowerCase();
  if (!needle) return null;
  return employees.find(employee => (
    [employee.id, employee.employeeId, employee.name, employee.employeeName, employee.email]
      .map(item => String(item || '').trim().toLowerCase())
      .includes(needle)
  )) || null;
};

/**
 * @function resolveBenefitPackage
 * @description Resolves a benefit package or falls back to a single benefit plan.
 * @param {string} value - Benefit package or benefit plan name.
 * @returns {Object} Package packet with itemized plans.
 * @collaboration HR benefits should behave like governed payroll packages, not a manually typed memo field.
 */
const resolveBenefitPackage = (value = '') => {
  const name = String(value || 'None').trim() || 'None';
  const packagePlan = BENEFIT_PACKAGE_LIBRARY[name];
  if (packagePlan) {
    return {
      name,
      isPackage: true,
      ...packagePlan,
      plans: packagePlan.items.map(item => ({ name: item, ...(BENEFIT_PLAN_LIBRARY[item] || BENEFIT_PLAN_LIBRARY.None) }))
    };
  }
  const singlePlan = BENEFIT_PLAN_LIBRARY[name] || BENEFIT_PLAN_LIBRARY.None;
  return {
    name: BENEFIT_PLAN_LIBRARY[name] ? name : 'None',
    isPackage: false,
    description: singlePlan.description,
    provider: '',
    coverage: '',
    eligibilityRule: '',
    waitingPeriod: '',
    taxable: 'Payroll review required',
    payrollDeductionCode: name && name !== 'None' ? `BEN-${name.replace(/[^a-z0-9]+/gi, '-').replace(/^-|-$/g, '').toUpperCase()}` : '',
    items: name === 'None' ? [] : [name],
    plans: name === 'None' ? [] : [{ name, ...singlePlan }]
  };
};

const FIELD_CONFIG = Object.freeze({
  employee: [
    { field: 'name', label: 'Full name', required: true },
    { field: 'email', label: 'Work email', type: 'email', required: true },
    { field: 'idType', label: 'Identity type', control: 'select', options: ID_TYPE_OPTIONS, required: true },
    { field: 'identityNumber', label: 'SA ID / identity number', inputMode: 'numeric' },
    { field: 'passportNumber', label: 'Passport number' },
    { field: 'nationality', label: 'Nationality', control: 'countryLookup' },
    { field: 'rightToWorkStatus', label: 'Right to work', control: 'select', options: RIGHT_TO_WORK_OPTIONS },
    { field: 'visaType', label: 'Visa type', control: 'select', options: VISA_TYPE_OPTIONS },
    { field: 'visaExpiry', label: 'Visa expiry', type: 'date' },
    { field: 'taxNumber', label: 'Tax number', inputMode: 'numeric' },
    { field: 'address', label: 'Residential address', control: 'addressLookup', required: true },
    { field: 'addressLatitude', label: 'Address latitude', type: 'number', inputMode: 'decimal' },
    { field: 'addressLongitude', label: 'Address longitude', type: 'number', inputMode: 'decimal' },
    { field: 'proofOfResidenceReference', label: 'Proof of residence reference' },
    { field: 'department', label: 'Department', control: 'datalist', optionSet: 'departments' },
    { field: 'position', label: 'Role', control: 'datalist', optionSet: 'roles' },
    { field: 'manager', label: 'Reporting line', control: 'datalist', optionSet: 'managers' },
    { field: 'location', label: 'Workplace', control: 'select', options: WORKPLACE_OPTIONS },
    { field: 'leaveEntitlement', label: 'Annual leave entitlement', type: 'number', inputMode: 'numeric' },
    { field: 'status', label: 'Status', control: 'select', options: ['ACTIVE', 'ONBOARDING', 'PROBATION', 'SUSPENDED', 'EXITED'] }
  ],
  candidate: [
    { field: 'name', label: 'Candidate name', required: true },
    { field: 'email', label: 'Email', type: 'email' },
    { field: 'phone', label: 'Mobile number', type: 'tel', inputMode: 'tel' },
    { field: 'idType', label: 'Identity type', control: 'select', options: ID_TYPE_OPTIONS },
    { field: 'identityNumber', label: 'SA ID / identity number', inputMode: 'numeric' },
    { field: 'passportNumber', label: 'Passport number' },
    { field: 'nationality', label: 'Nationality', control: 'countryLookup' },
    { field: 'rightToWorkStatus', label: 'Right to work', control: 'select', options: RIGHT_TO_WORK_OPTIONS },
    { field: 'address', label: 'Residential address', control: 'addressLookup' },
    { field: 'addressLatitude', label: 'Address latitude', type: 'number', inputMode: 'decimal' },
    { field: 'addressLongitude', label: 'Address longitude', type: 'number', inputMode: 'decimal' },
    { field: 'position', label: 'Target role', control: 'datalist', optionSet: 'roles' },
    { field: 'stage', label: 'Pipeline stage', control: 'select', options: RECRUITING_STAGE_OPTIONS },
    { field: 'assessmentScore', label: 'Assessment score', type: 'number', inputMode: 'decimal' },
    { field: 'assessmentEvidence', label: 'Evidence reference' },
    { field: 'interviewDate', label: 'Interview date', type: 'date' },
    { field: 'status', label: 'Decision status', control: 'select', options: ['ACTIVE', 'SHORTLISTED', 'OFFER', 'HIRED', 'REJECTED'] },
    { field: 'expectedSalary', label: 'Expected salary', type: 'number', inputMode: 'decimal' }
  ],
  jobOpening: [
    { field: 'title', label: 'Role title', control: 'datalist', optionSet: 'roles', required: true },
    { field: 'department', label: 'Department', control: 'datalist', optionSet: 'departments', required: true },
    { field: 'location', label: 'Workplace model', control: 'select', options: WORKPLACE_OPTIONS },
    { field: 'status', label: 'Opening status', control: 'select', options: JOB_STATUS_OPTIONS },
    { field: 'priority', label: 'Hiring priority', control: 'select', options: JOB_PRIORITY_OPTIONS },
    { field: 'headcount', label: 'Headcount needed', type: 'number', inputMode: 'numeric' },
    { field: 'salaryMin', label: 'Salary band min', type: 'number', inputMode: 'decimal' },
    { field: 'salaryMax', label: 'Salary band max', type: 'number', inputMode: 'decimal' }
  ],
  payroll: [
    { field: 'employeeName', label: 'Employee', control: 'datalist', optionSet: 'employees' },
    { field: 'payrollCountry', label: 'Payroll country', control: 'select', options: PAYROLL_COUNTRY_OPTIONS },
    { field: 'period', label: 'Payroll period', placeholder: 'June 2026' },
    { field: 'payrollMonth', label: 'Payroll month', type: 'number', inputMode: 'numeric' },
    { field: 'payrollYear', label: 'Payroll year', type: 'number', inputMode: 'numeric' },
    { field: 'payDay', label: 'Pay day', type: 'number', inputMode: 'numeric' },
    { field: 'plannedPayDate', label: 'Planned pay date', type: 'date' },
    { field: 'grossPay', label: 'Gross pay', type: 'number', inputMode: 'decimal' },
    { field: 'benefits', label: 'Benefit package', control: 'benefitPackagePicker' },
    { field: 'taxableBenefits', label: 'Taxable benefits', type: 'number', inputMode: 'decimal' },
    { field: 'preTaxDeductions', label: 'Pre-tax deductions', type: 'number', inputMode: 'decimal' },
    { field: 'benefitDeductions', label: 'Benefit deductions', type: 'number', inputMode: 'decimal' },
    { field: 'otherDeductions', label: 'Other deductions', type: 'number', inputMode: 'decimal' },
    { field: 'employerBenefits', label: 'Employer benefits', type: 'number', inputMode: 'decimal' },
    { field: 'netPay', label: 'Net pay', type: 'number', inputMode: 'decimal' },
    { field: 'status', label: 'Payroll status', control: 'select', options: PAYROLL_STATUS_OPTIONS }
  ],
  benefit: [
    { field: 'name', label: 'Benefit package', control: 'benefitPackagePicker', required: true },
    { field: 'provider', label: 'Provider / administrator' },
    { field: 'policyNumber', label: 'Policy / plan number' },
    { field: 'status', label: 'Status', control: 'select', options: BENEFIT_STATUS_OPTIONS },
    { field: 'coverage', label: 'Coverage', control: 'select', options: BENEFIT_COVERAGE_OPTIONS },
    { field: 'eligibilityRule', label: 'Eligibility rule', control: 'select', options: ['All active employees', 'Permanent staff only', 'Executives only', 'Department only', 'After probation', 'Custom approval'] },
    { field: 'waitingPeriod', label: 'Waiting period', control: 'select', options: ['None', '30 days', '3 months', '6 months', 'After probation'] },
    { field: 'eligibleEmployees', label: 'Eligible employees', type: 'number', inputMode: 'numeric' },
    { field: 'employerContribution', label: 'Employer monthly contribution', type: 'number', inputMode: 'decimal' },
    { field: 'employeeContribution', label: 'Employee monthly contribution', type: 'number', inputMode: 'decimal' },
    { field: 'cost', label: 'Monthly employer cost', type: 'number', inputMode: 'decimal' },
    { field: 'taxable', label: 'Tax treatment', control: 'select', options: ['Taxable benefit', 'Non-taxable', 'Payroll review required'] },
    { field: 'payrollDeductionCode', label: 'Payroll deduction code' },
    { field: 'effectiveDate', label: 'Effective date', type: 'date' },
    { field: 'renewalDate', label: 'Renewal date', type: 'date' }
  ],
  performanceReview: [
    { field: 'employeeName', label: 'Employee', control: 'datalist', optionSet: 'employees' },
    { field: 'reviewerName', label: 'Reviewer', control: 'datalist', optionSet: 'managers' },
    { field: 'roleTitle', label: 'Role being reviewed', control: 'datalist', optionSet: 'roles' },
    { field: 'rating', label: 'Rating', control: 'select', options: ['1', '2', '3', '4', '5'] },
    { field: 'period', label: 'Review period', placeholder: 'Q2 2026' },
    { field: 'goalsMet', label: 'Goals met', type: 'number', inputMode: 'numeric' },
    { field: 'goalsTotal', label: 'Total goals', type: 'number', inputMode: 'numeric' },
    { field: 'attendanceScore', label: 'Attendance score', type: 'number', inputMode: 'numeric' },
    { field: 'taskScore', label: 'Task score', type: 'number', inputMode: 'numeric' },
    { field: 'qualityScore', label: 'Quality score', type: 'number', inputMode: 'numeric' },
    { field: 'customerScore', label: 'Customer / stakeholder score', type: 'number', inputMode: 'numeric' },
    { field: 'roleTargetEvidence', label: 'Role target evidence' },
    { field: 'managerRecommendation', label: 'Manager recommendation' },
    { field: 'disciplinaryRisk', label: 'Disciplinary risk', control: 'select', options: PERFORMANCE_RISK_OPTIONS },
    { field: 'status', label: 'Review status', control: 'select', options: PERFORMANCE_STATUS_OPTIONS },
    { field: 'dueDate', label: 'Next review date', type: 'date' }
  ],
  employeeWorkLog: [
    { field: 'employeeName', label: 'Employee', control: 'datalist', optionSet: 'employees', required: true },
    { field: 'workDate', label: 'Work date', type: 'date', required: true },
    { field: 'workType', label: 'Work type', control: 'select', options: WORK_LOG_TYPE_OPTIONS },
    { field: 'achievementType', label: 'Achievement / evidence type' },
    { field: 'evidenceReference', label: 'Evidence reference' },
    { field: 'impactScore', label: 'Impact score', type: 'number', inputMode: 'numeric' },
    { field: 'performanceScore', label: 'Performance score', type: 'number', inputMode: 'numeric' },
    { field: 'description', label: 'Work evidence summary' },
    { field: 'status', label: 'Evidence status', control: 'select', options: ['RECORDED', 'MANAGER_REVIEW', 'VERIFIED', 'DISPUTED'] }
  ],
  employeeRelations: [
    { field: 'employeeName', label: 'Employee', control: 'datalist', optionSet: 'employees', required: true },
    { field: 'relationsActionType', label: 'Relations action', control: 'select', options: ['Verbal warning', 'Written warning', 'Final written warning', 'Suspension', 'Disciplinary hearing', 'Dismissal', 'Performance improvement plan'] },
    { field: 'incidentDate', label: 'Incident date', type: 'date' },
    { field: 'policyBreach', label: 'Policy / duty breached' },
    { field: 'incidentSummary', label: 'Incident evidence summary' },
    { field: 'correctiveAction', label: 'Corrective action / sanction' },
    { field: 'employeeResponse', label: 'Employee response' },
    { field: 'hearingDate', label: 'Hearing / review date', type: 'date' },
    { field: 'outcome', label: 'Outcome / next step' },
    { field: 'status', label: 'Case status', control: 'select', options: ['DRAFT', 'ISSUED', 'EMPLOYEE_RESPONSE_PENDING', 'HEARING_SCHEDULED', 'CLOSED'] }
  ],
  timeOff: [
    { field: 'employeeName', label: 'Employee', control: 'datalist', optionSet: 'employees' },
    { field: 'type', label: 'Leave type', control: 'select', options: LEAVE_TYPE_OPTIONS },
    { field: 'startDate', label: 'Start date', type: 'date' },
    { field: 'endDate', label: 'End date', type: 'date' },
    { field: 'leaveBalance', label: 'Current leave balance', type: 'number', inputMode: 'decimal' },
    { field: 'workLogConflict', label: 'Work log conflict', control: 'select', options: ['No conflict found', 'Timesheet exists', 'Shift roster conflict', 'Attendance conflict'] },
    { field: 'status', label: 'Decision status', control: 'select', options: TIME_OFF_STATUS_OPTIONS },
    { field: 'reason', label: 'Reason' }
  ]
});

/**
 * @function readBrowserUser
 * @description Reads the current operator identity from Wilsy OS browser storage.
 * @returns {Object} Stored user packet.
 * @collaboration HR profile identity should reuse the OS session instead of hardcoding operator names.
 */
const readBrowserUser = () => {
  if (typeof window === 'undefined') return {};
  try {
    const raw = window.localStorage.getItem('wilsy_user') || window.localStorage.getItem('userData') || window.localStorage.getItem('user');
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
};

/**
 * @function resolveOperatorName
 * @description Resolves the HR operator display name from auth state and browser identity.
 * @param {Object} user - Authenticated user.
 * @returns {string} Operator display name.
 * @collaboration Every Wilsy OS dashboard must show the same operator profile signal.
 */
const resolveOperatorName = (user = {}) => (
  user?.name
  || user?.fullName
  || user?.displayName
  || [user?.firstName, user?.lastName].filter(Boolean).join(' ')
  || user?.email
  || 'HR Operator'
);

/**
 * @function isDateField
 * @description Determines whether an HR form field should open a calendar picker.
 * @param {string} field - Field name.
 * @returns {boolean} True when field is a date input.
 * @collaboration HR operators should select dates from a calendar instead of typing fragile free-form date strings.
 */
const isDateField = (field = '') => DATE_FIELD_NAMES.includes(field);

/**
 * @function normalizeDateInputValue
 * @description Converts stored HR date values into native date-input format.
 * @param {unknown} value - Raw value.
 * @returns {string} YYYY-MM-DD value or empty string.
 * @collaboration Native date pickers require strict input values while the backend may return ISO strings.
 */
const normalizeDateInputValue = (value) => {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value).slice(0, 10);
  return date.toISOString().slice(0, 10);
};

/**
 * @function splitEmployeeName
 * @description Splits an employee display name into first name and surname for controlled HR artifacts.
 * @param {string} value - Employee display name.
 * @returns {Object} First name and surname.
 * @collaboration HR contracts should collect explicit identity fields instead of relying on one loose display string.
 */
const splitEmployeeName = (value = '') => {
  const parts = String(value || '').trim().split(/\s+/).filter(Boolean);
  return {
    firstName: parts[0] || '',
    surname: parts.slice(1).join(' ')
  };
};

/**
 * @function isEmailLike
 * @description Detects when a display value is an email address rather than a human legal name.
 * @param {string} value - Candidate value.
 * @returns {boolean} True when the value looks like an email address.
 * @collaboration Contract packs must never turn a login email into an employee first name.
 */
const isEmailLike = (value = '') => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value || '').trim());

/**
 * @function resolveEmployeeContractIdentity
 * @description Resolves controlled artifact identity fields from an employee row without trusting display strings blindly.
 * @param {Object} employee - HR employee row.
 * @returns {Object} Contract identity packet.
 * @collaboration HR artifacts need real names, contacts and address proof instead of accidental session values.
 */
const resolveEmployeeContractIdentity = (employee = {}) => {
  const explicitFirstName = employee.firstName || employee.givenName || employee.forename || '';
  const explicitSurname = employee.surname || employee.lastName || employee.familyName || '';
  const displayName = employee.name || employee.employeeName || employee.fullName || '';
  const email = employee.personalEmail || employee.email || employee.workEmail || '';
  const identity = explicitFirstName || explicitSurname || !isEmailLike(displayName)
    ? {
      firstName: explicitFirstName || splitEmployeeName(displayName).firstName,
      surname: explicitSurname || splitEmployeeName(displayName).surname,
      employeeName: !isEmailLike(displayName) ? displayName : [explicitFirstName, explicitSurname].filter(Boolean).join(' ')
    }
    : { firstName: '', surname: '', employeeName: '' };
  return {
    ...identity,
    personalEmail: isEmailLike(email) ? email : '',
    cellphone: employee.cellphone || employee.phone || employee.mobile || '',
    address: employee.address || employee.residentialAddress || '',
    addressLatitude: employee.addressLatitude || employee.latitude || employee.locationCoordinates?.lat || '',
    addressLongitude: employee.addressLongitude || employee.longitude || employee.locationCoordinates?.lng || '',
    addressMapUrl: employee.addressMapUrl || employee.mapUrl || '',
    identityNumber: employee.identityNumber || employee.nationalId || employee.passportNumber || '',
    nationality: employee.nationality || employee.country || '',
    nationalityCode: employee.nationalityCode || employee.countryCode || resolveCountrySignal(employee.nationality || employee.country)?.code || ''
  };
};

/**
 * @function composeEmployeeName
 * @description Builds the employee contract name from controlled identity fields.
 * @param {Object} form - Artifact form state.
 * @returns {string} Employee name.
 * @collaboration The artifact payload should be derived from verified identity fields, not duplicated manual text.
 */
const composeEmployeeName = (form = {}) => [form.firstName, form.surname].filter(Boolean).join(' ').trim() || form.employeeName || '';

/**
 * @function buildGoogleMapsSearchUrl
 * @description Builds a Google Maps query URL for address confirmation and coordinate discovery.
 * @param {string} address - Human address.
 * @returns {string} Google Maps search URL.
 * @collaboration Wilsy OS can verify address posture without storing a Google API key in the client.
 */
const buildGoogleMapsSearchUrl = (address = '') => {
  const query = String(address || '').trim();
  return query ? `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}` : '';
};

/**
 * @function resolveCountrySignal
 * @description Resolves country/nationality form values into a standardized ISO-backed signal.
 * @param {string} value - Raw country or nationality value.
 * @returns {Object|null} Country signal or null.
 * @collaboration HR identity records should carry country proof that payroll, immigration and artifacts can reuse.
 */
const resolveCountrySignal = (value = '') => resolveCountryOption(value);

/**
 * @function buildAddressSuggestions
 * @description Builds map-verifiable address suggestions from the typed address and known jurisdiction anchors.
 * @param {string} value - Raw address text.
 * @param {string} countryValue - Selected nationality or country value.
 * @param {number} limit - Maximum suggestions.
 * @returns {Array<Object>} Address suggestion packets.
 * @collaboration Address entry should guide the operator toward map proof while refusing to pretend client-side guesses are verified addresses.
 */
const buildAddressSuggestions = (value = '', countryValue = '', limit = 5) => {
  const query = String(value || '').trim();
  if (query.length < 3) return [];
  const country = resolveCountrySignal(countryValue);
  const countryName = country?.name || 'South Africa';
  const localAnchors = ADDRESS_INTELLIGENCE_ANCHORS.filter(anchor => (
    anchor.country === countryName || countryName === 'South Africa'
  ));
  const matchingAnchors = localAnchors.filter(anchor => {
    const haystack = `${anchor.city} ${anchor.province} ${anchor.country}`.toLowerCase();
    return query.toLowerCase().split(/\s+/).some(part => part.length > 2 && haystack.includes(part));
  });
  const anchors = (matchingAnchors.length ? matchingAnchors : localAnchors).slice(0, limit);
  return anchors.map(anchor => {
    const label = query.toLowerCase().includes(anchor.city.toLowerCase())
      ? `${query}, ${anchor.province}, ${anchor.country}`
      : `${query}, ${anchor.city}, ${anchor.province}, ${anchor.country}`;
    return {
      id: `${anchor.city}-${anchor.province}-${query}`.replace(/\s+/g, '-').toLowerCase(),
      label,
      region: `${anchor.city}, ${anchor.province}`,
      latitude: anchor.lat,
      longitude: anchor.lng,
      mapUrl: buildGoogleMapsSearchUrl(label),
      source: 'MAP_QUERY_SUGGESTION',
      confidence: matchingAnchors.length ? 'CITY_MATCH' : 'JURISDICTION_ANCHOR'
    };
  });
};

/**
 * @function resolveAddressPosture
 * @description Resolves address verification posture, coordinate readiness and map handoff link.
 * @param {Object} form - HR form state.
 * @returns {Object} Address posture packet.
 * @collaboration Address capture should support maps, proof and coordinates instead of a dead text box.
 */
const resolveAddressPosture = (form = {}) => {
  const address = String(form.address || '').trim();
  const rawLatitude = String(form.addressLatitude ?? '').trim();
  const rawLongitude = String(form.addressLongitude ?? '').trim();
  const latitude = Number(rawLatitude);
  const longitude = Number(rawLongitude);
  const coordinatesReady = rawLatitude !== '' && rawLongitude !== '' && Number.isFinite(latitude) && Number.isFinite(longitude);
  const mapUrl = form.addressMapUrl || buildGoogleMapsSearchUrl(address);
  return {
    address,
    coordinatesReady,
    latitude: coordinatesReady ? latitude : null,
    longitude: coordinatesReady ? longitude : null,
    mapUrl,
    source: form.addressSuggestionSource || (form.addressVerifiedAt ? 'LIVE_MAP_HANDOFF' : 'OPERATOR_ENTRY'),
    status: address && coordinatesReady ? 'ADDRESS_COORDINATES_READY' : address ? 'ADDRESS_MAP_REVIEW' : 'ADDRESS_REQUIRED'
  };
};

/**
 * @function calculateBenefitMath
 * @description Calculates benefit plan monthly and annual exposure from HR form fields.
 * @param {Object} form - Benefit form.
 * @returns {Object} Benefit math.
 * @collaboration Benefits should show financial impact while HR is creating the plan, not after a spreadsheet export.
 */
const calculateBenefitMath = (form = {}) => {
  const eligibleEmployees = Math.max(Number(form.eligibleEmployees || 0), 0);
  const benefitPackage = resolveBenefitPackage(form.name || form.benefits);
  const packageEmployerDefault = benefitPackage.plans.reduce((total, plan) => total + Number(plan.employerDefault || 0), 0);
  const packageEmployeeDefault = benefitPackage.plans.reduce((total, plan) => total + Number(plan.employeeDefault || 0), 0);
  const employerContribution = Math.max(Number(form.employerContribution || form.employerBenefits || form.cost || packageEmployerDefault || 0), 0);
  const employeeContribution = Math.max(Number(form.employeeContribution || form.benefitDeductions || packageEmployeeDefault || 0), 0);
  const monthlyEmployerCost = employerContribution * Math.max(eligibleEmployees, 1);
  const monthlyEmployeeContribution = employeeContribution * Math.max(eligibleEmployees, 1);
  return {
    benefitPackage,
    packageItems: benefitPackage.items,
    eligibleEmployees,
    employerContribution,
    employeeContribution,
    monthlyEmployerCost,
    monthlyEmployeeContribution,
    annualEmployerCost: monthlyEmployerCost * 12,
    annualEmployeeContribution: monthlyEmployeeContribution * 12,
    totalMonthlyPlanValue: monthlyEmployerCost + monthlyEmployeeContribution,
    totalAnnualPlanValue: (monthlyEmployerCost + monthlyEmployeeContribution) * 12
  };
};

/**
 * @function validateSouthAfricanId
 * @description Runs a local checksum posture check for South African ID numbers.
 * @param {string} value - ID number.
 * @returns {boolean} True when checksum passes.
 * @collaboration HR must flag identity quality before access, while final verification can still be backed by an external identity provider.
 */
const validateSouthAfricanId = (value = '') => {
  const digits = String(value || '').replace(/\D/g, '');
  if (!/^\d{13}$/.test(digits)) return false;
  const check = Number(digits[12]);
  const oddSum = digits
    .slice(0, 12)
    .split('')
    .filter((_, index) => index % 2 === 0)
    .reduce((total, digit) => total + Number(digit), 0);
  const evenNumber = Number(digits.slice(0, 12).split('').filter((_, index) => index % 2 === 1).join('')) * 2;
  const evenSum = String(evenNumber).split('').reduce((total, digit) => total + Number(digit), 0);
  return (10 - ((oddSum + evenSum) % 10)) % 10 === check;
};

/**
 * @function resolveIdentityPosture
 * @description Resolves employee/candidate identity and right-to-work posture.
 * @param {Object} form - HR form state.
 * @returns {Object} Identity posture.
 * @collaboration Wilsy OS HR must make identity risk visible before employment access is granted.
 */
const resolveIdentityPosture = (form = {}) => {
  const idType = form.idType || 'South African ID';
  const isSouthAfricanId = idType === 'South African ID';
  const saIdValid = isSouthAfricanId ? validateSouthAfricanId(form.identityNumber) : false;
  const passportReady = !isSouthAfricanId && Boolean(String(form.passportNumber || '').trim());
  const visaRequired = ['Passport', 'Work visa'].includes(idType);
  const visaExpiry = form.visaExpiry ? new Date(form.visaExpiry) : null;
  const visaExpired = visaExpiry ? visaExpiry.getTime() < Date.now() : false;
  const verified = (isSouthAfricanId && saIdValid) || (passportReady && !visaExpired && String(form.rightToWorkStatus || '').toLowerCase().includes('verified'));
  return {
    idType,
    saIdValid,
    passportReady,
    visaRequired,
    visaExpired,
    verified,
    status: verified ? 'IDENTITY_READY' : 'IDENTITY_REVIEW_REQUIRED'
  };
};

/**
 * @function resolveRoleProfile
 * @description Resolves role duties, KPIs and disciplinary anchors.
 * @param {string} role - Selected role.
 * @returns {Object} Role profile.
 * @collaboration Role selection must carry performance and disciplinary meaning across HR workflows.
 */
const resolveRoleProfile = (role = '') => {
  const exact = ROLE_INTELLIGENCE_LIBRARY[role];
  if (exact) return { role, ...exact };
  const family = ROLE_FAMILY_PROFILES.find(profile => profile.match.test(role));
  if (family) {
    return {
      role: role || 'Role pending',
      department: family.department,
      duties: family.duties,
      kpis: family.kpis,
      disciplinaryAnchors: family.disciplinaryAnchors
    };
  }
  return {
    role: role || 'Role pending',
    department: 'Operations',
    duties: ['Execute assigned duties', 'Maintain accurate work evidence', 'Escalate blockers and risks'],
    kpis: ['Attendance', 'Task completion', 'Quality of work', 'Manager feedback'],
    disciplinaryAnchors: ['Failure to perform duties', 'Attendance breach', 'Policy non-compliance']
  };
};

/**
 * @function calculateWorkingDays
 * @description Calculates weekday leave days between two dates.
 * @param {string} startDate - Start date.
 * @param {string} endDate - End date.
 * @returns {number} Working day count.
 * @collaboration Leave approval must understand absence days before payroll and attendance conflicts are created.
 */
const calculateWorkingDays = (startDate, endDate) => {
  const start = new Date(startDate);
  const end = new Date(endDate || startDate);
  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime()) || end < start) return 0;
  let days = 0;
  const cursor = new Date(start);
  while (cursor <= end) {
    const day = cursor.getDay();
    if (day !== 0 && day !== 6) days += 1;
    cursor.setDate(cursor.getDate() + 1);
  }
  return days;
};

/**
 * @function calculateLeaveMath
 * @description Calculates leave impact and attendance conflict posture.
 * @param {Object} form - Time-off form.
 * @returns {Object} Leave math.
 * @collaboration HR should not approve absence blindly when payroll, attendance or work logs conflict.
 */
const calculateLeaveMath = (form = {}) => {
  const requestedDays = calculateWorkingDays(form.startDate, form.endDate);
  const leaveBalance = Number(form.leaveBalance || 0);
  const balanceAfter = leaveBalance - requestedDays;
  const conflict = !/no conflict/i.test(form.workLogConflict || 'No conflict found');
  return {
    requestedDays,
    leaveBalance,
    balanceAfter,
    conflict,
    status: conflict ? 'ATTENDANCE_CONFLICT' : balanceAfter < 0 ? 'INSUFFICIENT_BALANCE' : 'LEAVE_READY'
  };
};

/**
 * @function roundMoney
 * @description Rounds payroll values to cents for stable UI and payloads.
 * @param {number} value - Monetary value.
 * @returns {number} Rounded value.
 * @collaboration Payroll math must be deterministic before it reaches the backend engine.
 */
const roundMoney = (value = 0) => Math.round((Number(value) || 0) * 100) / 100;

/**
 * @function calculateZaAnnualTax
 * @description Calculates annual South African PAYE-style tax after primary rebate.
 * @param {number} annualTaxableIncome - Annual taxable income.
 * @returns {number} Annual tax.
 * @collaboration HR should preview South African employment tax before saving payroll.
 */
const calculateZaAnnualTax = (annualTaxableIncome = 0) => {
  const taxable = Math.max(Number(annualTaxableIncome) || 0, 0);
  const bracket = ZA_PAYROLL_2027.brackets.find(row => taxable <= row.upTo) || ZA_PAYROLL_2027.brackets[ZA_PAYROLL_2027.brackets.length - 1];
  return roundMoney(Math.max(0, bracket.base + ((taxable - bracket.threshold) * bracket.rate) - ZA_PAYROLL_2027.primaryRebate));
};

/**
 * @function resolvePayrollPayDate
 * @description Resolves payday from tenant-selected day or the Wilsy OS default of the 25th.
 * @param {Object} form - Payroll form.
 * @returns {string} YYYY-MM-DD pay date.
 * @collaboration Tenants can choose payroll day, while the default remains the 25th with weekend protection.
 */
const resolvePayrollPayDate = (form = {}) => {
  if (form.plannedPayDate) return normalizeDateInputValue(form.plannedPayDate);
  const now = new Date();
  const month = Number(form.payrollMonth || (now.getMonth() + 1));
  const year = Number(form.payrollYear || now.getFullYear());
  const payDay = Math.min(Math.max(Number(form.payDay || ZA_PAYROLL_2027.defaultPayDay), 1), 28);
  const date = new Date(Date.UTC(year, month - 1, payDay, 10, 0, 0));
  const weekday = date.getUTCDay();
  if (weekday === 6) date.setUTCDate(date.getUTCDate() - 1);
  if (weekday === 0) date.setUTCDate(date.getUTCDate() - 2);
  return date.toISOString().slice(0, 10);
};

/**
 * @function calculatePayrollMath
 * @description Calculates gross pay, PAYE, UIF, deductions, net salary and employer exposure.
 * @param {Object} form - Payroll form.
 * @returns {Object} Payroll math.
 * @collaboration Payroll needs real payslip math, not shallow card arithmetic.
 */
const calculatePayrollMath = (form = {}) => {
  const country = String(form.payrollCountry || 'ZA').toUpperCase();
  const benefitPackage = resolveBenefitPackage(form.benefits || form.name);
  const packageEmployerDefault = benefitPackage.plans.reduce((total, plan) => total + Number(plan.employerDefault || 0), 0);
  const packageEmployeeDefault = benefitPackage.plans.reduce((total, plan) => total + Number(plan.employeeDefault || 0), 0);
  const grossPay = roundMoney(form.grossPay || 0);
  const taxableIncome = roundMoney(Math.max(0, grossPay + Number(form.taxableBenefits || 0) - Number(form.preTaxDeductions || 0)));
  const employeeTax = country === 'ZA' ? roundMoney(calculateZaAnnualTax(taxableIncome * 12) / 12) : roundMoney(form.employeeTax || 0);
  const uifBase = Math.min(grossPay, ZA_PAYROLL_2027.uifMonthlyCeiling);
  const uifEmployee = country === 'ZA' ? roundMoney(uifBase * ZA_PAYROLL_2027.uifRate) : 0;
  const uifEmployer = country === 'ZA' ? roundMoney(uifBase * ZA_PAYROLL_2027.uifRate) : 0;
  const benefitDeductions = roundMoney(form.benefitDeductions || packageEmployeeDefault || 0);
  const otherDeductions = roundMoney(form.otherDeductions || form.deductions || 0);
  const statutoryDeductions = roundMoney(employeeTax + uifEmployee);
  const employerBenefits = roundMoney(form.employerBenefits || packageEmployerDefault || 0);
  const netPay = roundMoney(Math.max(0, grossPay - statutoryDeductions - benefitDeductions - otherDeductions));
  const employerExposure = roundMoney(grossPay + uifEmployer + employerBenefits);
  const totalDeductions = roundMoney(statutoryDeductions + benefitDeductions + otherDeductions);
  return {
    payrollCountry: country,
    taxYear: country === 'ZA' ? ZA_PAYROLL_2027.taxYear : 'TENANT_RULESET_REQUIRED',
    payDay: Number(form.payDay || ZA_PAYROLL_2027.defaultPayDay),
    plannedPayDate: resolvePayrollPayDate(form),
    grossPay,
    taxableIncome,
    employeeTax,
    uifEmployee,
    uifEmployer,
    statutoryDeductions,
    benefitDeductions,
    benefitPackage,
    otherDeductions,
    totalDeductions,
    employerBenefits,
    netPay,
    employerExposure,
    deductionRate: grossPay ? Math.round((totalDeductions / grossPay) * 100) : 0,
    payrollEngine: country === 'ZA' ? `SARS_PAYE_${ZA_PAYROLL_2027.taxYear}_UIF` : 'COUNTRY_RULESET_PENDING'
  };
};

/**
 * @function calculateArtifactRemunerationMath
 * @description Calculates contract-pack remuneration from base pay, variable pay, benefits and deductions.
 * @param {Object} form - Artifact form state.
 * @returns {Object} Payroll-ready remuneration packet.
 * @collaboration HR should review compensation math inside contracts before any document is printed.
 */
const calculateArtifactRemunerationMath = (form = {}) => {
  const benefitPackage = resolveBenefitPackage(form.benefits);
  const baseSalary = roundMoney(form.baseSalary || 0);
  const variablePay = roundMoney(form.variablePay || 0);
  const taxableBenefits = roundMoney(form.taxableBenefits || 0);
  const employerBenefits = roundMoney(form.employerBenefits || benefitPackage.plans.reduce((total, plan) => total + Number(plan.employerDefault || 0), 0));
  const benefitDeductions = roundMoney(form.benefitDeductions || benefitPackage.plans.reduce((total, plan) => total + Number(plan.employeeDefault || 0), 0));
  const grossPay = roundMoney(baseSalary + variablePay + taxableBenefits);
  const payroll = calculatePayrollMath({
    ...form,
    grossPay,
    taxableBenefits,
    benefitDeductions,
    employerBenefits,
    payrollCountry: form.payrollCountry || 'ZA',
    payDay: form.payDay || ZA_PAYROLL_2027.defaultPayDay
  });
  return {
    ...payroll,
    baseSalary,
    variablePay,
    taxableBenefits,
    benefitPackage,
    benefitPlan: benefitPackage,
    benefitPlanName: form.benefits || 'None',
    remunerationControl: grossPay > 0 ? 'REMUNERATION_REVIEW_READY' : 'REMUNERATION_REQUIRED'
  };
};

/**
 * @function resolveRoleTargets
 * @description Resolves role-specific performance target data.
 * @param {string} role - Role title.
 * @returns {Object} Role target packet.
 * @collaboration Goals must be role-aware so sales, mechanics, engineers and HR are not judged by generic checklists.
 */
const resolveRoleTargets = (role = '') => (
  ROLE_TARGET_LIBRARY[role]
  || ROLE_FAMILY_TARGETS.find(profile => profile.match.test(role))
  || ROLE_TARGET_LIBRARY.default
);

/**
 * @function resolveCompensationBand
 * @description Resolves an editable monthly salary planning band for the selected role.
 * @param {string} role - Role title.
 * @returns {Object} Monthly salary min and max.
 * @collaboration Hiring requisitions should start with a sensible band while HR still controls the final tenant-approved numbers.
 */
const resolveCompensationBand = (role = '') => (
  ROLE_COMPENSATION_BANDS.find(profile => profile.match.test(role))
  || { min: 12000, max: 45000 }
);

/**
 * @function calculatePerformanceMath
 * @description Calculates goal completion, productivity score and HR recommendation.
 * @param {Object} form - Performance review form.
 * @returns {Object} Performance math.
 * @collaboration Performance reviews should guide employees with evidence and targets, not just store ratings.
 */
const calculatePerformanceMath = (form = {}) => {
  const targets = resolveRoleTargets(form.roleTitle || form.position || form.title);
  const goalsMet = Number(form.goalsMet || 0);
  const goalsTotal = Number(form.goalsTotal || targets.targets.length || 0);
  const goalCompletion = goalsTotal ? Math.round((goalsMet / goalsTotal) * 100) : 0;
  const attendanceScore = Number(form.attendanceScore || 0);
  const taskScore = Number(form.taskScore || form.tasksCompleted || 0);
  const qualityScore = Number(form.qualityScore || 0);
  const customerScore = Number(form.customerScore || 0);
  const activityScore = Math.round((attendanceScore + taskScore + qualityScore + customerScore) / 4);
  const rating = Number(form.rating || 0);
  const productivityScore = Math.max(0, Math.min(100, Math.round(((rating / 5) * 40) + (goalCompletion * 0.4) + (activityScore * 0.2))));
  const recommendation = form.managerRecommendation || (
    productivityScore >= 80
      ? 'Recognize strong performance and consider incentive, promotion or retention path.'
      : productivityScore >= 55
        ? targets.recommendation
        : 'Open a performance improvement plan with dated targets, manager support and weekly evidence review.'
  );
  return { targets, goalsMet, goalsTotal, goalCompletion, activityScore, productivityScore, recommendation };
};

/**
 * @function buildDefaultFormState
 * @description Creates process-specific default form values.
 * @param {string} type - HR modal type.
 * @param {Object|null} item - Existing item.
 * @param {Object} context - Current HR context.
 * @returns {Object} Form state.
 * @collaboration Defaults should reduce typing by using the OS context already available.
 */
const buildDefaultFormState = (type = 'employee', item = null, context = {}) => {
  if (item) return item;
  const firstEmployee = context.employees?.[0] || {};
  const now = new Date();
  const currentPeriod = now.toLocaleDateString('en-ZA', { month: 'long', year: 'numeric' });
  const defaults = {
    employee: { status: 'ACTIVE', department: 'Executive', manager: context.operatorName, idType: 'South African ID', nationality: 'South Africa', nationalityCode: 'ZA', payrollCountry: 'ZA', rightToWorkStatus: 'Pending verification', leaveEntitlement: 15 },
    candidate: { stage: 'New', status: 'ACTIVE', position: context.openRoles?.[0]?.title || 'Operations Coordinator', idType: 'South African ID', nationality: 'South Africa', nationalityCode: 'ZA', rightToWorkStatus: 'Pending verification' },
    jobOpening: {
      title: context.openRoles?.[0]?.title || 'Operations Coordinator',
      status: 'Draft',
      priority: 'Normal',
      location: 'Hybrid',
      headcount: 1,
      department: 'Operations',
      salaryMin: resolveCompensationBand(context.openRoles?.[0]?.title || 'Operations Coordinator').min,
      salaryMax: resolveCompensationBand(context.openRoles?.[0]?.title || 'Operations Coordinator').max
    },
    payroll: {
      employeeId: firstEmployee.id || firstEmployee.employeeId || '',
      employeeName: firstEmployee.name || firstEmployee.employeeName || firstEmployee.email || '',
      email: firstEmployee.email || '',
      department: firstEmployee.department || '',
      position: firstEmployee.position || '',
      payrollCountry: 'ZA',
      benefits: firstEmployee.benefits || 'Standard Employee Pack',
      period: currentPeriod,
      payrollMonth: now.getMonth() + 1,
      payrollYear: now.getFullYear(),
      payDay: context.payDay || ZA_PAYROLL_2027.defaultPayDay,
      plannedPayDate: resolvePayrollPayDate({ payrollMonth: now.getMonth() + 1, payrollYear: now.getFullYear(), payDay: context.payDay || ZA_PAYROLL_2027.defaultPayDay }),
      status: 'DRAFT',
      grossPay: 0,
      taxableBenefits: 0,
      preTaxDeductions: 0,
      benefitDeductions: 0,
      otherDeductions: 0,
      employerBenefits: 0,
      netPay: 0
    },
    benefit: { name: 'Standard Employee Pack', provider: 'Wilsy OS Benefits Vault', status: 'Pending approval', coverage: 'Employee only', eligibilityRule: 'All active employees', waitingPeriod: 'After probation', taxable: 'Payroll review required', payrollDeductionCode: 'BEN-STD-EMP', eligibleEmployees: context.employeeCount || 1, employerContribution: 0, employeeContribution: 0, cost: 0 },
    performanceReview: {
      employeeId: firstEmployee.id || firstEmployee.employeeId || '',
      employeeName: firstEmployee.name || firstEmployee.employeeName || firstEmployee.email || '',
      reviewerName: context.operatorName,
      roleTitle: firstEmployee.position || firstEmployee.title || 'Operations Coordinator',
      rating: '3',
      period: currentPeriod,
      goalsMet: 0,
      goalsTotal: 4,
      attendanceScore: 75,
      taskScore: 75,
      qualityScore: 75,
      customerScore: 75,
      disciplinaryRisk: 'None',
      status: 'Draft'
    },
    employeeWorkLog: {
      employeeId: firstEmployee.id || firstEmployee.employeeId || '',
      employeeName: firstEmployee.name || firstEmployee.employeeName || firstEmployee.email || '',
      workDate: now.toISOString().slice(0, 10),
      workType: 'Daily work',
      achievementType: WORK_LOG_TYPE_WORKFLOWS['Daily work'].achievementType,
      impactScore: 50,
      performanceScore: 50,
      status: 'RECORDED'
    },
    employeeRelations: {
      employeeId: firstEmployee.id || firstEmployee.employeeId || '',
      employeeName: firstEmployee.name || firstEmployee.employeeName || firstEmployee.email || '',
      relationsActionType: 'Verbal warning',
      incidentDate: now.toISOString().slice(0, 10),
      hearingDate: '',
      status: 'DRAFT'
    },
    timeOff: { employeeName: firstEmployee.name || '', type: 'Annual leave', status: 'Pending' }
  };
  return defaults[type] || {};
};

/**
 * @function normalizeMutationPayload
 * @description Adds computed HR fields before persisting a mutation.
 * @param {string} type - HR modal type.
 * @param {Object} form - Form state.
 * @returns {Object} Backend payload.
 * @collaboration Persisted rows should contain useful derived values such as benefit exposure and payroll net pay.
 */
const normalizeMutationPayload = (type = 'employee', form = {}) => {
  if (type === 'employee') {
    const roleProfile = resolveRoleProfile(form.position);
    const identityPosture = resolveIdentityPosture(form);
    const addressPosture = resolveAddressPosture(form);
    const countrySignal = resolveCountrySignal(form.nationality || form.nationalityCode || form.countryCode);
    return {
      ...form,
      nationality: countrySignal?.name || form.nationality || '',
      nationalityCode: countrySignal?.code || form.nationalityCode || '',
      countryCode: countrySignal?.code || form.countryCode || '',
      department: form.department || roleProfile.department,
      identityPosture,
      addressPosture,
      countrySignal,
      roleProfile,
      metadata: {
        ...(form.metadata || {}),
        identityPosture,
        addressPosture,
        countrySignal,
        roleProfile
      }
    };
  }
  if (type === 'candidate') {
    const roleProfile = resolveRoleProfile(form.position);
    const identityPosture = resolveIdentityPosture(form);
    const addressPosture = resolveAddressPosture(form);
    const countrySignal = resolveCountrySignal(form.nationality || form.nationalityCode || form.countryCode);
    const stageWorkflow = RECRUITING_STAGE_WORKFLOWS[form.stage] || RECRUITING_STAGE_WORKFLOWS.New;
    return {
      ...form,
      nationality: countrySignal?.name || form.nationality || '',
      nationalityCode: countrySignal?.code || form.nationalityCode || '',
      countryCode: countrySignal?.code || form.countryCode || '',
      identityPosture,
      addressPosture,
      countrySignal,
      roleProfile,
      stageWorkflow,
      metadata: {
        ...(form.metadata || {}),
        identityPosture,
        addressPosture,
        countrySignal,
        roleProfile,
        stageWorkflow
      }
    };
  }
  if (type === 'benefit') {
    const benefitMath = calculateBenefitMath(form);
    const benefitPlan = resolveBenefitPackage(form.name);
    return {
      ...form,
      ...benefitMath,
      name: benefitPlan.name,
      provider: form.provider || benefitPlan.provider || '',
      coverage: form.coverage || benefitPlan.coverage || '',
      eligibilityRule: form.eligibilityRule || benefitPlan.eligibilityRule || '',
      waitingPeriod: form.waitingPeriod || benefitPlan.waitingPeriod || '',
      taxable: form.taxable || benefitPlan.taxable || 'Payroll review required',
      payrollDeductionCode: form.payrollDeductionCode || benefitPlan.payrollDeductionCode || '',
      cost: benefitMath.monthlyEmployerCost,
      metadata: {
        ...(form.metadata || {}),
        benefitMath,
        benefitPlan,
        payrollControl: {
          deductionCode: form.payrollDeductionCode || '',
          taxable: form.taxable || 'Payroll review required',
          eligibilityRule: form.eligibilityRule || ''
        }
      }
    };
  }
  if (type === 'payroll') {
    const payrollMath = calculatePayrollMath(form);
    return {
      ...form,
      ...payrollMath,
      status: form.status || 'DRAFT',
      payrollGateStatus: form.payrollGateStatus || 'PAYROLL_GATE_PENDING_SERVER_VERIFICATION',
      metadata: {
        ...(form.metadata || {}),
        payrollMath,
        benefitPackage: payrollMath.benefitPackage,
        payrollControls: {
          defaultPayDay: ZA_PAYROLL_2027.defaultPayDay,
          plannedPayDate: payrollMath.plannedPayDate,
          engine: payrollMath.payrollEngine
        }
      }
    };
  }
  if (type === 'jobOpening') {
    const roleProfile = resolveRoleProfile(form.title || form.position);
    return {
      ...form,
      title: form.title || form.position || '',
      headcount: Number(form.headcount || 1),
      salaryMin: Number(form.salaryMin || 0),
      salaryMax: Number(form.salaryMax || 0),
      roleProfile,
      metadata: {
        ...(form.metadata || {}),
        roleProfile
      }
    };
  }
  if (type === 'performanceReview') {
    const roleProfile = resolveRoleProfile(form.roleTitle || form.position);
    const performanceMath = calculatePerformanceMath(form);
    return {
      ...form,
      rating: Number(form.rating || 0),
      goalsMet: performanceMath.goalsMet,
      goalsTotal: performanceMath.goalsTotal,
      goalCompletion: performanceMath.goalCompletion,
      activityScore: performanceMath.activityScore,
      productivityScore: performanceMath.productivityScore,
      recommendation: performanceMath.recommendation,
      managerRecommendation: form.managerRecommendation || performanceMath.recommendation,
      roleTargets: performanceMath.targets,
      roleProfile,
      metadata: {
        ...(form.metadata || {}),
        roleProfile,
        performanceMath
      }
    };
  }
  if (type === 'employeeWorkLog') {
    return {
      ...form,
      impactScore: Number(form.impactScore || 0),
      performanceScore: Number(form.performanceScore || 0),
      metadata: {
        ...(form.metadata || {}),
        evidenceCapturedAt: new Date().toISOString(),
        activityControl: 'DAILY_EMPLOYEE_EVIDENCE'
      }
    };
  }
  if (type === 'employeeRelations') {
    return {
      ...form,
      relationsActionType: form.relationsActionType || 'Employee relations action',
      status: form.status || 'DRAFT',
      metadata: {
        ...(form.metadata || {}),
        relationsControl: 'EMPLOYEE_RELATIONS_EVIDENCE',
        evidenceCapturedAt: new Date().toISOString()
      }
    };
  }
  if (type === 'timeOff') {
    const leaveMath = calculateLeaveMath(form);
    return {
      ...form,
      ...leaveMath,
      metadata: {
        ...(form.metadata || {}),
        leaveMath
      }
    };
  }
  return form;
};

/**
 * @function validateArtifactForm
 * @description Validates minimum HR controls before generating HR artifacts.
 * @param {Object} form - Artifact form state.
 * @returns {Array<string>} Missing field labels.
 * @collaboration Multi-billion-dollar OS access requires traceable identity while artifact-specific controls keep legal documents usable.
 */
const validateArtifactForm = (form = {}) => {
  const identityFields = [
    ['firstName', 'First name'],
    ['surname', 'Surname'],
    ['cellphone', 'Cellphone number'],
    ['address', 'Residential address']
  ];
  const appointmentFields = [
    ['roleTitle', 'Role / appointment title'],
    ['department', 'Department'],
    ['startDate', 'Start date'],
    ['employmentType', 'Employment type'],
    ['baseSalary', 'Base remuneration']
  ];
  const relationsFields = [
    ['relationsActionType', 'Employee-relations action'],
    ['incidentDate', 'Incident date'],
    ['policyBreach', 'Policy breach'],
    ['incidentSummary', 'Incident summary'],
    ['correctiveAction', 'Corrective action']
  ];
  const requiredFields = [
    ...identityFields,
    ...(isEmployeeRelationsArtifact(form.artifactType) ? relationsFields : appointmentFields)
  ];
  return requiredFields
    .filter(([field]) => !String(form[field] || '').trim())
    .map(([, label]) => label);
};

/**
 * @function isEmployeeRelationsArtifact
 * @description Detects artifacts that need incident, hearing, warning or dismissal evidence controls.
 * @param {string} artifactType - Artifact type.
 * @returns {boolean} True when employee-relations controls are required.
 * @collaboration Employee-relations documents must be evidence-led without cluttering ordinary contract generation.
 */
const isEmployeeRelationsArtifact = (artifactType = '') => /warning|suspension|dismissal|disciplinary|performance/i.test(String(artifactType || ''));

/**
 * @function downloadHtmlArtifact
 * @description Opens and downloads a generated printable HR artifact.
 * @param {Object} artifact - Artifact response.
 * @returns {void}
 * @collaboration HR should review remuneration in-browser before printing while still receiving a saved artifact file.
 */
const downloadHtmlArtifact = (artifact = {}) => {
  if (typeof window === 'undefined' || !artifact.content) return;
  const blob = new Blob([artifact.content], { type: 'text/html;charset=utf-8' });
  const url = window.URL.createObjectURL(blob);
  const handoff = window.open(url, '_blank', 'noopener,noreferrer');
  if (!handoff) {
    const link = document.createElement('a');
    link.href = url;
    link.download = artifact.filename || 'WILSY_HR_ARTIFACT.html';
    document.body.appendChild(link);
    link.click();
    link.remove();
  }
  window.setTimeout(() => window.URL.revokeObjectURL(url), 120000);
};

/**
 * @function createEmptySnapshot
 * @description Creates a source-honest HR snapshot before the backend ledger answers.
 * @returns {Object} Empty HR snapshot.
 * @collaboration Empty state should read as pending source, not as invented workforce data.
 */
const createEmptySnapshot = () => ({
  sourceStatus: 'HR_LEDGER_PENDING',
  summary: {},
  timestamp: null
});

/**
 * @function normalizeDataset
 * @description Normalizes HR API payloads into a stable paginated dataset.
 * @param {Object} payload - HR service response.
 * @param {Object} page - Requested page.
 * @returns {Object} Normalized dataset.
 * @collaboration HR views need consistent pagination even when a source returns a lean payload.
 */
const normalizeDataset = (payload = {}, page = DEFAULT_PAGE) => {
  const items = Array.isArray(payload?.items) ? payload.items : Array.isArray(payload?.data) ? payload.data : [];
  const total = Number(payload?.total ?? items.length);
  const limit = Number(payload?.limit ?? page.limit);
  const offset = Number(payload?.offset ?? page.offset);
  return {
    items,
    total: Number.isFinite(total) ? total : items.length,
    limit: Number.isFinite(limit) ? limit : page.limit,
    offset: Number.isFinite(offset) ? offset : page.offset,
    hasMore: Boolean(payload?.hasMore ?? (offset + limit < total))
  };
};

/**
 * @function resolveHrErrorFeedback
 * @description Converts API errors into honest HR cockpit feedback instead of blaming the wrong source.
 * @param {Error} error - Axios or local source error.
 * @param {string} fallbackTitle - Default feedback title.
 * @returns {Object} Feedback packet.
 * @collaboration Expired identity must read as a session problem, not as a fake HR ledger outage.
 */
const resolveHrErrorFeedback = (error = {}, fallbackTitle = 'HR source pending') => {
  const detail = error?.response?.data?.message || error?.message || 'HR source failed.';
  if (/jwt expired|token expired|expired token|session expired/i.test(detail)) {
    return {
      tone: 'risk',
      title: 'Session expired',
      detail: 'Wilsy OS identity expired. Sign in again so HR can reopen the live ledger.'
    };
  }
  return {
    tone: 'warning',
    title: fallbackTitle,
    detail
  };
};

/**
 * @function formatMoney
 * @description Formats payroll and benefits values for South African HR operations.
 * @param {number|null} value - Numeric value.
 * @returns {string} Currency string.
 * @collaboration Compensation surfaces must be readable without pretending absent values are live.
 */
const formatMoney = (value) => {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return 'R 0';
  return new Intl.NumberFormat('en-ZA', { style: 'currency', currency: 'ZAR', maximumFractionDigits: 0 }).format(numeric);
};

/**
 * @function formatCount
 * @description Formats count metrics for compact HR KPI display.
 * @param {number|null} value - Numeric count.
 * @returns {string} Count string.
 * @collaboration KPI values should stay stable and scannable across all HR lanes.
 */
const formatCount = (value) => {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric.toLocaleString('en-ZA') : '0';
};

/**
 * @function getSummaryMetric
 * @description Reads a metric from the HR snapshot summary.
 * @param {Object} snapshot - HR snapshot.
 * @param {string} type - HR record type.
 * @param {string} key - Metric key.
 * @returns {number} Numeric metric.
 * @collaboration Snapshot summary keeps top-level KPIs synchronized with backend truth.
 */
const getSummaryMetric = (snapshot = {}, type = '', key = 'total') => Number(snapshot.summary?.[type]?.[key] || 0);

/**
 * @function getTabConfig
 * @description Resolves the active HR tab config.
 * @param {string} activeTab - Active tab id.
 * @returns {Object} HR tab config.
 * @collaboration Central tab config keeps navigation, modal and process behavior aligned.
 */
const getTabConfig = (activeTab = 'employees') => HR_TABS.find(tab => tab.id === activeTab) || HR_TABS[0];

/**
 * @function formatModalTypeLabel
 * @description Converts HR modal types into operator-readable labels.
 * @param {string} type - Modal type.
 * @returns {string} Display label.
 * @collaboration HR users should see business language, not JavaScript identifier names.
 */
const formatModalTypeLabel = (type = 'employee') => ({
  employee: 'Employee',
  candidate: 'Candidate',
  jobOpening: 'Job Opening',
  payroll: 'Payroll Run',
  benefit: 'Benefit Plan',
  performanceReview: 'Performance Review',
  employeeWorkLog: 'Employee Activity',
  employeeRelations: 'Employee Relations',
  timeOff: 'Time Off Request'
}[type] || type);

/**
 * @function buildHrWorkspace
 * @description Builds the active HR operating workspace from live datasets and snapshot metrics.
 * @param {Object} params - Workspace inputs.
 * @returns {Object} Workspace model.
 * @collaboration Every HR nav item must change the process and business value, not repaint the same table.
 */
const buildHrWorkspace = ({ activeTab, snapshot, datasets, telemetryCount }) => {
  const employees = Math.max(
    getSummaryMetric(snapshot, 'employee'),
    Number(datasets.employees.total || 0),
    datasets.employees.items.length
  );
  const candidates = getSummaryMetric(snapshot, 'candidate');
  const openings = getSummaryMetric(snapshot, 'jobOpening');
  const payrollNet = getSummaryMetric(snapshot, 'payroll', 'netPay');
  const benefits = getSummaryMetric(snapshot, 'benefit');
  const rating = getSummaryMetric(snapshot, 'performanceReview', 'avgRating');
  const timeOffOpen = getSummaryMetric(snapshot, 'timeOff', 'open');
  const departments = Math.max(
    getSummaryMetric(snapshot, 'employee', 'departments'),
    new Set(datasets.employees.items.map(item => item.department).filter(Boolean)).size
  );
  const models = {
    employees: {
      kicker: 'Workforce Command',
      title: 'People Roster',
      description: 'Know who works here, where they sit, who manages them and what workforce records need action.',
      primary: 'Add Employee',
      kpis: [
        ['Employees', employees, 'Active people in HR ledger'],
        ['Departments', departments, 'Distinct operating domains'],
        ['Telemetry', telemetryCount, 'HR events in live stream']
      ],
      process: ['Verify headcount', 'Assign missing departments', 'Review manager coverage', 'Export workforce roster']
    },
    candidates: {
      kicker: 'Hiring Pipeline',
      title: 'Candidate Command',
      description: 'Move candidates through screening, interview, offer and rejection without losing stage accountability.',
      primary: 'Add Candidate',
      kpis: [
        ['Candidates', candidates, 'People in recruiting pipeline'],
        ['Interviews', datasets.candidates.items.filter(item => /interview/i.test(item.stage || item.status || '')).length, 'Interview-stage candidates'],
        ['Open Roles', openings, 'Roles requiring capacity']
      ],
      process: ['Screen new candidates', 'Schedule interviews', 'Prepare offers', 'Close rejected candidates']
    },
    jobOpenings: {
      kicker: 'Capacity Planning',
      title: 'Open Roles',
      description: 'See which roles are approved, blocked, urgent and tied to hiring pipeline pressure.',
      primary: 'Add Role',
      kpis: [
        ['Open Roles', openings, 'Hiring demand'],
        ['Urgent Roles', datasets.jobOpenings.items.filter(item => /urgent|high/i.test(item.priority || '')).length, 'Priority hiring pressure'],
        ['Candidates', candidates, 'Available recruiting supply']
      ],
      process: ['Approve role scope', 'Assign recruiter', 'Review compensation band', 'Publish or pause opening']
    },
    payroll: {
      kicker: 'Payroll Control',
      title: 'Payroll And Payslips',
      description: 'Run salary on the tenant pay day, calculate PAYE/UIF, block ghost employees, and issue proofed payslips.',
      primary: 'Create Payroll',
      kpis: [
        ['Payroll Records', getSummaryMetric(snapshot, 'payroll'), 'Compensation rows'],
        ['Net Pay', formatMoney(payrollNet), 'Total net payroll'],
        ['PAYE / UIF', formatMoney(getSummaryMetric(snapshot, 'payroll', 'statutoryDeductions')), 'Statutory deductions'],
        ['Employer Exposure', formatMoney(getSummaryMetric(snapshot, 'payroll', 'employerExposure')), 'Gross plus employer costs']
      ],
      process: ['Create payroll run', 'Review identity holds', 'Generate payslips', 'Export payroll evidence']
    },
    benefits: {
      kicker: 'Benefits Command',
      title: 'Employee Coverage',
      description: 'Manage benefit plans, coverage states and cost exposure without spreadsheet drift.',
      primary: 'Add Benefit',
      kpis: [
        ['Benefits', benefits, 'Coverage plans'],
        ['Monthly Cost', formatMoney(datasets.benefits.items.reduce((total, item) => total + Number(item.cost || 0), 0)), 'Known benefit cost'],
        ['Active Plans', datasets.benefits.items.filter(item => /active/i.test(item.status || '')).length, 'Live coverage']
      ],
      process: ['Review active plans', 'Check uncovered staff', 'Approve plan changes', 'Export benefits ledger']
    },
    performance: {
      kicker: 'Performance Matrix',
      title: 'Performance Intelligence',
      description: 'Review role goals, daily evidence, productivity score and recommendations before coaching or discipline.',
      primary: 'Add Review',
      kpis: [
        ['Reviews', getSummaryMetric(snapshot, 'performanceReview'), 'Performance records'],
        ['Average Rating', rating ? rating.toFixed(1) : '0.0', 'Review average'],
        ['Productivity', formatCount(getSummaryMetric(snapshot, 'performanceReview', 'productivityScore')), 'Average productivity score']
      ],
      process: ['Review role goals', 'Inspect activity evidence', 'Approve development plan', 'Export talent evidence']
    },
    activity: {
      kicker: 'Employee Activity',
      title: 'Daily Evidence Ledger',
      description: 'Record work done, achievements, incidents, customer outcomes and evidence so HR can understand productivity.',
      primary: 'Add Activity',
      kpis: [
        ['Activity Rows', getSummaryMetric(snapshot, 'employeeWorkLog'), 'Work evidence records'],
        ['Impact', datasets.activity.items.reduce((total, item) => total + Number(item.impactScore || 0), 0), 'Visible work impact'],
        ['Verified', datasets.activity.items.filter(item => /verified/i.test(item.status || '')).length, 'Manager-verified evidence']
      ],
      process: ['Record daily work', 'Verify manager evidence', 'Review productivity signals', 'Export activity proof']
    },
    relations: {
      kicker: 'Employee Relations',
      title: 'Warnings And Discipline',
      description: 'Issue verbal warnings, written warnings, hearings, suspensions and dismissal evidence with a defensible record trail.',
      primary: 'Add Relations Case',
      kpis: [
        ['Cases', getSummaryMetric(snapshot, 'employeeRelations'), 'Employee-relations records'],
        ['Open Cases', datasets.relations.items.filter(item => !/closed/i.test(item.status || '')).length, 'Requires HR action'],
        ['Issued', datasets.relations.items.filter(item => /issued|hearing|closed/i.test(item.status || '')).length, 'Formal actions issued']
      ],
      process: ['Issue verbal warning', 'Issue written warning', 'Schedule disciplinary hearing', 'Generate dismissal pack']
    },
    timeoff: {
      kicker: 'Absence Command',
      title: 'Leave And Coverage',
      description: 'Approve absence requests while seeing workforce coverage and pending leave pressure.',
      primary: 'Add Time Off',
      kpis: [
        ['Requests', getSummaryMetric(snapshot, 'timeOff'), 'Absence records'],
        ['Pending', timeOffOpen, 'Open approvals'],
        ['Approved', datasets.timeoff.items.filter(item => /approved/i.test(item.status || '')).length, 'Confirmed absences']
      ],
      process: ['Approve pending leave', 'Deny risky overlaps', 'Check team coverage', 'Export absence ledger']
    },
    artifacts: {
      kicker: 'HR Artifact Command',
      title: 'Contracts And Letters',
      description: 'Generate employment contracts, appointment letters, remuneration addenda and HR evidence from live people records.',
      primary: 'Generate Artifact',
      kpis: [
        ['Generated', getSummaryMetric(snapshot, 'hrArtifact'), 'HR artifacts sealed in the ledger'],
        ['Templates', HR_ARTIFACT_TYPES.length, 'HR-only artifact types'],
        ['Employees', employees, 'Available people source']
      ],
      process: ['Generate employment contract', 'Generate appointment letter', 'Review remuneration addendum', 'Export artifact ledger']
    }
  };
  return models[activeTab] || models.employees;
};

/**
 * @function HrDashboard
 * @description Renders the Wilsy OS HR operating suite with live people, hiring, payroll, performance and time-off workflows.
 * @returns {JSX.Element} HR operating dashboard.
 * @collaboration Wilson mandated HR must become a usable business operating surface, not a static data table.
 */
const HrDashboard = () => {
  const { activeTenant } = useTenants();
  const auth = useAuth() || {};
  const { user: authUser, logout } = auth;
  const user = authUser || readBrowserUser();
  const tenantId = activeTenant?.tenantId || activeTenant?.id || DEFAULT_TENANT_ID;
  const [activeTab, setActiveTab] = useState('employees');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [showProfilePanel, setShowProfilePanel] = useState(false);
  const [showArtifactModal, setShowArtifactModal] = useState(false);
  const [artifactCatalog, setArtifactCatalog] = useState(HR_ARTIFACT_TYPES);
  const [artifactForm, setArtifactForm] = useState(ARTIFACT_FORM_DEFAULTS);
  const [feedback, setFeedback] = useState({ tone: 'ready', title: 'HR Ready', detail: 'People operating system is listening.' });
  const [isRailOpen, setIsRailOpen] = useState(true);
  const [profileRuntime, setProfileRuntime] = useState({
    mode: {
      selectedMode: typeof window !== 'undefined' ? (window.localStorage.getItem('wilsy_profile_mode_v2') || 'day') : 'day',
      resolvedMode: typeof document !== 'undefined' ? (document.documentElement.dataset.wilsyResolvedMode || 'night') : 'night'
    },
    theme: {
      id: 'sovereign-gold',
      label: 'Sovereign Gold',
      color: typeof document !== 'undefined' ? (document.documentElement.style.getPropertyValue('--wilsy-os-accent') || '#d4af37') : '#d4af37'
    }
  });
  const [snapshot, setSnapshot] = useState(createEmptySnapshot);
  const [datasets, setDatasets] = useState(DATASET_DEFAULTS);
  const [pageStates, setPageStates] = useState({
    employees: { ...DEFAULT_PAGE },
    candidates: { ...DEFAULT_PAGE },
    jobOpenings: { ...DEFAULT_PAGE },
    payroll: { ...DEFAULT_PAGE },
    benefits: { ...DEFAULT_PAGE },
    performance: { ...DEFAULT_PAGE },
    activity: { ...DEFAULT_PAGE },
    relations: { ...DEFAULT_PAGE },
    timeoff: { ...DEFAULT_PAGE },
    artifacts: { ...DEFAULT_PAGE }
  });
  const [showModal, setShowModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [modalType, setModalType] = useState('employee');
  const [formState, setFormState] = useState({});
  const { events: telemetryEvents = [] } = useTelemetryFeed(tenantId);
  const hrActivities = useMemo(() => telemetryEvents.filter(event => String(event.eventType || '').toUpperCase().includes('HR')).slice(0, 8), [telemetryEvents]);
  const activeConfig = getTabConfig(activeTab);
  const workspace = useMemo(() => buildHrWorkspace({ activeTab, snapshot, datasets, telemetryCount: hrActivities.length }), [activeTab, datasets, hrActivities.length, snapshot]);
  const operatorName = resolveOperatorName(user);
  const activeArtifactTemplate = ARTIFACT_TEMPLATE_GUIDANCE[artifactForm.artifactType] || ARTIFACT_TEMPLATE_GUIDANCE.employment_contract;
  const artifactRequiresRelations = isEmployeeRelationsArtifact(artifactForm.artifactType);
  const roleOptions = useMemo(() => uniqueOptions(
    ROLE_OPTIONS,
    datasets.jobOpenings.items.map(item => item.title || item.name),
    datasets.employees.items.map(item => item.position || item.title)
  ), [datasets.employees.items, datasets.jobOpenings.items]);
  const departmentOptions = useMemo(() => uniqueOptions(
    DEPARTMENT_OPTIONS,
    datasets.employees.items.map(item => item.department),
    datasets.jobOpenings.items.map(item => item.department)
  ), [datasets.employees.items, datasets.jobOpenings.items]);
  const managerOptions = useMemo(() => {
    const managementRows = datasets.employees.items.filter(item => (
      /founder|chief|executive|director|head|manager|lead|supervisor/i.test(`${item.position || ''} ${item.role || ''} ${item.department || ''}`)
    ));
    return uniqueOptions(
      [operatorName],
      managementRows.map(item => item.name || item.employeeName || item.email),
      datasets.employees.items.map(item => item.manager || item.reportingLine)
    );
  }, [datasets.employees.items, operatorName]);
  const employeeOptions = useMemo(() => uniqueOptions(
    datasets.employees.items.map(item => item.name || item.employeeName || item.email),
    [operatorName]
  ), [datasets.employees.items, operatorName]);
  const benefitMath = useMemo(() => calculateBenefitMath(formState), [formState]);
  const identityPosture = useMemo(() => resolveIdentityPosture(formState), [formState]);
  const roleProfile = useMemo(() => resolveRoleProfile(formState.position || formState.title || formState.roleTitle), [formState.position, formState.roleTitle, formState.title]);
  const candidateStageWorkflow = useMemo(() => RECRUITING_STAGE_WORKFLOWS[formState.stage] || RECRUITING_STAGE_WORKFLOWS.New, [formState.stage]);
  const leaveMath = useMemo(() => calculateLeaveMath(formState), [formState]);
  const payrollMath = useMemo(() => calculatePayrollMath(formState), [formState]);
  const performanceMath = useMemo(() => calculatePerformanceMath(formState), [formState]);
  const selectedBenefitPlan = useMemo(() => resolveBenefitPackage(formState.name || formState.benefits), [formState.benefits, formState.name]);
  const artifactRemunerationMath = useMemo(() => calculateArtifactRemunerationMath(artifactForm), [artifactForm]);
  const artifactAddressPosture = useMemo(() => resolveAddressPosture(artifactForm), [artifactForm]);
  const getFieldOptions = useCallback((config = {}) => {
    if (config.optionSet === 'roles') return roleOptions;
    if (config.optionSet === 'departments') return departmentOptions;
    if (config.optionSet === 'managers') return managerOptions;
    if (config.optionSet === 'employees') return employeeOptions;
    return config.options || [];
  }, [departmentOptions, employeeOptions, managerOptions, roleOptions]);

  /**
   * @function useEffect
   * @description Hydrates shared Wilsy OS profile runtime tokens before the HR profile panel opens.
   * @returns {undefined} React cleanup placeholder.
   * @collaboration HR must inherit the same account, accent and day-night settings as Executive instead of becoming a separate island.
   */
  useEffect(() => {
    const runtime = hydrateWilsyProfileRuntime({
      defaultAccent: activeTenant?.branding?.accentColor
        || activeTenant?.branding?.primaryColor
        || activeTenant?.themeColor
        || '#d4af37'
    });
    setProfileRuntime(runtime);

    /**
     * @function handleProfileModeRuntime
     * @description Mirrors global profile mode changes into the HR shell runtime state.
     * @param {CustomEvent} event - Shared Wilsy profile mode event.
     * @returns {void}
     * @collaboration HR must react to profile mode changes with the same deterministic shell contract as Executive.
     */
    const handleProfileModeRuntime = (event = {}) => {
      setProfileRuntime(previous => ({
        ...previous,
        mode: event.detail || previous.mode
      }));
    };

    /**
     * @function handleProfileThemeRuntime
     * @description Mirrors global tenant accent changes into the HR shell runtime state.
     * @param {CustomEvent} event - Shared Wilsy profile theme event.
     * @returns {void}
     * @collaboration Tenant accent changes should brand HR instantly without opening or remounting the profile panel.
     */
    const handleProfileThemeRuntime = (event = {}) => {
      setProfileRuntime(previous => ({
        ...previous,
        theme: event.detail || previous.theme
      }));
    };

    window.addEventListener('wilsy:profile-mode-change', handleProfileModeRuntime);
    window.addEventListener('wilsy:profile-theme-change', handleProfileThemeRuntime);

    return () => {
      window.removeEventListener('wilsy:profile-mode-change', handleProfileModeRuntime);
      window.removeEventListener('wilsy:profile-theme-change', handleProfileThemeRuntime);
    };
  }, [activeTenant?.branding?.accentColor, activeTenant?.branding?.primaryColor, activeTenant?.themeColor]);

  /**
   * @function pushFeedback
   * @description Publishes command feedback in the HR cockpit.
   * @param {Object} packet - Feedback packet.
   * @returns {void}
   * @collaboration HR operators need immediate confirmation for source reads and mutations.
   */
  const pushFeedback = useCallback((packet = {}) => {
    setFeedback({
      tone: packet.tone || 'ready',
      title: packet.title || 'Command Accepted',
      detail: packet.detail || 'HR command completed.'
    });
  }, []);

  /**
   * @function handleProfileThemeChange
   * @description Converts shared profile accent changes into HR cockpit feedback.
   * @param {string} color - Applied accent color.
   * @param {Object} theme - Applied theme token.
   * @returns {void}
   * @collaboration Tenant accents must visibly and operationally propagate across HR without dashboard-specific rewrites.
   */
  const handleProfileThemeChange = useCallback((color = '', theme = {}) => {
    setProfileRuntime(previous => ({
      ...previous,
      theme: {
        ...theme,
        color: color || theme.color || previous.theme?.color || '#d4af37',
        label: theme.label || previous.theme?.label || 'Tenant Accent'
      }
    }));
    pushFeedback({
      tone: 'ready',
      title: theme.label || 'Theme selected',
      detail: `Shared OS accent ${color || theme.color || 'selected'} is now applied to HR.`
    });
  }, [pushFeedback]);

  /**
   * @function handleProfileModeChange
   * @description Converts shared day/night/auto changes into HR cockpit feedback.
   * @param {string} mode - Selected mode.
   * @param {Object} modeToken - Resolved mode token.
   * @returns {void}
   * @collaboration Mode switching must be a real operating preference that every dashboard acknowledges.
   */
  const handleProfileModeChange = useCallback((mode = 'day', modeToken = {}) => {
    setProfileRuntime(previous => ({
      ...previous,
      mode: {
        ...modeToken,
        selectedMode: modeToken.selectedMode || mode || 'day',
        resolvedMode: modeToken.resolvedMode || mode || 'day'
      }
    }));
    pushFeedback({
      tone: 'ready',
      title: 'Profile mode changed',
      detail: `${String(mode).toUpperCase()} resolved to ${String(modeToken.resolvedMode || mode).toUpperCase()} for the HR cockpit.`
    });
  }, [pushFeedback]);

  /**
   * @function handleProfilePanelAction
   * @description Routes shared profile account commands into HR command feedback.
   * @param {Object} action - Profile command action packet.
   * @returns {void}
   * @collaboration My Account commands must feel native inside HR while remaining governed by the shared profile panel.
   */
  const handleProfilePanelAction = useCallback((action = {}) => {
    const label = action.label || action.command?.label || action.theme?.label || 'Profile command';
    const details = {
      mode: 'Shared profile mode updated the HR runtime.',
      theme: 'Tenant accent now brands HR controls and focus states.',
      account: 'My Account identity, security, devices, sessions and activity sources opened.',
      'account-command': `${action.command?.label || 'Account'} source inspected from HR.`,
      default: 'Shared Wilsy OS profile command executed inside HR.'
    };
    pushFeedback({
      tone: action.type === 'theme' || action.type === 'mode' ? 'ready' : 'info',
      title: label,
      detail: details[action.type] || details.default
    });
  }, [pushFeedback]);

  /**
   * @function fetchSnapshot
   * @description Loads the HR operating snapshot from the backend ledger.
   * @returns {Promise<void>}
   * @collaboration First viewport KPIs should come from one backend summary instead of client-side guessing.
   */
  const fetchSnapshot = useCallback(async () => {
    try {
      const response = await api.get('/hr/snapshot', { params: { tenantId }, headers: { 'X-Tenant-ID': tenantId }, skipAuthRedirect: true });
      setSnapshot(response.data || createEmptySnapshot());
    } catch (error) {
      setSnapshot(createEmptySnapshot());
      pushFeedback(resolveHrErrorFeedback(error, 'HR snapshot pending'));
    }
  }, [pushFeedback, tenantId]);

  /**
   * @function fetchTabData
   * @description Fetches one HR workspace dataset.
   * @param {string} tabName - HR tab id.
   * @param {Object} targetPage - Pagination state.
   * @param {string} currentSearch - Search string.
   * @returns {Promise<void>}
   * @collaboration Fetching by active process keeps HR responsive with large workforce ledgers.
   */
  const fetchTabData = useCallback(async (tabName, targetPage = DEFAULT_PAGE, currentSearch = '') => {
    const search = currentSearch;
    const params = { limit: targetPage.limit, offset: targetPage.offset, search };
    const readers = {
      employees: () => hrService.getEmployees(tenantId, params),
      candidates: () => hrService.getRecruitmentCandidates(tenantId, params),
      jobOpenings: () => hrService.getJobOpenings(tenantId, params),
      payroll: () => hrService.getPayrollSummary(tenantId, params),
      benefits: () => hrService.getBenefits(tenantId, params),
      performance: () => hrService.getPerformanceReviews(tenantId, params),
      activity: () => hrService.getEmployeeWorkLogs(tenantId, params),
      relations: () => hrService.getEmployeeRelations(tenantId, params),
      timeoff: () => hrService.getTimeOffRequests(tenantId, params),
      artifacts: () => hrService.getHrArtifacts(tenantId, params)
    };
    try {
      const payload = await readers[tabName]();
      if (tabName === 'artifacts' && Array.isArray(payload.catalog) && payload.catalog.length) {
        setArtifactCatalog(payload.catalog);
      }
      setDatasets(previous => ({ ...previous, [tabName]: normalizeDataset(payload, targetPage) }));
    } catch (error) {
      setDatasets(previous => ({ ...previous, [tabName]: { ...EMPTY_DATASET, limit: targetPage.limit, offset: targetPage.offset } }));
      pushFeedback(resolveHrErrorFeedback(error, `${getTabConfig(tabName).label} pending`));
    }
  }, [pushFeedback, tenantId]);

  /**
   * @function loadDashboard
   * @description Hydrates snapshot and active HR process data.
   * @returns {Promise<void>}
   * @collaboration Refresh should be useful and bounded, not a full-page freeze.
   */
  const loadDashboard = useCallback(async () => {
    setIsRefreshing(true);
    const reads = [
      fetchSnapshot(),
      fetchTabData(activeTab, pageStates[activeTab], searchTerm)
    ];
    if (activeTab !== 'employees') reads.push(fetchTabData('employees', pageStates.employees, ''));
    if (!['jobOpenings', 'employees'].includes(activeTab)) reads.push(fetchTabData('jobOpenings', pageStates.jobOpenings, ''));
    await Promise.allSettled(reads);
    setIsRefreshing(false);
    setLoading(false);
  }, [activeTab, fetchSnapshot, fetchTabData, pageStates, searchTerm]);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  /**
   * @function changeTab
   * @description Opens a specific HR operating lane.
   * @param {string} tabId - Target tab.
   * @returns {void}
   * @collaboration HR navigation must change the business process, not repaint the same list.
   */
  const changeTab = (tabId) => {
    setActiveTab(tabId);
    pushFeedback({ tone: 'ready', title: `${getTabConfig(tabId).label} opened`, detail: 'Workspace process changed.' });
  };

  /**
   * @function openMutationModal
   * @description Opens a create/edit form for the active HR process.
   * @param {string} type - Modal type.
   * @param {Object|null} item - Existing item.
   * @returns {void}
   * @collaboration HR mutations need real fields, not an empty placeholder commit.
   */
  const openMutationModal = (type = activeConfig.modalType, item = null) => {
    if (type === 'hrArtifact') {
      openArtifactGenerator(item);
      return;
    }
    setModalType(type);
    setEditingItem(item);
    setFormState(buildDefaultFormState(type, item, {
      employees: datasets.employees.items,
      openRoles: datasets.jobOpenings.items,
      employeeCount: Math.max(getSummaryMetric(snapshot, 'employee'), datasets.employees.total, datasets.employees.items.length, 1),
      operatorName
    }));
    setShowModal(true);
  };

  /**
   * @function openArtifactGenerator
   * @description Opens the HR artifact generator with optional employee context.
   * @param {Object|null} item - Optional HR row used to prefill the artifact.
   * @returns {void}
   * @collaboration Contracts and appointment letters should start from live employee data, then let HR verify remuneration before print.
   */
  const openArtifactGenerator = (item = null, artifactType = 'employment_contract') => {
    const employee = item && activeTab === 'employees' ? item : datasets.employees.items[0] || {};
    const identity = resolveEmployeeContractIdentity(employee);
    const benefitPlan = BENEFIT_PLAN_LIBRARY[employee.benefits] || BENEFIT_PLAN_LIBRARY.None;
    setArtifactForm({
      ...ARTIFACT_FORM_DEFAULTS,
      artifactType,
      employeeId: employee.id || employee.employeeId || '',
      firstName: identity.firstName,
      surname: identity.surname,
      cellphone: identity.cellphone,
      nationality: identity.nationality,
      nationalityCode: identity.nationalityCode,
      address: identity.address,
      addressLatitude: identity.addressLatitude,
      addressLongitude: identity.addressLongitude,
      addressMapUrl: identity.addressMapUrl || buildGoogleMapsSearchUrl(identity.address),
      identityNumber: identity.identityNumber,
      personalEmail: identity.personalEmail,
      employeeName: identity.employeeName,
      roleTitle: employee.position || employee.title || '',
      department: employee.department || '',
      reportingLine: employee.manager || '',
      workplace: employee.location || '',
      baseSalary: employee.baseSalary || employee.grossPay || employee.salary || '',
      payrollCountry: employee.payrollCountry || 'ZA',
      payDay: employee.payDay || ZA_PAYROLL_2027.defaultPayDay,
      benefits: employee.benefits || '',
      benefitDeductions: employee.benefitDeductions || benefitPlan.employeeDefault || '',
      employerBenefits: employee.employerBenefits || benefitPlan.employerDefault || '',
      variablePay: employee.variablePay || employee.commission || '',
      companyName: activeTenant?.name || activeTenant?.companyName || activeTenant?.legalName || 'Wilsy OS Tenant',
      signatoryName: operatorName
    });
    setShowArtifactModal(true);
  };

  /**
   * @function updateArtifactField
   * @description Updates HR artifact fields and applies role, benefit, payroll and address intelligence.
   * @param {string} field - Artifact field.
   * @param {string} value - New value.
   * @returns {void}
   * @collaboration Artifact forms should react like an operating system, not a static PDF wizard.
   */
  const updateArtifactField = useCallback((field, value) => {
    setArtifactForm(previous => {
      const next = { ...previous, [field]: value };
      if (field === 'address') {
        next.addressMapUrl = buildGoogleMapsSearchUrl(value);
        next.addressVerifiedAt = '';
      }
      if (field === 'nationality') {
        const country = resolveCountrySignal(value);
        next.nationalityCode = country?.code || '';
        next.countryCode = country?.code || '';
        if (country?.code && !next.payrollCountry) next.payrollCountry = country.code;
      }
      if (field === 'roleTitle') {
        const profile = resolveRoleProfile(value);
        next.department = next.department || profile.department;
      }
      if (field === 'benefits') {
        const benefitPlan = resolveBenefitPackage(value);
        next.name = benefitPlan.name;
        next.provider = benefitPlan.provider || next.provider || '';
        next.coverage = benefitPlan.coverage || next.coverage || '';
        next.eligibilityRule = benefitPlan.eligibilityRule || next.eligibilityRule || '';
        next.waitingPeriod = benefitPlan.waitingPeriod || next.waitingPeriod || '';
        next.taxable = benefitPlan.taxable || next.taxable || 'Payroll review required';
        next.payrollDeductionCode = benefitPlan.payrollDeductionCode || next.payrollDeductionCode || '';
        next.employerBenefits = benefitPlan.plans.reduce((total, plan) => total + Number(plan.employerDefault || 0), 0) || next.employerBenefits || '';
        next.benefitDeductions = benefitPlan.plans.reduce((total, plan) => total + Number(plan.employeeDefault || 0), 0) || next.benefitDeductions || '';
      }
      return next;
    });
  }, []);

  /**
   * @function openAddressInMaps
   * @description Opens Google Maps for address confirmation and stores the map proof posture.
   * @param {string} scope - mutation or artifact scope.
   * @returns {void}
   * @collaboration Address verification needs a real map handoff, coordinates and proof timing.
   */
  const openAddressInMaps = useCallback((scope = 'mutation') => {
    const address = scope === 'artifact' ? artifactForm.address : formState.address;
    const mapUrl = buildGoogleMapsSearchUrl(address);
    if (!mapUrl) {
      pushFeedback({ tone: 'warning', title: 'Address required', detail: 'Enter a residential address before opening the map verifier.' });
      return;
    }
    if (typeof window !== 'undefined') {
      window.open(mapUrl, '_blank', 'noopener,noreferrer');
    }
    const verifiedAt = new Date().toISOString();
    if (scope === 'artifact') {
      setArtifactForm(previous => ({ ...previous, addressMapUrl: mapUrl, addressVerifiedAt: verifiedAt }));
    } else {
      setFormState(previous => ({ ...previous, addressMapUrl: mapUrl, addressVerifiedAt: verifiedAt }));
    }
    pushFeedback({ tone: 'ready', title: 'Address map opened', detail: 'Google Maps handoff recorded. Add coordinates after confirmation.' });
  }, [artifactForm.address, formState.address, pushFeedback]);

  /**
   * @function applyCountrySelection
   * @description Applies a country registry selection to the active HR form scope.
   * @param {string} scope - mutation or artifact scope.
   * @param {Object} country - Country registry packet.
   * @returns {void}
   * @collaboration Nationality selection should instantly enrich identity, payroll and jurisdiction fields across Wilsy OS.
   */
  const applyCountrySelection = useCallback((scope = 'mutation', country = {}) => {
    if (!country?.code) return;
    const patch = {
      nationality: country.name,
      nationalityCode: country.code,
      countryCode: country.code,
      payrollCountry: country.code
    };
    if (scope === 'artifact') {
      setArtifactForm(previous => ({ ...previous, ...patch }));
    } else {
      setFormState(previous => ({ ...previous, ...patch }));
    }
    pushFeedback({ tone: 'ready', title: `${country.name} selected`, detail: `ISO ${country.code} attached to HR identity controls.` });
  }, [pushFeedback]);

  /**
   * @function applyBenefitPackageSelection
   * @description Applies a governed benefit package and recalculates employer and employee contribution fields.
   * @param {string} scope - mutation or artifact scope.
   * @param {string} packageName - Benefit package name.
   * @returns {void}
   * @collaboration Benefits should be selected as operational packages that immediately influence payroll, contracts and proof.
   */
  const applyBenefitPackageSelection = useCallback((scope = 'mutation', packageName = '') => {
    const benefitPackage = resolveBenefitPackage(packageName);
    const employerContribution = roundMoney(benefitPackage.plans.reduce((total, plan) => total + Number(plan.employerDefault || 0), 0));
    const employeeContribution = roundMoney(benefitPackage.plans.reduce((total, plan) => total + Number(plan.employeeDefault || 0), 0));
    const patch = {
      benefits: benefitPackage.name,
      name: benefitPackage.name,
      provider: benefitPackage.provider || '',
      coverage: benefitPackage.coverage || '',
      eligibilityRule: benefitPackage.eligibilityRule || '',
      waitingPeriod: benefitPackage.waitingPeriod || '',
      taxable: benefitPackage.taxable || 'Payroll review required',
      payrollDeductionCode: benefitPackage.payrollDeductionCode || '',
      employerContribution,
      employeeContribution,
      employerBenefits: employerContribution,
      benefitDeductions: employeeContribution,
      description: benefitPackage.description,
      cost: employerContribution * Math.max(Number((scope === 'artifact' ? artifactForm.eligibleEmployees : formState.eligibleEmployees) || 1), 1)
    };
    if (scope === 'artifact') {
      setArtifactForm(previous => ({ ...previous, ...patch }));
    } else {
      setFormState(previous => ({ ...previous, ...patch }));
    }
    pushFeedback({ tone: 'ready', title: `${benefitPackage.name} mounted`, detail: `${benefitPackage.items.length} benefit lines connected to payroll math.` });
  }, [artifactForm.eligibleEmployees, formState.eligibleEmployees, pushFeedback]);

  /**
   * @function applyAddressSuggestion
   * @description Applies a map-query address suggestion to mutation or artifact state.
   * @param {string} scope - mutation or artifact scope.
   * @param {Object} suggestion - Address suggestion packet.
   * @returns {void}
   * @collaboration Address lookup should capture coordinates, map URL and suggestion source for audit posture.
   */
  const applyAddressSuggestion = useCallback((scope = 'mutation', suggestion = {}) => {
    if (!suggestion?.label) return;
    const patch = {
      address: suggestion.label,
      addressLatitude: suggestion.latitude,
      addressLongitude: suggestion.longitude,
      addressMapUrl: suggestion.mapUrl,
      addressSuggestionSource: suggestion.source,
      addressSuggestionConfidence: suggestion.confidence,
      addressVerifiedAt: ''
    };
    if (scope === 'artifact') {
      setArtifactForm(previous => ({ ...previous, ...patch }));
    } else {
      setFormState(previous => ({ ...previous, ...patch }));
    }
    pushFeedback({ tone: 'ready', title: 'Address suggestion staged', detail: `${suggestion.region} map query attached. Open Map to verify live.` });
  }, [pushFeedback]);

  /**
   * @function updatePageOffset
   * @description Moves the active table page backward or forward.
   * @param {boolean} increment - True for next page.
   * @returns {Promise<void>}
   * @collaboration Pagination keeps the HR ledger useful with more than a handful of records.
   */
  const updatePageOffset = async (increment) => {
    const current = pageStates[activeTab];
    const nextPage = {
      ...current,
      offset: increment ? current.offset + current.limit : Math.max(0, current.offset - current.limit)
    };
    setPageStates(previous => ({ ...previous, [activeTab]: nextPage }));
    setIsRefreshing(true);
    await fetchTabData(activeTab, nextPage, searchTerm);
    setIsRefreshing(false);
  };

  /**
   * @function saveMutation
   * @description Persists an HR record create/update action.
   * @returns {Promise<void>}
   * @collaboration Save operations must write to backend HR APIs and refresh the active process.
   */
  const saveMutation = async () => {
    const type = modalType;
    try {
      setIsRefreshing(true);
      if (type === 'employee') {
        const payload = normalizeMutationPayload(type, formState);
        if (editingItem) await hrService.updateEmployee(editingItem.id, payload, tenantId);
        else await hrService.createEmployee(payload, tenantId);
      }
      if (type === 'candidate') {
        const payload = normalizeMutationPayload(type, formState);
        if (editingItem) await hrService.updateCandidate(editingItem.id, payload, tenantId);
        else await hrService.createCandidate(payload, tenantId);
      }
      if (type === 'jobOpening') {
        const payload = normalizeMutationPayload(type, formState);
        if (editingItem) await hrService.updateJobOpening(editingItem.id, payload, tenantId);
        else await hrService.createJobOpening(payload, tenantId);
      }
      if (type === 'payroll') {
        const payload = normalizeMutationPayload(type, formState);
        if (editingItem) await hrService.updatePayrollRecord(editingItem.id, payload, tenantId);
        else await hrService.createPayrollRecord(payload, tenantId);
      }
      if (type === 'benefit') {
        const payload = normalizeMutationPayload(type, formState);
        if (editingItem) await hrService.updateBenefit(editingItem.id, payload, tenantId);
        else await hrService.createBenefit(payload, tenantId);
      }
      if (type === 'performanceReview') {
        const payload = normalizeMutationPayload(type, formState);
        if (editingItem) await hrService.updatePerformanceReview(editingItem.id, payload, tenantId);
        else await hrService.createPerformanceReview(payload, tenantId);
      }
      if (type === 'employeeWorkLog') {
        const payload = normalizeMutationPayload(type, formState);
        if (editingItem) await hrService.updateEmployeeWorkLog(editingItem.id, payload, tenantId);
        else await hrService.createEmployeeWorkLog(payload, tenantId);
      }
      if (type === 'employeeRelations') {
        const payload = normalizeMutationPayload(type, formState);
        if (editingItem) await hrService.updateEmployeeRelation(editingItem.id, payload, tenantId);
        else await hrService.createEmployeeRelation(payload, tenantId);
      }
      if (type === 'timeOff') {
        const payload = normalizeMutationPayload(type, formState);
        if (editingItem) await hrService.updateTimeOffRequest(editingItem.id, payload, tenantId);
        else await hrService.createTimeOffRequest(payload, tenantId);
      }
      setShowModal(false);
      setEditingItem(null);
      await Promise.all([fetchSnapshot(), fetchTabData(activeTab, pageStates[activeTab], searchTerm)]);
      pushFeedback({ tone: 'ready', title: 'HR record saved', detail: `${type} ledger updated.` });
    } catch (error) {
      pushFeedback({ tone: 'risk', title: 'HR save failed', detail: error?.response?.data?.message || error?.message || 'Mutation failed.' });
    } finally {
      setIsRefreshing(false);
    }
  };

  /**
   * @function generateArtifact
   * @description Generates an HR artifact, opens the printable artifact, and refreshes the HR artifact ledger.
   * @returns {Promise<void>}
   * @collaboration HR contracts must become tangible output, not command receipts with no business value.
   */
  const generateArtifact = async () => {
    try {
      const missing = validateArtifactForm(artifactForm);
      if (missing.length) {
        pushFeedback({
          tone: 'risk',
          title: 'Artifact controls required',
          detail: `Complete: ${missing.slice(0, 4).join(', ')}${missing.length > 4 ? '...' : ''}`
        });
        return;
      }
      setIsRefreshing(true);
      const employeeName = composeEmployeeName(artifactForm);
      const response = await hrService.generateHrArtifact(tenantId, {
        artifactType: artifactForm.artifactType,
        payload: {
          ...artifactForm,
          employeeName,
          addressPosture: artifactAddressPosture,
          remunerationMath: artifactRemunerationMath,
          tenantName: activeTenant?.name || activeTenant?.companyName || activeTenant?.legalName || 'Wilsy OS Tenant'
        }
      });
      if (isEmployeeRelationsArtifact(artifactForm.artifactType)) {
        await hrService.createEmployeeRelation({
          employeeId: artifactForm.employeeId || '',
          employeeName,
          relationsActionType: artifactForm.relationsActionType || artifactForm.artifactType,
          incidentDate: artifactForm.incidentDate || null,
          incidentSummary: artifactForm.incidentSummary || '',
          policyBreach: artifactForm.policyBreach || '',
          correctiveAction: artifactForm.correctiveAction || '',
          employeeResponse: artifactForm.employeeResponse || '',
          hearingDate: artifactForm.hearingDate || artifactForm.reviewDate || null,
          outcome: artifactForm.outcome || '',
          status: 'ISSUED',
          proofHash: response.artifact?.proofHash || '',
          artifactType: artifactForm.artifactType,
          artifactTitle: response.artifact?.title || activeArtifactTemplate.title,
          metadata: {
            artifactId: response.artifact?.id,
            artifactProofHash: response.artifact?.proofHash,
            generatedFrom: 'HR_ARTIFACT_GENERATOR'
          }
        }, tenantId);
      }
      downloadHtmlArtifact(response.artifact);
      setShowArtifactModal(false);
      await Promise.all([fetchSnapshot(), fetchTabData('artifacts', pageStates.artifacts, searchTerm)]);
      pushFeedback({ tone: 'ready', title: 'HR artifact generated', detail: `${response.artifact?.title || 'Artifact'} opened for review and print.` });
      setActiveTab('artifacts');
    } catch (error) {
      pushFeedback({ tone: 'risk', title: 'Artifact failed', detail: error?.response?.data?.message || error?.message || 'HR artifact generation failed.' });
    } finally {
      setIsRefreshing(false);
    }
  };

  /**
   * @function generatePayslip
   * @description Opens a printable payslip generated from a payroll ledger row.
   * @param {Object} row - Payroll row.
   * @returns {Promise<void>}
   * @collaboration Payroll rows need one-click payslips with statutory deductions and proof.
   */
  const generatePayslip = async (row = {}) => {
    try {
      setIsRefreshing(true);
      const response = await hrService.generatePayslip(row.id, tenantId);
      downloadHtmlArtifact(response.artifact);
      pushFeedback({ tone: 'ready', title: 'Payslip generated', detail: `${response.artifact?.title || 'Payslip'} opened for review.` });
    } catch (error) {
      pushFeedback({ tone: 'risk', title: 'Payslip failed', detail: error?.response?.data?.message || error?.message || 'Could not generate payslip.' });
    } finally {
      setIsRefreshing(false);
    }
  };

  /**
   * @function deleteRecord
   * @description Deletes an HR record after explicit confirmation.
   * @param {Object} item - HR record.
   * @returns {Promise<void>}
   * @collaboration Delete commands remain deliberate because people records are institutional memory.
   */
  const deleteRecord = async (item) => {
    if (!window.confirm('Delete this HR ledger record?')) return;
    try {
      setIsRefreshing(true);
      if (activeTab === 'employees') await hrService.deleteEmployee(item.id, tenantId);
      if (activeTab === 'candidates') await hrService.deleteCandidate(item.id, tenantId);
      if (activeTab === 'jobOpenings') await hrService.deleteJobOpening(item.id, tenantId);
      if (activeTab === 'benefits') await hrService.deleteBenefit(item.id, tenantId);
      if (activeTab === 'performance') await hrService.deletePerformanceReview(item.id, tenantId);
      if (activeTab === 'activity') await hrService.deleteEmployeeWorkLog(item.id, tenantId);
      if (activeTab === 'relations') await hrService.deleteEmployeeRelation(item.id, tenantId);
      if (activeTab === 'timeoff') await hrService.deleteTimeOffRequest(item.id, tenantId);
      await Promise.all([fetchSnapshot(), fetchTabData(activeTab, pageStates[activeTab], searchTerm)]);
      pushFeedback({ tone: 'ready', title: 'HR record deleted', detail: 'Ledger row removed.' });
    } catch (error) {
      pushFeedback({ tone: 'risk', title: 'Delete failed', detail: error?.response?.data?.message || error?.message || 'Delete failed.' });
    } finally {
      setIsRefreshing(false);
    }
  };

  /**
   * @function syncPayroll
   * @description Requests payroll synchronization.
   * @returns {Promise<void>}
   * @collaboration Payroll has its own command because compensation sync is not a generic row creation.
   */
  async function syncPayroll() {
    try {
      setIsRefreshing(true);
      await hrService.syncPayroll(tenantId);
      await Promise.all([fetchSnapshot(), fetchTabData('payroll', pageStates.payroll, searchTerm)]);
      pushFeedback({ tone: 'ready', title: 'Payroll sync accepted', detail: 'Compensation ledger command completed.' });
    } catch (error) {
      pushFeedback({ tone: 'warning', title: 'Payroll sync pending', detail: error?.response?.data?.message || error?.message || 'Payroll source did not answer.' });
    } finally {
      setIsRefreshing(false);
    }
  }

  /**
   * @function exportActiveDataset
   * @description Exports the active HR process dataset to CSV.
   * @returns {Promise<void>}
   * @collaboration HR export should be explicit, scoped and source-backed.
   */
  const exportActiveDataset = async () => {
    await exportCSV(datasets[activeTab].items, `wilsy_hr_${activeTab}_${tenantId}`, { tenantId, redact: false });
    pushFeedback({ tone: 'ready', title: 'HR export generated', detail: `${datasets[activeTab].items.length} ${activeConfig.label.toLowerCase()} rows exported.` });
  };

  /**
   * @function runProcessStep
   * @description Executes a process step from the HR next-work panel.
   * @param {string} step - Process step label.
   * @param {number} index - Step index.
   * @returns {void}
   * @collaboration Process buttons should route to real work rather than decorative command receipts.
   */
  const runProcessStep = (step = '', index = 0) => {
    if (/generate payslip/i.test(step)) {
      const firstPayroll = datasets.payroll.items[0];
      if (firstPayroll) {
        generatePayslip(firstPayroll);
        return;
      }
      openMutationModal('payroll');
      return;
    }
    if (/create payroll|payroll run/i.test(step)) {
      openMutationModal('payroll');
      return;
    }
    if (/record daily work|activity|evidence/i.test(step) && activeTab === 'activity') {
      openMutationModal('employeeWorkLog');
      return;
    }
    if (/dismissal pack/i.test(step) && activeTab === 'relations') {
      openArtifactGenerator(null, 'dismissal_notice');
      return;
    }
    if (/written warning/i.test(step) && activeTab === 'relations') {
      openArtifactGenerator(null, 'written_warning');
      return;
    }
    if (/warning|disciplinary|dismissal|relations/i.test(step) && activeTab === 'relations') {
      openMutationModal('employeeRelations');
      return;
    }
    if (/sync payroll/i.test(step)) {
      syncPayroll();
      return;
    }
    if (activeTab === 'artifacts' || /contract|appointment|remuneration|artifact/i.test(step)) {
      openArtifactGenerator();
      return;
    }
    if (index === 0) {
      openMutationModal();
      return;
    }
    pushFeedback({ tone: 'ready', title: step, detail: `${activeConfig.label} process selected.` });
  };

  /**
   * @function renderRowCells
   * @description Renders table cells for the active HR process.
   * @param {Object} item - HR record.
   * @returns {Array<JSX.Element>} Table cells.
   * @collaboration Each process needs useful columns rather than a generic data dump.
   */
  const renderRowCells = (item = {}) => {
    const rows = {
      employees: [item.name, item.email, item.department || 'Unassigned', item.position || 'Staff', item.status || 'ACTIVE'],
      candidates: [item.name, item.email, item.position || 'Role pending', item.stage || item.status || 'SCREENING', item.phone || 'No phone'],
      jobOpenings: [item.title || item.name, item.department || 'Unassigned', item.location || 'Remote', item.priority || 'Normal', item.status || 'OPEN'],
      payroll: [item.employeeName || item.name, item.period || 'Current', `${formatMoney(item.grossPay)} gross`, `${formatMoney(item.employeeTax || item.statutoryDeductions || 0)} tax`, item.status || item.payrollGateStatus || 'READY'],
      benefits: [item.name, item.coverage || 'Coverage pending', formatMoney(item.cost), item.status || 'ACTIVE', item.type || 'Benefit'],
      performance: [item.employeeName || item.name, item.reviewerName || 'Reviewer pending', `${item.rating || '—'} / ${item.productivityScore || 0}`, item.period || 'Current', item.status || 'PENDING'],
      activity: [item.employeeName || item.name, item.workDate ? new Date(item.workDate).toLocaleDateString() : 'Today', item.workType || 'Work evidence', `${item.impactScore || 0} impact`, item.status || 'RECORDED'],
      relations: [item.employeeName || item.name, item.relationsActionType || item.artifactType || 'Relations action', item.policyBreach || 'Policy pending', item.hearingDate ? new Date(item.hearingDate).toLocaleDateString() : 'Review pending', item.status || 'DRAFT'],
      timeoff: [item.employeeName || item.name, item.type || 'Leave', item.startDate ? new Date(item.startDate).toLocaleDateString() : '—', item.endDate ? new Date(item.endDate).toLocaleDateString() : '—', item.status || 'PENDING'],
      artifacts: [item.artifactTitle || item.name, item.artifactType || 'HR Artifact', item.artifactFormat || 'HTML', item.proofHash ? item.proofHash.slice(0, 14) : 'Proof pending', item.status || 'GENERATED']
    };
    return (rows[activeTab] || rows.employees).map((value, index) => <td key={`${item.id}-${index}`}>{value}</td>);
  };

  /**
   * @function updateMutationField
   * @description Updates a mutation field and applies related HR intelligence defaults.
   * @param {Object} config - Field config.
   * @param {string} value - New value.
   * @returns {void}
   * @collaboration Selecting a role, stage or benefit should change the workflow immediately.
   */
  const updateMutationField = (config = {}, value = '') => {
    setFormState(previous => {
      const next = { ...previous, [config.field]: value };
      if (config.field === 'employeeName') {
        const employee = findEmployeeByDisplay(datasets.employees.items, value);
        if (employee) {
          next.employeeId = employee.id || employee.employeeId || next.employeeId || '';
          next.email = employee.email || next.email || '';
          next.department = employee.department || next.department || '';
          next.position = employee.position || employee.title || next.position || '';
          next.roleTitle = employee.position || employee.title || next.roleTitle || '';
          next.manager = employee.manager || next.manager || '';
          next.reportingLine = employee.manager || employee.reportingLine || next.reportingLine || '';
          next.identityNumber = employee.identityNumber || next.identityNumber || '';
          next.nationality = employee.nationality || employee.country || next.nationality || '';
          next.nationalityCode = employee.nationalityCode || employee.countryCode || resolveCountrySignal(next.nationality)?.code || next.nationalityCode || '';
          next.address = employee.address || employee.residentialAddress || next.address || '';
          next.addressLatitude = employee.addressLatitude || employee.latitude || next.addressLatitude || '';
          next.addressLongitude = employee.addressLongitude || employee.longitude || next.addressLongitude || '';
          next.addressMapUrl = employee.addressMapUrl || next.addressMapUrl || buildGoogleMapsSearchUrl(next.address);
          next.rightToWorkStatus = employee.rightToWorkStatus || next.rightToWorkStatus || '';
          if (modalType === 'performanceReview') {
            const targets = resolveRoleTargets(next.roleTitle);
            next.goalsTotal = Number(next.goalsTotal || targets.targets.length || 0);
            next.roleTargetEvidence = next.roleTargetEvidence || targets.targets.join(' // ');
            next.managerRecommendation = next.managerRecommendation || targets.recommendation;
          }
        }
      }
      if (config.field === 'address') {
        next.addressMapUrl = buildGoogleMapsSearchUrl(value);
        next.addressVerifiedAt = '';
      }
      if (config.field === 'nationality') {
        const country = resolveCountrySignal(value);
        next.nationalityCode = country?.code || '';
        next.countryCode = country?.code || '';
        if (country?.code && !next.payrollCountry) next.payrollCountry = country.code;
      }
      if (['position', 'title', 'roleTitle'].includes(config.field)) {
        const profile = resolveRoleProfile(value);
        if (profile.department) next.department = profile.department;
        if (modalType === 'jobOpening') {
          const band = resolveCompensationBand(value);
          next.salaryMin = next.salaryMin || band.min;
          next.salaryMax = next.salaryMax || band.max;
          next.description = `Role duties: ${profile.duties.join(' // ')} | KPIs: ${profile.kpis.join(' // ')}`;
        }
        if (modalType === 'performanceReview') {
          const targets = resolveRoleTargets(value);
          next.goalsTotal = targets.targets.length;
          next.roleTargetEvidence = targets.targets.join(' // ');
          next.managerRecommendation = next.managerRecommendation || targets.recommendation;
        }
      }
      if (modalType === 'candidate' && config.field === 'stage') {
        const workflow = RECRUITING_STAGE_WORKFLOWS[value] || RECRUITING_STAGE_WORKFLOWS.New;
        next.assessmentEvidence = next.assessmentEvidence || workflow.evidence.join(' // ');
        next.stageWorkflowTitle = workflow.title;
        next.nextAction = workflow.nextActions[0] || '';
      }
      if (['benefits', 'name'].includes(config.field)) {
        const benefitPlan = resolveBenefitPackage(value);
        const employerContribution = roundMoney(benefitPlan.plans.reduce((total, plan) => total + Number(plan.employerDefault || 0), 0));
        const employeeContribution = roundMoney(benefitPlan.plans.reduce((total, plan) => total + Number(plan.employeeDefault || 0), 0));
        next.benefits = benefitPlan.name;
        next.name = benefitPlan.name;
        next.provider = benefitPlan.provider || next.provider || '';
        next.coverage = benefitPlan.coverage || next.coverage || '';
        next.eligibilityRule = benefitPlan.eligibilityRule || next.eligibilityRule || '';
        next.waitingPeriod = benefitPlan.waitingPeriod || next.waitingPeriod || '';
        next.taxable = benefitPlan.taxable || next.taxable || 'Payroll review required';
        next.payrollDeductionCode = benefitPlan.payrollDeductionCode || next.payrollDeductionCode || '';
        next.employerContribution = employerContribution;
        next.employeeContribution = employeeContribution;
        next.employerBenefits = employerContribution;
        next.benefitDeductions = employeeContribution;
        next.cost = employerContribution * Math.max(Number(next.eligibleEmployees || 1), 1);
        next.description = benefitPlan.description;
      }
      if (modalType === 'benefit' && ['eligibleEmployees', 'employerContribution', 'employeeContribution'].includes(config.field)) {
        const benefit = calculateBenefitMath(next);
        next.cost = benefit.monthlyEmployerCost;
        next.monthlyEmployerCost = benefit.monthlyEmployerCost;
        next.monthlyEmployeeContribution = benefit.monthlyEmployeeContribution;
        next.totalMonthlyPlanValue = benefit.totalMonthlyPlanValue;
      }
      if (modalType === 'payroll' && ['grossPay', 'deductions', 'otherDeductions', 'benefits', 'benefitDeductions', 'employerBenefits', 'taxableBenefits', 'preTaxDeductions', 'payDay', 'payrollMonth', 'payrollYear', 'payrollCountry'].includes(config.field)) {
        const payroll = calculatePayrollMath(next);
        next.employeeTax = payroll.employeeTax;
        next.uifEmployee = payroll.uifEmployee;
        next.uifEmployer = payroll.uifEmployer;
        next.statutoryDeductions = payroll.statutoryDeductions;
        next.netPay = payroll.netPay;
        next.plannedPayDate = payroll.plannedPayDate;
      }
      if (modalType === 'performanceReview' && ['rating', 'goalsMet', 'goalsTotal', 'attendanceScore', 'taskScore', 'qualityScore', 'customerScore', 'managerRecommendation'].includes(config.field)) {
        const performance = calculatePerformanceMath(next);
        next.goalCompletion = performance.goalCompletion;
        next.activityScore = performance.activityScore;
        next.productivityScore = performance.productivityScore;
        next.recommendation = performance.recommendation;
      }
      if (modalType === 'employeeWorkLog' && config.field === 'workType') {
        const workflow = WORK_LOG_TYPE_WORKFLOWS[value] || WORK_LOG_TYPE_WORKFLOWS['Daily work'];
        next.achievementType = workflow.achievementType;
        next.impactScore = workflow.impactScore;
        next.performanceScore = workflow.performanceScore;
        next.status = workflow.status;
      }
      return next;
    });
  };

  /**
   * @function renderMutationField
   * @description Renders a process-aware HR mutation control.
   * @param {Object} config - Field config.
   * @returns {JSX.Element} Field control.
   * @collaboration HR forms should use selects, lists, date pickers and numeric keyboards instead of generic text inputs.
   */
  const renderMutationField = (config = {}) => {
    const options = getFieldOptions(config);
    const value = isDateField(config.field) || config.type === 'date'
      ? normalizeDateInputValue(formState[config.field])
      : (formState[config.field] || '');
    const commonProps = {
      value,
      onChange: event => updateMutationField(config, event.target.value),
      placeholder: config.placeholder || config.label
    };
    if (config.control === 'addressLookup') {
      const addressPosture = resolveAddressPosture(formState);
      const suggestions = buildAddressSuggestions(value, formState.nationality || formState.countryCode);
      return (
        <label key={config.field} className={styles.addressField}>
          <span>{config.label}{config.required ? ' *' : ''}</span>
          <div className={styles.addressControl}>
            <input
              {...commonProps}
              type="text"
              autoComplete="street-address"
            />
            <button type="button" onClick={() => openAddressInMaps('mutation')}>
              <MapPin size={14} /> Map
            </button>
          </div>
          <small className={styles.addressMeta}>
            {addressPosture.status.replace(/_/g, ' ')} // {addressPosture.source.replace(/_/g, ' ')} // {addressPosture.coordinatesReady ? `${addressPosture.latitude}, ${addressPosture.longitude}` : 'coordinates pending'}
          </small>
          {suggestions.length > 0 && (
            <div className={styles.addressSuggestionRail}>
              {suggestions.map(suggestion => (
                <button key={suggestion.id} type="button" onClick={() => applyAddressSuggestion('mutation', suggestion)}>
                  <MapPin size={13} />
                  <span>{suggestion.label}</span>
                  <small>{suggestion.confidence.replace(/_/g, ' ')}</small>
                </button>
              ))}
            </div>
          )}
        </label>
      );
    }
    if (config.control === 'countryLookup') {
      const countryMatches = searchSovereignCountries(value, 6);
      const activeCountry = resolveCountrySignal(value);
      return (
        <label key={config.field} className={styles.countryField}>
          <span>{config.label}{config.required ? ' *' : ''}</span>
          <div className={styles.countryControl}>
            <Globe2 size={16} />
            <input
              {...commonProps}
              type="text"
              autoComplete="country-name"
            />
            <b>{activeCountry?.code || 'ISO'}</b>
          </div>
          <div className={styles.countrySuggestionRail}>
            {countryMatches.map(country => (
              <button key={country.code} type="button" onClick={() => applyCountrySelection('mutation', country)}>
                <span>{country.name}</span>
                <small>{country.code}</small>
              </button>
            ))}
          </div>
        </label>
      );
    }
    if (config.control === 'benefitPackagePicker') {
      const benefitPackage = resolveBenefitPackage(value);
      const packageMatches = BENEFIT_OPTIONS
        .filter(option => !value || option.toLowerCase().includes(String(value).toLowerCase()))
        .slice(0, 8);
      return (
        <label key={config.field} className={styles.benefitPackageField}>
          <span>{config.label}{config.required ? ' *' : ''}</span>
          <div className={styles.benefitPackageControl}>
            <Heart size={16} />
            <input
              {...commonProps}
              list={`wilsy-hr-${modalType}-${config.field}-options`}
              type="text"
              placeholder="Search benefit package"
            />
            <b>{benefitPackage.isPackage ? 'PACK' : 'PLAN'}</b>
          </div>
          <datalist id={`wilsy-hr-${modalType}-${config.field}-options`}>
            {BENEFIT_OPTIONS.map(option => <option key={option} value={option} />)}
          </datalist>
          <div className={styles.benefitPackageRail}>
            {packageMatches.map(option => {
              const packagePlan = resolveBenefitPackage(option);
              return (
                <button key={option} type="button" onClick={() => applyBenefitPackageSelection('mutation', option)}>
                  <strong>{packagePlan.name}</strong>
                  <small>{packagePlan.items.length || 1} lines // {formatMoney(packagePlan.plans.reduce((total, plan) => total + Number(plan.employerDefault || 0), 0))} employer</small>
                </button>
              );
            })}
          </div>
          <small className={styles.benefitPackageMeta}>
            {benefitPackage.description} // Employee deduction {formatMoney(benefitPackage.plans.reduce((total, plan) => total + Number(plan.employeeDefault || 0), 0))}
          </small>
        </label>
      );
    }
    if (config.control === 'select') {
      return (
        <label key={config.field}>
          <span>{config.label}{config.required ? ' *' : ''}</span>
          <select {...commonProps}>
            <option value="">Select {config.label.toLowerCase()}</option>
            {options.map(option => <option key={option} value={option}>{option}</option>)}
          </select>
        </label>
      );
    }
    if (config.control === 'datalist') {
      const listId = `wilsy-hr-${modalType}-${config.field}-options`;
      return (
        <label key={config.field}>
          <span>{config.label}{config.required ? ' *' : ''}</span>
          <input
            {...commonProps}
            type={config.type || 'text'}
            list={listId}
            inputMode={config.inputMode}
            autoComplete="off"
          />
          <datalist id={listId}>
            {options.map(option => <option key={option} value={option} />)}
          </datalist>
        </label>
      );
    }
    return (
      <label key={config.field}>
        <span>{config.label}{config.required ? ' *' : ''}</span>
        <input
          {...commonProps}
          type={config.type || (isDateField(config.field) ? 'date' : 'text')}
          inputMode={config.inputMode || (config.type === 'number' ? 'decimal' : undefined)}
          min={config.type === 'number' ? '0' : undefined}
          step={config.type === 'number' ? '0.01' : undefined}
        />
      </label>
    );
  };

  const activeDataset = datasets[activeTab] || EMPTY_DATASET;
  const totalPages = Math.max(1, Math.ceil(activeDataset.total / (activeDataset.limit || DEFAULT_PAGE.limit)));
  const currentPage = Math.floor((activeDataset.offset || 0) / (activeDataset.limit || DEFAULT_PAGE.limit)) + 1;

  if (loading) {
    return (
      <div className={styles.hrLoading}>
        <strong>WILSY OS HR</strong>
        <span>Hydrating people operating ledger...</span>
      </div>
    );
  }

  const hrChromeLeftRail = (
    <nav aria-label="HR workspace modules">
      {HR_TABS.map((tab) => {
        const TabIcon = tab.icon;
        const active = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            type="button"
            data-active={active ? 'true' : 'false'}
            onClick={() => changeTab(tab.id)}
            title={tab.label}
          >
            {TabIcon ? <TabIcon size={15} aria-hidden /> : null}
            <span>{tab.label}</span>
          </button>
        );
      })}
    </nav>
  );

  const hrTenantIdentity = {
    name: activeTenant?.name || activeTenant?.displayName || activeTenant?.companyName || 'Wilsy OS Root',
    displayName: activeTenant?.name || activeTenant?.displayName || 'Wilsy OS Root',
    logo: activeTenant?.logo || activeTenant?.logoUrl || wilsyLogo,
    logoUrl: activeTenant?.logo || activeTenant?.logoUrl || wilsyLogo,
    status: 'TENANT COMMAND',
    tenantId: tenantId || DEFAULT_TENANT_ID
  };

  const hrStory = 'People operating system — hire, govern, pay, and prove every employee action.';


  return (
    <WilsyOSDashboardChrome
      dashboardKey="hr"
      commandLabel="Wilsy OS HR"
      title="People Operating System"
      role="HR_OPERATOR"
      posture="HR_LEDGER"
      storyMessages={[hrStory]}
      tenant={hrTenantIdentity}
      operator={null}
      leftRail={hrChromeLeftRail}
      search={{
        value: searchTerm,
        onChange: (event) => setSearchTerm(event.target.value),
        placeholder: 'Search HR ledger…'
      }}
      actions={{
        primaryLabel: workspace?.primary || 'Add Employee',
        onPrimary: () => openMutationModal(),
        primaryDisabled: Boolean(isRefreshing),
        onSync: () => loadDashboard(),
        syncLabel: 'Resync'
      }}
      account={{
        isOpen: showProfilePanel,
        onOpen: () => setShowProfilePanel(true),
        onClose: () => setShowProfilePanel(false),
        user: user || {},
        label: 'COMMAND',
        CommandCenterComponent: WilsyAccountCommandCenter
      }}
      metrics={[]}
    >

      <div
        className={styles.hrShell}
        data-rail={isRailOpen ? 'open' : 'closed'}
        data-profile-mode={profileRuntime.mode?.resolvedMode || 'night'}
        data-profile-accent={profileRuntime.theme?.id || 'sovereign-gold'}
        style={{
          '--hr-runtime-accent': profileRuntime.theme?.color || '#d4af37',
          '--wilsy-os-accent': profileRuntime.theme?.color || '#d4af37',
          '--wilsy-os-accent-glow': profileRuntime.theme?.glow || '#ffe875',
          '--wilsy-os-accent-contrast': profileRuntime.theme?.contrast || '#070806',
          '--wilsy-os-bg': profileRuntime.mode?.background || '#030403',
          '--wilsy-os-panel': profileRuntime.mode?.panel || 'rgba(14, 16, 12, 0.94)',
          '--wilsy-os-surface': profileRuntime.mode?.surface || 'rgba(0, 0, 0, 0.72)',
          '--wilsy-os-ink': profileRuntime.mode?.ink || '#f5f1df',
          '--wilsy-os-muted': profileRuntime.mode?.muted || 'rgba(245, 241, 223, 0.58)',
          '--wilsy-os-grid-opacity': profileRuntime.mode?.gridOpacity || '0.08'
        }}
      >
        <main className={styles.hrFrame}>
          <section className={styles.hrWorkspace}>
            <section className={styles.hrFeedback} data-tone={feedback.tone}>
              <strong>{feedback.title}</strong>
              <span>{feedback.detail}</span>
              <em>{snapshot.sourceStatus || 'HR_LEDGER_PENDING'}</em>
            </section>

            <section className={styles.hrHero}>
              <div>
                <span>{workspace.kicker}</span>
                <h2>{workspace.title}</h2>
                <p>{workspace.description}</p>
              </div>
              <div className={styles.hrHeroActions}>
                <label className={styles.hrSearch}>
                  <Search size={16} />
                  <input value={searchTerm} onChange={event => setSearchTerm(event.target.value)} placeholder="Search HR ledger..." />
                </label>
                <button type="button" onClick={() => openArtifactGenerator()}>
                  <FileText size={15} />
                  Contract / Letter
                </button>
              </div>
            </section>

            <section className={styles.hrArtifactStrip} aria-label="HR artifact shortcuts">
              {artifactCatalog.slice(0, 4).map(artifact => (
                <button
                  type="button"
                  key={artifact.id}
                  onClick={() => openArtifactGenerator(null, artifact.id)}
                >
                  <FileText size={15} />
                  <span>{artifact.label}</span>
                </button>
              ))}
            </section>

            <section className={styles.hrKpis}>
              {workspace.kpis.map(([label, value, detail]) => (
                <article key={`${activeTab}-${label}`}>
                  <span>{label}</span>
                  <strong>{typeof value === 'number' ? formatCount(value) : value}</strong>
                  <small>{detail}</small>
                </article>
              ))}
            </section>

            <section className={styles.hrGrid}>
              <div className={styles.hrPanel}>
                <header>
                  <div>
                    <span>Live Ledger</span>
                    <h3>{activeConfig.label}</h3>
                  </div>
                  <div className={styles.hrPager}>
                    <button type="button" onClick={() => updatePageOffset(false)} disabled={activeDataset.offset === 0 || isRefreshing}>Prev</button>
                    <span>{currentPage}/{totalPages}</span>
                    <button type="button" onClick={() => updatePageOffset(true)} disabled={!activeDataset.hasMore || isRefreshing}>Next</button>
                  </div>
                </header>
                <div className={styles.hrTableWrap}>
                  <table>
                    <thead>
                      <tr>
                        {['Primary', 'Source', 'Domain', 'Metric', 'Status'].map(header => <th key={header}>{header}</th>)}
                        <th>Command</th>
                      </tr>
                    </thead>
                    <tbody>
                      {activeDataset.items.map(item => (
                        <tr key={item.id}>
                          {renderRowCells(item)}
                          <td>
                            <button type="button" onClick={() => openMutationModal(activeConfig.modalType, item)}><Edit size={14} /></button>
                            {activeTab === 'employees' && <button type="button" onClick={() => openArtifactGenerator(item)}><FileText size={14} /></button>}
                            {activeTab === 'payroll' && <button type="button" onClick={() => generatePayslip(item)}><FileText size={14} /></button>}
                            {!['payroll', 'artifacts'].includes(activeTab) && <button type="button" onClick={() => deleteRecord(item)}><Trash2 size={14} /></button>}
                          </td>
                        </tr>
                      ))}
                      {!activeDataset.items.length && (
                        <tr>
                          <td colSpan={6}>No {activeConfig.label.toLowerCase()} records found in the HR ledger.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              <aside className={styles.hrPanel}>
                <header>
                  <div>
                    <span>Operating Process</span>
                    <h3>Next Work</h3>
                  </div>
                  <button type="button">{workspace.process.length}</button>
                </header>
                <div className={styles.hrProcess}>
                  {workspace.process.map((step, index) => (
                    <button key={step} type="button" onClick={() => runProcessStep(step, index)}>
                      <span>{String(index + 1).padStart(2, '0')}</span>
                      <strong>{step}</strong>
                      <small>{activeConfig.label}</small>
                    </button>
                  ))}
                </div>
                <div className={styles.hrTelemetry}>
                  <span><Activity size={14} /> HR Telemetry</span>
                  {hrActivities.length === 0 && <small>No HR telemetry events yet.</small>}
                  {hrActivities.map((event, index) => (
                    <small key={`${event.id || event.timestamp || 'hr'}-${index}`}>{event.eventType || 'HR_EVENT'} // {event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : 'LIVE'}</small>
                  ))}
                </div>
              </aside>
            </section>
          </section>
        </main>

        <WilsyProfilePanel
          isOpen={showProfilePanel}
          onClose={() => setShowProfilePanel(false)}
          user={user}
          activeTenant={activeTenant}
          access={{ userId: user?.id || user?._id, userRole: user?.role, edition: activeTenant?.edition }}
          onSignOut={logout}
          onThemeChange={handleProfileThemeChange}
          onModeChange={handleProfileModeChange}
          onProfileAction={handleProfilePanelAction}
        />

        {showArtifactModal && (
          <div className={styles.hrModal} role="dialog" aria-modal="true" aria-label="HR artifact generator">
            <section>
              <header>
                <div>
                  <span><FileText size={16} /> HR Artifact Generator</span>
                  <h2>{activeArtifactTemplate.title}</h2>
                </div>
                <button type="button" onClick={() => setShowArtifactModal(false)} aria-label="Close HR artifact generator"><X size={16} /></button>
              </header>
              <div className={styles.hrFormGrid}>
                <label>
                  <span>Artifact Type</span>
                  <select
                    value={artifactForm.artifactType}
                    onChange={event => {
                      const nextArtifactType = event.target.value;
                      setArtifactForm(previous => ({
                        ...previous,
                        artifactType: nextArtifactType,
                        relationsActionType: isEmployeeRelationsArtifact(nextArtifactType) ? nextArtifactType.replace(/_/g, ' ') : previous.relationsActionType
                      }));
                      pushFeedback({ tone: 'ready', title: 'Artifact type selected', detail: `${nextArtifactType.replace(/_/g, ' ')} workflow loaded.` });
                    }}
                  >
                    {artifactCatalog.map(artifact => <option key={artifact.id} value={artifact.id}>{artifact.label}</option>)}
                  </select>
                </label>
                <article className={styles.artifactTemplatePanel} data-template={artifactForm.artifactType}>
                  <span>{activeArtifactTemplate.kicker}</span>
                  <strong>{activeArtifactTemplate.intent}</strong>
                  <div>
                    {activeArtifactTemplate.controls.map(control => (
                      <small key={control}>{control}</small>
                    ))}
                  </div>
                </article>
                <label>
                  <span>First Name</span>
                  <input value={artifactForm.firstName || ''} onChange={event => setArtifactForm(previous => ({ ...previous, firstName: event.target.value }))} placeholder="First name" />
                </label>
                <label>
                  <span>Surname</span>
                  <input value={artifactForm.surname || ''} onChange={event => setArtifactForm(previous => ({ ...previous, surname: event.target.value }))} placeholder="Surname" />
                </label>
                <label>
                  <span>Cellphone Number</span>
                  <input type="tel" value={artifactForm.cellphone || ''} onChange={event => setArtifactForm(previous => ({ ...previous, cellphone: event.target.value }))} placeholder="+27..." />
                </label>
                <label className={styles.countryField}>
                  <span>Nationality</span>
                  <div className={styles.countryControl}>
                    <Globe2 size={16} />
                    <input value={artifactForm.nationality || ''} onChange={event => updateArtifactField('nationality', event.target.value)} placeholder="Search country" autoComplete="country-name" />
                    <b>{resolveCountrySignal(artifactForm.nationality)?.code || artifactForm.nationalityCode || 'ISO'}</b>
                  </div>
                  <div className={styles.countrySuggestionRail}>
                    {searchSovereignCountries(artifactForm.nationality, 6).map(country => (
                      <button key={country.code} type="button" onClick={() => applyCountrySelection('artifact', country)}>
                        <span>{country.name}</span>
                        <small>{country.code}</small>
                      </button>
                    ))}
                  </div>
                </label>
                <label>
                  <span>Residential Address</span>
                  <div className={styles.addressControl}>
                    <input value={artifactForm.address || ''} onChange={event => updateArtifactField('address', event.target.value)} placeholder="Residential address" autoComplete="street-address" />
                    <button type="button" onClick={() => openAddressInMaps('artifact')}>
                      <MapPin size={14} /> Map
                    </button>
                  </div>
                  <small className={styles.addressMeta}>
                    {artifactAddressPosture.status.replace(/_/g, ' ')} // {artifactAddressPosture.source.replace(/_/g, ' ')} // {artifactAddressPosture.coordinatesReady ? `${artifactAddressPosture.latitude}, ${artifactAddressPosture.longitude}` : 'coordinates pending'}
                  </small>
                  {buildAddressSuggestions(artifactForm.address, artifactForm.nationality || artifactForm.countryCode).length > 0 && (
                    <div className={styles.addressSuggestionRail}>
                      {buildAddressSuggestions(artifactForm.address, artifactForm.nationality || artifactForm.countryCode).map(suggestion => (
                        <button key={suggestion.id} type="button" onClick={() => applyAddressSuggestion('artifact', suggestion)}>
                          <MapPin size={13} />
                          <span>{suggestion.label}</span>
                          <small>{suggestion.confidence.replace(/_/g, ' ')}</small>
                        </button>
                      ))}
                    </div>
                  )}
                </label>
                <label>
                  <span>Address Latitude</span>
                  <input type="number" step="0.000001" value={artifactForm.addressLatitude || ''} onChange={event => updateArtifactField('addressLatitude', event.target.value)} placeholder="-26.2041" />
                </label>
                <label>
                  <span>Address Longitude</span>
                  <input type="number" step="0.000001" value={artifactForm.addressLongitude || ''} onChange={event => updateArtifactField('addressLongitude', event.target.value)} placeholder="28.0473" />
                </label>
                <label>
                  <span>ID / Passport</span>
                  <input value={artifactForm.identityNumber || ''} onChange={event => setArtifactForm(previous => ({ ...previous, identityNumber: event.target.value }))} placeholder="Identity verification reference" />
                </label>
                <label>
                  <span>Personal Email</span>
                  <input type="email" value={artifactForm.personalEmail || ''} onChange={event => setArtifactForm(previous => ({ ...previous, personalEmail: event.target.value }))} placeholder="name@example.com" />
                </label>
                <label>
                  <span>Role / Appointment Title</span>
                  <input list="wilsy-hr-role-options" value={artifactForm.roleTitle || ''} onChange={event => updateArtifactField('roleTitle', event.target.value)} placeholder="Search role title" />
                </label>
                <label>
                  <span>Department</span>
                  <input list="wilsy-hr-department-options" value={artifactForm.department || ''} onChange={event => setArtifactForm(previous => ({ ...previous, department: event.target.value }))} placeholder="Search department" />
                </label>
                <label>
                  <span>Start Date</span>
                  <input type="date" value={normalizeDateInputValue(artifactForm.startDate)} onChange={event => setArtifactForm(previous => ({ ...previous, startDate: event.target.value }))} />
                </label>
                <label>
                  <span>Employment Type</span>
                  <select value={artifactForm.employmentType || ''} onChange={event => setArtifactForm(previous => ({ ...previous, employmentType: event.target.value }))}>
                    {EMPLOYMENT_TYPE_OPTIONS.map(option => <option key={option} value={option}>{option}</option>)}
                  </select>
                </label>
                <label className={styles.moneyField}>
                  <span>Base Remuneration</span>
                  <div>
                    <b>ZAR</b>
                    <input type="number" min="0" step="100" value={artifactForm.baseSalary || ''} onChange={event => updateArtifactField('baseSalary', event.target.value)} placeholder="0.00" />
                  </div>
                </label>
                <label>
                  <span>Payroll Country</span>
                  <select value={artifactForm.payrollCountry || 'ZA'} onChange={event => updateArtifactField('payrollCountry', event.target.value)}>
                    {PAYROLL_COUNTRY_OPTIONS.map(option => <option key={option} value={option}>{option}</option>)}
                  </select>
                </label>
                <label>
                  <span>Pay Day</span>
                  <input type="number" min="1" max="28" value={artifactForm.payDay || ZA_PAYROLL_2027.defaultPayDay} onChange={event => updateArtifactField('payDay', event.target.value)} />
                </label>
                <label>
                  <span>Pay Frequency</span>
                  <select value={artifactForm.payFrequency || ''} onChange={event => updateArtifactField('payFrequency', event.target.value)}>
                    {PAY_FREQUENCY_OPTIONS.map(option => <option key={option} value={option}>{option}</option>)}
                  </select>
                </label>
                <label>
                  <span>Benefits / Allowances</span>
                  <div className={styles.benefitPackageControl}>
                    <Heart size={16} />
                    <input list="wilsy-hr-benefit-options" value={artifactForm.benefits || ''} onChange={event => updateArtifactField('benefits', event.target.value)} placeholder="Search benefit package" />
                    <b>{resolveBenefitPackage(artifactForm.benefits).isPackage ? 'PACK' : 'PLAN'}</b>
                  </div>
                  <div className={styles.benefitPackageRail}>
                    {BENEFIT_OPTIONS.slice(0, 8).map(option => {
                      const packagePlan = resolveBenefitPackage(option);
                      return (
                        <button key={option} type="button" onClick={() => applyBenefitPackageSelection('artifact', option)}>
                          <strong>{packagePlan.name}</strong>
                          <small>{packagePlan.items.length || 1} lines // {formatMoney(packagePlan.plans.reduce((total, plan) => total + Number(plan.employerDefault || 0), 0))} employer</small>
                        </button>
                      );
                    })}
                  </div>
                </label>
                <label className={styles.moneyField}>
                  <span>Commission / Variable Pay</span>
                  <div>
                    <b>ZAR</b>
                    <input type="number" min="0" step="100" value={artifactForm.variablePay || ''} onChange={event => updateArtifactField('variablePay', event.target.value)} placeholder="0.00" />
                  </div>
                </label>
                <label className={styles.moneyField}>
                  <span>Taxable Benefits</span>
                  <div>
                    <b>ZAR</b>
                    <input type="number" min="0" step="100" value={artifactForm.taxableBenefits || ''} onChange={event => updateArtifactField('taxableBenefits', event.target.value)} placeholder="0.00" />
                  </div>
                </label>
                <label className={styles.moneyField}>
                  <span>Benefit Deductions</span>
                  <div>
                    <b>ZAR</b>
                    <input type="number" min="0" step="100" value={artifactForm.benefitDeductions || ''} onChange={event => updateArtifactField('benefitDeductions', event.target.value)} placeholder="0.00" />
                  </div>
                </label>
                <label className={styles.moneyField}>
                  <span>Other Deductions</span>
                  <div>
                    <b>ZAR</b>
                    <input type="number" min="0" step="100" value={artifactForm.otherDeductions || ''} onChange={event => updateArtifactField('otherDeductions', event.target.value)} placeholder="0.00" />
                  </div>
                </label>
                <article className={styles.benefitMathPanel} data-state={artifactRemunerationMath.grossPay ? 'ready' : 'risk'}>
                  <span>Remuneration Engine // {artifactRemunerationMath.payrollEngine}</span>
                  <strong>{formatMoney(artifactRemunerationMath.netPay)} net salary</strong>
                  <small>Gross {formatMoney(artifactRemunerationMath.grossPay)} // PAYE {formatMoney(artifactRemunerationMath.employeeTax)} // UIF {formatMoney(artifactRemunerationMath.uifEmployee)} // Pay date {artifactRemunerationMath.plannedPayDate}</small>
                  <div>
                    <b>Base {formatMoney(artifactRemunerationMath.baseSalary)}</b>
                    <b>{artifactRemunerationMath.benefitPlanName}</b>
                    <b>{artifactRemunerationMath.benefitPackage?.items?.length || 0} benefit lines</b>
                    <b>{formatMoney(artifactRemunerationMath.totalDeductions)} deductions</b>
                    <b>{formatMoney(artifactRemunerationMath.employerExposure)} employer exposure</b>
                  </div>
                </article>
                <label>
                  <span>Remuneration Effective Date</span>
                  <input type="date" value={normalizeDateInputValue(artifactForm.effectiveDate)} onChange={event => setArtifactForm(previous => ({ ...previous, effectiveDate: event.target.value }))} />
                </label>
                <label>
                  <span>Reporting Line</span>
                  <input list="wilsy-hr-manager-options" value={artifactForm.reportingLine || ''} onChange={event => setArtifactForm(previous => ({ ...previous, reportingLine: event.target.value }))} placeholder="Select manager or executive sponsor" />
                </label>
                <label>
                  <span>Workplace Model</span>
                  <select value={artifactForm.workplace || ''} onChange={event => setArtifactForm(previous => ({ ...previous, workplace: event.target.value }))}>
                    <option value="">Select workplace</option>
                    {WORKPLACE_OPTIONS.map(option => <option key={option} value={option}>{option}</option>)}
                  </select>
                </label>
                <label>
                  <span>Probation</span>
                  <input value={artifactForm.probation || ''} onChange={event => setArtifactForm(previous => ({ ...previous, probation: event.target.value }))} placeholder="3 months" />
                </label>
                <label>
                  <span>Authorized Signatory</span>
                  <input value={artifactForm.signatoryName || ''} onChange={event => setArtifactForm(previous => ({ ...previous, signatoryName: event.target.value }))} placeholder="Authorized signatory" />
                </label>
                {artifactRequiresRelations && (
                  <>
                    <article className={styles.artifactTemplatePanel} data-template={artifactForm.artifactType}>
                      <span>Employee Relations Evidence</span>
                      <strong>Record the incident, policy breach, corrective action, employee response and hearing/review path before issuing the document.</strong>
                      <div>
                        <small>Evidence-led</small>
                        <small>Employee response</small>
                        <small>HR authorization</small>
                      </div>
                    </article>
                    <label>
                      <span>Incident Date</span>
                      <input type="date" value={normalizeDateInputValue(artifactForm.incidentDate)} onChange={event => setArtifactForm(previous => ({ ...previous, incidentDate: event.target.value }))} />
                    </label>
                    <label>
                      <span>Policy / Duty Breached</span>
                      <input value={artifactForm.policyBreach || ''} onChange={event => setArtifactForm(previous => ({ ...previous, policyBreach: event.target.value }))} placeholder="Policy, duty or KPI breached" />
                    </label>
                    <label>
                      <span>Incident Summary</span>
                      <input value={artifactForm.incidentSummary || ''} onChange={event => setArtifactForm(previous => ({ ...previous, incidentSummary: event.target.value }))} placeholder="Evidence-backed summary" />
                    </label>
                    <label>
                      <span>Corrective Action</span>
                      <input value={artifactForm.correctiveAction || ''} onChange={event => setArtifactForm(previous => ({ ...previous, correctiveAction: event.target.value }))} placeholder="Expected correction or sanction" />
                    </label>
                    <label>
                      <span>Employee Response</span>
                      <input value={artifactForm.employeeResponse || ''} onChange={event => setArtifactForm(previous => ({ ...previous, employeeResponse: event.target.value }))} placeholder="Employee response or pending response" />
                    </label>
                    <label>
                      <span>Hearing / Review Date</span>
                      <input type="date" value={normalizeDateInputValue(artifactForm.hearingDate || artifactForm.reviewDate)} onChange={event => setArtifactForm(previous => ({ ...previous, hearingDate: event.target.value, reviewDate: event.target.value }))} />
                    </label>
                    <label>
                      <span>Outcome / Next Step</span>
                      <input value={artifactForm.outcome || ''} onChange={event => setArtifactForm(previous => ({ ...previous, outcome: event.target.value }))} placeholder="Review, suspension, final warning, dismissal..." />
                    </label>
                  </>
                )}
                <datalist id="wilsy-hr-role-options">{roleOptions.map(option => <option key={option} value={option} />)}</datalist>
                <datalist id="wilsy-hr-department-options">{departmentOptions.map(option => <option key={option} value={option} />)}</datalist>
                <datalist id="wilsy-hr-benefit-options">{BENEFIT_OPTIONS.map(option => <option key={option} value={option} />)}</datalist>
                <datalist id="wilsy-hr-manager-options">{managerOptions.map(option => <option key={option} value={option} />)}</datalist>
              </div>
              <footer>
                <button type="button" onClick={() => setShowArtifactModal(false)}>Cancel</button>
                <button type="button" data-primary="true" onClick={generateArtifact} disabled={isRefreshing}>
                  <CheckCircle size={15} /> Generate And Review
                </button>
              </footer>
            </section>
          </div>
        )}

        {showModal && (
          <div className={styles.hrModal} role="dialog" aria-modal="true" aria-label="HR mutation">
            <section>
              <header>
                <div>
                  <span><ShieldCheck size={16} /> HR Ledger Mutation</span>
                  <h2>{editingItem ? 'Update' : 'Create'} {formatModalTypeLabel(modalType)}</h2>
                </div>
                <button type="button" onClick={() => setShowModal(false)} aria-label="Close HR mutation"><X size={16} /></button>
              </header>
              <div className={styles.hrFormGrid}>
                {['employee', 'candidate'].includes(modalType) && (
                  <article className={styles.benefitMathPanel} data-state={identityPosture.verified ? 'ready' : 'risk'}>
                    <span>Identity And Right-To-Work Control</span>
                    <strong>{identityPosture.status.replace(/_/g, ' ')}</strong>
                    <small>{identityPosture.idType} // SA ID {identityPosture.saIdValid ? 'checksum valid' : 'requires review'} // Visa {identityPosture.visaExpired ? 'expired' : 'not expired'}</small>
                    <div>
                      <b>{identityPosture.verified ? 'Access eligible' : 'Block full access'}</b>
                      <b>{formState.rightToWorkStatus || 'Pending verification'}</b>
                    </div>
                  </article>
                )}
                {['employee', 'candidate', 'jobOpening', 'performanceReview'].includes(modalType) && (
                  <article className={styles.benefitMathPanel}>
                    <span>Role Intelligence</span>
                    <strong>{roleProfile.role}</strong>
                    <small>Duties: {roleProfile.duties.slice(0, 2).join(' // ')}</small>
                    <div>
                      {roleProfile.kpis.slice(0, 3).map(kpi => <b key={kpi}>{kpi}</b>)}
                    </div>
                  </article>
                )}
                {modalType === 'candidate' && (
                  <article className={styles.benefitMathPanel}>
                    <span>Pipeline Stage Workflow</span>
                    <strong>{candidateStageWorkflow.title}</strong>
                    <small>Evidence required: {candidateStageWorkflow.evidence.slice(0, 3).join(' // ')}</small>
                    <div>
                      {candidateStageWorkflow.nextActions.slice(0, 3).map(action => <b key={action}>{action}</b>)}
                    </div>
                  </article>
                )}
                {modalType === 'benefit' && (
                  <article className={styles.benefitMathPanel}>
                    <span>Benefit Cost Engine</span>
                    <strong>{formatMoney(benefitMath.monthlyEmployerCost)} / month</strong>
                    <small>{selectedBenefitPlan.description} // {formatMoney(benefitMath.annualEmployerCost)} annual employer exposure</small>
                    <div>
                      <b>{formatCount(benefitMath.eligibleEmployees)} eligible</b>
                      <b>{formatMoney(benefitMath.totalMonthlyPlanValue)} total monthly value</b>
                      <b>{benefitMath.packageItems.length || 1} benefit lines</b>
                      <b>{selectedBenefitPlan.payrollDeductionCode || 'Code pending'}</b>
                    </div>
                  </article>
                )}
                {modalType === 'jobOpening' && (
                  <article className={styles.benefitMathPanel}>
                    <span>Hiring Requisition</span>
                    <strong>{formState.title || 'Role pending'}</strong>
                    <small>{formState.department || 'Department pending'} // {formState.priority || 'Normal'} priority</small>
                    <div>
                      <b>{formatCount(formState.headcount || 1)} headcount</b>
                      <b>{formatMoney(formState.salaryMin)} - {formatMoney(formState.salaryMax)}</b>
                    </div>
                  </article>
                )}
                {modalType === 'payroll' && (
                  <article className={styles.benefitMathPanel}>
                    <span>Payroll Calculator // {payrollMath.payrollEngine}</span>
                    <strong>{formatMoney(payrollMath.netPay)}</strong>
                    <small>Gross {formatMoney(payrollMath.grossPay)} // PAYE {formatMoney(payrollMath.employeeTax)} // UIF {formatMoney(payrollMath.uifEmployee)} // Pay date {payrollMath.plannedPayDate}</small>
                    <div>
                      <b>{formState.employeeName || 'Employee pending'}</b>
                      <b>{payrollMath.benefitPackage?.name || 'No benefits'}</b>
                      <b>{formatMoney(payrollMath.totalDeductions)} deductions</b>
                      <b>{formatMoney(payrollMath.employerExposure)} employer exposure</b>
                      <b>{payrollMath.deductionRate}% deduction rate</b>
                    </div>
                  </article>
                )}
                {modalType === 'timeOff' && (
                  <article className={styles.benefitMathPanel} data-state={leaveMath.status === 'LEAVE_READY' ? 'ready' : 'risk'}>
                    <span>Absence And Attendance Control</span>
                    <strong>{formatCount(leaveMath.requestedDays)} working days</strong>
                    <small>Balance after request: {formatCount(leaveMath.balanceAfter)} // {leaveMath.status.replace(/_/g, ' ')}</small>
                    <div>
                      <b>{leaveMath.conflict ? 'Work log conflict' : 'No work log conflict'}</b>
                      <b>{formState.employeeName || 'Employee pending'}</b>
                    </div>
                  </article>
                )}
                {modalType === 'performanceReview' && (
                  <article className={styles.benefitMathPanel}>
                    <span>Performance Process</span>
                    <strong>{performanceMath.productivityScore}% productivity</strong>
                    <small>{performanceMath.recommendation} // Disciplinary anchor: {roleProfile.disciplinaryAnchors[0]}</small>
                    <div>
                      <b>{performanceMath.goalsMet}/{performanceMath.goalsTotal} goals</b>
                      <b>{performanceMath.goalCompletion}% goal completion</b>
                      <b>{performanceMath.activityScore}% activity score</b>
                      <b>{formState.disciplinaryRisk || 'No risk selected'}</b>
                    </div>
                    <div className={styles.performanceGraph} aria-label="Performance score graph">
                      {[
                        ['Goals', performanceMath.goalCompletion],
                        ['Activity', performanceMath.activityScore],
                        ['Productivity', performanceMath.productivityScore]
                      ].map(([label, score]) => (
                        <span key={label} style={{ '--score': `${Math.max(0, Math.min(Number(score) || 0, 100))}%` }}>
                          <i>{label}</i>
                        </span>
                      ))}
                    </div>
                  </article>
                )}
                {modalType === 'employeeWorkLog' && (
                  <article className={styles.benefitMathPanel}>
                    <span>Employee Activity Evidence</span>
                    <strong>{formState.workType || 'Daily work'}</strong>
                    <small>Every work day, achievement, incident or customer outcome becomes evidence for performance, payroll, leave and HR governance.</small>
                    <div>
                      <b>{formState.employeeName || 'Employee pending'}</b>
                      <b>{formState.workDate || 'Date pending'}</b>
                      <b>{formatCount(formState.impactScore || 0)} impact</b>
                      <b>{formatCount(formState.performanceScore || 0)} performance</b>
                    </div>
                  </article>
                )}
                {modalType === 'employeeRelations' && (
                  <article className={styles.benefitMathPanel} data-state={/closed|issued|hearing/i.test(formState.status || '') ? 'ready' : 'risk'}>
                    <span>Employee Relations Proof Chain</span>
                    <strong>{formState.relationsActionType || 'Relations action pending'}</strong>
                    <small>Evidence, policy breach, employee response, hearing/review date and outcome are required before formal action is defensible.</small>
                    <div>
                      <b>{formState.employeeName || 'Employee pending'}</b>
                      <b>{formState.incidentDate || 'Incident date pending'}</b>
                      <b>{formState.hearingDate || 'Hearing pending'}</b>
                      <b>{formState.status || 'DRAFT'}</b>
                    </div>
                  </article>
                )}
                {(FIELD_CONFIG[modalType] || FIELD_CONFIG.employee).map(renderMutationField)}
              </div>
              <footer>
                <button type="button" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="button" data-primary="true" onClick={saveMutation} disabled={isRefreshing}>
                  <CheckCircle size={15} /> Save HR Record
                </button>
              </footer>
            </section>
          </div>
        )}
      </div>
    </WilsyOSDashboardChrome>
  );
};

export default HrDashboard;
