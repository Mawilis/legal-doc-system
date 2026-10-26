// RETIRED — Python EOS owns evidence anchoring. Node blockchainService retired 2026-10-26
// Stub to keep imports from crashing, no web3 dependency
module.exports = {
  anchorHash: async () => ({ retired: true, anchored: false, reason: 'Node service retired, EOS owns anchoring' }),
  verifyAnchor: async () => ({ retired: true, verified: false }),
  getProvider: () => null
}
