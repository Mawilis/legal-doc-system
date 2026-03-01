#!import mongoose from 'mongoose';
import { expect } from 'chai';

describe('Import Verification', function() {
  it('should have correct imports', function() {
    expect(mongoose).to.be.ok;
    console.log('✅ Mongoose import works');
  });
});
