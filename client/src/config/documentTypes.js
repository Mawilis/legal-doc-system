// ~/client/src/config/documentTypes.js

export const DOCUMENT_CATEGORIES = {
    LITIGATION: 'Litigation & Court Process',
    PRE_LITIGATION: 'Pre-litigation & Settlement',
    PROPERTY: 'Property & Civil',
    FAMILY: 'Family Law',
    COMMERCIAL: 'Commercial & Employment'
};

export const DOCUMENT_TYPES = {
    [DOCUMENT_CATEGORIES.LITIGATION]: [
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
        'Application for Summary Judgment'
    ],
    [DOCUMENT_CATEGORIES.PRE_LITIGATION]: [
        'Letter of Demand',
        'Settlement Agreement',
        'Acknowledgment of Debt',
        'Offer to Settle'
    ],
    [DOCUMENT_CATEGORIES.PROPERTY]: [
        'Lease Agreement',
        'Sale Agreement',
        'Deed of Transfer',
        'Power of Attorney',
        'Affidavit of Loss',
        'Eviction Notice'
    ],
    [DOCUMENT_CATEGORIES.FAMILY]: [
        'Parenting Plan',
        'Maintenance Application',
        'Protection Order',
        'Divorce Settlement Agreement'
    ],
    [DOCUMENT_CATEGORIES.COMMERCIAL]: [
        'Employment Contract',
        'Restraint of Trade Agreement',
        'Shareholders Agreement',
        'Loan Agreement',
        'Service Level Agreement',
        'Non-Disclosure Agreement (NDA)',
        'Indemnity Form'
    ]
};

// Helper to determine which form fields to show
export const getFormType = (category) => {
    // Litigation & Family usually involve court case numbers and plaintiff/defendants
    if (
        category === DOCUMENT_CATEGORIES.LITIGATION ||
        category === DOCUMENT_CATEGORIES.FAMILY
    ) {
        return 'LITIGATION';
    }
    // Commercial, Property, and Pre-litigation usually involve Parties (A vs B) and Contracts
    return 'AGREEMENT';
};