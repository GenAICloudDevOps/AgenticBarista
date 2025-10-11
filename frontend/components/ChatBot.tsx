import { useState, useEffect, useRef } from 'react';
import { Send, MessageCircle, X, Brain, Wrench, Settings, Zap } from 'lucide-react';
import axios from 'axios';

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

type AgentType = 'modern' | 'advanced' | 'workflow';

export default function ChatBot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [agentType, setAgentType] = useState<AgentType>('modern');
  const [userTier, setUserTier] = useState<string>('basic');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setSessionId(Math.random().toString(36).substring(7));
    
    setMessages([{
      id: '1',
      text: "Welcome to our advanced cafe! ☕ Choose your experience:\n• Modern: Basic LangChain v1 features\n• Advanced: Full middleware & structured output\n• Workflow: Custom StateGraph routing\n\nHow can I help you today?",
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

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.data.response,
        isUser: false,
        timestamp: new Date(),
        content_blocks: response.data.content_blocks || [],
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
      default: return '🤖';
    }
  };

  return (
    <>
      {/* Chat Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 bg-coffee-600 hover:bg-coffee-700 text-white p-4 rounded-full shadow-lg transition-all z-50"
      >
        {isOpen ? <X size={24} /> : <MessageCircle size={24} />}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-20 right-6 w-[450px] h-[450px] bg-white rounded-lg shadow-xl border border-gray-200 flex flex-col z-40">
          {/* Header */}
          <div className="bg-coffee-600 text-white p-4 rounded-t-lg">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold">Advanced Barista {getAgentIcon(agentType)}</h3>
                <p className="text-sm opacity-90">
                  {agentType === 'advanced' && 'Full LangChain v1 Features'}
                  {agentType === 'workflow' && 'Custom StateGraph Routing'}
                  {agentType === 'modern' && 'Basic LangChain v1'}
                </p>
              </div>
              <Settings size={16} className="opacity-75" />
            </div>
            
            {/* Agent Type Selector */}
            <div className="mt-2 flex gap-1">
              {(['modern', 'advanced', 'workflow'] as AgentType[]).map((type) => (
                <button
                  key={type}
                  onClick={() => setAgentType(type)}
                  className={`px-2 py-1 text-xs rounded ${
                    agentType === type 
                      ? 'bg-white text-coffee-600' 
                      : 'bg-coffee-700 text-white hover:bg-coffee-800'
                  }`}
                >
                  {type}
                </button>
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
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
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
                      {message.content_blocks && message.content_blocks.length > 0 ? (
                        renderContentBlocks(message.content_blocks)
                      ) : (
                        <p className="whitespace-pre-wrap">{message.text}</p>
                      )}
                      
                      {/* Show structured output for advanced agent */}
                      {agentType === 'advanced' && renderStructuredOutput(message.structured_output)}
                      
                      {/* Show intent/confidence for workflow agent */}
                      {agentType === 'workflow' && message.intent && (
                        <div className="mt-2 text-xs text-gray-600">
                          Intent: {message.intent} ({Math.round((message.confidence || 0) * 100)}%)
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
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
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
    </>
  );
}
