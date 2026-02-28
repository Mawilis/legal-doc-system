/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - EQUITY & ARR VALUATION FORENSICS                              ║
 * ║ Validates R650M ARR target | 15x multiple | R9.75B valuation             ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

import { expect } from 'chai';
import { 
  calculateARR, 
  projectInvestorReturns, 
  getCapTable,
  getInvestorBreakdown,
  projectValuationAtMultiple
} from '../../services/finance/payoutService.js';

describe('💰 WILSY OS - Cap Table & Payout Service', () => {
  
  it('should accurately calculate $650M ARR and Investor Equity Value', () => {
    // Target: $650M ARR (R9.75B at current exchange)
    const currentMRR = 54166666.67; // ~$54.16M MRR (produces $650M ARR)
    
    const arr = calculateARR(currentMRR);
    const investorEquityValue = projectInvestorReturns(arr, 15); // 15x SaaS Multiple

    console.log('\n' + '='.repeat(70));
    console.log('📈 WILSY OS: INVESTOR RETURN PROJECTIONS');
    console.log('='.repeat(70));
    console.log(`🏦 Annual Run Rate (ARR): $${(arr / 1e6).toFixed(2)}M`);
    console.log(`💎 Platform Valuation (15x): $${((arr * 15) / 1e9).toFixed(2)}B`);
    console.log(`⚖️  Investor Equity Value (20%): $${(investorEquityValue / 1e9).toFixed(2)}B`);
    console.log(`💰 Founder Equity Value (60%): $${((arr * 15 * 0.6) / 1e9).toFixed(2)}B`);
    console.log(`👥 Employee Pool Value (20%): $${((arr * 15 * 0.2) / 1e9).toFixed(2)}B`);
    console.log('='.repeat(70));

    expect(arr).to.be.closeTo(650000000, 1000000); // $650M ARR ± $1M
    expect(getCapTable().investors).to.equal(0.20);
    expect(investorEquityValue).to.be.greaterThan(1000000000); // > $1B
    expect(investorEquityValue).to.be.closeTo(1950000000, 10000000); // $1.95B
  });

  it('should return correct cap table structure', () => {
    const capTable = getCapTable();
    
    expect(capTable).to.be.an('object');
    expect(capTable.founders).to.equal(0.60);
    expect(capTable.investors).to.equal(0.20);
    expect(capTable.employeePool).to.equal(0.20);
    
    const breakdown = getInvestorBreakdown();
    expect(breakdown.totalShares).to.equal(100000000);
    expect(breakdown.founders.shares).to.equal(60000000);
    expect(breakdown.investors.shares).to.equal(20000000);
    expect(breakdown.employeePool.shares).to.equal(20000000);
    
    console.log('\n📋 CAP TABLE VERIFICATION:');
    console.log(`  • Founders: ${breakdown.founders.percentage} (${breakdown.founders.shares.toLocaleString()} shares)`);
    console.log(`  • Investors: ${breakdown.investors.percentage} (${breakdown.investors.shares.toLocaleString()} shares)`);
    console.log(`  • Employee Pool: ${breakdown.employeePool.percentage} (${breakdown.employeePool.shares.toLocaleString()} shares)`);
  });

  it('should project valuations at different multiples', () => {
    const arr = 650000000; // $650M ARR
    const projections = projectValuationAtMultiple(arr, [10, 15, 20, 25, 30]);
    
    expect(projections).to.have.lengthOf(5);
    
    console.log('\n📊 VALUATION AT DIFFERENT MULTIPLES:');
    projections.forEach(p => {
      console.log(`  • ${p.multiple}x: $${(p.valuation / 1e9).toFixed(2)}B (Investor: $${(p.investorValue / 1e9).toFixed(2)}B)`);
    });
    
    // Verify 15x multiple gives $9.75B valuation
    const fifteenX = projections.find(p => p.multiple === 15);
    expect(fifteenX.valuation).to.equal(9750000000);
    expect(fifteenX.investorValue).to.equal(1950000000);
  });
});
