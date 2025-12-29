import React from 'react';
import DocumentDashboard from '../components/dashboard/DocumentDashboard';

// Mock Data (Replace this with data from your API/Redux)
const mockDocuments = [
    {
        caseNumber: "12345/2025",
        documentType: "Summons",
        currentStatus: "Completed",
        submittedAt: "2025-12-20T12:00:00Z",
        parties: "Smith vs. Jones",
        events: [
            { status: "Draft", timestamp: "2025-12-20T09:00:00Z", note: "Created by Admin" },
            { status: "Submitted", timestamp: "2025-12-20T12:00:00Z", note: "Filed via Court Online" },
            { status: "Completed", timestamp: "2025-12-20T16:00:00Z", note: "Service successful" },
        ],
    },
    {
        caseNumber: "67890/2025",
        documentType: "Divorce Summons",
        currentStatus: "Pending",
        submittedAt: "2025-12-19T15:00:00Z",
        parties: "Doe vs. Doe",
        events: [
            { status: "Draft", timestamp: "2025-12-19T14:00:00Z", note: "Drafted" },
            { status: "Pending", timestamp: "2025-12-19T15:00:00Z", note: "Partner review required" },
        ],
    },
];

const DashboardPage = () => {
    return (
        <div style={{ backgroundColor: '#f1f5f9', minHeight: '100vh', padding: '20px' }}>
            <DocumentDashboard documents={mockDocuments} />
        </div>
    );
};

export default DashboardPage;