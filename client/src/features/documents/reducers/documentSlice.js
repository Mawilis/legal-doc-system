import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import {
    getAllDocuments,
    createDocument as createDocumentService,
    markAsScanned,
    updateServiceStatus as updateServiceStatusService,
    deleteDocument as deleteDocumentService,
    updateDocument as updateDocumentService,
} from '../../../services/documentService';

const initialState = {
    documents: [],
    documentTypes: ['Summons', 'Returns', 'Affidavits', 'Legal Notice', 'Warrant', 'Motion'],
    loading: false,
    error: null,
    scannedDocuments: [],
    serviceTracking: {},
};

// Async thunk to fetch documents
export const fetchDocuments = createAsyncThunk('documents/fetchDocuments', async (_, { rejectWithValue }) => {
    try {
        return await getAllDocuments();
    } catch (err) {
        return rejectWithValue(err.response.data);
    }
});

// Async thunk to create a new document
export const createDocument = createAsyncThunk('documents/createDocument', async (documentData, { rejectWithValue }) => {
    try {
        return await createDocumentService(documentData);
    } catch (err) {
        return rejectWithValue(err.response.data);
    }
});

// Async thunk to mark document as scanned
export const markDocumentAsScanned = createAsyncThunk('documents/markAsScanned', async (documentId, { rejectWithValue }) => {
    try {
        return await markAsScanned(documentId);
    } catch (err) {
        return rejectWithValue(err.response.data);
    }
});

// Async thunk to update service status
export const updateServiceStatus = createAsyncThunk('documents/updateServiceStatus', async ({ documentId, status }, { rejectWithValue }) => {
    try {
        return await updateServiceStatusService(documentId, status);
    } catch (err) {
        return rejectWithValue(err.response.data);
    }
});

// Async thunk to delete a document
export const deleteDocument = createAsyncThunk('documents/deleteDocument', async (documentId, { rejectWithValue }) => {
    try {
        return await deleteDocumentService(documentId);
    } catch (err) {
        return rejectWithValue(err.response.data);
    }
});

// Async thunk to update a document
export const updateDocument = createAsyncThunk('documents/updateDocument', async ({ documentId, documentData }, { rejectWithValue }) => {
    try {
        return await updateDocumentService(documentId, documentData);
    } catch (err) {
        return rejectWithValue(err.response.data);
    }
});

const documentSlice = createSlice({
    name: 'documents',
    initialState,
    reducers: {
        addDocumentType: (state, action) => {
            state.documentTypes.push(action.payload);
        },
        addDocument: (state, action) => {
            state.documents.push(action.payload);
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchDocuments.pending, (state) => {
                state.loading = true;
            })
            .addCase(fetchDocuments.fulfilled, (state, action) => {
                state.loading = false;
                state.documents = action.payload;
            })
            .addCase(fetchDocuments.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload;
            })
            .addCase(createDocument.fulfilled, (state, action) => {
                state.documents.push(action.payload);
            })
            .addCase(markDocumentAsScanned.fulfilled, (state, action) => {
                state.scannedDocuments.push(action.payload);
            })
            .addCase(updateServiceStatus.fulfilled, (state, action) => {
                const { documentId, status } = action.payload;
                state.serviceTracking[documentId] = status;
            })
            .addCase(deleteDocument.fulfilled, (state, action) => {
                state.documents = state.documents.filter((doc) => doc.id !== action.payload.id);
            })
            .addCase(updateDocument.fulfilled, (state, action) => {
                const index = state.documents.findIndex((doc) => doc.id === action.payload.id);
                if (index !== -1) {
                    state.documents[index] = action.payload;
                }
            });
    },
});

export const { addDocumentType, addDocument } = documentSlice.actions;
export default documentSlice.reducer;
