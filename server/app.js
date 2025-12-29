'use strict';

require('dotenv').config();

const express = require("express");
const path = require("path");
const cors = require("cors");
const helmet = require("helmet");
const morgan = require("morgan");
const compression = require("compression");
const cookieParser = require("cookie-parser");
const xssClean = require("xss-clean");
const hpp = require("hpp");
const mongoSanitize = require("express-mongo-sanitize");

const errorHandler = require("./middleware/errorMiddleware");
const apiLimiter = require("./middleware/rateLimiter");
const logger = require("./utils/logger");

const { createProxyMiddleware } = require('http-proxy-middleware');
const bodyParser = require('body-parser');
const { randomUUID } = require('crypto');
const http = require('http');

// ---- Create app BEFORE creating http server ----
const app = express();

// --- Basic parsing & security middleware ---
app.use(bodyParser.json({ limit: '10kb' }));
app.use(bodyParser.urlencoded({ extended: true }));
app.use(helmet());
app.use(mongoSanitize());
app.use(xssClean());
app.use(hpp());
app.use(compression());
app.use(cookieParser());

// --- Logging ---
if (process.env.NODE_ENV === "development") {
  app.use(morgan("dev"));
}

// --- CORS Setup (preflight + allowed origins) ---
const allowedOrigins = process.env.CORS_ORIGINS ? process.env.CORS_ORIGINS.split(',') : [
  "http://localhost:3000",
  "https://localhost:3000",
  "http://localhost:3001",
  "https://localhost:3001"
];

app.use(cors({
  origin: (origin, callback) => {
    if (!origin) return callback(null, true);
    if (allowedOrigins.includes('*') || allowedOrigins.includes(origin)) return callback(null, true);
    logger && logger.warn && logger.warn(`Blocked by CORS: ${origin}`);
    return callback(new Error('CORS policy: Origin not allowed'));
  },
  credentials: true,
  methods: ['GET','POST','PUT','PATCH','DELETE','OPTIONS'],
  allowedHeaders: ['Content-Type','Authorization','x-request-id','x-tenant-id']
}));
app.options('*', (req, res) => res.sendStatus(204));

// --- Request ID middleware ---
app.use((req, res, next) => {
  req.requestId = req.headers['x-request-id'] || randomUUID();
  res.setHeader('x-request-id', req.requestId);
  next();
});

// --- Rate Limiting ---
app.use("/api", apiLimiter);

// --- Static Files ---
app.use(express.static(path.join(__dirname, "public")));
app.use("/uploads", express.static(path.join(__dirname, "../uploads")));

// --- Routes (existing) ---
app.use("/api/users", require("./routes/userRoutes"));
app.use("/api/clients", require("./routes/clientRoutes"));
app.use("/api/deputies", require("./routes/deputyRoutes"));
app.use("/api/documents", require("./routes/documentRoutes"));
app.use("/api/instructions", require("./routes/instructionRoutes"));
app.use("/api/invoices", require("./routes/invoiceRoutes"));
app.use("/api/chat", require("./routes/chatRoutes"));
app.use("/api/dashboard", require("./routes/dashboardRoutes"));
app.use("/api/notifications", require("./routes/notificationRoutes"));
app.use("/api/password", require("./routes/passwordRoutes"));
app.use("/api/settings", require("./routes/settingsRoutes"));
app.use("/api/upload", require("./routes/fileUploadRoutes"));
app.use("/api/analytics", require("./routes/analyticsRoutes"));
app.use("/api/reports", require("./routes/reportRoutes"));
app.use("/api/ai", require("./routes/aiRoutes"));
app.use("/api/search", require("./routes/searchRoutes"));

// --- Serve Frontend in Production ---
if (process.env.NODE_ENV === "production") {
  const clientBuildPath = path.join(__dirname, "..", "client", "build");
  app.use(express.static(clientBuildPath));
  app.get("*", (req, res) => {
    res.sendFile(path.resolve(clientBuildPath, "index.html"));
  });
}

// --- API 404 ---
app.use('/api', (req, res) => res.status(404).json({ message: 'Not Found', path: req.originalUrl, requestId: req.requestId }));

// --- Error Handler ---
app.use(errorHandler);

// --- Create HTTP server AFTER app is defined and start listening ---
const PORT = process.env.PORT || 3001;
const httpServer = http.createServer(app);

httpServer.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 [Wilsy Gateway] Epitome Routing Online (All Bridges Active) on port ${PORT}`);
});

module.exports = app;
