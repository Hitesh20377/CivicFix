import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { 
  Shield, MapPin, ArrowRight, Activity, CheckCircle2, AlertTriangle, 
  Users, HardHat, Building2, Wrench, ChevronRight, Zap, Sparkles 
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Home = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-blue-500 selection:text-white">
      {/* Shared Modern Navbar */}
      <Navbar />

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 px-4 sm:px-6 lg:px-8">
        {/* Ambient background blur elements */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-600/15 rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute top-1/3 right-10 w-96 h-96 bg-indigo-600/15 rounded-full blur-[100px] pointer-events-none" />

        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12 items-center relative z-10">
          
          {/* Hero Left Content */}
          <div className="lg:col-span-6 space-y-6 text-center lg:text-left">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-wider shadow-inner">
              <Zap className="w-3.5 h-3.5 text-blue-400 animate-pulse" />
              Next-Gen Municipal Operations
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-[1.15]">
              Streamline City Infrastructure <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-indigo-300 to-teal-300">Resolutions</span>
            </h1>

            <p className="text-base sm:text-lg text-slate-400 font-normal leading-relaxed max-w-2xl mx-auto lg:mx-0">
              CivicFix empowers citizens to report public hazards in real-time, connecting municipal officers and field workers with GIS location tracking and automated dispatch workflows.
            </p>

            {/* Action CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 pt-2">
              <button
                onClick={() => navigate(user ? '/issues/new' : '/login')}
                className="w-full sm:w-auto bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-sm px-6 py-3.5 rounded-xl shadow-xl shadow-blue-600/25 transition-all flex items-center justify-center gap-2 group"
              >
                <AlertTriangle className="w-4 h-4 text-amber-300" />
                <span>Report a Civic Issue</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </button>

              <button
                onClick={() => navigate('/issues')}
                className="w-full sm:w-auto bg-slate-900/80 hover:bg-slate-900 text-slate-200 border border-slate-800 hover:border-slate-700 font-semibold text-sm px-6 py-3.5 rounded-xl transition-all flex items-center justify-center gap-2"
              >
                <Activity className="w-4 h-4 text-blue-400" />
                <span>Explore Live Console</span>
              </button>
            </div>

            {/* Quick Metrics Bar */}
            <div className="grid grid-cols-3 gap-4 pt-6 border-t border-slate-800/80 max-w-lg mx-auto lg:mx-0">
              <div>
                <div className="text-2xl font-extrabold text-white">99.8%</div>
                <div className="text-xs text-slate-400 mt-0.5">SLA Uptime</div>
              </div>
              <div>
                <div className="text-2xl font-extrabold text-blue-400">1,245+</div>
                <div className="text-xs text-slate-400 mt-0.5">Resolved Issues</div>
              </div>
              <div>
                <div className="text-2xl font-extrabold text-indigo-400">&lt; 24h</div>
                <div className="text-xs text-slate-400 mt-0.5">Avg Response</div>
              </div>
            </div>
          </div>

          {/* Hero Right Visual Image Banner */}
          <div className="lg:col-span-6 relative">
            <div className="relative rounded-2xl overflow-hidden border border-slate-800/90 shadow-2xl group bg-slate-900">
              {/* Image banner */}
              <img 
                src="/civic_hero_banner.jpg" 
                alt="Futuristic Civic Network" 
                className="w-full h-auto object-cover transform group-hover:scale-105 transition-transform duration-700 opacity-90"
              />
              
              {/* Overlay Gradient Card Badge */}
              <div className="absolute bottom-4 left-4 right-4 p-4 rounded-xl bg-slate-950/85 backdrop-blur-md border border-slate-800 flex items-center justify-between text-xs">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-emerald-400 animate-ping" />
                  <div>
                    <div className="font-semibold text-slate-200">Municipal Dispatch Online</div>
                    <div className="text-[11px] text-slate-400">Real-time GIS PostGIS Location Sync Active</div>
                  </div>
                </div>
                <span className="text-[10px] bg-blue-500/10 text-blue-400 px-2.5 py-1 rounded-full font-mono border border-blue-500/20">
                  v2.4 Active
                </span>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* Role Breakdown Section */}
      <section className="py-16 bg-slate-900/50 border-t border-b border-slate-800/80 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white">Unified Platform for All Stakeholders</h2>
            <p className="text-sm text-slate-400 mt-2">Tailored interfaces for citizens, ward officers, and field repair units.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* Citizen Card */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 hover:border-blue-500/40 transition-all flex flex-col justify-between">
              <div>
                <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 mb-4">
                  <Users className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">Citizens</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-4">
                  Pinpoint issue coordinates on an interactive map, upload photo evidence, and track real-time resolution status.
                </p>
              </div>
              <Link to="/register" className="text-xs font-semibold text-blue-400 hover:text-blue-300 flex items-center gap-1">
                <span>Create Citizen Account</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {/* Officer Card */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 hover:border-indigo-500/40 transition-all flex flex-col justify-between">
              <div>
                <div className="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-4">
                  <Building2 className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">Municipal Officers</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-4">
                  Review ward-level issue queues, triage priorities, assign field workers, and monitor SLA compliance.
                </p>
              </div>
              <Link to="/login" className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1">
                <span>Officer Console Login</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {/* Field Worker Card */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 hover:border-emerald-500/40 transition-all flex flex-col justify-between">
              <div>
                <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-4">
                  <HardHat className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">Field Repair Workers</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-4">
                  Receive assigned repair orders with GPS location data, update work status, and submit completion proof.
                </p>
              </div>
              <Link to="/login" className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 flex items-center gap-1">
                <span>Field Worker Portal</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>

          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto py-8 bg-slate-950 border-t border-slate-800/80 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-blue-500" />
            <span className="font-semibold text-slate-400">CivicFix Municipal Platform</span>
          </div>
          <div>© {new Date().getFullYear()} CivicFix Inc. All rights reserved.</div>
        </div>
      </footer>
    </div>
  );
};

export default Home;
