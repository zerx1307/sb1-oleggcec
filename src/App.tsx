import React, { useState } from 'react';
import { Bot, MessageSquare, Network, BarChart3, Settings, Search } from 'lucide-react';
import ChatInterface from './components/ChatInterface';
import KnowledgeGraph from './components/KnowledgeGraph';
import Dashboard from './components/Dashboard';
import ContentManager from './components/ContentManager';

function App() {
  const [activeTab, setActiveTab] = useState('chat');

  const tabs = [
    { id: 'chat', label: 'Chat Bot', icon: MessageSquare },
    { id: 'knowledge', label: 'Knowledge Graph', icon: Network },
    { id: 'dashboard', label: 'Analytics', icon: BarChart3 },
    { id: 'content', label: 'Content Manager', icon: Settings },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'chat':
        return <ChatInterface />;
      case 'knowledge':
        return <KnowledgeGraph />;
      case 'dashboard':
        return <Dashboard />;
      case 'content':
        return <ContentManager />;
      default:
        return <ChatInterface />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800">
      {/* Header */}
      <header className="bg-white/10 backdrop-blur-md border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-blue-500 to-teal-500 p-2 rounded-lg">
                <Bot className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">MOSDAC AI Assistant</h1>
                <p className="text-sm text-blue-200">Intelligent Knowledge Retrieval System</p>
              </div>
            </div>
            <div className="hidden md:flex items-center space-x-2">
              <Search className="h-4 w-4 text-blue-300" />
              <span className="text-sm text-blue-200">Powered by Knowledge Graph & NLP</span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white/5 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8 overflow-x-auto">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                    activeTab === tab.id
                      ? 'border-blue-400 text-blue-300'
                      : 'border-transparent text-blue-200 hover:text-blue-100 hover:border-blue-300'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderContent()}
      </main>
    </div>
  );
}

export default App;