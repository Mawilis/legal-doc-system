/**
 * Wilsy OS - Document Template Registry
 * Authoritative source for all legal document types and validation rules
 */


const DOCUMENT_TYPES = {
  // LITIGATION
  SUMMONS: {
    id: 'SUMMONS',
    category: 'LITIGATION',
    version: '2.1.0',
    template: 'templates/litigation/summons-v2.1.0.docx',
    validators: {
      court: { required: true, pattern: /^[A-Z]{2,3}-\d{4}-\d{6}$/ },
      plaintiff: { required: true, minLength: 2 },
      defendant: { required: true, minLength: 2 },
      caseNumber: { required: true, pattern: /^\d{4}\/\d{6}$/ }
    },
    retentionPeriod: 10,
    confidentialityDefault: 'CONFIDENTIAL',
    piiFields: ['plaintiff.idNumber', 'defendant.idNumber']
  },
  
  PLEADING: {
    id: 'PLEADING',
    category: 'LITIGATION',
    version: '2.0.0',
    template: 'templates/litigation/pleading-v2.0.0.docx',
    validators: {
      court: { required: true, pattern: /^[A-Z]{2,3}-\d{4}-\d{6}$/ },
      filingParty: { required: true },
      documentType: { required: true, enum: ['DECLARATION', 'ANSWER', 'REPLY', 'COUNTERCLAIM'] }
    },
    retentionPeriod: 10,
    confidentialityDefault: 'CONFIDENTIAL'
  },
  
  AFFIDAVIT: {
    id: 'AFFIDAVIT',
    category: 'LITIGATION',
    version: '1.5.0',
    template: 'templates/litigation/affidavit-v1.5.0.docx',
    validators: {
      deponent: { required: true },
      commissioner: { required: true },
      date: { required: true, type: 'date' },
      jurat: { required: true, pattern: /^Thus sworn and subscribed before me at .+ on this \d+ day of .+ 20\d{2}$/ }
    },
    retentionPeriod: 10,
    confidentialityDefault: 'CONFIDENTIAL'
  },
  
  NOTICE_OF_MOTION: {
    id: 'NOTICE_OF_MOTION',
    category: 'LITIGATION',
    version: '1.2.0',
    template: 'templates/litigation/notice-of-motion-v1.2.0.docx',
    validators: {
      court: { required: true },
      applicant: { required: true },
      respondent: { required: true },
      reliefSought: { required: true, minLength: 50 }
    },
    retentionPeriod: 10,
    confidentialityDefault: 'CONFIDENTIAL'
  },
  
  HEADS_OF_ARGUMENT: {
    id: 'HEADS_OF_ARGUMENT',
    category: 'LITIGATION',
    version: '3.0.0',
    template: 'templates/litigation/heads-of-argument-v3.0.0.docx',
    validators: {
      court: { required: true },
      counsel: { required: true },
      authorities: { required: false },
      hearingDate: { required: true, type: 'date' }
    },
    retentionPeriod: 5,
    confidentialityDefault: 'RESTRICTED'
  },
  
  // CONVEYANCING
  DEED_OF_SALE: {
    id: 'DEED_OF_SALE',
    category: 'CONVEYANCING',
    version: '4.2.0',
    template: 'templates/conveyancing/deed-of-sale-v4.2.0.docx',
    validators: {
      seller: { required: true },
      purchaser: { required: true },
      property: { required: true, pattern: /^[A-Z0-9]+\/[A-Z0-9]+\/[A-Z0-9]+$/ },
      purchasePrice: { required: true, min: 1 },
      transferDate: { required: true, type: 'date' }
    },
    retentionPeriod: 20,
    confidentialityDefault: 'HIGHLY_CONFIDENTIAL',
    piiFields: ['seller.idNumber', 'purchaser.idNumber']
  },
  
  TITLE_DEED: {
    id: 'TITLE_DEED',
    category: 'CONVEYANCING',
    version: '1.0.0',
    template: 'templates/conveyancing/title-deed-v1.0.0.pdf',
    validators: {
      deedNumber: { required: true, pattern: /^T\d{7}\/\d{4}$/ },
      owner: { required: true },
      propertyDescription: { required: true },
      extent: { required: true },
      registrationDate: { required: true, type: 'date' }
    },
    retentionPeriod: 100,
    confidentialityDefault: 'RESTRICTED'
  },
  
  MORTGAGE_BOND: {
    id: 'MORTGAGE_BOND',
    category: 'CONVEYANCING',
    version: '3.1.0',
    template: 'templates/conveyancing/mortgage-bond-v3.1.0.docx',
    validators: {
      mortgagor: { required: true },
      mortgagee: { required: true },
      bondAmount: { required: true, min: 1 },
      property: { required: true },
      interestRate: { required: true, min: 0, max: 100 }
    },
    retentionPeriod: 30,
    confidentialityDefault: 'HIGHLY_CONFIDENTIAL'
  },
  
  // CORPORATE
  MEMORANDUM_OF_INCORPORATION: {
    id: 'MEMORANDUM_OF_INCORPORATION',
    category: 'CORPORATE',
    version: '5.0.0',
    template: 'templates/corporate/moi-v5.0.0.docx',
    validators: {
      companyName: { required: true },
      registrationNumber: { required: true, pattern: /^\d{4}\/\d{6}\/07$/ },
      incorporators: { required: true, minItems: 1 },
      shareCapital: { required: true, min: 1 }
    },
    retentionPeriod: 20,
    confidentialityDefault: 'INTERNAL'
  },
  
  SHAREHOLDERS_AGREEMENT: {
    id: 'SHAREHOLDERS_AGREEMENT',
    category: 'CORPORATE',
    version: '2.3.0',
    template: 'templates/corporate/shareholders-agreement-v2.3.0.docx',
    validators: {
      company: { required: true },
      shareholders: { required: true, minItems: 2 },
      shareholding: { required: true },
      directors: { required: true }
    },
    retentionPeriod: 20,
    confidentialityDefault: 'HIGHLY_CONFIDENTIAL'
  },
  
  DIRECTORS_RESOLUTION: {
    id: 'DIRECTORS_RESOLUTION',
    category: 'CORPORATE',
    version: '1.8.0',
    template: 'templates/corporate/directors-resolution-v1.8.0.docx',
    validators: {
      company: { required: true },
      date: { required: true, type: 'date' },
      resolution: { required: true, minLength: 100 },
      directorsPresent: { required: true, minItems: 1 }
    },
    retentionPeriod: 10,
    confidentialityDefault: 'CONFIDENTIAL'
  },
  
  // ESTATE
  LAST_WILL_AND_TESTAMENT: {
    id: 'LAST_WILL_AND_TESTAMENT',
    category: 'ESTATE',
    version: '3.4.0',
    template: 'templates/estate/last-will-v3.4.0.docx',
    validators: {
      testator: { required: true },
      date: { required: true, type: 'date' },
      executors: { required: true, minItems: 1 },
      beneficiaries: { required: true, minItems: 1 },
      witnesses: { required: true, minItems: 2 }
    },
    retentionPeriod: 50,
    confidentialityDefault: 'RESTRICTED',
    piiFields: ['testator.idNumber', 'beneficiaries[].idNumber']
  },
  
  CODICIL: {
    id: 'CODICIL',
    category: 'ESTATE',
    version: '1.2.0',
    template: 'templates/estate/codicil-v1.2.0.docx',
    validators: {
      willReference: { required: true },
      testator: { required: true },
      amendments: { required: true },
      date: { required: true, type: 'date' }
    },
    retentionPeriod: 50,
    confidentialityDefault: 'RESTRICTED'
  },
  
  LETTERS_OF_ADMINISTRATION: {
    id: 'LETTERS_OF_ADMINISTRATION',
    category: 'ESTATE',
    version: '2.0.0',
    template: 'templates/estate/letters-of-administration-v2.0.0.docx',
    validators: {
      deceased: { required: true },
      executor: { required: true },
      court: { required: true },
      grantDate: { required: true, type: 'date' }
    },
    retentionPeriod: 30,
    confidentialityDefault: 'CONFIDENTIAL'
  },
  
  // CONTRACT
  SERVICE_AGREEMENT: {
    id: 'SERVICE_AGREEMENT',
    category: 'CONTRACT',
    version: '4.1.0',
    template: 'templates/contract/service-agreement-v4.1.0.docx',
    validators: {
      serviceProvider: { required: true },
      client: { required: true },
      services: { required: true },
      term: { required: true },
      fees: { required: true, min: 0 }
    },
    retentionPeriod: 7,
    confidentialityDefault: 'CONFIDENTIAL'
  },
  
  NON_DISCLOSURE_AGREEMENT: {
    id: 'NON_DISCLOSURE_AGREEMENT',
    category: 'CONTRACT',
    version: '2.2.0',
    template: 'templates/contract/nda-v2.2.0.docx',
    validators: {
      disclosingParty: { required: true },
      receivingParty: { required: true },
      effectiveDate: { required: true, type: 'date' },
      term: { required: true, min: 1 }
    },
    retentionPeriod: 7,
    confidentialityDefault: 'HIGHLY_CONFIDENTIAL'
  },
  
  EMPLOYMENT_CONTRACT: {
    id: 'EMPLOYMENT_CONTRACT',
    category: 'CONTRACT',
    version: '3.0.0',
    template: 'templates/contract/employment-contract-v3.0.0.docx',
    validators: {
      employer: { required: true },
      employee: { required: true },
      position: { required: true },
      startDate: { required: true, type: 'date' },
      remuneration: { required: true, min: 1 }
    },
    retentionPeriod: 10,
    confidentialityDefault: 'CONFIDENTIAL',
    piiFields: ['employee.idNumber', 'employee.bankAccount']
  },
  
  // COMPLIANCE
  POPIA_REGISTER: {
    id: 'POPIA_REGISTER',
    category: 'COMPLIANCE',
    version: '1.0.0',
    template: 'templates/compliance/popia-register-v1.0.0.xlsx',
    validators: {
      responsibleParty: { required: true },
      informationOfficer: { required: true },
      processingActivities: { required: true, minItems: 1 }
    },
    retentionPeriod: 7,
    confidentialityDefault: 'INTERNAL'
  },
  
  PAIA_MANUAL: {
    id: 'PAIA_MANUAL',
    category: 'COMPLIANCE',
    version: '2.0.0',
    template: 'templates/compliance/paia-manual-v2.0.0.docx',
    validators: {
      company: { required: true },
      section51Officer: { required: true },
      categories: { required: true }
    },
    retentionPeriod: 5,
    confidentialityDefault: 'PUBLIC'
  },
  
  FICA_RECORD: {
    id: 'FICA_RECORD',
    category: 'COMPLIANCE',
    version: '1.3.0',
    template: 'templates/compliance/fica-record-v1.3.0.docx',
    validators: {
      client: { required: true },
      verificationDate: { required: true, type: 'date' },
      verificationMethod: { required: true },
      documents: { required: true, minItems: 1 }
    },
    retentionPeriod: 5,
    confidentialityDefault: 'HIGHLY_CONFIDENTIAL',
    piiFields: ['client.idNumber', 'client.passportNumber']
  },
  
  SARS_RETURN: {
    id: 'SARS_RETURN',
    category: 'COMPLIANCE',
    version: '2026.1',
    template: 'templates/compliance/sars-return-2026.1.pdf',
    validators: {
      taxReference: { required: true, pattern: /^\d{10}$/ },
      taxYear: { required: true, pattern: /^20\d{2}$/ },
      submissionDate: { required: true, type: 'date' }
    },
    retentionPeriod: 5,
    confidentialityDefault: 'RESTRICTED'
  }
};

class DocumentTemplateRegistry {
  constructor() {
    this.templates = DOCUMENT_TYPES;
  }

  getTemplate(documentType) {
    const template = this.templates[documentType];
    if (!template) {
      throw new Error(`DOCUMENT_TEMPLATE_NOT_FOUND: ${documentType}`);
    }
    return { ...template };
  }

  getValidationRules(documentType) {
    const template = this.getTemplate(documentType);
    return template.validators || {};
  }

  getRequiredFields(documentType) {
    const template = this.getTemplate(documentType);
    const validators = template.validators || {};
    return Object.entries(validators)

  validateDocument(documentType, data) {
    const template = this.getTemplate(documentType);
    const errors = [];
    const warnings = [];

    const requiredFields = this.getRequiredFields(documentType);
    requiredFields.forEach(field => {
      const value = this._getNestedValue(data, field);
      if (value === undefined || value === null || value === '') {
        errors.push({
          field,
          error: 'REQUIRED_FIELD_MISSING',
          message: `${field} is required`
        });
      }
    });

    return {
      valid: errors.length === 0,
      errors,
      warnings,
      templateVersion: template.version,
      documentType: template.id,
      category: template.category
    };
  }

  listCategories() {
    const categories = new Set();
    Object.values(this.templates).forEach(t => categories.add(t.category));
    return Array.from(categories);
  }

  listTypesByCategory(category) {
    return Object.values(this.templates)
      .filter(t => t.category === category)
      .map(t => t.id);
  }

  exists(documentType) {
    return !!this.templates[documentType];
  }

  getPIIFields(documentType) {
    const template = this.getTemplate(documentType);
    return template.piiFields || [];
  }

  getRetentionYears(documentType) {
    const template = this.getTemplate(documentType);
    return template.retentionPeriod || 7;
  }

  getDefaultConfidentiality(documentType) {
    const template = this.getTemplate(documentType);
    return template.confidentialityDefault || 'CONFIDENTIAL';
  }

  _getNestedValue(obj, path) {
    return path.split('.').reduce((current, key) => {
      if (key.includes('[') && key.includes(']')) {
        const [arrayKey, indexStr] = key.split('[');
        const index = parseInt(indexStr.replace(']', ''));
        return current && current[arrayKey] ? current[arrayKey][index] : undefined;
      }
      return current && current[key] !== undefined ? current[key] : undefined;
    }, obj);
  }
}

const templateRegistry = new DocumentTemplateRegistry();

module.exports = {
  templateRegistry,
  DOCUMENT_TYPES
};
