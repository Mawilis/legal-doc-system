const express = require('express');
const { tenantContextMiddleware } = require('./middleware/tenantContext');

const app = express();
app.use(express.json());

// Apply tenant middleware
app.use(tenantContextMiddleware({
  failClosed: true,
  auditAllRequests: true,
  validateTenantStatus: false // Set to true when Tenant model exists
}));

// Test route
app.get('/api/test', (req, res) => {
  res.json({
    message: 'Tenant context test',
    tenantContext: req.tenantContext,
    timestamp: new Date().toISOString()
  });
});

// Protected route
app.get('/api/documents', (req, res) => {
  const tenantId = req.tenantContext.extractionResult.tenantId;
  res.json({
    message: `Documents for tenant: ${tenantId}`,
    tenantId,
    timestamp: new Date().toISOString()
  });
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'tenant-middleware-test' });
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Test server running on http://localhost:${PORT}`);
  console.log('Test endpoints:');
  console.log('  GET /api/test - Test tenant extraction');
  console.log('  GET /api/documents - Protected route (requires tenant)');
  console.log('  GET /health - Health check');
});
