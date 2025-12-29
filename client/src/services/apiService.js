// client/src/services/apiService.js
// -----------------------------------------------------------------------------
// COLLABORATION NOTES:
// - This wraps the http.js client with domain‑specific helpers.
// - Purpose: keep component code clean by abstracting API calls.
// - Error helper: standardizes error messages for UI display.
// - Engineers: add new domain helpers here (e.g. getUsers, createInvoice).
//   Always use apiGet/apiPost wrappers so interceptors apply consistently.
// -----------------------------------------------------------------------------

import http from './http';

// Generic methods
export const apiGet = (path, config) => http.get(path, config);
export const apiPost = (path, data, config) => http.post(path, data, config);
export const apiPut = (path, data, config) => http.put(path, data, config);
export const apiPatch = (path, data, config) => http.patch(path, data, config);
export const apiDelete = (path, config) => http.delete(path, config);

// Error helper
export const handleApiError = (error) => {
    if (error.response) {
        return error.response.data?.message || 'Unexpected server error';
    }
    return error.message || 'Network error';
};

// Domain‑specific helpers
export const getDocuments = () => apiGet('/documents');
export const createDocument = (data) => apiPost('/documents', data);
export const updateDocumentStatus = (id, status, reason) =>
    apiPut(`/documents/${id}/status`, { status, reason });

// Export object for convenience
const apiService = {
    apiGet,
    apiPost,
    apiPut,
    apiPatch,
    apiDelete,
    getDocuments,
    createDocument,
    updateDocumentStatus,
    handleApiError
};

export default apiService;
