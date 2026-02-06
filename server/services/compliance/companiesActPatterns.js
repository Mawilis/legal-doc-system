module.exports = [
  {
    regex: /retention.*less than \d+ years/i,
    violation: 'INADEQUATE_RETENTION',
    severity: 8,
    legalReference: 'Companies Act §50',
    remediation: 'Specify minimum 5-year retention'
  }
];
