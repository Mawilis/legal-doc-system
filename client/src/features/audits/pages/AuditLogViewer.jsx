/**
 * File: client/src/features/audits/pages/AuditLogViewer.jsx
 * -----------------------------------------------------------------------------
 * STATUS: EPITOME | Forensic Data Explorer
 * -----------------------------------------------------------------------------
 */

import React from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableHead, TableRow, Chip } from '@mui/material';
import { FiShield } from 'react-icons/fi';

// MOCK DATA (Until you connect the audit API endpoint)
const MOCK_LOGS = [
    { id: 1, action: 'USER_LOGIN', actor: 'Wilson Khanyezi', role: 'SuperAdmin', ip: '197.23.12.1', severity: 'INFO', time: '10:02 AM' },
    { id: 2, action: 'INVOICE_GENERATED', actor: 'Billing Service', role: 'SYSTEM', ip: '127.0.0.1', severity: 'INFO', time: '10:05 AM' },
    { id: 3, action: 'FICA_EXPIRED', actor: 'Compliance Bot', role: 'SYSTEM', ip: '127.0.0.1', severity: 'WARNING', time: '10:15 AM' },
    { id: 4, action: 'SIGNATURE_VERIFIED', actor: 'Crypto Vault', role: 'SYSTEM', ip: '127.0.0.1', severity: 'INFO', time: '10:20 AM' },
];

export default function AuditLogViewer() {
    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h4" sx={{ mb: 3, fontWeight: 800 }}>
                <FiShield style={{ marginRight: 10, verticalAlign: 'middle' }} />
                Audit Forensics
            </Typography>

            <Paper sx={{ overflow: 'hidden' }}>
                <Table>
                    <TableHead sx={{ bgcolor: '#F8FAFC' }}>
                        <TableRow>
                            <TableCell>Time</TableCell>
                            <TableCell>Severity</TableCell>
                            <TableCell>Action</TableCell>
                            <TableCell>Actor</TableCell>
                            <TableCell>IP Address</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {MOCK_LOGS.map((log) => (
                            <TableRow key={log.id} hover>
                                <TableCell sx={{ fontFamily: 'monospace' }}>{log.time}</TableCell>
                                <TableCell>
                                    <Chip
                                        label={log.severity}
                                        size="small"
                                        color={log.severity === 'WARNING' ? 'warning' : 'default'}
                                        variant="outlined"
                                    />
                                </TableCell>
                                <TableCell sx={{ fontWeight: 600 }}>{log.action}</TableCell>
                                <TableCell>
                                    {log.actor}
                                    <Typography variant="caption" display="block" color="text.secondary">{log.role}</Typography>
                                </TableCell>
                                <TableCell sx={{ color: 'text.secondary' }}>{log.ip}</TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </Paper>
        </Box>
    );
}


