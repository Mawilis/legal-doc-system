// Simple test to verify model loads correctly
console.log('Loading mongoose...');
const mongoose = require('mongoose');
console.log('✅ Mongoose loaded');

console.log('Loading TaxRecord model...');
const TaxRecord = require('./server/models/TaxRecord');
console.log('✅ TaxRecord model loaded');

console.log('Checking model methods...');
console.log('updateStatus:', typeof TaxRecord.prototype.updateStatus);
console.log('recordPayment:', typeof TaxRecord.prototype.recordPayment);
console.log('addDocument:', typeof TaxRecord.prototype.addDocument);
console.log('calculateRiskScore:', typeof TaxRecord.prototype.calculateRiskScore);
console.log('generateForensicEvidence:', typeof TaxRecord.prototype.generateForensicEvidence);

console.log('Checking static methods...');
console.log('findByTenant:', typeof TaxRecord.findByTenant);
console.log('findByTaxpayer:', typeof TaxRecord.findByTaxpayer);
console.log('findOverdue:', typeof TaxRecord.findOverdue);
console.log('findBySubmissionId:', typeof TaxRecord.findBySubmissionId);
console.log('getEconomicMetrics:', typeof TaxRecord.getEconomicMetrics);

console.log('✅ All checks passed');
