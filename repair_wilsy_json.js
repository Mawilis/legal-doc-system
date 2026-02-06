/*
 * File: server/seedSuper.js
 * STATUS: PRODUCTION-READY | EPITOME
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * Emergency Provisioning of a New Super Admin for Wilsy OS.
 * This script bypasses existing legacy 'admin' records to establish a fresh
 * root identity with 'SUPER_ADMIN' clearance.
 * -----------------------------------------------------------------------------
 * COLLABORATION NOTES:
 * - AUTHOR: Wilson Khanyezi (Chief Architect)
 * - SECURITY: Strict Bcrypt 10-round salting.
 * - INTEGRITY: Uses a unique system email to ensure a clean DB entry.
 * - LINTING: Strict single-quote enforcement.
 * -----------------------------------------------------------------------------
 */
'use strict';
const dotenv = require('dotenv');
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const User = require('./models/userModel');
dotenv.config();
/**
 * seedSuperAdmin()
 * Creates a secondary, unassailable Super Admin record.
 */
async function seedSuperAdmin() {
  console.log('----------------------------------------------------');
  console.log('🏛️ WILSY OS: PARALLEL IDENTITY PROVISIONING');
  console.log('----------------------------------------------------');
  // CRITICAL: Ensure this URI matches the one in your server logs!
  const uri = process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/wilsy';

  // We use a new email to bypass the 'Identity not found' / 'Secret mismatch' loop
  const superEmail = 'architect@wilsy.os';
  const superPassword = 'Mawilis8596'; // CHANGE THIS TO A SECURE PASSWORD BEFORE RUNNING IN PRODUCTION
  const normalizedEmail = superEmail.toLowerCase().trim();
  try {
    console.log(`Connecting to Infrastructure: ${uri}`);
    await mongoose.connect(uri);
    console.log('Database Connected Successfully.');
    // 1. Check for existing super identity
    const existing = await User.findOne({ email: normalizedEmail });
    if (existing) {
      console.log('Identity exists. Deleting to ensure fresh hash injection...');
      await User.deleteOne({ email: normalizedEmail });
    }
    // 2. Cryptographic Preparation
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(superPassword, salt);
    // 3. Injection
    const superAdmin = await User.create({
      name: 'Wilson (Chief Architect)',
      email: normalizedEmail,
      password: hashedPassword,
      role: 'SUPER_ADMIN',
      isActive: true
    });
    console.log('----------------------------------------------------');
    console.log('✅ SUCCESS: NEW SUPER ADMIN PROVISIONED.');
    console.log(`📧 Login Email: ${superAdmin.email}`);
    console.log(`🛡️ Identity Role: ${superAdmin.role}`);
    console.log('----------------------------------------------------');
    console.log('INSTRUCTION: Use these new credentials to login now.');
    console.log('----------------------------------------------------');
  } catch (err) {
    console.error('❌ CRITICAL PROVISIONING ERROR:', err.message);
  } finally {
    await mongoose.disconnect();
    process.exit(0);
  }
}
seedSuperAdmin();