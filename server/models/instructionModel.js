const mongoose = require('mongoose');

const instructionSchema = new mongoose.Schema({
    title: {
        type: String,
        required: [true, 'Title is required'],
        trim: true,
        minlength: [3, 'Title must be at least 3 characters long'],
        maxlength: [100, 'Title must be at most 100 characters long'],
    },
    details: {
        type: String,
        required: [true, 'Details are required'],
        trim: true,
        minlength: [10, 'Details must be at least 10 characters long'],
    },
    createdBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true,
    },
    createdAt: {
        type: Date,
        default: Date.now,
    },
}, {
    timestamps: true, // Automatically adds createdAt and updatedAt fields
});

// Index to improve search performance (if required)
instructionSchema.index({ title: 'text', details: 'text' });

module.exports = mongoose.model('Instruction', instructionSchema);
