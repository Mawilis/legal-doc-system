const fs = require('fs');
const path = require('path');

console.log('🚑 SURGICAL REPAIR: BILLING SERVICE...');

// We use standard string concatenation (" + var + ") to avoid backtick errors entirely.
const code = `const express = require('express');
const cors = require('cors');
const app = express();

app.use(express.json());
app.use(cors());

const TARIFFS = {
  'service_summons': { base: 180, distanceCap: 15 },
  'urgent_6_12': { base: 450, multiplier: 1.5 },
  'ejectment': { base: 1500, security_surcharge: 400 },
  'per_km': 6.50
};

app.post('/calculate', (req, res) => {
    console.log('💰 [Billing] Calculating Invoice...');
    const { type, distanceKm, isUrgent } = req.body;
    
    let total = 0;
    let lines = [];

    const rule = TARIFFS[type] || { base: 200 };
    
    // 1. Base Fee
    let fee = rule.base;
    if (isUrgent || type === 'urgent_6_12') fee *= 1.5;
    total += fee;
    
    // SAFE SYNTAX: No backticks here
    lines.push({ desc: "Service Fee (" + type + ")", amount: fee });

    // 2. Travel
    if (distanceKm > 0) {
        const travel = distanceKm * TARIFFS.per_km;
        total += travel;
        lines.push({ desc: "Travel (" + distanceKm + "km @ R6.50)", amount: travel });
    }

    // 3. VAT (15%)
    const vat = total * 0.15;
    const grandTotal = total + vat;

    res.json({
        subtotal: total.toFixed(2),
        vat: vat.toFixed(2),
        total: grandTotal.toFixed(2),
        lineItems: lines,
        currency: 'ZAR',
        entity: 'Wilsy Pty Ltd'
    });
});

const PORT = 6400;
app.listen(PORT, '0.0.0.0', () => console.log('💰 [Smart Billing] Online on Port ' + PORT));
`;

fs.writeFileSync(path.join(__dirname, 'services/billing/index.js'), code);
console.log('✅ BILLING SERVICE CODE FIXED.');
