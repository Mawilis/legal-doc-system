#!/* eslint-disable */
/*
 * WILSY OS: BRANDING CONFIGURATION - QUANTUM FORTRESS VISUAL IDENTITY
 *
 * This file centralizes all branding elements for consistent application
 * across PDFs, emails, and UI components.
 */

export const BRANDING = {
  // Company identity
  company: {
    name: 'Wilsy OS',
    fullName: 'Wilsy Operating System',
    tagline: 'The Global Legal Operating System',
    founder: 'Wilson Khanyezi',
    founded: 2024,
    jurisdiction: 'South Africa',
  },

  // Color palette
  colors: {
    primary: '#001f3f', // Deep Navy - Trust, Authority, Stability
    secondary: '#0074D9', // Bright Blue - Innovation, Intelligence
    accent: '#FF851B', // Orange - Action, Urgency, Upsell
    success: '#2ECC40', // Green - Compliance, Success
    warning: '#FF851B', // Orange - Warnings
    error: '#FF4136', // Red - Errors, Critical
    background: '#FFFFFF', // White - Clean, Professional
    text: '#111111', // Near Black - Readability
    lightGray: '#F5F5F5', // Light Gray - Sections
    mediumGray: '#DDDDDD', // Borders, Lines
    darkGray: '#666666', // Secondary Text
  },

  // Typography
  typography: {
    title: {
      font: 'Helvetica-Bold',
      size: 25,
      color: '#001f3f',
    },
    header: {
      font: 'Helvetica-Bold',
      size: 16,
      color: '#001f3f',
    },
    subheader: {
      font: 'Helvetica-Bold',
      size: 14,
      color: '#001f3f',
    },
    body: {
      font: 'Helvetica',
      size: 12,
      color: '#111111',
    },
    small: {
      font: 'Helvetica',
      size: 10,
      color: '#666666',
    },
    footer: {
      font: 'Helvetica',
      size: 8,
      color: '#999999',
    },
  },

  // Layout
  layout: {
    margin: 50,
    pageWidth: 612,
    pageHeight: 792,
    columnWidth: 250,
  },

  // Legal compliance
  compliance: {
    statements: [
      'POPIA §19 - Technical measures for data protection',
      'ECT Act §15 - Evidential weight of data messages',
      'Companies Act §24 - Record keeping requirements',
      'Cybercrimes Act §54 - Cybersecurity duty to report',
    ],
    retentionPolicy: 'companies_act_10_years',
    dataResidency: 'ZA',
  },

  // URLs
  urls: {
    website: 'https://wilsy.os',
    verification: 'https://verify.wilsy.os',
    support: 'https://support.wilsy.os',
    investor: 'https://investors.wilsy.os',
  },

  // Social proof
  social: {
    twitter: '@WilsyOS',
    linkedin: 'company/wilsy-os',
    github: 'Mawilis/legal-doc-system',
  },
};

export default BRANDING;
