/* eslint-disable */
/*
 * File: /Users/wilsonkhanyezi/legal-doc-system/forensicMapper.js
 * STATUS: PRODUCTION-READY (WILSY OS V7.0-QUANTUM-OMEGA)
 * PURPOSE: Forensic architecture mapping for AI, EOS, and Intelligence integration.
 * COLLABORATION COMMENTS: Epitome, biblical worth billions no child's place. 
 * DESCRIPTION: Recursively scans the Wilsy OS filesystem to map out all files 
 *              containing core intelligence keywords to ensure safe, holistic upgrades.
 * AUTHOR: Wilson Khanyezi - 10th Generation Architect
 * LAST_UPDATE: 2026-08-04
 */

const fs = require('fs').promises;
const path = require('path');

// -----------------------------------------------------------------------------
// CONFIGURATION & KEYWORDS
// -----------------------------------------------------------------------------
const TARGET_DIRECTORIES = [
    '/Users/wilsonkhanyezi/legal-doc-system'
];

const KEYWORDS = [
    'intelligence', 
    'kennel', 
    'eos', 
    'ai', 
    'wilsy ai'
];

const IGNORED_DIRS = new Set([
    'node_modules', 
    '.git', 
    'dist', 
    'build', 
    'coverage', 
    '.next'
]);

const IGNORED_EXTENSIONS = new Set([
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', 
    '.mp4', '.mp3', '.wav', '.pdf', '.zip', '.tar', '.gz'
]);

// -----------------------------------------------------------------------------
// CORE MAPPING ENGINE
// -----------------------------------------------------------------------------

/**
 * Collaboration Comment: Escapes regex characters to ensure accurate forensic mapping.
 * @param {string} string - The keyword to escape
 * @returns {string} - Regex-safe string
 */
const escapeRegExp = (string) => {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
};

const keywordRegexes = KEYWORDS.map(kw => new RegExp(`\\b${escapeRegExp(kw)}\\b`, 'i'));

/**
 * Collaboration Comment: Recursively traverses the file system to map intelligence nodes.
 * @param {string} dir - Current directory path
 * @param {Array} results - Accumulator array for matched files
 */
async function scanDirectory(dir, results) {
    try {
        const entries = await fs.readdir(dir, { withFileTypes: true });

        for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);

            if (entry.isDirectory()) {
                if (!IGNORED_DIRS.has(entry.name)) {
                    await scanDirectory(fullPath, results);
                }
            } else if (entry.isFile()) {
                const ext = path.extname(entry.name).toLowerCase();
                if (!IGNORED_EXTENSIONS.has(ext)) {
                    await processFile(fullPath, results);
                }
            }
        }
    } catch (error) {
        console.error(`[SYSTEM WARNING] Could not access directory: ${dir} - ${error.message}`);
    }
}

/**
 * Collaboration Comment: Inspects file contents for Wilsy OS intelligence signatures.
 * @param {string} filePath - Absolute path to the file
 * @param {Array} results - Accumulator array
 */
async function processFile(filePath, results) {
    try {
        const content = await fs.readFile(filePath, 'utf-8');
        const matches = [];

        KEYWORDS.forEach((keyword, index) => {
            if (keywordRegexes[index].test(content)) {
                matches.push(keyword);
            }
        });

        // If file contains any of the target keywords, log it
        if (matches.length > 0) {
            results.push({
                file: filePath,
                keywordsDetected: matches,
                // Capture the first few lines as a preview/epitome of the file
                epitomePreview: content.split('\n').slice(0, 5).join('\n').trim() 
            });
        }
    } catch (error) {
        // Skip binary files or unreadable files silently to maintain clean output
    }
}

// -----------------------------------------------------------------------------
// EXECUTION & REPORT GENERATION
// -----------------------------------------------------------------------------
async function executeForensicMap() {
    console.log('=================================================================');
    console.log(' WILSY OS QUANTUM AI - FORENSIC FILE MAPPER INITIATED');
    console.log(' COLLABORATION: Epitome, biblical worth billions no child\'s place.');
    console.log('=================================================================\n');
    
    const results = [];
    const rootDir = TARGET_DIRECTORIES[0];

    console.log(`[SCANNING] Directory: ${rootDir}`);
    console.log(`[TARGETS] ${KEYWORDS.join(', ')}`);
    
    const startTime = Date.now();
    
    await scanDirectory(rootDir, results);
    
    const endTime = Date.now();
    const duration = ((endTime - startTime) / 1000).toFixed(2);

    const report = {
        scanDate: new Date().toISOString(),
        durationSeconds: duration,
        totalFilesMatched: results.length,
        mappedNodes: results
    };

    const reportPath = path.join(rootDir, 'wilsy-os-ai-map.json');
    await fs.writeFile(reportPath, JSON.stringify(report, null, 4), 'utf-8');

    console.log('\n[SUCCESS] Forensic Mapping Complete.');
    console.log(`[METRICS] Found ${results.length} files containing intelligence keywords in ${duration}s.`);
    console.log(`[OUTPUT] Report saved to: ${reportPath}`);
    console.log('\nReady for next-phase integration. Please provide the JSON output to proceed.');
}

executeForensicMap().catch(console.error);
