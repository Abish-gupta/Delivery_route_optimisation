import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { Truck, Package, Clock, MapPin, TrendingUp, Users, AlertTriangle, CheckCircle } from 'lucide-react';

const DeliveryOptimizationDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [orders, setOrders] = useState([]);
  const [vehicles, setVehicles] = useState([
    { id: 'VEH_001', name: 'Large Truck', capacity: '1000kg capacity' },
    { id: 'VEH_002', name: 'Medium Van', capacity: '750kg capacity' },
    { id: 'VEH_003', name: 'Small Van', capacity: '500kg capacity' },
  ]);
  const [selectedVehicle, setSelectedVehicle] = useState('VEH_001'); // State for selected vehicle
  const [deliveryMetrics, setDeliveryMetrics] = useState({});
  const [optimizedRouteData, setOptimizedRouteData] = useState({}); // State for optimized route

  // Mock data for demonstration
  useEffect(() => {
    // Simulate real-time data updates
    const interval = setInterval(() => {
      setDeliveryMetrics({
        totalOrders: Math.floor(Math.random() * 100) + 150,
        deliveredOrders: Math.floor(Math.random() * 80) + 120,
        inTransitOrders: Math.floor(Math.random() * 20) + 15,
        averageDeliveryTime: (Math.random() * 0.5 + 2.1).toFixed(1),
        onTimeDeliveryRate: (Math.random() * 5 + 92).toFixed(1),
        customerSatisfaction: (Math.random() * 0.3 + 4.2).toFixed(1)
      });
    }, 500000);

    // Initial route generation when component mounts
    generateRoute('VEH_001');

    return () => clearInterval(interval);
  }, []);

  // Function to simulate route generation based on vehicle
  const generateRoute = (vehicleId) => {
    let newRoute = [];
    let totalDistance = 0;
    let estimatedTime = 0;
    let fuelCost = 0;
    let deliveries = 0;

    switch (vehicleId) {
      case 'VEH_001': // Large Truck
        newRoute = [
          { stop: '🏭 Depot (Start)', time: '08:00 AM' },
          { stop: '📦 Bandra West - ORD_001', time: '08:25 AM' },
          { stop: '📦 Andheri East - ORD_003', time: '09:10 AM' },
          { stop: '📦 Churchgate - ORD_002', time: '09:45 AM' },
          { stop: '📦 Powai - ORD_004', time: '10:30 AM' },
          { stop: '🏭 Return to Depot', time: '11:15 AM' },
        ];
        totalDistance = 55.2;
        estimatedTime = 3.2;
        fuelCost = 480;
        deliveries = 4;
        break;
      case 'VEH_002': // Medium Van
        newRoute = [
          { stop: '🏭 Depot (Start)', time: '08:00 AM' },
          { stop: '📦 Worli - ORD_005', time: '08:20 AM' },
          { stop: '📦 Bandra West - ORD_001', time: '08:50 AM' },
          { stop: '📦 Andheri East - ORD_003', time: '09:35 AM' },
          { stop: '🏭 Return to Depot', time: '10:10 AM' },
        ];
        totalDistance = 42.1;
        estimatedTime = 2.8;
        fuelCost = 350;
        deliveries = 3;
        break;
      case 'VEH_003': // Small Van
        newRoute = [
          { stop: '🏭 Depot (Start)', time: '08:00 AM' },
          { stop: '📦 Churchgate - ORD_002', time: '08:30 AM' },
          { stop: '📦 Worli - ORD_005', time: '09:00 AM' },
          { stop: '🏭 Return to Depot', time: '09:45 AM' },
        ];
        totalDistance = 32.5;
        estimatedTime = 2.5;
        fuelCost = 285;
        deliveries = 2;
        break;
      default:
        newRoute = [];
    }
    setOptimizedRouteData({
      route: newRoute,
      totalDistance,
      estimatedTime,
      fuelCost,
      deliveries
    });
  };

  // Sample data
  const performanceData = [
    { month: 'Jan', deliveries: 245, onTime: 220, failed: 25 },
    { month: 'Feb', deliveries: 312, onTime: 285, failed: 27 },
    { month: 'Mar', deliveries: 389, onTime: 355, failed: 34 },
    { month: 'Apr', deliveries: 456, onTime: 430, failed: 26 },
    { month: 'May', deliveries: 523, onTime: 495, failed: 28 },
    { month: 'Jun', deliveries: 587, onTime: 560, failed: 27 }
  ];

  const routeEfficiencyData = [
    { route: 'Route 1', oldDistance: 45.2, newDistance: 32.1, timeSaved: 25 },
    { route: 'Route 2', oldDistance: 38.7, newDistance: 28.3, timeSaved: 18 },
    { route: 'Route 3', oldDistance: 52.1, newDistance: 39.4, timeSaved: 31 },
    { route: 'Route 4', oldDistance: 41.8, newDistance: 33.2, timeSaved: 22 },
    { route: 'Route 5', oldDistance: 47.5, newDistance: 35.8, timeSaved: 28 }
  ];

  const statusDistribution = [
    { name: 'Delivered', value: 450, color: '#22c55e' },
    { name: 'In Transit', value: 85, color: '#3b82f6' },
    { name: 'Pending', value: 32, color: '#f59e0b' },
    { name: 'Failed', value: 12, color: '#ef4444' }
  ];

  const liveTrackingData = [
    { id: 'ORD_001', driver: 'Rajesh Kumar', location: 'Bandra West', status: 'Out for Delivery', eta: '15 mins', progress: 85 },
    { id: 'ORD_002', driver: 'Priya Sharma', location: 'Andheri East', status: 'In Transit', eta: '32 mins', progress: 60 },
    { id: 'ORD_003', driver: 'Amit Singh', location: 'Churchgate', status: 'Delivered', eta: 'Completed', progress: 100 },
    { id: 'ORD_004', driver: 'Sneha Patel', location: 'Powai', status: 'Picked Up', eta: '45 mins', progress: 25 },
    { id: 'ORD_005', driver: 'Rohit Mehta', location: 'Worli', status: 'Out for Delivery', eta: '12 mins', progress: 90 }
  ];

  const MetricCard = ({ title, value, icon: Icon, trend, color = "blue" }) => (
    <Card className="relative overflow-hidden rounded-lg shadow-sm">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-gray-600">{title}</CardTitle>
        <Icon className={`h-4 w-4 text-${color}-600`} />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-gray-900">{value}</div>
        {trend && (
          <p className={`text-xs ${trend > 0 ? 'text-green-600' : 'text-red-600'} flex items-center mt-1`}>
            <TrendingUp className="h-3 w-3 mr-1" />
            {trend > 0 ? '+' : ''}{trend}% from last month
          </p>
        )}
      </CardContent>
    </Card>
  );

  const ProgressBar = ({ progress, color = "blue" }) => (
    <div className="w-full bg-gray-200 rounded-full h-2">
      <div 
        className={`bg-${color}-600 h-2 rounded-full transition-all duration-300`}
        style={{ width: `${progress}%` }}
      ></div>
    </div>
  );

  const StatusBadge = ({ status }) => {
    const colors = {
      'Delivered': 'bg-green-100 text-green-800',
      'Out for Delivery': 'bg-blue-100 text-blue-800',
      'In Transit': 'bg-yellow-100 text-yellow-800',
      'Picked Up': 'bg-purple-100 text-purple-800',
      'Failed': 'bg-red-100 text-red-800'
    };
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
        {status}
      </span>
    );
  };

  const TabButton = ({ id, label, isActive, onClick }) => (
    <button
      onClick={() => onClick(id)}
      className={`px-4 py-2 rounded-lg transition-colors duration-200 ${
        isActive 
          ? 'bg-blue-600 text-white shadow-md' 
          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
      }`}
    >
      {label}
    </button>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6 font-sans">
      <style>
        {`
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
          body {
            font-family: 'Inter', sans-serif;
          }
        `}
      </style>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Delivery Optimization Dashboard</h1>
          <p className="text-gray-600">Real-time monitoring and analytics for your delivery operations</p>
        </div>

        {/* Navigation Tabs */}
        <div className="flex space-x-2 mb-6">
          <TabButton id="overview" label="Overview" isActive={activeTab === 'overview'} onClick={setActiveTab} />
          <TabButton id="tracking" label="Live Tracking" isActive={activeTab === 'tracking'} onClick={setActiveTab} />
          <TabButton id="analytics" label="Analytics" isActive={activeTab === 'analytics'} onClick={setActiveTab} />
          <TabButton id="routes" label="Route Optimization" isActive={activeTab === 'routes'} onClick={setActiveTab} />
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <MetricCard 
                title="Total Orders Today" 
                value={deliveryMetrics.totalOrders || 185} 
                icon={Package}
                trend={12}
                color="blue"
              />
              <MetricCard 
                title="Delivered Orders" 
                value={deliveryMetrics.deliveredOrders || 142} 
                icon={CheckCircle}
                trend={8}
                color="green"
              />
              <MetricCard 
                title="Average Delivery Time" 
                value={`${deliveryMetrics.averageDeliveryTime || '2.3'} hrs`}
                icon={Clock}
                trend={-15}
                color="purple"
              />
              <MetricCard 
                title="On-Time Rate" 
                value={`${deliveryMetrics.onTimeDeliveryRate || '94.2'}%`}
                icon={TrendingUp}
                trend={6}
                color="indigo"
              />
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Performance Trend */}
              <Card className="rounded-lg shadow-sm">
                <CardHeader>
                  <CardTitle>Delivery Performance Trend</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="deliveries" stroke="#3b82f6" strokeWidth={2} name="Total Deliveries" />
                      <Line type="monotone" dataKey="onTime" stroke="#22c55e" strokeWidth={2} name="On-Time Deliveries" />
                      <Line type="monotone" dataKey="failed" stroke="#ef4444" strokeWidth={2} name="Failed Deliveries" />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Status Distribution */}
              <Card className="rounded-lg shadow-sm">
                <CardHeader>
                  <CardTitle>Order Status Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={statusDistribution}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={120}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {statusDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="flex flex-wrap justify-center mt-4 gap-4">
                    {statusDistribution.map((entry, index) => (
                      <div key={index} className="flex items-center">
                        <div 
                          className="w-3 h-3 rounded-full mr-2"
                          style={{ backgroundColor: entry.color }}
                        ></div>
                        <span className="text-sm text-gray-600">{entry.name}: {entry.value}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            <Card className="rounded-lg shadow-sm">
              <CardHeader>
                <CardTitle>Recent Delivery Updates</CardTitle>
                <div className="flex items-center text-sm text-gray-600">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                  Live updates every 30 seconds
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {liveTrackingData.slice(0, 5).map((order) => (
                    <div key={order.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                        <div>
                          <p className="font-medium text-gray-900">{order.id}</p>
                          <p className="text-sm text-gray-600">{order.driver} • {order.location}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <StatusBadge status={order.status} />
                        <span className="text-sm text-gray-600">{order.eta}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Live Tracking Tab */}
        {activeTab === 'tracking' && (
          <div className="space-y-6">
            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg shadow-sm">
                <div className="flex items-center">
                  <Truck className="h-8 w-8 text-blue-600 mr-3" />
                  <div>
                    <p className="text-sm text-blue-600">Active Vehicles</p>
                    <p className="text-2xl font-bold text-blue-800">12</p>
                  </div>
                </div>
              </div>
              <div className="bg-green-50 p-4 rounded-lg shadow-sm">
                <div className="flex items-center">
                  <MapPin className="h-8 w-8 text-green-600 mr-3" />
                  <div>
                    <p className="text-sm text-green-600">Out for Delivery</p>
                    <p className="text-2xl font-bold text-green-800">8</p>
                  </div>
                </div>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg shadow-sm">
                <div className="flex items-center">
                  <Clock className="h-8 w-8 text-yellow-600 mr-3" />
                  <div>
                    <p className="text-sm text-yellow-600">In Transit</p>
                    <p className="text-2xl font-bold text-yellow-800">15</p>
                  </div>
                </div>
              </div>
              <div className="bg-red-50 p-4 rounded-lg shadow-sm">
                <div className="flex items-center">
                  <AlertTriangle className="h-8 w-8 text-red-600 mr-3" />
                  <div>
                    <p className="text-sm text-red-600">Delays</p>
                    <p className="text-2xl font-bold text-red-800">3</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Live Tracking Table */}
            <Card className="rounded-lg shadow-sm">
              <CardHeader>
                <CardTitle>Real-time Order Tracking</CardTitle>
                <div className="flex items-center text-sm text-gray-600">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                  Live updates every 30 seconds
                </div>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-3 font-medium text-gray-600">Order ID</th>
                        <th className="text-left p-3 font-medium text-gray-600">Driver</th>
                        <th className="text-left p-3 font-medium text-gray-600">Current Location</th>
                        <th className="text-left p-3 font-medium text-gray-600">Status</th>
                        <th className="text-left p-3 font-medium text-gray-600">Progress</th>
                        <th className="text-left p-3 font-medium text-gray-600">ETA</th>
                      </tr>
                    </thead>
                    <tbody>
                      {liveTrackingData.map((order) => (
                        <tr key={order.id} className="border-b hover:bg-gray-50">
                          <td className="p-3 font-medium text-blue-600">{order.id}</td>
                          <td className="p-3">{order.driver}</td>
                          <td className="p-3">{order.location}</td>
                          <td className="p-3">
                            <StatusBadge status={order.status} />
                          </td>
                          <td className="p-3">
                            <div className="flex items-center space-x-2">
                              <ProgressBar progress={order.progress} />
                              <span className="text-sm text-gray-600">{order.progress}%</span>
                            </div>
                          </td>
                          <td className="p-3">{order.eta}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            {/* Key Performance Indicators */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <MetricCard 
                title="Customer Satisfaction" 
                value={`${deliveryMetrics.customerSatisfaction || '4.3'}/5.0`}
                icon={Users}
                trend={2.5}
                color="green"
              />
              <MetricCard 
                title="Cost per Delivery" 
                value="₹45.20"
                icon={TrendingUp}
                trend={-8.2}
                color="blue"
              />
              <MetricCard 
                title="Route Efficiency" 
                value="88.5%"
                icon={MapPin}
                trend={15.3}
                color="purple"
              />
            </div>

            {/* Detailed Analytics */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Route Efficiency Comparison */}
              <Card className="rounded-lg shadow-sm">
                <CardHeader>
                  <CardTitle>Route Optimization Results</CardTitle>
                  <p className="text-sm text-gray-600">Before vs After optimization</p>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={routeEfficiencyData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="route" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="oldDistance" fill="#ef4444" name="Old Distance (km)" />
                      <Bar dataKey="newDistance" fill="#22c55e" name="New Distance (km)" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Time Savings */}
              <Card className="rounded-lg shadow-sm">
                <CardHeader>
                  <CardTitle>Time Savings Analysis</CardTitle>
                  <p className="text-sm text-gray-600">Minutes saved per route</p>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {routeEfficiencyData.map((route, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <span className="font-medium">{route.route}</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-24 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-green-600 h-2 rounded-full"
                              style={{ width: `${(route.timeSaved / 35) * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium text-green-600">{route.timeSaved} min</span>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-6 p-4 bg-green-50 rounded-lg">
                    <p className="text-sm text-green-700">
                      <strong>Total Time Saved:</strong> 124 minutes/day
                    </p>
                    <p className="text-sm text-green-600 mt-1">
                      Equivalent to 2.07 hours of additional delivery capacity
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Performance Metrics */}
            <Card className="rounded-lg shadow-sm">
              <CardHeader>
                <CardTitle>Delivery Performance Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600 mb-2">94.2%</div>
                    <div className="text-sm text-gray-600">On-Time Delivery Rate</div>
                    <div className="text-xs text-green-600 mt-1">↑ 6.3% vs last month</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600 mb-2">2.3h</div>
                    <div className="text-sm text-gray-600">Avg Delivery Time</div>
                    <div className="text-xs text-green-600 mt-1">↓ 0.7h vs last month</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-purple-600 mb-2">₹45.20</div>
                    <div className="text-sm text-gray-600">Cost per Delivery</div>
                    <div className="text-xs text-green-600 mt-1">↓ ₹8.30 vs last month</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-orange-600 mb-2">4.3/5</div>
                    <div className="text-sm text-gray-600">Customer Rating</div>
                    <div className="text-xs text-green-600 mt-1">↑ 0.4 vs last month</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Route Optimization Tab */}
        {activeTab === 'routes' && (
          <div className="space-y-6">
            {/* Route Planning Interface */}
            <Card className="rounded-lg shadow-sm">
              <CardHeader>
                <CardTitle>Route Planning & Optimization</CardTitle>
                <p className="text-sm text-gray-600">Create and optimize delivery routes</p>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-medium mb-4 text-gray-800">Route Configuration</h3>
                    <div className="space-y-4">
                      <div>
                        <label htmlFor="vehicle-select" className="block text-sm font-medium text-gray-700 mb-2">Vehicle Selection</label>
                        <select 
                          id="vehicle-select"
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                          value={selectedVehicle}
                          onChange={(e) => {
                            setSelectedVehicle(e.target.value);
                            generateRoute(e.target.value); // Update route immediately on change
                          }}
                        >
                          {vehicles.map(vehicle => (
                            <option key={vehicle.id} value={vehicle.id}>
                              {vehicle.id} - {vehicle.name} ({vehicle.capacity})
                            </option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Optimization Priorities</label>
                        <div className="space-y-2">
                          <label className="flex items-center text-gray-700">
                            <input type="checkbox" className="mr-2 rounded text-blue-600 focus:ring-blue-500" defaultChecked />
                            <span className="text-sm">Include urgent deliveries first</span>
                          </label>
                          <label className="flex items-center text-gray-700">
                            <input type="checkbox" className="mr-2 rounded text-blue-600 focus:ring-blue-500" defaultChecked />
                            <span className="text-sm">Optimize for shortest distance</span>
                          </label>
                          <label className="flex items-center text-gray-700">
                            <input type="checkbox" className="mr-2 rounded text-blue-600 focus:ring-blue-500" />
                            <span className="text-sm">Consider traffic patterns</span>
                          </label>
                        </div>
                      </div>
                      {/* Removed the "Generate Optimized Route" button */}
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-medium mb-4 text-gray-800">Route Preview</h3>
                    <div className="border border-gray-200 rounded-lg p-4 bg-gray-50 shadow-inner">
                      <div className="space-y-3">
                        {optimizedRouteData.route && optimizedRouteData.route.length > 0 ? (
                          optimizedRouteData.route.map((stop, index) => (
                            <div key={index} className="flex items-center justify-between text-sm">
                              <span>{stop.stop}</span>
                              <span className="text-gray-500">{stop.time}</span>
                            </div>
                          ))
                        ) : (
                          <p className="text-gray-500 text-center py-4">Select a vehicle and generate a route.</p>
                        )}
                      </div>
                      
                      {optimizedRouteData.route && optimizedRouteData.route.length > 0 && (
                        <div className="mt-4 pt-4 border-t border-gray-200">
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="text-gray-600">Total Distance:</span>
                              <span className="font-medium ml-2">{optimizedRouteData.totalDistance} km</span>
                            </div>
                            <div>
                              <span className="text-gray-600">Est. Time:</span>
                              <span className="font-medium ml-2">{optimizedRouteData.estimatedTime} hours</span>
                            </div>
                            <div>
                              <span className="text-gray-600">Fuel Cost:</span>
                              <span className="font-medium ml-2">₹{optimizedRouteData.fuelCost}</span>
                            </div>
                            <div>
                              <span className="text-gray-600">Deliveries:</span>
                              <span className="font-medium ml-2">{optimizedRouteData.deliveries} orders</span>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Smart Packing Suggestions */}
            <Card className="rounded-lg shadow-sm">
              <CardHeader>
                <CardTitle>Smart Packing Recommendations</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium mb-3 text-gray-800">Loading Sequence</h4>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between p-2 bg-red-50 rounded-md">
                        <span className="text-sm text-gray-700">ORD_002 (Heavy items)</span>
                        <span className="text-xs text-red-600 font-semibold">Load first - Back</span>
                      </div>
                      <div className="flex items-center justify-between p-2 bg-yellow-50 rounded-md">
                        <span className="text-sm text-gray-700">ORD_003 (Medium items)</span>
                        <span className="text-xs text-yellow-600 font-semibold">Load second - Middle</span>
                      </div>
                      <div className="flex items-center justify-between p-2 bg-green-50 rounded-md">
                        <span className="text-sm text-gray-700">ORD_001 (Light/Fragile)</span>
                        <span className="text-xs text-green-600 font-semibold">Load last - Front</span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium mb-3 text-gray-800">Special Instructions</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-start">
                        <AlertTriangle className="h-4 w-4 text-yellow-500 mr-2 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700">ORD_001 contains fragile items - handle with care</span>
                      </div>
                      <div className="flex items-start">
                        <Clock className="h-4 w-4 text-blue-500 mr-2 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700">ORD_002 has tight delivery window (9:00-10:00 AM)</span>
                      </div>
                      <div className="flex items-start">
                        <Package className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700">All packages fit within vehicle capacity</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Route Efficiency Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="rounded-lg shadow-sm">
                <CardContent className="p-6">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600 mb-2">35%</div>
                    <div className="text-sm text-gray-600">Distance Reduction</div>
                    <div className="text-xs text-gray-500 mt-1">vs manual routing</div>
                  </div>
                </CardContent>
              </Card>
              <Card className="rounded-lg shadow-sm">
                <CardContent className="p-6">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600 mb-2">2.1h</div>
                    <div className="text-sm text-gray-600">Time Saved Daily</div>
                    <div className="text-xs text-gray-500 mt-1">per vehicle</div>
                  </div>
                </CardContent>
              </Card>
              <Card className="rounded-lg shadow-sm">
                <CardContent className="p-6">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600 mb-2">₹1,250</div>
                    <div className="text-sm text-gray-600">Daily Fuel Savings</div>
                    <div className="text-xs text-gray-500 mt-1">across all routes</div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DeliveryOptimizationDashboard;
