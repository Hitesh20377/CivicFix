import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Shield, LogIn, UserPlus, LayoutDashboard, Sparkles, MapPin } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const isActive = (path) => location.pathname === path;

  return (
    <header className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-3 group">
          <div className="bg-gradient-to-tr from-blue-600 to-indigo-600 p-2 rounded-xl text-white shadow-lg shadow-blue-500/20 ring-1 ring-white/20 group-hover:scale-105 transition-transform">
            <Shield size={22} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-extrabold tracking-tight text-white group-hover:text-blue-400 transition-colors">CivicFix</span>
              <span className="hidden sm:inline-block bg-blue-500/10 text-blue-400 text-[10px] font-bold px-2 py-0.5 rounded-full border border-blue-500/20 uppercase tracking-wide">
                Smart City Ops
              </span>
            </div>
            <span className="text-[10px] text-slate-400 block -mt-0.5">Municipal Resolution Platform</span>
          </div>
        </Link>

        {/* Center Nav Links */}
        <nav className="hidden md:flex items-center gap-1 bg-slate-900/60 p-1 rounded-xl border border-slate-800/80 text-xs">
          <Link
            to="/"
            className={`px-3.5 py-1.5 rounded-lg font-medium transition-all ${
              isActive('/') ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20' : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
            }`}
          >
            Home
          </Link>
          <Link
            to="/issues"
            className={`px-3.5 py-1.5 rounded-lg font-medium transition-all ${
              isActive('/issues') ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20' : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
            }`}
          >
            Live Issues
          </Link>
        </nav>

        {/* Right CTA Actions */}
        <div className="flex items-center gap-3">
          {user ? (
            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate('/issues')}
                className="bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700/80 font-semibold text-xs px-3.5 py-2 rounded-xl transition-all flex items-center gap-1.5"
              >
                <LayoutDashboard size={15} className="text-blue-400" />
                <span>Console</span>
              </button>
              <button
                onClick={logout}
                className="text-xs text-slate-400 hover:text-red-400 transition-colors px-2.5 py-1.5"
              >
                Sign Out
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                to="/login"
                className={`text-xs font-semibold px-3.5 py-2 rounded-xl transition-all flex items-center gap-1.5 ${
                  isActive('/login')
                    ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                    : 'text-slate-300 hover:text-white hover:bg-slate-900 border border-slate-800'
                }`}
              >
                <LogIn size={15} />
                <span>Sign In</span>
              </Link>
              <Link
                to="/register"
                className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-xs px-4 py-2 rounded-xl shadow-lg shadow-blue-600/20 transition-all flex items-center gap-1.5"
              >
                <UserPlus size={15} />
                <span>Register</span>
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Navbar;
