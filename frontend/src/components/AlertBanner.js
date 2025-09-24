import React from 'react';
import { AlertTriangle, AlertCircle, Info, X } from 'lucide-react';

const AlertBanner = ({ alerts, onResolve }) => {
  if (!alerts || alerts.length === 0) return null;

  const getAlertIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return <AlertCircle className="w-5 h-5" />;
      case 'high':
        return <AlertTriangle className="w-5 h-5" />;
      case 'medium':
        return <AlertTriangle className="w-5 h-5" />;
      default:
        return <Info className="w-5 h-5" />;
    }
  };

  const getAlertClass = (severity) => {
    switch (severity) {
      case 'critical':
        return 'alert-banner alert-critical';
      case 'high':
        return 'alert-banner alert-high';
      case 'medium':
        return 'alert-banner alert-medium';
      default:
        return 'alert-banner alert-low';
    }
  };

  return (
    <div className="space-y-2 mb-6">
      {alerts.map((alert) => (
        <div key={alert.id} className={getAlertClass(alert.severity)}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {getAlertIcon(alert.severity)}
              <div>
                <p className="font-medium">{alert.message}</p>
                <p className="text-sm opacity-75">
                  {alert.alert_type.toUpperCase()} • {new Date(alert.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
            <button
              onClick={() => onResolve(alert.id)}
              className="p-1 hover:bg-black hover:bg-opacity-10 rounded-full transition-colors"
              title="Resolve alert"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default AlertBanner;
