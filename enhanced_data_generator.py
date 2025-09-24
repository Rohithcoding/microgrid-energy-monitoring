import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import random
import argparse

class EnhancedMicrogridDataGenerator:
    """Enhanced data generator with edge scenarios and augmented columns"""
    
    def __init__(self):
        self.alert_thresholds = {
            'temperature_warning': 80,
            'temperature_critical': 100,
            'soc_warning': 30,
            'soc_critical': 15,
            'voltage_warning': 200,
            'voltage_critical': 180
        }
    
    def generate_enhanced_data(self, hours=24, interval_minutes=10, inject_anomalies=True):
        """Generate enhanced microgrid data with edge scenarios"""
        
        start_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
        data_points = int(hours * 60 / interval_minutes)
        
        data = []
        
        # Initialize storage state
        current_storage = 3.0
        
        for i in range(data_points):
            current_time = start_time + timedelta(minutes=i * interval_minutes)
            hour = current_time.hour + current_time.minute / 60
            
            # Solar generation with realistic sunrise-sunset pattern
            solar_generation = self._generate_solar_pattern(hour, inject_anomalies, i)
            
            # Battery and storage management
            consumption_load = self._generate_consumption_pattern(hour, inject_anomalies)
            current_storage, soc = self._update_storage(current_storage, solar_generation, consumption_load, interval_minutes)
            
            # Temperature with edge scenarios
            battery_temp, solar_panel_temp = self._generate_temperature_patterns(hour, solar_generation, inject_anomalies, i)
            
            # Voltage with realistic variations and dips
            voltage = self._generate_voltage_pattern(soc, consumption_load, inject_anomalies, i)
            
            # AI predictions (simulated)
            predicted_generation = self._predict_next_hour_generation(hour + 1)
            predicted_load = self._predict_next_hour_load(hour + 1)
            
            # Alert status determination
            alert_status = self._determine_alert_status(battery_temp, solar_panel_temp, soc, voltage)
            
            data_point = {
                'timestamp': current_time.isoformat(),
                'solar_generation': round(solar_generation, 1),
                'storage_level': round(current_storage, 2),
                'battery_temperature': round(battery_temp, 1),
                'solar_panel_temp': round(solar_panel_temp, 1),
                'soc': round(soc, 1),
                'voltage': round(voltage, 1),
                'consumption_load': round(consumption_load, 1),
                'alert_status': alert_status,
                'predicted_generation': round(predicted_generation, 1),
                'predicted_load': round(predicted_load, 1),
                'alert_type': self._get_alert_type(battery_temp, solar_panel_temp, soc, voltage)
            }
            
            data.append(data_point)
        
        return pd.DataFrame(data)
    
    def _generate_solar_pattern(self, hour, inject_anomalies, index):
        """Generate realistic solar generation with smooth sunrise-sunset pattern"""
        if 6 <= hour <= 18:
            # Smooth parabolic curve for solar generation
            solar_factor = -((hour - 12) ** 2) / 36 + 1
            base_generation = max(0, solar_factor * 1000)
            
            # Add weather variations
            weather_factor = np.random.uniform(0.7, 1.0)
            generation = base_generation * weather_factor
            
            # Inject cloud cover events
            if inject_anomalies and random.random() < 0.1:
                generation *= random.uniform(0.2, 0.6)  # Cloud cover
                
        else:
            generation = np.random.normal(0, 5)  # Night time minimal generation
        
        return max(0, generation)
    
    def _generate_consumption_pattern(self, hour, inject_anomalies):
        """Generate realistic consumption with day/night cycles"""
        # Base consumption patterns
        if 22 <= hour or hour < 6:  # Night
            base_load = 200
        elif 6 <= hour < 10:  # Morning peak
            base_load = 450
        elif 10 <= hour < 18:  # Day
            base_load = 300
        else:  # Evening peak
            base_load = 600
        
        # Add normal variation
        load = base_load + np.random.normal(0, 50)
        
        # Inject consumption spikes
        if inject_anomalies and random.random() < 0.05:
            load += random.uniform(200, 500)  # High consumption event
        
        return max(100, load)
    
    def _update_storage(self, current_storage, generation, consumption, interval_minutes):
        """Update storage level based on generation and consumption"""
        net_energy = (generation - consumption) / 1000  # Convert to kWh
        time_factor = interval_minutes / 60  # Convert to hours
        
        new_storage = current_storage + (net_energy * time_factor)
        new_storage = max(0.1, min(5.0, new_storage))  # Clamp between 0.1 and 5.0 kWh
        
        soc = (new_storage / 5.0) * 100
        return new_storage, soc
    
    def _generate_temperature_patterns(self, hour, solar_generation, inject_anomalies, index):
        """Generate battery and solar panel temperatures with edge scenarios"""
        # Base temperature patterns
        ambient_temp = 25 + 10 * np.sin((hour - 6) * np.pi / 12)
        
        # Battery temperature (affected by charging/discharging)
        battery_temp = ambient_temp + (solar_generation / 100) + np.random.normal(0, 3)
        
        # Solar panel temperature (higher due to sun exposure)
        if solar_generation > 100:
            solar_panel_temp = ambient_temp + 15 + (solar_generation / 50) + np.random.normal(0, 5)
        else:
            solar_panel_temp = ambient_temp + np.random.normal(0, 3)
        
        # Inject high temperature events (edge scenarios)
        if inject_anomalies:
            # Sporadic overheating events
            if random.random() < 0.03:  # 3% chance
                battery_temp += random.uniform(30, 50)
            
            if random.random() < 0.05:  # 5% chance for solar panels
                solar_panel_temp += random.uniform(20, 40)
        
        return max(15, battery_temp), max(15, solar_panel_temp)
    
    def _generate_voltage_pattern(self, soc, consumption_load, inject_anomalies, index):
        """Generate voltage with realistic variations and dips"""
        base_voltage = 240
        
        # Voltage drops with low SOC
        if soc < 30:
            voltage_drop = (30 - soc) * 2
        else:
            voltage_drop = 0
        
        # Voltage drops during high consumption
        if consumption_load > 500:
            voltage_drop += (consumption_load - 500) / 50
        
        # Normal variation
        voltage = base_voltage - voltage_drop + np.random.normal(0, 3)
        
        # Inject voltage dip events
        if inject_anomalies and random.random() < 0.02:  # 2% chance
            voltage -= random.uniform(30, 60)  # Voltage dip event
        
        return max(160, voltage)
    
    def _predict_next_hour_generation(self, next_hour):
        """Simulate AI prediction for next hour solar generation"""
        if 6 <= next_hour <= 18:
            solar_factor = -((next_hour - 12) ** 2) / 36 + 1
            predicted = max(0, solar_factor * 1000 * random.uniform(0.8, 1.0))
        else:
            predicted = 0
        return predicted
    
    def _predict_next_hour_load(self, next_hour):
        """Simulate AI prediction for next hour load"""
        if 22 <= next_hour or next_hour < 6:
            predicted = 200 + np.random.normal(0, 30)
        elif 6 <= next_hour < 10:
            predicted = 450 + np.random.normal(0, 50)
        elif 10 <= next_hour < 18:
            predicted = 300 + np.random.normal(0, 40)
        else:
            predicted = 600 + np.random.normal(0, 60)
        
        return max(100, predicted)
    
    def _determine_alert_status(self, battery_temp, solar_panel_temp, soc, voltage):
        """Determine overall alert status based on thresholds"""
        if (battery_temp > self.alert_thresholds['temperature_critical'] or 
            solar_panel_temp > self.alert_thresholds['temperature_critical'] or
            soc < self.alert_thresholds['soc_critical'] or
            voltage < self.alert_thresholds['voltage_critical']):
            return 'critical'
        elif (battery_temp > self.alert_thresholds['temperature_warning'] or
              solar_panel_temp > self.alert_thresholds['temperature_warning'] or
              soc < self.alert_thresholds['soc_warning'] or
              voltage < self.alert_thresholds['voltage_warning']):
            return 'warning'
        else:
            return 'healthy'
    
    def _get_alert_type(self, battery_temp, solar_panel_temp, soc, voltage):
        """Get specific alert type for filtering"""
        alerts = []
        
        if battery_temp > self.alert_thresholds['temperature_warning']:
            alerts.append('battery_temp')
        if solar_panel_temp > self.alert_thresholds['temperature_warning']:
            alerts.append('solar_temp')
        if soc < self.alert_thresholds['soc_warning']:
            alerts.append('low_soc')
        if voltage < self.alert_thresholds['voltage_warning']:
            alerts.append('voltage_drop')
        
        return ','.join(alerts) if alerts else 'none'
    
    def save_enhanced_data(self, df, base_filename='enhanced_microgrid_data'):
        """Save data in multiple formats with summary"""
        # Save CSV
        csv_file = f'{base_filename}.csv'
        df.to_csv(csv_file, index=False)
        
        # Save JSON
        json_file = f'{base_filename}.json'
        df.to_json(json_file, orient='records', date_format='iso', indent=2)
        
        # Generate summary report
        summary = self._generate_summary_report(df)
        
        # Save summary
        summary_file = f'{base_filename}_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"✅ Enhanced data saved:")
        print(f"   📊 CSV: {csv_file}")
        print(f"   📋 JSON: {json_file}")
        print(f"   📈 Summary: {summary_file}")
        
        return summary
    
    def _generate_summary_report(self, df):
        """Generate comprehensive summary report"""
        summary = {
            'dataset_info': {
                'total_records': len(df),
                'time_range': {
                    'start': df['timestamp'].iloc[0],
                    'end': df['timestamp'].iloc[-1]
                },
                'data_quality': {
                    'missing_values': df.isnull().sum().to_dict(),
                    'data_types': df.dtypes.astype(str).to_dict()
                }
            },
            'alert_analysis': {
                'alert_distribution': df['alert_status'].value_counts().to_dict(),
                'alert_types': df['alert_type'].value_counts().to_dict(),
                'critical_events': len(df[df['alert_status'] == 'critical']),
                'warning_events': len(df[df['alert_status'] == 'warning'])
            },
            'system_metrics': {
                'solar_generation': {
                    'max': float(df['solar_generation'].max()),
                    'min': float(df['solar_generation'].min()),
                    'avg': float(df['solar_generation'].mean()),
                    'zero_generation_hours': len(df[df['solar_generation'] == 0])
                },
                'battery_performance': {
                    'max_soc': float(df['soc'].max()),
                    'min_soc': float(df['soc'].min()),
                    'avg_soc': float(df['soc'].mean()),
                    'low_soc_events': len(df[df['soc'] < 30])
                },
                'temperature_analysis': {
                    'max_battery_temp': float(df['battery_temperature'].max()),
                    'max_solar_temp': float(df['solar_panel_temp'].max()),
                    'overheating_events': len(df[df['battery_temperature'] > 80])
                },
                'voltage_stability': {
                    'max_voltage': float(df['voltage'].max()),
                    'min_voltage': float(df['voltage'].min()),
                    'voltage_dip_events': len(df[df['voltage'] < 200])
                }
            },
            'edge_scenarios': {
                'high_temp_events': len(df[df['battery_temperature'] > 90]),
                'critical_soc_events': len(df[df['soc'] < 15]),
                'severe_voltage_drops': len(df[df['voltage'] < 180]),
                'consumption_spikes': len(df[df['consumption_load'] > 800])
            },
            'ai_predictions': {
                'generation_forecast_avg': float(df['predicted_generation'].mean()),
                'load_forecast_avg': float(df['predicted_load'].mean()),
                'prediction_variance': {
                    'generation': float(df['predicted_generation'].var()),
                    'load': float(df['predicted_load'].var())
                }
            }
        }
        
        return summary

def main():
    parser = argparse.ArgumentParser(description='Enhanced Microgrid Data Generator')
    parser.add_argument('--hours', type=int, default=48, help='Hours of data to generate')
    parser.add_argument('--interval', type=int, default=10, help='Interval in minutes')
    parser.add_argument('--no-anomalies', action='store_true', help='Disable anomaly injection')
    parser.add_argument('--output', default='enhanced_microgrid_data', help='Output filename base')
    
    args = parser.parse_args()
    
    generator = EnhancedMicrogridDataGenerator()
    
    print("🚀 Generating Enhanced Microgrid Dataset")
    print(f"   ⏱️  Duration: {args.hours} hours")
    print(f"   📊 Interval: {args.interval} minutes")
    print(f"   🎯 Anomalies: {'Disabled' if args.no_anomalies else 'Enabled'}")
    
    df = generator.generate_enhanced_data(
        hours=args.hours,
        interval_minutes=args.interval,
        inject_anomalies=not args.no_anomalies
    )
    
    summary = generator.save_enhanced_data(df, args.output)
    
    print("\n📈 Dataset Summary:")
    print(f"   📊 Total Records: {summary['dataset_info']['total_records']}")
    print(f"   🚨 Critical Events: {summary['alert_analysis']['critical_events']}")
    print(f"   ⚠️  Warning Events: {summary['alert_analysis']['warning_events']}")
    print(f"   🔥 Overheating Events: {summary['edge_scenarios']['high_temp_events']}")
    print(f"   🔋 Low SOC Events: {summary['system_metrics']['battery_performance']['low_soc_events']}")
    print(f"   ⚡ Voltage Dips: {summary['system_metrics']['voltage_stability']['voltage_dip_events']}")

if __name__ == "__main__":
    main()
