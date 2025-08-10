const GeofenceBreach = require('../models/geofenceBreachModel');

/**
 * GET /api/geofence/breaches
 */
async function getBreaches(req, res, next) {
    try {
        const page = Math.max(parseInt(req.query.page || '1', 10), 1);
        const limit = Math.min(Math.max(parseInt(req.query.limit || '50', 10), 1), 200);
        const skip = (page - 1) * limit;

        const [items, total] = await Promise.all([
            GeofenceBreach.find()
                .populate('user', 'name email role')
                .sort({ occurredAt: -1 })
                .skip(skip)
                .limit(limit),
            GeofenceBreach.countDocuments(),
        ]);

        res.status(200).json({
            success: true,
            data: items,
            pagination: {
                total,
                page,
                pages: Math.ceil(total / limit),
                limit,
            },
        });
    } catch (err) {
        next(err);
    }
}

/**
 * POST /api/geofence/breaches
 */
async function createBreach(req, res, next) {
    try {
        const breach = await GeofenceBreach.create(req.body);

        const io = req.app.get('io');
        if (io) {
            io.emit('geofence:breach', {
                _id: breach._id,
                user: breach.user,
                geofenceId: breach.geofenceId,
                type: breach.type,
                coords: breach.coords,
                radiusMeters: breach.radiusMeters,
                occurredAt: breach.occurredAt,
            });
        }

        res.status(201).json({ success: true, data: breach });
    } catch (err) {
        next(err);
    }
}

/**
 * GET /api/geofence/breaches/export/csv
 */
async function exportBreachesCsv(req, res, next) {
    try {
        const breaches = await GeofenceBreach.find()
            .populate('user', 'name email')
            .sort({ occurredAt: -1 })
            .lean();

        const header = 'occurredAt,userId,userName,userEmail,geofenceId,type,lat,lng,radiusMeters\n';
        const rows = breaches
            .map((b) =>
                [
                    new Date(b.occurredAt || b.createdAt).toISOString(),
                    b.user?._id || '',
                    b.user?.name || '',
                    b.user?.email || '',
                    b.geofenceId || '',
                    b.type || '',
                    b.coords?.lat ?? '',
                    b.coords?.lng ?? '',
                    b.radiusMeters ?? '',
                ].join(',')
            )
            .join('\n');

        res.setHeader('Content-Type', 'text/csv');
        res.setHeader('Content-Disposition', 'attachment; filename="geofence_breaches.csv"');
        res.status(200).send(header + rows);
    } catch (err) {
        next(err);
    }
}

module.exports = {
    getBreaches,
    createBreach,
    exportBreachesCsv,
};
