import mongoose from 'mongoose';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.join(__dirname, '.env') });

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/wilsy-sovereign-root';
const email = 'wilsonkhanyezi@gmail.com';
const newHash = '$2b$10$Q0hCa19lrmnvv8fnjSMj0.qnX1iYVPfDxWh14jIuHrTSDGBOMsVDO';

async function run() {
  try {
    await mongoose.connect(MONGODB_URI);
    const db = mongoose.connection.db;
    const result = await db.collection('users').updateOne(
      { email },
      { $set: { passwordHash: newHash } }
    );
    console.log('✅ Update result:', JSON.stringify(result, null, 2));
    const doc = await db.collection('users').findOne({ email }, { projection: { passwordHash: 1 } });
    console.log('✅ passwordHash set:', doc ? 'yes' : 'no');
    await mongoose.disconnect();
    console.log('✅ Done.');
  } catch (err) {
    console.error('❌ Error:', err);
  }
}

run();
