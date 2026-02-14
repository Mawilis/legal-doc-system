// Simple test to check if lpcService can be imported
try {
    const lpcService = require('../services/lpcService');
    console.log('✅ Successfully imported lpcService');
    console.log('Exports:', Object.keys(lpcService));
} catch (error) {
    console.error('❌ Failed to import lpcService:', error.message);
}
