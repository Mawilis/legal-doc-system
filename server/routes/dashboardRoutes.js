import express from "express";
import path from "path";
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const router = express.Router();

router.get('/warroom', (req, res) => {
  const filePath = path.join(__dirname, '../public/dashboard/warroom.html');
  res.sendFile(filePath);
});

export default router;
