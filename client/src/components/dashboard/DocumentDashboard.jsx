import React, { useState } from 'react';
import StatusBadge from './StatusBadge';
import StatusTimeline from './StatusTimeline';
import '../../styles/dashboard.css';

const DocumentDashboard = ({ documents }) => {
    const [expandedRow, setExpandedRow] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');

    // Safety check: ensure documents is an array
    const safeDocs = Array.isArray(documents) ? documents : [];

    const filtered = safeDocs.filter(doc =>
        JSON.stringify(doc).toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="dashboard-container">
            <div className="dashboard-controls">
                <input
                    className="search-input"
                    placeholder="Search cases, parties, status..."
                    value={searchTerm}
                    onChange={e => setSearchTerm(e.target.value)}
                />
                <button className="btn-export">Export CSV</button>
            </div>
            <table className="dashboard-table">
                <thead>
                    <tr>
                        <th>Case Number</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>Parties</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {filtered.length > 0 ? filtered.map((doc, i) => (
                        <React.Fragment key={i}>
                            <tr>
                                <td>{doc.caseNumber}</td>
                                <td>{doc.documentType}</td>
                                <td><StatusBadge status={doc.currentStatus} /></td>
                                <td>{doc.parties}</td>
                                <td className="row-actions">
                                    <button onClick={() => setExpandedRow(expandedRow === i ? null : i)}>
                                        {expandedRow === i ? 'Hide' : 'History'}
                                    </button>
                                </td>
                            </tr>
                            {expandedRow === i && (
                                <tr>
                                    <td colSpan="5">
                                        <StatusTimeline events={doc.events} />
                                    </td>
                                </tr>
                            )}
                        </React.Fragment>
                    )) : (
                        <tr><td colSpan="5" style={{ textAlign: 'center', padding: '20px' }}>No documents found</td></tr>
                    )}
                </tbody>
            </table>
        </div>
    );
};

// ✅ EXPORT DEFAULT IS CRITICAL
export default DocumentDashboard;