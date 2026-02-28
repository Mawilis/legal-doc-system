import fs from 'fs';

const redisPath = '/Users/wilsonkhanyezi/legal-doc-system/server/config/redis.js';

try {
  let content = fs.readFileSync(redisPath, 'utf8');
  
  // Convert the legacy CommonJS export to a modern ESM default export
  if (content.includes('module.exports')) {
    content = content.replace(/module\.exports\s*=\s*/g, 'export default ');
    fs.writeFileSync(redisPath, content);
    console.log("✅ Converted module.exports to export default in config/redis.js");
  } else {
    console.log("✅ No module.exports found. Already fixed.");
  }
} catch (error) {
  console.error("⚠️ Patch failed:", error.message);
}
