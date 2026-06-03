import mongoose from 'mongoose';
import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import User from './models/userModel.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// 🛡️ INTELLIGENT ENV DISCOVERY: Guarantees we find your auth credentials
if (fs.existsSync(path.join(__dirname, '.env'))) {
    dotenv.config({ path: path.join(__dirname, '.env') });
} else if (fs.existsSync(path.join(__dirname, '../.env'))) {
    dotenv.config({ path: path.join(__dirname, '../.env') });
}

const uri = process.env.MONGO_URI || process.env.DATABASE_URL;

if (!uri) {
    console.error("❌ ERROR: Could not locate database URI. Check your .env file.");
    process.exit(1);
}

mongoose.connect(uri).then(async () => {
  console.log('🔗 Connected to Sovereign DB Kernel...');
  const res = await User.updateOne(
    { email: 'wilsonkhanyezi@gmail.com' },
    {
      $set: { isTwoFactorEnabled: false },
      $unset: { 'securityMetadata.mfaSecret': "" }
    }
  );
  console.log(`✅ MFA NUKE COMPLETE. Old lock destroyed. (Records modified: ${res.modifiedCount})`);
  process.exit(0);
}).catch(err => {
  console.error('❌ DB ERROR:', err.message);
  process.exit(1);
});
