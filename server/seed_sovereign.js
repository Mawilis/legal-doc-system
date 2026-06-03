/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - DATABASE ANCHOR SEED [V1.0.0-SINGULARITY]                                                                                   ║
 * ║ [PROTOCOL: SOVEREIGN IDENTITY ANCHORING | MASTER DB STRIKE | BILLION DOLLAR SPEC]                                                      ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.0.0 | PRODUCTION READY | BIBLICAL WORTH BILLIONS                                                                            ║
 * ║ EPITOME: BIBLICAL WORTH BILLIONS | NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                          ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */
import mongoose from 'mongoose';
import User from './models/userModel.js';
import dotenv from 'dotenv';

dotenv.config();

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/legal-doc-system';
const PUBLIC_KEY = `-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqIuLlTbS7fk8KBV1tkez
Nz9y5vUs3Cu609wRmUxMFsHghMjpgDNhwKWmgjEA6qAvDIcYFUGGArD0sEPIsfH8
cH+ZLnFkRh1NmvUKcteSZ7O/iV3+FxLzuc82fLYFoYQxQZyHFzr91OWyqjE1EKCE
+/r28Cz+naOXQNmIAZgdCIkA3Zb7yIKWmV33VoVTVMmkeqPYwVDi3G42eHJhgH4f
LwOobpNJZonWUnf/uYfGYzZek9zOlHBZYbWXn1FFAGmOOVHH0ucFKObxoIXX+rQY
JqibEII2lkPpoYE/CHCEkmsOCteW78PRj4ZzL8svD5pMAu+KsrdQzTIPKQLBlpSg
0QIDAQAB
-----END PUBLIC KEY-----`;

async function seed() {
  try {
    await mongoose.connect(MONGODB_URI);
    console.log('✅ DATABASE NUCLEUS ONLINE');

    const user = await User.findOneAndUpdate(
      { email: 'wilsonkhanyezi@gmail.com' },
      {
        'biometric.biometricAnchor': PUBLIC_KEY,
        'biometric.registered': true,
        'isTwoFactorEnabled': true
      },
      { new: true }
    );

    if (user) {
      console.log('✅ SOVEREIGN ANCHOR PLACED FOR: wilsonkhanyezi@gmail.com');
      process.exit(0);
    } else {
      console.error('❌ IDENTITY NOT FOUND IN DB');
      process.exit(1);
    }
  } catch (err) {
    console.error('❌ DB STRIKE FAILED:', err.message);
    process.exit(1);
  }
}

seed();
