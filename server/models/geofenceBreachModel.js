// ~/server/models/geofenceBreachModel.js

const mongoose = require('mongoose');

/**
 * @file This file defines the Mongoose schema for a geofence breach event.
 * It is designed to create a detailed, auditable record every time a user
 * leaves a designated operational zone.
 */

const geofenceBreachSchema = new mongoose.Schema({
    // A required reference to the user who breached the geofence.
    // Indexing this field improves performance when querying for a specific user's breach history.
    user: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User', // This should match the name of your User model
        required: true,
        index: true,
    },
    // The location is stored in the official GeoJSON Point format.
    // This is the standard and most powerful way to store geospatial data in MongoDB.
    coords: {
        type: {
            type: String,
            enum: ['Point'], // 'coords.type' must be 'Point'
            required: true,
        },
        coordinates: {
            type: [Number], // Array of numbers for [longitude, latitude]
            required: true,
        },
    },
    // The name of the zone that was breached, for more descriptive logs.
    breachedZone: {
        type: String,
        required: true,
    },
    // A flag to indicate if an alert was successfully sent for this breach.
    alerted: {
        type: Boolean,
        default: false,
    },
}, {
    // Mongoose's built-in timestamp option automatically adds `createdAt` and `updatedAt` fields.
    timestamps: true,
});

// Compile the schema into a Mongoose model.
const GeofenceBreach = mongoose.model('GeofenceBreach', geofenceBreachSchema);

module.exports = GeofenceBreach;
