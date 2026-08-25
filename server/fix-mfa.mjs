import mongoose from 'mongoose';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import speakeasy from 'speakeasy';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load .env from server directory
dotenv.config({ path: path.join(__dirname, '.env') });

const MONGODB_URI = process.env.MONGODB_URI;
if (!MONGODB_URI) {
  console.error('❌ MONGODB_URI not found in .env');
  process.exit(1);
}

const email = 'wilsonkhanyezi@gmail.com';

async function run() {
  try {
    await mongoose.connect(MONGODB_URI);
    const db = mongoose.connection.db;
    const users = db.collection('users');

    // Generate a new secret
    const secret = speakeasy.generateSecret({ length: 20 });
    const otpauthUrl = secret.otpauth_url;

    // Update the user
    const result = await users.updateOne(
      { email },
      {
        $set: {
          'securityMetadata.mfaSecret': secret.base32,
          'securityMetadata.mfaEnabled': true,
          'securityMetadata.mfaSetupComplete': true,
          twoFactorSecret: secret.base32,
        }
      }
    );
    console.log('✅ MFA updated for', email, 'Modified:', result.modifiedCount);
    console.log('🔑 Secret:', secret.base32);
    console.log('🔗 OTP Auth URL:', otpauthUrl);
    console.log('📱 Scan this QR code or enter the secret manually.');
    console.log('   You can generate a QR code from the URL above.');
    await mongoose.disconnect();
  } catch (err) {
    console.error('❌ Error:', err);
  }
}

run();
