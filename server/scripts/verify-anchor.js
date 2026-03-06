#!/usr/bin/env node
/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ VERIFY ANCHOR SCRIPT - PRODUCTION GRADE                                   ║
  ║ CLI tool for verifying blockchain anchors                                 ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import { program } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import Table from 'cli-table3';
import mongoose from 'mongoose';
import dotenv from 'dotenv';
import BlockchainAnchor from '../models/BlockchainAnchor.js';
import blockchainService from '../services/blockchainService.js';
import { verifyProofOfExistence } from '../utils/blockchainCrypto.js';

dotenv.config();

program
  .version('1.0.0')
  .description('WILSY OS - Anchor Verification CLI');

program
  .command('verify <anchorId>')
  .description('Verify a blockchain anchor')
  .option('--deep', 'Perform deep blockchain verification', false)
  .action(async (anchorId, options) => {
    const spinner = ora('Verifying anchor...').start();

    try {
      await mongoose.connect(process.env.MONGODB_URI);

      const anchor = await BlockchainAnchor.findOne({ anchorId });
      if (!anchor) {
        throw new Error(`Anchor not found: ${anchorId}`);
      }

      spinner.text = 'Verifying on Hyperledger...';

      const verification = await blockchainService.verifyTransaction(
        anchor.transactionId
      );

      const proof = {
        documentHash: anchor.documentHash,
        timestamp: anchor.audit.anchoredAt?.getTime(),
        anchorId: anchor.anchorId,
        signature: anchor.signature
      };

      const cryptoValid = verifyProofOfExistence(
        proof,
        process.env.BLOCKCHAIN_PUBLIC_KEY
      );

      anchor.verificationChecks = [{
        check: 'blockchain-verification',
        passed: verification.verified,
        details: verification.details,
        timestamp: new Date()
      }];

      if (verification.verified) {
        anchor.status = 'verified';
        anchor.verifiedAt = new Date();
        anchor.verifiedBy = 'cli';
        await anchor.save();
      }

      spinner.succeed(chalk.green('Verification complete!'));

      const table = new Table({
        head: ['Check', 'Result', 'Details'],
        colWidths: [20, 15, 45]
      });

      table.push(
        ['Anchor Exists', anchor ? '✅' : '❌', anchorId],
        ['Blockchain Verification', verification.verified ? '✅' : '❌', verification.details],
        ['Cryptographic Proof', cryptoValid ? '✅' : '❌', cryptoValid ? 'Valid' : 'Invalid'],
        ['Hash Integrity', anchor.verifyIntegrity() ? '✅' : '❌', anchor.verifyIntegrity() ? 'Match' : 'Mismatch']
      );

      console.log(table.toString());

      if (options.deep) {
        console.log('\n' + chalk.cyan('Deep Verification Results:'));
        console.log(JSON.stringify(verification, null, 2));
      }

    } catch (error) {
      spinner.fail(chalk.red(`Failed: ${error.message}`));
      process.exit(1);
    } finally {
      await mongoose.disconnect();
    }
  });

program
  .command('check <documentId>')
  .description('Check all anchors for a document')
  .option('-t, --tenant <tenantId>', 'Tenant ID')
  .action(async (documentId, options) => {
    const spinner = ora('Checking document anchors...').start();

    try {
      await mongoose.connect(process.env.MONGODB_URI);

      const anchors = await BlockchainAnchor.find({
        documentId,
        tenantId: options.tenant || 'default'
      }).sort({ 'audit.createdAt': -1 });

      spinner.succeed(chalk.green(`Found ${anchors.length} anchors`));

      const table = new Table({
        head: ['Anchor ID', 'Status', 'Transaction ID', 'Block', 'Timestamp'],
        colWidths: [20, 12, 40, 10, 25]
      });

      anchors.forEach(anchor => {
        table.push([
          anchor.anchorId,
          anchor.status,
          anchor.transactionId?.slice(0, 20) + '...' || 'N/A',
          anchor.blockNumber || 'N/A',
          anchor.audit.anchoredAt?.toISOString() || 'N/A'
        ]);
      });

      console.log(table.toString());

    } catch (error) {
      spinner.fail(chalk.red(`Failed: ${error.message}`));
      process.exit(1);
    } finally {
      await mongoose.disconnect();
    }
  });

program.parse(process.argv);
