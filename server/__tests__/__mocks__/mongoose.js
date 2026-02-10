// Mock mongoose for testing
const mongoose = jest.createMockFromModule('mongoose');

let connectionState = 1; // 1 = connected

// Mock connection
mongoose.connect = jest.fn().mockResolvedValue({
  connection: { readyState: 1 }
});

mongoose.connection = {
  readyState: 1,
  close: jest.fn().mockResolvedValue(null),
  dropCollection: jest.fn().mockResolvedValue(true),
  collection: jest.fn().mockReturnValue({
    find: jest.fn().mockReturnValue({
      toArray: jest.fn().mockResolvedValue([])
    }),
    updateOne: jest.fn().mockResolvedValue({ modifiedCount: 1 }),
    updateMany: jest.fn().mockResolvedValue({ modifiedCount: 1 }),
    countDocuments: jest.fn().mockResolvedValue(0)
  })
};

// Mock Schema and Model
mongoose.Schema = jest.fn().mockImplementation(() => ({
  index: jest.fn(),
  pre: jest.fn(),
  post: jest.fn(),
  method: jest.fn(),
  static: jest.fn(),
  virtual: jest.fn().mockReturnValue({
    get: jest.fn(),
    set: jest.fn()
  })
}));

mongoose.model = jest.fn().mockReturnValue({
  find: jest.fn().mockReturnValue({
    populate: jest.fn().mockResolvedValue([])
  }),
  findOne: jest.fn().mockResolvedValue(null),
  findById: jest.fn().mockResolvedValue(null),
  countDocuments: jest.fn().mockResolvedValue(0),
  deleteMany: jest.fn().mockResolvedValue({ deletedCount: 0 }),
  aggregate: jest.fn().mockResolvedValue([])
});

mongoose.Types = {
  ObjectId: {
    isValid: jest.fn().mockReturnValue(true)
  }
};

module.exports = mongoose;
