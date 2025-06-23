import React, { useState } from 'react';
import { Upload, FileText, Database, Globe, RefreshCw, CheckCircle, AlertTriangle, Plus, Search, Filter } from 'lucide-react';

interface ContentItem {
  id: string;
  title: string;
  type: 'document' | 'webpage' | 'faq' | 'api';
  status: 'processed' | 'processing' | 'error' | 'pending';
  lastUpdated: string;
  entities: number;
  relationships: number;
  source: string;
}

const ContentManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  const contentItems: ContentItem[] = [
    {
      id: '1',
      title: 'INSAT-3D User Manual',
      type: 'document',
      status: 'processed',
      lastUpdated: '2024-01-15',
      entities: 247,
      relationships: 89,
      source: '/docs/insat3d_manual.pdf'
    },
    {
      id: '2',
      title: 'MOSDAC FAQ Database',
      type: 'faq',
      status: 'processed',
      lastUpdated: '2024-01-14',
      entities: 156,
      relationships: 203,
      source: '/faq/index.html'
    },
    {
      id: '3',
      title: 'API Documentation',
      type: 'api',
      status: 'processing',
      lastUpdated: '2024-01-16',
      entities: 89,
      relationships: 45,
      source: '/api/docs'
    },
    {
      id: '4',
      title: 'Product Catalog Pages',
      type: 'webpage',
      status: 'processed',
      lastUpdated: '2024-01-13',
      entities: 342,
      relationships: 156,
      source: '/catalog/*'
    },
    {
      id: '5',
      title: 'Mission Overview Documents',
      type: 'document',
      status: 'error',
      lastUpdated: '2024-01-12',
      entities: 0,
      relationships: 0,
      source: '/missions/overview.docx'
    }
  ];

  const processingStats = {
    totalItems: 247,
    processed: 189,
    processing: 12,
    errors: 6,
    pending: 40,
    totalEntities: 12847,
    totalRelationships: 8596
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'processed':
        return <CheckCircle className="h-4 w-4 text-green-400" />;
      case 'processing':
        return <RefreshCw className="h-4 w-4 text-blue-400 animate-spin" />;
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-400" />;
      default:
        return <FileText className="h-4 w-4 text-gray-400" />;
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'document':
        return <FileText className="h-4 w-4" />;
      case 'webpage':
        return <Globe className="h-4 w-4" />;
      case 'faq':
        return <Database className="h-4 w-4" />;
      case 'api':
        return <Upload className="h-4 w-4" />;
      default:
        return <FileText className="h-4 w-4" />;
    }
  };

  const filteredItems = contentItems.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.source.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || item.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Processing Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-200 text-sm">Total Content</p>
              <p className="text-2xl font-bold text-white mt-1">{processingStats.totalItems}</p>
            </div>
            <Database className="h-8 w-8 text-blue-400" />
          </div>
        </div>
        
        <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-200 text-sm">Processed</p>
              <p className="text-2xl font-bold text-white mt-1">{processingStats.processed}</p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-400" />
          </div>
        </div>
        
        <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-200 text-sm">Entities</p>
              <p className="text-2xl font-bold text-white mt-1">{processingStats.totalEntities.toLocaleString()}</p>
            </div>
            <Globe className="h-8 w-8 text-purple-400" />
          </div>
        </div>
        
        <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-200 text-sm">Relationships</p>
              <p className="text-2xl font-bold text-white mt-1">{processingStats.totalRelationships.toLocaleString()}</p>
            </div>
            <RefreshCw className="h-8 w-8 text-orange-400" />
          </div>
        </div>
      </div>

      {/* Processing Status Chart */}
      <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6">
        <h3 className="text-xl font-semibold text-white mb-6">Content Processing Status</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <CheckCircle className="h-5 w-5 text-green-400" />
              <span className="text-white">Processed</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-32 bg-white/20 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full"
                  style={{ width: `${(processingStats.processed / processingStats.totalItems) * 100}%` }}
                ></div>
              </div>
              <span className="text-white font-medium w-12 text-right">{processingStats.processed}</span>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <RefreshCw className="h-5 w-5 text-blue-400" />
              <span className="text-white">Processing</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-32 bg-white/20 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full"
                  style={{ width: `${(processingStats.processing / processingStats.totalItems) * 100}%` }}
                ></div>
              </div>
              <span className="text-white font-medium w-12 text-right">{processingStats.processing}</span>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <AlertTriangle className="h-5 w-5 text-red-400" />
              <span className="text-white">Errors</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-32 bg-white/20 rounded-full h-2">
                <div
                  className="bg-red-500 h-2 rounded-full"
                  style={{ width: `${(processingStats.errors / processingStats.totalItems) * 100}%` }}
                ></div>
              </div>
              <span className="text-white font-medium w-12 text-right">{processingStats.errors}</span>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <FileText className="h-5 w-5 text-gray-400" />
              <span className="text-white">Pending</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-32 bg-white/20 rounded-full h-2">
                <div
                  className="bg-gray-500 h-2 rounded-full"
                  style={{ width: `${(processingStats.pending / processingStats.totalItems) * 100}%` }}
                ></div>
              </div>
              <span className="text-white font-medium w-12 text-right">{processingStats.pending}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderContentList = () => (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div className="flex items-center space-x-4">
          <div className="relative">
            <Search className="h-4 w-4 text-blue-300 absolute left-3 top-1/2 transform -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search content..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-white/20 border border-white/30 rounded-lg pl-10 pr-4 py-2 text-white placeholder-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>
          
          <div className="relative">
            <Filter className="h-4 w-4 text-blue-300 absolute left-3 top-1/2 transform -translate-y-1/2" />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="bg-white/20 border border-white/30 rounded-lg pl-10 pr-8 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-400 appearance-none"
            >
              <option value="all">All Status</option>
              <option value="processed">Processed</option>
              <option value="processing">Processing</option>
              <option value="error">Error</option>
              <option value="pending">Pending</option>
            </select>
          </div>
        </div>

        <button className="bg-gradient-to-r from-blue-500 to-teal-500 text-white px-4 py-2 rounded-lg hover:from-blue-600 hover:to-teal-600 transition-colors duration-200 flex items-center space-x-2">
          <Plus className="h-4 w-4" />
          <span>Add Content</span>
        </button>
      </div>

      {/* Content Table */}
      <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/20 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-white/10">
              <tr>
                <th className="text-left text-blue-200 font-medium py-4 px-6">Content</th>
                <th className="text-left text-blue-200 font-medium py-4 px-6">Type</th>
                <th className="text-left text-blue-200 font-medium py-4 px-6">Status</th>
                <th className="text-left text-blue-200 font-medium py-4 px-6">Entities</th>
                <th className="text-left text-blue-200 font-medium py-4 px-6">Relations</th>
                <th className="text-left text-blue-200 font-medium py-4 px-6">Updated</th>
              </tr>
            </thead>
            <tbody>
              {filteredItems.map((item) => (
                <tr key={item.id} className="border-b border-white/10 hover:bg-white/5 transition-colors duration-200">
                  <td className="py-4 px-6">
                    <div>
                      <div className="text-white font-medium">{item.title}</div>
                      <div className="text-blue-200 text-sm">{item.source}</div>
                    </div>
                  </td>
                  <td className="py-4 px-6">
                    <div className="flex items-center space-x-2">
                      {getTypeIcon(item.type)}
                      <span className="text-blue-200 capitalize">{item.type}</span>
                    </div>
                  </td>
                  <td className="py-4 px-6">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(item.status)}
                      <span className={`capitalize text-sm ${
                        item.status === 'processed' ? 'text-green-400' :
                        item.status === 'processing' ? 'text-blue-400' :
                        item.status === 'error' ? 'text-red-400' : 'text-gray-400'
                      }`}>
                        {item.status}
                      </span>
                    </div>
                  </td>
                  <td className="py-4 px-6 text-white font-medium">{item.entities}</td>
                  <td className="py-4 px-6 text-white font-medium">{item.relationships}</td>
                  <td className="py-4 px-6 text-blue-200">{item.lastUpdated}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-white/10 backdrop-blur-md rounded-lg p-1">
        <button
          onClick={() => setActiveTab('overview')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors duration-200 ${
            activeTab === 'overview'
              ? 'bg-blue-500 text-white'
              : 'text-blue-200 hover:text-white hover:bg-white/10'
          }`}
        >
          Overview
        </button>
        <button
          onClick={() => setActiveTab('content')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors duration-200 ${
            activeTab === 'content'
              ? 'bg-blue-500 text-white'
              : 'text-blue-200 hover:text-white hover:bg-white/10'
          }`}
        >
          Content Items
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' ? renderOverview() : renderContentList()}
    </div>
  );
};

export default ContentManager;