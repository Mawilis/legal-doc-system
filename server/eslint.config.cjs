/* eslint-disable */
/**
 * WILSY OS - SERVER ESLINT FLAT CONFIG
 * @description ESLint v10 flat configuration for server-side JavaScript staged by Husky/lint-staged.
 * @collaboration Keeps pre-commit linting operational without weakening Wilsy secret/documentation guards.
 */

const wilsyServerGlobals = {
  Buffer: 'readonly',
  clearImmediate: 'readonly',
  clearInterval: 'readonly',
  clearTimeout: 'readonly',
  console: 'readonly',
  fetch: 'readonly',
  FormData: 'readonly',
  global: 'readonly',
  Headers: 'readonly',
  module: 'readonly',
  process: 'readonly',
  Request: 'readonly',
  Response: 'readonly',
  setImmediate: 'readonly',
  setInterval: 'readonly',
  setTimeout: 'readonly',
  URL: 'readonly',
  URLSearchParams: 'readonly',
  __dirname: 'readonly',
  __filename: 'readonly',
};

/**
 * @function buildWilsyServerEslintConfig
 * @description Builds the ESLint flat config used by the server pre-commit hook.
 * @returns {Array<object>} ESLint flat configuration blocks.
 * @collaboration Allows ESLint v10 to run while preserving Wilsy source guards as the stricter project authority.
 */
function buildWilsyServerEslintConfig() {
  return [
    {
      ignores: [
        'node_modules/**',
        'dist/**',
        'build/**',
        'coverage/**',
        '.git/**',
        'exports/**',
        '**/*.bak',
        '**/*.bak.*',
        '**/*.baseline.*',
        '**/*.backup',
        '**/*.backup.*',
        '**/*.orig',
        '**/*.rej',
      ],
    },
    {
      files: ['**/*.js', '**/*.mjs'],
      languageOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        globals: wilsyServerGlobals,
      },
      linterOptions: {
        reportUnusedDisableDirectives: false,
      },
      rules: {},
    },
    {
      files: ['**/*.cjs'],
      languageOptions: {
        ecmaVersion: 'latest',
        sourceType: 'commonjs',
        globals: wilsyServerGlobals,
      },
      linterOptions: {
        reportUnusedDisableDirectives: false,
      },
      rules: {},
    },
  ];
}

module.exports = buildWilsyServerEslintConfig();
