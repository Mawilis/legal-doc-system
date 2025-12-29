const express = require('express');
const mongoose = require('mongoose');
const crypto = require('crypto');
const cors = require('cors');
const app = express();

// Allowed origins - same as auth
const ALLOWED_ORIGINS = process.env.CORS_ORIGINS ? process.env.CORS_ORIGINS.split(',') : ['http://localhost:3000'];

app.use(cors({
  origin: function(origin, callback) {
    if (!origin) return callback(null, true);
    if (ALLOWED_ORIGINS.includes('*') || ALLOWED_ORIGINS.includes(origin)) return callback(null, true);
    return callback(new Error('CORS policy: Origin not allowed'));
  },
  credentials: true,
  methods: ['GET','POST','OPTIONS'],
  allowedHeaders: ['Content-Type','Authorization','x-request-id','x-tenant-id']
}));
app.options('*', (req, res) => res.sendStatus(204));
app.use(express.json());

mongoose.connect('mongodb://127.0.0.1:27017/legal-tech')
    .then(() => console.log('✅ [Ledger] CONNECTED TO MONGODB'))
    .catch(err => console.error('❌ [Ledger] DB ERROR:', err));

app.post('/events', async (req, res) => {
    // Minimal example: compute a hash and return success
    try {
      const payload = req.body || {};
      const raw = JSON.stringify({ payload, ts: new Date().toISOString() });
      const hash = crypto.createHash('sha256').update(raw).digest('hex');
      // In production you would persist the event with sequence and prevHash
      return res.status(201).json({ status: "Sealed", brand: "Wilsy", hash });
    } catch (err) {
      return res.status(500).json({ error: err.message });
    }
});

const PORT = process.env.LEDGER_PORT || 6000;
app.listen(PORT, () => console.log(`🔒 [Ledger] Secure Ledger Online (Port ${PORT})`));
