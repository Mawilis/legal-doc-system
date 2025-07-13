const Document = require('../models/documentModel');
const Client = require('../models/clientModel');
const User = require('../models/userModel');
const CustomError = require('../utils/customError');
const logger = require('../utils/logger');

/**
 * @desc    Perform a system-wide search across multiple collections
 * @route   GET /api/search?q=<query>
 * @access  Private
 */
exports.searchSystem = async (req, res, next) => {
    try {
        const { q } = req.query;

        if (!q || q.trim() === '') {
            return next(new CustomError('Please provide a search query.', 400));
        }

        const searchQuery = { $text: { $search: q } };
        const scoreProjection = { score: { $meta: 'textScore' } };

        const [documentResults, clientResults, userResults] = await Promise.all([
            Document.find(searchQuery, scoreProjection)
                .select('title caseNumber status documentType')
                .sort({ score: { $meta: 'textScore' } })
                .limit(10),
            Client.find(searchQuery, scoreProjection)
                .select('firmName accountNumber primaryContactName')
                .sort({ score: { $meta: 'textScore' } })
                .limit(5),
            User.find({
                $or: [
                    { name: { $regex: q, $options: 'i' } },
                    { email: { $regex: q, $options: 'i' } }
                ]
            })
                .select('name email role')
                .limit(5)
        ]);

        const searchResults = {
            documents: documentResults,
            clients: clientResults,
            users: userResults,
        };

        logger.info(`Search performed for query: "${q}"`);

        res.status(200).json({
            success: true,
            data: searchResults,
        });

    } catch (error) {
        logger.error(`Error during system search: ${error.message}`);
        next(error);
    }
};
