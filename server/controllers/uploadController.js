const Upload = require('../models/Upload');
const Dispatch = require('../models/Dispatch');

exports.saveUpload = async (req, res) => {
  try {
    const { caseId } = req.body;
    if (!req.files || req.files.length === 0) {
      return res.status(400).json({ message: 'No files uploaded' });
    }

    const savedFiles = [];
    for (const file of req.files) {
      const upload = await Upload.create({
        caseId,
        filename: file.filename,
        originalName: file.originalname,
        mimetype: file.mimetype,
        size: file.size,
        path: file.path
      });
      savedFiles.push(upload);
    }

    // Optional: Link back to Dispatch Record if it exists
    await Dispatch.findByIdAndUpdate(caseId, { 
      $push: { attachments: { $each: savedFiles.map(f => f._id) } } 
    });

    res.status(201).json({ success: true, count: savedFiles.length, files: savedFiles });
  } catch (err) {
    console.error('Upload Error:', err);
    res.status(500).json({ message: err.message });
  }
};
