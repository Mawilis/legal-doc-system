// File: /server.js

// Import required modules
const fs = require('fs');
const https = require('https');
const path = require('path');
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const bodyParser = require('body-parser');
const webPush = require('web-push');
const socket = require('./utils/socket');
require('dotenv').config();

// Initialize Express application
const app = express();

// Set SSL certificate paths and check if they exist
const sslKeyPath = process.env.SSL_KEY_PATH || '/path/to/your/key.pem';
const sslCertPath = process.env.SSL_CERT_PATH || '/path/to/your/cert.pem';

if (!fs.existsSync(sslKeyPath) || !fs.existsSync(sslCertPath)) {
    console.error('Error: SSL key or certificate file not found.');
    process.exit(1);
}

// Read SSL certificate files
const sslOptions = {
    key: fs.readFileSync(sslKeyPath),
    cert: fs.readFileSync(sslCertPath),
};

// Create a secure HTTPS server
const server = https.createServer(sslOptions, app);

// Initialize Socket.io with HTTPS server instance
const io = socket.init(server);

// Connect to MongoDB
mongoose
    .connect(process.env.MONGODB_URI, {
        useNewUrlParser: true,
        useUnifiedTopology: true,
    })
    .then(() => console.log('Connected to MongoDB'))
    .catch((err) => {
        console.error('Error connecting to MongoDB:', err);
        process.exit(1);
    });

// Middleware setup
app.use(helmet()); // Add security-related HTTP headers
app.use(cors()); // Enable CORS
app.use(bodyParser.json()); // Parse incoming JSON requests
app.use(express.json()); // Additional JSON parser

// Rate Limiter - Protect against DDoS
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 100,
    message: 'Too many requests from this IP, please try again later.',
});
app.use(limiter);

// VAPID keys setup for Web Push
const vapidPublicKey = process.env.VAPID_PUBLIC_KEY;
const vapidPrivateKey = process.env.VAPID_PRIVATE_KEY;

if (!vapidPublicKey || !vapidPrivateKey) {
    console.error('Error: VAPID keys are missing.');
    process.exit(1);
}

webPush.setVapidDetails(
    'mailto:your-email@example.com',
    vapidPublicKey,
    vapidPrivateKey
);

// Web Push Notification routes
let subscribers = [];
app.post('/api/subscribe', (req, res) => {
    const subscription = req.body;
    subscribers.push(subscription);
    res.status(201).json({});
    console.log('User subscribed:', subscription);
});

app.post('/api/notify', async (req, res) => {
    const notificationPayload = {
        title: 'New Notification',
        body: req.body.message || 'You have a new message!',
        icon: '/icon.png',
    };

    const sendNotificationPromises = subscribers.map((subscription) =>
        webPush.sendNotification(subscription, JSON.stringify(notificationPayload))
    );

    try {
        await Promise.all(sendNotificationPromises);
        res.status(200).json({ message: 'Notification sent successfully' });
    } catch (error) {
        console.error('Error sending notification:', error);
        res.status(500).json({ message: 'Error sending notification' });
    }
});

// Import and use route handlers
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

// Serve static client build files
const clientBuildPath = path.join(__dirname, 'client', 'build');
app.use(express.static(clientBuildPath));

// Root route to serve the client index.html
app.get('/', (req, res) => {
    res.sendFile(path.join(clientBuildPath, 'index.html'), (err) => {
        if (err) {
            console.error('Failed to load index.html:', err);
            res.status(404).send('Page not found.');
        }
    });
});

// Catch-all for undefined routes - 404 handling
app.use((req, res) => {
    res.status(404).json({ message: 'Resource not found' });
});

// Error Handling Middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ message: 'An error occurred on the server' });
});

// Socket.io connection setup
io.on('connection', (socket) => {
    console.log('User connected:', socket.id);

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

// Handle graceful server shutdown
process.on('SIGTERM', () => {
    server.close(() => {
        console.log('Process terminated');
        mongoose.connection.close(() => {
            console.log('MongoDB connection closed');
        });
    });
});

// Start server
const port = process.env.PORT || 3001;
server.listen(port, () => {
    console.log(`Secure Server running on https://localhost:${port}`);
});
