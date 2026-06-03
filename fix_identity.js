/* eslint-disable */
import { MongoClient, ObjectId } from 'mongodb';

const fix = async () => {
  const MONGO_URI = "mongodb://wilsonkhanyezi:Mawilis8596@127.0.0.1:27017/?authSource=admin";
  const SHARD_DB = "tenant_69dd419f39c41a1b067fc048";

  const client = new MongoClient(MONGO_URI, { directConnection: true });

  try {
    await client.connect();
    const db = client.db(SHARD_DB);

    console.log("🏛️ [SYSTEM]: Elevating Wilson Khanyezi to FOUNDER status...");

    await db.collection('users').updateOne(
      { email: 'wilsonkhanyezi@gmail.com' },
      {
        $set: {
          role: 'FOUNDER', // Matches the check in App.jsx
          status: 'ACTIVE',
          mfaEnabled: true,
          isVerified: false, // Forces the /otp route
          'securityMetadata.mfaEnabled': true
        }
      }
    );

    console.log("✅ SUCCESS: Role updated to FOUNDER. Shard synchronized.");
  } finally {
    await client.close();
    process.exit(0);
  }
};

fix();
