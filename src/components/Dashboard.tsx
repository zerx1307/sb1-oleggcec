import React from 'react';
import { TrendingUp, Users, MessageSquare, Database, Clock, CheckCircle, AlertCircle, Search } from 'lucide-react';

const Dashboard: React.FC = () => {
  const stats = [
    { label: 'Total Queries', value: '12,847', change: '+23%', icon: MessageSquare, color: 'bg-blue-500' },
    { label: 'Active Users', value: '1,429', change: '+12%', icon: Users, color: 'bg-green-500' },
    { label: 'Knowledge Entities', value: '8,596', change: '+8%', icon: Database, color: 'bg-purple-500' },
    { label: 'Avg Response Time', value: '1.2s', change: '-15%', icon: Clock, color: 'bg-orange-500' },
  ];

  const queryTypes = [
    { type: 'Product Information', count: 3240, percentage: 35, color: 'bg-blue-400' },
    { type: 'Download Procedures', count: 2187, percentage: 24, color: 'bg-green-400' },
    { type: 'Technical Support', count: 1854, percentage: 20, color: 'bg-purple-400' },
    { type: 'Geospatial Queries', count: 1236, percentage: 13, color: 'bg-orange-400' },
    { type: 'Documentation', count: 730, percentage: 8, color: 'bg-pink-400' },
  ];

  const recentQueries = [
    {
      id: 1,
      query: "How to download INSAT-3D imager data for India region?",
      intent: "data_download",
      confidence: 0.94,
      status: "resolved",
      timestamp: "2 minutes ago"
    },
    {
      id: 2,
      query: "What is the spatial resolution of Oceansat-2 OCM data?",
      intent: "product_specification",
      confidence: 0.87,
      status: "resolved",
      timestamp: "5 minutes ago"
    },
    {
      id: 3,
      query: "API documentation for bulk data access",
      intent: "technical_documentation",
      confidence: 0.91,
      status: "resolved",
      timestamp: "8 minutes ago"
    },
    {
      id: 4,
      query: "Scatterometer wind speed data processing algorithms",
      intent: "technical_details",
      confidence: 0.78,
      status: "partial",
      timestamp: "12 minutes ago"
    },
    {
      id: 5,
      query: "Coverage area for SCATSAT-1 mission",
      intent: "mission_information",
      confidence: 0.92,
      status: "resolved",
      timestamp: "15 minutes ago"
    }
  ];

  const entityExtractionStats = [
    { entity: 'Satellite Missions', count: 847, accuracy: 96.2 },
    { entity: 'Data Products', count: 1234, accuracy: 94.8 },
    { entity: 'Geographic Locations', count: 623, accuracy: 91.5 },
    { entity: 'Technical Terms', count: 2156, accuracy: 89.3 },
    { entity: 'Time Ranges', count: 456, accuracy: 93.7 },
  ];

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-200 text-sm">{stat.label}</p>
                  <p className="text-2xl font-bold text-white mt-1">{stat.value}</p>
                  <p className={`text-sm mt-1 ${stat.change.startsWith('+') ? 'text-green-400' : 'text-red-400'}`}>
                    {stat.change} from last month
                  </p>
                </div>
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Query Types Distribution */}
        <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6">
          <h3 className="text-xl font-semibold text-white mb-6">Query Types Distribution</h3>
          <div className="space-y-4">
            {queryTypes.map((type, index) => (
              <div key={index} className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-blue-200">{type.type}</span>
                  <span className="text-white font-medium">{type.count}</span>
                </div>
                <div className="w-full bg-white/20 rounded-full h-2">
                  <div
                    className={`${type.color} h-2 rounded-full transition-all duration-300`}
                    style={{ width: `${type.percentage}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Entity Recognition Accuracy */}
        <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6">
          <h3 className="text-xl font-semibold text-white mb-6">Entity Recognition Performance</h3>
          <div className="space-y-4">
            {entityExtractionStats.map((entity, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-blue-200">{entity.entity}</span>
                    <span className="text-white font-medium">{entity.accuracy}%</span>
                  </div>
                  <div className="w-full bg-white/20 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-green-500 to-teal-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${entity.accuracy}%` }}
                    ></div>
                  </div>
                  <div className="text-xs text-blue-300 mt-1">{entity.count} entities recognized</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Queries */}
      <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-white">Recent Queries</h3>
          <div className="flex items-center space-x-2">
            <Search className="h-4 w-4 text-blue-300" />
            <span className="text-sm text-blue-200">Live Feed</span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/20">
                <th className="text-left text-blue-200 font-medium py-3">Query</th>
                <th className="text-left text-blue-200 font-medium py-3">Intent</th>
                <th className="text-left text-blue-200 font-medium py-3">Confidence</th>
                <th className="text-left text-blue-200 font-medium py-3">Status</th>
                <th className="text-left text-blue-200 font-medium py-3">Time</th>
              </tr>
            </thead>
            <tbody>
              {recentQueries.map((query) => (
                <tr key={query.id} className="border-b border-white/10 hover:bg-white/5 transition-colors duration-200">
                  <td className="py-3 text-white max-w-xs truncate">{query.query}</td>
                  <td className="py-3 text-blue-200 text-sm">{query.intent}</td>
                  <td className="py-3">
                    <div className="flex items-center space-x-2">
                      <div className="w-12 bg-white/20 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            query.confidence > 0.9 ? 'bg-green-500' : 
                            query.confidence > 0.8 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${query.confidence * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-white text-sm">{Math.round(query.confidence * 100)}%</span>
                    </div>
                  </td>
                  <td className="py-3">
                    <div className="flex items-center space-x-2">
                      {query.status === 'resolved' ? (
                        <CheckCircle className="h-4 w-4 text-green-400" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-yellow-400" />
                      )}
                      <span className={`text-sm capitalize ${
                        query.status === 'resolved' ? 'text-green-400' : 'text-yellow-400'
                      }`}>
                        {query.status}
                      </span>
                    </div>
                  </td>
                  <td className="py-3 text-blue-200 text-sm">{query.timestamp}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;