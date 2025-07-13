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

const app = express();

// --- Security Middleware ---
app.use(helmet());
app.use(mongoSanitize());
app.use(xssClean());
app.use(hpp());
app.use(compression());

// --- CORS Setup ---
const allowedOrigins = [
    "http://localhost:3000",
    "https://localhost:3000",
    "http://localhost:3001",
    "https://localhost:3001"
];
app.use(cors({
    origin: (origin, callback) => {
        if (!origin || allowedOrigins.includes(origin)) {
            callback(null, true);
        } else {
            logger.warn(`Blocked by CORS: ${origin}`);
            callback(new Error("Not allowed by CORS"));
        }
    },
    credentials: true
}));

// --- Logging & Parsing ---
if (process.env.NODE_ENV === "development") {
    app.use(morgan("dev"));
}
app.use(express.json({ limit: "10kb" }));
app.use(express.urlencoded({ extended: true })); // Allow form submissions
app.use(cookieParser());

// --- Rate Limiting ---
app.use("/api", apiLimiter);

// --- Static Files ---
app.use(express.static(path.join(__dirname, "public")));
app.use("/uploads", express.static(path.join(__dirname, "../uploads")));

// --- Routes ---
app.use("/api/auth", require("./routes/authRoutes"));
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

// --- Error Handler ---
app.use(errorHandler);

module.exports = app;
