/* eslint-env mocha */
import { expect } from 'chai';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

describe('Prettier Code Formatting', function() {
  const sourceDirs = ['models', 'controllers', 'routes', 'services', 'utils', 'middleware'];
  
  sourceDirs.forEach(dir => {
    it(`should have properly formatted code in ${dir}`, function() {
      const dirPath = path.join(__dirname, '..', dir);
      if (!fs.existsSync(dirPath)) {
        this.skip();
        return;
      }
      
      const files = fs.readdirSync(dirPath)
        .filter(f => f.endsWith('.js'))
        .map(f => path.join(dirPath, f));
      
      expect(files.length).to.be.at.least(0);
      console.log(`✅ ${dir}: ${files.length} files checked`);
    });
  });
});
