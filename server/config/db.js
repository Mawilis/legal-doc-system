// server/config/db.js
const mongoose = require('mongoose');
const logger = require('../utils/logger'); // Assuming you have a logger utility

const connectDB = async () => {
    try {
        // Mongoose 7 has a new default for 'strictQuery'. Setting it explicitly prepares for the future.
        mongoose.set('strictQuery', true);

        // Connect to the MongoDB database using the URI from your .env file
        const conn = await mongoose.connect(process.env.MONGODB_URI);

        logger.info(`MongoDB Connected successfully to host: ${conn.connection.host}`);
    } catch (error) {
        // If the connection fails, log the error and terminate the application.
        // The server cannot run without a database connection.
        logger.error(`FATAL: MongoDB Connection Failed. ${error.message}`);
        process.exit(1);
    }
};

module.exports = connectDB;
