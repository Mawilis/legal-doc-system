/* eslint-disable */
/**
 * 🧪 TaxCompliance Forensic Audit
 * @description Verifying VAT/Tax accuracy for ZA and TZ nodes.
 */
import { expect } from 'chai';
import TaxComplianceService from '../../services/finance/TaxCompliance.service.js';

describe('⚖️ TaxCompliance Sovereign Audit', () => {
  it('calculates 15% VAT for South African (ZA) transactions', async () => {
    const amount = 1000000; // R1M
    const report = await TaxComplianceService.calculateTax(amount, 'ZA');

    expect(report.taxAmount).to.equal(150000);
    expect(report.totalWithTax).to.equal(1150000);
    expect(report.taxSignature).to.have.lengthOf(128); // SHA-512 Verification
  });

  it('calculates 18% VAT for Tanzanian (TZ) transactions', async () => {
    const amount = 1000000;
    const report = await TaxComplianceService.calculateTax(amount, 'TZ');

    expect(report.taxAmount).to.equal(180000);
    expect(report.totalWithTax).to.equal(1180000);
  });
});
