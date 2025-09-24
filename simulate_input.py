import requests
import pandas as pd
import time
import json
from datetime import datetime
import argparse

class MicrogridDataSimulator:
    def __init__(self, backend_url="http://localhost:8000"):
        self.backend_url = backend_url
        self.api_endpoint = f"{backend_url}/api/sensordata"
    
    def test_connection(self):
        """Test if backend is accessible"""
        try:
            response = requests.get(f"{self.backend_url}/api/health")
            if response.status_code == 200:
                print("✅ Backend connection successful")
                return True
            else:
                print(f"❌ Backend responded with status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to backend. Make sure it's running on http://localhost:8000")
            return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def send_data_point(self, data_point):
        """Send a single data point to the backend"""
        try:
            # Prepare data for API
            payload = {
                "timestamp": data_point["timestamp"],
                "generation": float(data_point["generation"]),
                "storage": float(data_point["storage"]),
                "temperature": float(data_point["temperature"]),
                "soc": float(data_point["soc"]),
                "voltage": float(data_point["voltage"])
            }
            
            response = requests.post(self.api_endpoint, json=payload)
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            return False, str(e)
    
    def simulate_from_csv(self, csv_file, delay_seconds=1, real_time=False):
        """Simulate data from CSV file"""
        try:
            df = pd.read_csv(csv_file)
            print(f"📊 Loaded {len(df)} data points from {csv_file}")
            
            successful = 0
            failed = 0
            
            for index, row in df.iterrows():
                # Update timestamp to current time if real_time is True
                if real_time:
                    row_data = row.to_dict()
                    row_data["timestamp"] = datetime.now().isoformat()
                else:
                    row_data = row.to_dict()
                
                success, result = self.send_data_point(row_data)
                
                if success:
                    successful += 1
                    print(f"✅ Sent data point {index + 1}/{len(df)} - Gen: {row['generation']}W, SOC: {row['soc']}%, Temp: {row['temperature']}°C")
                else:
                    failed += 1
                    print(f"❌ Failed to send data point {index + 1}: {result}")
                
                # Check if this data point should trigger alerts
                if row['temperature'] > 80:
                    print(f"🚨 High temperature alert expected: {row['temperature']}°C")
                if row['soc'] < 30:
                    print(f"🔋 Low battery alert expected: {row['soc']}%")
                if row['voltage'] < 200:
                    print(f"⚡ Voltage drop alert expected: {row['voltage']}V")
                
                time.sleep(delay_seconds)
            
            print(f"\n📈 Simulation complete!")
            print(f"✅ Successful: {successful}")
            print(f"❌ Failed: {failed}")
            
        except FileNotFoundError:
            print(f"❌ File not found: {csv_file}")
        except Exception as e:
            print(f"❌ Error during simulation: {e}")
    
    def simulate_real_time(self, duration_minutes=60, interval_seconds=10):
        """Generate and send real-time simulated data"""
        import numpy as np
        
        print(f"🔄 Starting real-time simulation for {duration_minutes} minutes")
        print(f"📡 Sending data every {interval_seconds} seconds")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        count = 0
        
        while time.time() < end_time:
            # Generate realistic data point
            current_hour = datetime.now().hour
            
            # Solar generation pattern
            if 6 <= current_hour <= 18:
                generation = max(0, 500 + np.random.normal(0, 100) + 
                               300 * np.sin((current_hour - 6) * np.pi / 12))
            else:
                generation = np.random.normal(10, 5)
            
            # Storage and SOC
            storage = max(0.1, min(5.0, 2.5 + np.random.normal(0, 1)))
            soc = (storage / 5.0) * 100
            
            # Temperature with occasional spikes
            base_temp = 35 + np.random.normal(0, 10)
            if np.random.random() < 0.1:  # 10% chance of temperature spike
                base_temp += np.random.normal(50, 20)
            temperature = max(0, base_temp)
            
            # Voltage with drops during low SOC
            voltage = 240 - (30 - min(30, soc)) * 2 + np.random.normal(0, 5)
            voltage = max(160, voltage)
            
            data_point = {
                "timestamp": datetime.now().isoformat(),
                "generation": round(max(0, generation), 1),
                "storage": round(storage, 2),
                "temperature": round(temperature, 1),
                "soc": round(soc, 1),
                "voltage": round(voltage, 1)
            }
            
            success, result = self.send_data_point(data_point)
            count += 1
            
            if success:
                print(f"✅ [{count}] Real-time data sent - Gen: {data_point['generation']}W, "
                      f"SOC: {data_point['soc']}%, Temp: {data_point['temperature']}°C, "
                      f"Voltage: {data_point['voltage']}V")
            else:
                print(f"❌ [{count}] Failed to send real-time data: {result}")
            
            time.sleep(interval_seconds)
        
        print(f"\n🏁 Real-time simulation completed. Sent {count} data points.")

def main():
    parser = argparse.ArgumentParser(description="Microgrid Data Simulator")
    parser.add_argument("--mode", choices=["csv", "realtime"], default="csv",
                       help="Simulation mode: csv or realtime")
    parser.add_argument("--file", default="microgrid_data.csv",
                       help="CSV file to simulate from (for csv mode)")
    parser.add_argument("--delay", type=float, default=1.0,
                       help="Delay between data points in seconds")
    parser.add_argument("--duration", type=int, default=60,
                       help="Duration for real-time simulation in minutes")
    parser.add_argument("--interval", type=int, default=10,
                       help="Interval for real-time data generation in seconds")
    parser.add_argument("--backend", default="http://localhost:8000",
                       help="Backend URL")
    parser.add_argument("--realtime-timestamps", action="store_true",
                       help="Use current timestamps instead of CSV timestamps")
    
    args = parser.parse_args()
    
    simulator = MicrogridDataSimulator(args.backend)
    
    print("🚀 Microgrid Data Simulator")
    print("=" * 50)
    
    if not simulator.test_connection():
        print("\n💡 To start the backend, run:")
        print("   cd backend && python main.py")
        return
    
    if args.mode == "csv":
        print(f"\n📁 CSV Simulation Mode")
        print(f"File: {args.file}")
        print(f"Delay: {args.delay} seconds between data points")
        print(f"Real-time timestamps: {args.realtime_timestamps}")
        print("-" * 50)
        
        simulator.simulate_from_csv(
            args.file, 
            delay_seconds=args.delay,
            real_time=args.realtime_timestamps
        )
    
    elif args.mode == "realtime":
        print(f"\n⏰ Real-time Simulation Mode")
        print(f"Duration: {args.duration} minutes")
        print(f"Interval: {args.interval} seconds")
        print("-" * 50)
        
        simulator.simulate_real_time(
            duration_minutes=args.duration,
            interval_seconds=args.interval
        )

if __name__ == "__main__":
    main()
