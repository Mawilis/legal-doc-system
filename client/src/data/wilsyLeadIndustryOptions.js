/* eslint-disable */

export const WILSY_LEAD_INDUSTRY_OPTIONS = Object.freeze([
  'Accounting',
  'Advertising & Marketing',
  'Agriculture',
  'Architecture',
  'Automotive',
  'Banking',
  'Business Services',
  'Construction',
  'Consulting',
  'Consumer Goods',
  'Education',
  'Energy',
  'Engineering',
  'Financial Services',
  'Government',
  'Healthcare',
  'Hospitality',
  'Insurance',
  'Legal Services',
  'Logistics & Supply Chain',
  'Manufacturing',
  'Media & Entertainment',
  'Mining',
  'Non-Profit',
  'Pharmaceuticals',
  'Professional Services',
  'Property & Real Estate',
  'Retail',
  'Software',
  'Telecommunications',
  'Technology',
  'Transport',
  'Travel & Tourism',
  'Wholesale',
  'Other'
]);

/**
 * @function normalizeWilsyLeadIndustryValue
 * @description Normalizes a Lead industry while preserving custom real-world industry values.
 * @collaboration Powers production CRM industry selection without forcing fake placeholders.
 */
export function normalizeWilsyLeadIndustryValue(value = '') {
  const candidate = String(value || '').replace(/\s+/g, ' ').trim();

  if (!candidate) {
    return '';
  }

  const match = WILSY_LEAD_INDUSTRY_OPTIONS.find((industry) => industry.toLowerCase() === candidate.toLowerCase());

  return match || candidate;
}
