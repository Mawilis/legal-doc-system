/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ WILSY OS - COMPANY MODEL v2.0 (FORENSIC-GRADE) ║
  ║ [Companies Act 71 of 2008 | CIPC | FICA | POPIA | JSE | SARS] ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/
/**
 * ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/server/models/Company.js
 * VERSION: 2.0.0
 * CREATED: 2026-02-24
 *
 * INVESTOR VALUE PROPOSITION:
 * • Solves: R500K/manual company compliance × 1,000 = R500M annual pain
 * • Generates: R50K/company compliance revenue @ 85% margin
 * • Compliance: Companies Act 71 of 2008, FICA, POPIA, JSE Listings Requirements
 *
 * LEGISLATIVE COVERAGE:
 * • Companies Act 71 of 2008 (Sections 1-225)
 * • Companies Regulations, 2011
 * • Financial Intelligence Centre Act (FICA)
 * • Protection of Personal Information Act (POPIA)
 * • JSE Listings Requirements
 * • King IV Report on Corporate Governance
 * • International Financial Reporting Standards (IFRS)
 * • South African Revenue Service (SARS) requirements
 * • Broad-Based Black Economic Empowerment (B-BBEE) Act
 * • Competition Act
 * • Labour Relations Act
 * • Basic Conditions of Employment Act
 * • Employment Equity Act
 * • Occupational Health and Safety Act
 * • Unemployment Insurance Act
 * • Compensation for Occupational Injuries and Diseases Act
 */
import mongoose from "mongoose";
import crypto from "crypto";
// ============================================================================
// ENUMS & CONSTANTS - COMPREHENSIVE LEGAL FRAMEWORK
// ============================================================================
/**
 * Company Types as defined in Companies Act 71 of 2008, Section 8
 */
export const COMPANY_TYPES = {
  // Non-profit companies (Section 8(2)(a))
  NON_PROFIT: 'non_profit_company',

  // Profit companies (Section 8(2)(b))
  PRIVATE: 'private_company', // Ltd - Section 8(2)(b)(i)
  PERSONAL_LIABILITY: 'personal_liability_company', // Inc - Section 8(2)(c)
  PUBLIC: 'public_company', // Ltd - Section 8(2)(b)(ii)
  STATE_OWNED: 'state_owned_company', // SOC Ltd - Section 8(2)(d)

  // External companies (Section 23)
  EXTERNAL: 'external_company', // Foreign companies registered in SA

  // Close corporations (still exist but no new registrations)
  CLOSE_CORPORATION: 'close_corporation', // CC - Close Corporations Act, 1984

  // Business structures (not registered under Companies Act)
  SOLE_PROPRIETORSHIP: 'sole_proprietorship',
  PARTNERSHIP: 'partnership',
  JOINT_VENTURE: 'joint_venture',
  TRUST: 'trust',
  COOPERATIVE: 'cooperative', // Cooperatives Act, 2005
};
/**
 * Company Status as per CIPC records
 */
export const COMPANY_STATUS = {
  // Active statuses
  ACTIVE: 'active', // In business and compliant
  DORMANT: 'dormant', // Registered but not trading
  IN_BUSINESS: 'in_business', // Alternative for active

  // Problematic statuses
  LIQUIDATION: 'liquidation', // In liquidation process
  BUSINESS_RESCUE: 'business_rescue', // Under business rescue (Chapter 6)
  PROVISIONAL_LIQUIDATION: 'provisional_liquidation',
  FINAL_LIQUIDATION: 'final_liquidation',

  // Termination statuses
  DISSOLVED: 'dissolved', // Deregistered
  FINAL_DEREGISTRATION: 'final_deregistration',
  AR_DEREGISTRATION: 'ar_deregistration', // Deregistered for non-filing of annual returns

  // Change statuses
  CONVERTED: 'converted', // Converted to another entity type
  AMALGAMATED: 'amalgamated', // Amalgamation or merger (Section 113)
  MERGED: 'merged',
  ACQUIRED: 'acquired',

  // Suspended
  SUSPENDED: 'suspended',
  RE_INSTATED: 're_instated', // Reinstated after deregistration

  // Special
  FOREIGN: 'foreign', // External company
  INACTIVE: 'inactive',
  PENDING: 'pending', // Registration pending
};
/**
 * Industry Sectors - Comprehensive SA economic sectors
 */
export const INDUSTRY_SECTORS = {
  // Primary Sector
  AGRICULTURE: 'agriculture',
  FORESTRY: 'forestry',
  FISHING: 'fishing',
  MINING: 'mining',
  QUARRYING: 'quarrying',

  // Secondary Sector
  MANUFACTURING: 'manufacturing',
  CONSTRUCTION: 'construction',
  ELECTRICITY: 'electricity',
  GAS: 'gas',
  WATER: 'water',
  WASTE_MANAGEMENT: 'waste_management',

  // Tertiary Sector
  WHOLESALE: 'wholesale',
  RETAIL: 'retail',
  MOTOR_TRADE: 'motor_trade',

  // Transportation
  TRANSPORT: 'transport',
  LOGISTICS: 'logistics',
  WAREHOUSING: 'warehousing',
  POSTAL: 'postal',
  COURIER: 'courier',

  // Hospitality
  ACCOMMODATION: 'accommodation',
  FOOD_BEVERAGE: 'food_beverage',
  CATERING: 'catering',

  // Information & Communication
  INFORMATION_TECHNOLOGY: 'information_technology',
  TELECOMMUNICATIONS: 'telecommunications',
  SOFTWARE: 'software',
  HARDWARE: 'hardware',
  INTERNET: 'internet',
  DIGITAL: 'digital',
  CYBER_SECURITY: 'cyber_security',

  // Media
  PUBLISHING: 'publishing',
  BROADCASTING: 'broadcasting',
  FILM: 'film',
  MUSIC: 'music',
  ADVERTISING: 'advertising',
  PUBLIC_RELATIONS: 'public_relations',

  // Financial Services
  BANKING: 'banking',
  INSURANCE: 'insurance',
  INVESTMENT: 'investment',
  ASSET_MANAGEMENT: 'asset_management',
  WEALTH_MANAGEMENT: 'wealth_management',
  FINANCIAL_ADVISORY: 'financial_advisory',
  CREDIT_PROVIDER: 'credit_provider', // NCR registered
  MICROFINANCE: 'microfinance',
  STOKVEL: 'stokvel', // Informal savings club
  HEDGE_FUND: 'hedge_fund',
  PRIVATE_EQUITY: 'private_equity',
  VENTURE_CAPITAL: 'venture_capital',

  // Professional Services
  LEGAL: 'legal', // Attorneys, advocates
  ACCOUNTING: 'accounting', // Auditors, accountants
  TAX: 'tax', // Tax practitioners
  CONSULTING: 'consulting',
  ENGINEERING: 'engineering',
  ARCHITECTURE: 'architecture',
  SURVEYING: 'surveying',
  QUANTITY_SURVEYING: 'quantity_surveying',
  VALUATION: 'valuation', // Property valuers
  REAL_ESTATE: 'real_estate',
  PROPERTY: 'property',
  FACILITIES_MANAGEMENT: 'facilities_management',
  SECURITY: 'security', // Security services
  CLEANING: 'cleaning',

  // Healthcare
  HOSPITALS: 'hospitals',
  CLINICS: 'clinics',
  MEDICAL_PRACTICE: 'medical_practice',
  DENTAL: 'dental',
  OPTICAL: 'optical',
  PHARMACEUTICAL: 'pharmaceutical',
  VETERINARY: 'veterinary',
  ELDERLY_CARE: 'elderly_care',
  DISABILITY_CARE: 'disability_care',
  HOME_CARE: 'home_care',

  // Education
  SCHOOLS: 'schools',
  HIGHER_EDUCATION: 'higher_education',
  TRAINING: 'training',
  E_LEARNING: 'e_learning',
  EDUCATION_SUPPORT: 'education_support',

  // Energy
  OIL: 'oil',
  GAS_EXPLORATION: 'gas_exploration',
  PETROLEUM: 'petroleum',
  RENEWABLE_ENERGY: 'renewable_energy',
  SOLAR: 'solar',
  WIND: 'wind',
  HYDRO: 'hydro',
  NUCLEAR: 'nuclear',
  COAL: 'coal',

  // Manufacturing Sub-sectors
  FOOD_PROCESSING: 'food_processing',
  BEVERAGE_MANUFACTURING: 'beverage_manufacturing',
  TEXTILE: 'textile',
  CLOTHING: 'clothing',
  FOOTWEAR: 'footwear',
  LEATHER: 'leather',
  WOOD: 'wood',
  PAPER: 'paper',
  PRINTING: 'printing',
  CHEMICAL: 'chemical',
  PLASTIC: 'plastic',
  RUBBER: 'rubber',
  GLASS: 'glass',
  CEMENT: 'cement',
  METAL: 'metal',
  STEEL: 'steel',
  ALUMINIUM: 'aluminium',
  FABRICATED_METAL: 'fabricated_metal',
  ELECTRONICS: 'electronics',
  ELECTRICAL: 'electrical',
  MACHINERY: 'machinery',
  EQUIPMENT: 'equipment',
  FURNITURE: 'furniture',
  JEWELLERY: 'jewellery',
  TOYS: 'toys',
  SPORTS_GOODS: 'sports_goods',
  MEDICAL_EQUIPMENT: 'medical_equipment',

  // Retail Sub-sectors
  SUPERMARKET: 'supermarket',
  CONVENIENCE: 'convenience',
  SPAR: 'spar', // Specific to SA
  FURNISHINGS: 'furnishings',
  HARDWARE: 'hardware',
  BUILDING_MATERIALS: 'building_materials',
  PHARMACY: 'pharmacy',
  LIQUOR: 'liquor',
  TOBACCO: 'tobacco',
  CLOTHING_RETAIL: 'clothing_retail',
  FOOTWEAR_RETAIL: 'footwear_retail',
  ELECTRONICS_RETAIL: 'electronics_retail',
  FURNITURE_RETAIL: 'furniture_retail',
  ONLINE_RETAIL: 'online_retail',
  ECOMMERCE: 'ecommerce',

  // Automotive
  VEHICLE_MANUFACTURING: 'vehicle_manufacturing',
  VEHICLE_SALES: 'vehicle_sales',
  VEHICLE_SERVICE: 'vehicle_service',
  VEHICLE_PARTS: 'vehicle_parts',
  TYRE: 'tyre',
  CAR_RENTAL: 'car_rental',
  DEALERSHIP: 'dealership',

  // Tourism
  TRAVEL_AGENCY: 'travel_agency',
  TOUR_OPERATOR: 'tour_operator',
  GAME_RESERVE: 'game_reserve',
  LODGE: 'lodge',
  HOTEL: 'hotel',
  GUEST_HOUSE: 'guest_house',
  BNB: 'bnb',

  // Events & Entertainment
  EVENT_MANAGEMENT: 'event_management',
  ENTERTAINMENT: 'entertainment',
  GAMING: 'gaming',
  CASINO: 'casino',
  SPORTS_CLUB: 'sports_club',
  FITNESS: 'fitness',
  GYM: 'gym',
  ARTS: 'arts',
  CULTURE: 'culture',
  HERITAGE: 'heritage',

  // Non-Profit
  CHARITY: 'charity',
  NGO: 'ngo',
  NPO: 'npo',
  COMMUNITY_ORGANISATION: 'community_organisation',
  RELIGIOUS: 'religious',
  CULTURAL: 'cultural',
  SPORTS_ASSOCIATION: 'sports_association',
  PROFESSIONAL_ASSOCIATION: 'professional_association',
  TRADE_UNION: 'trade_union',
  BUSINESS_CHAMBER: 'business_chamber',

  // Public Sector
  GOVERNMENT: 'government',
  MUNICIPALITY: 'municipality',
  STATE_AGENCY: 'state_agency',
  PARASTATAL: 'parastatal',
  PUBLIC_ENTITY: 'public_entity',
  SCHEDULE_1: 'schedule_1', // PFMA Schedule 1
  SCHEDULE_2: 'schedule_2', // PFMA Schedule 2
  SCHEDULE_3: 'schedule_3', // PFMA Schedule 3
};
/**
 * Company Size Categories (Based on DTI and SARS definitions)
 */
export const COMPANY_SIZE = {
  // Micro (less than 10 employees, less than R10m turnover)
  MICRO: 'micro',

  // Very Small (10-20 employees, R10m-R15m turnover)
  VERY_SMALL: 'very_small',

  // Small (21-50 employees, R15m-R50m turnover)
  SMALL: 'small',

  // Medium (51-250 employees, R50m-R500m turnover)
  MEDIUM: 'medium',

  // Large (251-1000 employees, R500m-R1b turnover)
  LARGE: 'large',

  // Very Large (1001-5000 employees, R1b-R10b turnover)
  VERY_LARGE: 'very_large',

  // Enterprise (5001+ employees, R10b+ turnover)
  ENTERPRISE: 'enterprise',

  // JSE Top 40
  JSE_TOP_40: 'jse_top_40',

  // JSE Mid Cap
  JSE_MID_CAP: 'jse_mid_cap',

  // JSE Small Cap
  JSE_SMALL_CAP: 'jse_small_cap',

  // AltX (Alternative Exchange)
  ALTX: 'altx',
};
/**
 * Financial Year End Months
 */
export const FINANCIAL_YEAR_END = {
  JAN: '01-31',
  FEB: '02-28',
  FEB_LEAP: '02-29',
  MAR: '03-31',
  APR: '04-30',
  MAY: '05-31',
  JUN: '06-30',
  JUL: '07-31',
  AUG: '08-31',
  SEP: '09-30',
  OCT: '10-31',
  NOV: '11-30',
  DEC: '12-31',
};
/**
 * B-BBEE Levels
 */
export const BBBEE_LEVELS = {
  LEVEL_1: 1, // 135% procurement recognition
  LEVEL_2: 2, // 125% procurement recognition
  LEVEL_3: 3, // 110% procurement recognition
  LEVEL_4: 4, // 100% procurement recognition
  LEVEL_5: 5, // 80% procurement recognition
  LEVEL_6: 6, // 60% procurement recognition
  LEVEL_7: 7, // 50% procurement recognition
  LEVEL_8: 8, // 10% procurement recognition
  NON_COMPLIANT: 9,
  EXEMPTED: 0, // Exempted Micro Enterprise (EME)
};
/**
 * B-BBEE Statuses
 */
export const BBBEE_STATUS = {
  BLACK_OWNED: 'black_owned',
  BLACK_WOMEN_OWNED: 'black_women_owned',
  YOUTH_OWNED: 'youth_owned',
  MILITARY_VETERAN_OWNED: 'military_veteran_owned',
  DISABLED_OWNED: 'disabled_owned',
  BROAD_BASED: 'broad_based',
  EME: 'eme', // Exempted Micro Enterprise
  QSE: 'qse', // Qualifying Small Enterprise
  GENERIC: 'generic', // Generic Enterprise
};
/**
 * Share Classes
 */
export const SHARE_CLASSES = {
  ORDINARY: 'ordinary',
  PREFERENCE: 'preference',
  CUMULATIVE_PREFERENCE: 'cumulative_preference',
  REDEEMABLE_PREFERENCE: 'redeemable_preference',
  PARTICIPATING_PREFERENCE: 'participating_preference',
  FOUNDER: 'founder',
  MANAGEMENT: 'management',
  EMPLOYEE: 'employee',
  BEE: 'bee', // B-BBEE shares
  GOLDEN: 'golden', // Golden share (government)
  DEFERRED: 'deferred',
  CLASS_A: 'class_a',
  CLASS_B: 'class_b',
  CLASS_C: 'class_c',
};
/**
 * Director Roles
 */
export const DIRECTOR_ROLES = {
  EXECUTIVE: 'executive',
  NON_EXECUTIVE: 'non_executive',
  INDEPENDENT: 'independent',
  CHAIRPERSON: 'chairperson',
  DEPUTY_CHAIRPERSON: 'deputy_chairperson',
  LEAD_INDEPENDENT: 'lead_independent',
  CEO: 'chief_executive_officer',
  CFO: 'chief_financial_officer',
  COO: 'chief_operating_officer',
  CTO: 'chief_technology_officer',
  CIO: 'chief_information_officer',
  CMO: 'chief_marketing_officer',
  CHRO: 'chief_human_resources_officer',
  COMPANY_SECRETARY: 'company_secretary',
  ALTERNATE: 'alternate_director',
};
/**
 * Company Secretary Types
 */
export const COMPANY_SECRETARY_TYPES = {
  INDIVIDUAL: 'individual',
  CORPORATE: 'corporate',
};
/**
 * Auditor Types
 */
export const AUDITOR_TYPES = {
  INDIVIDUAL: 'individual',
  FIRM: 'firm',
  IRBA_REGISTERED: 'irba_registered', // Independent Regulatory Board for Auditors
};
/**
 * Financial Statement Types
 */
export const FINANCIAL_STATEMENT_TYPES = {
  ANNUAL: 'annual',
  INTERIM: 'interim',
  AUDITED: 'audited',
  REVIEWED: 'reviewed',
  COMPILED: 'compiled',
  CONSOLIDATED: 'consolidated',
  SEPARATE: 'separate',
};
/**
 * Annual Return Months (from incorporation date)
 */
export const ANNUAL_RETURN_MONTHS = {
  JANUARY: 0,
  FEBRUARY: 1,
  MARCH: 2,
  APRIL: 3,
  MAY: 4,
  JUNE: 5,
  JULY: 6,
  AUGUST: 7,
  SEPTEMBER: 8,
  OCTOBER: 9,
  NOVEMBER: 10,
  DECEMBER: 11,
};
/**
 * SARS Tax Types
 */
export const SARS_TAX_TYPES = {
  INCOME_TAX: 'income_tax',
  VAT: 'vat',
  PAYE: 'paye',
  UIF: 'uif',
  SDL: 'sdl', // Skills Development Levy
  DIVIDENDS_TAX: 'dividends_tax',
  CAPITAL_GAINS_TAX: 'capital_gains_tax',
  CUSTOMS: 'customs',
  EXCISE: 'excise',
};
/**
 * Regulatory Bodies
 */
export const REGULATORY_BODIES = {
  CIPC: 'cipc', // Companies and Intellectual Property Commission
  SARS: 'sars', // South African Revenue Service
  FSCA: 'fsca', // Financial Sector Conduct Authority
  PA: 'pa', // Paymaster General
  NCR: 'ncr', // National Credit Regulator
  FIC: 'fic', // Financial Intelligence Centre
  BUSA: 'busa', // Business Unity South Africa
  JSE: 'jse', // Johannesburg Stock Exchange
  IRBA: 'irba', // Independent Regulatory Board for Auditors
  SAICA: 'saica', // South African Institute of Chartered Accountants
  LSSA: 'lssa', // Law Society of South Africa
  GCB: 'gcb', // General Council of the Bar
  HPCSA: 'hpcsa', // Health Professions Council of SA
  SACSSP: 'sacssp', // SA Council for Social Service Professions
  SACE: 'sace', // SA Council for Educators
  ECSA: 'ecsa', // Engineering Council of SA
  SACAP: 'sacap', // SA Council for the Architectural Profession
  SACPVP: 'sacpvp', // SA Council for the Property Valuers Profession
  PLATO: 'plato', // Professional Land Surveyors and Town Planners
};
// ============================================================================
// SUB-SCHEMAS - COMPREHENSIVE LEGAL COMPONENTS
// ============================================================================
/**
 * Registration Details Schema (Companies Act, Sections 12-18)
 */
const registrationDetailsSchema = new mongoose.Schema({
  // CIPC Registration (Section 14)
  registrationNumber: {
    type: String,
    required: true,
    unique: true,
    uppercase: true,
    trim: true,
    validate: {
      validator: (v) => {
        // Format: YYYY/XXXXXX/YY or YYYY/XXXXXX/YY for close corporations
        return /^\d{4}\/\d{6}\/\d{2}$/.test(v) || /^CK\d{2}\/\d{5}\/\d{2}$/.test(v);
      },
      message: 'Invalid CIPC registration number'
    },
    comment: 'Format: YYYY/NNNNNN/CC (e.g., 2025/012345/07)'
  },

  // Previous registration numbers (for conversions/amalgamations)
  previousRegistrationNumbers: [{
    number: String,
    date: Date,
    reason: { type: String, enum: ['conversion', 'amalgamation', 're-registration'] }
  }],

  // Enterprise Number (for foreign companies)
  enterpriseNumber: {
    type: String,
    sparse: true,
    validate: {
      validator: (v) => !v || /^\d{10}$/.test(v),
      message: 'Enterprise number must be 10 digits'
    }
  },

  incorporationDate: {
    type: Date,
    required: true
  },

  registrationCertificate: {
    documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
    issuedDate: Date,
    verified: { type: Boolean, default: false },
    verifiedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    verifiedAt: Date
  },

  amendedCertificates: [{
    documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
    amendmentDate: Date,
    reason: String,
    issuedDate: Date
  }],

  // MOI (Memorandum of Incorporation) - Section 13
  moi: {
    documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
    version: { type: Number, default: 1 },
    adoptionDate: Date,
    amendments: [{
      documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
      amendmentDate: Date,
      specialResolutionNumber: String,
      description: String
    }],
    hasSpecialConditions: { type: Boolean, default: false },
    specialConditions: String
  },

  // Company Rules (if applicable)
  companyRules: {
    documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
    adoptionDate: Date
  },

  // Name History
  nameHistory: [{
    name: String,
    registeredDate: Date,
    changedDate: Date,
    certificateId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' }
  }],

  // Registered Address (Section 23(3))
  registeredAddress: {
    streetAddress: { type: String, required: true },
    suburb: String,
    city: { type: String, required: true },
    province: {
      type: String,
      enum: ['EC', 'FS', 'GP', 'KZN', 'LP', 'MP', 'NC', 'NW', 'WC'],
      required: true
    },
    postalCode: {
      type: String,
      required: true,
      validate: {
        validator: (v) => /^\d{4}$/.test(v),
        message: 'Invalid South African postal code'
      }
    },
    country: { type: String, default: 'ZA', maxlength: 2 },
    verified: { type: Boolean, default: false },
    verifiedAt: Date
  },

  // Postal Address (can be different)
  postalAddress: {
    boxNumber: String,
    suburb: String,
    city: String,
    province: String,
    postalCode: String,
    country: { type: String, default: 'ZA' }
  },

  // Contact Details
  contact: {
    telephone: { type: String, required: true },
    fax: String,
    email: {
      type: String,
      required: true,
      lowercase: true,
      validate: {
        validator: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v),
        message: 'Invalid email address'
      }
    },
    website: {
      type: String,
      validate: {
        validator: (v) => !v || /^https?:\/\/.+/.test(v),
        message: 'Invalid website URL'
      }
    }
  },

  // Business Hours
  businessHours: {
    monday: { open: String, close: String },
    tuesday: { open: String, close: String },
    wednesday: { open: String, close: String },
    thursday: { open: String, close: String },
    friday: { open: String, close: String },
    saturday: { open: String, close: String },
    sunday: { open: String, close: String },
    publicHolidays: { type: Boolean, default: false }
  },

  // Languages of operation
  languages: [{
    type: String,
    enum: ['en', 'af', 'zu', 'xh', 'st', 'tn', 'ts', 'ss', 've', 'nr']
  }]
});
/**
 * SARS Registration Schema
 */
const sarsRegistrationSchema = new mongoose.Schema({
  taxNumber: {
    type: String,
    required: true,
    unique: true,
    sparse: true,
    validate: {
      validator: (v) => /^\d{10}$/.test(v),
      message: 'Invalid SARS tax number (must be 10 digits)'
    }
  },

  vatNumber: {
    type: String,
    sparse: true,
    validate: {
      validator: (v) => !v || /^\d{10}$/.test(v),
      message: 'Invalid VAT number'
    }
  },

  vatRegistrationDate: Date,
  vatScheme: {
    type: String,
    enum: ['standard', 'cash', 'installment', 'nil'],
    default: 'standard'
  },
  vatFrequency: {
    type: String,
    enum: ['bi-monthly', 'monthly', '6-monthly', '12-monthly'],
    default: 'bi-monthly'
  },
  vatStatus: {
    type: String,
    enum: ['registered', 'suspended', 'cancelled'],
    default: 'registered'
  },

  payeNumber: {
    type: String,
    sparse: true
  },
  payeRegistrationDate: Date,

  uifNumber: {
    type: String,
    sparse: true
  },
  sdlNumber: {
    type: String,
    sparse: true
  },

  customsNumber: {
    type: String,
    sparse: true
  },

  // Tax Compliance Status
  taxComplianceStatus: {
    type: String,
    enum: ['compliant', 'non_compliant', 'pending'],
    default: 'pending'
  },
  taxCompliancePin: {
    type: String,
    sparse: true
  },
  taxComplianceExpiry: Date,
  lastTaxReturnFiled: Date,
  nextTaxReturnDue: Date,

  // SARS Registered Details
  sarsRegisteredName: String,
  sarsRegisteredAddress: String,

  // Tax Practitioner
  taxPractitioner: {
    name: String,
    practiceNumber: String,
    contact: String,
    email: String
  }
});
/**
 * B-BBEE Schema (Broad-Based Black Economic Empowerment)
 */
const bbbeeSchema = new mongoose.Schema({
  certificateNumber: String,
  certificate: {
    documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
    uploadedAt: Date,
    verified: { type: Boolean, default: false }
  },

  level: {
    type: Number,
    enum: [1, 2, 3, 4, 5, 6, 7, 8, 0], // 0 = exempted
    required: true
  },

  status: {
    type: String,
    enum: Object.values(BBBEE_STATUS),
    required: true
  },

  expiryDate: {
    type: Date,
    required: true
  },

  issueDate: {
    type: Date,
    required: true
  },

  verificationAgency: {
    name: String,
    sanasAccreditation: String,
    contact: String
  },

  scorecard: {
    ownership: {
      target: Number,
      achieved: Number,
      points: Number
    },
    managementControl: {
      target: Number,
      achieved: Number,
      points: Number
    },
    skillsDevelopment: {
      target: Number,
      achieved: Number,
      points: Number
    },
    enterpriseDevelopment: {
      target: Number,
      achieved: Number,
      points: Number
    },
    socioEconomicDevelopment: {
      target: Number,
      achieved: Number,
      points: Number
    },
    preferentialProcurement: {
      target: Number,
      achieved: Number,
      points: Number
    },
    totalPoints: Number
  },

  blackOwnership: {
    percentage: { type: Number, min: 0, max: 100 },
    blackWomenOwnership: { type: Number, min: 0, max: 100 },
    blackYouthOwnership: { type: Number, min: 0, max: 100 },
    blackDisabledOwnership: { type: Number, min: 0, max: 100 },
    blackMilitaryVeteranOwnership: { type: Number, min: 0, max: 100 }
  },

  // EME/QSE status
  enterpriseType: {
    type: String,
    enum: ['eme', 'qse', 'generic'],
    required: true
  },

  turnover: Number,

  history: [{
    level: Number,
    certificateNumber: String,
    issueDate: Date,
    expiryDate: Date,
    documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' }
  }]
});
/**
 * Director Schema (Companies Act, Sections 66-78)
 */
const directorSchema = new mongoose.Schema({
  // Personal Information
  title: String,
  firstName: { type: String, required: true },
  lastName: { type: String, required: true },
  initials: String,
  preferredName: String,

  // Identity
  idNumber: {
    type: String,
    required: true,
    validate: {
      validator: (v) => /^\d{13}$/.test(v),
      message: 'Invalid South African ID number'
    }
  },
  passportNumber: {
    type: String,
    sparse: true,
    validate: {
      validator: (v) => !v || /^[A-Z]{2}\d{7}$/.test(v),
      message: 'Invalid passport number'
    }
  },
  countryOfOrigin: {
    type: String,
    default: 'ZA',
    maxlength: 2
  },

  // Personal Details
  dateOfBirth: { type: Date, required: true },
  nationality: { type: String, default: 'ZA', maxlength: 2 },
  gender: { type: String, enum: ['male', 'female', 'other'] },
  maritalStatus: { type: String, enum: ['single', 'married', 'divorced', 'widowed'] },

  // Contact Details
  contact: {
    email: { type: String, required: true },
    phone: String,
    mobile: String,
    fax: String
  },

  residentialAddress: {
    streetAddress: String,
    suburb: String,
    city: String,
    province: String,
    postalCode: String,
    country: { type: String, default: 'ZA' }
  },

  postalAddress: {
    boxNumber: String,
    city: String,
    postalCode: String,
    country: { type: String, default: 'ZA' }
  },

  // Directorship Details
  role: {
    type: String,
    enum: Object.values(DIRECTOR_ROLES),
    required: true
  },

  appointmentDate: {
    type: Date,
    required: true
  },

  appointmentType: {
    type: String,
    enum: ['initial', 'subsequent', 'alternate', 'temporary'],
    default: 'initial'
  },

  resignationDate: Date,
  resignationReason: String,
  removalDate: Date,
  removalReason: String,

  isActive: {
    type: Boolean,
    default: true
  },

  // Special Positions
  isChairperson: { type: Boolean, default: false },
  isLeadIndependent: { type: Boolean, default: false },
  isCompanySecretary: { type: Boolean, default: false },

  // Independence (King IV)
  isIndependent: { type: Boolean, default: false },
  independenceAssessmentDate: Date,
  independenceAssessmentBy: String,

  // Committees
  committees: [{
    name: { type: String, enum: ['audit', 'remuneration', 'nominations', 'risk', 'social_ethics', 'investment'] },
    role: { type: String, enum: ['chair', 'member'] },
    appointedDate: Date,
    resignedDate: Date
  }],

  // Shareholding
  shareholding: {
    shares: Number,
    percentage: { type: Number, min: 0, max: 100 },
    class: { type: String, enum: Object.values(SHARE_CLASSES) }
  },

  // Remuneration
  remuneration: {
    salary: Number,
    bonus: Number,
    benefits: Number,
    pension: Number,
    shareOptions: Number,
    total: Number,
    financialYear: String
  },

  // Other directorships
  otherDirectorships: [{
    companyName: String,
    registrationNumber: String,
    role: String,
    appointedDate: Date,
    resignedDate: Date
  }],

  // Disqualifications (Section 69)
  disqualifications: {
    isDisqualified: { type: Boolean, default: false },
    disqualificationReason: String,
    disqualificationDate: Date,
    rehabilitationDate: Date,
    courtOrder: String
  },

  // Criminal record (for declarations)
  criminalRecord: {
    hasCriminalRecord: { type: Boolean, default: false },
    details: String,
    date: Date
  },

  // Insolvency history
  insolvencyHistory: [{
    date: Date,
    details: String,
    rehabilitationDate: Date
  }],

  // FICA Verification
  fica: {
    verified: { type: Boolean, default: false },
    verifiedAt: Date,
    verifiedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    documentIds: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Document' }],
    riskRating: { type: String, enum: ['low', 'medium', 'high'] }
  },

  // POPIA Consent
  popiaConsent: {
    given: { type: Boolean, default: false },
    givenAt: Date,
    revokedAt: Date,
    consentDocumentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' }
  },

  // Documents
  documents: [{
    type: { type: String, enum: ['id', 'passport', 'proof_of_address', 'cv', 'consent', 'other'] },
    documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
    uploadedAt: Date,
    verified: { type: Boolean, default: false }
  }],

  // Audit Trail
  audit: {
    createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    createdAt: { type: Date, default: Date.now },
    updatedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    updatedAt: Date
  }
});
/**
 * Shareholder Schema
 */
const shareholderSchema = new mongoose.Schema({
  shareholderId: {
    type: String,
    default: () => `SH-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`
  },

  entityType: {
    type: String,
    enum: ['individual', 'company', 'trust', 'cc', 'partnership', 'stokvel'],
    required: true
  },

  // If individual
  individual: {
    title: String,
    firstName: String,
    lastName: String,
    idNumber: String,
    passportNumber: String,
    dateOfBirth: Date,
    nationality: String,
    contact: {
      email: String,
      phone: String
    }
  },

  // If company
  company: {
    name: String,
    registrationNumber: String,
    taxNumber: String,
    countryOfIncorporation: { type: String, default: 'ZA' }
  },

  // If trust
  trust: {
    name: String,
    registrationNumber: String,
    trustNumber: String,
    masterReference: String,
    dateEstablished: Date,
    trustees: [{
      name: String,
      idNumber: String
    }]
  },

  // Shareholding Details
  shares: {
    number: { type: Number, required: true, min: 1 },
    class: { type: String, enum: Object.values(SHARE_CLASSES), required: true },
    nominalValue: Number,
    paidUpCapital: Number,
    certificateNumber: String
  },

  ownershipPercentage: {
    type: Number,
    min: 0,
    max: 100
  },

  votingRights: {
    hasVotingRights: { type: Boolean, default: true },
    votesPerShare: { type: Number, default: 1 },
    totalVotes: Number
  },

  acquisitionDate: {
    type: Date,
    required: true
  },

  acquisitionType: {
    type: String,
    enum: ['subscription', 'transfer', 'inheritance', 'donation'],
    default: 'subscription'
  },

  disposalDate: Date,
  disposalReason: String,

  isBeneficialOwner: {
    type: Boolean,
    default: true,
    comment: 'For FICA beneficial ownership register'
  },

  // Certificates
  certificates: [{
    certificateNumber: String,
    issuedDate: Date,
    shareCount: Number,
    documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' }
  }],

  // Shareholder Register
  registerEntries: [{
    entryDate: Date,
    transactionType: { type: String, enum: ['issue', 'transfer', 'cancellation'] },
    sharesChange: Number,
    balanceAfter: Number,
    reference: String
  }]
});
/**
 * Share Register Schema
 */
const shareRegisterSchema = new mongoose.Schema({
  authorizedShares: {
    total: { type: Number, required: true },
    classes: [{
      class: { type: String, enum: Object.values(SHARE_CLASSES) },
      number: Number,
      nominalValue: Number
    }]
  },

  issuedShares: {
    total: { type: Number, default: 0 },
    classes: [{
      class: { type: String, enum: Object.values(SHARE_CLASSES) },
      number: Number,
      percentage: Number
    }]
  },

  unissuedShares: {
    total: Number,
    underOption: Number,
    reserved: Number
  },

  sharePremium: {
    total: Number,
    perShare: Number
  },

  shareholderRegister: [shareholderSchema],

  shareTransfers: [{
    transferDate: Date,
    fromShareholder: String,
    toShareholder: String,
    shares: Number,
    class: String,
    consideration: Number,
    approvedDate: Date,
    approvedBy: String,
    documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' }
  }],

  shareBuybacks: [{
    date: Date,
    shareholder: String,
    shares: Number,
    price: Number,
    consideration: Number,
    approvedBy: String,
    specialResolutionNumber: String
  }]
});
/**
 * Financial Schema (IFRS compliant)
 */
const financialSchema = new mongoose.Schema({
  fiscalYearEnd: {
    type: String,
    enum: Object.values(FINANCIAL_YEAR_END),
    required: true
  },

  currency: {
    type: String,
    enum: ['ZAR', 'USD', 'EUR', 'GBP', 'AUD', 'JPY'],
    default: 'ZAR'
  },

  reportingStandard: {
    type: String,
    enum: ['ifrs', 'ifrs_for_smes', 'sa_gaap'],
    default: 'ifrs'
  },

  // Current Financial Year
  currentFinancialYear: {
    startDate: Date,
    endDate: Date,
    closed: { type: Boolean, default: false }
  },

  // Financial Statements
  financialStatements: [{
    type: { type: String, enum: Object.values(FINANCIAL_STATEMENT_TYPES) },
    year: Number,
    startDate: Date,
    endDate: Date,
    documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
    uploadedAt: Date,
    approvedBy: String,
    approvedAt: Date,
    auditorReport: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' }
  }],

  // Auditor Details
  auditor: {
    name: String,
    firm: String,
    registrationNumber: String,
    irbaNumber: String,
    appointmentDate: Date,
    resignationDate: Date,
    contact: {
      email: String,
      phone: String,
      address: String
    },
    auditPartner: String,
    tenure: Number
  },

  // Audit Committee
  auditCommittee: {
    members: [{
      name: String,
      role: String,
      appointedDate: Date
    }],
    meetings: [{
      date: Date,
      minutes: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' }
    }]
  },

  // Key Financial Metrics
  metrics: [{
    year: Number,
    revenue: Number,
    costOfSales: Number,
    grossProfit: Number,
    operatingExpenses: Number,
    operatingProfit: Number,
    interestIncome: Number,
    interestExpense: Number,
    profitBeforeTax: Number,
    taxExpense: Number,
    profitAfterTax: Number,
    ebitda: Number,
    totalAssets: Number,
    totalLiabilities: Number,
    equity: Number,
    cashAndEquivalents: Number,
    debt: Number,
    workingCapital: Number,
    capex: Number,
    fcf: Number
  }],

  // Ratios
  ratios: [{
    year: Number,
    grossMargin: Number,
    operatingMargin: Number,
    netMargin: Number,
    roe: Number,
    roa: Number,
    currentRatio: Number,
    quickRatio: Number,
    debtToEquity: Number,
    interestCover: Number,
    assetTurnover: Number,
    inventoryTurnover: Number,
    daysSalesOutstanding: Number,
    eps: Number,
    peRatio: Number
  }]
});
/**
 * Compliance Schema (Regulatory Compliance)
 */
const complianceSchema = new mongoose.Schema({
  // CIPC Compliance
  cipc: {
    status: {
      type: String,
      enum: ['compliant', 'non_compliant', 'pending', 'suspended'],
      default: 'pending'
    },
    lastChecked: Date,
    nextCheckDue: Date,

    annualReturns: [{
      year: Number,
      returnMonth: Number,
      dueDate: Date,
      filedDate: Date,
      status: { type: String, enum: ['filed', 'pending', 'overdue'] },
      filingNumber: String,
      receipt: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' }
    }],

    financialStatementsFiled: [{
      year: Number,
      dueDate: Date,
      filedDate: Date,
      status: { type: String, enum: ['filed', 'pending', 'overdue'] },
      receipt: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' }
    }],

    directorsUpdated: {
      lastUpdated: Date,
      nextUpdateDue: Date,
      status: { type: String, enum: ['compliant', 'non_compliant'] }
    },

    beneficialOwnersUpdated: {
      lastUpdated: Date,
      nextUpdateDue: Date,
      status: { type: String, enum: ['compliant', 'non_compliant'] }
    },

    registeredAddressUpdated: {
      lastUpdated: Date,
      nextUpdateDue: Date,
      status: { type: String, enum: ['compliant', 'non_compliant'] }
    }
  },

  // FICA Compliance (Financial Intelligence Centre Act)
  fica: {
    status: { type: String, enum: ['compliant', 'non_compliant', 'pending'] },
    lastChecked: Date,
    nextCheckDue: Date,
    riskRating: { type: String, enum: ['low', 'medium', 'high'] },
    accountableInstitution: { type: Boolean, default: false },
    registrationNumber: String,
    complianceOfficer: {
      name: String,
      contact: String,
      appointmentDate: Date
    },
    riskManagementComplianceProgramme: {
      documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
      approvedDate: Date,
      reviewDate: Date
    }
  },

  // POPIA Compliance
  popia: {
    status: { type: String, enum: ['compliant', 'non_compliant', 'pending'] },
    lastChecked: Date,
    nextCheckDue: Date,
    informationOfficer: {
      name: String,
      contact: String,
      appointmentDate: Date
    },
    deputyInformationOfficer: {
      name: String,
      contact: String
    },
    registrationNumber: String,
    processingActivities: {
      documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
      lastUpdated: Date
    },
    dataSubjectRequests: [{
      requestId: String,
      type: { type: String, enum: ['access', 'correction', 'deletion', 'objection'] },
      requestedAt: Date,
      completedAt: Date,
      status: String
    }],
    securityMeasures: {
      documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
      lastReviewed: Date
    }
  },

  // SARS Compliance
  sars: {
    status: { type: String, enum: ['compliant', 'non_compliant', 'pending'] },
    lastChecked: Date,
    nextCheckDue: Date,

    taxTypes: [{
      type: { type: String, enum: Object.values(SARS_TAX_TYPES) },
      registrationNumber: String,
      status: { type: String, enum: ['compliant', 'non_compliant'] },
      lastReturnFiled: Date,
      nextReturnDue: Date,
      lastPaymentMade: Date,
      nextPaymentDue: Date,
      outstandingBalance: Number
    }],

    taxClearance: {
      pin: String,
      issueDate: Date,
      expiryDate: Date,
      documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' }
    }
  },

  // B-BBEE Compliance
  bbbee: bbbeeSchema,

  // Industry-specific regulatory compliance
  regulatory: [{
    body: { type: String, enum: Object.values(REGULATORY_BODIES) },
    registrationNumber: String,
    status: { type: String, enum: ['compliant', 'non_compliant', 'pending'] },
    lastChecked: Date,
    nextCheckDue: Date,
    licenseNumber: String,
    licenseExpiry: Date,
    licenseDocument: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' }
  }]
});
/**
 * Bank Account Schema
 */
const bankAccountSchema = new mongoose.Schema({
  accountId: {
    type: String,
    default: () => `ACC-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`
  },

  bankName: {
    type: String,
    required: true
  },

  branchName: String,

  branchCode: {
    type: String,
    required: true,
    validate: {
      validator: (v) => /^\d{6}$/.test(v),
      message: 'Branch code must be 6 digits'
    }
  },

  accountNumber: {
    type: String,
    required: true,
    set: (v) => v ? '[REDACTED]' : v // Redacted in database
  },

  accountType: {
    type: String,
    enum: ['cheque', 'savings', 'transmission', 'credit', 'investment'],
    required: true
  },

  accountHolder: {
    type: String,
    required: true
  },

  currency: {
    type: String,
    default: 'ZAR',
    enum: ['ZAR', 'USD', 'EUR', 'GBP']
  },

  isPrimary: {
    type: Boolean,
    default: false
  },

  isActive: {
    type: Boolean,
    default: true
  },

  openedDate: Date,
  closedDate: Date,

  verified: {
    status: { type: Boolean, default: false },
    verifiedAt: Date,
    verifiedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    method: { type: String, enum: ['bank_statement', 'letter', 'online'] }
  },

  // Bank confirmation letter
  confirmationLetter: {
    documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
    uploadedAt: Date
  },

  // For foreign currency accounts
  swiftCode: String,
  iban: String,
  correspondentBank: String
});
/**
 * Business Rescue Schema (Chapter 6)
 */
const businessRescueSchema = new mongoose.Schema({
  status: {
    type: String,
    enum: ['pending', 'active', 'completed', 'terminated']
  },

  commencementDate: Date,

  practitioner: {
    name: String,
    registrationNumber: String,
    contact: String,
    appointmentDate: Date
  },

  plan: {
    documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
    adoptionDate: Date,
    approvalDate: Date,
    amendments: [{
      documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
      date: Date
    }]
  },

  creditorsMeeting: [{
    date: Date,
    minutes: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' }
  }],

  employeesMeeting: [{
    date: Date,
    minutes: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' }
  }],

  progressReports: [{
    period: String,
    reportDate: Date,
    documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' }
  }],

  terminationDate: Date,
  terminationReason: String,
  terminationOrder: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' }
});
/**
 * Liquidation Schema
 */
const liquidationSchema = new mongoose.Schema({
  status: {
    type: String,
    enum: ['provisional', 'final', 'completed']
  },

  type: {
    type: String,
    enum: ['voluntary', 'compulsory', 'creditors']
  },

  commencementDate: Date,

  liquidator: {
    name: String,
    registrationNumber: String,
    contact: String,
    appointmentDate: Date,
    appointmentOrder: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' }
  },

  courtOrder: {
    documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
    court: String,
    caseNumber: String,
    date: Date
  },

  creditorsMeeting: [{
    date: Date,
    minutes: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' }
  }],

  proofOfDebt: [{
    creditor: String,
    amount: Number,
    admitted: Boolean,
    documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' }
  }],

  assetRealization: [{
    asset: String,
    amount: Number,
    date: Date,
    documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' }
  }],

  distribution: [{
    date: Date,
    amount: Number,
    recipients: String,
    documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' }
  }],

  finalizationDate: Date,
  finalReport: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' }
});
// ============================================================================
// MAIN COMPANY SCHEMA
// ============================================================================
const companySchema = new mongoose.Schema({
  // Core Identification
  companyId: {
    type: String,
    required: true,
    unique: true,
    index: true,
    default: () => `CMP-${Date.now()}-${crypto.randomBytes(4).toString('hex')}`
  },
  tenantId: {
    type: String,
    required: true,
    index: true,
    validate: {
      validator: (v) => /^[a-zA-Z0-9_-]{8,64}$/.test(v),
      message: 'tenantId must be 8-64 alphanumeric characters'
    }
  },
  // Basic Information
  name: {
    type: String,
    required: true,
    trim: true,
    maxlength: 200,
    index: true
  },
  tradingName: {
    type: String,
    trim: true,
    maxlength: 200,
    index: true
  },
  previousNames: [{
    name: String,
    registeredDate: Date,
    changedDate: Date
  }],
  type: {
    type: String,
    enum: Object.values(COMPANY_TYPES),
    required: true,
    index: true
  },
  status: {
    type: String,
    enum: Object.values(COMPANY_STATUS),
    default: COMPANY_STATUS.ACTIVE,
    index: true
  },
  industry: {
    type: String,
    enum: Object.values(INDUSTRY_SECTORS),
    required: true,
    index: true
  },
  subIndustry: String,
  size: {
    type: String,
    enum: Object.values(COMPANY_SIZE),
    default: COMPANY_SIZE.MICRO
  },
  // Registration Details (Companies Act)
  registration: {
    type: registrationDetailsSchema,
    required: true
  },
  // SARS Registration
  sars: sarsRegistrationSchema,
  // B-BBEE
  bbbee: bbbeeSchema,
  // Share Capital
  shareCapital: {
    authorized: {
      type: Number,
      required: true,
      min: 0
    },
    issued: {
      type: Number,
      default: 0
    },
    classes: [{
      class: { type: String, enum: Object.values(SHARE_CLASSES) },
      authorized: Number,
      issued: Number,
      nominalValue: Number
    }],
    shareRegister: shareRegisterSchema
  },
  // Directors and Officers
  directors: [directorSchema],
  companySecretary: {
    type: {
      type: String,
      enum: Object.values(COMPANY_SECRETARY_TYPES)
    },
    name: String,
    registrationNumber: String,
    appointmentDate: Date,
    resignationDate: Date,
    contact: {
      email: String,
      phone: String
    }
  },
  // Financial Information
  financials: financialSchema,
  // Employees
  employees: {
    total: { type: Number, default: 0 }
  },
  // Bank Accounts
  bankAccounts: [bankAccountSchema],
  // Business Rescue (if applicable)
  businessRescue: businessRescueSchema,
  // Liquidation (if applicable)
  liquidation: liquidationSchema,
  // Compliance
  compliance: complianceSchema,
  // CIPC Integration Data
  cipcData: {
    lastSync: Date,
    syncStatus: { type: String, enum: ['success', 'failed', 'pending'] },
    rawData: mongoose.Schema.Types.Mixed,
    discrepancies: [{
      field: String,
      cipcValue: mongoose.Schema.Types.Mixed,
      companyValue: mongoose.Schema.Types.Mixed,
      resolved: { type: Boolean, default: false },
      resolvedAt: Date
    }],
    syncHistory: [{
      date: Date,
      status: String,
      message: String
    }]
  },
  // Valuations (summary from Valuation model)
  valuations: {
    count: { type: Number, default: 0 },
    lastValuationDate: Date,
    lastValuationId: { type: mongoose.Schema.Types.ObjectId, ref: 'Valuation' },
    lastValue: Number,
    averageValue: Number,
    minValue: Number,
    maxValue: Number,
    valuationHistory: [{
      valuationId: { type: mongoose.Schema.Types.ObjectId, ref: 'Valuation' },
      date: Date,
      value: Number,
      method: String
    }]
  },
  // Related Entities
  subsidiaries: [{
    companyId: { type: mongoose.Schema.Types.ObjectId, ref: 'Company' },
    ownershipPercentage: Number,
    relationship: { type: String, enum: ['subsidiary', 'associate', 'joint_venture'] },
    consolidated: { type: Boolean, default: true }
  }],
  parentCompany: {
    companyId: { type: mongoose.Schema.Types.ObjectId, ref: 'Company' },
    ownershipPercentage: Number,
    relationship: { type: String, enum: ['subsidiary', 'branch'] }
  },
  holdings: [{
    companyId: { type: mongoose.Schema.Types.ObjectId, ref: 'Company' },
    percentage: Number,
    type: { type: String, enum: ['investment', 'subsidiary'] }
  }],
  // Documents
  documents: [{
    documentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' },
    type: {
      type: String,
      enum: [
        'registration', 'moi', 'amended_moi', 'annual_return',
        'financial_statement', 'tax_return', 'bbbee_certificate',
        'director_id', 'share_certificate', 'special_resolution',
        'ordinary_resolution', 'board_minutes', 'agm_minutes',
        'audit_report', 'bank_confirmation', 'cog', 'other'
      ]
    },
    category: String,
    uploadedAt: Date,
    expiryDate: Date,
    verified: { type: Boolean, default: false },
    verifiedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    verifiedAt: Date,
    notes: String
  }],
  // Tags and Categories
  tags: [String],
  categories: [String],
  // Notes
  notes: String,
  internalNotes: String,
  // Data Retention (POPIA Section 14, Companies Act Section 28)
  retention: {
    policy: {
      type: String,
      enum: [
        'companies_act_10_years',
        'tax_act_5_years',
        'popia_1_year',
        'forensic_permanent'
      ],
      default: 'companies_act_10_years'
    },
    dataResidency: {
      type: String,
      enum: ['ZA', 'US', 'EU', 'GB', 'AU'],
      default: 'ZA'
    },
    retentionStart: { type: Date, default: Date.now },
    retentionEnd: { type: Date },
    archivedAt: Date,
    destroyedAt: Date,
    destructionCertificate: { type: mongoose.Schema.Types.ObjectId, ref: 'Document' }
  },
  // Forensic Integrity
  forensic: {
    hash: {
      type: String,
      required: true,
      unique: true,
      match: /^[a-f0-9]{64}$/
    },
    previousHash: {
      type: String,
      match: /^[a-f0-9]{64}$/
    },
    chainVerified: { type: Boolean, default: false },
    blockchainAnchor: {
      transactionId: String,
      blockNumber: Number,
      network: { type: String, enum: ['ethereum', 'hyperledger', 'none'], default: 'none' },
      timestamp: Date,
      verificationUrl: String
    }
  },
  // Audit Trail
  audit: {
    createdAt: { type: Date, default: Date.now, immutable: true },
    createdBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    updatedAt: { type: Date, default: Date.now },
    updatedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    accessedAt: Date,
    accessedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    changeHistory: [{
      field: String,
      oldValue: mongoose.Schema.Types.Mixed,
      newValue: mongoose.Schema.Types.Mixed,
      changedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
      changedAt: Date,
      reason: String
    }]
  },
  // Version Control
  version: {
    type: Number,
    default: 1
  },
  // Metadata
  metadata: {
    source: { type: String, enum: ['manual', 'cipc_import', 'api', 'migration'] },
    sourceId: String,
    importedAt: Date,
    tags: [String],
    notes: String
  }
}, {
  timestamps: true,
  collection: 'companies',
  strict: true,
  minimize: false,
  toJSON: {
    virtuals: true,
    transform: (doc, ret) => {
      // Remove sensitive fields from JSON output
      delete ret.forensic;
      delete ret.bankAccounts?.accountNumber;
      delete ret.audit?.changeHistory;
      delete ret.metadata;
      return ret;
    }
  },
  toObject: {
    virtuals: true,
    transform: (doc, ret) => {
      delete ret.forensic;
      delete ret.bankAccounts?.accountNumber;
      return ret;
    }
  }
});
// ============================================================================
// INDEXES - COMPREHENSIVE QUERY OPTIMIZATION
// ============================================================================
// Primary lookup indexes
companySchema.index({ tenantId: 1, companyId: 1 });
companySchema.index({ tenantId: 1, name: 1 });
companySchema.index({ tenantId: 1, tradingName: 1 });
companySchema.index({ tenantId: 1, 'registration.registrationNumber': 1 });
companySchema.index({ tenantId: 1, 'sars.taxNumber': 1 });
// Filter indexes
companySchema.index({ tenantId: 1, type: 1, status: 1 });
companySchema.index({ tenantId: 1, industry: 1, size: 1 });
companySchema.index({ tenantId: 1, 'compliance.cipc.status': 1 });
companySchema.index({ tenantId: 1, 'compliance.fica.status': 1 });
companySchema.index({ tenantId: 1, 'compliance.popia.status': 1 });
// Date range indexes
companySchema.index({ tenantId: 1, 'audit.createdAt': -1 });
companySchema.index({ 'retention.retentionEnd': 1 }, { expireAfterSeconds: 0 });
// Director lookup indexes
companySchema.index({ 'directors.idNumber': 1 });
companySchema.index({ 'directors.passportNumber': 1 });
companySchema.index({ 'directors.isActive': 1 });
// Shareholder lookup indexes
companySchema.index({ 'shareCapital.shareRegister.shareholderRegister.entityType': 1 });
companySchema.index({ 'shareCapital.shareRegister.shareholderRegister.individual.idNumber': 1 });
// CIPC sync indexes
companySchema.index({ 'cipcData.lastSync': -1 });
companySchema.index({ 'cipcData.syncStatus': 1 });
// Valuation indexes
companySchema.index({ 'valuations.lastValuationDate': -1 });
companySchema.index({ 'valuations.lastValue': 1 });
// Forensic
companySchema.index({ 'forensic.hash': 1 }, { unique: true });
// Full text search index
companySchema.index({
  name: 'text',
  tradingName: 'text',
  'registration.registrationNumber': 'text',
  'previousNames.name': 'text'
}, {
  weights: {
    name: 10,
    tradingName: 8,
    'registration.registrationNumber': 5,
    'previousNames.name': 3
  },
  name: 'company_search_index'
});
// ============================================================================
// MIDDLEWARE
// ============================================================================
/**
 * Pre-save middleware
 */
companySchema.pre('save', async function (next) {
  try {
    // Update audit timestamp
    this.audit.updatedAt = new Date();
    // Set retention end date
    if (!this.retention.retentionEnd) {
      const endDate = new Date(this.retention.retentionStart || Date.now());

      switch (this.retention.policy) {
        case 'companies_act_10_years':
          endDate.setFullYear(endDate.getFullYear() + 10);
          break;
        case 'tax_act_5_years':
          endDate.setFullYear(endDate.getFullYear() + 5);
          break;
        case 'popia_1_year':
          endDate.setFullYear(endDate.getFullYear() + 1);
          break;
        case 'forensic_permanent':
          endDate.setFullYear(endDate.getFullYear() + 100);
          break;
      }

      this.retention.retentionEnd = endDate;
    }
    // Calculate company size based on turnover and employees
    const turnover = this.financials?.metrics?.[0]?.revenue || 0;
    const employees = this.employees?.total || 0;

    if (turnover < 10000000 && employees < 10) {
      this.size = COMPANY_SIZE.MICRO;
    } else if (turnover < 15000000 && employees < 20) {
      this.size = COMPANY_SIZE.VERY_SMALL;
    } else if (turnover < 50000000 && employees < 50) {
      this.size = COMPANY_SIZE.SMALL;
    } else if (turnover < 500000000 && employees < 250) {
      this.size = COMPANY_SIZE.MEDIUM;
    } else if (turnover < 1000000000 && employees < 1000) {
      this.size = COMPANY_SIZE.LARGE;
    } else if (turnover < 10000000000 && employees < 5000) {
      this.size = COMPANY_SIZE.VERY_LARGE;
    } else {
      this.size = COMPANY_SIZE.ENTERPRISE;
    }
    // Generate forensic hash
    const hashData = {
      companyId: this.companyId,
      tenantId: this.tenantId,
      name: this.name,
      registrationNumber: this.registration?.registrationNumber,
      taxNumber: this.sars?.taxNumber,
      type: this.type,
      status: this.status,
      directors: this.directors?.map(d => ({
        idNumber: d.idNumber,
        firstName: d.firstName,
        lastName: d.lastName,
        isActive: d.isActive
      })),
      version: this.version
    };
    const canonicalData = JSON.stringify(hashData, Object.keys(hashData).sort());
    this.forensic.hash = crypto.createHash('sha256').update(canonicalData).digest('hex');
    // Find previous version for hash chaining
    if (!this.forensic.previousHash) {
      const previousVersion = await this.constructor.findOne({
        'registration.registrationNumber': this.registration?.registrationNumber,
        tenantId: this.tenantId,
        version: this.version - 1
      });
      if (previousVersion) {
        this.forensic.previousHash = previousVersion.forensic.hash;
      }
    }
    this.forensic.chainVerified = true;
    next();
  } catch (error) {
    next(error);
  }
});
/**
 * Pre-update middleware
 */
companySchema.pre('findOneAndUpdate', function () {
  this.set({ 'audit.updatedAt': new Date() });
});
// ============================================================================
// INSTANCE METHODS
// ============================================================================
/**
 * Verify forensic hash integrity
 */
companySchema.methods.verifyIntegrity = function () {
  const hashData = {
    companyId: this.companyId,
    tenantId: this.tenantId,
    name: this.name,
    registrationNumber: this.registration?.registrationNumber,
    taxNumber: this.sars?.taxNumber,
    type: this.type,
    status: this.status,
    directors: this.directors?.map(d => ({
      idNumber: d.idNumber,
      firstName: d.firstName,
      lastName: d.lastName,
      isActive: d.isActive
    })),
    version: this.version
  };
  const canonicalData = JSON.stringify(hashData, Object.keys(hashData).sort());
  const calculatedHash = crypto.createHash('sha256').update(canonicalData).digest('hex');
  return {
    verified: calculatedHash === this.forensic.hash,
    calculated: calculatedHash,
    stored: this.forensic.hash,
    chainVerified: this.forensic.chainVerified
  };
};
/**
 * Get primary address
 */
companySchema.methods.getPrimaryAddress = function () {
  return this.registration?.registeredAddress;
};
/**
 * Get active directors
 */
companySchema.methods.getActiveDirectors = function () {
  return this.directors?.filter(d => d.isActive) || [];
};
/**
 * Get directors by role
 */
companySchema.methods.getDirectorsByRole = function (role) {
  return this.directors?.filter(d => d.isActive && d.role === role) || [];
};
/**
 * Add director
 */
companySchema.methods.addDirector = async function (directorData, userId) {
  const director = {
    ...directorData,
    appointmentDate: new Date(),
    isActive: true,
    audit: {
      createdBy: userId,
      createdAt: new Date()
    }
  };

  this.directors.push(director);

  this.audit.changeHistory.push({
    field: 'directors',
    action: 'add',
    newValue: director.idNumber,
    changedBy: userId,
    changedAt: new Date()
  });

  return this.save();
};
/**
 * Remove director
 */
companySchema.methods.removeDirector = async function (directorId, userId, reason) {
  const director = this.directors.id(directorId);
  if (director) {
    director.isActive = false;
    director.resignationDate = new Date();
    director.resignationReason = reason;

    director.audit.updatedBy = userId;
    director.audit.updatedAt = new Date();

    this.audit.changeHistory.push({
      field: 'directors',
      action: 'remove',
      oldValue: director.idNumber,
      changedBy: userId,
      changedAt: new Date(),
      reason
    });
  }

  return this.save();
};
/**
 * Update director
 */
companySchema.methods.updateDirector = async function (directorId, updates, userId) {
  const director = this.directors.id(directorId);
  if (director) {
    const oldValues = {};

    Object.keys(updates).forEach(key => {
      if (director[key] !== undefined) {
        oldValues[key] = director[key];
        director[key] = updates[key];
      }
    });

    director.audit.updatedBy = userId;
    director.audit.updatedAt = new Date();

    this.audit.changeHistory.push({
      field: 'directors',
      action: 'update',
      oldValue: oldValues,
      newValue: updates,
      changedBy: userId,
      changedAt: new Date()
    });
  }

  return this.save();
};
/**
 * Add shareholder
 */
companySchema.methods.addShareholder = async function (shareholderData, userId) {
  if (!this.shareCapital?.shareRegister?.shareholderRegister) {
    this.shareCapital = this.shareCapital || {};
    this.shareCapital.shareRegister = this.shareCapital.shareRegister || {};
    this.shareCapital.shareRegister.shareholderRegister = [];
  }

  const shareholder = {
    ...shareholderData,
    acquisitionDate: new Date()
  };

  this.shareCapital.shareRegister.shareholderRegister.push(shareholder);

  // Update issued shares
  if (this.shareCapital.issued !== undefined) {
    this.shareCapital.issued += shareholder.shares?.number || 0;
  }

  this.audit.changeHistory.push({
    field: 'shareholders',
    action: 'add',
    newValue: shareholder.shareholderId,
    changedBy: userId,
    changedAt: new Date()
  });

  return this.save();
};
/**
 * Update valuation summary
 */
companySchema.methods.updateValuationSummary = async function (valuation) {
  const current = this.valuations || {};

  const newCount = (current.count || 0) + 1;
  const newValue = valuation.finalValuation?.weightedAverage || 0;

  this.valuations = {
    count: newCount,
    lastValuationDate: new Date(),
    lastValuationId: valuation._id,
    lastValue: newValue,
    averageValue: current.averageValue ?
      ((current.averageValue * (newCount - 1)) + newValue) / newCount : newValue,
    minValue: Math.min(current.minValue || Infinity, newValue),
    maxValue: Math.max(current.maxValue || -Infinity, newValue),
    valuationHistory: [
      ...(current.valuationHistory || []).slice(-9),
      {
        valuationId: valuation._id,
        date: new Date(),
        value: newValue,
        method: valuation.methods?.methodCount > 0 ? 'multiple' : 'single'
      }
    ]
  };

  return this.save();
};
/**
 * Check compliance status
 */
companySchema.methods.checkCompliance = async function () {
  const now = new Date();
  const status = {
    overall: 'compliant',
    issues: []
  };

  // Check CIPC compliance
  if (this.compliance?.cipc?.status !== 'compliant') {
    status.overall = 'non_compliant';
    status.issues.push('CIPC compliance issue');
  }

  // Check FICA compliance
  if (this.compliance?.fica?.status !== 'compliant') {
    status.overall = 'non_compliant';
    status.issues.push('FICA compliance issue');
  }

  // Check POPIA compliance
  if (this.compliance?.popia?.status !== 'compliant') {
    status.overall = 'non_compliant';
    status.issues.push('POPIA compliance issue');
  }

  // Check SARS compliance
  if (this.compliance?.sars?.status !== 'compliant') {
    status.overall = 'non_compliant';
    status.issues.push('SARS compliance issue');
  }

  // Check B-BBEE expiry
  if (this.bbbee?.expiryDate && this.bbbee.expiryDate < now) {
    status.overall = 'non_compliant';
    status.issues.push('B-BBEE certificate expired');
  }

  return status;
};
/**
 * Sync with CIPC
 */
companySchema.methods.syncWithCIPC = async function (cipcData, userId) {
  const discrepancies = [];

  // Check for discrepancies
  if (cipcData.companyName && cipcData.companyName !== this.name) {
    discrepancies.push({
      field: 'name',
      cipcValue: cipcData.companyName,
      companyValue: this.name
    });
  }

  if (cipcData.registrationNumber && cipcData.registrationNumber !== this.registration?.registrationNumber) {
    discrepancies.push({
      field: 'registrationNumber',
      cipcValue: cipcData.registrationNumber,
      companyValue: this.registration?.registrationNumber
    });
  }

  if (cipcData.status && cipcData.status !== this.status) {
    discrepancies.push({
      field: 'status',
      cipcValue: cipcData.status,
      companyValue: this.status
    });
  }

  this.cipcData = {
    lastSync: new Date(),
    syncStatus: discrepancies.length > 0 ? 'discrepancies' : 'success',
    rawData: cipcData,
    discrepancies,
    syncHistory: [
      ...(this.cipcData?.syncHistory || []).slice(-19),
      {
        date: new Date(),
        status: discrepancies.length > 0 ? 'discrepancies' : 'success',
        message: `Sync completed with ${discrepancies.length} discrepancies`
      }
    ]
  };

  this.audit.changeHistory.push({
    field: 'cipcData',
    action: 'sync',
    details: { discrepanciesFound: discrepancies.length },
    changedBy: userId,
    changedAt: new Date()
  });

  return this.save();
};
/**
 * Get redacted version for external sharing
 */
companySchema.methods.getRedactedVersion = function (includeSensitive = false) {
  const redacted = this.toObject();

  // Always remove forensic data
  delete redacted.forensic;

  if (!includeSensitive) {
    // Remove sensitive fields
    delete redacted.bankAccounts;
    delete redacted.audit?.changeHistory;
    delete redacted.metadata;

    // Redact director IDs
    if (redacted.directors) {
      redacted.directors.forEach(d => {
        d.idNumber = d.idNumber ? d.idNumber.replace(/\d(?=\d{4})/g, '*') : d.idNumber;
        if (d.passportNumber) d.passportNumber = '*********';
      });
    }

    // Redact shareholder IDs
    if (redacted.shareCapital?.shareRegister?.shareholderRegister) {
      redacted.shareCapital.shareRegister.shareholderRegister.forEach(s => {
        if (s.individual?.idNumber) {
          s.individual.idNumber = s.individual.idNumber.replace(/\d(?=\d{4})/g, '*');
        }
      });
    }
  }

  return redacted;
};
// ============================================================================
// STATIC METHODS
// ============================================================================
/**
 * Find by registration number
 */
companySchema.statics.findByRegistrationNumber = function (registrationNumber, tenantId) {
  return this.findOne({
    'registration.registrationNumber': registrationNumber,
    tenantId
  });
};
/**
 * Find by tax number
 */
companySchema.statics.findByTaxNumber = function (taxNumber, tenantId) {
  return this.findOne({
    'sars.taxNumber': taxNumber,
    tenantId
  });
};
/**
 * Find by director ID
 */
companySchema.statics.findByDirectorId = function (idNumber, tenantId) {
  return this.find({
    'directors.idNumber': idNumber,
    tenantId,
    'directors.isActive': true
  });
};
/**
 * Find companies requiring compliance review
 */
companySchema.statics.findComplianceDue = function (tenantId) {
  const oneYearAgo = new Date();
  oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);

  return this.find({
    tenantId,
    $or: [
      { 'compliance.fica.lastChecked': { $lt: oneYearAgo } },
      { 'compliance.popia.lastChecked': { $lt: oneYearAgo } },
      { 'compliance.cipc.status': { $ne: 'compliant' } }
    ]
  });
};
/**
 * Find companies requiring annual return filing
 */
companySchema.statics.findAnnualReturnsDue = function (tenantId) {
  const currentYear = new Date().getFullYear();

  return this.find({
    tenantId,
    status: COMPANY_STATUS.ACTIVE,
    'compliance.cipc.annualReturns': {
      $not: {
        $elemMatch: { year: currentYear, status: 'filed' }
      }
    }
  });
};
/**
 * Find companies by size category
 */
companySchema.statics.findBySize = function (size, tenantId, options = {}) {
  const { limit = 100, skip = 0 } = options;

  return this.find({
    tenantId,
    size
  })
    .skip(skip)
    .limit(limit)
    .sort({ 'financials.metrics.revenue': -1 });
};
/**
 * Get industry statistics
 */
companySchema.statics.getIndustryStats = async function (tenantId) {
  return this.aggregate([
    { $match: { tenantId } },
    {
      $group: {
        _id: '$industry',
        count: { $sum: 1 },
        avgRevenue: { $avg: '$financials.metrics.revenue' },
        avgEmployees: { $avg: '$employees.total' },
        totalValuation: { $sum: '$valuations.lastValue' },
        compliantCount: {
          $sum: {
            $cond: [{ $eq: ['$compliance.cipc.status', 'compliant'] }, 1, 0]
          }
        }
      }
    },
    { $sort: { count: -1 } }
  ]);
};
/**
 * Get size distribution
 */
companySchema.statics.getSizeDistribution = async function (tenantId) {
  return this.aggregate([
    { $match: { tenantId } },
    {
      $group: {
        _id: '$size',
        count: { $sum: 1 },
        totalRevenue: { $sum: '$financials.metrics.revenue' },
        avgValuation: { $avg: '$valuations.averageValue' },
        avgEmployees: { $avg: '$employees.total' }
      }
    },
    { $sort: { count: -1 } }
  ]);
};
/**
 * Search companies
 */
companySchema.statics.search = function (query, tenantId, options = {}) {
  const { limit = 20, skip = 0 } = options;

  return this.find({
    tenantId,
    $text: { $search: query }
  })
    .select('-forensic -bankAccounts -audit.changeHistory')
    .sort({ score: { $meta: 'textScore' } })
    .skip(skip)
    .limit(limit)
    .lean();
};
/**
 * Get companies for valuation
 */
companySchema.statics.getForValuation = function (tenantId, options = {}) {
  const { limit = 50, minRevenue = 0, includeInactive = false } = options;

  const query = {
    tenantId,
    'financials.metrics.revenue': { $gte: minRevenue }
  };

  if (!includeInactive) {
    query.status = COMPANY_STATUS.ACTIVE;
  }

  return this.find(query)
    .select('companyId name type industry size financials.metrics valuations')
    .limit(limit)
    .lean();
};
// ============================================================================
// VIRTUAL PROPERTIES
// ============================================================================
/**
 * Full registered address string
 */
companySchema.virtual('registeredAddressString').get(function () {
  const addr = this.registration?.registeredAddress;
  if (!addr) return '';

  return `${addr.streetAddress}, ${addr.suburb ? addr.suburb + ', ' : ''}${addr.city}, ${addr.postalCode}`;
});
/**
 * Director count
 */
companySchema.virtual('directorCount').get(function () {
  return this.directors?.filter(d => d.isActive).length || 0;
});
/**
 * Shareholder count
 */
companySchema.virtual('shareholderCount').get(function () {
  return this.shareCapital?.shareRegister?.shareholderRegister?.length || 0;
});
/**
 * Compliance score (0-100)
 */
companySchema.virtual('complianceScore').get(function () {
  let score = 0;
  let total = 5;

  if (this.compliance?.cipc?.status === 'compliant') score++;
  if (this.compliance?.fica?.status === 'compliant') score++;
  if (this.compliance?.popia?.status === 'compliant') score++;
  if (this.compliance?.sars?.status === 'compliant') score++;
  if (this.bbbee?.expiryDate && this.bbbee.expiryDate > new Date()) score++;

  return Math.round((score / total) * 100);
});
/**
 * Age in years
 */
companySchema.virtual('ageInYears').get(function () {
  const age = Date.now() - this.registration?.incorporationDate.getTime();
  return Math.floor(age / (1000 * 60 * 60 * 24 * 365));
});
/**
 * Is JSE listed
 */
companySchema.virtual('isJSEListed').get(function () {
  return [COMPANY_SIZE.JSE_TOP_40, COMPANY_SIZE.JSE_MID_CAP, COMPANY_SIZE.JSE_SMALL_CAP, COMPANY_SIZE.ALTX].includes(this.size);
});
/**
 * Is B-BBEE compliant
 */
companySchema.virtual('isBBBEECompliant').get(function () {
  return this.bbbee?.level && this.bbbee.level <= 4 && this.bbbee?.expiryDate > new Date();
});
// ============================================================================
// EXPORTS
// ============================================================================
const Company = mongoose.model('Company', companySchema);
export default Company;