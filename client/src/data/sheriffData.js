
export const SHERIFF_SERVICE_TYPES = [
  { id: 'service_summons', label: 'Service of Summons', baseFee: 180.00, desc: 'Standard service of initiating process' },
  { id: 'service_urgent', label: 'Urgent Service (Rule 6(12))', baseFee: 350.00, desc: 'Priority dispatch (24h SLA)' },
  { id: 'execution_writ', label: 'Writ of Execution', baseFee: 550.00, desc: 'Attachment of movable assets' },
  { id: 'ejectment', label: 'Ejectment / Eviction', baseFee: 850.00, desc: 'Removal of occupants (Requires SAPS)' },
  { id: 'interdict', label: 'Service of Interdict', baseFee: 400.00, desc: 'Personal service mandatory' }
];

export const RISK_FLAGS = [
  { id: 'saps', label: 'SAPS Support Required' },
  { id: 'dog', label: 'Dangerous Animals' },
  { id: 'access', label: 'Restricted Access / Estate' },
  { id: 'hostile', label: 'Hostile Respondent' }
];

export const TRAVEL_RATE = 6.50; // R6.50 per km
