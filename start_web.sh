#!/bin/bash
# TrustWise Web Interface Launcher for Linux/Mac

echo "============================================================"
echo "TrustWise Web Interface (TypeScript)"
echo "============================================================"
echo ""
echo "Building TypeScript server..."
echo ""

cd "$(dirname "$0")/web" || exit 1
npm run build || { echo "Build failed"; exit 1; }

echo ""
echo "Starting server..."
echo ""
echo "Once started, open your browser to: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

npm start
