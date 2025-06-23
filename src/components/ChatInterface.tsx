import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, FileText, MapPin, Database } from 'lucide-react';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  type?: 'text' | 'query_analysis' | 'geospatial' | 'document';
  metadata?: any;
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Hello! I\'m your MOSDAC AI Assistant. I can help you find information about satellite data, products, documentation, and services. What would you like to know?',
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const simulateAIResponse = (userQuery: string): Message => {
    const query = userQuery.toLowerCase();
    
    // Simulate different types of responses based on query content
    if (query.includes('satellite') || query.includes('data')) {
      return {
        id: Date.now().toString(),
        content: `Based on our knowledge graph analysis, I found several satellite data products relevant to your query. MOSDAC hosts data from multiple missions including INSAT-3D, SCATSAT-1, and Oceansat-2. Here are the key products:

• **INSAT-3D Imager Data**: High-resolution meteorological imagery
• **SCATSAT-1 Scatterometer**: Ocean wind vector data
• **Oceansat-2 OCM**: Ocean color and coastal zone monitoring

Would you like specific information about any of these products, including download procedures or technical specifications?`,
        sender: 'bot',
        timestamp: new Date(),
        type: 'query_analysis',
        metadata: {
          entities: ['INSAT-3D', 'SCATSAT-1', 'Oceansat-2'],
          intent: 'product_inquiry',
          confidence: 0.92
        }
      };
    } else if (query.includes('download') || query.includes('access')) {
      return {
        id: Date.now().toString(),
        content: `To download data from MOSDAC, you'll need to follow these steps:

1. **Registration**: Create an account on the MOSDAC portal
2. **Data Search**: Use the catalog to find your required datasets
3. **Request Submission**: Submit a data request with your requirements
4. **Approval Process**: Wait for approval (usually 24-48 hours)
5. **Download**: Access your approved data through the user dashboard

For bulk downloads or automated access, you can use our API services. Would you like me to provide the API documentation or help with a specific data request?`,
        sender: 'bot',
        timestamp: new Date(),
        type: 'document',
        metadata: {
          procedure: 'data_download',
          steps: 5
        }
      };
    } else if (query.includes('location') || query.includes('area') || query.includes('region')) {
      return {
        id: Date.now().toString(),
        content: `I can help you find satellite data for specific geographical locations. Our geospatial intelligence system can identify relevant datasets based on:

🗺️ **Spatial Coverage**: Data available for your area of interest
📊 **Temporal Range**: Time series data availability
🛰️ **Sensor Types**: Optical, radar, and microwave sensors
🎯 **Resolution**: From 1km to 25m spatial resolution

Please provide your area of interest (coordinates, place name, or region) and I'll identify the most suitable datasets and their availability.`,
        sender: 'bot',
        timestamp: new Date(),
        type: 'geospatial',
        metadata: {
          spatialQuery: true,
          availableSensors: ['OCM', 'Scatterometer', 'Imager']
        }
      };
    } else {
      return {
        id: Date.now().toString(),
        content: `I understand you're looking for information about "${userQuery}". Let me search through our comprehensive knowledge base covering:

• **Product Documentation**: Technical specifications and user guides
• **FAQ Database**: Common questions and solutions
• **Mission Information**: Satellite mission details and objectives
• **Data Processing**: Algorithms and processing levels
• **Support Materials**: Tutorials and training resources

Could you please provide more specific details about what you're looking for? This will help me give you more targeted information.`,
        sender: 'bot',
        timestamp: new Date(),
        metadata: {
          generalQuery: true,
          searchAreas: ['documentation', 'faq', 'missions', 'support']
        }
      };
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate AI processing time
    setTimeout(() => {
      const botResponse = simulateAIResponse(inputValue);
      setMessages(prev => [...prev, botResponse]);
      setIsTyping(false);
    }, 1500);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getMessageIcon = (message: Message) => {
    if (message.sender === 'user') return <User className="h-5 w-5" />;
    
    switch (message.type) {
      case 'query_analysis':
        return <Sparkles className="h-5 w-5" />;
      case 'geospatial':
        return <MapPin className="h-5 w-5" />;
      case 'document':
        return <FileText className="h-5 w-5" />;
      default:
        return <Bot className="h-5 w-5" />;
    }
  };

  const getMessageBgColor = (message: Message) => {
    if (message.sender === 'user') return 'bg-blue-600';
    
    switch (message.type) {
      case 'query_analysis':
        return 'bg-purple-600';
      case 'geospatial':
        return 'bg-green-600';
      case 'document':
        return 'bg-orange-600';
      default:
        return 'bg-teal-600';
    }
  };

  return (
    <div className="bg-white/10 backdrop-blur-md rounded-xl border border-white/20 h-[calc(100vh-200px)] flex flex-col">
      {/* Chat Header */}
      <div className="p-4 border-b border-white/20">
        <div className="flex items-center space-x-3">
          <div className="bg-gradient-to-r from-teal-500 to-blue-500 p-2 rounded-lg">
            <Bot className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-white">AI Assistant</h3>
            <p className="text-sm text-blue-200">Online • Knowledge Graph Active</p>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`flex items-start space-x-3 max-w-3xl ${message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
              <div className={`p-2 rounded-lg ${getMessageBgColor(message)}`}>
                {getMessageIcon(message)}
              </div>
              <div className={`p-4 rounded-lg ${
                message.sender === 'user' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-white/20 text-white'
              }`}>
                <div className="whitespace-pre-wrap">{message.content}</div>
                {message.metadata && (
                  <div className="mt-3 pt-3 border-t border-white/20">
                    <div className="text-xs opacity-75">
                      {message.metadata.entities && (
                        <div>Entities: {message.metadata.entities.join(', ')}</div>
                      )}
                      {message.metadata.intent && (
                        <div>Intent: {message.metadata.intent} ({Math.round(message.metadata.confidence * 100)}%)</div>
                      )}
                      {message.metadata.spatialQuery && (
                        <div>Geospatial Query Detected</div>
                      )}
                    </div>
                  </div>
                )}
                <div className="text-xs opacity-60 mt-2">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex justify-start">
            <div className="flex items-start space-x-3 max-w-3xl">
              <div className="bg-teal-600 p-2 rounded-lg">
                <Bot className="h-5 w-5 text-white" />
              </div>
              <div className="bg-white/20 text-white p-4 rounded-lg">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-white/20">
        <div className="flex space-x-3">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about satellite data, documentation, or services..."
            className="flex-1 bg-white/20 border border-white/30 rounded-lg px-4 py-3 text-white placeholder-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isTyping}
            className="bg-gradient-to-r from-blue-500 to-teal-500 text-white p-3 rounded-lg hover:from-blue-600 hover:to-teal-600 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;