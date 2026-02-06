// Mock mongoose for testing
const mongoose = jest.createMockFromModule('mongoose');

let connectionState = 1; // 1 = connected

mongoose.connect = jest.fn().mockResolvedValue({
  connection: {
    readyState: 1,
    db: {
      databaseName: 'test_db'
    }
  }
});

mongoose.disconnect = jest.fn().mockResolvedValue(true);

mongoose.connection = {
  readyState: 1,
  close: jest.fn().mockResolvedValue(true),
  db: {
    databaseName: 'test_db'
  }
};

mongoose.Schema = jest.fn().mockImplementation(() => ({
  index: jest.fn(),
  pre: jest.fn(),
  post: jest.fn(),
  virtual: jest.fn().mockReturnThis(),
  get: jest.fn(),
  set: jest.fn()
}));

mongoose.Schema.Types = {
  ObjectId: 'ObjectId',
  String: 'String',
  Number: 'Number',
  Date: 'Date',
  Boolean: 'Boolean',
  Mixed: 'Mixed'
};

mongoose.Types = {
  ObjectId: jest.fn().mockImplementation((id) => ({
    toHexString: () => id || 'mockObjectId',
    toString: () => id || 'mockObjectId'
  }))
};

mongoose.model = jest.fn().mockReturnValue({
  find: jest.fn().mockReturnValue({
    sort: jest.fn().mockReturnThis(),
    limit: jest.fn().mockReturnThis(),
    skip: jest.fn().mockReturnThis(),
    populate: jest.fn().mockReturnThis(),
    lean: jest.fn().mockReturnThis(),
    exec: jest.fn().mockResolvedValue([])
  }),
  findById: jest.fn().mockReturnValue({
    exec: jest.fn().mockResolvedValue(null)
  }),
  findOne: jest.fn().mockReturnValue({
    exec: jest.fn().mockResolvedValue(null)
  }),
  create: jest.fn().mockResolvedValue({}),
  save: jest.fn().mockResolvedValue({}),
  deleteMany: jest.fn().mockResolvedValue({}),
  updateOne: jest.fn().mockResolvedValue({})
});

module.exports = mongoose;
EOFcat > __tests__/__mocks__/mongoose.js << 'EOF'
// Mock mongoose for testing
const mongoose = jest.createMockFromModule('mongoose');

let connectionState = 1; // 1 = connected

mongoose.connect = jest.fn().mockResolvedValue({
  connection: {
    readyState: 1,
    db: {
      databaseName: 'test_db'
    }
  }
});

mongoose.disconnect = jest.fn().mockResolvedValue(true);

mongoose.connection = {
  readyState: 1,
  close: jest.fn().mockResolvedValue(true),
  db: {
    databaseName: 'test_db'
  }
};

mongoose.Schema = jest.fn().mockImplementation(() => ({
  index: jest.fn(),
  pre: jest.fn(),
  post: jest.fn(),
  virtual: jest.fn().mockReturnThis(),
  get: jest.fn(),
  set: jest.fn()
}));

mongoose.Schema.Types = {
  ObjectId: 'ObjectId',
  String: 'String',
  Number: 'Number',
  Date: 'Date',
  Boolean: 'Boolean',
  Mixed: 'Mixed'
};

mongoose.Types = {
  ObjectId: jest.fn().mockImplementation((id) => ({
    toHexString: () => id || 'mockObjectId',
    toString: () => id || 'mockObjectId'
  }))
};

mongoose.model = jest.fn().mockReturnValue({
  find: jest.fn().mockReturnValue({
    sort: jest.fn().mockReturnThis(),
    limit: jest.fn().mockReturnThis(),
    skip: jest.fn().mockReturnThis(),
    populate: jest.fn().mockReturnThis(),
    lean: jest.fn().mockReturnThis(),
    exec: jest.fn().mockResolvedValue([])
  }),
  findById: jest.fn().mockReturnValue({
    exec: jest.fn().mockResolvedValue(null)
  }),
  findOne: jest.fn().mockReturnValue({
    exec: jest.fn().mockResolvedValue(null)
  }),
  create: jest.fn().mockResolvedValue({}),
  save: jest.fn().mockResolvedValue({}),
  deleteMany: jest.fn().mockResolvedValue({}),
  updateOne: jest.fn().mockResolvedValue({})
});

module.exports = mongoose;
