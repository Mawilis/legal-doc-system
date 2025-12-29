// client/src/components/dashboard/StatusTimeline.jsx
import React from 'react';
import PropTypes from 'prop-types';
import '../../styles/dashboard.css';

const StatusTimeline = ({ events }) => {
    if (!events || events.length === 0) {
        return <div className="timeline-container">No history available for this document.</div>;
    }

    return (
        <div className="timeline-container">
            <h4 style={{ marginBottom: '15px', color: '#64748b', fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase' }}>Audit Trail</h4>
            <div className="timeline">
                {events.map((event, index) => {
                    // Normalize status for class name generation (remove spaces, lowercase)
                    const statusClass = event.status
                        ? `dot-${event.status.replace(/\s+/g, '').toLowerCase()}`
                        : 'dot-default';

                    return (
                        <div key={index} className="timeline-item">
                            <div className={`timeline-dot ${statusClass}`} />
                            <div className="timeline-content">
                                <span className="timeline-status">{event.status}</span>
                                <span className="timeline-date">
                                    {event.timestamp ? new Date(event.timestamp).toLocaleString() : 'Date Unknown'}
                                </span>
                                {event.note && <p className="timeline-note">{event.note}</p>}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

// 🔒 STRICT VALIDATION
StatusTimeline.propTypes = {
    events: PropTypes.arrayOf(
        PropTypes.shape({
            status: PropTypes.string.isRequired,
            timestamp: PropTypes.string, // ISO Date string
            note: PropTypes.string
        })
    ).isRequired
};

export default StatusTimeline;