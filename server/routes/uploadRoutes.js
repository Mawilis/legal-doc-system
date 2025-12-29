const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const { saveUpload } = require('../controllers/uploadController');
const fs = require('fs');

// Ensure upload dir exists
const uploadDir = path.join(__dirname, '../uploads');
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir);

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, uploadDir),
  filename: (req, file, cb) => cb(null, Date.now() + '-' + file.originalname.replace(/\s+/g, '_'))
});

const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB Limit
  fileFilter: (req, file, cb) => {
    const allowed = ['.pdf', '.jpg', '.jpeg', '.png', '.mp3', '.wav'];
    const ext = path.extname(file.originalname).toLowerCase();
    if (!allowed.includes(ext)) return cb(new Error('Invalid file type. Only PDF, Images, and Audio allowed.'));
    cb(null, true);
  }
});

router.post('/', upload.array('files', 5), saveUpload);

module.exports = router;
