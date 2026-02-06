module.exports = [
  {
    regex: /personal information.*without consent/i,
    violation: 'CONSENT_VIOLATION',
    severity: 9,
    legalReference: 'POPIA §11',
    remediation: 'Insert explicit consent clause with opt-in mechanism'
  },
  {
    regex: /data breach.*no liability/i,
    violation: 'BREACH_NOTIFICATION_VIOLATION',
    severity: 10,
    legalReference: 'POPIA §22',
    remediation: 'Add 72-hour breach notification clause with regulator reporting'
  }
];
