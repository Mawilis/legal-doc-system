// server.js

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
const mongoose = require("mongoose");
require("dotenv").config();

const errorHandler = require("./middleware/errorMiddleware");
const apiLimiter = require("./middleware/rateLimiter");
const requestLogger = require("./middleware/requestLogger");
const logger = require("./utils/logger");

const app = express();

// --- Connect to MongoDB ---
const connectDB = async () => {
    try {
        mongoose.set("strictQuery", true);

        const shouldSkip =
            process.env.SKIP_CONNECT_DB === "true" &&
            process.env.NODE_ENV !== "test";

        if (shouldSkip) {
            logger.info("⏭️  Skipping DB connection due to SKIP_CONNECT_DB=true");
            return;
        }

        const mongoUri = process.env.MONGODB_URI;
        if (!mongoUri) {
            throw new Error("❌ MONGODB_URI is not defined in .env file.");
        }

        await mongoose.connect(mongoUri, {
            useNewUrlParser: true,
            useUnifiedTopology: true,
        });

        logger.info(`✅ MongoDB Connected: ${mongoose.connection.host}`);
    } catch (err) {
        logger.error(`❌ MongoDB connection error: ${err.message}`);
        process.exit(1);
    }
};

connectDB();

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
    "https://localhost:3001",
];

app.use(
    cors({
        origin: (origin, callback) => {
            if (!origin || allowedOrigins.includes(origin)) {
                callback(null, true);
            } else {
                logger.warn(`🚫 Blocked by CORS: ${origin}`);
                callback(new Error("Not allowed by CORS"));
            }
        },
        credentials: true,
    })
);

// --- Logging & Parsing ---
if (process.env.NODE_ENV === "development") {
    app.use(morgan("dev"));
}
app.use(express.json({ limit: "10kb" }));
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());
app.use(requestLogger);

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
app.use("/api/upload", require("./routes/fileUploadRoutes"));
app.use("/api/reports", require("./routes/reportRoutes"));
app.use("/api/chat", require("./routes/chatRoutes"));
app.use("/api/notifications", require("./routes/notificationRoutes"));
app.use("/api/dashboard", require("./routes/dashboardRoutes"));
app.use("/api/password", require("./routes/passwordRoutes"));
app.use("/api/settings", require("./routes/settingsRoutes"));
app.use("/api/analytics", require("./routes/analyticsRoutes"));
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
