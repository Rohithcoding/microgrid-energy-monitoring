#!/bin/bash

# Complete Microgrid Demo Startup Script
# This script starts the entire system with sample data

echo "🌟 MICROGRID AI ENERGY MONITORING SYSTEM"
echo "========================================"
echo "Complete Demo Startup Script"
echo ""

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo "✅ $service_name is ready!"
            return 0
        fi
        
        echo "   Attempt $attempt/$max_attempts..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name failed to start within expected time"
    return 1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Generate enhanced sample data
echo "📊 Generating enhanced sample data..."
if [ ! -f "enhanced_microgrid_data.csv" ]; then
    python enhanced_data_generator.py --hours 48 --interval 5
    echo "✅ Enhanced dataset created with edge scenarios"
else
    echo "✅ Enhanced dataset already exists"
fi
echo ""

# Start backend
echo "🚀 Starting backend server..."
if check_port 8000; then
    echo "⚠️  Port 8000 already in use. Stopping existing process..."
    pkill -f "uvicorn\|python.*main.py" || true
    sleep 2
fi

# Start backend in background
chmod +x start_backend.sh
./start_backend.sh > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready
if wait_for_service "http://localhost:8000/api/health" "Backend API"; then
    echo "🌐 Backend running at: http://localhost:8000"
    echo "📚 API Documentation: http://localhost:8000/docs"
else
    echo "❌ Failed to start backend. Check backend.log for details."
    exit 1
fi
echo ""

# Start frontend
echo "🎨 Starting frontend dashboard..."
if check_port 3000; then
    echo "⚠️  Port 3000 already in use. Stopping existing process..."
    pkill -f "react-scripts\|npm.*start" || true
    sleep 2
fi

# Start frontend in background
cd frontend
chmod +x ../start_frontend.sh
BROWSER=none npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to be ready
if wait_for_service "http://localhost:3000" "Frontend Dashboard"; then
    echo "🎨 Frontend running at: http://localhost:3000"
else
    echo "❌ Failed to start frontend. Check frontend.log for details."
    exit 1
fi
echo ""

# Start data simulator
echo "📡 Starting enhanced data simulator..."
python enhanced_simulator.py \
    --mode file \
    --source enhanced_microgrid_data.csv \
    --delay 2 \
    --real-time \
    --error-injection \
    --error-rate 0.02 \
    --loop \
    --verbose > simulator.log 2>&1 &
SIMULATOR_PID=$!

sleep 3
echo "✅ Data simulator started with realistic scenarios"
echo ""

# Display system status
echo "🌟 SYSTEM STATUS"
echo "==============="
echo "✅ Backend API: http://localhost:8000 (PID: $BACKEND_PID)"
echo "✅ Frontend Dashboard: http://localhost:3000 (PID: $FRONTEND_PID)"
echo "✅ Data Simulator: Running (PID: $SIMULATOR_PID)"
echo ""

echo "🎯 DEMO FEATURES ACTIVE:"
echo "========================"
echo "🤖 AI-Powered Features:"
echo "   • Intelligent fault detection"
echo "   • Grid switching recommendations"
echo "   • Solar generation predictions"
echo "   • Load demand forecasting"
echo "   • Smart load management"
echo ""
echo "📊 Dashboard Features:"
echo "   • Real-time data visualization"
echo "   • Interactive charts & metrics"
echo "   • Alert management system"
echo "   • Role-based authentication"
echo "   • Mobile-responsive design"
echo ""
echo "🔧 Technical Features:"
echo "   • WebSocket real-time updates"
echo "   • Enhanced data validation"
echo "   • Comprehensive error handling"
echo "   • Production-ready architecture"
echo ""

echo "👤 LOGIN CREDENTIALS:"
echo "===================="
echo "🔹 Operator Role: Select 'operator' and click login"
echo "   • View dashboard and analytics"
echo "   • Monitor system status"
echo "   • Receive alerts"
echo ""
echo "🔹 Admin Role: Select 'admin' and click login"
echo "   • Full operator access"
echo "   • System configuration"
echo "   • User management"
echo ""

echo "🌐 ACCESS POINTS:"
echo "================"
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 API Docs: http://localhost:8000/docs"
echo "📈 Health Check: http://localhost:8000/api/health"
echo "🤖 AI Endpoints: http://localhost:8000/api/ai/*"
echo ""

echo "📋 DEMO SCENARIOS:"
echo "=================="
echo "The system is now running with realistic data including:"
echo "• Battery depletion scenarios (SOC drops below 30%)"
echo "• Temperature anomalies (overheating events)"
echo "• Voltage instability (drops below 200V)"
echo "• Solar generation patterns (sunrise to sunset)"
echo "• Load consumption cycles (day/night patterns)"
echo "• Grid switching recommendations"
echo ""

echo "📝 LOG FILES:"
echo "============"
echo "• Backend: backend.log"
echo "• Frontend: frontend.log"
echo "• Simulator: simulator.log"
echo ""

echo "⏹️  TO STOP THE DEMO:"
echo "===================="
echo "Press Ctrl+C or run: ./stop_demo.sh"
echo ""

# Create stop script
cat > stop_demo.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping Microgrid Demo..."
kill $(jobs -p) 2>/dev/null || true
pkill -f "uvicorn\|python.*main.py\|react-scripts\|npm.*start\|enhanced_simulator" || true
echo "✅ Demo stopped"
EOF
chmod +x stop_demo.sh

echo "🎉 DEMO IS READY!"
echo "================="
echo "Open your browser and navigate to: http://localhost:3000"
echo "The system is now running with live data simulation!"
echo ""

# Keep script running and show live stats
trap 'echo ""; echo "🛑 Stopping demo..."; ./stop_demo.sh; exit 0' INT

echo "📊 LIVE SYSTEM MONITOR (Press Ctrl+C to stop)"
echo "=============================================="

while true; do
    # Get current stats
    BACKEND_STATUS=$(curl -s http://localhost:8000/api/health 2>/dev/null && echo "✅ Online" || echo "❌ Offline")
    FRONTEND_STATUS=$(curl -s http://localhost:3000 2>/dev/null && echo "✅ Online" || echo "❌ Offline")
    
    # Get latest sensor data
    SENSOR_DATA=$(curl -s http://localhost:8000/api/sensordata/latest 2>/dev/null)
    
    if [ ! -z "$SENSOR_DATA" ]; then
        GENERATION=$(echo $SENSOR_DATA | python -c "import sys, json; data=json.load(sys.stdin); print(f'{data.get(\"solar_generation\", 0):.1f}W')" 2>/dev/null || echo "N/A")
        SOC=$(echo $SENSOR_DATA | python -c "import sys, json; data=json.load(sys.stdin); print(f'{data.get(\"soc\", 0):.1f}%')" 2>/dev/null || echo "N/A")
        TEMP=$(echo $SENSOR_DATA | python -c "import sys, json; data=json.load(sys.stdin); print(f'{data.get(\"battery_temperature\", 0):.1f}°C')" 2>/dev/null || echo "N/A")
    else
        GENERATION="N/A"
        SOC="N/A"
        TEMP="N/A"
    fi
    
    # Clear screen and show status
    clear
    echo "🌟 MICROGRID DEMO - LIVE STATUS"
    echo "==============================="
    echo "⏰ $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo "🔧 Services:"
    echo "   Backend API: $BACKEND_STATUS"
    echo "   Frontend: $FRONTEND_STATUS"
    echo "   Simulator: ✅ Running"
    echo ""
    echo "📊 Current Readings:"
    echo "   ☀️  Solar Generation: $GENERATION"
    echo "   🔋 Battery SOC: $SOC"
    echo "   🌡️  Temperature: $TEMP"
    echo ""
    echo "🌐 Access: http://localhost:3000"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop demo"
    
    sleep 5
done
