import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import { LogIn, Mail, Lock, Shield, ArrowRight, Activity, CheckCircle2 } from 'lucide-react';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate('/issues');
    } catch (err) {
      setError('Invalid email or password. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickFill = (roleEmail) => {
    setEmail(roleEmail);
    setPassword('dummy');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans relative overflow-hidden">
      <Navbar />

      <div className="flex-1 flex items-center justify-center p-4 relative z-10 my-8">
        {/* Ambient background glow effects */}
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-red-600/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-rose-600/20 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-md w-full relative z-10">
          {/* Header Branding */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-semibold tracking-wide uppercase mb-4 shadow-inner">
              <Activity className="w-3.5 h-3.5 animate-pulse text-red-400" />
              Municipal Operations Management
            </div>
            <div className="flex items-center justify-center gap-3 mb-2">
              <div className="bg-gradient-to-tr from-red-600 to-rose-500 p-3 rounded-2xl text-white shadow-lg shadow-red-500/25 ring-1 ring-white/20">
                <Shield className="w-7 h-7" />
              </div>
              <h1 className="text-3xl font-extrabold tracking-tight text-white">CivicFix</h1>
            </div>
            <p className="text-sm text-slate-400">Sign in to access your dispatch & monitoring console</p>
          </div>

          {/* Glassmorphic Form Card */}
          <div className="bg-slate-900/80 backdrop-blur-2xl rounded-2xl shadow-2xl p-8 border border-slate-800/80 ring-1 ring-white/5">
            {error && (
              <div className="bg-red-500/10 text-red-400 p-3.5 rounded-xl text-sm mb-6 border border-red-500/20 flex items-start gap-2.5">
                <span className="mt-0.5 font-bold">!</span>
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    type="email"
                    required
                    className="w-full bg-slate-950/70 text-slate-100 pl-10 pr-4 py-2.5 rounded-xl border border-slate-800 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all placeholder:text-slate-600 text-sm"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="officer@civicfix.city"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    type="password"
                    required
                    className="w-full bg-slate-950/70 text-slate-100 pl-10 pr-4 py-2.5 rounded-xl border border-slate-800 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none transition-all placeholder:text-slate-600 text-sm"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-semibold py-3 rounded-xl transition-all shadow-lg shadow-red-600/25 active:scale-[0.99] disabled:opacity-50 flex items-center justify-center gap-2 group text-sm"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Authenticating...
                  </span>
                ) : (
                  <>
                    Sign In to Console
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                  </>
                )}
              </button>
            </form>

            {/* Quick Demo Credentials Assistant */}
            <div className="mt-8 pt-6 border-t border-slate-800/80">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-medium text-slate-400">Quick Test Profiles</span>
                <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full font-mono">Password: dummy</span>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => handleQuickFill('citizen@example.com')}
                  className="text-left p-2 rounded-lg bg-slate-950/50 hover:bg-slate-800/60 border border-slate-800 text-xs transition-all text-slate-300 hover:text-red-400 flex items-center justify-between"
                >
                  <span>Citizen</span>
                  <CheckCircle2 className="w-3.5 h-3.5 opacity-40" />
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickFill('officer@example.com')}
                  className="text-left p-2 rounded-lg bg-slate-950/50 hover:bg-slate-800/60 border border-slate-800 text-xs transition-all text-slate-300 hover:text-red-400 flex items-center justify-between"
                >
                  <span>Officer</span>
                  <CheckCircle2 className="w-3.5 h-3.5 opacity-40" />
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickFill('fieldworker@example.com')}
                  className="text-left p-2 rounded-lg bg-slate-950/50 hover:bg-slate-800/60 border border-slate-800 text-xs transition-all text-slate-300 hover:text-red-400 flex items-center justify-between"
                >
                  <span>Field Worker</span>
                  <CheckCircle2 className="w-3.5 h-3.5 opacity-40" />
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickFill('admin@example.com')}
                  className="text-left p-2 rounded-lg bg-slate-950/50 hover:bg-slate-800/60 border border-slate-800 text-xs transition-all text-slate-300 hover:text-red-400 flex items-center justify-between"
                >
                  <span>Admin</span>
                  <CheckCircle2 className="w-3.5 h-3.5 opacity-40" />
                </button>
              </div>
            </div>

            <div className="mt-6 text-center text-xs text-slate-400">
              Don't have an account?{' '}
              <Link to="/register" className="text-red-400 font-semibold hover:text-red-300 hover:underline">
                Create citizen account
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
