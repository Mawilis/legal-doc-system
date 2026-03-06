#!/usr/bin/env node
/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ VERIFY ADMIN CHAIN - WILSY OS CITADEL                                     ║
  ║ Forensic chain verification tool for Super-Admins                        ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import mongoose from 'mongoose';
import { SuperAdmin } from '../models/SuperAdmin.js';
import dotenv from 'dotenv';
import chalk from 'chalk';
import Table from 'cli-table3';
import { program } from 'commander';
import crypto from 'crypto';

dotenv.config();

program
  .version('1.0.0')
  .description('WILSY OS - Super-Admin Forensic Chain Verification');

program
  .command('admin <adminId>')
  .description('Verify entire forensic chain for an admin')
  .option('-v, --verbose', 'Show detailed chain entries')
  .option('-l, --last <number>', 'Show last N entries', parseInt)
  .action(async (adminId, options) => {
    try {
      await mongoose.connect(process.env.MONGODB_URI);

      const admin = await SuperAdmin.findOne({ adminId });
      if (!admin) {
        console.error(chalk.red(`❌ Admin not found: ${adminId}`));
        process.exit(1);
      }

      console.log(chalk.yellow('\n🔐 FORENSIC CHAIN VERIFICATION'));
      console.log(chalk.yellow('================================\n'));

      console.log(chalk.blue(`Admin: ${admin.identity.email} (${admin.adminId})`));
      console.log(chalk.blue(`Status: ${admin.status}`));
      console.log(chalk.blue(`Chain Length: ${admin.forensicChain.length} entries\n`));

      const result = admin.verifyChain();

      if (result.valid) {
        console.log(chalk.green('✅ Chain integrity: VALID'));
      } else {
        console.log(chalk.red(`❌ Chain broken at index ${result.brokenAt}: ${result.reason}`));
      }

      if (options.verbose) {
        console.log(chalk.yellow('\n📋 Chain Details:\n'));

        let entries = admin.forensicChain;
        if (options.last) {
          entries = entries.slice(-options.last);
        }

        const table = new Table({
          head: ['Index', 'Action', 'Timestamp', 'Hash (first 8)'],
          colWidths: [8, 20, 25, 15]
        });

        entries.forEach(entry => {
          table.push([
            entry.index,
            entry.action,
            new Date(entry.timestamp).toLocaleString(),
            entry.currentHash.substring(0, 8) + '...'
          ]);
        });

        console.log(table.toString());
      }

      // Verify final hash
      const lastEntry = admin.forensicChain[admin.forensicChain.length - 1];
      if (lastEntry.currentHash !== admin.forensicHash) {
        console.log(chalk.red(`❌ Final hash mismatch!`));
        console.log(`   Stored: ${admin.forensicHash.substring(0, 16)}...`);
        console.log(`   Chain:  ${lastEntry.currentHash.substring(0, 16)}...`);
      } else {
        console.log(chalk.green(`✅ Final hash matches`));
      }

      await mongoose.disconnect();

    } catch (error) {
      console.error(chalk.red(`Error: ${error.message}`));
      process.exit(1);
    }
  });

program
  command('block <adminId> <index>')
  .description('Verify specific block in chain')
  .action(async (adminId, index) => {
    try {
      await mongoose.connect(process.env.MONGODB_URI);

      const admin = await SuperAdmin.findOne({ adminId });
      if (!admin) {
        console.error(chalk.red(`❌ Admin not found: ${adminId}`));
        process.exit(1);
      }

      const block = admin.forensicChain.find(e => e.index === parseInt(index));
      if (!block) {
        console.error(chalk.red(`❌ Block ${index} not found`));
        process.exit(1);
      }

      console.log(chalk.yellow('\n🔍 BLOCK DETAILS'));
      console.log(chalk.yellow('================\n'));

      console.log(chalk.blue(`Index: ${block.index}`));
      console.log(chalk.blue(`Action: ${block.action}`));
      console.log(chalk.blue(`Timestamp: ${new Date(block.timestamp).toISOString()}`));
      console.log(chalk.blue(`Previous Hash: ${block.previousHash}`));
      console.log(chalk.blue(`Current Hash: ${block.currentHash}`));
      console.log(chalk.blue(`Metadata: ${JSON.stringify(block.metadata, null, 2)}`));

      // Verify this block
      const recomputedHash = crypto
        .createHash('sha256')
        .update(JSON.stringify({
          index: block.index,
          action: block.action,
          metadata: block.metadata,
          adminId: admin.adminId,
          previousHash: block.previousHash,
          timestamp: new Date(block.timestamp).getTime()
        }))
        .digest('hex');

      if (recomputedHash === block.currentHash) {
        console.log(chalk.green(`\n✅ Block hash: VALID`));
      } else {
        console.log(chalk.red(`\n❌ Block hash: INVALID`));
        console.log(`   Computed: ${recomputedHash.substring(0, 16)}...`);
        console.log(`   Stored:   ${block.currentHash.substring(0, 16)}...`);
      }

      await mongoose.disconnect();

    } catch (error) {
      console.error(chalk.red(`Error: ${error.message}`));
      process.exit(1);
    }
  });

program.parse(process.argv);
