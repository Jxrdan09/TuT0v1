import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  Code,
  User,
  LogOut,
  Home,
  Shield,
  CreditCard
} from 'lucide-react';

const Layout = ({ children }) => {
  const { user, logout, isAdmin } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => {
    return location.pathname === path;
  };

  // Si estamos en el dashboard, no mostrar el layout normal
  if (location.pathname === '/') {
    return children;
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Navbar */}
      <nav className="bg-gray-900/80 backdrop-blur border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <Code className="h-8 w-8 text-emerald-400 drop-shadow-[0_0_8px_rgba(16,185,129,0.7)]" />
                <span className="ml-2 text-xl font-bold text-emerald-300 tracking-wider">
                  Underground
                </span>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <Link
                  to="/"
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                    isActive('/') 
                      ? 'border-emerald-500 text-emerald-300' 
                      : 'border-transparent text-gray-400 hover:border-emerald-700 hover:text-gray-200'
                  }`}
                >
                  <Home className="h-4 w-4 mr-1" />
                  Inicio
                </Link>
        <Link
          to="/amazon"
          className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
            isActive('/amazon') 
              ? 'border-emerald-500 text-emerald-300' 
              : 'border-transparent text-gray-400 hover:border-emerald-700 hover:text-gray-200'
          }`}
        >
          <CreditCard className="h-4 w-4 mr-1" />
          Amazon
        </Link>
        
                {isAdmin && (
                  <Link
                    to="/admin"
                    className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                      isActive('/admin') 
                        ? 'border-emerald-500 text-emerald-300' 
                        : 'border-transparent text-gray-400 hover:border-emerald-700 hover:text-gray-200'
                    }`}
                  >
                    <Shield className="h-4 w-4 mr-1" />
                    Admin
                  </Link>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <User className="h-5 w-5 text-emerald-400" />
                <span className="text-sm text-gray-300">{user?.username}</span>
                {isAdmin && (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-900 text-emerald-300 border border-emerald-700">
                    ADMIN
                  </span>
                )}
              </div>
              <button
                onClick={handleLogout}
                className="inline-flex items-center px-3 py-2 border border-emerald-700 text-sm leading-4 font-medium rounded-md text-emerald-300 hover:bg-emerald-900/40 focus:outline-none transition-colors duration-200"
              >
                <LogOut className="h-4 w-4 mr-1" />
                Salir
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
};

export default Layout;
