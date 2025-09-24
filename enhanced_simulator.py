#!/usr/bin/env python3
"""
Enhanced Microgrid Data Simulator with Advanced Features
Supports multiple data sources, error injection, retry logic, and real-time streaming
"""

import requests
import pandas as pd
import numpy as np
import time
import json
import argparse
import click
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import random
import sys
from concurrent.futures import ThreadPoolExecutor
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('simulator.log')
    ]
)
logger = logging.getLogger(__name__)

class EnhancedMicrogridSimulator:
    """Enhanced simulator with comprehensive features"""
    
    def __init__(self, backend_url="http://localhost:8000", api_key=None):
        self.backend_url = backend_url
        self.api_endpoint = f"{backend_url}/api/sensordata"
        self.api_key = api_key
        self.session = requests.Session()
        self.stats = {
            'sent': 0,
            'failed': 0,
            'retries': 0,
            'start_time': None,
            'errors': []
        }
        self.stop_event = threading.Event()
        
        # Setup session headers
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
    
    def test_connection(self, timeout=5):
        """Test backend connectivity with detailed diagnostics"""
        try:
            response = self.session.get(f"{self.backend_url}/api/health", timeout=timeout)
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"✅ Backend healthy: {health_data}")
                return True
            else:
                logger.error(f"❌ Backend unhealthy: HTTP {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            logger.error("❌ Connection refused - backend not running")
            return False
        except requests.exceptions.Timeout:
            logger.error(f"❌ Connection timeout after {timeout}s")
            return False
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            return False
    
    def send_data_point(self, data_point: Dict, max_retries=3) -> tuple[bool, str]:
        """Send data point with retry logic and error handling"""
        for attempt in range(max_retries + 1):
            try:
                # Add timestamp if not present
                if 'timestamp' not in data_point:
                    data_point['timestamp'] = datetime.now().isoformat()
                
                response = self.session.post(
                    self.api_endpoint,
                    json=data_point,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.stats['sent'] += 1
                    return True, response.json()
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    if attempt < max_retries:
                        self.stats['retries'] += 1
                        logger.warning(f"Retry {attempt + 1}/{max_retries}: {error_msg}")
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        self.stats['failed'] += 1
                        self.stats['errors'].append(error_msg)
                        return False, error_msg
                        
            except Exception as e:
                error_msg = str(e)
                if attempt < max_retries:
                    self.stats['retries'] += 1
                    logger.warning(f"Retry {attempt + 1}/{max_retries}: {error_msg}")
                    time.sleep(2 ** attempt)
                    continue
                else:
                    self.stats['failed'] += 1
                    self.stats['errors'].append(error_msg)
                    return False, error_msg
        
        return False, "Max retries exceeded"
    
    def load_data_source(self, source_path: str, source_type: str = "auto") -> pd.DataFrame:
        """Load data from various sources with validation"""
        source_path = Path(source_path)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Data source not found: {source_path}")
        
        # Auto-detect source type
        if source_type == "auto":
            if source_path.suffix.lower() == '.csv':
                source_type = "csv"
            elif source_path.suffix.lower() == '.json':
                source_type = "json"
            else:
                raise ValueError(f"Cannot auto-detect source type for: {source_path}")
        
        # Load data
        try:
            if source_type == "csv":
                df = pd.read_csv(source_path)
            elif source_type == "json":
                df = pd.read_json(source_path)
            else:
                raise ValueError(f"Unsupported source type: {source_type}")
            
            logger.info(f"📊 Loaded {len(df)} records from {source_path}")
            return df
            
        except Exception as e:
            raise ValueError(f"Error loading data source: {e}")
    
    def inject_errors(self, data_point: Dict, error_rate: float = 0.05) -> Dict:
        """Inject random errors for resilience testing"""
        if random.random() < error_rate:
            error_type = random.choice([
                'missing_field',
                'invalid_value',
                'out_of_range',
                'wrong_type'
            ])
            
            if error_type == 'missing_field':
                # Remove a random field
                fields = list(data_point.keys())
                if fields:
                    field_to_remove = random.choice(fields)
                    data_point.pop(field_to_remove, None)
                    logger.debug(f"🔧 Injected error: removed field '{field_to_remove}'")
            
            elif error_type == 'invalid_value':
                # Set a field to invalid value
                field = random.choice(['solar_generation', 'soc', 'voltage'])
                if field in data_point:
                    data_point[field] = -999
                    logger.debug(f"🔧 Injected error: invalid value for '{field}'")
            
            elif error_type == 'out_of_range':
                # Set a field to out-of-range value
                field = random.choice(['soc', 'voltage', 'battery_temperature'])
                if field == 'soc':
                    data_point['soc'] = 150  # > 100%
                elif field == 'voltage':
                    data_point['voltage'] = 500  # > 300V
                elif field == 'battery_temperature':
                    data_point['battery_temperature'] = 200  # > 150°C
                logger.debug(f"🔧 Injected error: out-of-range value for '{field}'")
            
            elif error_type == 'wrong_type':
                # Set a field to wrong type
                field = random.choice(['solar_generation', 'soc'])
                if field in data_point:
                    data_point[field] = "invalid_string"
                    logger.debug(f"🔧 Injected error: wrong type for '{field}'")
        
        return data_point
    
    def add_randomization(self, data_point: Dict, variation: float = 0.05) -> Dict:
        """Add slight randomization to avoid monotony"""
        numeric_fields = [
            'solar_generation', 'storage_level', 'battery_temperature',
            'solar_panel_temp', 'soc', 'voltage', 'consumption_load'
        ]
        
        for field in numeric_fields:
            if field in data_point and isinstance(data_point[field], (int, float)):
                original_value = data_point[field]
                variation_amount = original_value * variation * (random.random() - 0.5) * 2
                data_point[field] = max(0, original_value + variation_amount)
        
        return data_point
    
    def simulate_from_source(self, source_path: str, **kwargs):
        """Simulate data from file source"""
        # Extract parameters
        delay = kwargs.get('delay', 1.0)
        real_time = kwargs.get('real_time', False)
        error_injection = kwargs.get('error_injection', False)
        error_rate = kwargs.get('error_rate', 0.05)
        randomization = kwargs.get('randomization', True)
        variation = kwargs.get('variation', 0.05)
        loop = kwargs.get('loop', False)
        max_records = kwargs.get('max_records', None)
        
        # Load data
        df = self.load_data_source(source_path)
        
        if max_records:
            df = df.head(max_records)
        
        self.stats['start_time'] = datetime.now()
        records_sent = 0
        
        logger.info(f"🚀 Starting simulation from {source_path}")
        logger.info(f"   📊 Records: {len(df)}")
        logger.info(f"   ⏱️  Delay: {delay}s")
        logger.info(f"   🔧 Error injection: {error_injection} ({error_rate*100:.1f}%)")
        logger.info(f"   🎲 Randomization: {randomization} ({variation*100:.1f}%)")
        logger.info(f"   🔄 Loop: {loop}")
        
        try:
            while not self.stop_event.is_set():
                for index, row in df.iterrows():
                    if self.stop_event.is_set():
                        break
                    
                    # Prepare data point
                    data_point = row.to_dict()
                    
                    # Update timestamp if real-time mode
                    if real_time:
                        data_point['timestamp'] = datetime.now().isoformat()
                    
                    # Add randomization
                    if randomization:
                        data_point = self.add_randomization(data_point, variation)
                    
                    # Inject errors for testing
                    if error_injection:
                        data_point = self.inject_errors(data_point, error_rate)
                    
                    # Send data point
                    success, result = self.send_data_point(data_point)
                    records_sent += 1
                    
                    if success:
                        logger.info(f"✅ [{records_sent}/{len(df)}] Sent: Gen={data_point.get('generation', 0):.1f}W, SOC={data_point.get('soc', 0):.1f}%, Temp={data_point.get('temperature', 0):.1f}°C")
                        
                        # Check for alert conditions
                        self._log_alert_conditions(data_point)
                    else:
                        logger.error(f"❌ [{records_sent}/{len(df)}] Failed: {result}")
                    
                    # Progress reporting
                    if records_sent % 10 == 0:
                        self._print_progress()
                    
                    time.sleep(delay)
                
                if not loop:
                    break
                else:
                    logger.info("🔄 Looping dataset...")
        
        except KeyboardInterrupt:
            logger.info("⏹️  Simulation stopped by user")
        finally:
            self._print_final_stats()
    
    def simulate_real_time(self, **kwargs):
        """Generate and send real-time data"""
        duration = kwargs.get('duration', 60)  # minutes
        interval = kwargs.get('interval', 10)  # seconds
        error_injection = kwargs.get('error_injection', False)
        error_rate = kwargs.get('error_rate', 0.05)
        
        logger.info(f"🔄 Starting real-time simulation")
        logger.info(f"   ⏱️  Duration: {duration} minutes")
        logger.info(f"   📡 Interval: {interval} seconds")
        
        self.stats['start_time'] = datetime.now()
        end_time = self.stats['start_time'] + timedelta(minutes=duration)
        count = 0
        
        try:
            while datetime.now() < end_time and not self.stop_event.is_set():
                # Generate realistic data point
                data_point = self._generate_realistic_data()
                
                # Inject errors if enabled
                if error_injection:
                    data_point = self.inject_errors(data_point, error_rate)
                
                success, result = self.send_data_point(data_point)
                count += 1
                
                if success:
                    logger.info(f"✅ [{count}] Real-time: Gen={data_point['generation']:.1f}W, SOC={data_point['soc']:.1f}%, Temp={data_point['temperature']:.1f}°C")
                    self._log_alert_conditions(data_point)
                else:
                    logger.error(f"❌ [{count}] Failed: {result}")
                
                if count % 10 == 0:
                    self._print_progress()
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            logger.info("⏹️  Real-time simulation stopped by user")
        finally:
            self._print_final_stats()
    
    def _generate_realistic_data(self) -> Dict:
        """Generate realistic microgrid data point"""
        current_hour = datetime.now().hour
        
        # Solar generation
        if 6 <= current_hour <= 18:
            solar_factor = -((current_hour - 12) ** 2) / 36 + 1
            generation = max(0, solar_factor * 1000 + np.random.normal(0, 100))
        else:
            generation = np.random.normal(10, 5)
        
        # Storage and SOC
        storage = max(0.1, min(5.0, 2.5 + np.random.normal(0, 1)))
        soc = (storage / 5.0) * 100
        
        # Temperatures
        battery_temp = 35 + np.random.normal(0, 10)
        solar_temp = battery_temp + 10 + (generation / 100)
        
        # Voltage
        voltage = 240 - (30 - min(30, soc)) * 2 + np.random.normal(0, 5)
        voltage = max(160, voltage)
        
        # Consumption
        consumption = {
            range(0, 6): 200,
            range(6, 10): 450,
            range(10, 18): 300,
            range(18, 22): 600,
            range(22, 24): 200
        }
        base_consumption = next(v for k, v in consumption.items() if current_hour in k)
        load = base_consumption + np.random.normal(0, 50)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'generation': round(max(0, generation), 1),  # Map to expected field name
            'storage': round(storage, 2),  # Map to expected field name
            'temperature': round(max(0, battery_temp), 1),  # Map to expected field name
            'soc': round(soc, 1),
            'voltage': round(voltage, 1)
        }
    
    def _log_alert_conditions(self, data_point: Dict):
        """Log potential alert conditions"""
        alerts = []
        
        if data_point.get('temperature', 0) > 80:
            alerts.append(f"🌡️  High temp: {data_point['temperature']}°C")
        if data_point.get('soc', 100) < 30:
            alerts.append(f"🔋 Low SOC: {data_point['soc']}%")
        if data_point.get('voltage', 240) < 200:
            alerts.append(f"⚡ Voltage drop: {data_point['voltage']}V")
        
        for alert in alerts:
            logger.warning(alert)
    
    def _print_progress(self):
        """Print simulation progress"""
        elapsed = datetime.now() - self.stats['start_time']
        rate = self.stats['sent'] / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
        
        logger.info(f"📈 Progress: {self.stats['sent']} sent, {self.stats['failed']} failed, {rate:.1f} msg/s")
    
    def _print_final_stats(self):
        """Print final simulation statistics"""
        if self.stats['start_time']:
            elapsed = datetime.now() - self.stats['start_time']
            rate = self.stats['sent'] / elapsed.total_seconds() if elapsed.total_seconds() > 0 else 0
            
            logger.info("📊 SIMULATION COMPLETE")
            logger.info(f"   ⏱️  Duration: {elapsed}")
            logger.info(f"   ✅ Sent: {self.stats['sent']}")
            logger.info(f"   ❌ Failed: {self.stats['failed']}")
            logger.info(f"   🔄 Retries: {self.stats['retries']}")
            logger.info(f"   📈 Rate: {rate:.1f} messages/second")
            
            if self.stats['errors']:
                logger.error(f"   🚨 Recent errors: {self.stats['errors'][-5:]}")

@click.command()
@click.option('--mode', type=click.Choice(['file', 'realtime']), default='file', help='Simulation mode')
@click.option('--source', default='enhanced_microgrid_data.csv', help='Data source file')
@click.option('--source-type', type=click.Choice(['auto', 'csv', 'json']), default='auto', help='Source file type')
@click.option('--delay', type=float, default=1.0, help='Delay between messages (seconds)')
@click.option('--duration', type=int, default=60, help='Duration for real-time mode (minutes)')
@click.option('--interval', type=int, default=10, help='Interval for real-time mode (seconds)')
@click.option('--backend', default='http://localhost:8000', help='Backend URL')
@click.option('--api-key', help='API key for authentication')
@click.option('--real-time', is_flag=True, help='Use current timestamps')
@click.option('--error-injection', is_flag=True, help='Enable error injection for testing')
@click.option('--error-rate', type=float, default=0.05, help='Error injection rate (0.0-1.0)')
@click.option('--no-randomization', is_flag=True, help='Disable value randomization')
@click.option('--variation', type=float, default=0.05, help='Randomization variation (0.0-1.0)')
@click.option('--loop', is_flag=True, help='Loop dataset continuously')
@click.option('--max-records', type=int, help='Maximum records to send')
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
def main(**kwargs):
    """Enhanced Microgrid Data Simulator"""
    
    if kwargs['verbose']:
        logging.getLogger().setLevel(logging.DEBUG)
    
    simulator = EnhancedMicrogridSimulator(
        backend_url=kwargs['backend'],
        api_key=kwargs['api_key']
    )
    
    # Test connection
    if not simulator.test_connection():
        logger.error("Cannot connect to backend. Exiting.")
        sys.exit(1)
    
    try:
        if kwargs['mode'] == 'file':
            simulator.simulate_from_source(
                source_path=kwargs['source'],
                delay=kwargs['delay'],
                real_time=kwargs['real_time'],
                error_injection=kwargs['error_injection'],
                error_rate=kwargs['error_rate'],
                randomization=not kwargs['no_randomization'],
                variation=kwargs['variation'],
                loop=kwargs['loop'],
                max_records=kwargs['max_records']
            )
        else:  # realtime
            simulator.simulate_real_time(
                duration=kwargs['duration'],
                interval=kwargs['interval'],
                error_injection=kwargs['error_injection'],
                error_rate=kwargs['error_rate']
            )
    
    except KeyboardInterrupt:
        logger.info("Simulation interrupted by user")
        simulator.stop_event.set()
    except Exception as e:
        logger.error(f"Simulation error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
