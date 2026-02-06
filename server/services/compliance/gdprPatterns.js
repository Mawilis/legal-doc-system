module.exports = [
  {
    regex: /process.*personal data.*without.*lawful basis/i,
    violation: 'LAWFUL_BASIS_VIOLATION',
    severity: 9,
    legalReference: 'GDPR Art.6',
    remediation: 'Specify lawful basis'
  }
];
