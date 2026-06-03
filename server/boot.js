import { server } from './app.js';

// Shifting to 5050 to bypass macOS AirPlay restrictions
const PORT = process.env.PORT || 5050;

server.listen(PORT, () => {
  console.log(`🚀 [WILSY_GATEWAY]: Core API listening on port ${PORT}`);
  console.log(`🛡️  Execute the Genesis Event: POST http://localhost:${PORT}/api/tenants`);
});
