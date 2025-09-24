import React, { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import useAuthStore from './store/authStore';
import LoginForm from './components/LoginForm';
import Navigation from './components/Navigation';
import Dashboard from './components/Dashboard';
import AIInsights from './components/AIInsights';
import AlertsPage from './components/AlertsPage';
import AlertsPageDebug from './components/AlertsPageDebug';
import AlertsPageSimple from './components/AlertsPageSimple';
import ErrorBoundary from './components/ErrorBoundary';
import LoadingSpinner from './components/LoadingSpinner';
import './index.css';

function App() {
  const { isAuthenticated, isLoading } = useAuthStore();
  const [currentView, setCurrentView] = useState('dashboard');

  if (isLoading) {
    return <LoadingSpinner size="xl" message="Initializing system..." />;
  }

  if (!isAuthenticated) {
    return (
      <ErrorBoundary>
        <LoginForm />
        <Toaster position="top-right" />
      </ErrorBoundary>
    );
  }

  const renderCurrentView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard onNavigateToAlerts={() => setCurrentView('alerts')} />;
      case 'analytics':
        return (
          <div className="p-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-6">AI Analytics & Insights</h1>
            <AIInsights />
          </div>
        );
      case 'alerts':
        return <AlertsPageSimple />;
      case 'settings':
        return (
          <div className="p-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-6">System Settings</h1>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600">System configuration interface coming soon...</p>
            </div>
          </div>
        );
      default:
        return <Dashboard />;
    }
  };

  return (
    <ErrorBoundary>
      <div className="App bg-gray-50 min-h-screen">
        <Navigation currentView={currentView} setCurrentView={setCurrentView} />
        
        {/* Main Content */}
        <div className="lg:pl-80">
          <main className="min-h-screen">
            {renderCurrentView()}
          </main>
        </div>
        
        <Toaster position="top-right" />
      </div>
    </ErrorBoundary>
  );
}

export default App;
