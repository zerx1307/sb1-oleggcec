import React, { useState, useEffect } from 'react';
import { Network, Satellite, Database, FileText, MapPin, Users, Zap, Search } from 'lucide-react';

interface Node {
  id: string;
  label: string;
  type: 'mission' | 'product' | 'document' | 'location' | 'user' | 'process';
  x: number;
  y: number;
  connections: string[];
  metadata: any;
}

interface Edge {
  from: string;
  to: string;
  label: string;
  type: 'provides' | 'contains' | 'processes' | 'accesses' | 'related';
}

const KnowledgeGraph: React.FC = () => {
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredNodes, setFilteredNodes] = useState<Node[]>([]);

  const nodes: Node[] = [
    {
      id: 'insat3d',
      label: 'INSAT-3D',
      type: 'mission',
      x: 200,
      y: 150,
      connections: ['imager_data', 'sounder_data', 'meteorology'],
      metadata: { launch: '2013', status: 'Active', orbit: 'Geostationary' }
    },
    {
      id: 'scatsat1',
      label: 'SCATSAT-1',  
      type: 'mission',
      x: 400,
      y: 100,
      connections: ['scatterometer_data', 'ocean_winds', 'weather'],
      metadata: { launch: '2016', status: 'Active', orbit: 'Polar' }
    },
    {
      id: 'oceansat2',
      label: 'Oceansat-2',
      type: 'mission',
      x: 600,
      y: 180,
      connections: ['ocm_data', 'ocean_color', 'coastal_monitoring'],
      metadata: { launch: '2009', status: 'Active', orbit: 'Sun-synchronous' }
    },
    {
      id: 'imager_data',
      label: 'Imager Data',
      type: 'product',
      x: 150,
      y: 300,
      connections: ['meteorology', 'weather_forecasting'],
      metadata: { resolution: '1km-4km', bands: '6 channels', format: 'HDF5' }
    },
    {
      id: 'scatterometer_data',
      label: 'Scatterometer Data',
      type: 'product',
      x: 400,
      y: 280,
      connections: ['ocean_winds', 'weather'],
      metadata: { resolution: '25km', swath: '1400km', format: 'NetCDF' }
    },
    {
      id: 'ocm_data',
      label: 'OCM Data',
      type: 'product',
      x: 650,
      y: 320,
      connections: ['ocean_color', 'coastal_monitoring'],
      metadata: { resolution: '360m', bands: '8 channels', format: 'HDF4' }
    },
    {
      id: 'user_manual',
      label: 'User Manual',
      type: 'document',
      x: 100,
      y: 450,
      connections: ['imager_data', 'data_processing'],
      metadata: { pages: 156, version: '2.1', format: 'PDF' }
    },
    {
      id: 'api_doc',
      label: 'API Documentation',
      type: 'document',
      x: 300,
      y: 480,
      connections: ['data_access', 'developers'],
      metadata: { endpoints: 12, version: '1.3', format: 'HTML' }
    },
    {
      id: 'faq',
      label: 'FAQ Database',
      type: 'document',
      x: 500,
      y: 450,
      connections: ['user_support', 'common_issues'],
      metadata: { questions: 247, categories: 8, updated: '2024-01-15' }
    },
    {
      id: 'indian_ocean',
      label: 'Indian Ocean',
      type: 'location',
      x: 750,
      y: 400,
      connections: ['oceansat2', 'scatsat1'],
      metadata: { area: '70.6M km²', coverage: 'Full', sensors: ['OCM', 'Scatterometer'] }
    }
  ];

  const edges: Edge[] = [
    { from: 'insat3d', to: 'imager_data', label: 'generates', type: 'provides' },
    { from: 'scatsat1', to: 'scatterometer_data', label: 'produces', type: 'provides' },
    { from: 'oceansat2', to: 'ocm_data', label: 'captures', type: 'provides' },
    { from: 'imager_data', to: 'user_manual', label: 'documented in', type: 'contains' },
    { from: 'scatterometer_data', to: 'api_doc', label: 'accessible via', type: 'accesses' },
    { from: 'ocm_data', to: 'indian_ocean', label: 'covers', type: 'related' },
    { from: 'scatsat1', to: 'indian_ocean', label: 'monitors', type: 'related' }
  ];

  useEffect(() => {
    const filtered = nodes.filter(node =>
      node.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
      node.type.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredNodes(filtered);
  }, [searchTerm]);

  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'mission': return <Satellite className="h-4 w-4" />;
      case 'product': return <Database className="h-4 w-4" />;
      case 'document': return <FileText className="h-4 w-4" />;
      case 'location': return <MapPin className="h-4 w-4" />;
      case 'user': return <Users className="h-4 w-4" />;
      case 'process': return <Zap className="h-4 w-4" />;
      default: return <Network className="h-4 w-4" />;
    }
  };

  const getNodeColor = (type: string) => {
    switch (type) {
      case 'mission': return 'bg-blue-500 border-blue-400';
      case 'product': return 'bg-green-500 border-green-400';
      case 'document': return 'bg-orange-500 border-orange-400';
      case 'location': return 'bg-purple-500 border-purple-400';
      case 'user': return 'bg-pink-500 border-pink-400';
      case 'process': return 'bg-yellow-500 border-yellow-400';
      default: return 'bg-gray-500 border-gray-400';
    }
  };

  const renderEdges = () => {
    return edges.map((edge, index) => {
      const fromNode = nodes.find(n => n.id === edge.from);
      const toNode = nodes.find(n => n.id === edge.to);
      if (!fromNode || !toNode) return null;

      return (
        <line
          key={index}
          x1={fromNode.x + 40}
          y1={fromNode.y + 40}
          x2={toNode.x + 40}
          y2={toNode.y + 40}
          stroke="rgba(59, 130, 246, 0.3)"
          strokeWidth="2"
          strokeDasharray={edge.type === 'related' ? '5,5' : 'none'}
        />
      );
    });
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-200px)]">
      {/* Graph Visualization */}
      <div className="lg:col-span-2 bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-white">Knowledge Graph Visualization</h3>
          <div className="flex items-center space-x-2">
            <Search className="h-4 w-4 text-blue-300" />
            <input
              type="text"
              placeholder="Search nodes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-white/20 border border-white/30 rounded-lg px-3 py-1 text-sm text-white placeholder-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>
        </div>

        <div className="relative h-full bg-slate-900/50 rounded-lg overflow-hidden">
          <svg className="w-full h-full" viewBox="0 0 800 600">
            {/* Render edges first (behind nodes) */}
            {renderEdges()}
            
            {/* Render nodes */}
            {(searchTerm ? filteredNodes : nodes).map((node) => (
              <g key={node.id}>
                <circle
                  cx={node.x + 40}
                  cy={node.y + 40}
                  r="35"
                  className={`${getNodeColor(node.type)} opacity-80 hover:opacity-100 cursor-pointer transition-opacity duration-200`}
                  onClick={() => setSelectedNode(node)}
                />
                <foreignObject x={node.x + 25} y={node.y + 25} width="30" height="30">
                  <div className="flex items-center justify-center w-full h-full text-white">
                    {getNodeIcon(node.type)}
                  </div>
                </foreignObject>
                <text
                  x={node.x + 40}
                  y={node.y + 100}
                  textAnchor="middle"
                  className="fill-white text-xs font-medium"
                >
                  {node.label}
                </text>
              </g>
            ))}
          </svg>

          {/* Legend */}
          <div className="absolute bottom-4 left-4 bg-black/50 backdrop-blur-sm rounded-lg p-3">
            <h4 className="text-sm font-semibold text-white mb-2">Node Types</h4>
            <div className="space-y-1 text-xs">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span className="text-blue-200">Missions</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-green-200">Products</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                <span className="text-orange-200">Documents</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                <span className="text-purple-200">Locations</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Node Details Panel */}
      <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6">
        <h3 className="text-xl font-semibold text-white mb-6">Node Details</h3>
        
        {selectedNode ? (
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className={`p-3 rounded-lg ${getNodeColor(selectedNode.type)}`}>
                {getNodeIcon(selectedNode.type)}
              </div>
              <div>
                <h4 className="font-semibold text-white">{selectedNode.label}</h4>
                <p className="text-sm text-blue-200 capitalize">{selectedNode.type}</p>
              </div>
            </div>

            <div className="bg-white/10 rounded-lg p-4">
              <h5 className="font-medium text-white mb-3">Metadata</h5>
              <div className="space-y-2 text-sm">
                {Object.entries(selectedNode.metadata).map(([key, value]) => (
                  <div key={key} className="flex justify-between">
                    <span className="text-blue-200 capitalize">{key.replace('_', ' ')}:</span>
                    <span className="text-white font-medium">{value}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white/10 rounded-lg p-4">
              <h5 className="font-medium text-white mb-3">Connections</h5>
              <div className="space-y-2">
                {selectedNode.connections.map((connectionId, index) => {
                  const connectedNode = nodes.find(n => n.id === connectionId);
                  return (
                    <div key={index} className="flex items-center space-x-2">
                      <div className={`w-2 h-2 rounded-full ${connectedNode ? getNodeColor(connectedNode.type).split(' ')[0] : 'bg-gray-500'}`}></div>
                      <span className="text-blue-200 text-sm">
                        {connectedNode ? connectedNode.label : connectionId}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="bg-white/10 rounded-lg p-4">
              <h5 className="font-medium text-white mb-3">Relationships</h5>
              <div className="space-y-2 text-sm">
                {edges
                  .filter(edge => edge.from === selectedNode.id || edge.to === selectedNode.id)
                  .map((edge, index) => (
                    <div key={index} className="text-blue-200">
                      <span className="capitalize">{edge.type}</span>: {edge.label}
                    </div>
                  ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center text-blue-200">
            <Network className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Click on a node in the graph to view its details and relationships.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default KnowledgeGraph;