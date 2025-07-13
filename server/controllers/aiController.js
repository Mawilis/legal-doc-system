const CustomError = require('../utils/customError');
const logger = require('../utils/logger');
require('dotenv').config(); // Ensure env is loaded in this file as a fallback

let openai = null;

async function initializeOpenAI() {
    try {
        const apiKey = process.env.OPENAI_API_KEY;

        if (!apiKey) {
            throw new Error('OPENAI_API_KEY is missing or empty.');
        }

        const { default: OpenAI } = await import('openai');
        openai = new OpenAI({ apiKey });
        logger.info('✅ OpenAI client initialized.');
    } catch (err) {
        logger.error(`❌ Failed to initialize OpenAI: ${err.message}`);
    }
}

// Initialize on import
initializeOpenAI();

exports.summarizeText = async (req, res, next) => {
    if (!openai) {
        logger.warn('⚠️ OpenAI not ready, retrying initialization...');
        await initializeOpenAI();
        if (!openai) {
            return next(new CustomError('OpenAI client is not initialized.', 500));
        }
    }

    const { text } = req.body;

    if (!text || text.trim().length < 50) {
        return next(new CustomError('Not enough text provided for summarization.', 400));
    }

    try {
        const completion = await openai.chat.completions.create({
            model: 'gpt-3.5-turbo',
            messages: [
                {
                    role: 'system',
                    content: 'You are a helpful legal assistant. Summarize the following legal document concisely.',
                },
                { role: 'user', content: text },
            ],
            temperature: 0.5,
            max_tokens: 150,
        });

        const summary = completion.choices[0].message.content.trim();

        logger.info('✅ Summary generated with OpenAI.');
        res.status(200).json({ success: true, summary });

    } catch (error) {
        logger.error(`OpenAI API error: ${error.message}`);
        next(new CustomError('Failed to generate summary.', 500));
    }
};
