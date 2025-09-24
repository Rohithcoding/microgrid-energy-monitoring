import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';

const AlertsPageDebug = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    console.log('🔍 Starting to fetch alerts...');
    try {
      setLoading(true);
      setError(null);
      
      console.log('📡 Making API call...');
      const response = await apiService.getAlerts();
      console.log('📦 Raw response:', response);
      console.log('📊 Response data:', response.data);
      console.log('🔢 Data type:', typeof response.data);
      console.log('📋 Is array?', Array.isArray(response.data));
      
      // Extract data from axios response
      const alertsData = response.data || response;
      console.log('✅ Processed alerts data:', alertsData);
      console.log('📏 Alerts count:', alertsData?.length);
      
      setAlerts(Array.isArray(alertsData) ? alertsData : []);
      setLoading(false);
      console.log('🎉 Alerts set successfully!');
      
    } catch (error) {
      console.error('❌ Error fetching alerts:', error);
      console.error('📋 Error details:', error.response?.data);
      setError(error.message);
      setAlerts([]);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Debug: Loading Alerts...</h1>
        <div className="animate-pulse bg-gray-200 h-20 rounded"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold text-red-600 mb-4">Debug: Error Loading Alerts</h1>
        <div className="bg-red-50 border border-red-200 rounded p-4">
          <p className="text-red-800">{error}</p>
        </div>
        <button 
          onClick={fetchAlerts}
          className="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-4">Debug: Alerts Section</h1>
      
      <div className="bg-blue-50 border border-blue-200 rounded p-4 mb-6">
        <h3 className="font-bold text-blue-800">Debug Info:</h3>
        <p>Alerts loaded: {alerts.length}</p>
        <p>Alerts type: {typeof alerts}</p>
        <p>Is array: {Array.isArray(alerts) ? 'Yes' : 'No'}</p>
      </div>

      {alerts.length === 0 ? (
        <div className="bg-gray-50 border border-gray-200 rounded p-8 text-center">
          <h3 className="text-lg font-medium text-gray-900 mb-2">No alerts found</h3>
          <p className="text-gray-600">The system returned no alerts.</p>
          <button 
            onClick={fetchAlerts}
            className="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Refresh
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Alerts ({alerts.length}):</h3>
          {alerts.slice(0, 5).map((alert, index) => (
            <div key={alert.id || index} className="bg-white border border-gray-200 rounded p-4">
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-medium">{alert.message || 'No message'}</p>
                  <p className="text-sm text-gray-600">
                    Type: {alert.alert_type || 'Unknown'} | 
                    Severity: {alert.severity || 'Unknown'} | 
                    Resolved: {alert.resolved ? 'Yes' : 'No'}
                  </p>
                  <p className="text-xs text-gray-500">
                    {alert.timestamp ? new Date(alert.timestamp).toLocaleString() : 'No timestamp'}
                  </p>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  alert.severity === 'critical' ? 'bg-red-100 text-red-800' :
                  alert.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                  alert.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-blue-100 text-blue-800'
                }`}>
                  {alert.severity?.toUpperCase() || 'UNKNOWN'}
                </span>
              </div>
            </div>
          ))}
          {alerts.length > 5 && (
            <p className="text-gray-600 text-center">... and {alerts.length - 5} more alerts</p>
          )}
        </div>
      )}
    </div>
  );
};

export default AlertsPageDebug;
