# WILSY OS - Twilio SMS Setup Guide
## Production-Ready SMS Notifications for Fortune 500 Legal System

### Step 1: Sign up for Twilio Account
1. Go to https://www.twilio.com/try-twilio
2. Sign up with your email (wilsonkhanyezi@gmail.com)
3. Verify your email and phone number
4. You'll get $15 free credit to start

### Step 2: Get Your Account Credentials
1. Log in to Twilio Console: https://console.twilio.com
2. Find your Account SID and Auth Token on the dashboard
3. They look like:
   - Account SID: ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   - Auth Token: your_auth_token_here

### Step 3: Purchase a Phone Number
1. Go to Phone Numbers → Manage → Buy a Number
2. Search for a South African number (+27) or international
3. Select SMS-capable number
4. Purchase the number (costs about $1-2/month)

### Step 4: Update .env File
Add these credentials to your .env file:

```env
# Twilio SMS Configuration
TWILIO_ACCOUNT_SID=ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+27691234567  # Your purchased number
ALERT_SMS_RECIPIENTS=+27791234567,+27821234567  # Your team numbers
Step 5: Test SMS Sending
Create a test script:

javascript
// test-sms.js
import twilio from 'twilio';

const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;
const client = twilio(accountSid, authToken);

async function sendTestSMS() {
  try {
    const message = await client.messages.create({
      body: '🚀 WILSY OS SMS Test: Quantum system operational!',
      from: process.env.TWILIO_PHONE_NUMBER,
      to: '+27791234567'
    });
    console.log('✅ SMS sent! SID:', message.sid);
  } catch (error) {
    console.error('❌ SMS failed:', error);
  }
}

sendTestSMS();
Step 6: Set Up Webhook for Incoming SMS (Optional)
In Twilio Console, go to Phone Numbers → Manage → Active Numbers

Click on your number

Configure webhook: https://api.wilsy.os/api/sms/incoming

Set to HTTP POST

Step 7: Enable Two-Factor Authentication
Go to Settings → Account Security

Enable Two-Factor Authentication

Add backup phone numbers

Configure API key restrictions

Step 8: Set Up Alert Recipients
Update your .env with team members:

env
# On-Call Rotation
ONCALL_PHONE_NUMBER=+27791234567
ONCALL_SCHEDULE_ID=primary-schedule-id

# Alert SMS Recipients (comma-separated)
ALERT_SMS_RECIPIENTS=+27791234567,+27792345678,+27793456789
Step 9: Configure SMS Alert Types
javascript
// sms-alert-config.js
export const SMS_ALERT_TYPES = {
  CRITICAL: 'critical',   // Immediate, high-priority alerts
  URGENT: 'urgent',       // Important, time-sensitive alerts
  NORMAL: 'normal',       // Routine notifications
  INFO: 'info'            // Informational only
};

export const SMS_ALERT_RULES = {
  critical: {
    maxPerHour: 10,
    recipients: 'all',
    retryCount: 3
  },
  urgent: {
    maxPerHour: 20,
    recipients: 'primary',
    retryCount: 2
  },
  normal: {
    maxPerHour: 50,
    recipients: 'secondary',
    retryCount: 1
  }
};
Step 10: Monitor SMS Usage
javascript
// sms-monitor.js
import { redisClient } from './cache/redisClient.js';

export async function monitorSMSUsage() {
  const today = new Date().toISOString().split('T')[0];
  const key = `sms:usage:${today}`;

  const usage = await redisClient.get(key) || 0;

  if (usage > 100) {
    console.warn(`⚠️ SMS usage high: ${usage} messages today`);
    // Trigger alert
  }

  return usage;
}
Step 11: Fallback SMS Provider (Optional)
For redundancy, configure a backup SMS provider:

env
# Backup SMS Provider (Twilio fallback)
BACKUP_SMS_PROVIDER=nexmo
NEXMO_API_KEY=your_nexmo_key
NEXMO_API_SECRET=your_nexmo_secret
NEXMO_PHONE_NUMBER=+27694567890
Step 12: SMS Delivery Logging
javascript
// sms-logger.js
import { createAuditLog } from './middleware/auditMiddleware.js';

export async function logSMSDelivery(recipient, status, messageId, error = null) {
  await createAuditLog({
    action: 'SMS_DELIVERY',
    category: 'NOTIFICATION',
    metadata: {
      recipient: recipient.substring(0, 4) + '****', // Redact for privacy
      status,
      messageId,
      error,
      provider: 'twilio',
      timestamp: new Date().toISOString()
    },
    status: status === 'delivered' ? 'SUCCESS' : 'FAILURE'
  });
}
Security Best Practices:
Never commit .env to version control

Rotate Auth Token every 90 days

Use environment-specific credentials (dev vs prod)

Enable IP whitelisting for API access

Monitor usage for abuse patterns

Set up budget alerts ($50/month threshold)

Use Twilio's Verify service for 2FA (separate from SMS alerts)

Cost Optimization:
Twilio Pricing:

SMS to South Africa: $0.0385 per message

SMS to International: $0.05-0.15 per message

Free monthly credit: $15 for new accounts

Optimization Strategies:

Batch messages for non-critical alerts
Use long codes for high volume (cheaper)
Implement intelligent throttling
Use webhooks for delivery status
Troubleshooting:
Error	Solution
"Account SID must start with AC"	Check ACCOUNT_SID format in .env
"Phone number not SMS-capable"	Buy SMS-capable number in Twilio console
"Insufficient credit"	Add payment method to Twilio account
"Invalid phone number format"	Use E.164 format: +27791234567
Production Checklist:
Account SID and Auth Token added to .env

SMS-capable phone number purchased

Team phone numbers added to ALERT_SMS_RECIPIENTS

Budget alert set ($50/month)

Usage monitoring implemented

Fallback SMS provider configured

Delivery logging enabled

Rate limiting configured

Webhook endpoint for incoming SMS (if needed)

Next Steps:
Test SMS sending with test-sms.js

Configure alert thresholds in SMS_ALERT_RULES

Set up on-call rotation schedule

Test emergency alert scenarios

Monitor initial usage patterns

WILSY OS - "Law knows no borders. Wilsy OS has no limits." 🚀
