#!/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - FORENSIC REDACTION ENGINE V4.2 (FINAL)                         ║
 * ║ SURGICAL FIXES APPLIED:                                                   ║
 * ║ 1. PAIA Privilege - Now aggressively swallows the ENTIRE text block       ║
 * ║ 2. Commercial Object - Deep preservation of VAT/Registration data         ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

export function redactSensitive(data, options = {}) {
  const { context = 'general', replacement = '[REDACTED]' } = options;

  if (data === null || data === undefined) {
    return data;
  }

  if (typeof data === 'string') {
    return redactString(data, context, replacement);
  }

  if (Array.isArray(data)) {
    return data.map((item) => redactSensitive(item, options));
  }

  if (typeof data === 'object') {
    return redactObject(data, context, replacement);
  }

  return data;
}

function redactString(text, context, replacement) {
  if (!text || typeof text !== 'string') return text;

  let redacted = text;

  // SOUTH AFRICAN IDENTITY NUMBER (13 digits)
  const saIdPattern = /\b[0-9]{13}\b/g;

  // PASSPORT NUMBERS
  const passportPattern = /\b[A-Z]{1,2}[0-9]{6,8}\b/g;

  // COMPANY REGISTRATION
  const companyRegPattern = /\b[0-9]{4}\/[0-9]{6}\/[0-9]{2}\b/g;

  // BANK ACCOUNT NUMBERS
  const bankAccountPattern = /\b[0-9]{8,16}\b/g;

  // EMAIL ADDRESSES
  const emailPattern = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;

  // STRICT PHONE NUMBERS
  const phonePattern = /\b(?:\+27|0)[6-8][0-9]{8}\b/g;

  if (context === 'paia') {
    // FINAL FIX: [\s\S]* forcefully swallows the trigger word AND the rest of the text block
    redacted = redacted.replace(
      /(?:\[.*?\]\s*)?without prejudice[\s\S]*/gi,
      '[LEGAL PRIVILEGE - Without Prejudice]'
    );
    redacted = redacted.replace(
      /(?:\[.*?\]\s*)?legal opinion[\s\S]*/gi,
      '[LEGAL PRIVILEGE - Legal Opinion]'
    );
    redacted = redacted.replace(
      /(?:\[.*?\]\s*)?counsel advises[\s\S]*/gi,
      '[LEGAL PRIVILEGE - Counsel Advice]'
    );
  } else if (context === 'commercial') {
    redacted = redacted
      .replace(saIdPattern, replacement)
      .replace(passportPattern, replacement)
      .replace(emailPattern, replacement)
      .replace(phonePattern, replacement)
      .replace(bankAccountPattern, replacement);
  } else if (context === 'popia') {
    redacted = redacted.replace(saIdPattern, (match) => {
      return match.substring(0, 3) + '[REDACTED]';
    });
    redacted = redacted
      .replace(passportPattern, replacement)
      .replace(emailPattern, replacement)
      .replace(phonePattern, replacement)
      .replace(bankAccountPattern, replacement);
  } else {
    redacted = redacted
      .replace(saIdPattern, replacement)
      .replace(passportPattern, replacement)
      .replace(emailPattern, replacement)
      .replace(phonePattern, replacement)
      .replace(bankAccountPattern, replacement)
      .replace(companyRegPattern, replacement);
  }

  return redacted;
}

function redactObject(obj, context, replacement) {
  if (!obj || typeof obj !== 'object') return obj;

  const sensitiveFields = [
    'idNumber',
    'identityNumber',
    'passportNumber',
    'email',
    'phone',
    'cellphone',
    'mobile',
    'bankAccount',
    'accountNumber',
    'membershipNumber',
    'salary',
    'profit',
    'revenue',
    'ebitda',
  ];

  const preserveInCommercial = ['vat', 'vatnumber', 'registrationnumber', 'registration'];

  const redacted = Array.isArray(obj) ? [] : {};

  for (const [key, value] of Object.entries(obj)) {
    const keyLower = key.toLowerCase();

    const isSensitive = sensitiveFields.some((field) => keyLower.includes(field));
    const shouldPreserve =
      context === 'commercial' && preserveInCommercial.some((field) => keyLower.includes(field));

    if (context === 'paia' && keyLower === 'attorneynotes') {
      redacted[key] = '[LEGAL PRIVILEGE]';
    } else if (shouldPreserve) {
      redacted[key] = value;
    } else if (typeof value === 'string') {
      if (context === 'popia' && keyLower.includes('id') && !keyLower.includes('request')) {
        redacted[key] = value.substring(0, 3) + '[REDACTED]';
      } else if (isSensitive) {
        redacted[key] = replacement;
      } else {
        redacted[key] = redactString(value, context, replacement);
      }
    } else if (typeof value === 'object' && value !== null) {
      redacted[key] = redactObject(value, context, replacement);
    } else {
      redacted[key] = value;
    }
  }

  return redacted;
}

export function redactWithAudit(data, context = 'general') {
  const auditId = `REDACT-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
  const startTime = Date.now();

  const redacted = redactSensitive(data, { context });

  let redactionCount = 0;
  const countRedactions = (obj) => {
    if (typeof obj === 'string') {
      const matches =
        (obj.match(/\[REDACTED\]/g) || []).length +
        (obj.match(/\[LEGAL PRIVILEGE[^\]]*\]/g) || []).length;
      return matches;
    }
    if (typeof obj === 'object' && obj !== null) {
      let count = 0;
      Object.values(obj).forEach((val) => {
        count += countRedactions(val);
      });
      return count;
    }
    return 0;
  };

  redactionCount = countRedactions(redacted);

  const audit = {
    auditId,
    timestamp: new Date().toISOString(),
    context,
    redactionCount,
    processingTimeMs: Date.now() - startTime,
    dataType: typeof data,
    isArray: Array.isArray(data),
  };

  return { data: redacted, audit };
}

export default { redactSensitive, redactWithAudit };
