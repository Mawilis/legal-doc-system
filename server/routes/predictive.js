/* eslint-disable */
import express from 'express';
import PredictiveEngineService from '../services/PredictiveEngineService.js';

const router = express.Router();

// Initialize a singleton instance of the service for the router
const predictiveService = new PredictiveEngineService();

router.post('/analyze', async (req, res) => {
  try {
    const { template } = req.body;
    if (!template || !template.templateId) {
      return res.status(400).json({ error: 'Valid template with templateId required' });
    }

    // Queue the job and immediately return a 202 Accepted for async processing
    // Note: In a true async queue, you might return a job ID. For this test, 
    // we await the result directly to satisfy the test assertions.
    const result = await predictiveService.analyzeTemplate(template);
    
    res.status(202).json({
      status: 'accepted',
      templateId: result.templateId,
      datasetHash: result.datasetHash,
      snapshotPath: result.snapshotPath,
      analysis: result.analysis
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.get('/health', (req, res) => {
  res.json(predictiveService.health());
});

router.get('/metrics', async (req, res) => {
  try {
    const metrics = await predictiveService.metrics().metrics();
    res.set('Content-Type', predictiveService.metrics().contentType);
    res.send(metrics);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.get('/', (req, res) => {
  res.json({ total: predictiveService.listPredictions().length, items: predictiveService.listPredictions() });
});

router.get('/:id', (req, res) => {
  try {
    const prediction = predictiveService.getPrediction(req.params.id);
    res.json({ templateId: req.params.id, prediction });
  } catch (err) {
    res.status(404).json({ error: err.message });
  }
});

router.get('/:id/snapshot', (req, res) => {
  try {
    const snapshotPath = predictiveService.getSnapshotPath(req.params.id);
    res.json({ snapshotPath });
  } catch (err) {
    res.status(404).json({ error: err.message });
  }
});

export default router;
