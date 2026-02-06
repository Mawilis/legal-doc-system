/**
 * File: client/src/data/saCourts.js
 * STATUS: EPITOME | JURISDICTION ENGINE | IMMUTABLE | PRODUCTION READY
 * -----------------------------------------------------------------------------
 * PURPOSE
 * - Authoritative registry of South African courts.
 * - Uses NAMED EXPORTS to allow destructured imports.
 * -----------------------------------------------------------------------------
 */

const _SA_COURTS = [
  // APEX COURTS
  { id: 'cc', name: 'Constitutional Court', type: 'Apex', province: 'Gauteng', city: 'Braamfontein', geo: { lat: -26.1936, lon: 28.0344 } },
  { id: 'sca', name: 'Supreme Court of Appeal', type: 'Apex', province: 'Free State', city: 'Bloemfontein', geo: { lat: -29.1233, lon: 26.2144 } },

  // LABOUR COURTS
  { id: 'lc-jhb', name: 'Labour Court Johannesburg', type: 'Labour', province: 'Gauteng', city: 'Johannesburg', geo: { lat: -26.2041, lon: 28.0473 } },
  { id: 'lc-cpt', name: 'Labour Court Cape Town', type: 'Labour', province: 'Western Cape', city: 'Cape Town', geo: { lat: -33.9249, lon: 18.4241 } },
  { id: 'lc-dbn', name: 'Labour Court Durban', type: 'Labour', province: 'KwaZulu-Natal', city: 'Durban', geo: { lat: -29.8587, lon: 31.0218 } },
  { id: 'lc-pe', name: 'Labour Court Gqeberha', type: 'Labour', province: 'Eastern Cape', city: 'Gqeberha', geo: { lat: -33.9610, lon: 25.6152 } },

  // GAUTENG HIGH COURTS
  { id: 'hc-jhb', name: 'Gauteng Division High Court (Johannesburg)', type: 'High Court', province: 'Gauteng', city: 'Johannesburg', geo: { lat: -26.2041, lon: 28.0473 } },
  { id: 'hc-pta', name: 'Gauteng Division High Court (Pretoria)', type: 'High Court', province: 'Gauteng', city: 'Pretoria', geo: { lat: -25.7479, lon: 28.2293 } },

  // WESTERN CAPE
  { id: 'hc-cpt', name: 'Western Cape Division High Court (Cape Town)', type: 'High Court', province: 'Western Cape', city: 'Cape Town', geo: { lat: -33.9249, lon: 18.4241 } },

  // KZN
  { id: 'hc-dbn', name: 'KwaZulu-Natal Local Division High Court (Durban)', type: 'High Court', province: 'KwaZulu-Natal', city: 'Durban', geo: { lat: -29.8587, lon: 31.0218 } },
  { id: 'hc-pmb', name: 'KwaZulu-Natal Division High Court (Pietermaritzburg)', type: 'High Court', province: 'KwaZulu-Natal', city: 'Pietermaritzburg', geo: { lat: -29.6168, lon: 30.3928 } },

  // OTHER PROVINCES
  { id: 'hc-bloem', name: 'Free State Division High Court (Bloemfontein)', type: 'High Court', province: 'Free State', city: 'Bloemfontein', geo: { lat: -29.1233, lon: 26.2144 } },
  { id: 'hc-kim', name: 'Northern Cape Division High Court (Kimberley)', type: 'High Court', province: 'Northern Cape', city: 'Kimberley', geo: { lat: -28.7283, lon: 24.7495 } },
  { id: 'hc-nw', name: 'North West Division High Court (Mahikeng)', type: 'High Court', province: 'North West', city: 'Mahikeng', geo: { lat: -25.8567, lon: 25.6392 } },
  { id: 'hc-pol', name: 'Limpopo Division High Court (Polokwane)', type: 'High Court', province: 'Limpopo', city: 'Polokwane', geo: { lat: -23.9045, lon: 29.4689 } },
  { id: 'hc-mbom', name: 'Mpumalanga Division High Court (Mbombela)', type: 'High Court', province: 'Mpumalanga', city: 'Mbombela', geo: { lat: -25.4637, lon: 30.9860 } },
  { id: 'hc-mid', name: 'Mpumalanga Local Division High Court (Middelburg)', type: 'High Court', province: 'Mpumalanga', city: 'Middelburg', geo: { lat: -25.7833, lon: 29.4667 } },
  { id: 'hc-ec-bhisho', name: 'Eastern Cape Division High Court (Bhisho)', type: 'High Court', province: 'Eastern Cape', city: 'Bhisho', geo: { lat: -32.8496, lon: 27.4455 } },
  { id: 'hc-ec-el', name: 'Eastern Cape Local Division High Court (East London)', type: 'High Court', province: 'Eastern Cape', city: 'East London', geo: { lat: -33.0153, lon: 27.9116 } },
  { id: 'hc-ec-pe', name: 'Eastern Cape Local Division High Court (Gqeberha)', type: 'High Court', province: 'Eastern Cape', city: 'Gqeberha', geo: { lat: -33.9610, lon: 25.6152 } },
  { id: 'hc-ec-thatha', name: 'Eastern Cape Local Division High Court (Mthatha)', type: 'High Court', province: 'Eastern Cape', city: 'Mthatha', geo: { lat: -31.5880, lon: 28.7846 } },

  // MAGISTRATES COURTS
  { id: 'mag-rand', name: 'Randburg Magistrate Court', type: 'Magistrate', province: 'Gauteng', city: 'Randburg', geo: { lat: -26.0945, lon: 27.9914 } },
  { id: 'mag-jhb', name: 'Johannesburg Magistrate Court', type: 'Magistrate', province: 'Gauteng', city: 'Johannesburg', geo: { lat: -26.2041, lon: 28.0473 } },
  { id: 'mag-sand', name: 'Sandton Magistrate Court', type: 'Magistrate', province: 'Gauteng', city: 'Sandton', geo: { lat: -26.1075, lon: 28.0567 } },
  { id: 'mag-pta', name: 'Pretoria Magistrate Court', type: 'Magistrate', province: 'Gauteng', city: 'Pretoria', geo: { lat: -25.7479, lon: 28.2293 } },
  { id: 'mag-cpt', name: 'Cape Town Magistrate Court', type: 'Magistrate', province: 'Western Cape', city: 'Cape Town', geo: { lat: -33.9249, lon: 18.4241 } },
  { id: 'mag-wyn', name: 'Wynberg Magistrate Court', type: 'Magistrate', province: 'Western Cape', city: 'Wynberg', geo: { lat: -34.0008, lon: 18.4680 } },
  { id: 'mag-dbn', name: 'Durban Magistrate Court', type: 'Magistrate', province: 'KwaZulu-Natal', city: 'Durban', geo: { lat: -29.8587, lon: 31.0218 } },
  { id: 'mag-sov', name: 'Soweto Magistrate Court (Protea)', type: 'Magistrate', province: 'Gauteng', city: 'Soweto', geo: { lat: -26.2670, lon: 27.8580 } },
  { id: 'mag-empt', name: 'Kempton Park Magistrate Court', type: 'Magistrate', province: 'Gauteng', city: 'Kempton Park', geo: { lat: -26.1450, lon: 28.2328 } },
  { id: 'mag-germ', name: 'Germiston Magistrate Court', type: 'Magistrate', province: 'Gauteng', city: 'Germiston', geo: { lat: -26.2345, lon: 28.1673 } },
  { id: 'mag-ben', name: 'Benoni Magistrate Court', type: 'Magistrate', province: 'Gauteng', city: 'Benoni', geo: { lat: -26.1458, lon: 28.3228 } },
  { id: 'mag-ver', name: 'Vereeniging Magistrate Court', type: 'Magistrate', province: 'Gauteng', city: 'Vereeniging', geo: { lat: -26.6735, lon: 27.9253 } },
  { id: 'mag-stell', name: 'Stellenbosch Magistrate Court', type: 'Magistrate', province: 'Western Cape', city: 'Stellenbosch', geo: { lat: -33.9340, lon: 18.8603 } }
];

// 1. EXPORT THE DATA (NAMED EXPORT)
export const SA_COURTS = Object.freeze(_SA_COURTS.map(c => Object.freeze({ ...c })));

/* -------------------------
   Intelligence Helpers
   ------------------------- */

// 2. EXPORT THE FUNCTIONS (NAMED EXPORTS)

export const getCourtById = (id) => {
  if (!id) return null;
  return SA_COURTS.find(c => String(c.id).toLowerCase() === String(id).toLowerCase()) || null;
};

export const getCourtsByProvince = (province) => {
  if (!province) return SA_COURTS.slice();
  const p = String(province).toLowerCase();
  return SA_COURTS.filter(c => String(c.province || '').toLowerCase() === p);
};

export const getCourtsByType = (type) => {
  if (!type) return [];
  const t = String(type).toLowerCase();
  return SA_COURTS.filter(c => String(c.type || '').toLowerCase() === t);
};

export const getCourtsByCity = (city) => {
  if (!city) return [];
  const q = String(city).toLowerCase();
  return SA_COURTS.filter(c => String(c.city || '').toLowerCase() === q);
};

export const listProvinces = () => {
  const set = new Set(SA_COURTS.map(c => c.province).filter(Boolean));
  return Array.from(set).sort();
};

export const validateCourtId = (id) => {
  const court = getCourtById(id);
  if (!court) return { ok: false, court: null, message: `Unknown court id: ${id}` };
  return { ok: true, court, message: null };
};

// Internal Haversine (Private)
function _haversineDistance(lat1, lon1, lat2, lon2) {
  const toRad = v => (v * Math.PI) / 180;
  const R = 6371; // Earth radius in km
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

export const getNearestCourt = ({ lat, lon, type = null, province = null } = {}) => {
  if (lat == null || lon == null) return null;
  const candidates = SA_COURTS.filter(c => {
    if (type && String(c.type).toLowerCase() !== String(type).toLowerCase()) return false;
    if (province && String(c.province).toLowerCase() !== String(province).toLowerCase()) return false;
    return !!c;
  });
  if (candidates.length === 0) return null;

  let best = null;
  let bestDist = Infinity;
  for (const c of candidates) {
    if (!c.geo || c.geo.lat == null || c.geo.lon == null) continue;
    const d = _haversineDistance(lat, lon, c.geo.lat, c.geo.lon);
    if (d < bestDist) { bestDist = d; best = c; }
  }
  return best || candidates[0] || null;
};

// 3. EXPORT DEFAULT OBJECT (Compat)
export default {
  SA_COURTS,
  getCourtById,
  getCourtsByProvince,
  getCourtsByType,
  getCourtsByCity,
  listProvinces,
  validateCourtId,
  getNearestCourt
};
