#!/**
 * WILSY OS - User Routes
 */

import express from 'express';

const router = express.Router();

router.get('/', (req, res) => {
  res.json({ users: [], message: 'User routes working' });
});

router.get('/:id', (req, res) => {
  res.json({ userId: req.params.id, message: 'User found' });
});

export default router;
