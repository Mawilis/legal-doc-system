// Load test environment variables
require('dotenv').config({ path: './server/.env.test' });

// Mock mongoose completely BEFORE any imports
jest.mock('mongoose', () => {
  // Create a proper mock Schema with Types
  const mockSchema = {
    pre: jest.fn().mockReturnThis(),
    post: jest.fn().mockReturnThis(),
    index: jest.fn().mockReturnThis(),
    virtual: jest.fn().mockReturnThis(),
    set: jest.fn().mockReturnThis(),
    get: jest.fn().mockReturnThis()
  };

  // Create a constructor function that returns the mockSchema
  const Schema = jest.fn().mockImplementation(() => mockSchema);
  
  // Add Types to the Schema constructor
  Schema.Types = {
    Mixed: 'Mixed',
    ObjectId: 'ObjectId',
    String: String,
    Number: Number,
    Date: Date,
    Boolean: Boolean
  };

  return {
    Schema,
    model: jest.fn().mockImplementation(() => ({
      find: jest.fn(),
      findOne: jest.fn(),
      findById: jest.fn(),
      create: jest.fn(),
      updateOne: jest.fn(),
      deleteOne: jest.fn(),
      aggregate: jest.fn()
    })),
    connect: jest.fn().mockResolvedValue(),
    disconnect: jest.fn().mockResolvedValue(),
    Types: {
      Mixed: 'Mixed',
      ObjectId: 'ObjectId',
      String: String,
      Number: Number,
      Date: Date,
      Boolean: Boolean
    }
  };
});

// Mock all utilities
jest.mock('../utils/performance', () => ({
  PerformanceMonitor: jest.fn().mockImplementation(() => ({
    startTimer: jest.fn(),
    endTimer: jest.fn().mockReturnValue(100),
    measure: jest.fn().mockImplementation((_, fn) => fn()),
    record: jest.fn().mockReturnValue([{ value: 100 }]),
    getMetrics: jest.fn().mockReturnValue({}),
    getRecords: jest.fn().mockReturnValue({})
  }))
}));

jest.mock('../utils/retention', () => ({
  RetentionManager: jest.fn().mockImplementation(() => ({
    getPolicy: jest.fn().mockReturnValue({ name: 'test-policy', duration: 3650 }),
    calculateExpiryDate: jest.fn().mockReturnValue(new Date()),
    isExpired: jest.fn().mockReturnValue(false),
    daysUntilExpiry: jest.fn().mockReturnValue(3650)
  }))
}));

jest.mock('../utils/legalHold', () => ({
  LegalHoldManager: jest.fn().mockImplementation(() => ({
    createHold: jest.fn(),
    placeHoldOnRecord: jest.fn(),
    isRecordOnHold: jest.fn().mockReturnValue(false),
    getHoldsForRecord: jest.fn().mockReturnValue([]),
    releaseHold: jest.fn(),
    getActiveHolds: jest.fn().mockReturnValue([])
  }))
}));

jest.mock('../utils/regulatoryCalendar', () => ({
  RegulatoryCalendar: jest.fn().mockImplementation(() => ({
    isHoliday: jest.fn().mockReturnValue(false),
    isWeekend: jest.fn().mockReturnValue(false),
    isBusinessDay: jest.fn().mockReturnValue(true),
    addBusinessDays: jest.fn().mockReturnValue(new Date()),
    getQuarterDates: jest.fn().mockReturnValue({}),
    getRegulatoryDeadlines: jest.fn().mockReturnValue({}),
    daysUntilDeadline: jest.fn().mockReturnValue(30),
    initialize: jest.fn().mockReturnThis()
  }))
}));

// Mock cryptoUtils to avoid encryption key validation
jest.mock('../utils/cryptoUtils', () => ({
  generateForensicHash: jest.fn().mockReturnValue('mock-hash-1234567890abcdef'),
  encrypt: jest.fn().mockReturnValue('encrypted-data'),
  decrypt: jest.fn().mockReturnValue({})
}));
