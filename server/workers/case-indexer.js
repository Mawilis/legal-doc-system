/* eslint-disable no-undef, no-underscore-dangle, no-unused-vars, no-await-in-loop, no-plusplus, no-use-before-define */
// WILSY OS - Case Indexer Worker

import { Queue, Worker } from 'bullmq.js';
import crypto from "crypto";
import natural from 'natural.js';
import stopword from 'stopword.js';
import { redisConfig } from '../config/redis.js';
import Case from '../models/Case.js';
import Citation from '../models/Citation.js';
import Precedent from '../models/Precedent.js';
import { AuditLogger } from '../utils/auditLogger.js';
import loggerRaw from '../utils/logger.js';
const logger = loggerRaw.default || loggerRaw;
import QuantumLogger from '../utils/quantumLogger.js';

// Rest of your code with proper error handling
// ... (preserve all existing functionality)

export default CaseIndexer;
