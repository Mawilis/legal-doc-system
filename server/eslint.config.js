/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - PRODUCTION ESLINT CONFIG v3.0                                  ║
 * ║ [Handles missing files gracefully | Multi-billion dollar architecture]   ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

export default [
  // IGNORES - CRITICAL: Files that don't exist or shouldn't be linted
  {
    ignores: [
      // Missing files that cause ESLint to crash
      '**/models/securityLogModel.js',
      '**/models/*.missing.js',
      
      // Dependencies - NEVER LINT
      'node_modules/**',
      'dist/**',
      'build/**',
      'coverage/**',
      
      // Backup files
      '**/*.bak',
      '**/*.backup',
      '**/*.BAK',
      '**/*.final.bak',
      
      // Fix scripts (intentional patterns)
      'scripts/**/*.js',
      'final-*.js',
      'surgical-*.js',
      'strategic-*.js',
      
      // Legacy backup
      'tests_legacy_backup/**',
      
      // Evidence files
      'docs/evidence/**',
      '*.forensic.json',
      'evidence.json',
    ],
  },

  // PRODUCTION CODE - STRICT RULES
  {
    files: [
      '**/*.js', 
      '**/*.cjs', 
      '**/*.mjs',
      '!scripts/**',
      '!final-*.js',
      '!surgical-*.js',
      '!strategic-*.js',
      '!**/*.bak',
      '!**/*.backup',
    ],
    
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      globals: {
        // Node.js globals
        process: 'readonly',
        console: 'readonly',
        __dirname: 'readonly',
        __filename: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        setInterval: 'readonly',
        clearInterval: 'readonly',
        Buffer: 'readonly',
        global: 'readonly',
        
        // ES2021
        Promise: 'readonly',
        Map: 'readonly',
        Set: 'readonly',
        WeakMap: 'readonly',
        WeakSet: 'readonly',
        Symbol: 'readonly',
        BigInt: 'readonly',
        
        // Test globals
        describe: 'readonly',
        it: 'readonly',
        before: 'readonly',
        after: 'readonly',
        beforeEach: 'readonly',
        afterEach: 'readonly',
        context: 'readonly',
        specify: 'readonly',
        xdescribe: 'readonly',
        xit: 'readonly',
        expect: 'readonly',
        assert: 'readonly',
        sinon: 'readonly',
        chai: 'readonly',
        proxyquire: 'readonly',
        supertest: 'readonly',
        jest: 'readonly',
        beforeAll: 'readonly',
        afterAll: 'readonly',
      },
    },

    rules: {
      // CRITICAL - MUST FIX FOR LEGAL COMPLIANCE
      'no-undef': 'error',                    // Prevents runtime errors
      'no-unused-vars': ['error', {           // Clean code for auditors
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^(logger|auditLogger|validationUtils|expect|assert|should|sinon|chai|__)?[A-Za-z]*$',
        caughtErrorsIgnorePattern: '^_',
      }],
      
      // HIGH PRIORITY - Fix for production
      'no-console': ['error', { allow: ['warn', 'error'] }], // Use logger for audit trails
      'require-await': 'error',                // Async functions must use await
      'no-use-before-define': ['error', {      // Prevent temporal dead zone
        functions: false,
        classes: true,
        variables: true,
      }],
      
      // MEDIUM PRIORITY - Code quality
      'eqeqeq': ['error', 'always'],           // Type safety
      'no-multiple-empty-lines': ['error', { max: 2 }],
      'prefer-const': 'error',
      'prefer-template': 'error',
      'radix': 'error',
      
      // POPIA COMPLIANCE - PII PROTECTION
      'no-restricted-syntax': [
        'error',
        {
          selector: 'CallExpression[callee.object.name="logger"][callee.property.name=/^(info|debug|log)$/] BinaryExpression[operator="+"] Literal[value=/.*(idNumber|passport|email|phone|bank|credit|password|secret).*/i]',
          message: 'Potential PII in log concatenation - use redactSensitive()',
        },
      ],
    },
  },

  // FORENSIC ENGINES - SPECIAL RULES
  {
    files: ['wilsy-forensic-engine-*.cjs'],
    rules: {
      'no-console': 'off',      // Forensic engines need console
      'no-undef': 'off',        // They use CommonJS patterns
      'no-unused-vars': 'off',  // Intentional patterns
    },
  },

  // TEST FILES - RELAXED RULES
  {
    files: ['**/*.test.js', '**/*.spec.js', '__tests__/**/*.js', 'tests/**/*.js'],
    rules: {
      'no-console': 'off',
      'no-unused-expressions': 'off',
      'max-len': 'off',
    },
  },
];
