/**
 * /Users/wilsonkhanyezi/legal-doc-system/server/middleware/uploadMiddleware.js
 *
 * Enterprise Upload Middleware (Masterpiece Edition)
 * --------------------------------------------------
 * Complete, production-grade middleware for secure file uploads.
 * - Security: strict file type filtering, size limits, safe filenames.
 * - Features: single-file upload for documents (PDF, DOC, DOCX, JPG, PNG).
 * - Documentation: clear error messages for API consumers.
 * - Future-proof: structured for expansion (multi-file, cloud storage, virus scanning).
 */

const multer = require('multer');
const path = require('path');
const fs = require('fs');

// ------------------------------------------
// Ensure Upload Directory Exists
// ------------------------------------------
const UPLOAD_DIR = path.join(__dirname, '../../uploads/documents');
if (!fs.existsSync(UPLOAD_DIR)) {
    fs.mkdirSync(UPLOAD_DIR, { recursive: true });
    console.log(`✅ Upload directory created at: ${UPLOAD_DIR}`);
}

// ------------------------------------------
// Configure Storage Location + Filename
// ------------------------------------------
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, UPLOAD_DIR);
    },
    filename: (req, file, cb) => {
        const ext = path.extname(file.originalname).toLowerCase();
        const safeName = file.originalname
            .replace(/\s+/g, '-')       // Replace spaces with dashes
            .replace(/[^a-zA-Z0-9.-]/g, ''); // Strip unsafe characters
        cb(null, `${Date.now()}-${safeName}`);
    },
});

// ------------------------------------------
// File Type Filter
// ------------------------------------------
const fileFilter = (req, file, cb) => {
    const allowedTypes = /\.(pdf|doc|docx|jpg|jpeg|png)$/i;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = /(pdf|msword|vnd.openxmlformats-officedocument.wordprocessingml.document|jpeg|png)$/i.test(file.mimetype);

    if (extname && mimetype) {
        cb(null, true);
    } else {
        cb(
            new Error(
                '❌ File type not allowed. Allowed: PDF, DOC, DOCX, JPG, PNG.'
            )
        );
    }
};

// ------------------------------------------
// Multer Configuration
// ------------------------------------------
const upload = multer({
    storage,
    fileFilter,
    limits: {
        fileSize: 10 * 1024 * 1024, // 10 MB max
    },
});

// ------------------------------------------
// Export Middleware
// ------------------------------------------
/**
 * Single file upload middleware for field: "documentFile"
 * Usage: router.post('/upload', uploadDocument, controllerFn)
 */
exports.uploadDocument = upload.single('documentFile');
