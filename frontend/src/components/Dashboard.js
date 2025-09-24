import React, { useState, useEffect, useCallback } from 'react';
import { 
  Sun, 
  Battery, 
  Thermometer, 
  Zap, 
  Activity,
  RefreshCw,
  AlertTriangle,
  CheckCircle
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

const Dashboard = ({ onNavigateToAlerts }) => {
  const [sensorData, setSensorData] = useState([]);
  const [latestData, setLatestData] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [systemStatus, setSystemStatus] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  // Fetch all data
  const fetchData = useCallback(async () => {
    try {
      setError(null);
      
      const [
        sensorResponse,
        latestResponse,
        alertsResponse,
        statusResponse,
        analyticsResponse
      ] = await Promise.all([
        apiService.getSensorData({ hours: 6 }), // Last 6 hours
        apiService.getLatestSensorData(),
        apiService.getAlerts({ active_only: true }),
        apiService.getSystemStatus(),
        apiService.getAnalytics(24)
      ]);

      setSensorData(sensorResponse.data);
      setLatestData(latestResponse.data);
      setAlerts(alertsResponse.data);
      setSystemStatus(statusResponse.data);
      setAnalytics(analyticsResponse.data);
      setLastUpdate(new Date());
      
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to fetch data. Please ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial data fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  // Calculate trends (simplified)
  const calculateTrend = (current, previous) => {
    if (!previous || previous === 0) return 0;
    return ((current - previous) / previous) * 100;
  };

  const getMetricStatus = (type, value) => {
    switch (type) {
      case 'temperature':
        if (value > 100) return 'critical';
        if (value > 80) return 'warning';
        return 'good';
      case 'soc':
        if (value < 15) return 'critical';
        if (value < 30) return 'warning';
        return 'good';
      case 'voltage':
        if (value < 180) return 'critical';
        if (value < 200) return 'warning';
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
          <p className="text-gray-600">Loading dashboard...</p>
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

  const previousData = sensorData.length > 1 ? sensorData[sensorData.length - 2] : null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Microgrid Energy Monitor
              </h1>
              <p className="text-gray-600 mt-1">
                Real-time monitoring and analytics
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              {systemStatus && (
                <div className={`px-3 py-1 rounded-full text-sm font-medium status-${systemStatus.system_health}`}>
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

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Alert Summary - Clickable to navigate to alerts */}
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

        {/* Metrics Cards */}
        {latestData && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <MetricCard
              title="Solar Generation"
              value={latestData.generation}
              unit="W"
              trend={calculateTrend(latestData.generation, previousData?.generation)}
              icon={Sun}
              color="yellow"
            />
            
            <MetricCard
              title="Energy Storage"
              value={latestData.storage}
              unit="kWh"
              trend={calculateTrend(latestData.storage, previousData?.storage)}
              status={getMetricStatus('soc', latestData.soc)}
              icon={Battery}
              color="blue"
            />
            
            <MetricCard
              title="Temperature"
              value={latestData.temperature}
              unit="°C"
              trend={calculateTrend(latestData.temperature, previousData?.temperature)}
              status={getMetricStatus('temperature', latestData.temperature)}
              icon={Thermometer}
              color="red"
            />
            
            <MetricCard
              title="Voltage"
              value={latestData.voltage}
              unit="V"
              trend={calculateTrend(latestData.voltage, previousData?.voltage)}
              status={getMetricStatus('voltage', latestData.voltage)}
              icon={Zap}
              color="purple"
            />
          </div>
        )}

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <GenerationChart data={sensorData} />
          <StorageChart data={sensorData} />
          <TemperatureChart data={sensorData} />
          <VoltageChart data={sensorData} />
        </div>

        {/* System Overview and Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <SystemOverviewChart data={sensorData} />
          
          {/* Analytics Panel */}
          {analytics && (
            <div className="lg:col-span-2 metric-card">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                <Activity className="w-5 h-5 mr-2" />
                System Analytics & Predictions
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-medium text-blue-800 mb-2">Efficiency Score</h4>
                  <p className="text-2xl font-bold text-blue-900">
                    {analytics.efficiency_score?.toFixed(1)}%
                  </p>
                  <p className="text-sm text-blue-700">
                    Based on SOC and voltage stability
                  </p>
                </div>
                
                <div className="bg-green-50 p-4 rounded-lg">
                  <h4 className="font-medium text-green-800 mb-2">Generation Trend</h4>
                  <p className="text-lg font-semibold text-green-900 capitalize">
                    {analytics.generation_trend}
                  </p>
                  <p className="text-sm text-green-700">
                    Avg: {analytics.avg_generation?.toFixed(0)}W
                  </p>
                </div>
                
                <div className="bg-yellow-50 p-4 rounded-lg">
                  <h4 className="font-medium text-yellow-800 mb-2">Next Hour Prediction</h4>
                  <p className="text-lg font-semibold text-yellow-900">
                    {analytics.predictions?.next_hour_generation?.toFixed(0)}W
                  </p>
                  <p className="text-sm text-yellow-700">
                    Estimated generation
                  </p>
                </div>
                
                <div className="bg-purple-50 p-4 rounded-lg">
                  <h4 className="font-medium text-purple-800 mb-2">Storage Runtime</h4>
                  <p className="text-lg font-semibold text-purple-900">
                    {analytics.predictions?.storage_depletion_hours?.toFixed(1)}h
                  </p>
                  <p className="text-sm text-purple-700">
                    At current consumption
                  </p>
                </div>
              </div>
              
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-800 mb-2">Maintenance Recommendation</h4>
                <p className="text-sm text-gray-700">
                  {analytics.predictions?.maintenance_recommendation}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* AI Insights Section */}
        <AIInsights />

        {/* Footer */}
        <footer className="mt-8 text-center text-sm text-gray-500">
          {lastUpdate && (
            <p>Last updated: {lastUpdate.toLocaleString()}</p>
          )}
          <p className="mt-1">
            Ready for real IoT sensor integration • ESP32 compatible
          </p>
        </footer>
      </main>
    </div>
  );
};

export default Dashboard;
