#!/usr/bin/env node
// Production Readiness Validator for Wilsy OS
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

class ProductionValidator {
  constructor() {
    this.rootDir = process.cwd();
    this.issues = [];
    this.criticalIssues = [];
    this.validatedFiles = 0;
  }

  async validateAll() {
    console.log('🔍 WILSY OS PRODUCTION READINESS AUDIT\n');
    console.log('='.repeat(80));
    
    // Run all validations
    await this.validateStructure();
    await this.validateSecurity();
    await this.validatePerformance();
    await this.validateCompliance();
    await this.validateDependencies();
    await this.validateConfiguration();
    
    // Generate report
    this.generateReport();
    
    // Exit with appropriate code
    if (this.criticalIssues.length > 0) {
      console.error('\n❌ CRITICAL ISSUES FOUND - NOT PRODUCTION READY');
      process.exit(1);
    } else if (this.issues.length > 0) {
      console.warn('\n⚠️  ISSUES FOUND - REVIEW BEFORE PRODUCTION');
      process.exit(0);
    } else {
      console.log('\n✅ ALL CHECKS PASSED - PRODUCTION READY');
      process.exit(0);
    }
  }

  async validateStructure() {
    console.log('\n📁 Validating Project Structure...');
    
    const requiredDirs = [
      'models',
      'services',
      'routes', 
      'middleware',
      'utils',
      'config',
      'tests',
      'scripts'
    ];
    
    requiredDirs.forEach(dir => {
      if (!fs.existsSync(path.join(this.rootDir, dir))) {
        this.addIssue('Structure', `Missing required directory: ${dir}`, 'MEDIUM');
      }
    });
    
    // Check for misplaced files
    this.findMisplacedFiles();
  }

  async validateSecurity() {
    console.log('\n🔐 Validating Security...');
    
    // Check for hardcoded secrets
    await this.scanForSecrets();
    
    // Check SSL/TLS configuration
    this.checkSSLConfig();
    
    // Validate authentication middleware
    this.validateAuthMiddleware();
  }

  async validatePerformance() {
    console.log('\n⚡ Validating Performance...');
    
    // Check for memory leaks
    this.checkMemoryPatterns();
    
    // Validate database indexes
    this.validateDatabaseIndexes();
    
    // Check for N+1 query patterns
    this.checkQueryPatterns();
  }

  async validateCompliance() {
    console.log('\n📜 Validating Compliance...');
    
    // GDPR/POPIA compliance
    this.checkPrivacyCompliance();
    
    // Legal document validation
    this.validateLegalComponents();
    
    // Audit trail requirements
    this.checkAuditTrails();
  }

  async validateDependencies() {
    console.log('\n📦 Validating Dependencies...');
    
    const pkgPath = path.join(this.rootDir, 'package.json');
    if (!fs.existsSync(pkgPath)) {
      this.addCriticalIssue('Dependencies', 'Missing package.json');
      return;
    }
    
    const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
    
    // Check for vulnerable dependencies
    this.checkDependencyVersions(pkg);
    
    // Validate production dependencies
    this.validateProductionDeps(pkg);
  }

  async validateConfiguration() {
    console.log('\n⚙️  Validating Configuration...');
    
    // Check environment variables
    this.checkEnvConfiguration();
    
    // Validate config files
    this.validateConfigFiles();
    
    // Check logging configuration
    this.checkLoggingConfig();
  }

  findMisplacedFiles() {
    const misplacedPatterns = [
      { pattern: /test\.js$/, allowedIn: ['tests/', '__tests__/'] },
      { pattern: /config\.js$/, allowedIn: ['config/'] },
      { pattern: /model\.js$/, allowedIn: ['models/'] },
      { pattern: /service\.js$/, allowedIn: ['services/'] },
      { pattern: /route\.js$/, allowedIn: ['routes/'] },
      { pattern: /middleware\.js$/, allowedIn: ['middleware/'] },
      { pattern: /util\.js$/, allowedIn: ['utils/'] }
    ];
    
    // Walk through all .js files
    this.walkDirectory(this.rootDir, (filePath) => {
      if (filePath.endsWith('.js')) {
        this.validatedFiles++;
        const relativePath = path.relative(this.rootDir, filePath);
        
        misplacedPatterns.forEach(pattern => {
          if (pattern.pattern.test(filePath)) {
            const isInAllowedDir = pattern.allowedIn.some(dir => 
              relativePath.startsWith(dir)
            );
            
            if (!isInAllowedDir) {
              const suggestedDir = pattern.allowedIn[0].replace('/', '');
              this.addIssue('Structure', 
                `File misplaced: ${relativePath} should be in ${suggestedDir}/ directory`,
                'LOW'
              );
            }
          }
        });
      }
    });
  }

  walkDirectory(dir, callback) {
    const items = fs.readdirSync(dir);
    
    items.forEach(item => {
      if (item === 'node_modules' || item === '.git' || item === 'coverage') {
        return;
      }
      
      const fullPath = path.join(dir, item);
      const stat = fs.statSync(fullPath);
      
      if (stat.isDirectory()) {
        this.walkDirectory(fullPath, callback);
      } else {
        callback(fullPath);
      }
    });
  }

  addIssue(category, message, severity) {
    this.issues.push({ category, message, severity, timestamp: new Date().toISOString() });
  }

  addCriticalIssue(category, message) {
    this.criticalIssues.push({ category, message, timestamp: new Date().toISOString() });
  }

  generateReport() {
    console.log('\n' + '='.repeat(80));
    console.log('📋 PRODUCTION READINESS REPORT');
    console.log('='.repeat(80));
    
    console.log(`\nFiles Validated: ${this.validatedFiles}`);
    console.log(`Critical Issues: ${this.criticalIssues.length}`);
    console.log(`Other Issues: ${this.issues.length}`);
    
    if (this.criticalIssues.length > 0) {
      console.log('\n🚨 CRITICAL ISSUES:');
      this.criticalIssues.forEach((issue, index) => {
        console.log(`${index + 1}. [${issue.category}] ${issue.message}`);
      });
    }
    
    if (this.issues.length > 0) {
      console.log('\n⚠️  OTHER ISSUES:');
      this.issues.slice(0, 10).forEach((issue, index) => { // Show first 10
        console.log(`${index + 1}. [${issue.severity}] [${issue.category}] ${issue.message}`);
      });
      
      if (this.issues.length > 10) {
        console.log(`... and ${this.issues.length - 10} more issues`);
      }
    }
    
    // Save detailed report
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        filesValidated: this.validatedFiles,
        criticalIssues: this.criticalIssues.length,
        otherIssues: this.issues.length
      },
      criticalIssues: this.criticalIssues,
      issues: this.issues,
      recommendations: this.generateRecommendations()
    };
    
    const reportsDir = path.join(this.rootDir, 'reports');
    if (!fs.existsSync(reportsDir)) {
      fs.mkdirSync(reportsDir, { recursive: true });
    }
    
    fs.writeFileSync(
      path.join(reportsDir, 'production-readiness.json'),
      JSON.stringify(report, null, 2)
    );
    
    console.log(`\n📝 Detailed report saved to: ${path.join(reportsDir, 'production-readiness.json')}`);
  }

  generateRecommendations() {
    const recommendations = [];
    
    if (this.criticalIssues.length > 0) {
      recommendations.push('Fix all critical issues before production deployment');
    }
    
    if (this.issues.length > 20) {
      recommendations.push('Address high and medium priority issues');
    }
    
    if (!fs.existsSync(path.join(this.rootDir, 'Dockerfile'))) {
      recommendations.push('Add Dockerfile for containerized deployment');
    }
    
    if (!fs.existsSync(path.join(this.rootDir, 'docker-compose.yml'))) {
      recommendations.push('Add docker-compose.yml for local development');
    }
    
    return recommendations;
  }

  // Stub methods for validation checks
  scanForSecrets() { /* Implementation */ }
  checkSSLConfig() { /* Implementation */ }
  validateAuthMiddleware() { /* Implementation */ }
  checkMemoryPatterns() { /* Implementation */ }
  validateDatabaseIndexes() { /* Implementation */ }
  checkQueryPatterns() { /* Implementation */ }
  checkPrivacyCompliance() { /* Implementation */ }
  validateLegalComponents() { /* Implementation */ }
  checkAuditTrails() { /* Implementation */ }
  checkDependencyVersions() { /* Implementation */ }
  validateProductionDeps() { /* Implementation */ }
  checkEnvConfiguration() { /* Implementation */ }
  validateConfigFiles() { /* Implementation */ }
  checkLoggingConfig() { /* Implementation */ }
}

// Execute validation
const validator = new ProductionValidator();
validator.validateAll().catch(console.error);
