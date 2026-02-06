/**
 * File: client/src/features/admin/pages/SystemHealth.jsx
 * -----------------------------------------------------------------------------
 * STATUS: EPITOME | System Observability Deck
 * -----------------------------------------------------------------------------
 */

import React, { useState, useEffect } from 'react';
import {
    Box, Grid, Paper, Typography, Chip, IconButton, LinearProgress, Alert
} from '@mui/material';
import { FiRefreshCw, FiServer, FiCpu, FiActivity } from 'react-icons/fi';
import axios from 'axios';

// API Configuration
const API_URL = process.env.REACT_APP_GATEWAY_URL || 'http://localhost:3001';

export default function SystemHealth() {
    const [health, setHealth] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [lastUpdated, setLastUpdated] = useState(new Date());

    const checkHealth = async () => {
        setLoading(true);
        try {
            // Fetches status from the Main Gateway
            const res = await axios.get(`${API_URL}/api/health`);
            setHealth(res.data);
            setError(null);
        } catch (err) {
            setError('Gateway Unreachable');
            setHealth(null);
        } finally {
            setLoading(false);
            setLastUpdated(new Date());
        }
    };

    useEffect(() => { checkHealth(); }, []);

    return (
        <Box sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="h4" sx={{ fontWeight: 800 }}>
                    <FiActivity style={{ marginRight: 10, verticalAlign: 'middle' }} />
                    System Status
                </Typography>
                <IconButton onClick={checkHealth} disabled={loading} color="primary">
                    <FiRefreshCw className={loading ? 'spin' : ''} />
                </IconButton>
            </Box>

            {loading && <LinearProgress sx={{ mb: 2 }} />}
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

            <Grid container spacing={3}>
                {/* 1. GATEWAY STATUS */}
                <Grid item xs={12} md={4}>
                    <StatusCard
                        title="API Gateway"
                        status={health ? 'ONLINE' : 'OFFLINE'}
                        icon={<FiServer />}
                        detail={health ? `Socket Clients: ${health.socketClients}` : 'No Signal'}
                    />
                </Grid>

                {/* 2. DATABASE STATUS */}
                <Grid item xs={12} md={4}>
                    <StatusCard
                        title="MongoDB Atlas"
                        status={health?.dbState === 'connected' ? 'ONLINE' : 'OFFLINE'}
                        icon={<FiServer />}
                        detail="Primary Cluster"
                    />
                </Grid>

                {/* 3. AI NEURAL ENGINE */}
                <Grid item xs={12} md={4}>
                    <StatusCard
                        title="AI Microservice"
                        // Mocked check based on Gateway health for now
                        status={health ? 'ONLINE' : 'UNKNOWN'}
                        icon={<FiCpu />}
                        detail="Port 6500 (Risk & NLP)"
                    />
                </Grid>
            </Grid>

            <Typography variant="caption" sx={{ display: 'block', mt: 4, color: 'text.secondary' }}>
                Last Diagnostic: {lastUpdated.toLocaleTimeString()}
            </Typography>

            <style>{`
                .spin { animation: spin 1s linear infinite; }
                @keyframes spin { 100% { transform: rotate(360deg); } }
            `}</style>
        </Box>
    );
}

// Sub-component for consistency
function StatusCard({ title, status, icon, detail }) {
    const isOnline = status === 'ONLINE';
    return (
        <Paper sx={{ p: 3, borderLeft: `6px solid ${isOnline ? '#10B981' : '#EF4444'}` }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                    <Typography variant="h6" sx={{ fontWeight: 700 }}>{title}</Typography>
                    <Typography variant="body2" color="text.secondary">{detail}</Typography>
                </Box>
                <Box sx={{ fontSize: '2rem', opacity: 0.2 }}>{icon}</Box>
            </Box>
            <Chip
                label={status}
                size="small"
                sx={{
                    mt: 2,
                    fontWeight: 800,
                    bgcolor: isOnline ? '#D1FAE5' : '#FEE2E2',
                    color: isOnline ? '#065F46' : '#991B1B'
                }}
            />
        </Paper>
    );
}

