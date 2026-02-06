const path = require('path');

// Test if we can require the new route files
try {
    const spaceRoutes = require('./routes/spaceRoutes');
    console.log('✅ spaceRoutes.js loaded successfully');
} catch (error) {
    console.error('❌ Failed to load spaceRoutes.js:', error.message);
}

try {
    const interstellarRoutes = require('./routes/interstellarRoutes');
    console.log('✅ interstellarRoutes.js loaded successfully');
} catch (error) {
    console.error('❌ Failed to load interstellarRoutes.js:', error.message);
}

// List all route files
console.log('\n📁 All route files in routes directory:');
const fs = require('fs');
fs.readdirSync('./routes').forEach(file => {
    console.log(`  - ${file}`);
});
