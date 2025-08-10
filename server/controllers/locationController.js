// ~/server/controllers/locationController.js

const Location = require('../models/locationModel');
const asyncHandler = require('../middleware/asyncHandler'); // Assuming you have an async handler utility

/**
 * @desc    Update or create a user's location (for sheriffs).
 * @route   POST /api/locations
 * @access  Private/Sheriff
 */
exports.updateLocation = asyncHandler(async (req, res, next) => {
    const { latitude, longitude } = req.body;
    const userId = req.user.id; // Get user ID from authenticated request for security

    if (latitude === undefined || longitude === undefined) {
        return res.status(400).json({ success: false, message: 'Latitude and longitude are required.' });
    }

    const locationData = { type: 'Point', coordinates: [longitude, latitude] };

    const updatedLocation = await Location.findOneAndUpdate(
        { user: userId },
        { location: locationData },
        { new: true, upsert: true, setDefaultsOnInsert: true }
    ).populate('user', 'name email');

    req.app.get('io').emit('sheriff:locationUpdated', updatedLocation);

    res.status(200).json({
        success: true,
        data: updatedLocation,
    });
});

/**
 * @desc    Get all last known locations of users (for admins).
 * @route   GET /api/locations
 * @access  Private/Admin
 */
exports.getAllLocations = asyncHandler(async (req, res, next) => {
    const locations = await Location.find().populate('user', 'name email role');

    res.status(200).json({
        success: true,
        count: locations.length,
        data: locations,
    });
});

/**
 * @desc    Get the historical location path for a specific user.
 * @route   GET /api/locations/history/:userId
 * @access  Private/Admin
 */
exports.getUserPath = asyncHandler(async (req, res, next) => {
    // Find all location entries for the specified user, sorted by time.
    const pathData = await Location.find({ user: req.params.userId }).sort({ createdAt: 'asc' });

    if (!pathData || pathData.length === 0) {
        return res.status(404).json({ success: false, message: 'No location history found for this user.' });
    }

    res.status(200).json({
        success: true,
        count: pathData.length,
        data: pathData,
    });
});
