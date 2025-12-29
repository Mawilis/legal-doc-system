const mongoose = require('mongoose');

console.log('🧹 FLUSHING CORRUPTED LEDGER DATA...');

// Use the robust IPv4 address
const MONGO_URI = 'mongodb://127.0.0.1:27017/legal-tech';

async function flush() {
    try {
        await mongoose.connect(MONGO_URI, { serverSelectionTimeoutMS: 5000 });
        console.log('✅ Connected to Database.');
        
        // Access the native driver to drop the collection safely
        const collections = await mongoose.connection.db.listCollections({ name: 'ledgerevents' }).toArray();
        
        if (collections.length > 0) {
            await mongoose.connection.db.dropCollection('ledgerevents');
            console.log('🗑️  EXISTING LEDGER CLEARED. (Removed corrupted sequence)');
        } else {
            console.log('ℹ️  Ledger was already empty.');
        }
        
        console.log('✨ READY FOR A FRESH START.');
        process.exit(0);
    } catch (err) {
        console.error('❌ FLUSH FAILED:', err.message);
        process.exit(1);
    }
}

flush();
