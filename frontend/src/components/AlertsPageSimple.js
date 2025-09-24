import React, { useState, useEffect } from 'react';
import { ExclamationTriangleIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

const AlertsPageSimple = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchAlerts = async () => {
    try {
      console.log('🔍 Fetching alerts...');
      const response = await fetch('http://localhost:8000/api/alerts');
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('📊 Received alerts:', data);
      console.log('📏 Alert count:', data.length);
      
      setAlerts(Array.isArray(data) ? data : []);
      setError(null);
      setLoading(false);
    } catch (err) {
      console.error('❌ Error fetching alerts:', err);
      setError(err.message);
      setAlerts([]);
      setLoading(false);
    }
  };

  const handleResolveAlert = async (alertId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/alerts/${alertId}/resolve`, {
        method: 'POST'
      });
      
      if (response.ok) {
        // Refresh alerts after resolving
        fetchAlerts();
      }
    } catch (err) {
      console.error('Error resolving alert:', err);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">System Alerts</h1>
        <div className="flex items-center justify-center p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading alerts...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">System Alerts</h1>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="w-5 h-5 text-red-600 mr-2" />
            <span className="text-red-800 font-medium">Error loading alerts</span>
          </div>
          <p className="text-red-700 mt-2">{error}</p>
          <button 
            onClick={fetchAlerts}
            className="mt-3 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const activeAlerts = alerts.filter(alert => !alert.resolved);
  const resolvedAlerts = alerts.filter(alert => alert.resolved);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">System Alerts</h1>
      
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="w-8 h-8 text-red-600 mr-3" />
            <div>
              <p className="text-2xl font-bold text-gray-900">{activeAlerts.length}</p>
              <p className="text-sm text-gray-600">Active Alerts</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <CheckCircleIcon className="w-8 h-8 text-green-600 mr-3" />
            <div>
              <p className="text-2xl font-bold text-gray-900">{resolvedAlerts.length}</p>
              <p className="text-sm text-gray-600">Resolved</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
              <span className="text-blue-600 font-bold text-sm">{alerts.length}</span>
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{alerts.length}</p>
              <p className="text-sm text-gray-600">Total Alerts</p>
            </div>
          </div>
        </div>
      </div>

      {/* Alerts List */}
      {alerts.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <CheckCircleIcon className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No alerts found</h3>
          <p className="text-gray-600">System is running smoothly!</p>
        </div>
      ) : (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">
            Recent Alerts ({alerts.length})
          </h2>
          
          {alerts.slice(0, 20).map((alert) => (
            <div
              key={alert.id}
              className={`bg-white rounded-lg shadow border-l-4 ${
                alert.resolved 
                  ? 'border-l-green-500' 
                  : alert.severity === 'critical' 
                  ? 'border-l-red-500'
                  : alert.severity === 'high'
                  ? 'border-l-orange-500'
                  : alert.severity === 'medium'
                  ? 'border-l-yellow-500'
                  : 'border-l-blue-500'
              }`}
            >
              <div className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        alert.severity === 'critical' ? 'bg-red-100 text-red-800' :
                        alert.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                        alert.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {alert.severity?.toUpperCase()}
                      </span>
                      
                      <span className="text-xs text-gray-500">
                        {alert.alert_type?.replace('_', ' ').toUpperCase()}
                      </span>
                      
                      {alert.resolved && (
                        <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          RESOLVED
                        </span>
                      )}
                    </div>
                    
                    <p className="text-gray-900 font-medium mb-1">{alert.message}</p>
                    
                    <div className="text-sm text-gray-500">
                      <span>{new Date(alert.timestamp).toLocaleString()}</span>
                      {alert.value && alert.threshold && (
                        <span className="ml-4">
                          Value: {alert.value} | Threshold: {alert.threshold}
                        </span>
                      )}
                    </div>
                  </div>

                  {!alert.resolved && (
                    <button
                      onClick={() => handleResolveAlert(alert.id)}
                      className="ml-4 bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                    >
                      Resolve
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
          
          {alerts.length > 20 && (
            <div className="text-center py-4">
              <p className="text-gray-600">Showing first 20 of {alerts.length} alerts</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AlertsPageSimple;
