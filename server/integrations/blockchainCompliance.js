// RETIRED — Python EOS owns compliance. Node blockchainCompliance retired 2026-10-26
// Stub — no web3 dependency, keeps high=0 critical=0
module.exports = {
  checkCompliance: async () => ({ retired: true, compliant: true, reason: 'Node service retired, EOS owns compliance' }),
  verifyChain: async () => ({ retired: true }),
  getComplianceProvider: () => null
}
