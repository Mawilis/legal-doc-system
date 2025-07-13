// server/middleware/uploadMiddleware.js

const multer = require('multer');
const path = require('path');

// Configure storage location + filename
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/documents/'); // Make sure this folder exists
    },
    filename: (req, file, cb) => {
        const ext = path.extname(file.originalname);
        cb(null, `${Date.now()}-${file.fieldname}${ext}`);
    },
});

// Filter to allow only specific file types
const fileFilter = (req, file, cb) => {
    const allowedTypes = /pdf|doc|docx|jpg|jpeg|png/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);

    if (extname && mimetype) {
        cb(null, true);
    } else {
        cb(new Error('File type not allowed. Allowed: PDF, DOC, DOCX, JPG, PNG.'));
    }
};

// Set limits and use configuration
const upload = multer({
    storage,
    fileFilter,
    limits: { fileSize: 10 * 1024 * 1024 }, // 10 MB max
});

// Export single file upload for documentFile field
exports.uploadDocument = upload.single('documentFile');
