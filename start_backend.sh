#!/bin/bash

# Microgrid Backend Startup Script
# This script starts the FastAPI backend with enhanced features

echo "🚀 Starting Microgrid Backend Server"
echo "=================================="

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+ and try again."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install/upgrade dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Navigate to backend directory
cd backend

# Check if database needs initialization
if [ ! -f "enhanced_microgrid.db" ]; then
    echo "🗄️  Initializing database..."
    python -c "
from enhanced_models import Base, engine
from auth import create_default_users, get_db

# Create tables
Base.metadata.create_all(bind=engine)

# Create default users
db = next(get_db())
create_default_users(db)
db.close()

print('✅ Database initialized with default users')
print('   👤 Admin: admin / admin123')
print('   👤 Operator: operator / operator123')
"
fi

echo ""
echo "🌟 Backend Features Enabled:"
echo "   ✅ Enhanced data validation with Pydantic"
echo "   ✅ JWT authentication & role-based access"
echo "   ✅ WebSocket support for real-time updates"
echo "   ✅ Comprehensive API documentation"
echo "   ✅ Advanced AI predictions & fault detection"
echo "   ✅ Extensive logging & error handling"
echo ""

echo "🔗 API Endpoints:"
echo "   📊 Health Check: http://localhost:8000/api/health"
echo "   📚 API Docs: http://localhost:8000/docs"
echo "   🔐 Authentication: http://localhost:8000/auth/login"
echo "   📡 WebSocket: ws://localhost:8000/ws"
echo ""

echo "▶️  Starting server on http://localhost:8000"
echo "   Press Ctrl+C to stop"
echo ""

# Start the server
echo "🚀 Starting Uvicorn server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level info
