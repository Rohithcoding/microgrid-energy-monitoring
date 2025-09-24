#!/bin/bash

# Microgrid Frontend Startup Script
# This script starts the React frontend with enhanced features

echo "🎨 Starting Microgrid Frontend Dashboard"
echo "======================================="

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+ and try again."
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm and try again."
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "⚠️  Warning: Node.js version $NODE_VERSION detected. Recommended: 16+"
fi

# Clean cache and reinstall if needed
if [ "$1" = "--clean" ]; then
    echo "🧹 Cleaning npm cache and node_modules..."
    npm cache clean --force
    rm -rf node_modules package-lock.json
fi

# Install dependencies
if [ ! -d "node_modules" ] || [ "$1" = "--clean" ]; then
    echo "📦 Installing dependencies..."
    npm install
else
    echo "📦 Dependencies already installed"
fi

echo ""
echo "🌟 Frontend Features Enabled:"
echo "   ✅ Modern React 18 with functional components"
echo "   ✅ Tailwind CSS for responsive design"
echo "   ✅ Framer Motion for smooth animations"
echo "   ✅ Role-based authentication UI"
echo "   ✅ Real-time data visualization with Recharts"
echo "   ✅ Mobile-responsive navigation"
echo "   ✅ Error boundaries & loading states"
echo "   ✅ Toast notifications"
echo ""

echo "🔗 Dashboard Features:"
echo "   📊 Real-time system monitoring"
echo "   🤖 AI insights & predictions"
echo "   🚨 Alert management system"
echo "   ⚙️  System configuration (Admin only)"
echo ""

echo "👤 Demo Login Credentials:"
echo "   🔹 Operator: Just select 'operator' role and click login"
echo "   🔹 Admin: Just select 'admin' role and click login"
echo ""

echo "▶️  Starting development server on http://localhost:3000"
echo "   The dashboard will open automatically in your browser"
echo "   Press Ctrl+C to stop"
echo ""

# Set environment variable to prevent browser auto-open if needed
if [ "$1" = "--no-browser" ]; then
    export BROWSER=none
fi

# Start the development server
npm start
