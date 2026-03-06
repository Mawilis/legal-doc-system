#!/usr/bin/env node
/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ GENERATE FOUNDER KEYS - WILSY OS CITADEL                                  ║
  ║ Creates real RSA key pairs for founder signatures                        ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import crypto from 'crypto';
import fs from 'fs/promises';
import path from 'path';
import chalk from 'chalk';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function generateFounderKeys() {
  console.log(chalk.yellow('\n🔐 GENERATING FOUNDER CRYPTOGRAPHIC KEYS'));
  console.log(chalk.yellow('=========================================\n'));

  // Create founder certificates directory
  const founderDir = path.join(__dirname, '../../certificates/founder');
  await fs.mkdir(founderDir, { recursive: true });

  // Generate Founder 1 keys
  console.log(chalk.blue('Generating Founder 1 keys...'));
  const { publicKey: pub1, privateKey: priv1 } = crypto.generateKeyPairSync('rsa', {
    modulusLength: 4096,
    publicKeyEncoding: {
      type: 'spki',
      format: 'pem'
    },
    privateKeyEncoding: {
      type: 'pkcs8',
      format: 'pem',
      cipher: 'aes-256-cbc',
      passphrase: process.env.FOUNDER_KEY_PASSPHRASE || 'change-this-in-production'
    }
  });

  await fs.writeFile(path.join(founderDir, 'founder1-public.pem'), pub1);
  await fs.writeFile(path.join(founderDir, 'founder1-private.pem'), priv1);
  console.log(chalk.green('✅ Founder 1 keys generated'));

  // Generate Founder 2 keys
  console.log(chalk.blue('Generating Founder 2 keys...'));
  const { publicKey: pub2, privateKey: priv2 } = crypto.generateKeyPairSync('rsa', {
    modulusLength: 4096,
    publicKeyEncoding: {
      type: 'spki',
      format: 'pem'
    },
    privateKeyEncoding: {
      type: 'pkcs8',
      format: 'pem',
      cipher: 'aes-256-cbc',
      passphrase: process.env.FOUNDER_KEY_PASSPHRASE || 'change-this-in-production'
    }
  });

  await fs.writeFile(path.join(founderDir, 'founder2-public.pem'), pub2);
  await fs.writeFile(path.join(founderDir, 'founder2-private.pem'), priv2);
  console.log(chalk.green('✅ Founder 2 keys generated'));

  // Generate backup keys
  console.log(chalk.blue('Generating backup keys...'));
  const { publicKey: pubBackup, privateKey: privBackup } = crypto.generateKeyPairSync('rsa', {
    modulusLength: 4096,
    publicKeyEncoding: {
      type: 'spki',
      format: 'pem'
    },
    privateKeyEncoding: {
      type: 'pkcs8',
      format: 'pem',
      cipher: 'aes-256-cbc',
      passphrase: process.env.FOUNDER_KEY_PASSPHRASE || 'change-this-in-production'
    }
  });

  await fs.writeFile(path.join(founderDir, 'backup-public.pem'), pubBackup);
  await fs.writeFile(path.join(founderDir, 'backup-private.pem'), privBackup);
  console.log(chalk.green('✅ Backup keys generated'));

  // Generate .env format
  const envFormat = `
# ============================================================================
# FOUNDER CRYPTOGRAPHIC KEYS - GENERATED $(new Date().toISOString())
# WARNING: Keep these secure! Never commit to version control.
# ============================================================================

FOUNDER_PUBLIC_KEY_1="${pub1.replace(/\n/g, '\\n')}"
FOUNDER_PUBLIC_KEY_2="${pub2.replace(/\n/g, '\\n')}"
FOUNDER_BACKUP_PUBLIC_KEY="${pubBackup.replace(/\n/g, '\\n')}"

# Key fingerprints for verification
FOUNDER_KEY1_FINGERPRINT=$(crypto.createHash('sha256').update(pub1).digest('hex'))
FOUNDER_KEY2_FINGERPRINT=$(crypto.createHash('sha256').update(pub2).digest('hex'))
FOUNDER_BACKUP_FINGERPRINT=$(crypto.createHash('sha256').update(pubBackup).digest('hex'))
`;

  await fs.writeFile(path.join(founderDir, 'founder-keys.env'), envFormat);

  // Generate fingerprint report
  const fingerprint1 = crypto.createHash('sha256').update(pub1).digest('hex');
  const fingerprint2 = crypto.createHash('sha256').update(pub2).digest('hex');
  const fingerprintBackup = crypto.createHash('sha256').update(pubBackup).digest('hex');

  console.log(chalk.yellow('\n📋 KEY FINGERPRINTS:'));
  console.log(chalk.blue(`Founder 1: ${fingerprint1}`));
  console.log(chalk.blue(`Founder 2: ${fingerprint2}`));
  console.log(chalk.blue(`Backup:    ${fingerprintBackup}`));

  console.log(chalk.yellow('\n📍 Key locations:'));
  console.log(`   ${path.join(founderDir, 'founder1-public.pem')}`);
  console.log(`   ${path.join(founderDir, 'founder1-private.pem')}`);
  console.log(`   ${path.join(founderDir, 'founder2-public.pem')}`);
  console.log(`   ${path.join(founderDir, 'founder2-private.pem')}`);
  console.log(`   ${path.join(founderDir, 'backup-public.pem')}`);
  console.log(`   ${path.join(founderDir, 'backup-private.pem')}`);
  console.log(`   ${path.join(founderDir, 'founder-keys.env')}`);

  console.log(chalk.green('\n✅ Founder keys generated successfully!'));
  console.log(chalk.red('\n⚠️  WARNING: Store private keys offline in a secure vault!'));
  console.log(chalk.red('   Never commit private keys to version control.'));
}

generateFounderKeys().catch(console.error);
