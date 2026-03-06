#!/* eslint-disable */
/**
 * ╔═══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - NEURAL PRECEDENT VECTORIZER v1.0                               ║
 * ║ Quantum-inspired legal precedent embedding engine                         ║
 * ║ Transforms case law into 1536-dimensional vectors for semantic search    ║
 * ╚═══════════════════════════════════════════════════════════════════════════╝
 */

import { Worker } from 'bullmq';
import Redis from 'ioredis';
import crypto from 'crypto';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Redis connection for queue management
const redis = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
  maxRetriesPerRequest: null,
});

// Vector dimensions (OpenAI Ada-002 compatible)
export const VECTOR_DIMENSIONS = 1536;

// Model paths
const MODEL_PATH = path.join(__dirname, 'models', 'legal-bert.onnx');
const EMBEDDINGS_PATH = path.join(__dirname, 'embeddings');

export class NeuralPrecedentVectorizer {
  constructor() {
    this.model = null;
    this.tokenizer = null;
    this.initialized = false;
    this.processingQueue = [];
    this.stats = {
      processed: 0,
      failed: 0,
      totalTokens: 0,
      startTime: Date.now(),
    };
  }

  /**
   * Initialize the neural model (lazy loading)
   */
  async initialize() {
    if (this.initialized) return;

    console.log('🧠 Initializing Neural Precedent Vectorizer...');

    try {
      // In production, this would load actual ONNX model
      // For now, we'll use a mock implementation that will be replaced
      this.model = {
        predict: async (text) => {
          // Simulate neural processing
          await new Promise((resolve) => setTimeout(resolve, 50));
          return this.generateMockEmbedding(text);
        },
      };

      this.initialized = true;
      console.log('✅ Neural vectorizer initialized');
    } catch (error) {
      console.error('❌ Failed to initialize neural vectorizer:', error);
      throw error;
    }
  }

  /**
   * Generate a deterministic mock embedding (1536 dimensions)
   * In production, this would be replaced with actual model inference
   */
  generateMockEmbedding(text) {
    const hash = crypto.createHash('sha256').update(text).digest();
    const embedding = new Array(VECTOR_DIMENSIONS);

    // Generate pseudo-random but deterministic embedding
    for (let i = 0; i < VECTOR_DIMENSIONS; i++) {
      // Use hash to generate values between -1 and 1
      const byte = hash[i % hash.length];
      embedding[i] = byte / 127.5 - 1;
    }

    // Normalize the embedding (L2 norm)
    const norm = Math.sqrt(embedding.reduce((sum, val) => sum + val * val, 0));
    return embedding.map((val) => val / norm);
  }

  /**
   * Preprocess legal text for neural consumption
   */
  preprocessLegalText(text) {
    if (!text) return '';

    // Remove citations and legal boilerplate
    const processed = text
      .replace(/\b\d{4}\s+JDR\s+\d{4}\b/g, '') // Remove JDR citations
      .replace(/\b\d{4}\s+\(\d+\)\s+SA\s+\d+\b/g, '') // Remove SA citations
      .replace(/\b\d{4}\s+\(\d+\)\s+ALL\s+SA\s+\d+\b/g, '') // Remove ALL SA citations
      .replace(/\b\d{4}\s+ZACC\s+\d+\b/g, '') // Remove Constitutional Court citations
      .replace(/\b\d{4}\s+ZASCA\s+\d+\b/g, '') // Remove SCA citations
      .replace(/\b\d{4}\s+ZAGPJHC\s+\d+\b/g, '') // Remove Gauteng High Court citations
      .replace(/\s+/g, ' ') // Normalize whitespace
      .trim();

    return processed;
  }

  /**
   * Tokenize legal text into chunks for processing
   */
  tokenizeLegalText(text, maxTokens = 512) {
    // Simple whitespace tokenization (in production, use actual tokenizer)
    const words = text.split(/\s+/);
    const chunks = [];

    for (let i = 0; i < words.length; i += maxTokens) {
      chunks.push(words.slice(i, i + maxTokens).join(' '));
    }

    this.stats.totalTokens += words.length;
    return chunks;
  }

  /**
   * Generate embedding for a legal precedent
   */
  async generateEmbedding(precedent) {
    await this.initialize();

    const {
      caseName, citation, court, judgmentDate, summary, keyPrinciples, fullText,
    } = precedent;

    // Create rich text representation
    const richText = `
      Case: ${caseName}
      Citation: ${citation}
      Court: ${court}
      Date: ${judgmentDate || 'Unknown'}
      Summary: ${summary || ''}
      Principles: ${keyPrinciples ? keyPrinciples.join('; ') : ''}
      Text: ${fullText || ''}
    `
      .replace(/\s+/g, ' ')
      .trim();

    // Preprocess and tokenize
    const processed = this.preprocessLegalText(richText);
    const chunks = this.tokenizeLegalText(processed);

    // Generate embeddings for each chunk
    const chunkEmbeddings = await Promise.all(chunks.map((chunk) => this.model.predict(chunk)));

    // Average the chunk embeddings
    const finalEmbedding = new Array(VECTOR_DIMENSIONS).fill(0);
    for (const emb of chunkEmbeddings) {
      for (let i = 0; i < VECTOR_DIMENSIONS; i++) {
        finalEmbedding[i] += emb[i];
      }
    }

    // Normalize
    const norm = Math.sqrt(finalEmbedding.reduce((sum, val) => sum + val * val, 0));
    for (let i = 0; i < VECTOR_DIMENSIONS; i++) {
      finalEmbedding[i] /= norm;
    }

    return finalEmbedding;
  }

  /**
   * Save embedding to disk (for production, use vector database)
   */
  async saveEmbedding(citation, embedding, metadata) {
    const embeddingId = crypto.createHash('sha256').update(citation).digest('hex');

    const embeddingPath = path.join(EMBEDDINGS_PATH, `${embeddingId}.json`);

    await fs.writeFile(
      embeddingPath,
      JSON.stringify(
        {
          id: embeddingId,
          citation,
          embedding,
          metadata,
          generatedAt: new Date().toISOString(),
          version: '1.0',
          dimensions: VECTOR_DIMENSIONS,
        },
        null,
        2,
      ),
    );

    return embeddingId;
  }

  /**
   * Process a precedent job from the queue
   */
  async processJob(job) {
    const { precedent, options = {} } = job.data;

    console.log(`🧠 Processing precedent: ${precedent.citation}`);

    try {
      // Generate embedding
      const embedding = await this.generateEmbedding(precedent);

      // Save to disk/vector DB
      const embeddingId = await this.saveEmbedding(precedent.citation, embedding, {
        caseName: precedent.caseName,
        court: precedent.court,
        judgmentDate: precedent.judgmentDate,
        tags: precedent.tags || [],
      });

      this.stats.processed++;

      return {
        success: true,
        embeddingId,
        citation: precedent.citation,
        dimensions: VECTOR_DIMENSIONS,
        processingTime: Date.now() - job.timestamp,
        stats: {
          processed: this.stats.processed,
          failed: this.stats.failed,
        },
      };
    } catch (error) {
      this.stats.failed++;
      console.error(`❌ Failed to process ${precedent.citation}:`, error);
      throw error;
    }
  }

  /**
   * Get worker statistics
   */
  getStats() {
    return {
      ...this.stats,
      uptime: Date.now() - this.stats.startTime,
      queueSize: this.processingQueue.length,
      initialized: this.initialized,
      modelLoaded: !!this.model,
    };
  }
}

// Create and start the worker
const vectorizer = new NeuralPrecedentVectorizer();

export const worker = new Worker(
  'neural-vectorizer',
  async (job) => await vectorizer.processJob(job),
  {
    connection: redis,
    concurrency: 4,
    limiter: {
      max: 10,
      duration: 1000,
    },
  },
);

// Event handlers
worker.on('completed', (job, result) => {
  console.log(`✅ Job ${job.id} completed: ${result.citation}`);
});

worker.on('failed', (job, err) => {
  console.error(`❌ Job ${job.id} failed:`, err.message);
});

worker.on('progress', (job, progress) => {
  console.log(`📊 Job ${job.id} progress: ${progress}%`);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('🛑 Shutting down neural vectorizer...');
  await worker.close();
  await redis.quit();
  process.exit(0);
});

console.log('🧠 Neural Precedent Vectorizer worker started');
console.log(`📊 Configuration:
  - Vector Dimensions: ${VECTOR_DIMENSIONS}
  - Model Path: ${MODEL_PATH}
  - Embeddings Path: ${EMBEDDINGS_PATH}
  - Concurrency: 4
  - Rate Limit: 10 jobs/second
`);

// Export everything needed
export { vectorizer };
export default worker;
