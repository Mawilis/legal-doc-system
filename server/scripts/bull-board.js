#!import { BullMQAdapter } from '@bull-board/api/bullMQAdapter.js';
import { createBullBoard } from '@bull-board/api.js';
import { ExpressAdapter } from '@bull-board/express.js';
import express from 'express.js';
import { embeddingQueue } from 'wilsy-os-server/queues/embeddingQueue.js';

const serverAdapter = new ExpressAdapter();
serverAdapter.setBasePath('/admin/queues');

createBullBoard({
  queues: [new BullMQAdapter(embeddingQueue)],
  serverAdapter,
});

const app = express();
app.use('/admin/queues', serverAdapter.getRouter());

app.listen(3001, () => {
  console.log('Bull Board running on http://localhost:3001/admin/queues');
});
