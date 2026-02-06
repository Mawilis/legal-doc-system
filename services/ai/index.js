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

app.post('/risk-score', (req, res) => {
    const { area, crimeStats, defendantHistory } = req.body;
    
    // Simulation of a Trained ML Model
    let score = 0.1; // Low risk default
    if (area === 'Red Zone') score += 0.4;
    if (defendantHistory === 'Hostile') score += 0.4;
    
    const riskLevel = score > 0.7 ? 'HIGH' : (score > 0.4 ? 'MEDIUM' : 'LOW');
    
    res.json({
        score: score.toFixed(2),
        riskLevel,
        recommendation: riskLevel === 'HIGH' ? 'Requires SAPS Escort' : 'Standard Service',
        model_version: 'v1.0.2-wilsy'
    });
});

app.listen(6500, () => console.log('🤖 [AI Service] Listening on Port 6500'));
