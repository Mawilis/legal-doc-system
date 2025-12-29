// client/src/components/dashboard/StatusBadge.jsx
import React from 'react';
import PropTypes from 'prop-types';
import '../../styles/dashboard.css';

const StatusBadge = ({ status }) => {
    // Defensive Programming: Normalize input to prevent crashes on "Draft" vs "draft"
    const normalizedStatus = status ? status.trim() : 'Draft';

    const statusColors = {
        'Draft': 'badge-gray',
        'Pending': 'badge-yellow',
        'Approved': 'badge-blue',
        'Submitted': 'badge-indigo',
        'In Transit': 'badge-teal',
        'Served': 'badge-green',
        'Failed Service': 'badge-orange',
        'Returned': 'badge-purple',
        'Completed': 'badge-emerald',
        'Rejected': 'badge-red',
        'Suspended': 'badge-darkgray',
        'Appealed': 'badge-pink',
        'Archived': 'badge-slate',
        'Expunged': 'badge-black'
    };

    // Fallback to gray if status is unknown
    const badgeClass = statusColors[normalizedStatus] || 'badge-gray';

    return (
        <span className={`badge ${badgeClass}`}>
            {normalizedStatus}
        </span>
    );
};

// 🔒 STRICT VALIDATION
StatusBadge.propTypes = {
    status: PropTypes.string.isRequired
};

export default StatusBadge;