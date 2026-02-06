/**
 * File: client/src/features/audits/pages/AuditLogs.jsx
 * -----------------------------------------------------------------------------
 * STATUS: PRODUCTION-READY | Audit Logs Page (Minimal)
 * -----------------------------------------------------------------------------
 * PURPOSE:
 * - Visualize audit events from Redux for quick verification.
 * - Useful during development and demos to confirm emitters work.
 * -----------------------------------------------------------------------------
 */

'use client';

import React from 'react';
import { useSelector } from 'react-redux';

export default function AuditLogs() {
    const { items } = useSelector(s => s.audits);

    return (
        <div style={{ padding: 24 }}>
            <h2 style={{ fontWeight: 900, marginBottom: 12 }}>Audit Logs</h2>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                <thead style={{ background: '#f8fafc' }}>
                    <tr>
                        <th style={{ textAlign: 'left', padding: '8px' }}>Time</th>
                        <th style={{ textAlign: 'left', padding: '8px' }}>Type</th>
                        <th style={{ textAlign: 'left', padding: '8px' }}>Entity</th>
                        <th style={{ textAlign: 'left', padding: '8px' }}>Actor</th>
                        <th style={{ textAlign: 'left', padding: '8px' }}>Tenant</th>
                        <th style={{ textAlign: 'left', padding: '8px' }}>Meta</th>
                    </tr>
                </thead>
                <tbody>
                    {items.length === 0 && (
                        <tr>
                            <td colSpan={6} style={{ padding: '12px', color: '#64748b' }}>
                                No audit entries yet.
                            </td>
                        </tr>
                    )}
                    {items.map((e, i) => (
                        <tr key={i}>
                            <td style={{ padding: '8px' }}>{new Date(e.timestamp).toLocaleString('en-ZA')}</td>
                            <td style={{ padding: '8px' }}>{e.type}</td>
                            <td style={{ padding: '8px' }}>{e.entity} #{e.entityId}</td>
                            <td style={{ padding: '8px' }}>{e.actionBy?.name} ({e.actionBy?.role})</td>
                            <td style={{ padding: '8px' }}>{e.tenantId}</td>
                            <td style={{ padding: '8px' }}>
                                <code style={{ fontSize: '0.8rem' }}>{JSON.stringify(e.meta)}</code>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
