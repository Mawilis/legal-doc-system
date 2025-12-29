
export const LITIGATION_TYPES = [
  { id: 'combined_summons', label: 'Combined Summons', desc: 'Liquidated demands with dispute of fact', icon: '📜', baseFee: 2500 },
  { id: 'simple_summons', label: 'Simple Summons', desc: 'Liquidated debt/demands only', icon: '💰', baseFee: 1500 },
  { id: 'notice_motion', label: 'Notice of Motion', desc: 'Standard Application Procedure', icon: '📝', baseFee: 3500 },
  { id: 'urgent_app', label: 'Urgent Application', desc: 'Rule 6(12) - Priority handling', icon: '🚨', baseFee: 8500 },
  { id: 'default_judgment', label: 'Default Judgment', desc: 'Unopposed request for judgment', icon: '🔨', baseFee: 1200 },
  { id: 'rescission', label: 'Rescission of Judgment', desc: 'Application to set aside judgment', icon: '↩️', baseFee: 4000 },
  { id: 'interdict', label: 'Interdict', desc: 'Mandatory or Prohibitory Interdict', icon: '🛑', baseFee: 5500 },
  { id: 'eviction', label: 'Eviction Application', desc: 'PIE Act Application', icon: '🏠', baseFee: 6000 },
  { id: 'rule_43', label: 'Rule 43 Application', desc: 'Interim matrimonial relief', icon: '💍', baseFee: 4500 },
  { id: 'divorce_settlement', label: 'Divorce Settlement', desc: 'Settlement Agreement Drafting', icon: '🤝', baseFee: 2500 }
];
