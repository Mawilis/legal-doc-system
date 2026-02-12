/**
 * Wilsy OS - Document Template Registry
 * =======================================
 * FORENSIC-GRADE DOCUMENT ONTOLOGY ENGINE
 * 
 * @version 2.0.0
 * @author Wilson Khanyezi - Chief Quantum Sentinel
 * @copyright Wilsy OS 2026
 * 
 * @compliance POPIA §19 - Data minimization and purpose limitation
 * @compliance ECT Act §15 - Admissibility of data messages
 * @compliance Companies Act 71 of 2008 - Retention requirements
 */

/* eslint-env node */

// =================================================================================
// DOCUMENT TYPES - AUTHORITATIVE SOURCE - INVESTOR GRADE
// =================================================================================

/**
 * @readonly
 * @enum {string}
 */
const DOCUMENT_CATEGORIES = {
    LITIGATION: 'LITIGATION',
    CONVEYANCING: 'CONVEYANCING',
    CORPORATE: 'CORPORATE',
    ESTATE: 'ESTATE',
    CONTRACT: 'CONTRACT',
    COMPLIANCE: 'COMPLIANCE'
};

/**
 * @readonly
 * @enum {Object}
 */
const DOCUMENT_TYPES = {
    // =============================================================================
    // LITIGATION - High Court, Magistrates Court, Supreme Court of Appeal
    // =============================================================================
    SUMMONS: {
        id: 'SUMMONS',
        category: DOCUMENT_CATEGORIES.LITIGATION,
        version: '2.1.0',
        template: 'templates/litigation/summons-v2.1.0.docx',
        schema: 'schemas/litigation/summons.schema.json',
        validators: {
            court: { 
                required: true, 
                pattern: /^[A-Z]{2,3}-\d{4}-\d{6}$/,
                message: 'Court reference must be in format: GP-2026-123456'
            },
            plaintiff: { 
                required: true, 
                minLength: 2,
                message: 'Plaintiff name must be at least 2 characters'
            },
            defendant: { 
                required: true, 
                minLength: 2,
                message: 'Defendant name must be at least 2 characters'
            },
            caseNumber: { 
                required: true, 
                pattern: /^\d{4}\/\d{6}$/,
                message: 'Case number must be in format: 2026/123456'
            }
        },
        retentionPeriod: 10,
        confidentialityDefault: 'CONFIDENTIAL',
        piiFields: ['plaintiff.idNumber', 'defendant.idNumber'],
        compliance: ['POPIA §19', 'ECT Act §15'],
        jurisdiction: 'ZA',
        lastReviewed: '2026-01-15'
    },

    PLEADING: {
        id: 'PLEADING',
        category: DOCUMENT_CATEGORIES.LITIGATION,
        version: '2.0.0',
        template: 'templates/litigation/pleading-v2.0.0.docx',
        schema: 'schemas/litigation/pleading.schema.json',
        validators: {
            court: { 
                required: true, 
                pattern: /^[A-Z]{2,3}-\d{4}-\d{6}$/ 
            },
            filingParty: { 
                required: true 
            },
            documentType: { 
                required: true, 
                enum: ['DECLARATION', 'ANSWER', 'REPLY', 'COUNTERCLAIM'],
                message: 'Must be one of: DECLARATION, ANSWER, REPLY, COUNTERCLAIM'
            }
        },
        retentionPeriod: 10,
        confidentialityDefault: 'CONFIDENTIAL',
        compliance: ['POPIA §19', 'ECT Act §15'],
        jurisdiction: 'ZA',
        lastReviewed: '2026-01-15'
    },

    AFFIDAVIT: {
        id: 'AFFIDAVIT',
        category: DOCUMENT_CATEGORIES.LITIGATION,
        version: '1.5.0',
        template: 'templates/litigation/affidavit-v1.5.0.docx',
        schema: 'schemas/litigation/affidavit.schema.json',
        validators: {
            deponent: { required: true },
            commissioner: { required: true },
            date: { required: true, type: 'date' },
            jurat: { 
                required: true, 
                pattern: /^Thus sworn and subscribed before me at .+ on this \d+ day of .+ 20\d{2}$/,
                message: 'Jurat must be in proper legal format'
            }
        },
        retentionPeriod: 10,
        confidentialityDefault: 'CONFIDENTIAL',
        compliance: ['Justices of the Peace Act', 'ECT Act §15'],
        jurisdiction: 'ZA',
        lastReviewed: '2026-01-20'
    },

    NOTICE_OF_MOTION: {
        id: 'NOTICE_OF_MOTION',
        category: DOCUMENT_CATEGORIES.LITIGATION,
        version: '1.2.0',
        template: 'templates/litigation/notice-of-motion-v1.2.0.docx',
        schema: 'schemas/litigation/notice-of-motion.schema.json',
        validators: {
            court: { required: true },
            applicant: { required: true },
            respondent: { required: true },
            reliefSought: { 
                required: true, 
                minLength: 50,
                message: 'Relief sought must be at least 50 characters'
            }
        },
        retentionPeriod: 10,
        confidentialityDefault: 'CONFIDENTIAL',
        compliance: ['Uniform Rules of Court', 'ECT Act §15'],
        jurisdiction: 'ZA',
        lastReviewed: '2026-01-22'
    },

    HEADS_OF_ARGUMENT: {
        id: 'HEADS_OF_ARGUMENT',
        category: DOCUMENT_CATEGORIES.LITIGATION,
        version: '3.0.0',
        template: 'templates/litigation/heads-of-argument-v3.0.0.docx',
        schema: 'schemas/litigation/heads-of-argument.schema.json',
        validators: {
            court: { required: true },
            counsel: { required: true },
            authorities: { required: false },
            hearingDate: { required: true, type: 'date' }
        },
        retentionPeriod: 5,
        confidentialityDefault: 'RESTRICTED',
        compliance: ['Legal Practice Act 28 of 2014'],
        jurisdiction: 'ZA',
        lastReviewed: '2026-01-25'
    },

    // =============================================================================
    // CONVEYANCING - Deeds Office, Property Transfers, Bonds
    // =============================================================================
    DEED_OF_SALE: {
        id: 'DEED_OF_SALE',
        category: DOCUMENT_CATEGORIES.CONVEYANCING,
        version: '4.2.0',
        template: 'templates/conveyancing/deed-of-sale-v4.2.0.docx',
        schema: 'schemas/conveyancing/deed-of-sale.schema.json',
        validators: {
            seller: { required: true },
            purchaser: { required: true },
            property: { 
                required: true, 
                pattern: /^[A-Z0-9]+\/[A-Z0-9]+\/[A-Z0-9]+$/,
                message: 'Property reference must be in format: T1234/2025/001'
            },
            purchasePrice: { 
                required: true, 
                min: 1,
                message: 'Purchase price must be greater than 0'
            },
            transferDate: { required: true, type: 'date' }
        },
        retentionPeriod: 20,
        confidentialityDefault: 'HIGHLY_CONFIDENTIAL',
        piiFields: ['seller.idNumber', 'purchaser.idNumber'],
        compliance: ['Deeds Registries Act 47 of 1937', 'POPIA §19'],
        jurisdiction: 'ZA',
        lastReviewed: '2026-01-18'
    },

    TITLE_DEED: {
        id: 'TITLE_DEED',
        category: DOCUMENT_CATEGORIES.CONVEYANCING,
        version: '1.0.0',
        template: 'templates/conveyancing/title-deed-v1.0.0.pdf',
        schema: 'schemas/conveyancing/title-deed.schema.json',
        validators: {
            deedNumber: { 
                required: true, 
                pattern: /^T\d{7}\/\d{4}$/,
                message: 'Deed number must be in format: T1234567/2026'
            },
            owner: { required: true },
            propertyDescription: { required: true },
            extent: { required: true },
            registrationDate: { required: true, type: 'date' }
        },
        retentionPeriod: 100,
        confidentialityDefault: 'RESTRICTED',
        compliance: ['Deeds Registries Act 47 of 1937'],
        jurisdiction: 'ZA',
        lastReviewed: '2026-01-10'
    },

    MORTGAGE_BOND: {
        id: 'MORTGAGE_BOND',
        category: DOCUMENT_CATEGORIES.CONVEYANCING,
        version: '3.1.0',
        template: 'templates/conveyancing/mortgage-bond-v3.1.0.docx',
        schema: 'schemas/conveyancing/mortgage-bond.schema.json',
        validators: {
            mortgagor: { required: true },
            mortgagee: { required: true },
            bondAmount: { 
                required: true, 
                min: 1,
                message: 'Bond amount must be greater than 0'
            },
            property: { required: true },
            interestRate: { 
                required: true, 
                min: 0, 
                max: 100,
                message: 'Interest rate must be between 0 and 100'
            }
        },
        retentionPeriod: 30,
        confidentialityDefault: 'HIGHLY_CONFIDENTIAL',
        piiFields: ['mortgagor.idNumber'],
        compliance: ['National Credit Act 34 of 2005', 'POPIA §19'],
        jurisdiction: 'ZA',
        lastReviewed: '2026-01-21'
    },

    TRANSFER_DOCUMENT: {
        id: 'TRANSFER_DOCUMENT',
        category: DOCUMENT_CATEGORIES.CONVEYANCING,
        version: '2.0.0',
        template: 'templates/conveyancing/transfer-document-v2.0.0.docx',
        schema: 'schemas/conveyancing/transfer-document.schema.json',
        validators: {
            transferor: { required: true },
            transferee: { required: true },
            property: { required: true },
            consideration: { required: true, min: 1 },
            transferDate: { required: true, type: 'date' }
        },
        retentionPeriod: 20,
        confidentialityDefault: 'HIGHLY_CONFIDENTIAL',
        compliance: ['Deeds Registries Act 47 of 1937'],
        jurisdiction: 'ZA',
        lastReviewed: '2026-01-19'
    },

    // =============================================================================
    // CORPORATE - Companies and Intellectual Property Commission (CIPC)
    // =============================================================================
    MEMORANDUM_OF_INCORPORATION: {
        id: 'MEMORANDUM_OF_INCORPORATION',
        category: DOCUMENT_CATEGORIES.CORPORATE,
        version: '5.0.0',
        template: 'templates/corporate/moi-v5.0.0.docx',
        schema: 'schemas/corporate/moi.schema.json',
        validators: {
            companyName: { required: true },
            registrationNumber: { 
                required: true, 
                pattern: /^\d{4}\/\d{6}\/07$/,
                message: 'Registration number must be in format: 2026/123456/07'
            },
            incorporators: { 
                required: true, 
                minItems: 1,
                message: 'At least one incorporator is required'
            },
            shareCapital: { 
                required: true, 
                min: 1,
                message: 'Share capital must be greater than 0'
            }
        },
        retentionPeriod: 20,
        confidentialityDefault: 'INTERNAL',
        compliance: ['Companies Act 71 of 2008'],
        jurisdiction: 'ZA',
        lastReviewed: '2026-01-14'
    },

    SHAREHOLDERS_AGREEMENT: {
        id: 'SHAREHOLDERS_AGREEMENT',
        category: DOCUMENT_CATEGORIES.CORPORATE,
        version: '2.3.0',
        template: 'templates/corporate/shareholders-agreement-v2.3.0.docx',
        schema: 'schemas/corporate/shareholders-agreement.schema.json',
        validators: {
            company: { required: true },
            shareholders: { 
                required: true, 
                minItems: 2,
                message: 'At least 2 shareholders are required'
            },
            shareholding: { required: true },
            directors: { required: true }
        },
        retentionPeriod: 20,
        confidentialityDefault: 'HIGHLY_CONFIDENTIAL',
        compliance: ['Companies Act 71 of 2008'],
        jurisdiction: 'ZA',
        lastReviewed: '2026-01-16'
    },

    DIRECTORS_RESOLUTION: {
        id: 'DIRECTORS_RESOLUTION',
        category: DOCUMENT_CATEGORIES.CORPORATE,
        version: '1.8.0',
        template: 'templates/corporate/directors-resolution-v1.8.0.docx',
        schema: 'schemas/corporate/directors-resolution.schema.json',
        validators: {
            company: { required: true },
            date: { required: true, type: 'date' },
            resolution: { 
                required: true, 
                minLength: 100,
                message: 'Resolution text must be at least 100 characters'
            },
            directorsPresent: { 
                required: true, 
                minItems: 1,
                message: 'At least one director must be present'
            }
        },
        retentionPeriod: 10,
        confidentialityDefault: 'CONFIDENTIAL',
        compliance: ['Companies Act 71 of 2008'],
        jurisdiction: 'ZA',
        lastReviewed: '2026-01-17'
    },

    // =============================================================================
    // ESTATE - Wills, Trusts, Administration of Estates
    // =============================================================================
    LAST_WILL_AND_TESTAMENT: {
        id: 'LAST_WILL_AND_TESTAMENT',
        category: DOCUMENT_CATEGORIES.ESTATE,
        version: '3.4.0',
        template: 'templates/estate/last-will-v3.4.0.docx',
        schema: 'schemas/estate/will.schema.json',
        validators: {
            testator: { required: true },
            date: { required: true, type: 'date' },
            executors: { 
                required: true, 
                minItems: 1,
                message: 'At least one executor is required'
            },
            beneficiaries: { 
                required: true, 
                minItems: 1,
                message: 'At least one beneficiary is required'
            },
            witnesses: { 
                required: true, 
                minItems: 2,
                message: 'Two witnesses are required'
            }
        },
        retentionPeriod: 50,
        confidentialityDefault: 'RESTRICTED',
        piiFields: ['testator.idNumber', 'beneficiaries[].idNumber'],
        compliance: ['Wills Act 7 of 1953', 'POPIA §19'],
        jurisdiction: 'ZA',
        lastReviewed: '2026-01-12'
    },

    CODICIL: {
        id: 'CODICIL',
        category: DOCUMENT_CATEGORIES.ESTATE,
        version: '1.2.0',
        template: 'templates/estate/codicil-v1.2.0.docx',
        schema: 'schemas/estate/codicil.schema.json',
        validators: {
            willReference: { required: true },
            testator: { required: true },
            amendments: { required: true },
            date: { required: true, type: 'date' }
        },
        retentionPeriod: 50,
        confidentialityDefault: 'RESTRICTED',
        compliance: ['Wills Act 7 of 1953'],
        jurisdiction: 'ZA',
        lastReviewed: '2026-01-12'
    },

    LETTERS_OF_ADMINISTRATION: {
        id: 'LETTERS_OF_ADMINISTRATION',
        category: DOCUMENT_CATEGORIES.ESTATE,
        version: '2.0.0',
        template: 'templates/estate/letters-of-administration-v2.0.0.docx',
        schema: 'schemas/estate/letters-of-administration.schema.json',
        validators: {
            deceased: { required: true },
            executor: { required: true },
            court: { required: true },
            grantDate: { required: true, type: 'date' }
        },
        retentionPeriod: 30,
        confidentialityDefault: 'CONFIDENTIAL',
        compliance: ['Administration of Estates Act 66 of 1965'],
        jurisdiction: 'ZA',
        lastReviewed: '2026-01-13'
    },

    // =============================================================================
    // CONTRACT - Commercial and Employment Agreements
    // =============================================================================
    SERVICE_AGREEMENT: {
        id: 'SERVICE_AGREEMENT',
        category: DOCUMENT_CATEGORIES.CONTRACT,
        version: '4.1.0',
        template: 'templates/contract/service-agreement-v4.1.0.docx',
        schema: 'schemas/contract/service-agreement.schema.json',
        validators: {
            serviceProvider: { required: true },
            client: { required: true },
            services: { required: true },
            term: { required: true },
            fees: { 
                required: true, 
                min: 0,
                message: 'Fees must be a non-negative number'
            }
        },
        retentionPeriod: 7,
        confidentialityDefault: 'CONFIDENTIAL',
        compliance: ['Consumer Protection Act 68 of 2008'],
        jurisdiction: 'ZA',
        lastReviewed: '2026-01-19'
    },

    NON_DISCLOSURE_AGREEMENT: {
        id: 'NON_DISCLOSURE_AGREEMENT',
        category: DOCUMENT_CATEGORIES.CONTRACT,
        version: '2.2.0',
        template: 'templates/contract/nda-v2.2.0.docx',
        schema: 'schemas/contract/nda.schema.json',
        validators: {
            disclosingParty: { required: true },
            receivingParty: { required: true },
            effectiveDate: { required: true, type: 'date' },
            term: { 
                required: true, 
                min: 1,
                message: 'Term must be at least 1 year'
            }
        },
        retentionPeriod: 7,
        confidentialityDefault: 'HIGHLY_CONFIDENTIAL',
        compliance: ['Common Law'],
        jurisdiction: 'ZA',
        lastReviewed: '2026-01-20'
    },

    EMPLOYMENT_CONTRACT: {
        id: 'EMPLOYMENT_CONTRACT',
        category: DOCUMENT_CATEGORIES.CONTRACT,
        version: '3.0.0',
        template: 'templates/contract/employment-contract-v3.0.0.docx',
        schema: 'schemas/contract/employment-contract.schema.json',
        validators: {
            employer: { required: true },
            employee: { required: true },
            position: { required: true },
            startDate: { required: true, type: 'date' },
            remuneration: { 
                required: true, 
                min: 1,
                message: 'Remuneration must be greater than 0'
            }
        },
        retentionPeriod: 10,
        confidentialityDefault: 'CONFIDENTIAL',
        piiFields: ['employee.idNumber', 'employee.bankAccount'],
        compliance: ['Basic Conditions of Employment Act 75 of 1997', 'POPIA §19'],
        jurisdiction: 'ZA',
        lastReviewed: '2026-01-21'
    },

    // =============================================================================
    // COMPLIANCE - Regulatory and Statutory Compliance
    // =============================================================================
    POPIA_REGISTER: {
        id: 'POPIA_REGISTER',
        category: DOCUMENT_CATEGORIES.COMPLIANCE,
        version: '1.0.0',
        template: 'templates/compliance/popia-register-v1.0.0.xlsx',
        schema: 'schemas/compliance/popia-register.schema.json',
        validators: {
            responsibleParty: { required: true },
            informationOfficer: { required: true },
            processingActivities: { 
                required: true, 
                minItems: 1,
                message: 'At least one processing activity must be recorded'
            }
        },
        retentionPeriod: 7,
        confidentialityDefault: 'INTERNAL',
        compliance: ['POPIA 4 of 2013'],
        jurisdiction: 'ZA',
        lastReviewed: '2026-01-11'
    },

    PAIA_MANUAL: {
        id: 'PAIA_MANUAL',
        category: DOCUMENT_CATEGORIES.COMPLIANCE,
        version: '2.0.0',
        template: 'templates/compliance/paia-manual-v2.0.0.docx',
        schema: 'schemas/compliance/paia-manual.schema.json',
        validators: {
            company: { required: true },
            section51Officer: { required: true },
            categories: { required: true }
        },
        retentionPeriod: 5,
        confidentialityDefault: 'PUBLIC',
        compliance: ['PAIA 2 of 2000'],
        jurisdiction: 'ZA',
        lastReviewed: '2026-01-11'
    },

    FICA_RECORD: {
        id: 'FICA_RECORD',
        category: DOCUMENT_CATEGORIES.COMPLIANCE,
        version: '1.3.0',
        template: 'templates/compliance/fica-record-v1.3.0.docx',
        schema: 'schemas/compliance/fica-record.schema.json',
        validators: {
            client: { required: true },
            verificationDate: { required: true, type: 'date' },
            verificationMethod: { required: true },
            documents: { 
                required: true, 
                minItems: 1,
                message: 'At least one identification document is required'
            }
        },
        retentionPeriod: 5,
        confidentialityDefault: 'HIGHLY_CONFIDENTIAL',
        piiFields: ['client.idNumber', 'client.passportNumber'],
        compliance: ['FICA 38 of 2001', 'POPIA §19'],
        jurisdiction: 'ZA',
        lastReviewed: '2026-01-16'
    },

    SARS_RETURN: {
        id: 'SARS_RETURN',
        category: DOCUMENT_CATEGORIES.COMPLIANCE,
        version: '2026.1',
        template: 'templates/compliance/sars-return-2026.1.pdf',
        schema: 'schemas/compliance/sars-return.schema.json',
        validators: {
            taxReference: { 
                required: true, 
                pattern: /^\d{10}$/,
                message: 'Tax reference number must be 10 digits'
            },
            taxYear: { 
                required: true, 
                pattern: /^20\d{2}$/,
                message: 'Tax year must be in format: 2026'
            },
            submissionDate: { required: true, type: 'date' }
        },
        retentionPeriod: 5,
        confidentialityDefault: 'RESTRICTED',
        compliance: ['Tax Administration Act 28 of 2011'],
        jurisdiction: 'ZA',
        lastReviewed: '2026-01-22'
    }
};

// =================================================================================
// DOCUMENT TEMPLATE REGISTRY - FORENSIC-GRADE IMPLEMENTATION
// =================================================================================

/**
 * @class DocumentTemplateRegistry
 * @description Authoritative registry for all legal document types in South African law
 * 
 * @security All methods are pure - no side effects
 * @compliance POPIA §19, ECT Act §15, Companies Act 71 of 2008
 */
class DocumentTemplateRegistry {
    constructor() {
        this._templates = DOCUMENT_TYPES;
        this._categories = DOCUMENT_CATEGORIES;
        this._version = '2.0.0';
    }

    /**
     * Get template by document type
     * @param {string} documentType - Document type identifier
     * @returns {Object} Document template configuration
     * @throws {Error} If document type not found
     */
    getTemplate(documentType) {
        const template = this._templates[documentType];
        if (!template) {
            throw new Error(`DOCUMENT_TEMPLATE_NOT_FOUND: ${documentType}`);
        }
        return { ...template };
    }

    /**
     * Check if document type exists
     * @param {string} documentType - Document type identifier
     * @returns {boolean} True if exists
     */
    exists(documentType) {
        return !!this._templates[documentType];
    }

    /**
     * Get validation rules for document type
     * @param {string} documentType - Document type identifier
     * @returns {Object} Validation rules object
     */
    getValidationRules(documentType) {
        const template = this.getTemplate(documentType);
        return { ...(template.validators || {}) };
    }

    /**
     * Get required fields for document type
     * @param {string} documentType - Document type identifier
     * @returns {string[]} Array of required field names
     */
    getRequiredFields(documentType) {
        const template = this.getTemplate(documentType);
        const validators = template.validators || {};
        
        return Object.entries(validators)
            .filter(([_, rules]) => rules.required === true)
            .map(([field]) => field);
    }

    /**
     * Get PII fields for document type
     * @param {string} documentType - Document type identifier
     * @returns {string[]} Array of PII field paths
     */
    getPIIFields(documentType) {
        const template = this.getTemplate(documentType);
        return template.piiFields ? [...template.piiFields] : [];
    }

    /**
     * Get retention period in years
     * @param {string} documentType - Document type identifier
     * @returns {number} Retention period in years
     */
    getRetentionYears(documentType) {
        const template = this.getTemplate(documentType);
        return template.retentionPeriod || 7;
    }

    /**
     * Get default confidentiality level
     * @param {string} documentType - Document type identifier
     * @returns {string} Confidentiality level
     */
    getDefaultConfidentiality(documentType) {
        const template = this.getTemplate(documentType);
        return template.confidentialityDefault || 'CONFIDENTIAL';
    }

    /**
     * Get compliance requirements
     * @param {string} documentType - Document type identifier
     * @returns {string[]} Array of compliance standards
     */
    getComplianceRequirements(documentType) {
        const template = this.getTemplate(documentType);
        return template.compliance ? [...template.compliance] : [];
    }

    /**
     * Get jurisdiction
     * @param {string} documentType - Document type identifier
     * @returns {string} Jurisdiction code
     */
    getJurisdiction(documentType) {
        const template = this.getTemplate(documentType);
        return template.jurisdiction || 'ZA';
    }

    /**
     * Get template version
     * @param {string} documentType - Document type identifier
     * @returns {string} Template version
     */
    getVersion(documentType) {
        const template = this.getTemplate(documentType);
        return template.version || '1.0.0';
    }

    /**
     * Get last reviewed date
     * @param {string} documentType - Document type identifier
     * @returns {string} ISO date string
     */
    getLastReviewed(documentType) {
        const template = this.getTemplate(documentType);
        return template.lastReviewed || new Date().toISOString().split('T')[0];
    }

    /**
     * Get template path
     * @param {string} documentType - Document type identifier
     * @returns {string} Template file path
     */
    getTemplatePath(documentType) {
        const template = this.getTemplate(documentType);
        return template.template || '';
    }

    /**
     * Get schema path
     * @param {string} documentType - Document type identifier
     * @returns {string} Schema file path
     */
    getSchemaPath(documentType) {
        const template = this.getTemplate(documentType);
        return template.schema || '';
    }

    /**
     * Validate document data against template rules
     * @param {string} documentType - Document type identifier
     * @param {Object} data - Document data to validate
     * @returns {Object} Validation result
     */
    validateDocument(documentType, data) {
        const errors = [];
        const warnings = [];

        try {
            const template = this.getTemplate(documentType);
            const validators = template.validators || {};

            // Check required fields
            const requiredFields = this.getRequiredFields(documentType);
            for (const field of requiredFields) {
                const value = this._getNestedValue(data, field);
                if (value === undefined || value === null || value === '') {
                    errors.push({
                        field,
                        error: 'REQUIRED_FIELD_MISSING',
                        message: `${field} is required`,
                        rule: validators[field]
                    });
                }
            }

            // Validate field constraints
            for (const [field, rules] of Object.entries(validators)) {
                const value = this._getNestedValue(data, field);
                
                if (value !== undefined && value !== null && value !== '') {
                    // Pattern validation
                    if (rules.pattern && !rules.pattern.test(String(value))) {
                        errors.push({
                            field,
                            error: 'INVALID_FORMAT',
                            message: rules.message || `${field} has invalid format`,
                            expected: rules.pattern.toString(),
                            rule: rules
                        });
                    }

                    // Min length validation
                    if (rules.minLength && String(value).length < rules.minLength) {
                        errors.push({
                            field,
                            error: 'MIN_LENGTH_VIOLATION',
                            message: rules.message || `${field} must be at least ${rules.minLength} characters`,
                            rule: rules
                        });
                    }

                    // Max length validation
                    if (rules.maxLength && String(value).length > rules.maxLength) {
                        errors.push({
                            field,
                            error: 'MAX_LENGTH_VIOLATION',
                            message: rules.message || `${field} must not exceed ${rules.maxLength} characters`,
                            rule: rules
                        });
                    }

                    // Min value validation (numbers)
                    if (rules.min !== undefined && Number(value) < rules.min) {
                        errors.push({
                            field,
                            error: 'MIN_VALUE_VIOLATION',
                            message: rules.message || `${field} must be at least ${rules.min}`,
                            rule: rules
                        });
                    }

                    // Max value validation (numbers)
                    if (rules.max !== undefined && Number(value) > rules.max) {
                        errors.push({
                            field,
                            error: 'MAX_VALUE_VIOLATION',
                            message: rules.message || `${field} must not exceed ${rules.max}`,
                            rule: rules
                        });
                    }

                    // Min items validation (arrays)
                    if (rules.minItems !== undefined && Array.isArray(value) && value.length < rules.minItems) {
                        errors.push({
                            field,
                            error: 'MIN_ITEMS_VIOLATION',
                            message: rules.message || `${field} must have at least ${rules.minItems} items`,
                            rule: rules
                        });
                    }

                    // Enum validation
                    if (rules.enum && !rules.enum.includes(value)) {
                        errors.push({
                            field,
                            error: 'INVALID_VALUE',
                            message: rules.message || `${field} must be one of: ${rules.enum.join(', ')}`,
                            rule: rules
                        });
                    }

                    // Date validation
                    if (rules.type === 'date') {
                        const date = new Date(value);
                        if (isNaN(date.getTime())) {
                            errors.push({
                                field,
                                error: 'INVALID_DATE',
                                message: rules.message || `${field} must be a valid date`,
                                rule: rules
                            });
                        }
                    }
                }
            }

            // Check for deprecated template
            if (template.deprecated) {
                warnings.push({
                    type: 'DEPRECATED_TEMPLATE',
                    message: `Template version ${template.version} is deprecated. Please migrate to ${template.supersededBy || 'latest version'}.`,
                    template: template.id,
                    version: template.version
                });
            }

        } catch (error) {
            errors.push({
                field: '_registry',
                error: 'REGISTRY_ERROR',
                message: error.message
            });
        }

        return {
            valid: errors.length === 0,
            errors,
            warnings,
            documentType,
            timestamp: new Date().toISOString()
        };
    }

    /**
     * Get all document categories
     * @returns {string[]} Array of category names
     */
    listCategories() {
        return Object.values(this._categories);
    }

    /**
     * Get document types by category
     * @param {string} category - Document category
     * @returns {string[]} Array of document type IDs
     */
    listTypesByCategory(category) {
        return Object.entries(this._templates)
            .filter(([_, template]) => template.category === category)
            .map(([id]) => id);
    }

    /**
     * Get all document types
     * @returns {Object} Map of all document types
     */
    getAllTypes() {
        return Object.keys(this._templates).map(id => ({
            id,
            category: this._templates[id].category,
            version: this._templates[id].version,
            retentionPeriod: this._templates[id].retentionPeriod,
            confidentialityDefault: this._templates[id].confidentialityDefault
        }));
    }

    /**
     * Search document types
     * @param {string} query - Search query
     * @returns {Array} Matching document types
     */
    search(query) {
        const lowercaseQuery = query.toLowerCase();
        return Object.entries(this._templates)
            .filter(([id, template]) => 
                id.toLowerCase().includes(lowercaseQuery) ||
                template.category.toLowerCase().includes(lowercaseQuery) ||
                (template.compliance && template.compliance.some(c => 
                    c.toLowerCase().includes(lowercaseQuery)
                ))
            )
            .map(([id]) => id);
    }

    /**
     * Get registry version
     * @returns {string} Registry version
     */

    /**
     * Get registry statistics
     * @returns {Object} Registry statistics
     */
    getStats() {
        const stats = {
            totalTypes: Object.keys(this._templates).length,
            categories: {},
            byRetentionPeriod: {},
            totalPIIFields: 0,
            totalCompliance: 0
        };

        // Count by category
        for (const [id, template] of Object.entries(this._templates)) {
            stats.categories[template.category] = (stats.categories[template.category] || 0) + 1;
            
            const period = template.retentionPeriod || 7;
            stats.byRetentionPeriod[period] = (stats.byRetentionPeriod[period] || 0) + 1;
            
            if (template.piiFields) {
                stats.totalPIIFields += template.piiFields.length;
            }
            
            if (template.compliance) {
                stats.totalCompliance += template.compliance.length;
            }
        }

        stats.version = this._version;
        stats.timestamp = new Date().toISOString();

        return stats;
    }

    // =============================================================================
    // PRIVATE HELPER METHODS
    // =============================================================================

    /**
     * Get nested value from object using dot notation
     * @private
     */
    _getNestedValue(obj, path) {
        if (!obj || !path) return undefined;
        
        return path.split('.').reduce((current, key) => {
            if (current === null || current === undefined) {
                return undefined;
            }

            // Handle array notation (e.g., "beneficiaries[0].idNumber")
            if (key.includes('[') && key.includes(']')) {
                const [arrayKey, indexStr] = key.split('[');
                const index = parseInt(indexStr.replace(']', ''), 10);
                
                if (Array.isArray(current[arrayKey]) && current[arrayKey][index]) {
                    return current[arrayKey][index];
                }
                return undefined;
            }

            return current[key];
        }, obj);
    }
}

// =============================================================================
// EXPORT SINGLETON INSTANCE - INVESTOR GRADE
// =============================================================================

/**
 * Singleton instance of DocumentTemplateRegistry
 * @type {DocumentTemplateRegistry}
 */
const templateRegistry = new DocumentTemplateRegistry();

module.exports = {
    templateRegistry,
    DOCUMENT_TYPES,
    DOCUMENT_CATEGORIES
};

// =============================================================================
// MERMAID INTEGRATION DIAGRAM
// =============================================================================

/**
 * @mermaid
 * graph TD
 *     Client[Client Application] --> Registry[DocumentTemplateRegistry]
 *     Registry --> Validation[Document Validation]
 *     Registry --> PII[PII Field Detection]
 *     Registry --> Retention[Retention Policy]
 *     Registry --> Compliance[Compliance Requirements]
 *     
 *     Validation --> Court[Court Documents]
 *     Validation --> Deeds[Conveyancing]
 *     Validation --> Corporate[Corporate Filings]
 *     Validation --> Estate[Estate Planning]
 *     Validation --> Contract[Commercial Contracts]
 *     Validation --> Regulatory[Regulatory Compliance]
 *     
 *     style Registry fill:#e1f5e1
 *     style Validation fill:#fff3cd
 *     style PII fill:#f8d7da
 *     style Compliance fill:#d4edda
 */
