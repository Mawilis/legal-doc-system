import * as chai from 'chai';
import sinon from 'sinon';
import mongoose from 'mongoose';
import blockchainService from '../../services/blockchainService.js';

const { expect } = chai;

describe('🔗 Blockchain Service - WILSY OS 2050 FORENSIC TEST SUITE', () => {
  it('should verify the service is running in ESM mode', () => {
    expect(blockchainService).to.not.be.undefined;
    expect(blockchainService.network).to.equal('hyperledger-fabric-2.5');
  });
  
  // Your other test cases will follow...
});
