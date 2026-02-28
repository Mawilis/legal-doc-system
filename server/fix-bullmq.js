import fs from 'fs';
import path from 'path';

function fixBullMQ(dir) {
  let files;
  try {
    files = fs.readdirSync(dir);
  } catch (e) { return; } // Safely skip unreadable directories

  for (const file of files) {
    const fullPath = path.join(dir, file);
    try {
      // lstatSync safely inspects symlinks without crashing if the target is missing
      const stat = fs.lstatSync(fullPath);
      
      if (stat.isDirectory()) {
        if (!fullPath.includes('node_modules') && !fullPath.includes('.git') && !fullPath.includes('backups')) {
          fixBullMQ(fullPath);
        }
      } else if (stat.isFile() && (fullPath.endsWith('.js') || fullPath.endsWith('.cjs') || fullPath.endsWith('.mjs'))) {
        let content = fs.readFileSync(fullPath, 'utf8');
        if (content.includes('QueueScheduler')) {
          // Surgically remove from import objects
          content = content.replace(/,\s*QueueScheduler/g, '');
          content = content.replace(/QueueScheduler\s*,/g, '');
          content = content.replace(/import\s*\{\s*QueueScheduler\s*\}\s*from\s*['"]bullmq['"];?/g, '');
          
          // Comment out any instantiation lines to prevent execution crashes
          content = content.replace(/.*new\s+QueueScheduler.*/g, '// FORENSIC FIX: QueueScheduler removed (Natively handled in BullMQ v3+)');
          
          fs.writeFileSync(fullPath, content);
          console.log(`✅ Purged deprecated QueueScheduler from: ${fullPath}`);
        }
      }
    } catch (error) {
      // 🛡️ Bulletproof shield: Silently ignore broken symlinks and unreadable files
    }
  }
}

console.log("🔍 Scanning for BullMQ Technical Debt with Forensic Shielding...");
fixBullMQ(process.cwd());
console.log("🎯 BullMQ cleanup complete.");
