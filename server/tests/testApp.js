/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ 🧪 TEST APP - WILSY OS 2050                                               ║
  ║ Minimal Express app wired with real auth middleware                       ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import express from 'express';
import crypto from 'crypto';
import { protect } from '../middleware/auth.js';
import auditRoutes from '../routes/superadmin/audit.routes.js';   // ✅ add this

const app = express();
app.use(express.json());

// Request ID middleware
app.use((req, res, next) => {
  req.id = req.headers['x-request-id'] || crypto.randomBytes(8).toString('hex');
  res.setHeader('x-request-id', req.id);
  next();
});

// Dashboard routes with protect middleware
app.get('/api/dashboard/metrics', protect, (req, res) => {
  res.json({
    success: true,
    data: {
      totalDocuments: 3,
      documentsByStatus: { published: 2, draft: 1, archived: 0 },
      recentActivity: [],
      storageUsed: 1024 * 1024 * 5,
      complianceScore: 98
    }
  });
});

app.get('/api/dashboard/activity', protect, (req, res) => {
  res.json({ success: true, data: [{ id: 1, action: 'Document created', timestamp: new Date() }] });
});

app.get('/api/dashboard/usage', protect, (req, res) => {
  const period = req.query.period || '30d';
  res.json({ success: true, data: { period, documentCount: 3, storageUsed: 1024 * 1024 * 5, userCount: 1, apiCalls: 42 } });
});

app.get('/api/dashboard/compliance', protect, (req, res) => {
  res.json({ success: true, data: { complianceScore: 98, activePolicies: ['ISO27001','SOC2','POPIA'], pendingActions: [], lastAudit: new Date() } });
});

app.get('/api/dashboard/forecast', protect, (req, res) => {
  const months = parseInt(req.query.months) || 12;
  res.json({
    success: true,
    data: {
      forecast: Array(months).fill(0).map((_, i) => ({ month: i+1, predictedDocuments: 10 + i*2 })),
      confidence: 92,
      recommendations: ['Increase storage capacity in 3 months','Review compliance policies quarterly']
    }
  });
});

// ✅ Mount Super Admin Audit routes
app.use('/api/superadmin/audit', auditRoutes);

// Health check
app.get('/health', (req, res) => res.json({ status: 'healthy', timestamp: new Date() }));

// 404 handler
app.use('*', (req, res) => res.status(404).json({ success: false, message: 'Route not found' }));

// Error handler
app.use((err, req, res, next) => {
  console.error('Test app error:', err);
  res.status(500).json({ success: false, message: 'Internal server error' });
});

export default app;
