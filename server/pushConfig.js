// server/pushConfig.js
const webPush = require('web-push');

const publicVapidKey = '<YOUR_PUBLIC_VAPID_KEY>';
const privateVapidKey = '<YOUR_PRIVATE_VAPID_KEY>';

webPush.setVapidDetails(
    'mailto:your-email@example.com',
    publicVapidKey,
    privateVapidKey
);

module.exports = webPush;
