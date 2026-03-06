#!import mongoose from 'mongoose';
import { expect } from 'chai';

describe('Import Verification', () => {
  it('should have correct imports', () => {
    expect(mongoose).to.be.ok;
    console.log('✅ Mongoose import works');
  });
});
