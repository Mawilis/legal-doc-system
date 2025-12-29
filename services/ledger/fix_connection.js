const fs = require('fs');
const path = require('path');

console.log('🚑 APPLYING IPV4 CONNECTION PATCH...');

const indexPath = path.join(__dirname, 'index.js');
let code = fs.readFileSync(indexPath, 'utf8');

// REPLACE 'localhost' with '127.0.0.1' to force IPv4
const oldString = "mongodb://localhost:27017/legal-tech";
const newString = "mongodb://127.0.0.1:27017/legal-tech";

if (code.includes(oldString)) {
    code = code.replace(oldString, newString);
    fs.writeFileSync(indexPath, code);
    console.log('✅ FIXED: Forced Ledger to use 127.0.0.1 (IPv4).');
} else if (code.includes(newString)) {
    console.log('ℹ️ Already patched.');
} else {
    console.log('⚠️ Could not find connection string. Replacing entire file to be safe.');
    
    // Fallback: Rewrite the file with the correct IP if replace fails
    const fixedCode = `
require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const crypto = require('crypto');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();
app.use(bodyParser.json());
app.use(cors());

// --- 1. DATABASE CONNECTION (FIXED) ---
const connectDB = async () => {
    try {
        // FORCE 127.0.0.1 to avoid Mac IPv6 issues
        await mongoose.connect(process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/legal-tech', {
            serverSelectionTimeoutMS: 5000
        });
        console.log('✅ [Ledger] Connected to MongoDB');
    } catch (err) {
        console.error('❌ [Ledger] DB Connection Failed:', err.message);
    }
};
connectDB();

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

app.post('/events', async (req, res) => {
  try {
      const last = await Event.findOne().sort({ sequence: -1 }).lean();
      const seq = last ? last.sequence + 1 : 1;
      const prevHash = last ? last.hash : 'GENESIS_BLOCK';
      const payload = req.body;
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
      res.status(500).json({ error: err.message });
  }
});

app.get('/events', async (req, res) => {
  try {
      const items = await Event.find().sort({ sequence: -1 }).limit(100);
      res.json(items);
  } catch (err) {
      res.status(500).json({ error: err.message });
  }
});

app.get('/health', (req, res) => res.json({ status: 'Ledger Online' }));

const PORT = 6000;
app.listen(PORT, () => console.log(\`🔒 [Ledger Service] Running on Port \${PORT}\`));
`;
    fs.writeFileSync(indexPath, fixedCode);
    console.log('✅ RE-WROTE INDEX.JS WITH IPV4 FIX.');
}
