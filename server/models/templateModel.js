const mongoose = require('mongoose');

// --- Field Sub-Schema ---
const fieldSchema = new mongoose.Schema({
    name: {
        type: String,
        required: [true, 'Each field must have a name (e.g., "plaintiff_name").'],
        trim: true,
        lowercase: true,  // Ensures consistency (e.g., "plaintiff_name")
    },
    label: {
        type: String,
        required: [true, 'Each field must have a user-friendly label (e.g., "Plaintiff Name").'],
        trim: true,
    },
    fieldType: {
        type: String,
        required: true,
        enum: ['text', 'textarea', 'date', 'number', 'dropdown'],
        default: 'text',
    },
    options: {
        type: [String],
        validate: {
            validator: function (val) {
                if (this.fieldType === 'dropdown') {
                    return Array.isArray(val) && val.length > 0;
                }
                return true; // For non-dropdowns, options can be undefined
            },
            message: 'Dropdown fields must have at least one option.'
        }
    },
    required: {
        type: Boolean,
        default: false,
    },
}, { _id: false }); // Prevent creation of nested _id for sub-docs

// --- Template Schema ---
const templateSchema = new mongoose.Schema(
    {
        name: {
            type: String,
            required: [true, 'A template must have a name.'],
            unique: true,
            trim: true,
        },
        description: {
            type: String,
            required: [true, 'A template must have a description.'],
            trim: true,
            maxlength: [500, 'Description must be less than 500 characters.'],
        },
        fields: {
            type: [fieldSchema],
            validate: {
                validator: function (val) {
                    return val.length > 0;
                },
                message: 'A template must have at least one field.'
            }
        },
        createdBy: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'User',
            required: true,
        },
    },
    {
        timestamps: true,
    }
);

// Index for faster querying by name
templateSchema.index({ name: 1 });

const Template = mongoose.model('Template', templateSchema);

module.exports = Template;
