#!/usr/bin/env python3
"""
Comprehensive Demo of All Microgrid AI Features
This script demonstrates fault detection, grid switching, load management, and predictions
"""

import requests
import json
import time
from datetime import datetime

class MicrogridFeatureDemo:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        
    def print_header(self, title):
        print("\n" + "=" * 80)
        print(f"🤖 {title}")
        print("=" * 80)
        
    def print_section(self, title):
        print(f"\n🔍 {title}")
        print("-" * 60)
        
    def pretty_print_json(self, data, indent=2):
        print(json.dumps(data, indent=indent, default=str))
        
    def demo_fault_detection(self):
        self.print_section("AI FAULT DETECTION SYSTEM")
        
        try:
            response = requests.get(f"{self.base_url}/api/ai/fault-detection")
            data = response.json()
            
            print(f"🏥 System Health: {data['system_health'].upper()}")
            print(f"📊 Data Points Analyzed: {data['data_points_analyzed']}")
            print(f"⏰ Analysis Time: {data['analysis_timestamp']}")
            
            if data['faults']:
                print(f"\n🚨 DETECTED FAULTS ({len(data['faults'])}):")
                for i, fault in enumerate(data['faults'], 1):
                    severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}
                    print(f"\n  {i}. {severity_emoji.get(fault['severity'], '⚪')} {fault['type'].upper()}")
                    print(f"     Severity: {fault['severity'].upper()}")
                    print(f"     Message: {fault['message']}")
                    print(f"     Recommendation: {fault['recommendation']}")
            else:
                print("\n✅ NO FAULTS DETECTED - System operating normally")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def demo_grid_switching(self):
        self.print_section("INTELLIGENT GRID SWITCHING ANALYSIS")
        
        try:
            response = requests.get(f"{self.base_url}/api/ai/grid-switching")
            data = response.json()
            
            status_emoji = "🔴" if data['switch_to_grid'] else "🟢"
            action = "SWITCH TO GRID IMMEDIATELY" if data['switch_to_grid'] else "CONTINUE MICROGRID OPERATION"
            
            print(f"{status_emoji} DECISION: {action}")
            print(f"💡 Recommendation: {data['recommendation']}")
            
            print(f"\n📊 CURRENT STATUS:")
            print(f"   🔋 Battery SOC: {data['current_soc']}%")
            print(f"   ⚡ Generation: {data['current_generation']}W")
            print(f"   📉 6h Energy Deficit: {data['predicted_deficit_6h']:.1f}W")
            
            if data['reasons']:
                print(f"\n🎯 REASONS FOR DECISION:")
                for i, reason in enumerate(data['reasons'], 1):
                    print(f"   {i}. {reason}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def demo_solar_predictions(self):
        self.print_section("SOLAR GENERATION PREDICTIONS")
        
        try:
            response = requests.get(f"{self.base_url}/api/ai/solar-predictions?hours=6")
            data = response.json()
            
            print(f"🔮 Method: {data['method'].replace('_', ' ').title()}")
            print(f"📈 Average Confidence: {data['average_confidence']*100:.1f}%")
            
            print(f"\n☀️ 6-HOUR SOLAR FORECAST:")
            total_predicted = 0
            for pred in data['predictions']:
                time_str = datetime.fromisoformat(pred['timestamp'].replace('Z', '')).strftime('%H:%M')
                confidence = pred['confidence'] * 100
                generation = pred['predicted_generation']
                total_predicted += generation
                
                sun_emoji = "☀️" if generation > 0 else "🌙"
                print(f"   {sun_emoji} {time_str}: {generation:6.1f}W ({confidence:4.1f}% confidence)")
            
            print(f"\n📊 Total Predicted Generation (6h): {total_predicted:.1f}W")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def demo_load_predictions(self):
        self.print_section("LOAD DEMAND PREDICTIONS")
        
        try:
            response = requests.get(f"{self.base_url}/api/ai/load-predictions?hours=12")
            data = response.json()
            
            print(f"🔮 Method: {data['method'].replace('_', ' ').title()}")
            print(f"⚡ Peak Hours: {', '.join(data['peak_hours'])}")
            
            print(f"\n📊 12-HOUR LOAD FORECAST:")
            total_predicted = 0
            for pred in data['predictions']:
                time_str = datetime.fromisoformat(pred['timestamp'].replace('Z', '')).strftime('%H:%M')
                load = pred['predicted_load']
                load_type = pred['load_type'].replace('_', ' ').title()
                total_predicted += load
                
                # Emoji based on load type
                load_emoji = {
                    'Evening Peak': '🔥',
                    'Morning Peak': '⚡',
                    'Daytime': '💡',
                    'Base Load': '🔋'
                }.get(load_type, '📊')
                
                print(f"   {load_emoji} {time_str}: {load:6.1f}W ({load_type})")
            
            print(f"\n📊 Total Predicted Load (12h): {total_predicted:.1f}W")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def demo_load_management(self):
        self.print_section("SMART LOAD MANAGEMENT OPTIMIZATION")
        
        try:
            response = requests.get(f"{self.base_url}/api/ai/load-management")
            data = response.json()
            
            current = data['current_status']
            print(f"📊 CURRENT STATUS:")
            print(f"   ⚡ Generation: {current['generation']}W")
            print(f"   🔋 SOC: {current['soc']}%")
            print(f"   🕐 Hour: {current['hour']}:00")
            
            strategies = data['optimization_strategies']
            if strategies:
                print(f"\n🎯 OPTIMIZATION STRATEGIES ({len(strategies)}):")
                
                for i, strategy in enumerate(strategies, 1):
                    priority_emoji = {
                        'critical': '🔴',
                        'high': '🟠', 
                        'medium': '🟡',
                        'low': '🟢'
                    }.get(strategy['priority'], '⚪')
                    
                    action_emoji = {
                        'load_shedding': '✂️',
                        'load_reduction': '📉',
                        'load_shifting': '🔄',
                        'battery_charging': '🔋',
                        'grid_export': '📤'
                    }.get(strategy['action'], '⚙️')
                    
                    print(f"\n  {i}. {action_emoji} {strategy['action'].replace('_', ' ').upper()}")
                    print(f"     Priority: {priority_emoji} {strategy['priority'].upper()}")
                    print(f"     Message: {strategy['message']}")
                    
                    if 'loads_to_shed' in strategy:
                        print(f"     Loads to shed: {', '.join(strategy['loads_to_shed'])}")
                        print(f"     Estimated savings: {strategy['estimated_savings']}")
                    
                    if 'recommended_loads' in strategy:
                        print(f"     Recommended loads: {', '.join(strategy['recommended_loads'])}")
                        if 'reason' in strategy:
                            print(f"     Reason: {strategy['reason']}")
            else:
                print("\n✅ NO OPTIMIZATION NEEDED - Load management is optimal")
            
            next_review = datetime.fromisoformat(data['next_review'].replace('Z', ''))
            print(f"\n⏰ Next Review: {next_review.strftime('%H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def demo_system_status(self):
        self.print_section("REAL-TIME SYSTEM STATUS")
        
        try:
            # Get current sensor data
            response = requests.get(f"{self.base_url}/api/sensordata/latest")
            sensor_data = response.json()
            
            # Get system status
            response = requests.get(f"{self.base_url}/api/system/status")
            system_status = response.json()
            
            # Get active alerts
            response = requests.get(f"{self.base_url}/api/alerts?active_only=true")
            alerts = response.json()
            
            print(f"🏥 System Health: {system_status['system_health'].upper()}")
            print(f"🚨 Active Alerts: {system_status['active_alerts']}")
            print(f"⏰ Last Updated: {system_status['last_updated']}")
            
            print(f"\n📊 CURRENT READINGS:")
            print(f"   ☀️ Solar Generation: {sensor_data['generation']}W")
            print(f"   🔋 Energy Storage: {sensor_data['storage']}kWh ({sensor_data['soc']}% SOC)")
            print(f"   🌡️ Temperature: {sensor_data['temperature']}°C")
            print(f"   ⚡ Voltage: {sensor_data['voltage']}V")
            
            if alerts:
                print(f"\n🚨 ACTIVE ALERTS ({len(alerts)}):")
                for alert in alerts[:5]:  # Show first 5 alerts
                    severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}
                    alert_time = datetime.fromisoformat(alert['timestamp'].replace('Z', '')).strftime('%H:%M')
                    print(f"   {severity_emoji.get(alert['severity'], '⚪')} [{alert_time}] {alert['message']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def run_complete_demo(self):
        self.print_header("MICROGRID AI INTELLIGENCE SYSTEM - COMPLETE FEATURE DEMO")
        
        print("🌟 This demo showcases advanced AI capabilities for microgrid management:")
        print("   • Real-time fault detection and system health monitoring")
        print("   • Intelligent grid switching decisions based on multiple factors")
        print("   • Solar generation predictions using time-series analysis")
        print("   • Load demand forecasting with pattern recognition")
        print("   • Smart load management and optimization strategies")
        print("   • Comprehensive system status and alerting")
        
        # Run all demos
        self.demo_system_status()
        self.demo_fault_detection()
        self.demo_grid_switching()
        self.demo_solar_predictions()
        self.demo_load_predictions()
        self.demo_load_management()
        
        self.print_header("DEMO COMPLETE - READY FOR PRODUCTION DEPLOYMENT")
        
        print("🎯 KEY CAPABILITIES DEMONSTRATED:")
        print("   ✅ AI-powered fault detection with predictive maintenance")
        print("   ✅ Intelligent grid switching to prevent system failures")
        print("   ✅ Solar generation forecasting for optimal energy planning")
        print("   ✅ Load demand predictions for efficient resource allocation")
        print("   ✅ Smart load management with automatic optimization")
        print("   ✅ Real-time monitoring with comprehensive alerting")
        
        print("\n🚀 PRODUCTION READY FEATURES:")
        print("   • REST API endpoints for all AI functions")
        print("   • Real-time dashboard with live data visualization")
        print("   • Configurable thresholds and alert parameters")
        print("   • Historical data analysis and trend detection")
        print("   • IoT sensor integration (ESP32, Arduino, etc.)")
        print("   • Scalable architecture for enterprise deployment")
        
        print(f"\n📊 Dashboard: http://localhost:3000")
        print(f"🔧 API Documentation: http://localhost:8000/docs")
        print(f"⚡ Backend API: http://localhost:8000")

def main():
    demo = MicrogridFeatureDemo()
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend not accessible. Please start the backend server first.")
            return
    except:
        print("❌ Backend not running. Please start with: cd backend && python main.py")
        return
    
    demo.run_complete_demo()

if __name__ == "__main__":
    main()
