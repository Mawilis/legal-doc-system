class ValidationError extends Error {
    constructor(message, details) {
        super(message);
        this.name = 'ValidationError';
        this.details = details;
        this.statusCode = 400;
    }
}

class ComplianceError extends Error {
    constructor(message, details) {
        super(message);
        this.name = 'ComplianceError';
        this.details = details;
        this.statusCode = 451; // Unavailable For Legal Reasons
    }
}

class NotFoundError extends Error {
    constructor(message, details) {
        super(message);
        this.name = 'NotFoundError';
        this.details = details;
        this.statusCode = 404;
    }
}

class AuthorizationError extends Error {
    constructor(message, details) {
        super(message);
        this.name = 'AuthorizationError';
        this.details = details;
        this.statusCode = 403;
    }
}

module.exports = {
    ValidationError,
    ComplianceError,
    NotFoundError,
    AuthorizationError
};
