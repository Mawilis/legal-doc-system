const mongoose = require('mongoose');

const apiKeySchema = new mongoose.Schema({
    user: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true,
        index: true, // Faster lookups by user
    },
    keyHash: {
        type: String,
        required: true,
        unique: true, // Ensure no two keys have the same hash
    },
    keyPrefix: {
        type: String,
        required: true,
        minlength: [6, 'Key prefix must be at least 6 characters.'],
        maxlength: [12, 'Key prefix must be at most 12 characters.'],
        index: true, // Useful for quick filtering by prefix
    },
    name: {
        type: String,
        required: [true, 'Please provide a name for this API key.'],
        trim: true,
        maxlength: [100, 'API key name must be less than 100 characters.'],
    },
    permissions: {
        type: [String],
        enum: ['read_only', 'read_write'],
        default: ['read_only'],
        validate: {
            validator: (val) => val.length > 0,
            message: 'At least one permission is required.',
        },
    },
    expiresAt: {
        type: Date,
        validate: {
            validator: function (val) {
                return !val || val > new Date();
            },
            message: 'Expiration date must be in the future.',
        },
    },
    lastUsed: {
        type: Date,
    },
}, {
    timestamps: true,
});

// Add a compound index for efficient queries by user + keyPrefix (if needed)
apiKeySchema.index({ user: 1, keyPrefix: 1 });

const ApiKey = mongoose.model('ApiKey', apiKeySchema);

module.exports = ApiKey;
