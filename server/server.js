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
const logger = require('./utils/logger');
const swaggerJsDoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');
require('dotenv').config();

// Initialize Express application
const app = express();

// Swagger configuration
const swaggerOptions = {
    swaggerDefinition: {
        openapi: "3.0.0",
        info: {
            title: "Legal Document System API",
            version: "1.0.0",
            description: "API Documentation for Legal Document System",
            contact: {
                name: "Your Name",
                email: "your-email@example.com"
            }
        },
        servers: [
            {
                url: "https://localhost:3001",
                description: "Development server"
            }
        ],
    },
    apis: ["./server/routes/*.js"], // Path where your API documentation comments are.
};

const swaggerDocs = swaggerJsDoc(swaggerOptions);
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocs));

// Set SSL certificate paths and check if they exist
const sslKeyPath = process.env.SSL_KEY_PATH || '/path/to/your/key.pem';
const sslCertPath = process.env.SSL_CERT_PATH || '/path/to/your/cert.pem';

if (!fs.existsSync(sslKeyPath) || !fs.existsSync(sslCertPath)) {
    logger.error('Error: SSL key or certificate file not found.');
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
    .then(() => logger.info('Connected to MongoDB'))
    .catch((err) => {
        logger.error('Error connecting to MongoDB:', err);
        process.exit(1);
    });

// Middleware setup
app.use(helmet());
app.use(cors());
app.use(bodyParser.json());
app.use(express.json());

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
    logger.error('Error: VAPID keys are missing.');
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
    logger.info('User subscribed:', subscription);
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
        logger.error('Error sending notification:', error);
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
const clientBuildPath = path.join(__dirname, '..', 'client', 'build');
app.use(express.static(clientBuildPath));

// Root route to serve the client index.html
app.get('*', (req, res) => {
    res.sendFile(path.join(clientBuildPath, 'index.html'), (err) => {
        if (err) {
            logger.error('Failed to load index.html:', err);
            res.status(404).send('Page not found.');
        }
    });
});

// Import the global error handler
const globalErrorHandler = require('./globalErrorHandler');

// Use the global error handler
app.use(globalErrorHandler);

// Socket.io connection setup
io.on('connection', (socket) => {
    logger.info('User connected:', socket.id);

    socket.on('joinRoom', (room) => {
        socket.join(room);
        logger.info(`User joined room: ${room}`);
    });

    socket.on('sendMessage', (message) => {
        io.to(message.chatRoomId).emit('newMessage', message);
    });

    socket.on('newNotification', (notification) => {
        io.emit('newNotification', notification);
    });

    socket.on('disconnect', () => {
        logger.info('User disconnected:', socket.id);
    });
});

// Handle graceful server shutdown
process.on('SIGTERM', () => {
    server.close(() => {
        logger.info('Process terminated');
        mongoose.connection.close(() => {
            logger.info('MongoDB connection closed');
        });
    });
});

// Start server
const port = process.env.PORT || 3001;
server.listen(port, () => {
    logger.info(`Secure Server running on https://localhost:${port}`);
});
