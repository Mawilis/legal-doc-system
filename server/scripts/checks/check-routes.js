const fs = require('fs');
const routes = fs.readdirSync('./routes');

const manifestRoutes = [
    'generationalRoutes.js', 'foundationRoutes.js', 'billionRoutes.js',
    'revenueRoutes.js', 'investmentRoutes.js', 'sovereignRoutes.js',
    'aiRoutes.js', 'quantumRoutes.js', 'globalRoutes.js',
    'internationalRoutes.js', 'africaRoutes.js', 'continentalRoutes.js',
    'spaceRoutes.js', 'interstellarRoutes.js', 'galacticRoutes.js',
    'cosmicLawRoutes.js', 'cosmicRoutes.js', 'eternalRoutes.js',
    'legacyRoutes.js', 'eternityRoutes.js', 'authRoutes.js',
    'firmRoutes.js', 'documentRoutes.js', 'caseRoutes.js',
    'billingRoutes.js', 'analyticsRoutes.js'
];

console.log('Checking route manifest:');
for (const manifestRoute of manifestRoutes) {
    if (routes.includes(manifestRoute)) {
        console.log(`✅ ${manifestRoute}`);
    } else {
        console.log(`❌ MISSING: ${manifestRoute}`);
    }
}
