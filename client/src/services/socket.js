// ~/client/src/services/socket.js
import { io } from 'socket.io-client';

// --- CONFIGURATION ---
const RAW_API_ORIGIN = process.env.REACT_APP_SERVER_URL || 'http://localhost:3001';
const SOCKET_ORIGIN = RAW_API_ORIGIN.replace(/\/api\/?$/i, '');

console.log('🔌 [SocketService] Configured Origin:', SOCKET_ORIGIN);

// --- SINGLETON INSTANCE ---
export const socket = io(SOCKET_ORIGIN, {
  path: '/socket.io',
  transports: ['websocket'],
  autoConnect: false, // Critical: Wait for login
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
});

// --- LISTENERS (Global) ---
socket.on('connect', () => {
  console.log('✅ [Socket] CONNECTED:', socket.id);
});

socket.on('disconnect', (reason) => {
  console.warn('⚠️ [Socket] DISCONNECTED:', reason);
});

socket.on('connect_error', (err) => {
  console.error('❌ [Socket] CONNECTION ERROR:', err.message);
});

/**
 * CONNECT FUNCTION
 * Call this ONLY after login when you have a valid token.
 */
export const connectSocket = (token) => {
  if (!token) {
    console.warn('🚫 [Socket] Cannot connect: No token provided.');
    return;
  }

  if (socket.connected) {
    console.log('ℹ️ [Socket] Already connected.');
    return;
  }

  console.log('🔌 [Socket] Connecting with token...');
  socket.auth = { token };
  socket.connect();
};

/**
 * DISCONNECT FUNCTION
 */
export const disconnectSocket = () => {
  if (socket.connected) {
    console.log('🔌 [Socket] Disconnecting...');
    socket.disconnect();
  }
};

/**
 * HELPER: Wait for connection (Used by Chat.jsx)
 */
export const waitUntilConnected = (timeoutMs = 5000) => {
  if (socket.connected) return Promise.resolve();

  console.log('[socket] Waiting for connection...');
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      cleanup();
      reject(new Error('Socket connection timeout'));
    }, timeoutMs);

    const onConnect = () => {
      cleanup();
      resolve();
    };

    const onErr = (err) => {
      cleanup();
      reject(err);
    };

    function cleanup() {
      clearTimeout(timer);
      socket.off('connect', onConnect);
      socket.off('connect_error', onErr);
    }

    socket.once('connect', onConnect);
    socket.once('connect_error', onErr);
  });
};

/**
 * HELPER: Send Chat Message (Used by Chat.jsx)
 */
export const sendChatMessage = (payload) => {
  return new Promise((resolve, reject) => {
    if (!socket.connected) {
      return reject(new Error('Socket not connected'));
    }

    socket.timeout(5000).emit('chat:message', payload, (err, response) => {
      if (err) {
        console.error('❌ [Socket] Chat Send Timeout/Error:', err);
        return reject(err);
      }
      resolve(response);
    });
  });
};

/**
 * HELPER: Debug Snapshot (Used by Chat.jsx)
 */
export const snapshotSocket = () => {
  return {
    connected: socket.connected,
    id: socket.id,
    auth: socket.auth ? 'present' : 'missing',
    transport: socket.io?.engine?.transport?.name
  };
};

export default socket;