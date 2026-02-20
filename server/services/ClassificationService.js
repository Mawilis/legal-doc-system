'use strict';

/**
 * WILSY OS - CLASSIFICATION ENGINE
 * Version: 2.4.0 (Deterministic Return Patch)
 */

class ClassificationService {
    /**
     * Classify document text and verify against claimed type
     * @param {string} text - The raw OCR text from the document
     * @param {string} claimedType - The type the user claims this is (e.g., 'ID_DOCUMENT')
     * @param {object} options - Options including audit logger
     */
    static async classify(text, claimedType, options = {}) {
        const start = Date.now();
        const cleanText = (text || '').toUpperCase();
        
        // 1. DETERMINE DOCUMENT TYPE & CONFIDENCE
        let detectedType = 'UNKNOWN';
        let confidence = 0.0;
        let score = 0;

        // Keyword Dictionaries
        const patterns = {
            ID_DOCUMENT: ['IDENTITY DOCUMENT', 'REPUBLIC OF SOUTH AFRICA', 'DATE OF BIRTH', 'ID NUMBER', 'IDENTITY NUMBER'],
            PROOF_OF_ADDRESS: ['TAX INVOICE', 'MUNICIPALITY', 'UTILITY BILL', 'STATEMENT', 'ERF NUMBER', 'PHYSICAL ADDRESS'],
            COMPANY_REGISTRATION: ['CIPC', 'CERTIFICATE OF REGISTRATION', 'COR14.3', 'REGISTRATION NUMBER', 'ENTERPRISE NAME'],
            PROOF_OF_INCOME: ['PAYSLIP', 'SALARY', 'EARNINGS', 'NET PAY', 'EMPLOYEE NUMBER']
        };

        // Scoring Logic
        for (const [type, keywords] of Object.entries(patterns)) {
            let matches = 0;
            keywords.forEach(word => {
                if (cleanText.includes(word)) matches++;
            });

            // Calculate confidence based on keyword density
            const typeConfidence = matches / keywords.length;
            
            if (typeConfidence > score) {
                score = typeConfidence;
                detectedType = type;
            }
        }

        // Boost confidence if we have a strong match (3+ keywords)
        confidence = score > 0 ? Math.min(score + 0.3, 1.0) : 0;

        // 2. VERIFICATION LOGIC
        let verificationStatus = 'MISMATCH';
        
        if (detectedType === 'UNKNOWN') {
            verificationStatus = 'FLAGGED';
        } else if (detectedType === claimedType) {
            // If types match, check confidence threshold
            verificationStatus = confidence > 0.6 ? 'VERIFIED' : 'FLAGGED';
        } else {
            // Explicit Mismatch
            verificationStatus = 'MISMATCH';
        }

        // 3. CONSTRUCT RESULT OBJECT
        const result = {
            component: 'ClassificationService',
            action: 'classify',
            timestamp: new Date().toISOString(),
            claimedType,
            detectedType,
            confidence,
            verificationStatus,
            textLength: cleanText.length,
            wordCount: cleanText.split(/\s+/).length,
            hasNumbers: /\d/.test(cleanText),
            hasPhone: /(\+27|0)\d{9}/.test(cleanText),
            hasEmail: /@/.test(cleanText),
            lineCount: cleanText.split('\n').length,
            processingTime: Date.now() - start,
            optionsUsed: options
        };

        // 4. AUDIT LOGGING (If service provided)
        if (options.audit && typeof options.audit.log === 'function') {
            options.audit.log('classify', result);
        }

        // 5. CRITICAL: RETURN THE RESULT
        return result;
    }
}

module.exports = ClassificationService;
