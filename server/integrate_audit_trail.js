const fs = require('fs');
const path = require('path');

console.log('🔗 INTEGRATING DISPATCH ENGINE WITH IMMUTABLE LEDGER...');

const controllerPath = path.join(__dirname, 'controllers/dispatchInstructionController.js');
let code = fs.readFileSync(controllerPath, 'utf8');

// The code we want to inject: A helper that fires-and-forgets a Ledger entry
const ledgerLogic = `
// --- BILLION-DOLLAR AUDIT TRAIL ---
const axios = require('axios');

async function logToLedger(type, actor, desc, meta) {
    try {
        // Fire and forget - don't slow down the main user
        axios.post('http://localhost:6000/events', {
            eventType: type,
            actor: actor,
            description: desc,
            meta: meta
        }).catch(err => console.error('❌ Ledger Sync Failed:', err.message));
    } catch (e) {
        console.error('❌ Ledger Error:', e.message);
    }
}
`;

// We inject this at the top of the file (after imports)
if (!code.includes('logToLedger')) {
    const importEnd = code.indexOf('DispatchInstruction = require');
    code = code.slice(0, importEnd) + ledgerLogic + '\n' + code.slice(viewport = importEnd);
}

// Now we inject the CALL inside createInstruction
// We look for "await instruction.save();"
const hookPoint = "await instruction.save();";
const auditCall = `
    // AUTOMATED AUDIT LOG
    logToLedger(
        'INSTRUCTION_CREATED', 
        'SYSTEM_DISPATCHER', 
        \`Created Case: \${req.body.caseNumber}\`, 
        { instructionId: instruction._id }
    );
`;

if (code.includes('logToLedger(\'INSTRUCTION_CREATED\'')) {
    console.log("ℹ️ Audit Trail already active.");
} else if (code.includes(hookPoint)) {
    code = code.replace(hookPoint, hookPoint + auditCall);
    fs.writeFileSync(controllerPath, code);
    console.log("✅ INTEGRATION COMPLETE: Dispatch Controller now syncs to Ledger.");
} else {
    console.log("❌ Could not find insertion point. Check controller structure.");
}
