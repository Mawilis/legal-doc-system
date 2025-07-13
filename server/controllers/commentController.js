const Comment = require('../models/commentModel');
const Document = require('../models/documentModel');
const CustomError = require('../utils/customError');
const logger = require('../utils/logger');

/**
 * @desc    Add a new comment to a document
 * @route   POST /api/comments
 * @access  Private
 */
exports.addComment = async (req, res, next) => {
    try {
        const { documentId, content, parentCommentId } = req.body;

        if (!content || content.trim().length === 0) {
            return next(new CustomError('Comment content cannot be empty.', 400));
        }

        const documentExists = await Document.findById(documentId);
        if (!documentExists) {
            return next(new CustomError('Document not found.', 404));
        }

        if (parentCommentId) {
            const parentExists = await Comment.findById(parentCommentId);
            if (!parentExists) {
                return next(new CustomError('Parent comment not found.', 404));
            }
        }

        const comment = await Comment.create({
            document: documentId,
            content,
            parentComment: parentCommentId || null,
            author: req.user.id,
        });

        const populatedComment = await Comment.findById(comment._id).populate('author', 'name email');

        logger.info(`Comment ${comment._id} added to document ${documentId} by ${req.user.email}`);

        res.status(201).json({
            success: true,
            data: populatedComment,
        });
    } catch (error) {
        logger.error(`Error adding comment: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Get all comments for a specific document
 * @route   GET /api/comments/document/:documentId
 * @access  Private
 */
exports.getCommentsForDocument = async (req, res, next) => {
    try {
        const { documentId } = req.params;

        const comments = await Comment.find({ document: documentId })
            .populate('author', 'name email')
            .sort({ createdAt: 1 });

        res.status(200).json({
            success: true,
            count: comments.length,
            data: comments,
        });
    } catch (error) {
        logger.error(`Error fetching comments: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Update a comment
 * @route   PUT /api/comments/:commentId
 * @access  Private
 */
exports.updateComment = async (req, res, next) => {
    try {
        const { content } = req.body;

        if (!content || content.trim().length === 0) {
            return next(new CustomError('Updated content cannot be empty.', 400));
        }

        const comment = await Comment.findById(req.params.commentId);
        if (!comment) {
            return next(new CustomError('Comment not found.', 404));
        }

        if (comment.author.toString() !== req.user.id) {
            return next(new CustomError('User not authorized to update this comment.', 403));
        }

        comment.content = content.trim();
        await comment.save();

        const populatedComment = await Comment.findById(comment._id).populate('author', 'name email');

        logger.info(`Comment ${comment._id} updated by ${req.user.email}`);

        res.status(200).json({
            success: true,
            data: populatedComment,
        });
    } catch (error) {
        logger.error(`Error updating comment: ${error.message}`);
        next(error);
    }
};

/**
 * @desc    Delete a comment
 * @route   DELETE /api/comments/:commentId
 * @access  Private
 */
exports.deleteComment = async (req, res, next) => {
    try {
        const comment = await Comment.findById(req.params.commentId);

        if (!comment) {
            return next(new CustomError('Comment not found.', 404));
        }

        if (comment.author.toString() !== req.user.id && req.user.role !== 'ADMIN') {
            return next(new CustomError('User not authorized to delete this comment.', 403));
        }

        await comment.remove();

        logger.info(`Comment ${req.params.commentId} deleted by ${req.user.email}`);

        res.status(200).json({
            success: true,
            data: {},
        });
    } catch (error) {
        logger.error(`Error deleting comment: ${error.message}`);
        next(error);
    }
};
