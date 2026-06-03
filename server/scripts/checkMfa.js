import mongoose from 'mongoose';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import User from '../models/userModel.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.join(__dirname, '../.env') });

mongoose.connect(process.env.MONGO_URI || process.env.DATABASE_URL || 'mongodb://127.0.0.1:27017/wilsy_os').then(async () => {
  const user = await User.findOne({ email: 'wilsonkhanyezi@gmail.com' }).select('+securityMetadata.mfaSecret');
  console.log('\n--- 🔍 DEEPSEEK DIAGNOSTIC: DB MFA STATUS ---');
  console.log('Identity:', user?.email || 'NOT FOUND');
  console.log('MFA Secret Saved?:', user?.securityMetadata?.mfaSecret ? '✅ YES (' + user.securityMetadata.mfaSecret.substring(0,5) + '...)' : '❌ MISSING');
  console.log('2FA Status:', user?.isTwoFactorEnabled ? '✅ ENABLED' : '❌ DISABLED');
  console.log('---------------------------------------------\n');
  process.exit(0);
}).catch(err => {
  console.error('DB Connection Failed:', err.message);
  process.exit(1);
});
