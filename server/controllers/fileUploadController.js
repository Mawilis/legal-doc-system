const multer = require('multer');
const CustomError = require('../utils/customError');
const path = require('path');

// Define multer storage
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/');
    },
    filename: (req, file, cb) => {
        cb(null, Date.now() + path.extname(file.originalname));  // Append file extension
    }
});

// Multer upload middleware
const upload = multer({ storage });

exports.uploadFile = upload.single('file');

exports.uploadDocument = async (req, res, next) => {
    try {
        if (!req.file) {
            return next(new CustomError('No file uploaded', 400));
        }
        res.status(200).json({ message: 'File uploaded successfully', file: req.file });
    } catch (error) {
        next(new CustomError('Error uploading file', 500));
    }
};
