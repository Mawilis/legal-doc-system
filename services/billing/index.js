/**
 * Copyright (c) 2026 Wilsy Pty Ltd [Reg: 2024/617944/07].
 * All Rights Reserved.
 * * This software is the confidential and proprietary information of Wilsy Pty Ltd.
 * Unauthorized copying of this file, via any medium is strictly prohibited.
 * Proprietary and confidential.
 */

const express = require('express');
const app = express();
app.use(express.json());

// TARIFF MATRIX (South African Sheriff Board Standards)
const TARIFFS = {
  'service_summons': { base: 180, distanceCap: 15 },
  'urgent_6_12': { base: 450, multiplier: 1.5 },
  'ejectment': { base: 1500, security_surcharge: 400 },
  'per_km': 6.50
};

app.post('/calculate', (req, res) => {
    const { type, distanceKm, isUrgent } = req.body;
    let total = 0;
    let lines = [];

    const rule = TARIFFS[type] || { base: 200 };
    
    // Base Fee
    let fee = rule.base;
    if (isUrgent || type === 'urgent_6_12') fee *= 1.5;
    total += fee;
    lines.push({ desc: `Service Fee (${type})`, amount: fee });

    // Travel
    if (distanceKm > 0) {
        const travel = distanceKm * TARIFFS.per_km;
        total += travel;
        lines.push({ desc: `Travel (${distanceKm}km @ R6.50)`, amount: travel });
    }

    // VAT (15%)
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

app.listen(6400, () => console.log('💰 [Billing Service] Listening on Port 6400'));
