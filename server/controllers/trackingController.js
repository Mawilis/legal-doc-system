const DispatchInstruction = require('../models/DispatchInstruction');
const Attempt = require('../models/Attempt');

exports.getLiveFleetData = async (req, res) => {
    try {
        // 1. Find all active instructions
        const activeJobs = await DispatchInstruction.find({ 
            status: { $in: ['in_progress', 'Pending Dispatch', 'completed', 'returned'] } 
        }).select('title caseNumber serviceType status urgency distanceKm');

        // 2. Find the LATEST GPS ping for each job
        const fleetData = await Promise.all(activeJobs.map(async (job) => {
            const lastAttempt = await Attempt.findOne({ instructionId: job._id })
                                             .sort({ at: -1 }); // Newest first
            
            // If no attempt yet, use a "base" location (Sandton Central for demo)
            // In prod, this would be the Sheriff's live phone GPS
            const position = lastAttempt ? lastAttempt.gps : { lat: -26.1076, lng: 28.0567 }; // Sandton
            
            return {
                id: job._id,
                caseNumber: job.caseNumber,
                title: job.title,
                type: job.serviceType,
                status: job.status,
                urgency: job.urgency,
                location: position,
                lastUpdate: lastAttempt ? lastAttempt.at : new Date(),
                outcome: lastAttempt ? lastAttempt.outcome : 'En Route'
            };
        }));

        res.status(200).json(fleetData);
    } catch (err) {
        res.status(500).json({ message: err.message });
    }
};
