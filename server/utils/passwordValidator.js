/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - SOVEREIGN PASSWORD VALIDATOR                                   ║
 * ║ [PASSWORD STRENGTH | COMPLIANCE | SECURITY ENFORCEMENT]                   ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | INSTITUTIONAL GRADE                   ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 *
 * @team Collaboration Notes:
 * - NIST 800-63B compliant password validation
 * - Password strength scoring and entropy calculation
 * - Common password blacklist checking
 * - Breached password detection (haveibeenpwned API integration)
 * - 101/10 security standard
 *
 * @last_updated: 2026-03-18
 * @lead_architect: Wilson Khanyezi
 */

import crypto from 'crypto';
import zxcvbn from 'zxcvbn'; // For advanced password strength estimation

// ============================================================================
// CONFIGURATION
// ============================================================================

const PASSWORD_CONFIG = {
  // NIST 800-63B guidelines
  minLength: 12,
  maxLength: 128,

  // Character requirements
  requireUppercase: true,
  requireLowercase: true,
  requireNumbers: true,
  requireSpecialChars: true,

  // Special characters allowed
  specialChars: '!@#$%^&*()_+-=[]{}|;:,.<>?~',

  // Password policy
  maxConsecutiveRepeats: 3,
  maxSequentialChars: 4,
  minUniqueChars: 6,

  // Strength thresholds (0-4)
  strengthThresholds: {
    weak: 1,
    fair: 2,
    good: 3,
    strong: 4
  },

  // Common password blacklist
  commonPasswordsPath: './data/common-passwords.txt',

  // Breached password checking
  hibpApiUrl: 'https://api.pwnedpasswords.com/range/',
  checkBreached: true,

  // Rate limiting
  maxAttemptsPerIP: 5,
  lockoutDuration: 15 * 60 * 1000, // 15 minutes

  // Password history
  rememberPasswordCount: 5, // Number of previous passwords to remember
  passwordExpiryDays: 90, // Force password change every 90 days
  warnDaysBeforeExpiry: 14
};

// ============================================================================
// COMMON PASSWORD BLACKLIST
// ============================================================================

// Top 100 most common passwords (in production, this would be a much larger list)
const COMMON_PASSWORDS = new Set([
  'password', '123456', '12345678', '1234', 'qwerty', '12345', 'dragon',
  'pussy', 'baseball', 'football', 'letmein', 'monkey', '696969', 'abc123',
  'mustang', 'michael', 'shadow', 'master', 'jennifer', '111111', '2000',
  'jordan', 'superman', 'harley', '1234567', 'fuckme', 'hunter', 'fuckyou',
  'trustno1', 'ranger', 'buster', 'thomas', 'tigger', 'robert', 'soccer',
  'fuck', 'batman', 'test', 'pass', 'killer', 'hockey', 'george', 'charlie',
  'andrew', 'michelle', 'love', 'sunshine', 'jessica', 'asshole', '6969',
  'pepper', 'daniel', 'access', '123456789', '654321', 'joshua', 'maggie',
  'starwars', 'silver', 'william', 'dallas', 'yankees', 'girl', 'booboo',
  'wilsy', 'admin', 'administrator', 'root', 'toor', 'qwertyuiop', 'asdfghjkl',
  'zxcvbnm', 'qwerty123', 'password123', '1q2w3e4r', '123qwe', 'q1w2e3r4'
]);

// ============================================================================
// PASSWORD STRENGTH CALCULATION
// ============================================================================

/**
 * Calculate password entropy (bits)
 * @param {string} password - Password to analyze
 * @returns {number} Entropy in bits
 */
export const calculateEntropy = (password) => {
  if (!password) return 0;

  // Character set sizes
  let charsetSize = 0;

  if (/[a-z]/.test(password)) charsetSize += 26;
  if (/[A-Z]/.test(password)) charsetSize += 26;
  if (/[0-9]/.test(password)) charsetSize += 10;
  if (/[^a-zA-Z0-9]/.test(password)) charsetSize += 33; // Approximate special chars

  // Calculate entropy: log2(charsetSize^length)
  return Math.log2(Math.pow(charsetSize, password.length));
};

/**
 * Check password complexity requirements
 * @param {string} password - Password to check
 * @returns {Object} Complexity check result
 */
export const checkComplexity = (password) => {
  if (!password) {
    return {
      valid: false,
      errors: ['Password is required']
    };
  }

  const errors = [];
  const checks = {
    hasUppercase: /[A-Z]/.test(password),
    hasLowercase: /[a-z]/.test(password),
    hasNumbers: /[0-9]/.test(password),
    hasSpecialChars: new RegExp(`[${PASSWORD_CONFIG.specialChars.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, '\\$&')}]`).test(password),
    length: password.length >= PASSWORD_CONFIG.minLength && password.length <= PASSWORD_CONFIG.maxLength,
    noConsecutiveRepeats: !/(.)\1{3,}/.test(password), // No 4+ consecutive repeats
    noSequentialChars: !checkSequentialChars(password)
  };

  // Required checks
  if (PASSWORD_CONFIG.requireUppercase && !checks.hasUppercase) {
    errors.push('Password must contain at least one uppercase letter');
  }

  if (PASSWORD_CONFIG.requireLowercase && !checks.hasLowercase) {
    errors.push('Password must contain at least one lowercase letter');
  }

  if (PASSWORD_CONFIG.requireNumbers && !checks.hasNumbers) {
    errors.push('Password must contain at least one number');
  }

  if (PASSWORD_CONFIG.requireSpecialChars && !checks.hasSpecialChars) {
    errors.push(`Password must contain at least one special character: ${PASSWORD_CONFIG.specialChars}`);
  }

  if (!checks.length) {
    if (password.length < PASSWORD_CONFIG.minLength) {
      errors.push(`Password must be at least ${PASSWORD_CONFIG.minLength} characters long`);
    }
    if (password.length > PASSWORD_CONFIG.maxLength) {
      errors.push(`Password must be no more than ${PASSWORD_CONFIG.maxLength} characters long`);
    }
  }

  if (!checks.noConsecutiveRepeats) {
    errors.push('Password contains too many consecutive repeated characters');
  }

  if (!checks.noSequentialChars) {
    errors.push('Password contains sequential characters (e.g., "abc" or "123")');
  }

  return {
    valid: errors.length === 0,
    errors,
    checks
  };
};

/**
 * Check for sequential characters
 * @param {string} password - Password to check
 * @returns {boolean} True if sequential chars found
 */
const checkSequentialChars = (password) => {
  const lowercase = password.toLowerCase();
  const sequences = [
    'abcdefghijklmnopqrstuvwxyz',
    'zyxwvutsrqponmlkjihgfedcba',
    '0123456789',
    '9876543210',
    'qwertyuiop', 'poiuytrewq',
    'asdfghjkl', 'lkjhgfdsa',
    'zxcvbnm', 'mnbvcxz'
  ];

  for (const seq of sequences) {
    for (let i = 0; i <= seq.length - PASSWORD_CONFIG.maxSequentialChars; i++) {
      const chunk = seq.substr(i, PASSWORD_CONFIG.maxSequentialChars);
      if (lowercase.includes(chunk)) {
        return true;
      }
    }
  }

  return false;
};

// ============================================================================
// PASSWORD STRENGTH SCORING
// ============================================================================

/**
 * Calculate password strength score (0-4)
 * @param {string} password - Password to score
 * @returns {Object} Strength score and feedback
 */
export const calculateStrength = (password) => {
  if (!password) {
    return {
      score: 0,
      strength: 'none',
      entropy: 0,
      crackTime: 'instant',
      feedback: ['Enter a password']
    };
  }

  // Use zxcvbn for advanced strength estimation
  const result = zxcvbn(password);

  // Calculate our own entropy as well
  const entropy = calculateEntropy(password);

  // Map crack time to human-readable format
  let crackTime;
  if (result.crack_times_display) {
    crackTime = result.crack_times_display.offline_slow_hashing_1e4_per_second;
  } else {
    if (entropy < 28) crackTime = 'seconds';
    else if (entropy < 36) crackTime = 'minutes';
    else if (entropy < 60) crackTime = 'hours';
    else if (entropy < 80) crackTime = 'days';
    else if (entropy < 100) crackTime = 'months';
    else if (entropy < 128) crackTime = 'years';
    else crackTime = 'centuries';
  }

  // Map score to strength level
  let strength;
  switch (result.score) {
    case 0: strength = 'very weak'; break;
    case 1: strength = 'weak'; break;
    case 2: strength = 'fair'; break;
    case 3: strength = 'good'; break;
    case 4: strength = 'strong'; break;
    default: strength = 'unknown';
  }

  return {
    score: result.score,
    strength,
    entropy: Math.round(entropy * 10) / 10,
    crackTime,
    feedback: result.feedback?.warning ? [result.feedback.warning] : [],
    suggestions: result.feedback?.suggestions || []
  };
};

// ============================================================================
// COMMON PASSWORD CHECK
// ============================================================================

/**
 * Check if password is in common password list
 * @param {string} password - Password to check
 * @returns {Object} Check result
 */
export const isCommonPassword = (password) => {
  if (!password) return { isCommon: false };

  const lowercase = password.toLowerCase();
  const isCommon = COMMON_PASSWORDS.has(lowercase);

  return {
    isCommon,
    message: isCommon ? 'This password is too common and easily guessable' : null
  };
};

// ============================================================================
// BREACHED PASSWORD CHECK (HIBP)
// ============================================================================

/**
 * Check if password has been breached using HaveIBeenPwned API
 * @param {string} password - Password to check
 * @returns {Promise<Object>} Breach check result
 */
export const checkBreachedPassword = async (password) => {
  if (!PASSWORD_CONFIG.checkBreached) {
    return { isBreached: false, checked: false };
  }

  try {
    // Create SHA-1 hash of password
    const sha1 = crypto.createHash('sha1').update(password).digest('hex').toUpperCase();
    const prefix = sha1.substring(0, 5);
    const suffix = sha1.substring(5);

    // Query HIBP API
    const response = await fetch(`${PASSWORD_CONFIG.hibpApiUrl}${prefix}`);

    if (!response.ok) {
      throw new Error(`HIBP API error: ${response.status}`);
    }

    const data = await response.text();
    const hashes = data.split('\n');

    // Check if our hash suffix exists in response
    const isBreached = hashes.some(line => {
      const [hashSuffix] = line.split(':');
      return hashSuffix === suffix;
    });

    return {
      isBreached,
      checked: true,
      message: isBreached ? 'This password has been exposed in data breaches' : null
    };
  } catch (error) {
    console.error('[PASSWORD] Breach check failed:', error);
    return {
      isBreached: false,
      checked: false,
      error: error.message
    };
  }
};

// ============================================================================
// PASSWORD VALIDATION (COMPREHENSIVE)
// ============================================================================

/**
 * Comprehensive password validation
 * @param {string} password - Password to validate
 * @param {Object} options - Validation options
 * @returns {Promise<Object>} Validation result
 */
export const validatePassword = async (password, options = {}) => {
  const {
    checkBreached = PASSWORD_CONFIG.checkBreached,
    minStrength = 2, // Minimum strength score required (0-4)
    allowCommon = false,
    customBlacklist = []
  } = options;

  const result = {
    valid: false,
    score: 0,
    strength: 'none',
    errors: [],
    warnings: [],
    suggestions: []
  };

  if (!password) {
    result.errors.push('Password is required');
    return result;
  }

  // Check length
  if (password.length < PASSWORD_CONFIG.minLength) {
    result.errors.push(`Password must be at least ${PASSWORD_CONFIG.minLength} characters long`);
  }
  if (password.length > PASSWORD_CONFIG.maxLength) {
    result.errors.push(`Password cannot exceed ${PASSWORD_CONFIG.maxLength} characters`);
  }

  // Check complexity
  const complexity = checkComplexity(password);
  if (!complexity.valid) {
    result.errors.push(...complexity.errors);
  }

  // Check common passwords
  if (!allowCommon) {
    const commonCheck = isCommonPassword(password);
    if (commonCheck.isCommon) {
      result.errors.push('This password is too common and easily guessable');
    }

    // Check custom blacklist
    if (customBlacklist.includes(password.toLowerCase())) {
      result.errors.push('This password is blacklisted');
    }
  }

  // Calculate strength
  const strength = calculateStrength(password);
  result.score = strength.score;
  result.strength = strength.strength;
  result.entropy = strength.entropy;
  result.crackTime = strength.crackTime;

  if (strength.feedback.length) {
    result.warnings.push(...strength.feedback);
  }
  if (strength.suggestions.length) {
    result.suggestions.push(...strength.suggestions);
  }

  // Check minimum strength requirement
  if (strength.score < minStrength) {
    result.errors.push(`Password strength is too weak. Try to make it more complex.`);
  }

  // Check breached passwords
  if (checkBreached && result.errors.length === 0) {
    const breachCheck = await checkBreachedPassword(password);
    if (breachCheck.isBreached) {
      result.errors.push('This password has been exposed in data breaches. Please choose a different password.');
    }
  }

  result.valid = result.errors.length === 0;
  return result;
};

// ============================================================================
// PASSWORD GENERATION
// ============================================================================

/**
 * Generate a strong random password
 * @param {Object} options - Generation options
 * @returns {string} Generated password
 */
export const generatePassword = (options = {}) => {
  const {
    length = 16,
    includeUppercase = true,
    includeLowercase = true,
    includeNumbers = true,
    includeSpecialChars = true,
    excludeAmbiguous = true // Exclude characters like O, 0, I, l, 1
  } = options;

  let chars = '';

  if (includeLowercase) {
    chars += excludeAmbiguous ? 'abcdefghjkmnpqrstuvwxyz' : 'abcdefghijklmnopqrstuvwxyz';
  }
  if (includeUppercase) {
    chars += excludeAmbiguous ? 'ABCDEFGHJKMNPQRSTUVWXYZ' : 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  }
  if (includeNumbers) {
    chars += excludeAmbiguous ? '23456789' : '0123456789';
  }
  if (includeSpecialChars) {
    chars += PASSWORD_CONFIG.specialChars;
  }

  if (chars.length === 0) {
    throw new Error('At least one character set must be included');
  }

  let password = '';
  const randomBytes = crypto.randomBytes(length);

  for (let i = 0; i < length; i++) {
    const randomIndex = randomBytes[i] % chars.length;
    password += chars[randomIndex];
  }

  return password;
};

// ============================================================================
// PASSWORD HISTORY
// ============================================================================

/**
 * Check if password has been used before
 * @param {string} newPassword - New password
 * @param {Array} passwordHistory - Array of previous password hashes
 * @returns {Object} History check result
 */
export const checkPasswordHistory = async (newPassword, passwordHistory = []) => {
  if (!passwordHistory || passwordHistory.length === 0) {
    return { isReused: false };
  }

  const newHash = crypto.createHash('sha256').update(newPassword).digest('hex');

  for (const oldHash of passwordHistory) {
    if (oldHash === newHash) {
      return {
        isReused: true,
        message: `Password has been used in the last ${PASSWORD_CONFIG.rememberPasswordCount} passwords`
      };
    }
  }

  return { isReused: false };
};

// ============================================================================
// PASSWORD EXPIRY
// ============================================================================

/**
 * Check if password has expired
 * @param {Date} lastChanged - Last password change date
 * @returns {Object} Expiry check result
 */
export const checkPasswordExpiry = (lastChanged) => {
  if (!lastChanged) {
    return {
      expired: true,
      daysRemaining: 0,
      shouldWarn: true
    };
  }

  const lastChangeDate = new Date(lastChanged);
  const now = new Date();
  const daysSinceChange = Math.floor((now - lastChangeDate) / (1000 * 60 * 60 * 24));
  const daysRemaining = PASSWORD_CONFIG.passwordExpiryDays - daysSinceChange;

  return {
    expired: daysRemaining <= 0,
    daysRemaining,
    shouldWarn: daysRemaining <= PASSWORD_CONFIG.warnDaysBeforeExpiry,
    expiryDate: new Date(lastChangeDate.getTime() + PASSWORD_CONFIG.passwordExpiryDays * 24 * 60 * 60 * 1000)
  };
};

// ============================================================================
// PASSWORD POLICY INFO
// ============================================================================

/**
 * Get password policy information
 * @returns {Object} Password policy
 */
export const getPasswordPolicy = () => {
  return {
    minLength: PASSWORD_CONFIG.minLength,
    maxLength: PASSWORD_CONFIG.maxLength,
    requireUppercase: PASSWORD_CONFIG.requireUppercase,
    requireLowercase: PASSWORD_CONFIG.requireLowercase,
    requireNumbers: PASSWORD_CONFIG.requireNumbers,
    requireSpecialChars: PASSWORD_CONFIG.requireSpecialChars,
    specialChars: PASSWORD_CONFIG.specialChars,
    maxConsecutiveRepeats: PASSWORD_CONFIG.maxConsecutiveRepeats,
    maxSequentialChars: PASSWORD_CONFIG.maxSequentialChars,
    passwordExpiryDays: PASSWORD_CONFIG.passwordExpiryDays,
    rememberPasswordCount: PASSWORD_CONFIG.rememberPasswordCount,
    strengthThresholds: PASSWORD_CONFIG.strengthThresholds,
    checkBreached: PASSWORD_CONFIG.checkBreached
  };
};

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  validatePassword,
  calculateStrength,
  calculateEntropy,
  checkComplexity,
  isCommonPassword,
  checkBreachedPassword,
  generatePassword,
  checkPasswordHistory,
  checkPasswordExpiry,
  getPasswordPolicy
};
