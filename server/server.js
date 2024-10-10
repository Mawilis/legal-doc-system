// File: /server.js

// Import required modules for the server setup
const fs = require('fs'); // Required for reading SSL certificate files
const https = require('https'); // HTTPS module for creating a secure server
const path = require('path'); // Module to handle and manipulate file paths
const express = require('express'); // Framework for building the server and handling routes
const mongoose = require('mongoose'); // ODM library for MongoDB interactions
const cors = require('cors'); // Cross-Origin Resource Sharing (CORS) middleware
const helmet = require('helmet'); // Security middleware to set various HTTP headers
const rateLimit = require('express-rate-limit'); // Middleware to limit repeated requests
const bodyParser = require('body-parser'); // Middleware for parsing incoming request bodies
const webPush = require('web-push'); // Library for Web Push Notifications
const socket = require('./utils/socket'); // Import socket utility for Socket.io setup
require('dotenv').config(); // Load environment variables from .env file

// Initialize Express application
const app = express();

// Define absolute paths for the SSL certificate files
const sslKeyPath = '/Users/wilsonkhanyezi/legal-doc-system/server/ssl-certificates/localhost-key.pem';
const sslCertPath = '/Users/wilsonkhanyezi/legal-doc-system/server/ssl-certificates/localhost.pem';

// Log the SSL certificate paths to verify correctness
console.log('SSL Key Path:', sslKeyPath);
console.log('SSL Cert Path:', sslCertPath);

// Check if the SSL key and certificate files exist
if (!fs.existsSync(sslKeyPath) || !fs.existsSync(sslCertPath)) {
    console.error(`Error: SSL key or certificate file not found.`);
    process.exit(1); // Exit the application if files are missing
}

try {
    // Read SSL key and certificate files to set up HTTPS server options
    const sslKey = fs.readFileSync(sslKeyPath);
    const sslCert = fs.readFileSync(sslCertPath);

    // Define HTTPS server options using the loaded key and certificate
    const httpsOptions = {
        key: sslKey,
        cert: sslCert,
    };

    // Create a secure HTTPS server with the provided options
    const server = https.createServer(httpsOptions, app);

    // Initialize Socket.io using the HTTP/HTTPS server instance
    const io = socket.init(server);

    // Connect to MongoDB using Mongoose
    mongoose.connect(process.env.MONGODB_URI, {
        useNewUrlParser: true,
        useUnifiedTopology: true,
    })
        .then(() => console.log('Connected to MongoDB'))
        .catch((err) => {
            console.error('Error connecting to MongoDB:', err);
            process.exit(1);
        });

    // Set up middleware for security and data handling
    app.use(cors()); // Enable CORS to allow cross-origin requests
    app.use(express.json()); // Parse incoming JSON requests
    app.use(helmet()); // Add security-related HTTP headers
    app.use(bodyParser.json()); // Parse incoming request bodies in JSON format

    // Implement rate limiter to prevent abuse of the server by limiting repeated requests
    const limiter = rateLimit({
        windowMs: 15 * 60 * 1000, // Time window for rate limiting (15 minutes)
        max: 100, // Maximum number of requests per IP address within the time window
        message: 'Too many requests from this IP, please try again later.',
    });
    app.use(limiter);

    // Web Push Notifications setup
    const vapidPublicKey = process.env.VAPID_PUBLIC_KEY;
    const vapidPrivateKey = process.env.VAPID_PRIVATE_KEY;

    if (!vapidPublicKey || !vapidPrivateKey) {
        console.error('Error: VAPID keys are missing.');
        process.exit(1);
    }

    webPush.setVapidDetails('mailto:your-email@example.com', vapidPublicKey, vapidPrivateKey);

    // Routes for push notifications
    let notifications = [];
    const subscribers = [];

    app.post('/api/subscribe', (req, res) => {
        const subscription = req.body;
        subscribers.push(subscription);
        res.status(201).json({});
        console.log('User subscribed:', subscription);
    });

    app.post('/api/notify', async (req, res) => {
        const notificationPayload = {
            title: 'New Notification',
            body: 'You have a new message!',
            icon: '/icon.png',
        };

        const promises = subscribers.map(subscription =>
            webPush.sendNotification(subscription, JSON.stringify(notificationPayload))
        );

        try {
            await Promise.all(promises);
            res.status(200).json({ message: 'Notification sent successfully' });
        } catch (error) {
            console.error('Error sending notification:', error);
            res.status(500).json({ message: 'Error sending notification' });
        }
    });

    // Import and use route handlers for different functionalities
    const adminRoutes = require('./routes/adminRoutes');
    const authRoutes = require('./routes/authRoutes');
    const documentRoutes = require('./routes/documentRoutes');
    const chatRoutes = require('./routes/chatRoutes');
    const dashboardRoutes = require('./routes/dashboardRoutes');

    app.use('/api/admin', adminRoutes);
    app.use('/api/auth', authRoutes);
    app.use('/api/documents', documentRoutes);
    app.use('/api/chat', chatRoutes);
    app.use('/api/dashboard', dashboardRoutes);

    // Serve static files from the client build directory (if you're using a frontend build)
    const clientBuildPath = path.join(__dirname, 'client', 'build');
    app.use(express.static(clientBuildPath));

    // Root route to handle requests to `/` and serve the client index.html if it exists
    app.get('/', (req, res) => {
        res.sendFile(path.join(clientBuildPath, 'index.html'), (err) => {
            if (err) {
                console.error('Failed to load root index.html:', err);
                res.status(404).send('Page not found.');
            }
        });
    });

    // Handle undefined routes with a 404 error message
    app.use((req, res) => {
        res.status(404).send({ message: 'Resource not found' });
    });

    // Handle WebSocket connections for real-time chat and notifications
    io.on('connection', (socket) => {
        console.log('User connected:', socket.id);

        // Handle joining a chat room
        socket.on('joinRoom', (room) => {
            socket.join(room);
            console.log(`User joined room: ${room}`);
        });

        socket.on('sendMessage', (message) => {
            io.to(message.chatRoomId).emit('newMessage', message);
        });

        socket.on('newNotification', (notification) => {
            io.emit('newNotification', notification);
        });

        socket.on('disconnect', () => {
            console.log('User disconnected:', socket.id);
        });
    });

    // Handle process termination gracefully by closing server and MongoDB connection
    process.on('SIGTERM', () => {
        server.close(() => {
            console.log('Process terminated');
            mongoose.connection.close(() => {
                console.log('MongoDB connection closed');
            });
        });
    });

    // Start the server and listen on the specified port (default: 3001)
    const port = process.env.PORT || 3001;
    server.listen(port, () => {
        console.log(`Secure Server running on https://localhost:${port}`);
    });
} catch (error) {
    console.error('Failed to load SSL certificates:', error);
    process.exit(1);
}
