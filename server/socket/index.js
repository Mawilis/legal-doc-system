/* eslint-disable */
/*
 * File: server/socket/index.js
 * -----------------------------------------------------------------------------
 * STATUS: EPITOME | Real-Time Nervous System (Secure & Isolated)
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - SECURITY: Middleware intercepts handshake and validates JWT.
 * - ISOLATION: Automatically joins users to 'Tenant' and 'Role' rooms.
 * - LOGGING: Tracks specific users (Name/ID) instead of random socket IDs.
 * -----------------------------------------------------------------------------
 */

import jwt from 'jsonwebtoken';
import { Server } from 'socket.io';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.resolve(__dirname, '../.env') });

/**
 * @function readSocketEnvList
 * @description Reads comma-separated websocket origin keys from server/.env.
 * @param {Array<string>} keys - Candidate environment keys.
 * @returns {Array<string>} Allowed origin list.
 * @collaboration Keeps realtime CORS policy deployment-owned instead of hardcoded in the socket source.
 */
const readSocketEnvList = (keys = []) => {
  const key = keys.find(candidate => process.env[candidate]);
  return key ? process.env[key].split(',').map(origin => origin.trim()).filter(Boolean) : [];
};

/**
 * @function requireSocketEnv
 * @description Resolves a mandatory socket secret from server/.env.
 * @param {string} key - Required environment key.
 * @returns {string} Environment value.
 * @collaboration Websocket authentication must never fall back to a source-code JWT secret.
 */
const requireSocketEnv = (key) => {
  const value = process.env[key];
  if (!value) throw new Error(`Missing required server/.env key: ${key}`);
  return value;
};

/**
 * @function resolveSocketOrigins
 * @description Resolves allowed websocket origins from server/.env with development-only local fallback.
 * @returns {Array<string>} Allowed websocket origins.
 * @collaboration Production tenants must connect through declared origins only.
 */
const resolveSocketOrigins = () => {
  const origins = readSocketEnvList(['CLIENT_URL', 'CORS_ORIGIN', 'CORS_ORIGINS']);
  if (origins.length) return origins;
  if (process.env.NODE_ENV !== 'production') return ['http://localhost:3000', 'http://127.0.0.1:3000'];
  throw new Error('Missing CLIENT_URL or CORS_ORIGIN in server/.env for production websocket CORS.');
};

/**
 * @function createSocketServer
 * @description Creates the tenant-isolated websocket server with JWT authentication.
 * @param {import('http').Server} httpServer - HTTP server instance.
 * @returns {Server} Socket.IO server.
 * @collaboration Realtime Wilsy OS events must be tenant-isolated, role-aware and backed by env-owned secrets.
 */
const createSocketServer = (httpServer) => {
  // 1. CONFIGURATION
  const allowedOrigins = resolveSocketOrigins();

  const io = new Server(httpServer, {
    cors: {
      origin: allowedOrigins,
      methods: ['GET', 'POST'],
      credentials: true,
    },
  });

  // 2. MIDDLEWARE: SECURITY GATEKEEPER
  // This runs BEFORE a connection is accepted.
  io.use((socket, next) => {
    const { token } = socket.handshake.auth;

    if (!token) {
      console.warn(`⛔ [Socket] Blocked connection attempt (No Token): ${socket.id}`);
      return next(new Error('Authentication Error: Token missing'));
    }

    try {
      // Verify Token against Secret
      const secret = requireSocketEnv('JWT_SECRET');
      const decoded = jwt.verify(token, secret);

      // Attach Identity to Socket Session
      socket.user = {
        id: decoded.id || decoded._id,
        name: decoded.name || 'Unknown Agent',
        role: decoded.role,
        tenantId: decoded.tenantId,
      };

      next(); // Access Granted
    } catch (err) {
      console.warn(`⛔ [Socket] Blocked invalid token from ${socket.id}`);
      next(new Error('Authentication Error: Invalid Token'));
    }
  });

  // 3. CONNECTION LIFECYCLE
  io.on('connection', (socket) => {
    const { name, role, tenantId } = socket.user;

    // A. JOIN SECURE ROOMS
    // 1. Tenant Room: Broadcasts only to this firm (e.g., "wilsy")
    socket.join(tenantId);
    // 2. Role Room: Broadcasts only to this rank (e.g., "sheriff")
    socket.join(`role:${role}`);
    // 3. Personal Room: Direct messages
    socket.join(socket.user.id);

    console.log(`🔌 [Socket] Connected: ${name} (${role}) | 🏢 Tenant: ${tenantId}`);

    // B. HANDLING DISCONNECT
    socket.on('disconnect', (reason) => {
      console.log(`🔌 [Socket] Disconnected: ${name} | Reason: ${reason}`);
    });

    // C. ERROR LOGGING
    socket.on('error', (err) => {
      console.error(`❌ [Socket] Error on ${name}:`, err);
    });
  });

  return io;
};

export default createSocketServer;
