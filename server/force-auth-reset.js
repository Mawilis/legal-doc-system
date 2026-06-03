import mongoose from 'mongoose';
import bcrypt from 'bcrypt';
import dotenv from 'dotenv';
dotenv.config();

async function forceAuthReset() {
  try {
    console.log('📡 Connecting to Sovereign Database...');

    const mongoUri = process.env.MONGODB_URI || 'mongodb://localhost:27017/wilsy-os';
    await mongoose.connect(mongoUri);

    const plainTextPassword = 'Wilsy2026Secure';
    const saltRounds = 10;
    const newHashedPassword = await bcrypt.hash(plainTextPassword, saltRounds);

    console.log('🔐 Generated new cryptographic hash for Siyabonga.');
    console.log('Hash:', newHashedPassword);

    const db = mongoose.connection.collection('users');

    const result = await db.updateOne(
      { email: 'wilsy.wk@gmail.com' },
      {
        $set: {
          password: newHashedPassword,
          'securityMetadata.failedLoginAttempts': 0,
          'securityMetadata.lockedUntil': null,
          isActive: true,
          emailVerified: true
        }
      }
    );

    console.log('✅ Update Acknowledged:', result.acknowledged);
    console.log('✅ Matched:', result.matchedCount);
    console.log('✅ Modified:', result.modifiedCount);

    if (result.matchedCount === 0) {
      console.log('⚠️ User not found! Creating user...');
      await db.insertOne({
        email: 'wilsy.wk@gmail.com',
        password: newHashedPassword,
        firstName: 'Siyabonga',
        lastName: 'Khanyezi',
        role: 'sales_representative',
        tenantId: 'MASTER',
        permissions: ['view_revenue', 'view_forecasts', 'view_risk', 'export_reports', 'view_tenant_dashboard', 'view_user_activity'],
        emailVerified: true,
        isActive: true,
        securityMetadata: { failedLoginAttempts: 0, lockedUntil: null },
        createdAt: new Date(),
        updatedAt: new Date()
      });
      console.log('✅ User created successfully');
    }

    console.log('\n🚀 Siyabonga can now log in using:');
    console.log('   SOVEREIGN IDENTIFIER: wilsy.wk@gmail.com');
    console.log('   QUANTUM CREDENTIAL:   Wilsy2026Secure');

    await mongoose.disconnect();
    process.exit(0);
  } catch (error) {
    console.error('❌ Sovereign Auth Reset Failed:', error);
    process.exit(1);
  }
}

forceAuthReset();
