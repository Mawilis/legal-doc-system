/**
 * File: server/routes/uploadRoutes.js
 * -----------------------------------------------------------------------------
 * STATUS: EPITOME | Upload Gateway (Tenant-Scoped, Auditable, Investor-Grade)
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - Handle secure file uploads with validation and audit logging.
 * - Enforce tenant isolation and RBAC/ABAC authorization.
 * - Limit file size and restrict file types for compliance.
 * - Emit audit events for observability and investor-grade transparency.
 * -----------------------------------------------------------------------------
 */

'use strict';

const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');

const { saveUpload } = require('../controllers/uploadController');

// Security + Observability middleware
const { tenantGuard, emitAudit } = require('../middleware/security');
const { protect, authorize } = require('../middleware/authProtect');

// ------------------------------
// Ensure upload directory exists
// ------------------------------
const uploadDir = path.join(__dirname, '../uploads');
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir);

// ------------------------------
// Multer Storage Configuration
// ------------------------------
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, uploadDir),
  filename: (req, file, cb) =>
    cb(null, Date.now() + '-' + file.originalname.replace(/\s+/g, '_')),
});

// ------------------------------
// Multer Upload Middleware
// ------------------------------
const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB Limit
  fileFilter: (req, file, cb) => {
    const allowed = ['.pdf', '.jpg', '.jpeg', '.png', '.mp3', '.wav'];
    const ext = path.extname(file.originalname).toLowerCase();
    if (!allowed.includes(ext)) {
      return cb(
        new Error('Invalid file type. Only PDF, Images, and Audio allowed.')
      );
    }
    cb(null, true);
  },
});

// ------------------------------
// Routes
// ------------------------------

/**
 * @route   POST /api/uploads
 * @desc    Upload files (max 5 files, 10MB each)
 */
router.post(
  '/',
  protect,
  tenantGuard(),
  authorize(['ADMIN', 'SUPER_ADMIN', 'LAWYER']),
  upload.array('files', 5),
  async (req, res, next) => {
    try {
      const result = await saveUpload(req, res);

      await emitAudit(req, {
        resource: 'upload',
        action: 'create',
        severity: 'warning',
        metadata: {
          files: req.files?.map((f) => ({
            filename: f.filename,
            size: f.size,
            mimetype: f.mimetype,
          })),
        },
      });

      if (!res.headersSent) res.status(201).json({ status: 'success', data: result });
    } catch (err) {
      err.code = 'UPLOAD_FAILED';
      next(err);
    }
  }
);

module.exports = router;
