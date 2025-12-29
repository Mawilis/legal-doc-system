const fs = require('fs');

console.log("🛠️  GENERATING ORCHESTRATOR...");

// The clean, simple Orchestrator code
const orchestratorCode = `
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

console.log('\\n🚀 WILSY PTY LTD - ENTERPRISE LAUNCHER...\\n');

const services = [
    { name: 'Gateway',   folder: 'server',             port: 3001, color: '\\x1b[37m' }, // White
    { name: 'Billing',   folder: 'services/billing',   port: 6400, color: '\\x1b[32m' }, // Green
    { name: 'AI Engine', folder: 'services/ai',        port: 6500, color: '\\x1b[35m' }, // Magenta
    { name: 'Crypto',    folder: 'services/crypto',    port: 6600, color: '\\x1b[36m' }, // Cyan
    { name: 'Ledger',    folder: 'services/ledger',    port: 6000, color: '\\x1b[33m' }, // Yellow
    { name: 'Standards', folder: 'services/standards', port: 6100, color: '\\x1b[34m' }  // Blue
];

// 1. CLEANUP PORTS
try {
    const ports = services.map(s => s.port).join(',');
    require('child_process').execSync('lsof -ti:' + ports + ' | xargs kill -9 2>/dev/null');
    console.log('🧹 Ports cleaned.');
} catch (e) {}

// 2. START SERVICES
services.forEach(svc => {
    const cwd = path.join(__dirname, svc.folder);
    
    // Skip if folder missing
    if (!fs.existsSync(cwd)) return;

    console.log('⏳ Starting ' + svc.name + '...');

    const child = spawn('npm', ['start'], {
        cwd: cwd,
        shell: true,
        env: { ...process.env, PORT: svc.port }
    });

    // Simple Log Stream
    child.stdout.on('data', d => {
        const msg = d.toString().trim();
        if(msg) console.log(svc.color + '[' + svc.name + '] ' + '\\x1b[0m' + msg);
    });
    
    child.stderr.on('data', d => {
        const msg = d.toString().trim();
        if(msg) console.error(svc.color + '[' + svc.name + ' ERR] ' + '\\x1b[0m' + msg);
    });
});
`;

fs.writeFileSync('orchestrator.js', orchestratorCode);
console.log("✅ SUCCESS: orchestrator.js created.");
