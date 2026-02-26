module.exports = {
  root: true,
  env: {
    node: true,
    es2022: true,
    jest: true,
  },
  extends: [
    'eslint:recommended',
    'airbnb-base',
  ],
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module',
  },
  rules: {
    'no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    'import/prefer-default-export': 'off',
    'import/extensions': ['error', 'ignorePackages'],
    'comma-dangle': ['error', 'always-multiline'],
    'no-underscore-dangle': ['error', {
      allow: ['_id', '__v', '_doc'],
    }],
  },
  settings: {
    'import/resolver': {
      node: {
        extensions: ['.js'],
      },
    },
  },
  ignorePatterns: [
    'public/**/*',
    'dist/**/*',
    'build/**/*',
    'coverage/**/*',
    'node_modules/**/*',
    '**/*.min.js',
    '**/*.css',
    '**/*.html',
  ],
};
