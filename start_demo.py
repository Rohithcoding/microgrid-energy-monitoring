#!/usr/bin/env python3
"""
Microgrid Energy Monitoring System - Demo Launcher
This script starts the complete demo environment
"""

import subprocess
import sys
import time
import os
import signal
import requests
from threading import Thread

class DemoLauncher:
    def __init__(self):
        self.processes = []
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        print("🔍 Checking dependencies...")
        
        # Check Python dependencies
        try:
            import fastapi, uvicorn, pandas, numpy, requests
            print("✅ Python dependencies OK")
        except ImportError as e:
            print(f"❌ Missing Python dependency: {e}")
            print("Run: pip install -r requirements.txt")
            return False
        
        # Check if Node.js is available
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Node.js {result.stdout.strip()} found")
            else:
                print("❌ Node.js not found")
                return False
        except FileNotFoundError:
            print("❌ Node.js not found. Please install Node.js")
            return False
        
        return True
    
    def install_frontend_deps(self):
        """Install frontend dependencies if needed"""
        frontend_dir = os.path.join(self.base_dir, 'frontend')
        node_modules = os.path.join(frontend_dir, 'node_modules')
        
        if not os.path.exists(node_modules):
            print("📦 Installing frontend dependencies...")
            try:
                subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
                print("✅ Frontend dependencies installed")
            except subprocess.CalledProcessError:
                print("❌ Failed to install frontend dependencies")
                return False
        else:
            print("✅ Frontend dependencies already installed")
        
        return True
    
    def start_backend(self):
        """Start the FastAPI backend"""
        print("🚀 Starting backend server...")
        backend_dir = os.path.join(self.base_dir, 'backend')
        
        try:
            process = subprocess.Popen(
                [sys.executable, 'main.py'],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes.append(('Backend', process))
            
            # Wait for backend to start
            for i in range(30):  # Wait up to 30 seconds
                try:
                    response = requests.get('http://localhost:8000/api/health', timeout=1)
                    if response.status_code == 200:
                        print("✅ Backend server started successfully")
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)
            
            print("❌ Backend server failed to start")
            return False
            
        except Exception as e:
            print(f"❌ Error starting backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the React frontend"""
        print("🎨 Starting frontend dashboard...")
        frontend_dir = os.path.join(self.base_dir, 'frontend')
        
        try:
            # Set environment variable to avoid browser auto-opening
            env = os.environ.copy()
            env['BROWSER'] = 'none'
            
            process = subprocess.Popen(
                ['npm', 'start'],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            self.processes.append(('Frontend', process))
            
            # Wait for frontend to start
            time.sleep(10)  # Give React time to compile
            
            for i in range(30):
                try:
                    response = requests.get('http://localhost:3000', timeout=1)
                    if response.status_code == 200:
                        print("✅ Frontend dashboard started successfully")
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)
            
            print("❌ Frontend dashboard failed to start")
            return False
            
        except Exception as e:
            print(f"❌ Error starting frontend: {e}")
            return False
    
    def start_data_simulator(self):
        """Start the data simulator in a separate thread"""
        def run_simulator():
            time.sleep(5)  # Wait for backend to be ready
            print("📊 Starting data simulator...")
            try:
                subprocess.run([
                    sys.executable, 'simulate_input.py',
                    '--mode', 'csv',
                    '--file', 'microgrid_data.csv',
                    '--delay', '2',
                    '--realtime-timestamps'
                ], cwd=self.base_dir)
            except Exception as e:
                print(f"❌ Error running data simulator: {e}")
        
        simulator_thread = Thread(target=run_simulator, daemon=True)
        simulator_thread.start()
    
    def cleanup(self):
        """Clean up all processes"""
        print("\n🧹 Cleaning up processes...")
        for name, process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"🔪 {name} force killed")
            except Exception as e:
                print(f"❌ Error stopping {name}: {e}")
    
    def run_demo(self):
        """Run the complete demo"""
        print("=" * 60)
        print("🌟 MICROGRID ENERGY MONITORING SYSTEM DEMO")
        print("=" * 60)
        
        try:
            # Check dependencies
            if not self.check_dependencies():
                return False
            
            # Install frontend dependencies
            if not self.install_frontend_deps():
                return False
            
            # Start backend
            if not self.start_backend():
                return False
            
            # Start frontend
            if not self.start_frontend():
                return False
            
            # Start data simulator
            self.start_data_simulator()
            
            print("\n" + "=" * 60)
            print("🎉 DEMO IS RUNNING!")
            print("=" * 60)
            print("📊 Dashboard: http://localhost:3000")
            print("🔧 API Docs: http://localhost:8000/docs")
            print("📈 Backend API: http://localhost:8000")
            print("=" * 60)
            print("\n🔄 Data simulator is feeding real-time data...")
            print("🚨 Watch for alerts when thresholds are breached!")
            print("📱 Dashboard updates automatically every 30 seconds")
            print("\n💡 This system is ready for real ESP32/IoT sensor integration")
            print("\nPress Ctrl+C to stop the demo")
            
            # Keep the demo running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n👋 Demo stopped by user")
                
        except Exception as e:
            print(f"❌ Demo error: {e}")
            return False
        finally:
            self.cleanup()
        
        return True

def main():
    launcher = DemoLauncher()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n\n🛑 Stopping demo...")
        launcher.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    success = launcher.run_demo()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
