// ~/legal-doc-system/server/server.js

// **Import Required Modules**
const fs = require('fs');
const https = require('https');
const path = require('path');
const express = require('express');
const mongoose = require('mongoose');
const dotenv = require('dotenv');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const morgan = require('morgan'); // HTTP request logger middleware
const compression = require('compression'); // Compression middleware
const cookieParser = require('cookie-parser'); // Parse Cookie header
const xssClean = require('xss-clean'); // Prevent XSS attacks
const hpp = require('hpp'); // HTTP Parameter Pollution protection
const mongoSanitize = require('express-mongo-sanitize'); // Prevent NoSQL injection
const webPush = require('web-push'); // Web Push Notifications
const socketIO = require('socket.io'); // Real-time communication
const logger = require('./utils/logger'); // Custom logger (e.g., Winston)
const swaggerJsDoc = require('swagger-jsdoc'); // API documentation
const swaggerUi = require('swagger-ui-express'); // Swagger UI
const errorHandler = require('./middleware/errorMiddleware'); // Global error handler

// **Load Environment Variables**
dotenv.config(); // Loads .env by default from the current directory

// **Verify VAPID Keys for Debugging (Temporary)**
// Uncomment the following lines to verify VAPID keys are loaded
//console.log('VAPID_PUBLIC_KEY:', process.env.VAPID_PUBLIC_KEY);
//console.log('VAPID_PRIVATE_KEY:', process.env.VAPID_PRIVATE_KEY);

// **Initialize Express Application**
const app = express();

// **Set Security HTTP Headers**
app.use(helmet());

// **Enable CORS with Options**
const allowedOrigins = [
    'https://localhost:3000', // React frontend running on HTTPS
    'https://your-frontend-domain.com', // Replace with your actual frontend domain
];

const corsOptions = {
    origin: function (origin, callback) {
        if (!origin) return callback(null, true); // Allow server-to-server or mobile app requests
        if (allowedOrigins.includes(origin)) {
            return callback(null, true);
        } else {
            const msg = `The CORS policy does not allow access from origin ${origin}`;
            return callback(new Error(msg), false);
        }
    },
    credentials: true, // Allow cookies and authentication headers
};
app.use(cors(corsOptions));
app.options('*', cors(corsOptions)); // Handle preflight requests

// **Data Sanitization against NoSQL Injection and XSS**
app.use(mongoSanitize());
app.use(xssClean());

// **Prevent Parameter Pollution**
app.use(
    hpp({
        whitelist: [], // Add parameters that you want to allow duplicates for
    })
);

// **Compress Responses**
app.use(compression());

// **HTTP Request Logger**
if (process.env.NODE_ENV === 'development') {
    app.use(morgan('dev'));
}

// **Parse JSON and Cookie Data**
app.use(express.json({ limit: '10kb' })); // Body parser, reading data from body into req.body
app.use(cookieParser());

// **Rate Limiting to Prevent DDoS Attacks**
const limiter = rateLimit({
    max: 1000, // Limit each IP to 1000 requests per windowMs
    windowMs: 15 * 60 * 1000, // 15 minutes
    message: 'Too many requests from this IP, please try again after 15 minutes.',
});
app.use('/api', limiter); // Apply rate limiting to all API routes

// **Serve Static Files**
app.use(express.static(path.join(__dirname, 'public')));

// **Swagger API Documentation Setup**
const swaggerOptions = {
    swaggerDefinition: {
        openapi: '3.0.0',
        info: {
            title: 'Legal Document System API',
            version: '1.0.0',
            description: 'API Documentation for Legal Document System',
            contact: {
                name: 'Wilsy',
                email: 'wilsy.wk@gmail.com', // Updated contact email
            },
        },
        servers: [
            {
                url: `https://localhost:${process.env.PORT || 3001}`,
                description: 'Development server',
            },
        ],
    },
    apis: ['./routes/*.js'], // Path to the API docs
};

const swaggerDocs = swaggerJsDoc(swaggerOptions);
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocs));

// **VAPID Keys Setup for Web Push Notifications**
const vapidPublicKey = process.env.VAPID_PUBLIC_KEY;
const vapidPrivateKey = process.env.VAPID_PRIVATE_KEY;

if (!vapidPublicKey || !vapidPrivateKey) {
    logger.error('Error: VAPID keys are missing.');
    process.exit(1);
}

webPush.setVapidDetails(
    'mailto:wilsy.wk@gmail.com', // Updated contact email
    vapidPublicKey,
    vapidPrivateKey
);

// **Web Push Notification Routes**
let subscribers = [];

app.post('/api/subscribe', (req, res) => {
    const subscription = req.body;
    subscribers.push(subscription);
    res.status(201).json({});
    logger.info('User subscribed for notifications.');
});

app.post('/api/notify', async (req, res) => {
    const notificationPayload = {
        title: 'New Notification',
        body: req.body.message || 'You have a new message!',
        icon: '/icon.png',
    };

    const sendNotifications = subscribers.map((subscription) =>
        webPush.sendNotification(subscription, JSON.stringify(notificationPayload))
    );

    try {
        await Promise.all(sendNotifications);
        res.status(200).json({ message: 'Notification sent successfully' });
    } catch (error) {
        logger.error('Error sending notification:', error);
        res.status(500).json({ message: 'Error sending notification' });
    }
});

// **Import Route Handlers**
const adminRoutes = require('./routes/adminRoutes');
const authRoutes = require('./routes/authRoutes');
const documentRoutes = require('./routes/documentRoutes');
const chatRoutes = require('./routes/chatRoutes');
const dashboardRoutes = require('./routes/dashboardRoutes');

// **Mount Routes**
app.use('/api/admin', adminRoutes);
app.use('/api/auth', authRoutes);
app.use('/api/documents', documentRoutes);
app.use('/api/chat', chatRoutes);
app.use('/api/dashboard', dashboardRoutes);

// **Serve Client Build Files for React App**
const clientBuildPath = path.join(__dirname, '..', 'client', 'build');
app.use(express.static(clientBuildPath));

// **Handle Unhandled Routes (Serve React App)**
app.get('*', (req, res) => {
    res.sendFile(path.join(clientBuildPath, 'index.html'), (err) => {
        if (err) {
            logger.error('Failed to load index.html:', err);
            res.status(404).send('Page not found.');
        }
    });
});

// **Global Error Handling Middleware**
app.use(errorHandler);

// **SSL Certificate Configuration**
const sslKeyPath = process.env.SSL_KEY_PATH || './ssl/key.pem';
const sslCertPath = process.env.SSL_CERT_PATH || './ssl/cert.pem';

// **Check if SSL Certificates Exist**
if (!fs.existsSync(sslKeyPath) || !fs.existsSync(sslCertPath)) {
    logger.error('SSL key or certificate file not found.');
    process.exit(1);
}

// **Read SSL Certificate Files**
const sslOptions = {
    key: fs.readFileSync(path.resolve(__dirname, sslKeyPath)),
    cert: fs.readFileSync(path.resolve(__dirname, sslCertPath)),
};

// **Create HTTPS Server**
const server = https.createServer(sslOptions, app);

// **Initialize Socket.io for Real-time Communication**
const io = socketIO(server, {
    cors: {
        origin: function (origin, callback) {
            if (!origin) return callback(null, true);
            if (allowedOrigins.includes(origin)) {
                return callback(null, true);
            } else {
                const msg = `Socket.io CORS policy does not allow access from origin ${origin}`;
                return callback(new Error(msg), false);
            }
        },
        methods: ['GET', 'POST'],
        credentials: true,
    },
});

// **Socket.io Connection Handling**
io.on('connection', (socket) => {
    logger.info('User connected via Socket.io:', socket.id);

    // **Join Room Event**
    socket.on('joinRoom', (room) => {
        socket.join(room);
        logger.info(`User ${socket.id} joined room: ${room}`);
    });

    // **Send Message Event**
    socket.on('sendMessage', (message) => {
        io.to(message.chatRoomId).emit('newMessage', message);
    });

    // **New Notification Event**
    socket.on('newNotification', (notification) => {
        io.emit('newNotification', notification);
    });

    // **Disconnect Event**
    socket.on('disconnect', () => {
        logger.info('User disconnected:', socket.id);
    });
});

// **Database Connection**
const DB = process.env.MONGODB_URI.replace(
    '<PASSWORD>',
    process.env.MONGODB_PASSWORD
);

mongoose
    .connect(DB, {
        useNewUrlParser: true,
        useUnifiedTopology: true,
    })
    .then(() => logger.info('Connected to MongoDB'))
    .catch((err) => {
        logger.error('Error connecting to MongoDB:', err);
        process.exit(1);
    });

// **Handle Graceful Server Shutdown**
process.on('SIGTERM', () => {
    logger.info('SIGTERM signal received: closing HTTPS server');
    server.close(() => {
        logger.info('HTTPS server closed');
        mongoose.connection.close(false, () => {
            logger.info('MongoDB connection closed');
            process.exit(0);
        });
    });
});

// **Start Server**
const port = process.env.PORT || 3001;
server.listen(port, () => {
    logger.info(`Secure Server running on https://localhost:${port}`);
});

// **Handle Uncaught Exceptions and Rejections**
process.on('unhandledRejection', (err) => {
    logger.error('Unhandled Rejection:', err);
    server.close(() => {
        process.exit(1);
    });
});

process.on('uncaughtException', (err) => {
    logger.error('Uncaught Exception:', err);
    server.close(() => {
        process.exit(1);
    });
});
