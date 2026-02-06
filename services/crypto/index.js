/**
 * Copyright (c) 2026 Wilsy Pty Ltd [Reg: 2024/617944/07].
 * All Rights Reserved.
 * * This software is the confidential and proprietary information of Wilsy Pty Ltd.
 * Unauthorized copying of this file, via any medium is strictly prohibited.
 * Proprietary and confidential.
 */

const express = require('express');
const crypto = require('crypto');
const app = express();
app.use(express.json());

// In production, this connects to AWS KMS or Azure Key Vault
app.post('/sign-document', (req, res) => {
    const { documentHash, tenantId } = req.body;
    
    // Simulating a High-Security Module (HSM) signature
    const signer = crypto.createSign('SHA256');
    signer.update(documentHash);
    signer.update(process.env.HSM_SECRET || 'wilsy-master-key');
    const signature = signer.sign(crypto.createPrivateKey({
        key: require('crypto').generateKeyPairSync('rsa', {modulusLength: 2048}).privateKey,
        format: 'pem',
        type: 'pkcs1'
    }), 'hex');

    res.json({
        signature,
        algorithm: 'RSA-SHA256',
        timestamp: new Date().toISOString(),
        provider: 'Wilsy-Vault-v1'
    });
});

app.listen(6600, () => console.log('🔐 [Crypto Vault] Listening on Port 6600'));
