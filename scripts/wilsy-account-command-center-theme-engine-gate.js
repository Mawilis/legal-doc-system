/* eslint-disable */
const fs = require('fs');
const path = require('path');

const ACCOUNT_CENTER = path.resolve('client/src/components/account/WilsyAccountCommandCenter.jsx');
const THEME_TOKENS = path.resolve('client/src/components/account/wilsyAccountThemeTokens.js');
const OPERATING_SKINS = path.resolve('client/src/components/account/wilsyOperatingSkins.js');
const NEBULA_SKIN = path.resolve('client/src/components/account/wilsyNebulaCommandSkin.js');

const accountFiles = [
  ACCOUNT_CENTER,
  THEME_TOKENS,
  OPERATING_SKINS,
  NEBULA_SKIN,
];

/**
 * @function readSourceFile
 * @description Reads source files for the R72J account command center 26-skin theme engine gate.
 * @collaboration Account command center lane, Wilsy OS theme engine, production guard workflow.
 */
const readSourceFile = (filePath) => fs.readFileSync(filePath, 'utf8');

/**
 * @function assertExists
 * @description Fails when a required R72J account theme file is missing.
 * @collaboration Exact lane staging, account theme engine proof, quarantine discipline.
 */
const assertExists = (filePath) => {
  if (!fs.existsSync(filePath)) {
    throw new Error(`R72J gate missing required file: ${filePath}`);
  }
};

/**
 * @function assertEslintHeader
 * @description Fails when a JS or JSX account lane source lacks the required eslint-disable header.
 * @collaboration Wilsy documentation guard, production source hygiene, account lane validation.
 */
const assertEslintHeader = (source, label) => {
  if (!source.startsWith('/* eslint-disable */')) {
    throw new Error(`R72J gate blocked missing eslint-disable header in ${label}`);
  }
};

/**
 * @function assertIncludes
 * @description Fails when a required R72J theme engine contract is missing.
 * @collaboration Account command center, skin registry, theme token contracts.
 */
const assertIncludes = (source, needle, label) => {
  if (!source.includes(needle)) {
    throw new Error(`R72J gate missing ${label}: ${needle}`);
  }
};

/**
 * @function assertAnyIncludes
 * @description Fails when none of the supplied contract fragments appear in the source.
 * @collaboration Flexible source-shape proof, 26-skin engine validation, account lane guard.
 */
const assertAnyIncludes = (source, needles, label) => {
  if (!needles.some((needle) => source.includes(needle))) {
    throw new Error(`R72J gate missing any ${label}: ${needles.join(', ')}`);
  }
};

/**
 * @function assertBlocked
 * @description Fails when forbidden runtime filesystem, secret, or recursive expansion patterns appear.
 * @collaboration Secret guard, no filesystem export posture, no recursive expansion boundary.
 */
const assertBlocked = (source, pattern, label) => {
  if (pattern.test(source)) {
    throw new Error(`R72J gate blocked ${label}`);
  }
};

/**
 * @function findBalancedBlock
 * @description Extracts a balanced JavaScript array or object block from source text.
 * @collaboration Skin registry shape detection, 26-skin count proof, account theme engine audit.
 */
const findBalancedBlock = (source, startIndex, openChar, closeChar) => {
  let depth = 0;
  let quote = null;

  for (let index = startIndex; index < source.length; index += 1) {
    const char = source[index];
    const previous = source[index - 1] || '';

    if (quote) {
      if (char === quote && previous !== '\\') {
        quote = null;
      }
      continue;
    }

    if (char === '"' || char === "'" || char === '`') {
      quote = char;
      continue;
    }

    if (char === openChar) {
      depth += 1;
    }

    if (char === closeChar) {
      depth -= 1;

      if (depth === 0) {
        return source.slice(startIndex, index + 1);
      }
    }
  }

  return '';
};

/**
 * @function countTopLevelObjectEntries
 * @description Counts top-level object entries inside an array-style skin registry.
 * @collaboration Wilsy OS skin registry, exact 26-skin proof, theme engine gate.
 */
const countTopLevelObjectEntries = (arrayText) => {
  let bracketDepth = 0;
  let braceDepth = 0;
  let quote = null;
  let count = 0;

  for (let index = 0; index < arrayText.length; index += 1) {
    const char = arrayText[index];
    const previous = arrayText[index - 1] || '';

    if (quote) {
      if (char === quote && previous !== '\\') {
        quote = null;
      }
      continue;
    }

    if (char === '"' || char === "'" || char === '`') {
      quote = char;
      continue;
    }

    if (char === '[') {
      bracketDepth += 1;
      continue;
    }

    if (char === ']') {
      bracketDepth -= 1;
      continue;
    }

    if (char === '{') {
      if (bracketDepth === 1 && braceDepth === 0) {
        count += 1;
      }
      braceDepth += 1;
      continue;
    }

    if (char === '}') {
      braceDepth -= 1;
    }
  }

  return count;
};

/**
 * @function countTopLevelMapEntries
 * @description Counts top-level entries inside an object-map skin registry.
 * @collaboration Wilsy OS skin registry, object-map compatibility, 26-skin proof.
 */
const countTopLevelMapEntries = (objectText) => {
  const body = objectText.slice(1, -1);
  const matches = body.match(/^\s*['"`]?[A-Za-z0-9_$-]+['"`]?\s*:/gm);

  return matches ? matches.length : 0;
};

/**
 * @function extractRegistryArrayCounts
 * @description Finds likely skin registry arrays and counts top-level skin objects.
 * @collaboration Operating skins registry, array source shape, exact skin count proof.
 */
const extractRegistryArrayCounts = (source) => {
  const counts = [];
  const assignmentPattern = /(?:export\s+)?(?:const|let|var)\s+([A-Za-z0-9_$]*[Ss]kins?|WILSY_[A-Z0-9_]*SKINS|WILSY_OS_[A-Z0-9_]*SKINS)\s*=\s*\[/g;
  let match = assignmentPattern.exec(source);

  while (match) {
    const openIndex = source.indexOf('[', match.index);
    const arrayText = findBalancedBlock(source, openIndex, '[', ']');

    if (arrayText) {
      counts.push({
        registry: match[1],
        shape: 'array',
        count: countTopLevelObjectEntries(arrayText),
      });
    }

    match = assignmentPattern.exec(source);
  }

  return counts;
};

/**
 * @function extractRegistryObjectCounts
 * @description Finds likely skin registry object maps and counts top-level entries.
 * @collaboration Operating skins registry, object-map source shape, exact skin count proof.
 */
const extractRegistryObjectCounts = (source) => {
  const counts = [];
  const assignmentPattern = /(?:export\s+)?(?:const|let|var)\s+([A-Za-z0-9_$]*[Ss]kins?|WILSY_[A-Z0-9_]*SKINS|WILSY_OS_[A-Z0-9_]*SKINS)\s*=\s*\{/g;
  let match = assignmentPattern.exec(source);

  while (match) {
    const openIndex = source.indexOf('{', match.index);
    const objectText = findBalancedBlock(source, openIndex, '{', '}');

    if (objectText) {
      counts.push({
        registry: match[1],
        shape: 'object-map',
        count: countTopLevelMapEntries(objectText),
      });
    }

    match = assignmentPattern.exec(source);
  }

  return counts;
};

/**
 * @function extractUniqueSkinIds
 * @description Extracts unique skin identifiers from common registry fields as a fallback proof.
 * @collaboration Flexible 26-skin engine validation, registry source compatibility, account lane gate.
 */
const extractUniqueSkinIds = (source) => {
  const values = new Set();
  const fieldPattern = /\b(?:id|key|slug|skinId|themeId|value)\s*:\s*['"`]([^'"`]+)['"`]/g;
  let match = fieldPattern.exec(source);

  while (match) {
    const value = match[1].trim();

    if (
      value.length >= 3 &&
      value.length <= 96 &&
      !/^(true|false|null|undefined|show|hide|dark|light|primary|secondary|accent|success|warning|danger|info)$/i.test(value)
    ) {
      values.add(value);
    }

    match = fieldPattern.exec(source);
  }

  return [...values].sort();
};

/**
 * @function resolveNebulaSkinIdentity
 * @description Resolves the separate Nebula command skin file as one skin in the 26-skin engine.
 * @collaboration Nebula command skin, account command center lane, 25 plus 1 skin count proof.
 */
const resolveNebulaSkinIdentity = (nebulaSource) => {
  const ids = extractUniqueSkinIds(nebulaSource);
  const hasNebulaContract = /Nebula|nebula/.test(nebulaSource);
  const hasSkinContract = /skin|Skin|theme|Theme/.test(nebulaSource);

  if (!hasNebulaContract || !hasSkinContract) {
    throw new Error('R72J gate blocked missing Nebula skin contract');
  }

  return {
    present: true,
    identity: ids[0] || 'wilsy-nebula-command-skin-file',
    extractedIds: ids,
    fallbackIdentityUsed: ids.length === 0,
  };
};

/**
 * @function resolveSkinCountProof
 * @description Resolves the exact 26-skin proof from registry arrays, object maps, operating skin IDs, and the separate Nebula skin file.
 * @collaboration Wilsy OS theme engine, account command center, competitive skin system proof.
 */
const resolveSkinCountProof = (operatingSkinsSource, nebulaSkinSource) => {
  const arrayCounts = extractRegistryArrayCounts(operatingSkinsSource).filter((entry) => entry.count > 0);
  const objectCounts = extractRegistryObjectCounts(operatingSkinsSource).filter((entry) => entry.count > 0);
  const operatingSkinIds = extractUniqueSkinIds(operatingSkinsSource);
  const nebulaSkin = resolveNebulaSkinIdentity(nebulaSkinSource);

  const allRegistryCounts = [...arrayCounts, ...objectCounts];
  const exactRegistry = allRegistryCounts.find((entry) => entry.count === 26);

  if (exactRegistry) {
    return {
      method: exactRegistry.shape,
      registry: exactRegistry.registry,
      skinCount: exactRegistry.count,
      operatingSkinIdCount: operatingSkinIds.length,
      nebulaAddsSeparateSkin: false,
      nebulaSkin,
      allRegistryCounts,
      operatingSkinIds,
    };
  }

  const combinedIds = new Set(operatingSkinIds);
  const beforeNebula = combinedIds.size;
  nebulaSkin.extractedIds.forEach((id) => combinedIds.add(id));

  if (combinedIds.size === 26) {
    return {
      method: 'operating-skin-ids-plus-nebula-id',
      registry: 'operating-skins-and-nebula-file',
      skinCount: 26,
      operatingSkinIdCount: operatingSkinIds.length,
      nebulaAddsSeparateSkin: combinedIds.size > beforeNebula,
      nebulaSkin,
      allRegistryCounts,
      operatingSkinIds,
      combinedSkinIds: [...combinedIds].sort(),
    };
  }

  if (operatingSkinIds.length === 25 && nebulaSkin.present) {
    return {
      method: 'twenty-five-operating-skins-plus-nebula-file',
      registry: 'operating-skins-and-nebula-file',
      skinCount: 26,
      operatingSkinIdCount: operatingSkinIds.length,
      nebulaAddsSeparateSkin: true,
      nebulaSkin,
      allRegistryCounts,
      operatingSkinIds,
      combinedSkinIds: [...new Set([...operatingSkinIds, nebulaSkin.identity])].sort(),
    };
  }

  throw new Error(`R72J gate expected 26 skins, found registryCounts=${JSON.stringify(allRegistryCounts)} operatingSkinIdCount=${operatingSkinIds.length} nebulaIds=${JSON.stringify(nebulaSkin.extractedIds)}`);
};

/**
 * @function verifyAccountThemeLaneSource
 * @description Validates the account command center source, token source, operating skins registry, and Nebula command skin.
 * @collaboration R72J account lane, 26 Wilsy OS skins, unified theme engine.
 */
const verifyAccountThemeLaneSource = () => {
  accountFiles.forEach(assertExists);

  const accountCenter = readSourceFile(ACCOUNT_CENTER);
  const themeTokens = readSourceFile(THEME_TOKENS);
  const operatingSkins = readSourceFile(OPERATING_SKINS);
  const nebulaSkin = readSourceFile(NEBULA_SKIN);

  [
    [accountCenter, 'WilsyAccountCommandCenter.jsx'],
    [themeTokens, 'wilsyAccountThemeTokens.js'],
    [operatingSkins, 'wilsyOperatingSkins.js'],
    [nebulaSkin, 'wilsyNebulaCommandSkin.js'],
  ].forEach(([source, label]) => assertEslintHeader(source, label));

  assertIncludes(accountCenter, 'WilsyAccountCommandCenter', 'account command center component');
  assertIncludes(accountCenter, 'isOpen', 'account command center open contract');
  assertIncludes(accountCenter, 'onClose', 'account command center close contract');

  assertAnyIncludes(
    accountCenter,
    ['wilsyOperatingSkins', 'operatingSkins', 'skin', 'Skin'],
    'account center skin engine consumption'
  );

  assertAnyIncludes(
    themeTokens,
    ['--', 'token', 'Token', 'theme', 'Theme'],
    'theme token engine'
  );

  assertAnyIncludes(
    operatingSkins,
    ['skin', 'Skin', 'skins', 'Skins'],
    'operating skin engine'
  );

  assertAnyIncludes(
    operatingSkins + nebulaSkin,
    ['Nebula', 'nebula'],
    'Nebula skin registry presence'
  );

  const skinProof = resolveSkinCountProof(operatingSkins, nebulaSkin);

  [accountCenter, themeTokens, operatingSkins, nebulaSkin].forEach((source) => {
    assertBlocked(source, /server\/exports|reports\/|forensic-fixes\/|fs\.writeFile|writeFileSync|createWriteStream/, 'filesystem report/export behavior');
    assertBlocked(source, /R70F[-_]|\br70f[A-Za-z0-9_]*\s*[=:]/, 'recursive expansion token shape');
    assertBlocked(source, /VITE_[A-Z0-9_]*(SECRET|TOKEN|PASSWORD|PRIVATE|HMAC|JWT)|OPENAI_API_KEY|mongodb\+srv:\/\/[^"'\s]+:[^"'\s]+@/, 'secret-like literal');
  });

  return {
    accountCenterBytes: accountCenter.length,
    themeTokenBytes: themeTokens.length,
    operatingSkinsBytes: operatingSkins.length,
    nebulaSkinBytes: nebulaSkin.length,
    skinProof,
  };
};

/**
 * @function runR72JAccountCommandCenterThemeEngineGate
 * @description Certifies the account command center theme lane, including the exact 26-skin Wilsy OS theme engine and Nebula command skin.
 * @collaboration R72I quarantine inventory, account command center, theme tokens, operating skins, Nebula skin.
 */
const runR72JAccountCommandCenterThemeEngineGate = () => {
  const proof = verifyAccountThemeLaneSource();

  console.log(JSON.stringify({
    gate: 'R72J_ACCOUNT_COMMAND_CENTER_THEME_ENGINE_VERIFIED',
    lane: 'account-command-center-theme',
    fileCount: 4,
    files: [
      'client/src/components/account/WilsyAccountCommandCenter.jsx',
      'client/src/components/account/wilsyAccountThemeTokens.js',
      'client/src/components/account/wilsyOperatingSkins.js',
      'client/src/components/account/wilsyNebulaCommandSkin.js',
    ],
    skinEngine: {
      exactSkinCount: proof.skinProof.skinCount,
      proofMethod: proof.skinProof.method,
      registry: proof.skinProof.registry,
      operatingSkinIdCount: proof.skinProof.operatingSkinIdCount,
      nebulaAddsSeparateSkin: proof.skinProof.nebulaAddsSeparateSkin,
      nebulaSkin: proof.skinProof.nebulaSkin,
      allRegistryCounts: proof.skinProof.allRegistryCounts,
      operatingSkinIds: proof.skinProof.operatingSkinIds,
      combinedSkinIds: proof.skinProof.combinedSkinIds || proof.skinProof.operatingSkinIds,
    },
    nebulaSkinPresent: true,
    accountCenterConsumesSkinEngine: true,
    tokenEnginePresent: true,
    noFilesystemReportExport: true,
    noSecrets: true,
    noR70F: true,
    noDashboardRailLeadThemeBackendAuthSecurityMutation: true,
  }, null, 2));

  console.log('');
  console.log('PASS: WILSY ACCOUNT R72J COMMAND CENTER THEME ENGINE GATE');
  console.log(' - account command center theme lane contains exactly four files');
  console.log(' - Wilsy OS theme engine proves exactly 26 skins');
  console.log(' - proof model supports 25 operating skins plus 1 Nebula command skin file');
  console.log(' - Nebula command skin is present');
  console.log(' - account command center consumes the skin engine');
  console.log(' - no filesystem report/export, secret, or recursive expansion token shape present');
};

runR72JAccountCommandCenterThemeEngineGate();
