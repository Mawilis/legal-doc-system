const mongoose = require('mongoose');

const commentSchema = new mongoose.Schema(
    {
        document: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'Document',
            required: true,
            index: true, // Optimized for querying comments by document
        },
        author: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'User',
            required: true,
        },
        content: {
            type: String,
            required: [true, 'Comment content cannot be empty.'],
            trim: true,
            maxlength: [1000, 'Comment cannot exceed 1000 characters.'],
        },
        parentComment: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'Comment',
            default: null,
        },
    },
    {
        timestamps: true,
    }
);

// Index for efficiently retrieving threaded replies per document
commentSchema.index({ document: 1, parentComment: 1, createdAt: 1 });

// Compound index for fetching comments by author if needed
commentSchema.index({ author: 1, createdAt: -1 });

// Virtual populate for easy fetching of child replies (optional enhancement)
commentSchema.virtual('replies', {
    ref: 'Comment',
    localField: '_id',
    foreignField: 'parentComment',
});

const Comment = mongoose.model('Comment', commentSchema);

module.exports = Comment;
