import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import { UserPlus, User, Mail, Lock, Shield, ArrowRight } from 'lucide-react';

const Register = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { register, login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await register(fullName, email, password);
      await login(email, password);
      navigate('/issues');
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError('Registration failed. Please check your inputs.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans relative overflow-hidden">
      <Navbar />

      <div className="flex-1 flex items-center justify-center p-4 relative z-10 my-8">
        {/* Ambient background glow effects */}
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-emerald-600/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl pointer-events-none" />

        <div className="max-w-md w-full relative z-10">
          {/* Header Branding */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold tracking-wide uppercase mb-4">
              <Shield className="w-3.5 h-3.5" />
              Citizen Registration
            </div>
            <div className="flex items-center justify-center gap-3 mb-2">
              <div className="bg-gradient-to-tr from-emerald-600 to-teal-500 p-3 rounded-2xl text-white shadow-lg shadow-emerald-500/25 ring-1 ring-white/20">
                <UserPlus className="w-7 h-7" />
              </div>
              <h1 className="text-3xl font-extrabold tracking-tight text-white">CivicFix</h1>
            </div>
            <p className="text-sm text-slate-400">Register an account to submit & track city reports</p>
          </div>

          {/* Glassmorphic Card */}
          <div className="bg-slate-900/80 backdrop-blur-2xl rounded-2xl shadow-2xl p-8 border border-slate-800/80 ring-1 ring-white/5">
            {error && (
              <div className="bg-red-500/10 text-red-400 p-3.5 rounded-xl text-sm mb-6 border border-red-500/20 flex items-start gap-2.5">
                <span className="mt-0.5 font-bold">!</span>
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Full Name</label>
                <div className="relative">
                  <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    type="text"
                    required
                    className="w-full bg-slate-950/70 text-slate-100 pl-10 pr-4 py-2.5 rounded-xl border border-slate-800 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none transition-all text-sm placeholder:text-slate-600"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Alex Morgan"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    type="email"
                    required
                    className="w-full bg-slate-950/70 text-slate-100 pl-10 pr-4 py-2.5 rounded-xl border border-slate-800 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none transition-all text-sm placeholder:text-slate-600"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="citizen@example.com"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Password</label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    type="password"
                    required
                    minLength={8}
                    className="w-full bg-slate-950/70 text-slate-100 pl-10 pr-4 py-2.5 rounded-xl border border-slate-800 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none transition-all text-sm placeholder:text-slate-600"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="•••••••• (min 8 chars)"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold py-3 rounded-xl transition-all shadow-lg shadow-emerald-600/25 active:scale-[0.99] disabled:opacity-50 flex items-center justify-center gap-2 group text-sm mt-2"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Creating Account...
                  </span>
                ) : (
                  <>
                    Complete Registration
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                  </>
                )}
              </button>
            </form>

            <div className="mt-6 text-center text-xs text-slate-400">
              Already have an account?{' '}
              <Link to="/login" className="text-emerald-400 font-semibold hover:text-emerald-300 hover:underline">
                Sign in to Console
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
