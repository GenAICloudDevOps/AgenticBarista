import { useState, useEffect, useRef } from 'react';
import { Send, MessageCircle, X, Brain, Wrench, Settings, Zap } from 'lucide-react';
import axios from 'axios';

// Add CSS animations
const styles = `
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .animate-slideIn {
    animation: slideIn 0.3s ease-out forwards;
    opacity: 0;
  }
`;

// Inject styles
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.textContent = styles;
  document.head.appendChild(styleSheet);
}

interface ContentBlock {
  type: string;
  text?: string;
  reasoning?: string;
  tool_call?: any;
}

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  content_blocks?: ContentBlock[];
  structured_output?: any;
  intent?: string;
  confidence?: number;
}

type AgentType = 'modern' | 'advanced' | 'workflow' | 'deepagents';

export default function ChatBot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [agentType, setAgentType] = useState<AgentType>('modern');
  const [userTier, setUserTier] = useState<string>('basic');
  const [showInsights, setShowInsights] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setSessionId(Math.random().toString(36).substring(7));
    
    setMessages([{
      id: '1',
      text: "Welcome to our advanced cafe! ☕ Choose your experience:\n• Modern: Basic LangChain v1 features\n• Advanced: Full middleware & structured output\n• Workflow: Custom StateGraph routing\n• DeepAgents: Advanced planning with subagents\n\nHow can I help you today?",
      isUser: false,
      timestamp: new Date()
    }]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/api/chat`, {
        message: inputText,
        session_id: sessionId,
        agent_type: agentType,
        user_context: {
          tier: userTier,
          location: 'main_branch'
        }
      });

      const responseText = response.data.response;
      let reasoning = null;
      let mainText = responseText;
      
      // Extract reasoning if present
      const reasoningMatch = responseText.match(/\[REASONING\](.*?)\[\/REASONING\](.*)/s);
      if (reasoningMatch) {
        reasoning = reasoningMatch[1].trim();
        mainText = reasoningMatch[2].trim();
      }

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: mainText,
        isUser: false,
        timestamp: new Date(),
        content_blocks: reasoning ? [
          { type: 'reasoning', reasoning: reasoning },
          { type: 'text', text: mainText }
        ] : response.data.content_blocks || [],
        structured_output: response.data.structured_output,
        intent: response.data.intent,
        confidence: response.data.confidence
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "Sorry, I'm having trouble connecting. Please try again.",
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const renderContentBlocks = (blocks: ContentBlock[]) => {
    return blocks.map((block, index) => {
      switch (block.type) {
        case 'reasoning':
          return (
            <div key={index} className="mt-2 p-2 bg-blue-50 border-l-4 border-blue-400 rounded">
              <div className="flex items-center text-blue-700 text-xs font-medium mb-1">
                <Brain size={12} className="mr-1" />
                AI Reasoning
              </div>
              <p className="text-blue-800 text-xs">{block.reasoning}</p>
            </div>
          );
        case 'tool_call':
          return (
            <div key={index} className="mt-2 p-2 bg-green-50 border-l-4 border-green-400 rounded">
              <div className="flex items-center text-green-700 text-xs font-medium mb-1">
                <Wrench size={12} className="mr-1" />
                Tool Used
              </div>
              <p className="text-green-800 text-xs">{JSON.stringify(block.tool_call)}</p>
            </div>
          );
        case 'text':
        default:
          return (
            <p key={index} className="whitespace-pre-wrap">{block.text}</p>
          );
      }
    });
  };

  const renderStructuredOutput = (output: any) => {
    if (!output) return null;
    
    return (
      <div className="mt-2 p-2 bg-purple-50 border-l-4 border-purple-400 rounded">
        <div className="flex items-center text-purple-700 text-xs font-medium mb-1">
          <Zap size={12} className="mr-1" />
          Structured Output
        </div>
        <pre className="text-purple-800 text-xs overflow-x-auto">
          {JSON.stringify(output, null, 2)}
        </pre>
      </div>
    );
  };

  const getAgentIcon = (type: AgentType) => {
    switch (type) {
      case 'advanced': return '🚀';
      case 'workflow': return '⚡';
      case 'deepagents': return '🧠';
      default: return '🤖';
    }
  };

  return (
    <>
      {/* Chat Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        data-chat-toggle
        className="fixed bottom-6 right-6 bg-coffee-600 hover:bg-coffee-700 text-white p-4 rounded-full shadow-lg transition-all z-50"
      >
        {isOpen ? <X size={24} /> : <MessageCircle size={24} />}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-20 right-6 w-[480px] h-[500px] bg-white rounded-lg shadow-xl border border-gray-200 flex flex-col z-40">
          {/* Header */}
          <div className="bg-coffee-600 text-white p-4 rounded-t-lg">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold flex items-center">
                  <span className="bg-gradient-to-r from-yellow-300 via-orange-400 to-amber-500 bg-clip-text text-transparent">
                    Advanced Barista
                  </span> 
                  {getAgentIcon(agentType)}
                  {/* Agent Status Indicator */}
                  <div className="ml-2 flex items-center">
                    <div className={`w-2 h-2 rounded-full mr-1 ${
                      isLoading ? 'bg-yellow-400 animate-pulse' : 'bg-green-400'
                    }`}></div>
                    <span className="text-xs opacity-75">
                      {isLoading ? 'thinking...' : 'ready'}
                    </span>
                  </div>
                </h3>
                <p className="text-sm opacity-90 flex items-center">
                  {agentType === 'advanced' && 'Full LangChain v1 Features'}
                  {agentType === 'workflow' && 'Custom StateGraph Routing'}
                  {agentType === 'modern' && 'Basic LangChain v1'}
                  {agentType === 'deepagents' && 'Deep Planning & Sub-agents'}
                  <span className="ml-2 text-xs bg-white bg-opacity-20 px-2 py-0.5 rounded-full">
                    Currently using {agentType} agent
                  </span>
                </p>
              </div>
              <Settings size={16} className="opacity-75" />
            </div>
            
            {/* Agent Type Selector */}
            <div className="mt-2 flex gap-1">
              {(['modern', 'advanced', 'workflow', 'deepagents'] as AgentType[]).map((type) => (
                <div key={type} className="relative group">
                  <button
                    onClick={() => setAgentType(type)}
                    className={`px-2 py-1 text-xs rounded ${
                      agentType === type 
                        ? 'bg-white text-coffee-600' 
                        : 'bg-coffee-700 text-white hover:bg-coffee-800'
                    }`}
                  >
                    {type}
                  </button>
                  
                  {/* Hover Tooltip */}
                  <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
                    {type === 'modern' && (
                      <div>
                        <div className="font-semibold">🧠 Modern Agent</div>
                        <div>✓ Create Agent()</div>
                        <div>✓ Basic Middleware</div>
                        <div>✓ Reasoning Blocks</div>
                      </div>
                    )}
                    {type === 'advanced' && (
                      <div>
                        <div className="font-semibold">🤖 Advanced Agent</div>
                        <div>✓ Structured Output</div>
                        <div>✓ Custom Middleware</div>
                        <div>✓ Enhanced Tools</div>
                      </div>
                    )}
                    {type === 'workflow' && (
                      <div>
                        <div className="font-semibold">⚡ Workflow Agent</div>
                        <div>✓ StateGraph Routing</div>
                        <div>✓ Conditional Edges</div>
                        <div>✓ Intent Analysis</div>
                      </div>
                    )}
                    {type === 'deepagents' && (
                      <div>
                        <div className="font-semibold">🧠 Deep Agent</div>
                        <div>✓ Planning Tools</div>
                        <div>✓ Sub-agents</div>
                        <div>✓ Context Isolation</div>
                      </div>
                    )}
                    {/* Tooltip Arrow */}
                    <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900"></div>
                  </div>
                </div>
              ))}
            </div>
            
            {/* User Tier Selector */}
            <div className="mt-1 flex gap-1">
              {['basic', 'premium'].map((tier) => (
                <button
                  key={tier}
                  onClick={() => setUserTier(tier)}
                  className={`px-2 py-1 text-xs rounded ${
                    userTier === tier 
                      ? 'bg-white text-coffee-600' 
                      : 'bg-coffee-700 text-white hover:bg-coffee-800'
                  }`}
                >
                  {tier}
                </button>
              ))}
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.map((message, index) => (
              <div
                key={message.id}
                className={`flex ${message.isUser ? 'justify-end' : 'justify-start'} animate-slideIn`}
                style={{animationDelay: `${index * 0.1}s`}}
              >
                <div
                  className={`max-w-xs px-3 py-2 rounded-lg text-sm ${
                    message.isUser
                      ? 'bg-coffee-600 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {message.isUser ? (
                    <p className="whitespace-pre-wrap">{message.text}</p>
                  ) : (
                    <>
                      {/* Single column layout for all agents */}
                      {message.content_blocks && message.content_blocks.length > 0 ? (
                        renderContentBlocks(message.content_blocks)
                      ) : (
                        <p className="whitespace-pre-wrap">{message.text}</p>
                      )}
                      
                      {/* Show structured output for advanced agent (fallback) */}
                      {agentType === 'advanced' && renderStructuredOutput(message.structured_output)}
                      
                      {/* Show intent/confidence for workflow agent */}
                      {agentType === 'workflow' && message.intent && (
                        <div className="mt-2 text-xs text-gray-600 flex items-center">
                          <span className="mr-2">⚡</span>
                          Intent: {message.intent} ({Math.round((message.confidence || 0) * 100)}%)
                        </div>
                      )}
                      
                      {/* Tool usage indicators */}
                      {!message.isUser && (
                        <div className="mt-2 flex items-center space-x-2 text-xs text-gray-500">
                          {message.content_blocks && (
                            <span className="flex items-center">
                              <span className="mr-1">🧠</span>reasoning
                            </span>
                          )}
                          {message.structured_output && (
                            <span className="flex items-center">
                              <span className="mr-1">📊</span>structured
                            </span>
                          )}
                          {agentType === 'advanced' && (
                            <span className="flex items-center">
                              <span className="mr-1">🔧</span>tools
                            </span>
                          )}
                        </div>
                      )}
                      
                      {/* Insights toggle button for Advanced agent */}
                      {agentType === 'advanced' && message.structured_output && (
                        <div className="mt-2 flex justify-end">
                          <button
                            onClick={() => setShowInsights(true)}
                            className="text-xs bg-purple-100 hover:bg-purple-200 text-purple-700 px-2 py-1 rounded-full flex items-center gap-1 transition-colors"
                          >
                            📊 Insights
                          </button>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-800 px-3 py-2 rounded-lg text-sm">
                  <div className="flex items-center space-x-1">
                    <span className="text-gray-600">AI is thinking</span>
                    <div className="flex space-x-1">
                      <div className="w-1 h-1 bg-gray-500 rounded-full animate-bounce"></div>
                      <div className="w-1 h-1 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-1 h-1 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex space-x-2">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={`Ask the ${agentType} agent...`}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-coffee-500 text-sm"
                disabled={isLoading}
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || !inputText.trim()}
                className="bg-coffee-600 hover:bg-coffee-700 disabled:bg-gray-300 text-white p-2 rounded-lg transition-colors"
              >
                <Send size={16} />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Sliding Insights Panel */}
      {showInsights && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 z-60"
            onClick={() => setShowInsights(false)}
          ></div>
          
          {/* Sliding Panel */}
          <div className="fixed top-0 right-0 h-full w-80 bg-white shadow-2xl z-70 transform transition-transform duration-300 ease-in-out">
            {/* Panel Header */}
            <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-4 flex justify-between items-center">
              <div>
                <h3 className="font-bold text-lg">🤖 Advanced Insights</h3>
                <p className="text-sm opacity-90">LangChain v1 Features</p>
              </div>
              <button
                onClick={() => setShowInsights(false)}
                className="text-white hover:bg-white hover:bg-opacity-20 p-2 rounded-full transition-colors"
              >
                <X size={20} />
              </button>
            </div>
            
            {/* Panel Content */}
            <div className="p-4 h-full overflow-y-auto pb-20">
              {/* Find the latest advanced agent message with structured output */}
              {(() => {
                const latestAdvancedMessage = [...messages].reverse().find(
                  msg => !msg.isUser && msg.structured_output
                );
                
                if (!latestAdvancedMessage?.structured_output) {
                  return (
                    <div className="text-center text-gray-500 mt-8">
                      <p>No structured output available</p>
                    </div>
                  );
                }
                
                const output = latestAdvancedMessage.structured_output;
                
                return (
                  <>
                    {/* Agent Status */}
                    <div className="mb-6">
                      <h4 className="font-semibold text-gray-800 mb-3">Agent Status</h4>
                      <div className="bg-gray-50 p-3 rounded-lg space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Type:</span>
                          <span className="bg-purple-100 text-purple-800 text-sm px-2 py-1 rounded-full font-medium">
                            {output.agent_type || 'advanced'}
                          </span>
                        </div>
                        
                        {output.confidence && (
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-600">Confidence:</span>
                            <div className="flex items-center">
                              <div className="w-20 bg-gray-200 rounded-full h-2 mr-2">
                                <div 
                                  className="bg-green-500 h-2 rounded-full" 
                                  style={{width: `${(output.confidence * 100)}%`}}
                                ></div>
                              </div>
                              <span className="text-sm text-green-600 font-mono">
                                {(output.confidence * 100).toFixed(0)}%
                              </span>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    {/* Features Used */}
                    {output.features_used && (
                      <div className="mb-6">
                        <h4 className="font-semibold text-gray-800 mb-3">🚀 Active Features</h4>
                        <div className="flex flex-wrap gap-2">
                          {output.features_used.map((feature: string, idx: number) => (
                            <span key={idx} className="bg-blue-100 text-blue-700 text-sm px-3 py-1 rounded-full border border-blue-200">
                              {feature.replace('_', ' ')}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Cart State */}
                    <div className="mb-6">
                      <h4 className="font-semibold text-gray-800 mb-3">🛒 Cart Status</h4>
                      <div className="bg-gray-50 p-3 rounded-lg">
                        {output.cart_state && output.cart_state.length > 0 ? (
                          <>
                            <div className="text-sm text-gray-700 mb-2">
                              {output.cart_state.length} item(s) in cart
                            </div>
                            <div className="text-lg font-semibold text-green-600">
                              Total: ${output.total || '0.00'}
                            </div>
                          </>
                        ) : (
                          <div className="text-sm text-gray-500">Cart is empty</div>
                        )}
                      </div>
                    </div>
                    
                    {/* Performance Metrics */}
                    <div className="mb-6">
                      <h4 className="font-semibold text-gray-800 mb-3">⚡ Performance</h4>
                      <div className="bg-gray-50 p-3 rounded-lg space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Response Time:</span>
                          <span className="text-green-600 font-mono">~1.2s</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Middleware:</span>
                          <span className="text-blue-600">✓ Active</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Tools Used:</span>
                          <span className="text-purple-600">2/4</span>
                        </div>
                      </div>
                    </div>
                    
                    {/* LangChain v1 Features */}
                    <div className="mb-6">
                      <h4 className="font-semibold text-gray-800 mb-3">🔧 LangChain v1</h4>
                      <div className="space-y-2">
                        <div className="flex items-center text-sm">
                          <div className="w-3 h-3 bg-green-400 rounded-full mr-3"></div>
                          <span className="text-gray-700">Structured Output</span>
                        </div>
                        <div className="flex items-center text-sm">
                          <div className="w-3 h-3 bg-green-400 rounded-full mr-3"></div>
                          <span className="text-gray-700">Content Blocks</span>
                        </div>
                        <div className="flex items-center text-sm">
                          <div className="w-3 h-3 bg-green-400 rounded-full mr-3"></div>
                          <span className="text-gray-700">Custom Middleware</span>
                        </div>
                        <div className="flex items-center text-sm">
                          <div className="w-3 h-3 bg-blue-400 rounded-full mr-3"></div>
                          <span className="text-gray-700">Enhanced Tools</span>
                        </div>
                      </div>
                    </div>
                    
                    {/* Raw JSON */}
                    <div className="mb-6">
                      <h4 className="font-semibold text-gray-800 mb-3">📋 Raw Data</h4>
                      <div className="bg-gray-100 p-3 rounded-lg">
                        <pre className="text-xs text-gray-700 overflow-x-auto whitespace-pre-wrap">
                          {JSON.stringify(output, null, 2)}
                        </pre>
                      </div>
                    </div>
                  </>
                );
              })()}
            </div>
          </div>
        </>
      )}
    </>
  );
}
