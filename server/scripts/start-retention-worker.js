const { startRetentionWorker } = require('../workers/retentionAgenda');

async function main() {
  try {
    console.log('Starting retention worker...');
    const worker = await startRetentionWorker();
    console.log('Retention worker started successfully');
  } catch (error) {
    console.error('Failed to start retention worker:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = main;
