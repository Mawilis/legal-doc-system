/* eslint-disable */

export const WILSY_LEAD_TITLE_OPTIONS = Object.freeze([
  'Founder',
  'Co-Founder',
  'Owner',
  'Partner',
  'Trustee',
  'Chairperson',
  'Board Member',
  'Chief Executive Officer',
  'Chief Operating Officer',
  'Chief Financial Officer',
  'Chief Technology Officer',
  'Chief Information Officer',
  'Chief Revenue Officer',
  'Chief Marketing Officer',
  'Chief Sales Officer',
  'Chief Legal Officer',
  'Chief Compliance Officer',
  'Chief Procurement Officer',
  'Chief Product Officer',
  'Chief People Officer',
  'Managing Director',
  'Executive Director',
  'Non-Executive Director',
  'General Manager',
  'Country Manager',
  'Regional Manager',
  'Branch Manager',
  'Head of Sales',
  'Sales Director',
  'Sales Manager',
  'Business Development Director',
  'Business Development Manager',
  'Account Executive',
  'Key Account Manager',
  'Customer Success Director',
  'Customer Success Manager',
  'Operations Director',
  'Operations Manager',
  'Finance Director',
  'Financial Manager',
  'Procurement Director',
  'Procurement Manager',
  'Supply Chain Manager',
  'Legal Counsel',
  'Compliance Manager',
  'Risk Manager',
  'IT Director',
  'IT Manager',
  'Engineering Manager',
  'Product Manager',
  'Marketing Director',
  'Marketing Manager',
  'HR Director',
  'HR Manager',
  'Office Manager',
  'Project Director',
  'Project Manager',
  'Programme Manager',
  'Administrator',
  'Decision Maker'
]);

/**
 * @function normalizeWilsyLeadTitleValue
 * @description Normalizes a Lead title while preserving custom real-world titles.
 * @collaboration Powers low-friction Lead editing without blocking custom decision-maker roles.
 */
export function normalizeWilsyLeadTitleValue(value = '') {
  const candidate = String(value || '').replace(/\s+/g, ' ').trim();

  if (!candidate) {
    return '';
  }

  const match = WILSY_LEAD_TITLE_OPTIONS.find((title) => title.toLowerCase() === candidate.toLowerCase());

  return match || candidate;
}
