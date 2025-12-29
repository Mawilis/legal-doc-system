
const { spawn } = require('child_process');
const path = require('path');

const services = [
    { name: 'Gateway',   folder: 'server',             port: 3001, color: '\x1b[37m' },
    { name: 'Auth',      folder: 'services/auth',      port: 4000, color: '\x1b[32m' },
    { name: 'Billing',   folder: 'services/billing',   port: 6400, color: '\x1b[32m' },
    { name: 'AI Engine', folder: 'services/ai',        port: 6500, color: '\x1b[35m' },
    { name: 'Ledger',    folder: 'services/ledger',    port: 6000, color: '\x1b[33m' }
];

services.forEach(svc => {
    const child = spawn('npm', ['start'], {
        cwd: path.join(__dirname, svc.folder),
        shell: true,
        env: { ...process.env, PORT: svc.port }
    });
    child.stdout.on('data', d => console.log(svc.color + '[' + svc.name + '] ' + '\x1b[0m' + d.toString().trim()));
    child.stderr.on('data', d => console.error(svc.color + '[' + svc.name + ' ERR] ' + '\x1b[0m' + d.toString().trim()));
});
