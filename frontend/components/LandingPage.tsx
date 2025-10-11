import { Coffee, Star, Clock, MapPin, Brain, Zap } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-coffee-50 to-coffee-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="flex items-center space-x-2">
                <Coffee className="h-8 w-8 text-coffee-600" />
                <Brain className="h-6 w-6 text-blue-600" />
              </div>
              <h1 className="text-2xl font-bold text-coffee-900 ml-3">Coffee and AI</h1>
            </div>
            <nav className="hidden md:flex space-x-8">
              <a href="#menu" className="text-coffee-700 hover:text-coffee-900">Menu</a>
              <a href="#about" className="text-coffee-700 hover:text-coffee-900">About</a>
              <a href="#contact" className="text-coffee-700 hover:text-coffee-900">Contact</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-5xl font-bold text-coffee-900 mb-6">
              Where Intelligence Meets Espresso
            </h2>
            <p className="text-xl text-coffee-700 mb-8 max-w-3xl mx-auto">
              Experience the future of coffee ordering with our AI-powered barista assistant. 
              Get personalized recommendations, smart ordering, and perfect coffee every time using LangChain and LangGraph technology.
            </p>
            <div className="text-center">
              <p className="text-lg text-coffee-600 font-medium">
                To explore our menu and place orders, use the chat option in the bottom right corner
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* AI Features */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-coffee-900 mb-4">AI-Powered Coffee Experience</h3>
            <p className="text-lg text-coffee-600">Discover how artificial intelligence enhances your coffee journey</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <Brain className="h-12 w-12 text-blue-600 mx-auto mb-4" />
              <h4 className="text-xl font-semibold mb-3">Smart Recommendations</h4>
              <p className="text-coffee-600">Our AI learns your preferences and suggests the perfect coffee for your mood and taste.</p>
            </div>
            
            <div className="text-center p-6">
              <div className="text-4xl mb-4">💬</div>
              <h4 className="text-xl font-semibold mb-3">Natural Conversations</h4>
              <p className="text-coffee-600">Chat naturally with our AI barista using LangChain and LangGraph technology.</p>
            </div>
            
            <div className="text-center p-6">
              <Zap className="h-12 w-12 text-yellow-600 mx-auto mb-4" />
              <h4 className="text-xl font-semibold mb-3">Instant Ordering</h4>
              <p className="text-coffee-600">Place orders quickly with intelligent cart management and seamless checkout.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Menu Preview */}
      <section id="menu" className="py-16 bg-coffee-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-coffee-900 mb-4">Our AI-Curated Menu</h3>
            <p className="text-lg text-coffee-600">Expertly crafted beverages enhanced by intelligent recommendations</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
              <h4 className="font-semibold text-lg mb-2">Neural Espresso</h4>
              <p className="text-coffee-600 text-sm mb-3">Rich, bold shot powered by AI precision</p>
              <p className="text-coffee-800 font-semibold">$2.50</p>
            </div>
            
            <div className="bg-white rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
              <h4 className="font-semibold text-lg mb-2">AI Latte</h4>
              <p className="text-coffee-600 text-sm mb-3">Perfectly balanced espresso and steamed milk</p>
              <p className="text-coffee-800 font-semibold">$4.50</p>
            </div>
            
            <div className="bg-white rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
              <h4 className="font-semibold text-lg mb-2">Smart Cappuccino</h4>
              <p className="text-coffee-600 text-sm mb-3">Equal parts espresso, milk, and foam</p>
              <p className="text-coffee-800 font-semibold">$4.00</p>
            </div>
            
            <div className="bg-white rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
              <h4 className="font-semibold text-lg mb-2">Algorithm Mocha</h4>
              <p className="text-coffee-600 text-sm mb-3">Espresso, chocolate, and steamed milk</p>
              <p className="text-coffee-800 font-semibold">$5.00</p>
            </div>
          </div>
        </div>
      </section>

      {/* Technology Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-coffee-900 mb-4">Powered by Advanced AI</h3>
            <p className="text-lg text-coffee-600">Built with cutting-edge technology for the perfect coffee experience</p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h4 className="text-2xl font-semibold mb-4">LangChain & LangGraph</h4>
              <p className="text-coffee-600 mb-4">
                Our AI assistant uses state-of-the-art language models with LangChain for natural conversations 
                and LangGraph for intelligent workflow management.
              </p>
              <ul className="space-y-2 text-coffee-600">
                <li>• Multi-agent architecture for specialized tasks</li>
                <li>• Vector memory for personalized experiences</li>
                <li>• Smart tool calling for menu operations</li>
                <li>• Amazon Nova Micro AI integration</li>
              </ul>
            </div>
            
            <div className="bg-gray-900 text-green-400 p-6 rounded-lg font-mono text-sm">
              <div className="mb-2">$ coffee-ai --start</div>
              <div className="mb-2">✅ LangChain agents initialized</div>
              <div className="mb-2">✅ LangGraph workflow active</div>
              <div className="mb-2">✅ Vector memory loaded</div>
              <div className="mb-2">✅ AI barista ready</div>
              <div className="text-yellow-400">Welcome to Coffee and AI! ☕🤖</div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 bg-coffee-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-3xl font-bold mb-2">10K+</div>
              <div className="text-coffee-200">AI Conversations</div>
            </div>
            <div>
              <div className="text-3xl font-bold mb-2">98%</div>
              <div className="text-coffee-200">Order Accuracy</div>
            </div>
            <div>
              <div className="text-3xl font-bold mb-2">5★</div>
              <div className="text-coffee-200">AI Experience</div>
            </div>
            <div>
              <div className="text-3xl font-bold mb-2">24/7</div>
              <div className="text-coffee-200">AI Assistant</div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Coffee className="h-6 w-6 text-coffee-400" />
                <Brain className="h-5 w-5 text-blue-400" />
                <span className="text-xl font-bold">Coffee and AI</span>
              </div>
              <p className="text-gray-400">Where Intelligence Meets Espresso</p>
            </div>
            
            <div>
              <h5 className="font-semibold mb-4">Menu</h5>
              <ul className="space-y-2 text-gray-400">
                <li>AI-Curated Coffee</li>
                <li>Smart Pastries</li>
                <li>Neural Food</li>
                <li>Algorithm Specials</li>
              </ul>
            </div>
            
            <div>
              <h5 className="font-semibold mb-4">Technology</h5>
              <ul className="space-y-2 text-gray-400">
                <li>LangChain</li>
                <li>LangGraph</li>
                <li>Amazon Nova</li>
                <li>AI Agents</li>
              </ul>
            </div>
            
            <div>
              <h5 className="font-semibold mb-4">Contact</h5>
              <ul className="space-y-2 text-gray-400">
                <li>hello@coffeeandai.com</li>
                <li>(555) 123-BREW</li>
                <li>123 AI Street</li>
                <li>Tech City, TC 12345</li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Coffee and AI. All rights reserved. Built with LangChain, LangGraph, and Amazon Nova.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
