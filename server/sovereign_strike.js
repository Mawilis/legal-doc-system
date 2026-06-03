/* eslint-disable */
/**
 * ╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - UNIFIED SOVEREIGN STRIKE [V1.3.0-OMEGA]                                                                                     ║
 * ║ [PROTOCOL: LIVE-SIGNING | AUTO-NETWORK-STRIKE | RSA-PSS 2048 | BILLION DOLLAR SPEC]                                                   ║
 * ╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
 * ║ VERSION: 1.3.0 | CEO SIGN-OFF: Wilson Khanyezi                                                                                         ║
 * ║ EPITOME: NO CHILD'S PLACE | INSTITUTIONAL AUTHORITY                                                                                    ║
 * ╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
 */
import crypto from 'crypto';
import fs from 'fs';
import fetch from 'node-fetch';

const OTP_ARG = process.argv[2];
if (!OTP_ARG || OTP_ARG.length !== 6) {
  console.error("❌ ERROR: Provide 6-digit OTP. Usage: node sovereign_strike.js 123456");
  process.exit(1);
}

const IDENTITY = 'wilsonkhanyezi@gmail.com';
const GATEWAY_URL = 'http://localhost:5050/api/auth/verify-3fa';
const PRIVATE_KEY_PATH = 'private.pem';

async function performUnifiedStrike() {
  try {
    console.log(`\n🚀 [STRIKE-INIT] Generating Sovereign Signature...`);

    // 1. Generate fresh signature using local private.pem with EXACT PSS parameters
    const privateKey = fs.readFileSync(PRIVATE_KEY_PATH, 'utf8');
    const challenge = 'wilsy-auth-challenge';

    const signature = crypto.sign('sha256', Buffer.from(challenge), {
      key: privateKey,
      padding: crypto.constants.RSA_PKCS1_PSS_PADDING,
      saltLength: crypto.constants.RSA_PSS_SALTLEN_DIGEST
    });

    const biometricToken = signature.toString('base64');
    console.log(`✅ Signature Manifested. Attacking Gateway...`);

    // 2. Strike the Gateway
    const response = await fetch(GATEWAY_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: IDENTITY,
        otp: OTP_ARG,
        biometricToken
      })
    });

    const data = await response.json();

    if (data.success) {
      console.log("\n╔════════════════════════════════════════════════════════════╗");
      console.log("║ ✅ SOVEREIGN GATEWAY BREACHED - DASHBOARD ACCESS GRANTED   ║");
      console.log("╠════════════════════════════════════════════════════════════╣");
      console.log(`║ TOKEN: ${data.token.substring(0, 45)}... ║`);
      console.log("╚════════════════════════════════════════════════════════════╝\n");
    } else {
      console.error("\n❌ [STRIKE-FAILED] Repelled:", data.message);
    }
  } catch (err) {
    console.error("\n❌ [STRIKE-FRACTURE] Sequence Error:", err.message);
  }
}

performUnifiedStrike();
