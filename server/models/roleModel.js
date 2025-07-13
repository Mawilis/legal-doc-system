const mongoose = require('mongoose');

const roleSchema = new mongoose.Schema(
    {
        name: {
            type: String,
            required: [true, 'A role must have a name.'],
            unique: true,
            uppercase: true, // Consistency: e.g., ADMIN, USER
            trim: true,
        },
        description: {
            type: String,
            trim: true,
            maxlength: [250, 'Description must be less than 250 characters.'],
        },
        permissions: {
            type: [String],
            required: [true, 'A role must have at least one permission.'],
            validate: [
                {
                    validator: (val) => val.length > 0,
                    message: 'A role must have at least one permission.',
                },
                {
                    validator: (val) => new Set(val).size === val.length,
                    message: 'Permissions must be unique within the role.',
                },
            ],
        },
    },
    {
        timestamps: true,
    }
);

// Create an index on the name field for faster queries (useful for auth checks)
roleSchema.index({ name: 1 });

const Role = mongoose.model('Role', roleSchema);

module.exports = Role;
