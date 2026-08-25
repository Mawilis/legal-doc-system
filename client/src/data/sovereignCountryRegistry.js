/* eslint-disable */
/**
 * =============================================================================
 * Wilsy OS — Sovereign Country Registry
 * =============================================================================
 * File:           client/src/data/sovereignCountryRegistry.js
 * Version:        v1.0.0-INSTITUTIONAL
 * Authority:      Wilsy OS Core Governance
 * Epitome:        ISO-aligned country options for HR, billing jurisdictions,
 *                 VAT/GST posture, and tenant onboarding. South Africa first.
 * Classification: Production Artifact
 * =============================================================================
 */

export const SOVEREIGN_COUNTRIES = Object.freeze([
    {
        code: 'ZA',
        alpha2: 'ZA',
        alpha3: 'ZAF',
        name: 'South Africa',
        label: 'South Africa (ZA)',
        currency: 'ZAR',
        taxRegime: 'VAT',
        defaultTaxRate: 15,
        region: 'AF'
    },
    {
        code: 'US',
        alpha2: 'US',
        alpha3: 'USA',
        name: 'United States',
        label: 'United States (US)',
        currency: 'USD',
        taxRegime: 'SALES_TAX',
        defaultTaxRate: null,
        region: 'GLOBAL'
    },
    {
        code: 'GB',
        alpha2: 'GB',
        alpha3: 'GBR',
        name: 'United Kingdom',
        label: 'United Kingdom (GB)',
        currency: 'GBP',
        taxRegime: 'VAT',
        defaultTaxRate: 20,
        region: 'GLOBAL'
    },
    {
        code: 'EU',
        alpha2: 'EU',
        alpha3: 'EUU',
        name: 'European Union (generic)',
        label: 'European Union (generic) (EU)',
        currency: 'EUR',
        taxRegime: 'VAT',
        defaultTaxRate: null,
        region: 'GLOBAL'
    },
    {
        code: 'DE',
        alpha2: 'DE',
        alpha3: 'DEU',
        name: 'Germany',
        label: 'Germany (DE)',
        currency: 'EUR',
        taxRegime: 'VAT',
        defaultTaxRate: 19,
        region: 'GLOBAL'
    },
    {
        code: 'FR',
        alpha2: 'FR',
        alpha3: 'FRA',
        name: 'France',
        label: 'France (FR)',
        currency: 'EUR',
        taxRegime: 'VAT',
        defaultTaxRate: 20,
        region: 'GLOBAL'
    },
    {
        code: 'NL',
        alpha2: 'NL',
        alpha3: 'NLD',
        name: 'Netherlands',
        label: 'Netherlands (NL)',
        currency: 'EUR',
        taxRegime: 'VAT',
        defaultTaxRate: 21,
        region: 'GLOBAL'
    },
    {
        code: 'IE',
        alpha2: 'IE',
        alpha3: 'IRL',
        name: 'Ireland',
        label: 'Ireland (IE)',
        currency: 'EUR',
        taxRegime: 'VAT',
        defaultTaxRate: 23,
        region: 'GLOBAL'
    },
    {
        code: 'BE',
        alpha2: 'BE',
        alpha3: 'BEL',
        name: 'Belgium',
        label: 'Belgium (BE)',
        currency: 'EUR',
        taxRegime: 'VAT',
        defaultTaxRate: 21,
        region: 'GLOBAL'
    },
    {
        code: 'ES',
        alpha2: 'ES',
        alpha3: 'ESP',
        name: 'Spain',
        label: 'Spain (ES)',
        currency: 'EUR',
        taxRegime: 'VAT',
        defaultTaxRate: 21,
        region: 'GLOBAL'
    },
    {
        code: 'IT',
        alpha2: 'IT',
        alpha3: 'ITA',
        name: 'Italy',
        label: 'Italy (IT)',
        currency: 'EUR',
        taxRegime: 'VAT',
        defaultTaxRate: 22,
        region: 'GLOBAL'
    },
    {
        code: 'PT',
        alpha2: 'PT',
        alpha3: 'PRT',
        name: 'Portugal',
        label: 'Portugal (PT)',
        currency: 'EUR',
        taxRegime: 'VAT',
        defaultTaxRate: 23,
        region: 'GLOBAL'
    },
    {
        code: 'AT',
        alpha2: 'AT',
        alpha3: 'AUT',
        name: 'Austria',
        label: 'Austria (AT)',
        currency: 'EUR',
        taxRegime: 'VAT',
        defaultTaxRate: 20,
        region: 'GLOBAL'
    },
    {
        code: 'CH',
        alpha2: 'CH',
        alpha3: 'CHE',
        name: 'Switzerland',
        label: 'Switzerland (CH)',
        currency: 'CHF',
        taxRegime: 'VAT',
        defaultTaxRate: 8.1,
        region: 'GLOBAL'
    },
    {
        code: 'AE',
        alpha2: 'AE',
        alpha3: 'ARE',
        name: 'United Arab Emirates',
        label: 'United Arab Emirates (AE)',
        currency: 'AED',
        taxRegime: 'VAT',
        defaultTaxRate: 5,
        region: 'GLOBAL'
    },
    {
        code: 'SA',
        alpha2: 'SA',
        alpha3: 'SAU',
        name: 'Saudi Arabia',
        label: 'Saudi Arabia (SA)',
        currency: 'SAR',
        taxRegime: 'VAT',
        defaultTaxRate: 15,
        region: 'GLOBAL'
    },
    {
        code: 'NG',
        alpha2: 'NG',
        alpha3: 'NGA',
        name: 'Nigeria',
        label: 'Nigeria (NG)',
        currency: 'NGN',
        taxRegime: 'VAT',
        defaultTaxRate: 7.5,
        region: 'AF'
    },
    {
        code: 'KE',
        alpha2: 'KE',
        alpha3: 'KEN',
        name: 'Kenya',
        label: 'Kenya (KE)',
        currency: 'KES',
        taxRegime: 'VAT',
        defaultTaxRate: 16,
        region: 'AF'
    },
    {
        code: 'GH',
        alpha2: 'GH',
        alpha3: 'GHA',
        name: 'Ghana',
        label: 'Ghana (GH)',
        currency: 'GHS',
        taxRegime: 'VAT',
        defaultTaxRate: 15,
        region: 'AF'
    },
    {
        code: 'EG',
        alpha2: 'EG',
        alpha3: 'EGY',
        name: 'Egypt',
        label: 'Egypt (EG)',
        currency: 'EGP',
        taxRegime: 'VAT',
        defaultTaxRate: 14,
        region: 'AF'
    },
    {
        code: 'BW',
        alpha2: 'BW',
        alpha3: 'BWA',
        name: 'Botswana',
        label: 'Botswana (BW)',
        currency: 'BWP',
        taxRegime: 'VAT',
        defaultTaxRate: 14,
        region: 'AF'
    },
    {
        code: 'NA',
        alpha2: 'NA',
        alpha3: 'NAM',
        name: 'Namibia',
        label: 'Namibia (NA)',
        currency: 'NAD',
        taxRegime: 'VAT',
        defaultTaxRate: 15,
        region: 'AF'
    },
    {
        code: 'ZW',
        alpha2: 'ZW',
        alpha3: 'ZWE',
        name: 'Zimbabwe',
        label: 'Zimbabwe (ZW)',
        currency: 'ZWL',
        taxRegime: 'VAT',
        defaultTaxRate: 15,
        region: 'AF'
    },
    {
        code: 'MZ',
        alpha2: 'MZ',
        alpha3: 'MOZ',
        name: 'Mozambique',
        label: 'Mozambique (MZ)',
        currency: 'MZN',
        taxRegime: 'VAT',
        defaultTaxRate: 16,
        region: 'AF'
    },
    {
        code: 'ZM',
        alpha2: 'ZM',
        alpha3: 'ZMB',
        name: 'Zambia',
        label: 'Zambia (ZM)',
        currency: 'ZMW',
        taxRegime: 'VAT',
        defaultTaxRate: 16,
        region: 'AF'
    },
    {
        code: 'MW',
        alpha2: 'MW',
        alpha3: 'MWI',
        name: 'Malawi',
        label: 'Malawi (MW)',
        currency: 'MWK',
        taxRegime: 'VAT',
        defaultTaxRate: 16.5,
        region: 'AF'
    },
    {
        code: 'TZ',
        alpha2: 'TZ',
        alpha3: 'TZA',
        name: 'Tanzania',
        label: 'Tanzania (TZ)',
        currency: 'TZS',
        taxRegime: 'VAT',
        defaultTaxRate: 18,
        region: 'AF'
    },
    {
        code: 'UG',
        alpha2: 'UG',
        alpha3: 'UGA',
        name: 'Uganda',
        label: 'Uganda (UG)',
        currency: 'UGX',
        taxRegime: 'VAT',
        defaultTaxRate: 18,
        region: 'AF'
    },
    {
        code: 'RW',
        alpha2: 'RW',
        alpha3: 'RWA',
        name: 'Rwanda',
        label: 'Rwanda (RW)',
        currency: 'RWF',
        taxRegime: 'VAT',
        defaultTaxRate: 18,
        region: 'AF'
    },
    {
        code: 'AU',
        alpha2: 'AU',
        alpha3: 'AUS',
        name: 'Australia',
        label: 'Australia (AU)',
        currency: 'AUD',
        taxRegime: 'GST',
        defaultTaxRate: 10,
        region: 'GLOBAL'
    },
    {
        code: 'NZ',
        alpha2: 'NZ',
        alpha3: 'NZL',
        name: 'New Zealand',
        label: 'New Zealand (NZ)',
        currency: 'NZD',
        taxRegime: 'GST',
        defaultTaxRate: 15,
        region: 'GLOBAL'
    },
    {
        code: 'CA',
        alpha2: 'CA',
        alpha3: 'CAN',
        name: 'Canada',
        label: 'Canada (CA)',
        currency: 'CAD',
        taxRegime: 'GST',
        defaultTaxRate: 5,
        region: 'GLOBAL'
    },
    {
        code: 'IN',
        alpha2: 'IN',
        alpha3: 'IND',
        name: 'India',
        label: 'India (IN)',
        currency: 'INR',
        taxRegime: 'GST',
        defaultTaxRate: 18,
        region: 'GLOBAL'
    },
    {
        code: 'SG',
        alpha2: 'SG',
        alpha3: 'SGP',
        name: 'Singapore',
        label: 'Singapore (SG)',
        currency: 'SGD',
        taxRegime: 'GST',
        defaultTaxRate: 9,
        region: 'GLOBAL'
    },
    {
        code: 'HK',
        alpha2: 'HK',
        alpha3: 'HKG',
        name: 'Hong Kong',
        label: 'Hong Kong (HK)',
        currency: 'HKD',
        taxRegime: 'NONE',
        defaultTaxRate: 0,
        region: 'GLOBAL'
    },
    {
        code: 'JP',
        alpha2: 'JP',
        alpha3: 'JPN',
        name: 'Japan',
        label: 'Japan (JP)',
        currency: 'JPY',
        taxRegime: 'CT',
        defaultTaxRate: 10,
        region: 'GLOBAL'
    },
    {
        code: 'CN',
        alpha2: 'CN',
        alpha3: 'CHN',
        name: 'China',
        label: 'China (CN)',
        currency: 'CNY',
        taxRegime: 'VAT',
        defaultTaxRate: 13,
        region: 'GLOBAL'
    },
    {
        code: 'BR',
        alpha2: 'BR',
        alpha3: 'BRA',
        name: 'Brazil',
        label: 'Brazil (BR)',
        currency: 'BRL',
        taxRegime: 'ICMS',
        defaultTaxRate: null,
        region: 'GLOBAL'
    },
    {
        code: 'MX',
        alpha2: 'MX',
        alpha3: 'MEX',
        name: 'Mexico',
        label: 'Mexico (MX)',
        currency: 'MXN',
        taxRegime: 'VAT',
        defaultTaxRate: 16,
        region: 'GLOBAL'
    },
    {
        code: 'AR',
        alpha2: 'AR',
        alpha3: 'ARG',
        name: 'Argentina',
        label: 'Argentina (AR)',
        currency: 'ARS',
        taxRegime: 'VAT',
        defaultTaxRate: 21,
        region: 'GLOBAL'
    },
    {
        code: 'CL',
        alpha2: 'CL',
        alpha3: 'CHL',
        name: 'Chile',
        label: 'Chile (CL)',
        currency: 'CLP',
        taxRegime: 'VAT',
        defaultTaxRate: 19,
        region: 'GLOBAL'
    },
    {
        code: 'CO',
        alpha2: 'CO',
        alpha3: 'COL',
        name: 'Colombia',
        label: 'Colombia (CO)',
        currency: 'COP',
        taxRegime: 'VAT',
        defaultTaxRate: 19,
        region: 'GLOBAL'
    },
    {
        code: 'IL',
        alpha2: 'IL',
        alpha3: 'ISR',
        name: 'Israel',
        label: 'Israel (IL)',
        currency: 'ILS',
        taxRegime: 'VAT',
        defaultTaxRate: 17,
        region: 'GLOBAL'
    },
    {
        code: 'TR',
        alpha2: 'TR',
        alpha3: 'TUR',
        name: 'Türkiye',
        label: 'Türkiye (TR)',
        currency: 'TRY',
        taxRegime: 'VAT',
        defaultTaxRate: 20,
        region: 'GLOBAL'
    },
    {
        code: 'SE',
        alpha2: 'SE',
        alpha3: 'SWE',
        name: 'Sweden',
        label: 'Sweden (SE)',
        currency: 'SEK',
        taxRegime: 'VAT',
        defaultTaxRate: 25,
        region: 'GLOBAL'
    },
    {
        code: 'NO',
        alpha2: 'NO',
        alpha3: 'NOR',
        name: 'Norway',
        label: 'Norway (NO)',
        currency: 'NOK',
        taxRegime: 'VAT',
        defaultTaxRate: 25,
        region: 'GLOBAL'
    },
    {
        code: 'DK',
        alpha2: 'DK',
        alpha3: 'DNK',
        name: 'Denmark',
        label: 'Denmark (DK)',
        currency: 'DKK',
        taxRegime: 'VAT',
        defaultTaxRate: 25,
        region: 'GLOBAL'
    },
    {
        code: 'FI',
        alpha2: 'FI',
        alpha3: 'FIN',
        name: 'Finland',
        label: 'Finland (FI)',
        currency: 'EUR',
        taxRegime: 'VAT',
        defaultTaxRate: 24,
        region: 'GLOBAL'
    },
    {
        code: 'PL',
        alpha2: 'PL',
        alpha3: 'POL',
        name: 'Poland',
        label: 'Poland (PL)',
        currency: 'PLN',
        taxRegime: 'VAT',
        defaultTaxRate: 23,
        region: 'GLOBAL'
    },
    {
        code: 'CZ',
        alpha2: 'CZ',
        alpha3: 'CZE',
        name: 'Czechia',
        label: 'Czechia (CZ)',
        currency: 'CZK',
        taxRegime: 'VAT',
        defaultTaxRate: 21,
        region: 'GLOBAL'
    },
    {
        code: 'RO',
        alpha2: 'RO',
        alpha3: 'ROU',
        name: 'Romania',
        label: 'Romania (RO)',
        currency: 'RON',
        taxRegime: 'VAT',
        defaultTaxRate: 19,
        region: 'GLOBAL'
    },
    {
        code: 'HU',
        alpha2: 'HU',
        alpha3: 'HUN',
        name: 'Hungary',
        label: 'Hungary (HU)',
        currency: 'HUF',
        taxRegime: 'VAT',
        defaultTaxRate: 27,
        region: 'GLOBAL'
    },
    {
        code: 'GR',
        alpha2: 'GR',
        alpha3: 'GRC',
        name: 'Greece',
        label: 'Greece (GR)',
        currency: 'EUR',
        taxRegime: 'VAT',
        defaultTaxRate: 24,
        region: 'GLOBAL'
    },
    {
        code: 'CY',
        alpha2: 'CY',
        alpha3: 'CYP',
        name: 'Cyprus',
        label: 'Cyprus (CY)',
        currency: 'EUR',
        taxRegime: 'VAT',
        defaultTaxRate: 19,
        region: 'GLOBAL'
    },
    {
        code: 'MT',
        alpha2: 'MT',
        alpha3: 'MLT',
        name: 'Malta',
        label: 'Malta (MT)',
        currency: 'EUR',
        taxRegime: 'VAT',
        defaultTaxRate: 18,
        region: 'GLOBAL'
    },
    {
        code: 'LU',
        alpha2: 'LU',
        alpha3: 'LUX',
        name: 'Luxembourg',
        label: 'Luxembourg (LU)',
        currency: 'EUR',
        taxRegime: 'VAT',
        defaultTaxRate: 17,
        region: 'GLOBAL'
    },
    {
        code: 'MU',
        alpha2: 'MU',
        alpha3: 'MUS',
        name: 'Mauritius',
        label: 'Mauritius (MU)',
        currency: 'MUR',
        taxRegime: 'VAT',
        defaultTaxRate: 15,
        region: 'AF'
    },
    {
        code: 'SC',
        alpha2: 'SC',
        alpha3: 'SYC',
        name: 'Seychelles',
        label: 'Seychelles (SC)',
        currency: 'SCR',
        taxRegime: 'VAT',
        defaultTaxRate: 15,
        region: 'AF'
    }
]);

/**
 * @function normalizeCountryQuery
 * @description Normalises user or form input for country matching.
 * @param {'*'} value - Raw query.
 * @returns {'string'} Normalised query.
 * @collaboration HR country fields, billing jurisdiction selects.
 */
function normalizeCountryQuery(value) {
    return String(value ?? '')
        .trim()
        .toLowerCase()
        .replace(/\s+/g, ' ');
}

/**
 * @function resolveCountryOption
 * @description Resolves a single country option from code or name.
 * @param {'*'} query - ISO alpha-2/3, name, or partial label.
 * @returns {'object|null'} Country option or null.
 * @collaboration HrDashboard country selects, employee/location forms.
 */
export function resolveCountryOption(query) {
    const q = normalizeCountryQuery(query);
    if (!q) return SOVEREIGN_COUNTRIES.find((c) => c.code === 'ZA') || null;

    const exact = SOVEREIGN_COUNTRIES.find(
        (c) =>
            c.code.toLowerCase() === q ||
            c.alpha2.toLowerCase() === q ||
            c.alpha3.toLowerCase() === q ||
            c.name.toLowerCase() === q ||
            c.label.toLowerCase() === q
    );
    if (exact) return exact;

    return (
        SOVEREIGN_COUNTRIES.find(
            (c) =>
                c.name.toLowerCase().startsWith(q) ||
                c.label.toLowerCase().includes(q) ||
                c.code.toLowerCase().startsWith(q)
        ) || null
    );
}

/**
 * @function searchSovereignCountries
 * @description Searches the sovereign country registry for typeahead UIs.
 * @param {'*'} query - Search string.
 * @param {'number'} [limit=25] - Max results.
 * @returns {'Array<object>'} Matching country options.
 * @collaboration HR typeahead, billing jurisdiction picker.
 */
export function searchSovereignCountries(query, limit = 25) {
    const q = normalizeCountryQuery(query);
    const max = Math.max(1, Math.min(100, Number(limit) || 25));

    if (!q) {
        return SOVEREIGN_COUNTRIES.slice(0, max);
    }

    const scored = SOVEREIGN_COUNTRIES.map((country) => {
        const hay = `${country.code} ${country.alpha3} ${country.name} ${country.label}`.toLowerCase();
        let score = 0;
        if (country.code.toLowerCase() === q || country.alpha3.toLowerCase() === q) score = 100;
        else if (country.name.toLowerCase().startsWith(q)) score = 80;
        else if (hay.includes(q)) score = 40;
        else score = 0;
        return { country, score };
    })
        .filter((row) => row.score > 0)
        .sort((a, b) => b.score - a.score || a.country.name.localeCompare(b.country.name))
        .slice(0, max)
        .map((row) => row.country);

    return scored;
}

export default {
    SOVEREIGN_COUNTRIES,
    resolveCountryOption,
    searchSovereignCountries
};

/**
 * =============================================================================
 * INSTITUTIONAL CERTIFICATION SEAL — sovereignCountryRegistry v1.0.0
 * =============================================================================
 */
