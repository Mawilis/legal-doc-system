// server/models/documentModel.js

const mongoose = require('mongoose');

// This schema defines the structure for every document in our database.
const documentSchema = new mongoose.Schema(
    {
        // --- Core Document Information ---
        title: {
            type: String,
            required: [true, 'A document must have a title.'],
            trim: true, // Removes whitespace from both ends of a string.
        },
        caseNumber: {
            type: String,
            required: [true, 'A case number is required.'],
            unique: true, // Ensures every document has a unique case number.
            trim: true,
        },
        documentType: {
            type: String,
            required: true,
            enum: [ // Using an enum restricts the value to a predefined list.
                'Combined Summons',
                'Notice of Motion',
                'Directive Execution',
                'Other'
            ],
            default: 'Other',
        },
        content: {
            type: String,
            required: [true, 'Document content cannot be empty.'],
        },

        // --- Relationships ---
        // These fields link this document to other collections in the database.
        createdBy: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'User', // Creates a direct reference to the User model.
            required: true,
        },
        client: {
            // In a full application, this would reference a 'Client' model.
            // For now, we'll store the client's name.
            type: String,
            required: [true, 'A client name is required.'],
        },
        assignedTo: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'User', // References the deputy (who is also a User).
        },

        // --- Status & Workflow ---
        status: {
            type: String,
            required: true,
            enum: [
                'Registered',
                'Assigned',
                'Out for Service',
                'Attempted',
                'Served',
                'Non-Service',
                'Return Generated',
                'Billed'
            ],
            default: 'Registered',
        },

        // --- Tracking & History ---
        // This array will store a log of every action taken on the document.
        history: [
            {
                action: {
                    type: String,
                    required: true,
                    // e.g., 'Created', 'Assigned', 'Service Attempted', 'Served'
                },
                user: {
                    type: mongoose.Schema.Types.ObjectId,
                    ref: 'User',
                },
                timestamp: {
                    type: Date,
                    default: Date.now,
                },
                notes: String, // Optional notes for the history entry.
            }
        ]
    },
    {
        // --- Schema Options ---
        // `timestamps: true` automatically adds `createdAt` and `updatedAt` fields.
        timestamps: true,
        // `toJSON` and `toObject` ensure that when we convert the document to JSON,
        // we include virtual properties if we add any later.
        toJSON: { virtuals: true },
        toObject: { virtuals: true },
    }
);

// --- Database Indexing for Performance ---
// Create a text index on the most commonly searched fields.
// This will make text-based searches significantly faster.
documentSchema.index({
    title: 'text',
    caseNumber: 'text',
    content: 'text',
    documentType: 'text'
});


// --- Mongoose Middleware (Hooks) ---
// This middleware runs automatically *before* a new document is saved (`pre('save')`).
// We use it to create the initial history entry.
documentSchema.pre('save', function (next) {
    // `isNew` is a Mongoose property that is true if the document is being created.
    if (this.isNew) {
        this.history.push({
            action: 'Document Registered',
            user: this.createdBy,
            notes: `Document created with case number ${this.caseNumber}.`
        });
    }
    next();
});


const Document = mongoose.model('Document', documentSchema);

module.exports = Document;
