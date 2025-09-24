import React from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

// Custom tooltip component
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
        <p className="text-sm text-gray-600 mb-1">
          {new Date(label).toLocaleTimeString()}
        </p>
        {payload.map((entry, index) => (
          <p key={index} className="text-sm font-medium" style={{ color: entry.color }}>
            {entry.name}: {entry.value?.toFixed(1)} {entry.unit || ''}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export const GenerationChart = ({ data }) => {
  const chartData = data.map(item => ({
    timestamp: item.timestamp,
    generation: item.generation,
    time: new Date(item.timestamp).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }));

  return (
    <div className="metric-card">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Solar Generation</h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="time" 
            stroke="#666"
            fontSize={12}
            interval="preserveStartEnd"
          />
          <YAxis 
            stroke="#666"
            fontSize={12}
            label={{ value: 'Watts', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="generation"
            stroke="#f59e0b"
            fill="#fef3c7"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export const StorageChart = ({ data }) => {
  const chartData = data.map(item => ({
    timestamp: item.timestamp,
    storage: item.storage,
    soc: item.soc,
    time: new Date(item.timestamp).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }));

  return (
    <div className="metric-card">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Energy Storage</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="time" 
            stroke="#666"
            fontSize={12}
            interval="preserveStartEnd"
          />
          <YAxis 
            yAxisId="left"
            stroke="#666"
            fontSize={12}
            label={{ value: 'kWh', angle: -90, position: 'insideLeft' }}
          />
          <YAxis 
            yAxisId="right"
            orientation="right"
            stroke="#666"
            fontSize={12}
            label={{ value: 'SOC %', angle: 90, position: 'insideRight' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="storage"
            stroke="#0ea5e9"
            strokeWidth={2}
            dot={false}
            name="Storage"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="soc"
            stroke="#22c55e"
            strokeWidth={2}
            dot={false}
            name="SOC"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export const TemperatureChart = ({ data }) => {
  const chartData = data.map(item => ({
    timestamp: item.timestamp,
    temperature: item.temperature,
    time: new Date(item.timestamp).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }));

  return (
    <div className="metric-card">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Temperature Monitoring</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="time" 
            stroke="#666"
            fontSize={12}
            interval="preserveStartEnd"
          />
          <YAxis 
            stroke="#666"
            fontSize={12}
            label={{ value: '°C', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="temperature"
            stroke="#ef4444"
            strokeWidth={2}
            dot={false}
          />
          {/* Warning threshold line */}
          <Line
            type="monotone"
            dataKey={() => 80}
            stroke="#f59e0b"
            strokeWidth={1}
            strokeDasharray="5 5"
            dot={false}
            name="Warning Threshold"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export const VoltageChart = ({ data }) => {
  const chartData = data.map(item => ({
    timestamp: item.timestamp,
    voltage: item.voltage,
    time: new Date(item.timestamp).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }));

  return (
    <div className="metric-card">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Voltage Monitoring</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="time" 
            stroke="#666"
            fontSize={12}
            interval="preserveStartEnd"
          />
          <YAxis 
            stroke="#666"
            fontSize={12}
            domain={['dataMin - 10', 'dataMax + 10']}
            label={{ value: 'Volts', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="voltage"
            stroke="#8b5cf6"
            strokeWidth={2}
            dot={false}
          />
          {/* Critical threshold line */}
          <Line
            type="monotone"
            dataKey={() => 200}
            stroke="#ef4444"
            strokeWidth={1}
            strokeDasharray="5 5"
            dot={false}
            name="Critical Threshold"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export const SystemOverviewChart = ({ data }) => {
  if (!data || data.length === 0) return null;

  const latest = data[data.length - 1];
  
  const pieData = [
    { name: 'Used', value: latest.soc, color: '#22c55e' },
    { name: 'Available', value: 100 - latest.soc, color: '#e5e7eb' }
  ];

  return (
    <div className="metric-card">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Battery Status</h3>
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie
            data={pieData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={5}
            dataKey="value"
          >
            {pieData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip 
            formatter={(value) => [`${value.toFixed(1)}%`, 'Percentage']}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="text-center mt-4">
        <p className="text-2xl font-bold text-gray-800">{latest.soc.toFixed(1)}%</p>
        <p className="text-sm text-gray-600">State of Charge</p>
      </div>
    </div>
  );
};
