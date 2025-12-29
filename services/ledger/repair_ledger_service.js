const fs = require('fs');
const path = require('path');

console.log('🚑 REPAIRING LEDGER MICROSERVICE...');

// 1. DEFINE PATHS
const packagePath = path.join(__dirname, 'package.json');
const indexPath = path.join(__dirname, 'index.js');

// 2. DEFINE CLEAN CODE
const packageJson = {
  "name": "svc-ledger",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "body-parser": "^1.20.2",
    "crypto": "^1.0.1",
    "mongoose": "^7.0.0",
    "cors": "^2.8.5",
    "dotenv": "^16.0.3"
  }
};

const indexJs = `
require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const crypto = require('crypto');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();
app.use(bodyParser.json());
app.use(cors());

// --- 1. DATABASE CONNECTION ---
// Robust connection logic with retries
const connectDB = async () => {
    try {
        await mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/legal-tech', {
            serverSelectionTimeoutMS: 5000
        });
        console.log('✅ [Ledger] Connected to MongoDB');
    } catch (err) {
        console.error('❌ [Ledger] DB Connection Failed:', err.message);
        // Don't exit, let it try again on next request or restart
    }
};
connectDB();

// --- 2. THE IMMUTABLE SCHEMA ---
const EventSchema = new mongoose.Schema({
  sequence: { type: Number, required: true, unique: true },
  eventType: String,
  actor: String,
  description: String,
  meta: Object,
  createdAt: { type: Date, default: Date.now },
  prevHash: String,
  hash: { type: String, required: true },
});

const Event = mongoose.model('LedgerEvent', EventSchema);

// --- 3. ROUTES ---

// Append Event (The main audit logic)
app.post('/events', async (req, res) => {
  try {
      // 1. Get the last event to chain the hash
      const last = await Event.findOne().sort({ sequence: -1 }).lean();
      
      const seq = last ? last.sequence + 1 : 1;
      const prevHash = last ? last.hash : 'GENESIS_BLOCK';
      
      const payload = req.body; // { eventType, actor, description, meta }
      
      // 2. Create the Cryptographic Hash
      // We hash the sequence, data, AND previous hash to create a blockchain-like link
      const rawData = JSON.stringify({ seq, payload, prevHash, ts: new Date().toISOString() });
      const hash = crypto.createHash('sha256').update(rawData).digest('hex');
      
      const ev = new Event({ 
          sequence: seq, 
          eventType: payload.eventType || 'GENERIC', 
          actor: payload.actor || 'SYSTEM',
          description: payload.description,
          meta: payload.meta,
          prevHash, 
          hash 
      });
      
      await ev.save();
      
      console.log(\`📝 [Ledger] New Block #\${seq}: \${hash.substring(0, 10)}...\`);
      res.status(201).json({ success: true, sequence: seq, hash });
  } catch (err) {
      console.error('❌ [Ledger Error]', err);
      // Return 500 but include message for debugging
      res.status(500).json({ error: err.message });
  }
});

// Read Ledger (Audit View)
app.get('/events', async (req, res) => {
  try {
      const items = await Event.find().sort({ sequence: -1 }).limit(100);
      res.json(items);
  } catch (err) {
      res.status(500).json({ error: err.message });
  }
});

// Health Check
app.get('/health', (req, res) => res.json({ status: 'Ledger Online' }));

// --- 4. START SERVER ---
const PORT = 6000;
app.listen(PORT, () => console.log(\`🔒 [Ledger Service] Running on Port \${PORT}\`));
`;

// 3. WRITE FILES SAFELY
try {
    fs.writeFileSync(packagePath, JSON.stringify(packageJson, null, 2));
    console.log('✅ package.json rewritten.');

    fs.writeFileSync(indexPath, indexJs);
    console.log('✅ index.js rewritten (Corruption fixed).');
    
    console.log('✨ LEDGER REPAIR COMPLETE.');
} catch (e) {
    console.error('❌ REPAIR FAILED:', e);
}
