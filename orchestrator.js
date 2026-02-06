/**
 * File: orchestrator.js
 * -----------------------------------------------------------------------------
 * STATUS: PRODUCTION-READY | The General (System Commander)
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - Manages the lifecycle of the entire Legal OS.
 * - Spawns the API Gateway (High Priority) and Worker Nodes (Low Priority).
 * - SELF-HEALING: Automatically restarts any service that crashes.
 * -----------------------------------------------------------------------------
 */

'use strict';

const { fork } = require('child_process');
const path = require('path');

// --- CONFIGURATION ---
const RESTART_DELAY_MS = 3000;
const SERVICES = [
    {
        name: 'GATEWAY',
        script: './server/server.js',
        color: '\x1b[36m', // Cyan
        instances: 1
    },
    {
        name: 'WORKER',
        script: './server/jobs/workerEntry.js', // Points to the file we just made
        color: '\x1b[35m', // Magenta
        instances: 1 // Scale this up for more PDF power
    }
];

const processes = {};

/**
 * 🚀 spawnService
 * Launches a child process with color-coded logging and crash recovery.
 */
const spawnService = (service, index = 0) => {
    const scriptPath = path.resolve(__dirname, service.script);
    const processName = `${service.name}-${index}`;
    const prefix = `${service.color}[${processName}]\x1b[0m`;

    console.log(`[Orchestrator] 🚀 Launching ${processName}...`);

    // Fork allows Node-to-Node IPC (Inter-Process Communication)
    const child = fork(scriptPath, [], {
        env: { ...process.env, SERVICE_NAME: processName },
        silent: true // Capture stdout/stderr manually for coloring
    });

    processes[child.pid] = { service, index, name: processName };

    // --- LOG PIPING ---
    child.stdout.on('data', (data) => {
        const lines = data.toString().trim().split('\n');
        lines.forEach(line => console.log(`${prefix} ${line}`));
    });

    child.stderr.on('data', (data) => {
        const lines = data.toString().trim().split('\n');
        lines.forEach(line => console.error(`${prefix} ❌ ${line}`));
    });

    // --- CRASH HANDLER (Self-Healing) ---
    child.on('exit', (code) => {
        if (code !== 0 && code !== null) {
            console.error(`[Orchestrator] ⚠️ ${processName} died (Code: ${code}). Respawning in ${RESTART_DELAY_MS}ms...`);
            setTimeout(() => spawnService(service, index), RESTART_DELAY_MS);
        } else {
            console.log(`[Orchestrator] 🛑 ${processName} stopped gracefully.`);
        }
    });
};

// --- BOOT SEQUENCE ---
console.clear();
console.log('\x1b[1m\x1b[34m'); // Blue Bold
console.log('------------------------------------------------');
console.log('   WILSY OS | BILLION DOLLAR ARCHITECTURE       ');
console.log('   System Orchestrator Online                   ');
console.log('------------------------------------------------');
console.log('\x1b[0m'); // Reset

SERVICES.forEach(service => {
    for (let i = 0; i < service.instances; i++) {
        spawnService(service, i);
    }
});

// Handle Orchestrator Shutdown
process.on('SIGINT', () => {
    console.log('\n[Orchestrator] 🛑 Shutting down cluster...');
    Object.keys(processes).forEach(pid => process.kill(pid));
    process.exit();
});



