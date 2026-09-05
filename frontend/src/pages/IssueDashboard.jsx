import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, Map, List, PlusCircle, Shield, AlertCircle, CheckCircle2, Clock, Activity, User } from 'lucide-react';
import api from '../services/api';

const IssueDashboard = () => {
  const { user, logout } = useAuth();
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('ALL');
  const navigate = useNavigate();

  useEffect(() => {
    api.get('/health').catch(() => {});

    api.get('/issues')
      .then(res => {
        setIssues(res.data.data || res.data.issues || []);
      })
      .catch(err => {
        console.error("Error fetching issues:", err);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const totalCount = issues.length;
  const reportedCount = issues.filter(i => i.status === 'REPORTED' || i.status === 'OPEN').length;
  const inProgressCount = issues.filter(i => i.status === 'IN_PROGRESS' || i.status === 'ASSIGNED').length;
  const resolvedCount = issues.filter(i => i.status === 'RESOLVED').length;

  const filteredIssues = issues.filter(issue => {
    if (filter === 'ALL') return true;
    if (filter === 'REPORTED') return issue.status === 'REPORTED' || issue.status === 'OPEN';
    if (filter === 'IN_PROGRESS') return issue.status === 'IN_PROGRESS' || issue.status === 'ASSIGNED';
    if (filter === 'RESOLVED') return issue.status === 'RESOLVED';
    return true;
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Glass Nav */}
      <header className="sticky top-0 z-30 bg-slate-900/90 backdrop-blur-xl border-b border-slate-800 px-6 py-3.5 flex justify-between items-center">
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/issues')}>
          <div className="bg-gradient-to-tr from-blue-600 to-indigo-600 p-2 rounded-xl text-white shadow-lg shadow-blue-500/20 ring-1 ring-white/20">
            <Shield size={20} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold tracking-tight text-white">CivicFix</h1>
              <span className="bg-blue-500/10 text-blue-400 text-[10px] font-bold px-2 py-0.5 rounded-full border border-blue-500/20 uppercase tracking-wide">
                Management Console
              </span>
            </div>
            <p className="text-[11px] text-slate-400">Municipal Dispatch & Resolution Operations</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-2 bg-slate-950/80 px-3 py-1.5 rounded-xl border border-slate-800 text-xs">
            <User className="w-3.5 h-3.5 text-blue-400" />
            <span className="text-slate-300 font-medium">{user?.email || 'User'}</span>
            <span className="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded font-mono uppercase">
              {user?.role || 'Citizen'}
            </span>
          </div>

          <button 
            onClick={logout}
            className="flex items-center gap-2 text-slate-400 hover:text-red-400 transition-colors px-3 py-1.5 rounded-xl hover:bg-red-500/10 text-xs font-semibold border border-transparent hover:border-red-500/20"
          >
            <LogOut size={16} />
            <span className="hidden sm:inline">Sign Out</span>
          </button>
        </div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto p-6">
        {/* Metric Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div 
            onClick={() => setFilter('ALL')}
            className={`p-4 rounded-2xl border transition-all cursor-pointer ${
              filter === 'ALL' ? 'bg-blue-600/15 border-blue-500/50 shadow-lg shadow-blue-500/10' : 'bg-slate-900/60 border-slate-800/80 hover:border-slate-700'
            }`}
          >
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-1">
              <span>Total Issues</span>
              <Activity className="w-4 h-4 text-blue-400" />
            </div>
            <div className="text-2xl font-extrabold text-white">{totalCount}</div>
          </div>

          <div 
            onClick={() => setFilter('REPORTED')}
            className={`p-4 rounded-2xl border transition-all cursor-pointer ${
              filter === 'REPORTED' ? 'bg-blue-600/15 border-blue-500/50 shadow-lg shadow-blue-500/10' : 'bg-slate-900/60 border-slate-800/80 hover:border-slate-700'
            }`}
          >
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-1">
              <span>Pending / Reported</span>
              <AlertCircle className="w-4 h-4 text-blue-400" />
            </div>
            <div className="text-2xl font-extrabold text-blue-400">{reportedCount}</div>
          </div>

          <div 
            onClick={() => setFilter('IN_PROGRESS')}
            className={`p-4 rounded-2xl border transition-all cursor-pointer ${
              filter === 'IN_PROGRESS' ? 'bg-amber-600/15 border-amber-500/50 shadow-lg shadow-amber-500/10' : 'bg-slate-900/60 border-slate-800/80 hover:border-slate-700'
            }`}
          >
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-1">
              <span>In Progress</span>
              <Clock className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-2xl font-extrabold text-amber-400">{inProgressCount}</div>
          </div>

          <div 
            onClick={() => setFilter('RESOLVED')}
            className={`p-4 rounded-2xl border transition-all cursor-pointer ${
              filter === 'RESOLVED' ? 'bg-emerald-600/15 border-emerald-500/50 shadow-lg shadow-emerald-500/10' : 'bg-slate-900/60 border-slate-800/80 hover:border-slate-700'
            }`}
          >
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-1">
              <span>Resolved</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-extrabold text-emerald-400">{resolvedCount}</div>
          </div>
        </div>

        {/* Dashboard Header Actions */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">Municipal Issues Queue</h2>
            <p className="text-xs text-slate-400 mt-0.5">Filter, inspect, and dispatch city work orders</p>
          </div>

          <div className="flex items-center gap-3">
            <button 
              onClick={() => navigate('/issues/new')}
              className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-xs px-4 py-2.5 rounded-xl shadow-lg shadow-blue-600/20 transition-all flex items-center gap-2"
            >
              <PlusCircle size={16} />
              Report New Issue
            </button>
          </div>
        </div>

        {/* Issues List Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 animate-pulse">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <div key={i} className="bg-slate-900/50 rounded-2xl h-44 border border-slate-800"></div>
            ))}
          </div>
        ) : filteredIssues.length === 0 ? (
          <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-12 text-center">
            <CheckCircle2 className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-base font-semibold text-slate-300">No issues found</h3>
            <p className="text-xs text-slate-500 mt-1">No active reports match the current filter selection.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredIssues.map(issue => (
              <div 
                key={issue.id} 
                onClick={() => navigate(`/issues/${issue.id}`)}
                className="bg-slate-900/70 border border-slate-800/80 hover:border-blue-500/40 rounded-2xl p-5 hover:shadow-xl hover:shadow-blue-500/5 transition-all group cursor-pointer relative overflow-hidden flex flex-col justify-between"
              >
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-indigo-500 opacity-80" />
                
                <div>
                  <div className="flex items-center justify-between gap-2 mb-3">
                    <span className={`text-[10px] font-bold px-2.5 py-1 rounded-full uppercase tracking-wider border ${
                      issue.priority === 'HIGH' ? 'bg-red-500/10 text-red-400 border-red-500/20' : 
                      issue.priority === 'MEDIUM' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 
                      'bg-slate-800 text-slate-300 border-slate-700'
                    }`}>
                      {issue.priority || 'NORMAL'}
                    </span>
                    <span className="text-[10px] font-medium text-slate-400 bg-slate-950 px-2.5 py-1 rounded-full border border-slate-800 uppercase tracking-wider">
                      {issue.category || 'General'}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-slate-100 mb-2 leading-snug group-hover:text-blue-400 transition-colors line-clamp-2">
                    {issue.title}
                  </h3>

                  {issue.description && (
                    <p className="text-xs text-slate-400 line-clamp-2 mb-4 leading-relaxed">
                      {issue.description}
                    </p>
                  )}
                </div>

                <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${
                      issue.status === 'REPORTED' || issue.status === 'OPEN' ? 'bg-blue-400 animate-pulse' :
                      issue.status === 'IN_PROGRESS' || issue.status === 'ASSIGNED' ? 'bg-amber-400' :
                      'bg-emerald-400'
                    }`} />
                    <span className="font-semibold text-slate-300 uppercase tracking-wide text-[11px]">
                      {(issue.status || 'REPORTED').replace('_', ' ')}
                    </span>
                  </div>
                  <span className="text-[11px] text-slate-500">ID: #{issue.id}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default IssueDashboard;
