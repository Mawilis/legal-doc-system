#!/bin/bash

echo "=== CLEANING UP UNUSED VARIABLES ==="

# 1. /server/validators/popiaConsentValidator.js
echo "Fixing popiaConsentValidator.js..."
sed -i '' '37s/const POPIA_RETENTION_PERIODS =.*/\/\/ const POPIA_RETENTION_PERIODS = require("..\/constants\/popiaRetentionPeriods"); \/\/ Unused variable/' /Users/wilsonkhanyezi/legal-doc-system/server/validators/popiaConsentValidator.js

# 2. /server/validators/popiaValidator.js
echo "Fixing popiaValidator.js..."

# Remove unused imports if they exist
sed -i '' '91s/const bcrypt =.*/\/\/ const bcrypt = require("bcrypt"); \/\/ Unused variable/' /Users/wilsonkhanyezi/legal-doc-system/server/validators/popiaValidator.js
sed -i '' '92s/const mongoose =.*/\/\/ const mongoose = require("mongoose"); \/\/ Unused variable/' /Users/wilsonkhanyezi/legal-doc-system/server/validators/popiaValidator.js
sed -i '' '95s/const { sanitizePIIInput } =.*/\/\/ const { sanitizePIIInput } = require("..\/utils\/piiSanitizer"); \/\/ Unused variable/' /Users/wilsonkhanyezi/legal-doc-system/server/validators/popiaValidator.js

# Fix function parameters
sed -i '' '2037s/(entityType)/(_entityType)/' /Users/wilsonkhanyezi/legal-doc-system/server/validators/popiaValidator.js
sed -i '' '2046s/(_, data)/(_unused, data)/' /Users/wilsonkhanyezi/legal-doc-system/server/validators/popiaValidator.js

# Comment out unused variable
sed -i '' '2871s/const startTime =.*/\/\/ const startTime = Date.now(); \/\/ Unused variable/' /Users/wilsonkhanyezi/legal-doc-system/server/validators/popiaValidator.js

# 3. /server/validators/superAdminValidator.js
echo "Fixing superAdminValidator.js..."
sed -i '' '1114s/(email)/(_email)/' /Users/wilsonkhanyezi/legal-doc-system/server/validators/superAdminValidator.js
sed -i '' '1125s/(idNumber)/(_idNumber)/' /Users/wilsonkhanyezi/legal-doc-system/server/validators/superAdminValidator.js

# 4. /server/websockets/auditWebSocket.js
echo "Fixing auditWebSocket.js..."
sed -i '' '85s/const complianceService =.*/\/\/ const complianceService = require("..\/services\/complianceService"); \/\/ Unused variable/' /Users/wilsonkhanyezi/legal-doc-system/server/websockets/auditWebSocket.js
sed -i '' '614s/(verificationId)/(_verificationId)/' /Users/wilsonkhanyezi/legal-doc-system/server/websockets/auditWebSocket.js

# 5. /server/worker-bootstrap/fileWorkers.js
echo "Fixing fileWorkers.js..."
sed -i '' '28s/const path =.*/\/\/ const path = require("path"); \/\/ Unused variable/' /Users/wilsonkhanyezi/legal-doc-system/server/worker-bootstrap/fileWorkers.js

# 6. /server/workers/reportWorker.js
echo "Fixing reportWorker.js..."
# Replace with actual usage or comment
sed -i '' '20s/async function generateReport(report)/async function generateReport(_report)/' /Users/wilsonkhanyezi/legal-doc-system/server/workers/reportWorker.js

# 7. /server/workers/retentionAgenda.js
echo "Fixing retentionAgenda.js..."
sed -i '' '658s/(recordData)/(_recordData)/' /Users/wilsonkhanyezi/legal-doc-system/server/workers/retentionAgenda.js

# Fix destructuring - only destructure what you need
sed -i '' '926s/const { _id, __v, createdAt, updatedAt, .* } = recordData;/const cleanData = recordData; \/\/ Removed unused destructuring/' /Users/wilsonkhanyezi/legal-doc-system/server/workers/retentionAgenda.js

sed -i '' '1377s/const mermaidDiagram =.*/\/\/ const mermaidDiagram = generateDiagram(); \/\/ Unused variable/' /Users/wilsonkhanyezi/legal-doc-system/server/workers/retentionAgenda.js
sed -i '' '1452s/const mongoose =.*/\/\/ const mongoose = require("mongoose"); \/\/ Unused variable/' /Users/wilsonkhanyezi/legal-doc-system/server/workers/retentionAgenda.js
sed -i '' '1504s/const Agenda =.*/\/\/ const Agenda = require("agenda"); \/\/ Unused variable/' /Users/wilsonkhanyezi/legal-doc-system/server/workers/retentionAgenda.js

echo "=== CLEANUP COMPLETE ==="
echo "Running ESLint to verify..."
