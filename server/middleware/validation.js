/* eslint-env node */
const errorHandler = require('./errorHandler');

/**
 * Validation middleware for document upload
 */
exports.validateDocumentUpload = (req, res, next) => {
  const { documentType, fileName, fileSize } = req.body;
  const errors = {};
  
  if (!documentType) {
    errors.documentType = 'Document type is required';
  }
  
  if (!fileName) {
    errors.fileName = 'File name is required';
  }
  
  if (fileSize && fileSize > 100 * 1024 * 1024) { // 100MB
    errors.fileSize = 'File size exceeds 100MB limit';
  }
  
  if (Object.keys(errors).length > 0) {
    return next(errorHandler.validationError('Validation failed', errors));
  }
  
  next();
};

/**
 * Validate document ID parameter
 */
exports.validateDocumentId = (req, res, next) => {
  const { documentId } = req.params;
  
  if (!documentId || !documentId.match(/^[a-f0-9]{32}$/)) {
    return next(errorHandler.validationError('Invalid document ID'));
  }
  
  next();
};

/**
 * Validate classification request
 */
exports.validateClassification = (req, res, next) => {
  const { text, claimedType } = req.body;
  const errors = {};
  
  if (!text || text.length < 10) {
    errors.text = 'Text must be at least 10 characters';
  }
  
  const validTypes = ['ID_DOCUMENT', 'PROOF_OF_ADDRESS', 'COMPANY_REGISTRATION', 'PROOF_OF_INCOME'];
  if (!claimedType || !validTypes.includes(claimedType)) {
    errors.claimedType = `Claimed type must be one of: ${validTypes.join(', ')}`;
  }
  
  if (Object.keys(errors).length > 0) {
    return next(errorHandler.validationError('Classification validation failed', errors));
  }
  
  next();
};

/**
 * Validate pagination parameters
 */
exports.validatePagination = (req, res, next) => {
  const { limit, offset } = req.query;
  const errors = {};
  
  if (limit) {
    const numLimit = parseInt(limit);
    if (isNaN(numLimit) || numLimit < 1 || numLimit > 1000) {
      errors.limit = 'Limit must be between 1 and 1000';
    }
  }
  
  if (offset) {
    const numOffset = parseInt(offset);
    if (isNaN(numOffset) || numOffset < 0) {
      errors.offset = 'Offset must be a non-negative number';
    }
  }
  
  if (Object.keys(errors).length > 0) {
    return next(errorHandler.validationError('Pagination validation failed', errors));
  }
  
  next();
};
