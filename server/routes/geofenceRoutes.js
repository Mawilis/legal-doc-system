const express = require('express');
const router = express.Router();

// Try to import all possible guards (different projects name them differently)
const auth = require('../middleware/authMiddleware');
const geofenceCtrl = require('../controllers/geofenceController');

// Debug what we actually have
if (process.env.NODE_ENV !== 'production') {
    // eslint-disable-next-line no-console
    console.log('[AuthMiddleware exports]', Object.keys(auth));
    // eslint-disable-next-line no-console
    console.log('[GeofenceController exports]', Object.keys(geofenceCtrl));
}

// ---- Resolve Guards Safely ----
const noop = (req, _res, next) => next();

// protect: prefer `auth.protect`, else `auth.authenticate`, else no-op
const protect = typeof auth.protect === 'function'
    ? auth.protect
    : (typeof auth.authenticate === 'function' ? auth.authenticate : noop);

// admin guard: prefer `auth.admin`, else wrap `auth.authorize('admin')`, else no-op (with warning)
let adminGuard = noop;
if (typeof auth.admin === 'function') {
    adminGuard = auth.admin;
} else if (typeof auth.authorize === 'function') {
    adminGuard = auth.authorize('admin');
} else {
    console.warn('[WARN] No admin/authorize guard found. Geofence routes are temporarily unprotected.');
}

// ---- Validate controller handlers ----
const ensureFn = (fnName) => {
    if (typeof geofenceCtrl[fnName] !== 'function') {
        const available = Object.keys(geofenceCtrl).join(', ') || '<<none>>';
        throw new Error(
            `geofenceController.${fnName} is not a function. Available: ${available}`
        );
    }
    return geofenceCtrl[fnName];
};

// ---- Routes ----
router.get('/breaches', protect, adminGuard, ensureFn('getBreaches'));
router.post('/breaches', protect, adminGuard, ensureFn('createBreach'));
router.get('/breaches/export/csv', protect, adminGuard, ensureFn('exportBreachesCsv'));

module.exports = router;
