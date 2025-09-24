#!/bin/bash
echo "🛑 Stopping Microgrid Demo..."
kill $(jobs -p) 2>/dev/null || true
pkill -f "uvicorn\|python.*main.py\|react-scripts\|npm.*start\|enhanced_simulator" || true
echo "✅ Demo stopped"
