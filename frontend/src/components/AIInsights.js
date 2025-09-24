import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  Zap, 
  AlertTriangle, 
  TrendingUp, 
  Settings,
  Power,
  Sun,
  Battery,
  Activity,
  Clock,
  Shield
} from 'lucide-react';
import { apiService } from '../services/api';

const AIInsights = () => {
  const [faultDetection, setFaultDetection] = useState(null);
  const [gridSwitching, setGridSwitching] = useState(null);
  const [solarPredictions, setSolarPredictions] = useState(null);
  const [loadManagement, setLoadManagement] = useState(null);
  const [loadPredictions, setLoadPredictions] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAIData();
    const interval = setInterval(fetchAIData, 60000); // Update every minute
    return () => clearInterval(interval);
  }, []);

  const fetchAIData = async () => {
    try {
      const [faults, grid, solar, management, loads] = await Promise.all([
        fetch('http://localhost:8000/api/ai/fault-detection').then(r => r.json()),
        fetch('http://localhost:8000/api/ai/grid-switching').then(r => r.json()),
        fetch('http://localhost:8000/api/ai/solar-predictions?hours=6').then(r => r.json()),
        fetch('http://localhost:8000/api/ai/load-management').then(r => r.json()),
        fetch('http://localhost:8000/api/ai/load-predictions?hours=12').then(r => r.json())
      ]);

      setFaultDetection(faults);
      setGridSwitching(grid);
      setSolarPredictions(solar);
      setLoadManagement(management);
      setLoadPredictions(loads);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching AI data:', error);
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-100 border-red-200';
      case 'high': return 'text-orange-600 bg-orange-100 border-orange-200';
      case 'medium': return 'text-yellow-600 bg-yellow-100 border-yellow-200';
      default: return 'text-blue-600 bg-blue-100 border-blue-200';
    }
  };

  const getHealthColor = (health) => {
    switch (health) {
      case 'excellent': return 'text-green-600 bg-green-100';
      case 'good': return 'text-blue-600 bg-blue-100';
      case 'degraded': return 'text-yellow-600 bg-yellow-100';
      case 'critical': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="metric-card">
        <div className="flex items-center justify-center p-8">
          <Brain className="w-8 h-8 animate-pulse text-blue-500 mr-3" />
          <span className="text-gray-600">Loading AI insights...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* AI Header */}
      <div className="metric-card">
        <div className="flex items-center mb-4">
          <Brain className="w-6 h-6 text-purple-600 mr-3" />
          <h2 className="text-xl font-bold text-gray-800">AI-Powered Microgrid Intelligence</h2>
        </div>
        <p className="text-gray-600">
          Advanced AI analysis for fault detection, load optimization, and predictive maintenance
        </p>
      </div>

      {/* Grid Switching Analysis */}
      {gridSwitching && (
        <div className="metric-card">
          <div className="flex items-center mb-4">
            <Power className="w-5 h-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-800">Grid Switching Intelligence</h3>
          </div>
          
          <div className={`p-4 rounded-lg border-2 ${
            gridSwitching.switch_to_grid 
              ? 'bg-red-50 border-red-200' 
              : 'bg-green-50 border-green-200'
          }`}>
            <div className="flex items-center mb-3">
              <Zap className={`w-5 h-5 mr-2 ${
                gridSwitching.switch_to_grid ? 'text-red-600' : 'text-green-600'
              }`} />
              <span className={`font-semibold ${
                gridSwitching.switch_to_grid ? 'text-red-800' : 'text-green-800'
              }`}>
                {gridSwitching.switch_to_grid ? 'SWITCH TO GRID' : 'CONTINUE MICROGRID'}
              </span>
            </div>
            
            <p className={`text-sm mb-3 ${
              gridSwitching.switch_to_grid ? 'text-red-700' : 'text-green-700'
            }`}>
              {gridSwitching.recommendation}
            </p>
            
            {gridSwitching.reasons && gridSwitching.reasons.length > 0 && (
              <div className="space-y-1">
                <p className="text-sm font-medium text-gray-700">Reasons:</p>
                {gridSwitching.reasons.map((reason, index) => (
                  <p key={index} className="text-sm text-gray-600">• {reason}</p>
                ))}
              </div>
            )}
            
            <div className="grid grid-cols-2 gap-4 mt-4 pt-3 border-t border-gray-200">
              <div>
                <p className="text-xs text-gray-500">Current SOC</p>
                <p className="text-lg font-bold text-gray-800">{gridSwitching.current_soc}%</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">6h Energy Deficit</p>
                <p className="text-lg font-bold text-gray-800">{gridSwitching.predicted_deficit_6h?.toFixed(0)}W</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Fault Detection */}
      {faultDetection && (
        <div className="metric-card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <Shield className="w-5 h-5 text-red-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-800">AI Fault Detection</h3>
            </div>
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${getHealthColor(faultDetection.system_health)}`}>
              {faultDetection.system_health?.toUpperCase()}
            </div>
          </div>
          
          {faultDetection.faults && faultDetection.faults.length > 0 ? (
            <div className="space-y-3">
              {faultDetection.faults.map((fault, index) => (
                <div key={index} className={`p-3 rounded-lg border ${getSeverityColor(fault.severity)}`}>
                  <div className="flex items-center mb-2">
                    <AlertTriangle className="w-4 h-4 mr-2" />
                    <span className="font-medium">{fault.type.replace('_', ' ').toUpperCase()}</span>
                    <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${getSeverityColor(fault.severity)}`}>
                      {fault.severity}
                    </span>
                  </div>
                  <p className="text-sm mb-2">{fault.message}</p>
                  <p className="text-xs opacity-75">💡 {fault.recommendation}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-4">
              <Shield className="w-12 h-12 text-green-500 mx-auto mb-2" />
              <p className="text-green-600 font-medium">No faults detected</p>
              <p className="text-sm text-gray-500">System operating normally</p>
            </div>
          )}
          
          <div className="mt-4 pt-3 border-t border-gray-200 text-xs text-gray-500">
            Analyzed {faultDetection.data_points_analyzed} data points • 
            Last check: {new Date(faultDetection.analysis_timestamp).toLocaleTimeString()}
          </div>
        </div>
      )}

      {/* Load Management */}
      {loadManagement && loadManagement.optimization_strategies && (
        <div className="metric-card">
          <div className="flex items-center mb-4">
            <Settings className="w-5 h-5 text-green-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-800">Smart Load Management</h3>
          </div>
          
          {loadManagement.optimization_strategies.length > 0 ? (
            <div className="space-y-3">
              {loadManagement.optimization_strategies.map((strategy, index) => (
                <div key={index} className={`p-3 rounded-lg border ${
                  strategy.priority === 'critical' ? 'bg-red-50 border-red-200' :
                  strategy.priority === 'high' ? 'bg-orange-50 border-orange-200' :
                  strategy.priority === 'medium' ? 'bg-yellow-50 border-yellow-200' :
                  'bg-blue-50 border-blue-200'
                }`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-800">{strategy.action.replace('_', ' ').toUpperCase()}</span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      strategy.priority === 'critical' ? 'bg-red-100 text-red-800' :
                      strategy.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                      strategy.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {strategy.priority}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 mb-2">{strategy.message}</p>
                  
                  {strategy.loads_to_shed && (
                    <div className="text-xs text-gray-600">
                      <span className="font-medium">Loads to shed: </span>
                      {strategy.loads_to_shed.join(', ')}
                      <span className="ml-2 text-green-600">({strategy.estimated_savings})</span>
                    </div>
                  )}
                  
                  {strategy.recommended_loads && (
                    <div className="text-xs text-gray-600">
                      <span className="font-medium">Recommended: </span>
                      {strategy.recommended_loads.join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-4">
              <Activity className="w-12 h-12 text-green-500 mx-auto mb-2" />
              <p className="text-green-600 font-medium">Load management optimal</p>
              <p className="text-sm text-gray-500">No optimization needed</p>
            </div>
          )}
        </div>
      )}

      {/* Solar Predictions */}
      {solarPredictions && (
        <div className="metric-card">
          <div className="flex items-center mb-4">
            <Sun className="w-5 h-5 text-yellow-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-800">Solar Generation Forecast</h3>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {solarPredictions.predictions.slice(0, 6).map((pred, index) => {
              const time = new Date(pred.timestamp).toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit' 
              });
              return (
                <div key={index} className="bg-yellow-50 p-3 rounded-lg border border-yellow-200">
                  <div className="flex items-center justify-between mb-1">
                    <Clock className="w-4 h-4 text-yellow-600" />
                    <span className="text-xs text-gray-500">{time}</span>
                  </div>
                  <p className="text-lg font-bold text-gray-800">{pred.predicted_generation}W</p>
                  <p className="text-xs text-gray-600">
                    {Math.round(pred.confidence * 100)}% confidence
                  </p>
                </div>
              );
            })}
          </div>
          
          <div className="mt-4 pt-3 border-t border-gray-200 text-sm text-gray-600">
            <span className="font-medium">Method:</span> {solarPredictions.method?.replace('_', ' ')} • 
            <span className="font-medium ml-2">Avg Confidence:</span> {Math.round(solarPredictions.average_confidence * 100)}%
          </div>
        </div>
      )}

      {/* Load Predictions */}
      {loadPredictions && (
        <div className="metric-card">
          <div className="flex items-center mb-4">
            <TrendingUp className="w-5 h-5 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-800">Load Demand Forecast</h3>
          </div>
          
          <div className="space-y-2">
            {loadPredictions.predictions.slice(0, 8).map((pred, index) => {
              const time = new Date(pred.timestamp).toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit' 
              });
              const isEvening = pred.load_type === 'evening_peak';
              
              return (
                <div key={index} className={`flex items-center justify-between p-2 rounded ${
                  isEvening ? 'bg-red-50' : 'bg-blue-50'
                }`}>
                  <div className="flex items-center">
                    <Battery className={`w-4 h-4 mr-2 ${isEvening ? 'text-red-600' : 'text-blue-600'}`} />
                    <span className="text-sm font-medium">{time}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-bold">{pred.predicted_load}W</span>
                    <p className={`text-xs ${isEvening ? 'text-red-600' : 'text-blue-600'}`}>
                      {pred.load_type.replace('_', ' ')}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
          
          {loadPredictions.peak_hours && (
            <div className="mt-4 pt-3 border-t border-gray-200">
              <p className="text-sm text-gray-600">
                <span className="font-medium">Peak hours:</span> {loadPredictions.peak_hours.join(', ')}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AIInsights;
