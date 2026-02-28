import fs from 'fs';

const metricsPath = '/Users/wilsonkhanyezi/legal-doc-system/server/utils/metrics.js';
const redisPath = '/Users/wilsonkhanyezi/legal-doc-system/server/config/redis.js';

try {
  // 1. Convert legacy CommonJS export to modern ESM
  if (fs.existsSync(metricsPath)) {
    let content = fs.readFileSync(metricsPath, 'utf8');
    content = content.replace(/module\.exports\s*=\s*/g, 'export default ');
    fs.writeFileSync(metricsPath, content);
    console.log('✅ Converted module.exports to export default in utils/metrics.js');
  }

  // 2. Upgrade the polyfilled require() to a native ESM import
  if (fs.existsSync(redisPath)) {
    let content = fs.readFileSync(redisPath, 'utf8');
    content = content.replace(/(?:const|let|var)\s+([^=\s]+)\s*=\s*require\(['"]([^'"]+metrics(?:\.js)?)['"]\);?/g, "import $1 from '$2';");
    fs.writeFileSync(redisPath, content);
    console.log('✅ Upgraded require() to import in config/redis.js');
  }
} catch (e) {
  console.error("⚠️ Patch failed:", e.message);
}
