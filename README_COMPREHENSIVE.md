# Comprehensive Hybrid Microgrid Monitoring System

A complete real-time monitoring and analytics system for hybrid microgrids with solar, thermal, and storage components.

## 🚀 Features

### Core Monitoring
- **Real-time sensor data collection** from all system components
- **Comprehensive alert system** with fault detection and notifications
- **Advanced analytics engine** with efficiency calculations and performance metrics
- **Predictive forecasting** for solar generation and battery depletion
- **WebSocket real-time updates** for live dashboard updates

### System Components Monitored

#### 1. Solar System
- Solar irradiance and PV output monitoring
- Thermoelectric generator (TEG) status
- Solar concentrator health and alignment
- PV efficiency tracking

#### 2. Thermal System
- Hot water temperature (450-500°C target)
- Storage tank pressure and energy storage
- Molten salts/oils loop monitoring
- Steam generation and pressure
- Pipe integrity status

#### 3. Conversion and Control
- Inverter efficiency (>15% target)
- Hybrid microgrid controller health
- Grid/islanded mode monitoring
- Scheduling and switching status

#### 4. Storage System
- Battery State of Charge (SOC)
- Battery temperature and health
- Thermal energy storage efficiency
- Water storage tank levels

#### 5. Output and Loads
- Turbine operation and power output
- Condenser status and temperature
- Critical and non-critical load monitoring
- Load scheduling and shedding

### Analytics and Insights
- **Efficiency calculations** with 15% and 30% targets
- **System health scoring** and performance metrics
- **Predictive analytics** for maintenance and optimization
- **Historical trend analysis** and reporting
- **Real-time efficiency monitoring**

### Forecasting Capabilities
- **Solar generation forecasting** (1h, 6h, 24h ahead)
- **Battery depletion estimates** with backup time calculations
- **Outage prediction** with probability and duration
- **Load demand forecasting** for optimization
- **Weather-based solar predictions**

## 🏗️ Architecture

### Backend Components
- **`comprehensive_models.py`** - Complete data models for all monitoring points
- **`sensor_interfaces.py`** - Sensor interface classes and data collection
- **`monitoring_engine.py`** - Real-time monitoring and data processing
- **`alert_system.py`** - Advanced fault detection and alerting
- **`analytics_engine.py`** - Efficiency calculations and performance analytics
- **`forecasting_engine.py`** - Solar forecasting and battery depletion prediction
- **`comprehensive_api.py`** - Complete REST API with WebSocket support

### Frontend Components
- **`ComprehensiveDashboard.js`** - Advanced monitoring dashboard
- **Real-time WebSocket integration** for live updates
- **Multi-tab interface** for different system views
- **Responsive design** for desktop and mobile

## 🚀 Quick Start

### 1. Start the Comprehensive System
```bash
python start_comprehensive_system.py
```

### 2. Access the Dashboard
- **Main Dashboard**: http://localhost:3000
- **Comprehensive Dashboard**: Navigate to "Comprehensive" tab
- **API Documentation**: http://localhost:8000/docs
- **WebSocket Endpoint**: ws://localhost:8000/ws

### 3. Monitor System Components
- **Overview**: System health and key metrics
- **Solar System**: PV output, irradiance, TEG status
- **Thermal System**: Hot water temp, pressure, steam output
- **Storage**: Battery SOC, temperature, backup time
- **Analytics**: Efficiency metrics and performance
- **Forecasts**: Solar predictions and battery depletion

## 📊 Key Monitoring Points

### Critical Alerts
- **Hot water temperature** outside 450-500°C range
- **Storage tank pressure** above 20 Bar or below 10 Bar
- **Battery SOC** below 15% (critical) or 20% (warning)
- **Inverter efficiency** below 15%
- **System efficiency** below 15% target

### Efficiency Targets
- **15% minimum efficiency** - System must maintain at least 15% overall efficiency
- **30% optimal efficiency** - Target for optimal system performance
- **Real-time tracking** of efficiency trends and targets

### Predictive Insights
- **Battery backup time** - Hours of backup power remaining
- **Solar generation forecast** - Predicted output for next 24 hours
- **Outage probability** - Risk assessment for system failures
- **Maintenance recommendations** - Proactive maintenance alerts

## 🔧 API Endpoints

### System Status
- `GET /api/system/status` - Comprehensive system status
- `GET /api/health` - System health check
- `GET /api/sensors/readings` - Latest sensor readings

### Alerts
- `GET /api/alerts` - Get active alerts
- `POST /api/alerts/{id}/resolve` - Resolve alert
- `GET /api/alerts/statistics` - Alert statistics

### Analytics
- `GET /api/analytics/efficiency` - Efficiency metrics
- `GET /api/analytics/performance` - Performance metrics
- `GET /api/analytics/health` - System health score
- `GET /api/analytics/targets` - Efficiency targets status

### Forecasting
- `GET /api/forecasts/solar` - Solar generation forecast
- `GET /api/forecasts/battery` - Battery depletion forecast
- `GET /api/forecasts/outages` - Outage predictions
- `GET /api/forecasts/summary` - Comprehensive forecast summary

### Data Access
- `GET /api/data/solar` - Solar system data
- `GET /api/data/thermal` - Thermal system data
- `GET /api/data/storage` - Storage system data

## 🔌 WebSocket Real-time Updates

Connect to `ws://localhost:8000/ws` for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.type === 'sensor_data') {
    // Handle sensor data update
  } else if (message.type === 'alert') {
    // Handle new alert
  }
};
```

## 📈 Dashboard Features

### Overview Tab
- Key metrics for all system components
- System health status and efficiency targets
- Recent alerts and notifications
- Real-time updates via WebSocket

### Solar System Tab
- Solar irradiance and PV output
- TEG efficiency and output
- Concentrator alignment status
- Historical generation data

### Thermal System Tab
- Hot water temperature monitoring
- Storage tank pressure and energy
- Molten salt flow rates
- Steam generation output

### Storage Tab
- Battery SOC and temperature
- Backup time calculations
- Thermal storage efficiency
- Water tank levels

### Analytics Tab
- Efficiency calculations and trends
- Performance metrics
- System health scoring
- AI insights and recommendations

### Forecasts Tab
- Solar generation predictions
- Battery depletion estimates
- Outage probability assessments
- Maintenance recommendations

## 🛠️ Configuration

### Monitoring Configuration
```python
config = MonitoringConfig(
    data_collection_interval=1.0,      # Sensor data collection interval
    database_write_interval=5.0,       # Database write interval
    alert_check_interval=2.0,          # Alert checking interval
    efficiency_calculation_interval=10.0,  # Efficiency calculation interval
    predictive_analytics_interval=60.0,    # Predictive analytics interval
    enable_real_time_alerts=True,      # Enable real-time alerts
    enable_predictive_analytics=True   # Enable predictive analytics
)
```

### Alert Thresholds
- **Solar irradiance**: < 100 W/m² (warning)
- **PV output**: < 200 W (high severity)
- **Hot water temperature**: < 450°C or > 500°C (critical)
- **Storage pressure**: < 10 Bar or > 20 Bar (critical)
- **Battery SOC**: < 20% (high), < 15% (critical)
- **Inverter efficiency**: < 15% (high severity)

## 🔍 Monitoring and Troubleshooting

### Log Files
- **System logs**: `comprehensive_system.log`
- **API logs**: Console output
- **Database**: SQLite database files

### Health Checks
- **System status**: `GET /api/health`
- **Component status**: Check individual engine status
- **Database connectivity**: Automatic health checks
- **WebSocket connectivity**: Real-time connection monitoring

### Performance Metrics
- **Data collection rate**: Sensors per second
- **Database write performance**: Write operations per minute
- **Alert response time**: Time from detection to notification
- **Forecast accuracy**: Prediction vs actual performance

## 🚀 Deployment

### Production Deployment
1. **Database**: Use PostgreSQL for production
2. **WebSocket**: Configure for production WebSocket servers
3. **Logging**: Configure production logging levels
4. **Security**: Implement authentication and authorization
5. **Monitoring**: Set up external monitoring and alerting

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Or run individual components
docker build -t microgrid-monitoring .
docker run -p 8000:8000 microgrid-monitoring
```

## 📚 Documentation

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### System Architecture
- **Component diagrams**: See architecture documentation
- **Data flow**: Real-time data processing pipeline
- **Alert flow**: Fault detection and notification system
- **Forecasting flow**: Predictive analytics pipeline

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- **Issues**: Create GitHub issues for bugs and feature requests
- **Documentation**: Check the comprehensive documentation
- **API**: Use the interactive API documentation
- **Logs**: Check system logs for troubleshooting

## 🔮 Future Enhancements

- **Machine learning models** for advanced predictions
- **Mobile app** for remote monitoring
- **Integration with external weather APIs**
- **Advanced visualization** with 3D system models
- **Automated control systems** for system optimization
- **Cloud deployment** options
- **Multi-tenant support** for multiple microgrids