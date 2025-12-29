#!/bin/bash
echo "🚀 LAUNCHING BILLION-DOLLAR LEGAL OS..."

# Kill any existing node processes on these ports to prevent errors
lsof -ti:3001,6000,6100 | xargs kill -9 2>/dev/null

# 1. Start Ledger (Background)
echo "Starting Ledger Service (Port 6000)..."
cd services/ledger
nohup npm start > ../../ledger.log 2>&1 &
PID_LEDGER=$!

# 2. Start Standards (Background)
echo "Starting Standards Service (Port 6100)..."
cd ../standards
nohup npm start > ../../standards.log 2>&1 &
PID_STANDARDS=$!

# 3. Start Main Server (Foreground)
echo "Starting Main Gateway (Port 3001)..."
cd ../../server
npm start &
PID_SERVER=$!

# Wait for user to exit
echo "✅ ALL SYSTEMS GO. Logs are being written to ledger.log and standards.log"
echo "Press CTRL+C to stop everything."

trap "kill $PID_LEDGER $PID_STANDARDS $PID_SERVER; exit" SIGINT
wait
