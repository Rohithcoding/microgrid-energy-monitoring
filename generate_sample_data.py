import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def generate_microgrid_data():
    """Generate realistic microgrid data with normal, warning, and critical scenarios"""
    
    # Start from current time
    start_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
    
    # Generate 24 hours of data with 10-minute intervals
    timestamps = []
    generation = []
    storage = []
    temperature = []
    soc = []
    voltage = []
    
    for i in range(144):  # 24 hours * 6 (10-min intervals per hour)
        current_time = start_time + timedelta(minutes=i*10)
        timestamps.append(current_time.isoformat())
        
        # Hour of day for solar generation pattern
        hour = current_time.hour + current_time.minute/60
        
        # Solar generation pattern (0 at night, peak at noon)
        if 6 <= hour <= 18:
            # Parabolic curve for solar generation
            solar_factor = -((hour - 12) ** 2) / 36 + 1
            base_generation = max(0, solar_factor * 1000)
            # Add some randomness
            gen = base_generation + np.random.normal(0, 50)
        else:
            gen = np.random.normal(0, 10)  # Minimal generation at night
        
        generation.append(max(0, gen))
        
        # Storage level - decreases when generation is low, increases when high
        if i == 0:
            storage_level = 3.0  # Starting storage
        else:
            # Storage changes based on generation vs consumption
            consumption = 400 + np.random.normal(0, 50)  # Base consumption
            net_energy = (generation[i] - consumption) / 1000  # Convert to kWh
            storage_level = max(0.1, min(5.0, storage[-1] + net_energy * 0.167))  # 10min = 1/6 hour
        
        storage.append(storage_level)
        
        # SOC based on storage level (assuming 5kWh max capacity)
        soc_value = (storage_level / 5.0) * 100
        soc.append(soc_value)
        
        # Temperature - higher during day, with some critical periods
        base_temp = 25 + 15 * np.sin((hour - 6) * np.pi / 12)  # Daily temperature cycle
        
        # Add critical temperature periods (overheating scenarios)
        if 12 <= hour <= 15:  # Hot afternoon
            temp_spike = np.random.normal(20, 10)
            temp = base_temp + max(0, temp_spike)
        else:
            temp = base_temp + np.random.normal(0, 5)
        
        temperature.append(max(0, temp))
        
        # Voltage - normally around 230V, drops during high load or low SOC
        base_voltage = 240
        voltage_drop = 0
        
        # Voltage drops when SOC is low
        if soc_value < 30:
            voltage_drop += (30 - soc_value) * 2
        
        # Voltage drops during high consumption periods
        if 18 <= hour <= 22:  # Evening peak
            voltage_drop += np.random.normal(15, 5)
        
        # Add some random variation
        voltage_drop += np.random.normal(0, 3)
        
        final_voltage = base_voltage - voltage_drop
        voltage.append(max(160, final_voltage))  # Minimum 160V
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'generation': [round(g, 1) for g in generation],
        'storage': [round(s, 2) for s in storage],
        'temperature': [round(t, 1) for t in temperature],
        'soc': [round(s, 1) for s in soc],
        'voltage': [round(v, 1) for v in voltage]
    })
    
    return df

def save_data_formats(df):
    """Save data in multiple formats"""
    # CSV format
    df.to_csv('/Users/rohithkumard/Desktop/energy monitoring/microgrid_data.csv', index=False)
    
    # JSON format
    df.to_json('/Users/rohithkumard/Desktop/energy monitoring/microgrid_data.json', 
               orient='records', date_format='iso', indent=2)
    
    print(f"Generated {len(df)} data points")
    print(f"Time range: {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
    print("\nData summary:")
    print(df.describe())
    
    # Check for alert conditions
    critical_temp = df[df['temperature'] > 80]
    low_soc = df[df['soc'] < 30]
    low_voltage = df[df['voltage'] < 200]
    
    print(f"\nAlert conditions in sample data:")
    print(f"High temperature (>80°C): {len(critical_temp)} occurrences")
    print(f"Low SOC (<30%): {len(low_soc)} occurrences")
    print(f"Low voltage (<200V): {len(low_voltage)} occurrences")

if __name__ == "__main__":
    df = generate_microgrid_data()
    save_data_formats(df)
