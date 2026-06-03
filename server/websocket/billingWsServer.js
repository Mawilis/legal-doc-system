/**
 * ╔══════════════════════════════════════════════════════════════════════════╗
 * ║ WILSY OS - BILLING WEBSOCKET SERVER [V1.0.0-MARS]                        ║
 * ║ [GLOBAL_ROOT FORCED | NO AUTH REQUIRED | SOVEREIGN STREAM]              ║
 * ╚══════════════════════════════════════════════════════════════════════════╝
 */
import { WebSocketServer } from 'ws';
import http from 'http';

const server = http.createServer();
const wss = new WebSocketServer({ server, path: '/ws/billing' });

wss.on('connection', (ws, req) => {
  // Force sovereign context
  const tenant = 'GLOBAL_ROOT';
  console.log(`[BILLING-WS] Connection established for ${tenant}`);

  ws.send(JSON.stringify({ type: 'connected', tenant, timestamp: Date.now() }));

  ws.on('message', (data) => {
    // Echo or handle subscriptions
    try {
      const msg = JSON.parse(data);
      if (msg.type === 'subscribe') {
        ws.send(JSON.stringify({ type: 'subscribed', channel: msg.channel }));
      }
    } catch (e) {}
  });
});

server.listen(5050, () => {
  console.log('🛡️ Billing WebSocket running on ws://localhost:5050/ws/billing');
});
