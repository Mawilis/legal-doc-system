/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - BIOMETRIC SIGNATURE STRIKE [V1.0.0-OMEGA]                                                                                   ║
 * ║ [PROTOCOL: RSA-PSS 2048 | CHALLENGE: wilsy-auth-challenge | BILLION DOLLAR SPEC]                                                       ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */
import crypto from 'crypto';
import fs from 'fs';

try {
  const privateKey = fs.readFileSync('private.pem', 'utf8');
  const challenge = 'wilsy-auth-challenge';

  const signature = crypto.sign('sha256', Buffer.from(challenge), {
    key: privateKey,
    padding: crypto.constants.RSA_PKCS1_PSS_PADDING
  });

  console.log("\n╔════════════════════════════════════════════════════════════╗");
  console.log("║ 🛰️  YOUR SOVEREIGN BIOMETRIC TOKEN (BASE64)                ║");
  console.log("╠════════════════════════════════════════════════════════════╣");
  console.log(signature.toString('base64'));
  console.log("╚════════════════════════════════════════════════════════════╝\n");
} catch (err) {
  console.error('❌ SIGNATURE STRIKE FRACTURE:', err.message);
}
