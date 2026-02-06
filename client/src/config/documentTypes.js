/**
 * File: client/src/config/documentTypes.js
 * STATUS: EPITOME | IMMUTABLE | FINAL | PRODUCTION-READY
 * -----------------------------------------------------------------------------
 * PURPOSE
 * - Single Source of Truth for all legal document categories and types
 * - Drives UI form rendering, templates, validation, and tenant onboarding
 *
 * COLLABORATION COMMENTS
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - REVIEWERS: @legal, @product, @design, @security, @platform
 * - OPERATIONS: This file is intentionally frozen to prevent runtime mutation.
 * - TESTING: Add unit tests that assert immutability and mapping completeness.
 *
 * CODE EXPLANATION
 * - DOCUMENT_CATEGORIES: high level buckets used across the app and API.
 * - DOCUMENT_TYPES: exhaustive lists per category; used to populate selectors.
 * - DOCUMENT_METADATA_SCHEMA: recommended fields per category to drive form fields.
 * - getFormType: maps category to UI form family (LITIGATION or AGREEMENT).
 * - getRequiredFieldsForType: returns canonical required fields for a specific doc type.
 * -----------------------------------------------------------------------------
 */

export const DOCUMENT_CATEGORIES = Object.freeze({
    LITIGATION: 'Litigation & Court Process',
    PRE_LITIGATION: 'Pre-litigation & Settlement',
    PROPERTY: 'Property & Civil',
    FAMILY: 'Family Law',
    COMMERCIAL: 'Commercial & Employment',
    CORPORATE: 'Corporate & Governance',
    INTELLECTUAL_PROPERTY: 'Intellectual Property',
    TAX_AND_FINANCE: 'Tax & Finance',
    ADMINISTRATIVE: 'Administrative & Regulatory',
    PROBATE: 'Wills, Estates & Probate',
    IMMIGRATION: 'Immigration & Visas',
    CONSUMER: 'Consumer Protection',
    CRIMINAL: 'Criminal Law',
    ENVIRONMENTAL: 'Environmental & Planning'
});

/**
 * DOCUMENT_TYPES
 * - Exhaustive, curated list of common and specialized legal instruments.
 * - Keep entries human-readable; templates map to these keys.
 */
export const DOCUMENT_TYPES = Object.freeze({
    [DOCUMENT_CATEGORIES.LITIGATION]: Object.freeze([
        'Summons (Simple & Combined)',
        'Notice of Motion',
        'Founding Affidavit',
        'Answering Affidavit',
        'Replying Affidavit',
        'Warrant of Execution',
        'Warrant of Ejectment',
        'Section 65 Financial Inquiry',
        'Garnishee Order (Emoluments Attachment)',
        'Subpoena (ad testificandum / duces tecum)',
        'Divorce Summons',
        'Interdict',
        'Court Directive',
        'Default Judgment',
        'Notice of Set Down',
        'Notice of Intention to Defend',
        'Notice of Withdrawal',
        'Notice of Bar',
        'Plea',
        'Special Plea',
        'Counterclaim',
        'Replication',
        'Application for Summary Judgment',
        'Application for Leave to Appeal',
        'Heads of Argument',
        'Practice Note',
        'Judgment Summaries',
        'Enforcement Application'
    ]),

    [DOCUMENT_CATEGORIES.PRE_LITIGATION]: Object.freeze([
        'Letter of Demand',
        'Settlement Agreement',
        'Acknowledgment of Debt',
        'Offer to Settle',
        'Cease and Desist Letter',
        'Pre-action Protocol Letter',
        'Mediation Agreement',
        'Payment Plan Agreement'
    ]),

    [DOCUMENT_CATEGORIES.PROPERTY]: Object.freeze([
        'Lease Agreement',
        'Commercial Lease',
        'Residential Lease',
        'Sale Agreement',
        'Deed of Transfer',
        'Power of Attorney (Property)',
        'Affidavit of Loss',
        'Eviction Notice',
        'Bond Cancellation Instruction',
        'Title Search Report',
        'Sectional Title Transfer',
        'Property Transfer Instruction'
    ]),

    [DOCUMENT_CATEGORIES.FAMILY]: Object.freeze([
        'Parenting Plan',
        'Maintenance Application',
        'Protection Order',
        'Divorce Settlement Agreement',
        'Divorce Consent Paper',
        'Ante-nuptial Contract',
        'Post-nuptial Agreement',
        'Adoption Papers',
        'Guardianship Application'
    ]),

    [DOCUMENT_CATEGORIES.COMMERCIAL]: Object.freeze([
        'Employment Contract',
        'Restraint of Trade Agreement',
        'Shareholders Agreement',
        'Loan Agreement',
        'Service Level Agreement',
        'Non-Disclosure Agreement (NDA)',
        'Indemnity Form',
        'Consulting Agreement',
        'Master Services Agreement',
        'Statement of Work',
        'Supplier Agreement',
        'Distribution Agreement'
    ]),

    [DOCUMENT_CATEGORIES.CORPORATE]: Object.freeze([
        'Memorandum of Incorporation',
        'Board Resolution',
        'Minutes of Meeting',
        'Director Appointment Letter',
        'Share Issue Resolution',
        'Company Secretarial Pack',
        'Annual General Meeting Notice',
        'Corporate Governance Policy'
    ]),

    [DOCUMENT_CATEGORIES.INTELLECTUAL_PROPERTY]: Object.freeze([
        'Trademark Application',
        'Patent Assignment',
        'Copyright Assignment',
        'IP Licensing Agreement',
        'Confidential Disclosure Agreement',
        'Technology Transfer Agreement'
    ]),

    [DOCUMENT_CATEGORIES.TAX_AND_FINANCE]: Object.freeze([
        'Tax Clearance Application',
        'VAT Registration',
        'Financial Statement',
        'Loan Security Agreement',
        'Guarantee Agreement',
        'Tax Opinion Letter'
    ]),

    [DOCUMENT_CATEGORIES.ADMINISTRATIVE]: Object.freeze([
        'Regulatory Filing',
        'Compliance Report',
        'Permit Application',
        'Licensing Agreement',
        'Notice of Compliance',
        'Administrative Appeal'
    ]),

    [DOCUMENT_CATEGORIES.PROBATE]: Object.freeze([
        'Last Will and Testament',
        'Letter of Executorship',
        'Estate Inventory',
        'Grant of Probate Application',
        'Intestate Administration Papers',
        'Estate Distribution Agreement'
    ]),

    [DOCUMENT_CATEGORIES.IMMIGRATION]: Object.freeze([
        'Work Visa Application',
        'Permanent Residence Application',
        'Study Visa Application',
        'Immigration Appeal',
        'Sponsorship Undertaking'
    ]),

    [DOCUMENT_CATEGORIES.CONSUMER]: Object.freeze([
        'Consumer Complaint Letter',
        'Product Liability Claim',
        'Refund Agreement',
        'Consumer Settlement'
    ]),

    [DOCUMENT_CATEGORIES.CRIMINAL]: Object.freeze([
        'Charge Sheet',
        'Bail Application',
        'Plea Bargain Agreement',
        'Victim Impact Statement',
        'Criminal Appeal Notice'
    ]),

    [DOCUMENT_CATEGORIES.ENVIRONMENTAL]: Object.freeze([
        'Environmental Impact Assessment',
        'Permit to Operate Application',
        'Compliance Undertaking',
        'Remediation Plan'
    ])
});

/**
 * DOCUMENT_METADATA_SCHEMA
 * - Canonical fields to drive dynamic form rendering and template population.
 * - Each category maps to an ordered list of fields commonly required.
 * - Fields are descriptive tokens; UI maps tokens to labels, input types, and validators.
 */
export const DOCUMENT_METADATA_SCHEMA = Object.freeze({
    [DOCUMENT_CATEGORIES.LITIGATION]: Object.freeze([
        'caseNumber',
        'courtName',
        'plaintiff',
        'defendant',
        'attorney',
        'opposingAttorney',
        'hearingDate',
        'reliefSought',
        'supportingAffidavits'
    ]),

    [DOCUMENT_CATEGORIES.PRE_LITIGATION]: Object.freeze([
        'claimant',
        'respondent',
        'amountClaimed',
        'dueDate',
        'settlementTerms',
        'deadline'
    ]),

    [DOCUMENT_CATEGORIES.PROPERTY]: Object.freeze([
        'propertyDescription',
        'seller',
        'buyer',
        'purchasePrice',
        'leaseTerm',
        'landSurveyNumber',
        'bondDetails'
    ]),

    [DOCUMENT_CATEGORIES.FAMILY]: Object.freeze([
        'applicant',
        'respondent',
        'children',
        'custodyArrangements',
        'maintenanceAmount',
        'marriageDate'
    ]),

    [DOCUMENT_CATEGORIES.COMMERCIAL]: Object.freeze([
        'partyA',
        'partyB',
        'effectiveDate',
        'term',
        'scopeOfWork',
        'fees',
        'terminationClause'
    ]),

    [DOCUMENT_CATEGORIES.CORPORATE]: Object.freeze([
        'companyName',
        'registrationNumber',
        'directorList',
        'shareStructure',
        'resolutionDate'
    ]),

    [DOCUMENT_CATEGORIES.INTELLECTUAL_PROPERTY]: Object.freeze([
        'owner',
        'title',
        'registrationNumber',
        'jurisdiction',
        'effectiveDate'
    ]),

    [DOCUMENT_CATEGORIES.TAX_AND_FINANCE]: Object.freeze([
        'taxYear',
        'taxpayer',
        'amount',
        'filingDate',
        'referenceNumber'
    ]),

    [DOCUMENT_CATEGORIES.ADMINISTRATIVE]: Object.freeze([
        'authority',
        'applicationNumber',
        'applicant',
        'submissionDate'
    ]),

    [DOCUMENT_CATEGORIES.PROBATE]: Object.freeze([
        'deceasedName',
        'dateOfDeath',
        'executor',
        'estateValue',
        'beneficiaries'
    ]),

    [DOCUMENT_CATEGORIES.IMMIGRATION]: Object.freeze([
        'applicantName',
        'passportNumber',
        'visaType',
        'sponsor',
        'applicationDate'
    ]),

    [DOCUMENT_CATEGORIES.CONSUMER]: Object.freeze([
        'consumerName',
        'product',
        'purchaseDate',
        'claimAmount',
        'vendor'
    ]),

    [DOCUMENT_CATEGORIES.CRIMINAL]: Object.freeze([
        'accused',
        'charge',
        'policeCaseNumber',
        'bailConditions',
        'courtDate'
    ]),

    [DOCUMENT_CATEGORIES.ENVIRONMENTAL]: Object.freeze([
        'siteLocation',
        'projectDescription',
        'impactSummary',
        'mitigationMeasures'
    ])
});

/**
 * getFormType
 * - Returns 'LITIGATION' for court-centric documents, otherwise 'AGREEMENT'.
 */
export const getFormType = (category) => {
    if (
        category === DOCUMENT_CATEGORIES.LITIGATION ||
        category === DOCUMENT_CATEGORIES.FAMILY ||
        category === DOCUMENT_CATEGORIES.CRIMINAL ||
        category === DOCUMENT_CATEGORIES.PROBATE
    ) {
        return 'LITIGATION';
    }
    return 'AGREEMENT';
};

/**
 * getRequiredFieldsForType
 * - Returns the canonical required metadata fields for a specific document type.
 * - Falls back to the category schema when a type-specific mapping is not present.
 */
const TYPE_OVERRIDES = Object.freeze({
    'Summons (Simple & Combined)': ['caseNumber', 'courtName', 'plaintiff', 'defendant', 'reliefSought'],
    'Letter of Demand': ['claimant', 'respondent', 'amountClaimed', 'dueDate'],
    'Lease Agreement': ['propertyDescription', 'lessor', 'lessee', 'leaseTerm', 'rent'],
    'Employment Contract': ['partyA', 'partyB', 'effectiveDate', 'term', 'fees'],
    'Last Will and Testament': ['deceasedName', 'executor', 'beneficiaries', 'estateValue'],
    'Trademark Application': ['owner', 'title', 'jurisdiction', 'registrationNumber']
});

export const getRequiredFieldsForType = (category, type) => {
    if (TYPE_OVERRIDES[type]) return TYPE_OVERRIDES[type];
    return DOCUMENT_METADATA_SCHEMA[category] || [];
};

/* -------------------------
   FINAL NOTES
   - This module is intentionally immutable. If you need to extend the ontology,
     create a migration script and version the ontology.
   - Keep human-readable labels here; template keys map to these strings.
   - Add unit tests that assert:
     * DOCUMENT_CATEGORIES and DOCUMENT_TYPES are frozen
     * getFormType returns expected values
     * getRequiredFieldsForType returns arrays for known types
   ------------------------- */
