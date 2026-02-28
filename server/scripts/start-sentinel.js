/* ╔═══════════════════════════════════════════════════════════════════════════════════════╗
  ║ WILSY OS: SENTINEL BOOTSTRAP - LAUNCH AUTONOMOUS PROTECTION                           ║
  ║ [99.999% Uptime | Gen 10 Ready | Self-Healing Infrastructure]                         ║
  ╚═══════════════════════════════════════════════════════════════════════════════════════╝ */

import dotenv from 'dotenv.js';
import { dirname, join } from "path";
import { fileURLToPath } from 'url';
import RecoverySentinel from './RecoverySentinel.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load environment variables
dotenv.config({ path: join(__dirname, '../.env') });

console.log(`\n${'='.repeat(60)}`);
console.log('🚀 LAUNCHING WILSY OS SENTINEL PROTECTION');
console.log('='.repeat(60));
console.log(`📋 PID: ${process.pid}`);
console.log(`🕒 Started: ${new Date().toISOString()}`);
console.log(`🔐 Sentinel ID: ${RecoverySentinel.sentinelId}`);
console.log(`📊 Check Interval: ${RecoverySentinel.checkInterval / 1000}s`);
console.log('🎯 Target: 99.999% Uptime');
console.log('='.repeat(60));

// Handle graceful shutdown
process.on('SIGTERM', async () => {
  console.log('\n📥 SIGTERM received, shutting down sentinel...');
  await RecoverySentinel.stop();
  process.exit(0);
});

process.on('SIGINT', async () => {
  console.log('\n📥 SIGINT received, shutting down sentinel...');
  await RecoverySentinel.stop();
  process.exit(0);
});

// Handle uncaught errors
process.on('uncaughtException', (error) => {
  console.error('❌ Uncaught Exception:', error);
  // Sentinel should not crash - log and continue
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
  // Sentinel should not crash - log and continue
});

// Start the sentinel
RecoverySentinel.start().catch((error) => {
  console.error('❌ Failed to start sentinel:', error);
  process.exit(1);
});

// Export for testing
export default RecoverySentinel;
