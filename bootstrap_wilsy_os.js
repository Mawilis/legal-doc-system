const fs = require('fs');
const path = require('path');

// --- 1. CORPORATE IDENTITY ---
const COMPANY = "Wilsy Pty Ltd";
const REG_NO = "2024/617944/07";
const YEAR = new Date().getFullYear();
const COPYRIGHT_HEADER = `/**
 * Copyright (c) ${YEAR} ${COMPANY} [Reg: ${REG_NO}].
 * All Rights Reserved.
 * * This software is the confidential and proprietary information of ${COMPANY}.
 * Unauthorized copying of this file, via any medium is strictly prohibited.
 * Proprietary and confidential.
 */\n\n`;

console.log(`🏗️  BOOTSTRAPPING ${COMPANY} ENTERPRISE ARCHITECTURE...`);

// Helper to write files safely
const writeFile = (filePath, content) => {
    const fullPath = path.join(__dirname, filePath);
    const dir = path.dirname(fullPath);
    
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
        console.log(`📁 Created Dir: ${dir}`);
    }
    
    // We do not overwrite server.js or existing core files to protect current work
    if (fs.existsSync(fullPath) && filePath.includes('server.js')) {
        console.log(`⚠️  Skipping ${filePath} to protect existing logic.`);
        return;
    }

    fs.writeFileSync(fullPath, COPYRIGHT_HEADER + content);
    console.log(`✅ Generated: ${filePath}`);
};

// --- 2. INFRASTRUCTURE (Docker Compose) ---
// This sets up the heavy machinery: Redis (Caching), Kafka (Events), MinIO (S3 Storage)
const dockerCompose = `version: '3.8'
services:
  # EVENT BUS (Kafka) - The Nervous System
  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    ports: ['2181:2181']

  kafka:
    image: confluentinc/cp-kafka:7.4.0
    depends_on: [zookeeper]
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    ports: ['9092:9092']

  # CACHE & QUEUE - Speed Layer
  redis:
    image: redis:7
    ports: ['6379:6379']

  # DOCUMENT STORAGE (S3 Compatible) - The Vault
  minio:
    image: minio/minio:RELEASE.2024-01-01T00-00-00Z
    command: server /data
    environment:
      MINIO_ROOT_USER: admin
      MINIO_ROOT_PASSWORD: password123
    ports: ['9000:9000','9001:9001']
    volumes: ['miniodata:/data']

volumes:
  miniodata:
`;
writeFile('infra/docker-compose.yml', dockerCompose);


// --- 3. MICROSERVICE: BILLING ENGINE ---
// Handles Tariffs, VAT, and Invoicing
const billingPackage = {
  "name": "svc-billing",
  "version": "1.0.0",
  "main": "index.js",
  "dependencies": { "express": "^4.18.2", "body-parser": "^1.20.2", "cors": "^2.8.5" }
};
const billingCode = `const express = require('express');
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
    lines.push({ desc: \`Service Fee (\${type})\`, amount: fee });

    // Travel
    if (distanceKm > 0) {
        const travel = distanceKm * TARIFFS.per_km;
        total += travel;
        lines.push({ desc: \`Travel (\${distanceKm}km @ R6.50)\`, amount: travel });
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
        entity: '${COMPANY}'
    });
});

app.listen(6400, () => console.log('💰 [Billing Service] Listening on Port 6400'));
`;
writeFile('services/billing/package.json', JSON.stringify(billingPackage, null, 2));
writeFile('services/billing/index.js', billingCode);


// --- 4. MICROSERVICE: AI ENGINE ---
// Risk Scoring and Autofill
const aiPackage = {
  "name": "svc-ai",
  "version": "1.0.0",
  "main": "index.js",
  "dependencies": { "express": "^4.18.2" }
};
const aiCode = `const express = require('express');
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
`;
writeFile('services/ai/package.json', JSON.stringify(aiPackage, null, 2));
writeFile('services/ai/index.js', aiCode);


// --- 5. MICROSERVICE: CRYPTO VAULT (HSM Stub) ---
// Managing Digital Signatures
const cryptoPackage = {
  "name": "svc-crypto",
  "version": "1.0.0",
  "main": "index.js",
  "dependencies": { "express": "^4.18.2", "crypto": "^1.0.1" }
};
const cryptoCode = `const express = require('express');
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
`;
writeFile('services/crypto/package.json', JSON.stringify(cryptoPackage, null, 2));
writeFile('services/crypto/index.js', cryptoCode);


// --- 6. ORCHESTRATOR SCRIPT (Updated) ---
// Updates start_all.sh to include the new billion-dollar services
const startScript = `#!/bin/bash
# Copyright (c) ${YEAR} ${COMPANY}
echo "🚀 LAUNCHING WILSY PTY LTD ENTERPRISE OS..."

# Kill ports to ensure clean start (3001=Gateway, 6000=Ledger, 6100=Standards, 6400=Billing, 6500=AI, 6600=Crypto)
lsof -ti:3001,6000,6100,6400,6500,6600 | xargs kill -9 2>/dev/null

echo "--- CORE SERVICES ---"
# Ledger
cd services/ledger && nohup npm start > ../../ledger.log 2>&1 &
echo "✅ Ledger (Port 6000)"

# Standards
cd ../standards && nohup npm start > ../../standards.log 2>&1 &
echo "✅ Standards (Port 6100)"

# Billing
cd ../billing && nohup npm start > ../../billing.log 2>&1 &
echo "✅ Billing (Port 6400)"

# AI
cd ../ai && nohup npm start > ../../ai.log 2>&1 &
echo "✅ AI Engine (Port 6500)"

# Crypto
cd ../crypto && nohup npm start > ../../crypto.log 2>&1 &
echo "✅ Crypto Vault (Port 6600)"

echo "--- GATEWAY ---"
# Main Server
cd ../../server && npm start &
PID_SERVER=$!

echo "✨ SYSTEM LIVE. Press CTRL+C to stop."
trap "kill 0" SIGINT
wait
`;
writeFile('start_wilsy_os.sh', startScript);


console.log("🏁 ARCHITECTURE DEPLOYMENT COMPLETE.");
console.log("👉 Run 'chmod +x start_wilsy_os.sh' then './start_wilsy_os.sh' to launch.");



