import mongoose from 'mongoose';
import dotenv from 'dotenv';
import User from './models/userModel.js';
import chalk from 'chalk';

dotenv.config();

const resetMFA = async () => {
  try {
    if (!process.env.MONGODB_URI) {
      throw new Error('MONGODB_URI is missing from environment.');
    }

    await mongoose.connect(process.env.MONGODB_URI);
    console.log(chalk.cyan('📡 Connected to Sovereign Nucleus...'));

    const email = 'wilsonkhanyezi@gmail.com';
    const result = await User.findOneAndUpdate(
      { email },
      {
        isTwoFactorEnabled: false,
        'securityMetadata.mfaEnabled': false
      },
      { new: true }
    );

    if (!result) {
      console.log(chalk.red('🚨 Identity Shard not found.'));
    } else {
      console.log(chalk.green('\n=========================================================='));
      console.log(chalk.green('✅ MFA FLAG DEACTIVATED FOR FOUNDER'));
      console.log(chalk.green('🚀 Status: Ready for Fresh Genesis Login'));
      console.log(chalk.green('==========================================================\n'));
    }

    process.exit(0);
  } catch (error) {
    console.error(chalk.red('💥 Connection Fracture:'), error.message);
    process.exit(1);
  }
};

resetMFA();
