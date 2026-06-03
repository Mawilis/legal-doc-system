/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║  🧠 SOVEREIGN CONFIGURATION ENGINE - WILSY OS 2050                       ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/
const config = {
  database: {
    uri: process.env.MONGODB_URI || 'mongodb://localhost:27017/wilsy_os',
    poolSize: 10
  },
  cors: {
    origins: ['http://localhost:3000', 'http://localhost:3001']
  },
  bodyLimit: '10mb',
  requiresRedis: false
};

export default config;
