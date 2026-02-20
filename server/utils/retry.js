/**
 * Retry utility for handling transient failures
 */

async function withRetry(fn, options = {}) {
    const {
        maxRetries = 3,
        initialDelay = 1000,
        backoffFactor = 2,
        correlationId = 'unknown'
    } = options;

    let lastError;
    let delay = initialDelay;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            return await fn();
        } catch (error) {
            lastError = error;
            
            console.log(`Retry attempt ${attempt}/${maxRetries} failed`, {
                correlationId,
                error: error.message,
                nextRetryDelay: delay
            });

            if (attempt === maxRetries) break;
            
            await new Promise(resolve => setTimeout(resolve, delay));
            delay *= backoffFactor;
        }
    }

    throw lastError;
}

module.exports = { withRetry };
