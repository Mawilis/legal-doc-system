// server.js
const fs = require('fs');  // Required for SSL certificates
const https = require('https');  // HTTPS module
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const webPush = require('web-push');
const bodyParser = require('body-parser');
const { Server } = require('socket.io');
require('dotenv').config();  // To load .env variables

const app = express();

// Load SSL certificates
const httpsOptions = {
    key: fs.readFileSync('path/to/localhost-key.pem'),  // Replace with your key path
    cert: fs.readFileSync('path/to/localhost.pem')      // Replace with your certificate path
};

// Create HTTPS server
const server = https.createServer(httpsOptions, app);
const io = new Server(server, {
    cors: {
        origin: process.env.CLIENT_URL || 'http://localhost:3000',  // Allow requests from the frontend
        methods: ['GET', 'POST'],
        credentials: true  // Enable cookies and authorization headers
    }
});

// MongoDB connection
mongoose.connect(process.env.MONGODB_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
})
    .then(() => console.log('Connected to MongoDB'))
    .catch((err) => {
        console.error('Error connecting to MongoDB:', err);
        process.exit(1);  // Exit process if database connection fails
    });

// Middleware
app.use(cors());
app.use(express.json());
app.use(helmet());  // Adds security headers
app.use(bodyParser.json());  // Parse incoming requests with JSON payloads

// Rate Limiter Middleware for security (Limit requests from a single IP)
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000,  // 15 minutes
    max: 100,  // Limit each IP to 100 requests per windowMs
    message: 'Too many requests from this IP, please try again later.',
});
app.use(limiter);

// VAPID keys setup for Push Notifications
webPush.setVapidDetails(
    'mailto:your-email@example.com',  // Your email
    process.env.VAPID_PUBLIC_KEY,    // Loaded from .env
    process.env.VAPID_PRIVATE_KEY    // Loaded from .env
);

// In-memory notification store (replace with a database in production)
let notifications = [];

// Push notification subscribers array
const subscribers = [];

// Route for subscribing to push notifications
app.post('/api/subscribe', (req, res) => {
    const subscription = req.body;
    subscribers.push(subscription);
    res.status(201).json({});
    console.log('User subscribed:', subscription);
});

// Route for sending push notifications
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

// Routes for handling admin, auth, documents, and chat functionalities
const adminRoutes = require('./routes/adminRoutes');
const authRoutes = require('./routes/authRoutes');
const documentRoutes = require('./routes/documentRoutes');
const chatRoutes = require('./routes/chatRoutes');
const dashboardRoutes = require('./routes/dashboardRoutes');  // Add the dashboard route

// Apply routes
app.use('/api/admin', adminRoutes);
app.use('/api/auth', authRoutes);
app.use('/api/documents', documentRoutes);
app.use('/api/chat', chatRoutes);
app.use('/api/dashboard', dashboardRoutes);  // Apply dashboard route

// Handle WebSocket connections for real-time chat and notifications
io.on('connection', (socket) => {
    console.log('User connected:', socket.id);

    // Listen for fetching notification history
    socket.on('fetchNotifications', () => {
        // Emit the existing notification history
        socket.emit('notificationHistory', notifications);
    });

    // Listen for new notifications
    socket.on('new-notification', (notification) => {
        // Save the notification (in-memory for now, consider using a database)
        notifications.push(notification);

        // Broadcast the new notification to all connected clients
        io.emit('new-notification', notification);
    });

    socket.on('disconnect', () => {
        console.log('User disconnected:', socket.id);
    });
});

// Graceful shutdown of server and MongoDB connection
process.on('SIGTERM', () => {
    server.close(() => {
        console.log('Process terminated');
        mongoose.connection.close(() => {
            console.log('MongoDB connection closed');
        });
    });
});

// Start the server with HTTPS support
const port = process.env.PORT || 3001;
server.listen(port, () => {
    console.log(`Secure Server running on https://localhost:${port}`);
});
