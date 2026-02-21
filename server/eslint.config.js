import js from '@eslint/js';  // Recommended base rules
import globals from 'globals';  // For environments like Node
import importPlugin from 'eslint-plugin-import';  // Your import plugin
import { FlatCompat } from '@eslint/eslintrc';  // Compatibility for airbnb-base

const compat = new FlatCompat();  // No baseDirectory needed

export default [
    ...compat.extends('airbnb-base'),  // Loads your airbnb config
    {
        plugins: {
            import: importPlugin  // Enables import rules
        },
        languageOptions: {
            ecmaVersion: 'latest',  // Supports ES2021+ syntax
            sourceType: 'module',   // Allows import/require
            globals: {
                ...globals.node       // Node.js globals
            }
        },
        rules: {
            // Custom overrides if needed
            'no-console': 'warn'
        },
        ignores: ['node_modules/**', 'dist/**']  // Ignore patterns
    }
];