const Analytics = require('../models/analyticsModel');

exports.trackUsage = async (req, res, next) => {
    try {
        const { userId, action } = req.body;
        const newRecord = await Analytics.create({ userId, action, timestamp: new Date() });
        res.status(201).json(newRecord);
    } catch (error) {
        next(new CustomError('Failed to track analytics', 500));
    }
};
