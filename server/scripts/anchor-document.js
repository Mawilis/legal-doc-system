#!/usr/bin/env node
/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ ANCHOR DOCUMENT SCRIPT - PRODUCTION GRADE                                 ║
  ║ CLI tool for anchoring documents to Hyperledger                          ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import { program } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import Table from 'cli-table3';
import crypto from 'crypto';
import mongoose from 'mongoose';
import dotenv from 'dotenv';
import BlockchainAnchor, { BLOCKCHAIN_STATUS } from '../models/BlockchainAnchor.js';
import blockchainService from '../services/blockchainService.js';
import { MerkleTree } from '../utils/blockchainCrypto.js';

dotenv.config();

program
  .version('1.0.0')
  .description('WILSY OS - Document Anchoring CLI');

program
  .command('anchor <documentId>')
  .description('Anchor a document to Hyperledger')
  .option('-t, --tenant <tenantId>', 'Tenant ID')
  .option('-h, --hash <hash>', 'Document hash (if not provided, will be generated)')
  .option('-w, --wait', 'Wait for confirmation', false)
  .action(async (documentId, options) => {
    const spinner = ora('Anchoring document...').start();

    try {
      await mongoose.connect(process.env.MONGODB_URI);

      const documentHash = options.hash || crypto
        .createHash('sha256')
        .update(documentId + Date.now())
        .digest('hex');

      const anchor = new BlockchainAnchor({
        documentId,
        documentHash,
        tenantId: options.tenant || 'default',
        documentType: 'document',
        status: BLOCKCHAIN_STATUS.PENDING,
        audit: { createdBy: 'cli' }
      });

      await anchor.save();
      spinner.text = 'Anchoring to Hyperledger...';

      const result = await blockchainService.anchorDocument({
        documentHash,
        documentId,
        tenantId: options.tenant || 'default'
      });

      anchor.transactionId = result.transactionId;
      anchor.blockNumber = result.blockNumber;
      anchor.blockHash = result.blockHash;
      anchor.status = BLOCKCHAIN_STATUS.ANCHORED;
      anchor.audit.anchoredBy = 'cli';
      anchor.audit.anchoredAt = new Date();
      await anchor.save();

      spinner.succeed(chalk.green('Document anchored successfully!'));

      const table = new Table({
        head: ['Property', 'Value'],
        colWidths: [20, 60]
      });

      table.push(
        ['Anchor ID', anchor.anchorId],
        ['Document ID', documentId],
        ['Document Hash', documentHash],
        ['Transaction ID', result.transactionId],
        ['Block Number', result.blockNumber],
        ['Block Hash', result.blockHash],
        ['Channel', result.channelName],
        ['Chaincode', result.chaincodeName],
        ['Timestamp', new Date().toISOString()]
      );

      console.log(table.toString());

    } catch (error) {
      spinner.fail(chalk.red(`Failed: ${error.message}`));
      process.exit(1);
    } finally {
      await mongoose.disconnect();
    }
  });

program
  .command('batch <file>')
  .description('Batch anchor documents from JSON file')
  .option('-t, --tenant <tenantId>', 'Tenant ID')
  .action(async (file, options) => {
    const spinner = ora('Processing batch...').start();

    try {
      const documents = JSON.parse(require('fs').readFileSync(file, 'utf8'));
      
      await mongoose.connect(process.env.MONGODB_URI);

      const leaves = documents.map(doc => 
        crypto.createHash('sha256').update(JSON.stringify(doc)).digest('hex')
      );
      
      const merkleTree = new MerkleTree(leaves);
      const merkleRoot = merkleTree.getRoot();

      spinner.text = `Anchoring ${documents.length} documents...`;

      const result = await blockchainService.anchorBatch({
        documents,
        merkleRoot,
        tenantId: options.tenant || 'default'
      });

      const anchors = [];
      for (let i = 0; i < documents.length; i++) {
        const doc = documents[i];
        const anchor = new BlockchainAnchor({
          documentId: doc.id,
          documentHash: leaves[i],
          tenantId: options.tenant || 'default',
          documentType: doc.type || 'document',
          transactionId: result.transactionId,
          blockNumber: result.blockNumber,
          blockHash: result.blockHash,
          merkleProof: {
            root: merkleRoot,
            proof: merkleTree.getProof(leaves[i])
          },
          status: BLOCKCHAIN_STATUS.ANCHORED,
          audit: { createdBy: 'cli' }
        });
        await anchor.save();
        anchors.push(anchor);
      }

      spinner.succeed(chalk.green(`Batch anchored successfully!`));

      const table = new Table({
        head: ['Metric', 'Value'],
        colWidths: [20, 60]
      });

      table.push(
        ['Documents Anchored', documents.length],
        ['Merkle Root', merkleRoot],
        ['Transaction ID', result.transactionId],
        ['Block Number', result.blockNumber]
      );

      console.log(table.toString());

    } catch (error) {
      spinner.fail(chalk.red(`Failed: ${error.message}`));
      process.exit(1);
    } finally {
      await mongoose.disconnect();
    }
  });

program.parse(process.argv);
