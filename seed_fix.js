/* eslint-disable */
import { MongoClient, ObjectId } from 'mongodb';

const seed = async () => {
  const MONGO_URI = "mongodb://wilsonkhanyezi:Mawilis8596@127.0.0.1:27017/?authSource=admin";
  const SHARD_DB = "tenant_69dd419f39c41a1b067fc048";

  const client = new MongoClient(MONGO_URI, { directConnection: true });

  try {
    await client.connect();
    const db = client.db(SHARD_DB);

    console.log("🛡️ [SYSTEM]: Adjusting Security Flags for OTP Entry...");

    // We set isVerified to false (so OTP triggers)
    // but ensure the 'mfaEnabled' and 'status' allow the transition.
    await db.collection('users').updateOne(
      { email: 'wilsonkhanyezi@gmail.com' },
      {
        $set: {
          status: 'ACTIVE',
          isVerified: false,
          mfaEnabled: true,
          mfaSecret: "WILSY_SOVEREIGN_ROOT_BEYOND_REPROACH",
          lastLogin: new Date()
        }
      }
    );

    console.log(`\n╔══════════════════════════════════════════════════════════╗`);
    console.log(`║ ✅ SUCCESS: OTP GATEWAY ALIGNED                          ║`);
    ║ FRONTEND SHOULD NOW RENDER: <OTPComponent />             ║
    ╚══════════════════════════════════════════════════════════╝`);

  } catch (err) {
    console.error("🚨 [CRITICAL]:", err.message);
  } finally {
    await client.close();
    process.exit(0);
  }
};

seed();
