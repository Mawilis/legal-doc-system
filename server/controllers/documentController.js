const Document = require('../models/documentModel');

exports.createDocument = async (req, res) => {
    try {
        const { title, content } = req.body;
        const document = new Document({ title, content, owner: req.user._id });
        await document.save();

        res.status(201).json(document);
    } catch (err) {
        res.status(400).json({ message: 'Error creating document' });
    }
};

exports.getDocument = async (req, res) => {
    try {
        const document = await Document.findById(req.params.id);
        if (!document) return res.status(404).json({ message: 'Document not found' });

        res.status(200).json(document);
    } catch (err) {
        res.status(500).json({ message: 'Server error' });
    }
};

exports.updateDocument = async (req, res) => {
    try {
        const document = await Document.findByIdAndUpdate(req.params.id, req.body, { new: true });
        if (!document) return res.status(404).json({ message: 'Document not found' });

        res.status(200).json(document);
    } catch (err) {
        res.status(500).json({ message: 'Server error' });
    }
};

exports.deleteDocument = async (req, res) => {
    try {
        const document = await Document.findByIdAndDelete(req.params.id);
        if (!document) return res.status(404).json({ message: 'Document not found' });

        res.status(200).json({ message: 'Document deleted' });
    } catch (err) {
        res.status(500).json({ message: 'Server error' });
    }
};
