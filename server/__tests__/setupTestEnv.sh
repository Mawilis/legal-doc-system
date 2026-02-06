#!/bin/bash
# Wilsy OS - Test Environment Setup Script
# Sets up everything needed to run Case model tests

echo "Setting up test environment for Case model..."

# Navigate to project root
cd /Users/wilsonkhanyezi/legal-doc-system/server

# Install test dependencies if not already installed
echo "Checking/installing test dependencies..."
npm list mongodb-memory-server || npm install --save-dev mongodb-memory-server
npm list jest || npm install --save-dev jest
npm list supertest || npm install --save-dev supertest

# Create test .env file if it doesn't exist
if [ ! -f ".env.test" ]; then
    echo "Creating .env.test file..."
    cat > .env.test << 'ENVEOF'
# Test Environment Variables
NODE_ENV=test

# MongoDB Test Database
MONGO_URI_TEST=mongodb+srv://wilsonkhanyezi:*******@legal-doc-test.xmlpwmq.mongodb.net/?retryWrites=true&w=majority&appName=legal-doc-test

# Test JWT Secret
JWT_SECRET=test_jwt_secret_do_not_use_in_production

# Vault Test Credentials (mocked in tests)
VAULT_ADDR=http://localhost:8200
VAULT_TOKEN=test_token

# Test Email Configuration (mocked)
SMTP_HOST=smtp.test.com
SMTP_PORT=587
SMTP_USER=test@wilsyos.com
SMTP_PASS=test_password

# Test File Storage (mocked)
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=test_access_key
S3_SECRET_KEY=test_secret_key
S3_BUCKET=test-bucket

# Test Rate Limits
RATE_LIMIT_WINDOW=900000
RATE_LIMIT_MAX=100
ENVEOF
    echo ".env.test created with test configuration"
fi

# Check if models directory exists
if [ ! -d "models" ]; then
    echo "ERROR: models directory not found!"
    echo "Please ensure you're in the correct directory: /Users/wilsonkhanyezi/legal-doc-system/server"
    exit 1
fi

# Check if Case model exists
if [ ! -f "models/Case.js" ]; then
    echo "ERROR: Case.js model not found!"
    echo "Please generate the Case model first using the provided script"
    exit 1
fi

echo "Test environment setup complete!"
echo ""
echo "To run the Case model tests:"
echo "1. Ensure MongoDB is running or use MONGO_URI_TEST"
echo "2. Run: npm test -- __tests__/models/Case.test.js"
echo "3. Or run specific test: npm test -- --testNamePattern='PAIA Request Tracking'"
echo ""
echo "To run all tests: npm test"
