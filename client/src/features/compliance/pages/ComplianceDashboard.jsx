/**
 * File: client/src/features/compliance/pages/ComplianceDashboard.jsx
 * -----------------------------------------------------------------------------
 * STATUS: EPITOME | Standards & Rules Engine
 * -----------------------------------------------------------------------------
 */

import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, Grid, Chip, List, ListItem, ListItemText } from '@mui/material';
import { FiCheckCircle } from 'react-icons/fi';
import axios from 'axios';

const API_URL = process.env.REACT_APP_GATEWAY_URL || 'http://localhost:3001';

export default function ComplianceDashboard() {
    const [rules, setRules] = useState([]);

    useEffect(() => {
        // Fetch Rules from Standards Microservice
        axios.get(`${API_URL}/api/standards/rules`)
            .then(res => setRules(res.data))
            .catch(err => console.error("Compliance Engine Offline"));
    }, []);

    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h4" sx={{ mb: 3, fontWeight: 800 }}>
                <FiCheckCircle style={{ marginRight: 10, verticalAlign: 'middle' }} />
                Standards & Compliance
            </Typography>

            <Grid container spacing={3}>
                {rules.length > 0 ? rules.map((rule) => (
                    <Grid item xs={12} md={6} key={rule._id}>
                        <Paper sx={{ p: 3, height: '100%' }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                                <Typography variant="h6" fontWeight={700}>{rule.courtType}</Typography>
                                <Chip label="ACTIVE" color="success" size="small" />
                            </Box>

                            <Typography variant="subtitle2" color="text.secondary" sx={{ mt: 2 }}>REQUIRED FIELDS</Typography>
                            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
                                {rule.requiredFields.map(f => (
                                    <Chip key={f} label={f} variant="outlined" />
                                ))}
                            </Box>

                            <Typography variant="subtitle2" color="text.secondary" sx={{ mt: 3 }}>VALIDATION PATTERNS</Typography>
                            <List dense>
                                {Object.entries(rule.regexPatterns || {}).map(([key, val]) => (
                                    <ListItem key={key} disablePadding>
                                        <ListItemText primary={key} secondary={String(val)} sx={{ fontFamily: 'monospace' }} />
                                    </ListItem>
                                ))}
                            </List>
                        </Paper>
                    </Grid>
                )) : (
                    <Grid item xs={12}>
                        <Paper sx={{ p: 4, textAlign: 'center' }}>
                            <Typography>Connecting to Standards Microservice...</Typography>
                        </Paper>
                    </Grid>
                )}
            </Grid>
        </Box>
    );
}