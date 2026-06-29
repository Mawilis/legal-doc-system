/* eslint-disable */

import {
  getCountries,
  getCountryCallingCode,
  parsePhoneNumberFromString,
} from 'libphonenumber-js';

export const WILSY_DEFAULT_PHONE_COUNTRY = 'ZA';

export const WILSY_DEFAULT_ALLOWED_PHONE_COUNTRIES = Object.freeze([
  'ZA',
  'US',
  'GB',
  'NG',
  'KE',
  'GH',
  'BW',
  'NA',
  'ZW',
  'ZM',
  'MZ',
  'LS',
  'SZ',
  'TZ',
  'UG',
  'RW',
  'AE',
  'IN',
  'AU',
  'CA',
]);

/**
 * @function normalizeWilsyCountryIso2
 * @description Normalizes a country code into an uppercase ISO-2 value supported by phone metadata.
 * @collaboration Keeps tenant phone defaults safe before rendering the country-aware edit control.
 */
export function normalizeWilsyCountryIso2(value = WILSY_DEFAULT_PHONE_COUNTRY) {
  const normalizedValue = String(value || WILSY_DEFAULT_PHONE_COUNTRY).trim().toUpperCase();
  const countries = getCountries();

  return countries.includes(normalizedValue) ? normalizedValue : WILSY_DEFAULT_PHONE_COUNTRY;
}

/**
 * @function getWilsyPhoneCountryOptions
 * @description Builds country selector options from local libphonenumber metadata.
 * @collaboration Avoids hardcoded country arrays and avoids runtime calls to third-party phone APIs.
 */
export function getWilsyPhoneCountryOptions(allowedCountries = WILSY_DEFAULT_ALLOWED_PHONE_COUNTRIES) {
  const countries = getCountries();
  const allowedSet = new Set(
    (Array.isArray(allowedCountries) && allowedCountries.length ? allowedCountries : countries)
      .map((country) => normalizeWilsyCountryIso2(country))
  );

  return countries
    .filter((country) => allowedSet.has(country))
    .map((country) => ({
      iso2: country,
      callingCode: `+${getCountryCallingCode(country)}`,
      label: `${country} +${getCountryCallingCode(country)}`,
    }))
    .sort((left, right) => left.label.localeCompare(right.label));
}

/**
 * @function normalizeWilsyPhoneForClient
 * @description Normalizes a phone input into E.164-style client metadata before backend validation.
 * @collaboration Gives the edit surface immediate feedback while the backend remains the authority.
 */
export function normalizeWilsyPhoneForClient(rawInput = '', countryIso2 = WILSY_DEFAULT_PHONE_COUNTRY) {
  const normalizedCountry = normalizeWilsyCountryIso2(countryIso2);
  const rawValue = String(rawInput || '').trim();

  if (!rawValue || rawValue === '—' || rawValue.toUpperCase() === 'SOURCE SILENT') {
    return {
      rawInput: rawValue,
      e164: '',
      countryIso2: normalizedCountry,
      countryCallingCode: `+${getCountryCallingCode(normalizedCountry)}`,
      nationalNumber: '',
      isValid: false,
      validationEngine: 'libphonenumber-js',
    };
  }

  const phone = parsePhoneNumberFromString(rawValue, normalizedCountry);

  return {
    rawInput: rawValue,
    e164: phone?.number || rawValue,
    countryIso2: phone?.country || normalizedCountry,
    countryCallingCode: phone?.countryCallingCode ? `+${phone.countryCallingCode}` : `+${getCountryCallingCode(normalizedCountry)}`,
    nationalNumber: phone?.nationalNumber || rawValue.replace(/\D/g, ''),
    isValid: Boolean(phone?.isValid()),
    validationEngine: 'libphonenumber-js',
  };
}

/**
 * @function formatWilsyPhoneDisplay
 * @description Produces a readable phone value for the CRM edit and proof surfaces.
 * @collaboration Lets operators see normalized phone posture without losing raw source evidence.
 */
export function formatWilsyPhoneDisplay(phoneValue = '') {
  if (phoneValue && typeof phoneValue === 'object') {
    return phoneValue.e164 || phoneValue.rawInput || 'Source silent';
  }

  const rawValue = String(phoneValue || '').trim();

  return rawValue || 'Source silent';
}
