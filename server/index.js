const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Routes
const dashboardRoute = require('./routes/dashboard');
app.use('/api/dashboard', dashboardRoute);

// Example Admin Route (you should implement other routes similarly)
const adminRoute = require('./routes/admin');
app.use('/api/admin', adminRoute);

// Example Documents Route
const documentsRoute = require('./routes/documents');
app.use('/api/documents', documentsRoute);

// Example Profile Route
const profileRoute = require('./routes/profile');
app.use('/api/profile', profileRoute);

// Example Chat Route
const chatRoute = require('./routes/chat');
app.use('/api/chat', chatRoute);

// Start Server
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
