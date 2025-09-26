import React, { useState, useEffect, useCallback } from 'react';
import { 
  Sun, 
  Battery, 
  Thermometer, 
  Zap, 
  Activity,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  TrendingDown,
  Target,
  Clock,
  Gauge
} from 'lucide-react';

import MetricCard from './MetricCard';
import AIInsights from './AIInsights';
import { 
  GenerationChart, 
  StorageChart, 
  TemperatureChart, 
  VoltageChart,
  SystemOverviewChart 
} from './Charts';
import { apiService } from '../services/api';

const ComprehensiveDashboard = ({ onNavigateToAlerts }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [systemStatus, setSystemStatus] = useState(null);
  const [sensorReadings, setSensorReadings] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [efficiencyData, setEfficiencyData] = useState(null);
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [ws, setWs] = useState(null);

  // WebSocket connection for real-time updates
  const connectWebSocket = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    const websocket = new WebSocket(wsUrl);
    
    websocket.onopen = () => {
      console.log('WebSocket connected');
    };
    
    websocket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === 'sensor_data' || message.type === 'alert') {
          fetchData(); // Refresh data on real-time updates
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
    
    websocket.onclose = () => {
      console.log('WebSocket disconnected');
      setTimeout(connectWebSocket, 5000); // Reconnect after 5 seconds
    };
    
    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    setWs(websocket);
  }, []);

  // Fetch comprehensive system data
  const fetchData = useCallback(async () => {
    try {
      setError(null);
      
      const [
        statusResponse,
        sensorsResponse,
        alertsResponse,
        efficiencyResponse,
        forecastResponse
      ] = await Promise.all([
        apiService.get('/api/system/status'),
        apiService.get('/api/sensors/readings'),
        apiService.get('/api/alerts?active_only=true'),
        apiService.get('/api/analytics/efficiency?hours=24'),
        apiService.get('/api/forecasts/summary?hours_ahead=24')
      ]);

      setSystemStatus(statusResponse.data);
      setSensorReadings(sensorsResponse.data.readings);
      setAlerts(alertsResponse.data.alerts);
      setEfficiencyData(efficiencyResponse.data);
      setForecastData(forecastResponse.data);
      setLastUpdate(new Date());
      
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to fetch data. Please ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial data fetch and WebSocket connection
  useEffect(() => {
    fetchData();
    connectWebSocket();
    
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [fetchData, connectWebSocket]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const getMetricStatus = (type, value) => {
    switch (type) {
      case 'temperature':
        if (value > 500) return 'critical';
        if (value > 450) return 'warning';
        return 'good';
      case 'soc':
        if (value < 15) return 'critical';
        if (value < 30) return 'warning';
        return 'good';
      case 'voltage':
        if (value < 180) return 'critical';
        if (value < 200) return 'warning';
        return 'good';
      case 'pressure':
        if (value > 20) return 'critical';
        if (value > 15) return 'warning';
        return 'good';
      default:
        return 'normal';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">Loading comprehensive dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Connection Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchData}
            className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'solar', label: 'Solar System', icon: '☀️' },
    { id: 'thermal', label: 'Thermal System', icon: '🔥' },
    { id: 'storage', label: 'Storage', icon: '🔋' },
    { id: 'analytics', label: 'Analytics', icon: '📈' },
    { id: 'forecasts', label: 'Forecasts', icon: '🔮' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Hybrid Microgrid Monitoring System
              </h1>
              <p className="text-gray-600 mt-1">
                Comprehensive real-time monitoring and analytics
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              {systemStatus && (
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                  systemStatus.system_health === 'healthy' 
                    ? 'bg-green-100 text-green-800' 
                    : systemStatus.system_health === 'warning'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  <div className="flex items-center space-x-2">
                    {systemStatus.system_health === 'healthy' ? (
                      <CheckCircle className="w-4 h-4" />
                    ) : (
                      <AlertTriangle className="w-4 h-4" />
                    )}
                    <span>System {systemStatus.system_health}</span>
                  </div>
                </div>
              )}
              
              <button
                onClick={fetchData}
                className="flex items-center space-x-2 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Refresh</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Alert Summary */}
        {alerts && alerts.length > 0 && (
          <div className="mb-6">
            <div 
              onClick={() => onNavigateToAlerts && onNavigateToAlerts()}
              className="bg-amber-50 border border-amber-200 rounded-lg p-4 cursor-pointer hover:bg-amber-100 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <AlertTriangle className="w-5 h-5 text-amber-600 mr-2" />
                  <span className="text-amber-800 font-medium">
                    {alerts.length} Active Alert{alerts.length !== 1 ? 's' : ''}
                  </span>
                </div>
                <span className="text-sm text-amber-600">
                  Click to view alerts →
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <MetricCard
                title="Solar Generation"
                value={sensorReadings['pv_output_001']?.value || 0}
                unit="W"
                icon={Sun}
                color="yellow"
                status={getMetricStatus('generation', sensorReadings['pv_output_001']?.value || 0)}
              />
              <MetricCard
                title="Battery SOC"
                value={sensorReadings['battery_soc_001']?.value || 0}
                unit="%"
                icon={Battery}
                color="blue"
                status={getMetricStatus('soc', sensorReadings['battery_soc_001']?.value || 0)}
              />
              <MetricCard
                title="Hot Water Temp"
                value={sensorReadings['hot_water_temp_001']?.value || 0}
                unit="°C"
                icon={Thermometer}
                color="red"
                status={getMetricStatus('temperature', sensorReadings['hot_water_temp_001']?.value || 0)}
              />
              <MetricCard
                title="System Health"
                value={systemStatus?.system_health_score?.overall_score || 0}
                unit="%"
                icon={Gauge}
                color="purple"
                status="good"
              />
            </div>

            {/* System Status Overview */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">System Status Overview</h2>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{systemStatus?.alerts?.active_count || 0}</div>
                  <div className="text-sm text-gray-600">Active Alerts</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {systemStatus?.efficiency_targets?.current_efficiency || 0}%
                  </div>
                  <div className="text-sm text-gray-600">Efficiency</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {systemStatus?.battery_forecast?.backup_hours || 0}h
                  </div>
                  <div className="text-sm text-gray-600">Backup Time</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    {systemStatus?.solar_forecast_6h?.predicted_power || 0}W
                  </div>
                  <div className="text-sm text-gray-600">6h Forecast</div>
                </div>
              </div>
            </div>

            {/* Efficiency Targets */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Target className="w-5 h-5 mr-2" />
                Efficiency Targets
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <div className="font-medium text-gray-900">15% Target</div>
                    <div className="text-sm text-gray-600">Minimum efficiency</div>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                    systemStatus?.efficiency_targets?.target_15_met 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {systemStatus?.efficiency_targets?.target_15_met ? '✅ Met' : '❌ Not Met'}
                  </div>
                </div>
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <div className="font-medium text-gray-900">30% Target</div>
                    <div className="text-sm text-gray-600">Optimal efficiency</div>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                    systemStatus?.efficiency_targets?.target_30_met 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {systemStatus?.efficiency_targets?.target_30_met ? '✅ Met' : '⚠️ Not Met'}
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Alerts */}
            {systemStatus?.alerts?.active_count > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Alerts</h2>
                <div className="space-y-2">
                  {systemStatus?.alerts?.recent_alerts?.slice(0, 3).map((alert, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                      <div className="flex items-center">
                        <span className="text-red-600 mr-2">🚨</span>
                        <span className="text-sm font-medium text-gray-900">{alert.type}</span>
                        <span className={`ml-2 px-2 py-1 rounded text-xs ${
                          alert.severity === 'critical' ? 'bg-red-100 text-red-800' :
                          alert.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {alert.severity}
                        </span>
                      </div>
                      <span className="text-xs text-gray-500">
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Solar System Tab */}
        {activeTab === 'solar' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <MetricCard
                title="Solar Irradiance"
                value={sensorReadings['solar_irradiance_001']?.value || 0}
                unit="W/m²"
                icon={Sun}
                color="yellow"
              />
              <MetricCard
                title="PV Output"
                value={sensorReadings['pv_output_001']?.value || 0}
                unit="W"
                icon={Zap}
                color="blue"
              />
              <MetricCard
                title="TEG Output"
                value={sensorReadings['teg_001']?.value || 0}
                unit="W"
                icon={Activity}
                color="green"
              />
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Solar System Status</h3>
              <p className="text-gray-600">Solar system monitoring and control interface would go here.</p>
            </div>
          </div>
        )}

        {/* Thermal System Tab */}
        {activeTab === 'thermal' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <MetricCard
                title="Hot Water Temp"
                value={sensorReadings['hot_water_temp_001']?.value || 0}
                unit="°C"
                icon={Thermometer}
                color="red"
                status={getMetricStatus('temperature', sensorReadings['hot_water_temp_001']?.value || 0)}
              />
              <MetricCard
                title="Tank Pressure"
                value={sensorReadings['tank_pressure_001']?.value || 0}
                unit="Bar"
                icon={Gauge}
                color="orange"
                status={getMetricStatus('pressure', sensorReadings['tank_pressure_001']?.value || 0)}
              />
              <MetricCard
                title="Molten Salt Flow"
                value={sensorReadings['molten_salt_flow_001']?.value || 0}
                unit="L/min"
                icon={Activity}
                color="blue"
              />
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Thermal System Status</h3>
              <p className="text-gray-600">Thermal system monitoring and control interface would go here.</p>
            </div>
          </div>
        )}

        {/* Storage Tab */}
        {activeTab === 'storage' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <MetricCard
                title="Battery SOC"
                value={sensorReadings['battery_soc_001']?.value || 0}
                unit="%"
                icon={Battery}
                color="blue"
                status={getMetricStatus('soc', sensorReadings['battery_soc_001']?.value || 0)}
              />
              <MetricCard
                title="Battery Temp"
                value={sensorReadings['battery_temp_001']?.value || 0}
                unit="°C"
                icon={Thermometer}
                color="green"
              />
              <MetricCard
                title="Backup Hours"
                value={systemStatus?.battery_forecast?.backup_hours || 0}
                unit="h"
                icon={Clock}
                color="purple"
              />
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Storage System Status</h3>
              <p className="text-gray-600">Storage system monitoring and control interface would go here.</p>
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            {efficiencyData && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Efficiency Analytics</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {efficiencyData.efficiency_metrics?.overall_efficiency || 0}%
                    </div>
                    <div className="text-sm text-gray-600">Overall Efficiency</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {efficiencyData.efficiency_metrics?.solar_to_electrical_efficiency || 0}%
                    </div>
                    <div className="text-sm text-gray-600">Solar Efficiency</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-orange-600">
                      {efficiencyData.efficiency_metrics?.thermal_to_electrical_efficiency || 0}%
                    </div>
                    <div className="text-sm text-gray-600">Thermal Efficiency</div>
                  </div>
                </div>
              </div>
            )}
            <AIInsights />
          </div>
        )}

        {/* Forecasts Tab */}
        {activeTab === 'forecasts' && (
          <div className="space-y-6">
            {forecastData && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">System Forecasts</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium text-gray-800 mb-2">Solar Generation Forecast</h4>
                    <div className="space-y-2">
                      {forecastData.solar_forecasts?.slice(0, 6).map((forecast, index) => (
                        <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                          <span>{forecast.forecast_horizon}h ahead</span>
                          <span className="font-medium">{forecast.predicted_power}W</span>
                          <span className="text-sm text-gray-500">{forecast.confidence}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-800 mb-2">Battery Forecast</h4>
                    {forecastData.battery_forecast && (
                      <div className="space-y-2">
                        <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                          <span>Current SOC</span>
                          <span className="font-medium">{forecastData.battery_forecast.current_soc}%</span>
                        </div>
                        <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                          <span>Backup Hours</span>
                          <span className="font-medium">{forecastData.battery_forecast.backup_hours}h</span>
                        </div>
                        <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                          <span>Depletion Rate</span>
                          <span className="font-medium">{forecastData.battery_forecast.depletion_rate}%/h</span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <footer className="mt-8 text-center text-sm text-gray-500">
          {lastUpdate && (
            <p>Last updated: {lastUpdate.toLocaleString()}</p>
          )}
          <p className="mt-1">
            Comprehensive Hybrid Microgrid Monitoring System • Real-time WebSocket updates
          </p>
        </footer>
      </main>
    </div>
  );
};

export default ComprehensiveDashboard;