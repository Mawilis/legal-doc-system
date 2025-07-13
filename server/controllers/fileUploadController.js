const path = require('path');
const multer = require('multer');
const CustomError = require('../utils/customError');

// Set up multer storage
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/documents/');  // ✅ Make sure this folder exists
    },
    filename: (req, file, cb) => {
        const uniqueName = `${Date.now()}-${file.originalname}`;
        cb(null, uniqueName);
    }
});

// File type validation
const fileFilter = (req, file, cb) => {
    const allowedTypes = /pdf|doc|docx|jpg|jpeg|png/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);

    if (extname && mimetype) {
        cb(null, true);
    } else {
        cb(new CustomError('Only PDF, DOC, DOCX, JPG, JPEG, PNG files are allowed.', 400));
    }
};

// Multer upload config
const upload = multer({
    storage,
    fileFilter
}).single('documentFile');  // Expect field: documentFile

// Middleware to handle file upload
exports.uploadDocument = (req, res, next) => {
    upload(req, res, (err) => {
        if (err instanceof multer.MulterError) {
            return next(new CustomError(`Multer error: ${err.message}`, 400));
        } else if (err) {
            return next(err);  // Pass CustomError or other error to error handler
        }

        if (!req.file) {
            return next(new CustomError('No file uploaded', 400));
        }

        // Success response
        res.status(200).json({
            message: 'File uploaded successfully',
            fileUrl: `/uploads/documents/${req.file.filename}`
        });
    });
};
