// Clear cache
delete require.cache[require.resolve('./models/auditEventModel')];
delete require.cache[require.resolve('./utils/auditLogger')];
delete require.cache[require.resolve('mongoose')];

console.log('Fresh require test...');
try {
    const auditLogger = require('./utils/auditLogger');
    console.log('✅ Successfully required auditLogger');
} catch (error) {
    console.log('❌ Error:', error.message);
    console.log('Full error:');
    console.error(error);
}
