/**
 * File: client/src/data/sheriffData.js
 * STATUS: EPITOME | PRODUCTION-READY | SHERIFF OPERATIONS DNA | VERSION: 1.0.0
 * -----------------------------------------------------------------------------
 * PURPOSE
 * - Canonical dataset and helper utilities for Sheriff operations used by Wilsy OS.
 * - Drives Sheriff Module (dispatch, service instructions, job routing), Document
 *   Service (service type validation), and Dashboard (ETA, SLA, analytics).
 *
 * COLLABORATION (Billion Dollar Readiness)
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - TECH LEAD: @platform
 * - SECURITY: @security (service authorization, PII handling)
 * - PRODUCT: @product (workflows, SLAs)
 * - OPERATIONS: @sre (queueing, retries, geo-routing)
 * - REVIEWERS: @frontend, @backend, @legal, @sheriff-ops
 *
 * ARCHITECTURAL VALUE
 * - SERVICE_TYPES: canonical tokens for all sheriff actions (used across UI, API, and workers).
 * - SHERIFF_OFFICES: geo-indexed offices for routing and SLA estimation.
 * - JOB_PRIORITIES & SLA: map riskLevel -> priority -> SLA for queueing and alerts.
 * - HELPERS: deterministic functions for routing, fee estimation, instruction generation,
 *   and validation used by the Sheriff UI and backend job producers.
 *
 * GOVERNANCE
 * - This module is immutable at runtime (Object.freeze). To change, create a migration
 *   script and update the changelog. All changes must be reviewed by @legal and @ops.
 *
 * USAGE
 * - Import constants and helpers in Sheriff pages, Document workflows, and background workers.
 *   Example:
 *     import { SERVICE_TYPES, getSheriffOfficeForRegion, estimateServiceFee } from '../../data/sheriffData';
 *
 * -----------------------------------------------------------------------------
 */

/* -------------------------
   SERVICE TYPES
   - Canonical tokens used across the product and backend.
   - Keep tokens short, uppercase, and stable.
   ------------------------- */
export const SERVICE_TYPES = Object.freeze({
  NORMAL_SERVICE: 'NORMAL_SERVICE',                 // Standard sheriff service
  PERSONAL_SERVICE_REQUIRED: 'PERSONAL_SERVICE_REQUIRED', // Requires personal delivery
  URGENT_SERVICE: 'URGENT_SERVICE',                 // High priority, expedited
  IMMEDIATE_SERVICE: 'IMMEDIATE_SERVICE',           // Immediate same-day action
  SECTION_4_2_SERVICE: 'SECTION_4_2_SERVICE',       // PIE Act specific instruction
  MUNICIPAL_SERVICE: 'MUNICIPAL_SERVICE',           // Service to municipality/authority
  COURT_REGISTRAR_FILING: 'COURT_REGISTRAR_FILING', // Registrar filing action
  NONE: 'NONE'                                      // No sheriff action required
});

/* -------------------------
   JOB PRIORITIES & SLA
   - Map risk levels to queue priority and SLA in minutes/hours.
   - Used by dispatcher and alerting rules.
   ------------------------- */
export const JOB_PRIORITIES = Object.freeze({
  CRITICAL: { priority: 100, slaMinutes: 60 },   // Immediate attention (1 hour)
  HIGH: { priority: 80, slaMinutes: 240 },  // High (4 hours)
  MEDIUM: { priority: 50, slaMinutes: 1440 }, // Standard (24 hours)
  LOW: { priority: 20, slaMinutes: 4320 }  // Low (72 hours)
});

/* -------------------------
   SHERIFF OFFICES
   - Representative list of sheriff offices with geo and contact metadata.
   - Used for routing, ETA, and contact display in UI.
   - In production, this should be synced with backend registry and kept authoritative.
   ------------------------- */
export const SHERIFF_OFFICES = Object.freeze([
  {
    id: 'sheriff_jhb_central',
    name: 'Johannesburg Central Sheriff Office',
    region: 'Gauteng',
    city: 'Johannesburg',
    address: 'Civic Centre, Main St, Johannesburg',
    phone: '+27-11-000-0000',
    email: 'jhb.sheriff@wilsy.example',
    geo: { lat: -26.2041, lon: 28.0473 },
    capabilities: [SERVICE_TYPES.NORMAL_SERVICE, SERVICE_TYPES.PERSONAL_SERVICE_REQUIRED, SERVICE_TYPES.URGENT_SERVICE],
    notes: 'Covers central Johannesburg metro and surrounding suburbs.'
  },
  {
    id: 'sheriff_cpt_central',
    name: 'Cape Town Central Sheriff Office',
    region: 'Western Cape',
    city: 'Cape Town',
    address: 'Civic Centre, Cape Town',
    phone: '+27-21-000-0000',
    email: 'cpt.sheriff@wilsy.example',
    geo: { lat: -33.9249, lon: 18.4241 },
    capabilities: [SERVICE_TYPES.NORMAL_SERVICE, SERVICE_TYPES.MUNICIPAL_SERVICE, SERVICE_TYPES.SECTION_4_2_SERVICE],
    notes: 'Handles municipal service and PIE-related coordination with local authorities.'
  },
  {
    id: 'sheriff_dbn_central',
    name: 'Durban Sheriff Office',
    region: 'KwaZulu-Natal',
    city: 'Durban',
    address: 'Durban Law Courts, Durban',
    phone: '+27-31-000-0000',
    email: 'dbn.sheriff@wilsy.example',
    geo: { lat: -29.8587, lon: 31.0218 },
    capabilities: [SERVICE_TYPES.NORMAL_SERVICE, SERVICE_TYPES.PERSONAL_SERVICE_REQUIRED],
    notes: 'Primary Durban office; supports urgent same-day requests when available.'
  },
  {
    id: 'sheriff_pta_central',
    name: 'Pretoria Sheriff Office',
    region: 'Gauteng',
    city: 'Pretoria',
    address: 'Pretoria Magistrate Court, Pretoria',
    phone: '+27-12-000-0000',
    email: 'pta.sheriff@wilsy.example',
    geo: { lat: -25.7479, lon: 28.2293 },
    capabilities: [SERVICE_TYPES.NORMAL_SERVICE, SERVICE_TYPES.COURT_REGISTRAR_FILING],
    notes: 'Registrar filing and standard service coverage for Pretoria.'
  }
]);

/* -------------------------
   DEFAULT FEES
   - Base fee table for service types; used by estimateServiceFee.
   - In production, fees may be tenant-configurable and subject to local tariffs.
   ------------------------- */
export const SERVICE_FEES = Object.freeze({
  [SERVICE_TYPES.NORMAL_SERVICE]: { base: 350, perKm: 8, description: 'Standard service fee' },
  [SERVICE_TYPES.PERSONAL_SERVICE_REQUIRED]: { base: 500, perKm: 12, description: 'Personal delivery required' },
  [SERVICE_TYPES.URGENT_SERVICE]: { base: 1200, perKm: 20, description: 'Expedited urgent service' },
  [SERVICE_TYPES.IMMEDIATE_SERVICE]: { base: 2000, perKm: 25, description: 'Immediate same-day service' },
  [SERVICE_TYPES.SECTION_4_2_SERVICE]: { base: 900, perKm: 15, description: 'PIE Act specific service (municipal coordination)' },
  [SERVICE_TYPES.MUNICIPAL_SERVICE]: { base: 450, perKm: 10, description: 'Service to municipal offices' },
  [SERVICE_TYPES.COURT_REGISTRAR_FILING]: { base: 250, perKm: 5, description: 'Registrar filing fee' },
  [SERVICE_TYPES.NONE]: { base: 0, perKm: 0, description: 'No sheriff action required' }
});

/* -------------------------
   HELPERS
   - Deterministic, pure functions for routing, validation, and fee estimation.
   ------------------------- */

/**
 * getSheriffOfficeForRegion
 * - Returns the best-matching sheriff office for a given region or city.
 * - Simple deterministic selection: first office matching city, then region, then nearest by geo.
 */
export function getSheriffOfficeForRegion({ region = null, city = null, geo = null } = {}) {
  // Exact city match
  if (city) {
    const byCity = SHERIFF_OFFICES.find(o => o.city && o.city.toLowerCase() === String(city).toLowerCase());
    if (byCity) return byCity;
  }

  // Region match
  if (region) {
    const byRegion = SHERIFF_OFFICES.find(o => o.region && o.region.toLowerCase() === String(region).toLowerCase());
    if (byRegion) return byRegion;
  }

  // Geo fallback: nearest by haversine distance (if geo provided)
  if (geo && geo.lat != null && geo.lon != null) {
    let best = null;
    let bestDist = Infinity;
    for (const office of SHERIFF_OFFICES) {
      if (!office.geo) continue;
      const d = _haversineDistance(geo.lat, geo.lon, office.geo.lat, office.geo.lon);
      if (d < bestDist) { bestDist = d; best = office; }
    }
    if (best) return best;
  }

  // Default to first office
  return SHERIFF_OFFICES[0] || null;
}

/**
 * estimateServiceFee
 * - Estimates a service fee given serviceType and approximate distance (km).
 * - Returns { total, breakdown }.
 */
export function estimateServiceFee(serviceType, distanceKm = 10) {
  const fee = SERVICE_FEES[serviceType] || SERVICE_FEES[SERVICE_TYPES.NORMAL_SERVICE];
  const travel = Math.max(0, Number(distanceKm) || 0);
  const total = Math.round(fee.base + (fee.perKm * travel));
  return {
    total,
    breakdown: {
      base: fee.base,
      perKm: fee.perKm,
      distanceKm: travel,
      description: fee.description
    }
  };
}

/**
 * validateServiceTypeForOffice
 * - Ensures the selected office supports the requested service type.
 * - Returns { ok: boolean, supported: boolean, office, message }.
 */
export function validateServiceTypeForOffice(officeId, serviceType) {
  const office = SHERIFF_OFFICES.find(o => o.id === officeId) || null;
  if (!office) return { ok: false, supported: false, office: null, message: 'Unknown sheriff office' };
  const supported = Array.isArray(office.capabilities) && office.capabilities.includes(serviceType);
  return {
    ok: supported,
    supported,
    office,
    message: supported ? 'Supported' : `Service type ${serviceType} not supported by ${office.name}`
  };
}

/**
 * getServiceInstructions
 * - Returns human-readable instructions for the sheriff based on serviceType and litigation type metadata.
 * - This is used to populate job payloads and printable instructions.
 */
export function getServiceInstructions({ serviceType, litigationType = null, address = null, notes = '' } = {}) {
  const lines = [];
  lines.push(`Service Type: ${serviceType}`);
  if (litigationType) lines.push(`Case Type: ${litigationType.label || litigationType}`);
  if (address) lines.push(`Service Address: ${address}`);
  if (serviceType === SERVICE_TYPES.SECTION_4_2_SERVICE) {
    lines.push('PIE Act: Coordinate with local municipality and confirm Section 4(2) notice delivery.');
    lines.push('Ensure municipal service and proof of delivery to municipality is captured.');
  }
  if (serviceType === SERVICE_TYPES.PERSONAL_SERVICE_REQUIRED) {
    lines.push('Personal service required: attempt personal delivery at least twice; if unsuccessful, follow up with alternative service per court rules.');
  }
  if (serviceType === SERVICE_TYPES.URGENT_SERVICE || serviceType === SERVICE_TYPES.IMMEDIATE_SERVICE) {
    lines.push('Urgent: prioritize this job; same-day or immediate execution required where possible.');
  }
  if (notes) lines.push(`Notes: ${notes}`);
  lines.push('Capture photographic evidence, GPS coordinates, and signed acknowledgment where applicable.');
  lines.push('Upload proof of service documents to the case record immediately after completion.');
  return lines.join('\n');
}

/* -------------------------
   INTERNAL UTILITIES
   - Small helpers kept private to this module.
   ------------------------- */

/**
 * _haversineDistance
 * - Returns distance in kilometers between two lat/lon points.
 */
function _haversineDistance(lat1, lon1, lat2, lon2) {
  const toRad = (v) => (v * Math.PI) / 180;
  const R = 6371; // Earth radius km
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

/* -------------------------
   EXPORTS
   - Freeze the exported object to prevent runtime mutation.
   ------------------------- */
const _exports = {
  SERVICE_TYPES,
  JOB_PRIORITIES,
  SHERIFF_OFFICES,
  SERVICE_FEES,
  getSheriffOfficeForRegion,
  estimateServiceFee,
  validateServiceTypeForOffice,
  getServiceInstructions
};

export default Object.freeze(_exports);
