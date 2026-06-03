import bcrypt from 'bcryptjs';
import { MongoClient } from 'mongodb';

const uri = 'mongodb://localhost:27017';
const client = new MongoClient(uri);

async function debugAuth() {
  try {
    await client.connect();
    const db = client.db('wilsy-os');
    const user = await db.collection('users').findOne({ email: 'wilsy.wk@gmail.com' });

    if (!user) {
      console.log('User not found');
      return;
    }

    console.log('User found:', user.email);
    console.log('Role:', user.role);

    const isValid = await bcrypt.compare('Wilsy2026Secure', user.password);
    console.log('Password valid:', isValid);

    await client.close();
  } catch (err) {
    console.error('Error:', err);
  }
}

debugAuth();
