import { useState, useEffect, useRef } from 'react';
import { Coffee, Star, Clock, MapPin, Brain, Zap, LogIn, UserPlus, User, LogOut, Mail, Calendar, Shield, ShoppingBag, Package } from 'lucide-react';
import AuthModal from './AuthModal';
import axios from 'axios';

export default function LandingPage() {
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);
  const [showOrders, setShowOrders] = useState(false);
  const [orders, setOrders] = useState<any[]>([]);
  const [loadingOrders, setLoadingOrders] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [token, setToken] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Check if user is already logged in
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowProfileDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleAuthSuccess = (newToken: string, newUser: any) => {
    setToken(newToken);
    setUser(newUser);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
    setShowProfileDropdown(false);
  };

  const fetchOrders = async () => {
    if (!token || !user) return;
    
    setLoadingOrders(true);
    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/api/my-orders`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      setOrders(response.data);
    } catch (error) {
      console.error('Error fetching orders:', error);
      setOrders([]);
    } finally {
      setLoadingOrders(false);
    }
  };

  const handleShowOrders = () => {
    setShowOrders(true);
    setShowProfileDropdown(false);
    fetchOrders();
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

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
            <nav className="flex items-center space-x-4">
              <div className="hidden md:flex space-x-8 mr-4">
                <a href="#menu" className="text-coffee-700 hover:text-coffee-900">Menu</a>
                <a href="#about" className="text-coffee-700 hover:text-coffee-900">About</a>
                <a href="#contact" className="text-coffee-700 hover:text-coffee-900">Contact</a>
              </div>
              
              {/* Auth Buttons */}
              {user ? (
                <div className="flex items-center space-x-3 relative" ref={dropdownRef}>
                  <button
                    onClick={() => setShowProfileDropdown(!showProfileDropdown)}
                    className="flex items-center space-x-2 bg-coffee-50 hover:bg-coffee-100 px-4 py-2 rounded-full transition-colors cursor-pointer"
                  >
                    <User size={18} className="text-coffee-600" />
                    <span className="text-sm font-medium text-coffee-900">{user.username}</span>
                  </button>
                  
                  {/* Profile Dropdown */}
                  {showProfileDropdown && (
                    <div className="absolute top-full right-0 mt-2 w-80 bg-white rounded-lg shadow-xl border border-gray-200 z-50 overflow-hidden">
                      {/* Header */}
                      <div className="bg-gradient-to-r from-coffee-600 to-coffee-800 text-white p-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                            <User size={24} />
                          </div>
                          <div>
                            <h3 className="font-semibold text-lg">{user.full_name || user.username}</h3>
                            <p className="text-coffee-100 text-sm">
                              {user.is_admin ? '👑 Admin' : '☕ Customer'}
                            </p>
                          </div>
                        </div>
                      </div>
                      
                      {/* Profile Info */}
                      <div className="p-4 space-y-3">
                        <div className="flex items-start space-x-3">
                          <User size={18} className="text-gray-400 mt-0.5" />
                          <div>
                            <p className="text-xs text-gray-500">Username</p>
                            <p className="text-sm font-medium text-gray-900">{user.username}</p>
                          </div>
                        </div>
                        
                        <div className="flex items-start space-x-3">
                          <Mail size={18} className="text-gray-400 mt-0.5" />
                          <div>
                            <p className="text-xs text-gray-500">Email</p>
                            <p className="text-sm font-medium text-gray-900">{user.email}</p>
                          </div>
                        </div>
                        
                        <div className="flex items-start space-x-3">
                          <Calendar size={18} className="text-gray-400 mt-0.5" />
                          <div>
                            <p className="text-xs text-gray-500">Member Since</p>
                            <p className="text-sm font-medium text-gray-900">
                              {formatDate(user.created_at)}
                            </p>
                          </div>
                        </div>
                        
                        {user.is_admin && (
                          <div className="flex items-start space-x-3">
                            <Shield size={18} className="text-yellow-500 mt-0.5" />
                            <div>
                              <p className="text-xs text-gray-500">Role</p>
                              <p className="text-sm font-medium text-yellow-600">Administrator</p>
                            </div>
                          </div>
                        )}
                        
                        <div className="pt-2 border-t border-gray-200">
                          <div className="flex items-center justify-between text-xs text-gray-500">
                            <span>Account Status</span>
                            <span className={`px-2 py-1 rounded-full ${
                              user.is_active 
                                ? 'bg-green-100 text-green-700' 
                                : 'bg-red-100 text-red-700'
                            }`}>
                              {user.is_active ? '✓ Active' : '✗ Inactive'}
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      {/* Actions */}
                      <div className="border-t border-gray-200 p-2 space-y-2">
                        <button
                          onClick={handleShowOrders}
                          className="w-full flex items-center justify-center space-x-2 bg-coffee-50 hover:bg-coffee-100 text-coffee-700 px-4 py-2 rounded-lg transition-colors"
                        >
                          <ShoppingBag size={18} />
                          <span className="font-medium">My Orders</span>
                        </button>
                        <button
                          onClick={handleLogout}
                          className="w-full flex items-center justify-center space-x-2 bg-red-50 hover:bg-red-100 text-red-700 px-4 py-2 rounded-lg transition-colors"
                        >
                          <LogOut size={18} />
                          <span className="font-medium">Logout</span>
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="flex items-center space-x-2 bg-coffee-600 hover:bg-coffee-700 text-white px-6 py-2 rounded-full transition-colors shadow-md hover:shadow-lg"
                >
                  <LogIn size={18} />
                  <span className="font-medium">Login / Register</span>
                </button>
              )}
            </nav>
          </div>
        </div>
      </header>

      {/* Auth Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onSuccess={handleAuthSuccess}
      />

      {/* Orders Modal */}
      {showOrders && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-coffee-600 to-coffee-800 text-white p-6 flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold flex items-center">
                  <ShoppingBag className="mr-2" size={24} />
                  My Orders
                </h2>
                <p className="text-coffee-100 mt-1">Your order history</p>
              </div>
              <button
                onClick={() => setShowOrders(false)}
                className="text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2 transition-colors"
              >
                <LogOut size={20} />
              </button>
            </div>

            {/* Orders List */}
            <div className="p-6 overflow-y-auto max-h-[calc(80vh-120px)]">
              {loadingOrders ? (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-coffee-600 mx-auto"></div>
                  <p className="text-gray-600 mt-4">Loading your orders...</p>
                </div>
              ) : orders.length === 0 ? (
                <div className="text-center py-12">
                  <Package size={48} className="mx-auto text-gray-300 mb-4" />
                  <p className="text-gray-600 text-lg">No orders yet</p>
                  <p className="text-gray-400 mt-2">Start ordering to see your history here!</p>
                  <button
                    onClick={() => {
                      setShowOrders(false);
                      const chatButton = document.querySelector('[data-chat-toggle]') as HTMLElement;
                      if (chatButton) chatButton.click();
                    }}
                    className="mt-4 bg-coffee-600 hover:bg-coffee-700 text-white px-6 py-2 rounded-lg transition-colors"
                  >
                    Order Now
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {orders.map((order) => (
                    <div key={order.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      {/* Order Header */}
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h3 className="font-semibold text-lg text-gray-900">
                            Order #{order.id}
                          </h3>
                          <p className="text-sm text-gray-500">
                            {order.created_at ? new Date(order.created_at).toLocaleDateString('en-US', {
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            }) : 'Date not available'}
                          </p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          order.status === 'confirmed' ? 'bg-green-100 text-green-700' :
                          order.status === 'preparing' ? 'bg-yellow-100 text-yellow-700' :
                          order.status === 'ready' ? 'bg-blue-100 text-blue-700' :
                          order.status === 'completed' ? 'bg-gray-100 text-gray-700' :
                          'bg-orange-100 text-orange-700'
                        }`}>
                          {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                        </span>
                      </div>

                      {/* Order Items */}
                      <div className="space-y-2 mb-3">
                        {order.items.map((item: any, idx: number) => (
                          <div key={idx} className="flex justify-between text-sm">
                            <span className="text-gray-700">
                              {item.quantity}x {item.name}
                            </span>
                            <span className="text-gray-900 font-medium">
                              ${(item.price * item.quantity).toFixed(2)}
                            </span>
                          </div>
                        ))}
                      </div>

                      {/* Order Total with Tax Breakdown */}
                      <div className="border-t border-gray-200 pt-3 space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Subtotal</span>
                          <span className="text-gray-900">
                            ${(parseFloat(order.total) / 1.08).toFixed(2)}
                          </span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Tax (8%)</span>
                          <span className="text-gray-900">
                            ${(parseFloat(order.total) - (parseFloat(order.total) / 1.08)).toFixed(2)}
                          </span>
                        </div>
                        <div className="flex justify-between items-center pt-2 border-t border-gray-100">
                          <span className="font-semibold text-gray-900">Total</span>
                          <span className="text-lg font-bold text-coffee-600">
                            ${parseFloat(order.total).toFixed(2)}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

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
            
            {/* CTA Button */}
            <div className="mb-8">
              <button 
                onClick={() => {
                  const chatButton = document.querySelector('[data-chat-toggle]') as HTMLElement;
                  if (chatButton) chatButton.click();
                }}
                className="bg-coffee-600 hover:bg-coffee-700 text-white font-semibold py-4 px-8 rounded-full text-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
              >
                ☕ Try Our AI Barista
              </button>
            </div>
            
            {/* Coffee Steam Animation */}
            <div className="relative inline-block">
              <div className="text-6xl">☕</div>
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <div className="flex space-x-1">
                  <div className="w-1 h-8 bg-gray-300 rounded-full opacity-60 animate-pulse" style={{animationDelay: '0s', animationDuration: '2s'}}></div>
                  <div className="w-1 h-6 bg-gray-400 rounded-full opacity-50 animate-pulse" style={{animationDelay: '0.3s', animationDuration: '2.2s'}}></div>
                  <div className="w-1 h-7 bg-gray-300 rounded-full opacity-70 animate-pulse" style={{animationDelay: '0.6s', animationDuration: '1.8s'}}></div>
                </div>
              </div>
            </div>
            
            <div className="text-center mt-6">
              <p className="text-lg text-coffee-600 font-medium">
                Click the chat button to start your AI coffee experience
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
