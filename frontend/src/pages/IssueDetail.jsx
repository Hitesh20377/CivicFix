import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ArrowLeft, MapPin, Image as ImageIcon, MessageSquare, Clock, Send } from 'lucide-react';
import api from '../services/api';

import AssignmentManager from '../components/AssignmentManager';

const IssueDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [issue, setIssue] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const [commentText, setCommentText] = useState('');
  const [submittingComment, setSubmittingComment] = useState(false);

  const fetchIssue = async () => {
    try {
      const res = await api.get(`/issues/${id}`);
      if (res.data && res.data.data) {
        setIssue(res.data.data);
      } else {
        setError('Issue not found.');
      }
    } catch (err) {
      console.error("Failed to fetch issue details:", err);
      setError('Failed to fetch issue details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIssue();
  }, [id]);

  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!commentText.trim()) return;
    
    setSubmittingComment(true);
    try {
      await api.post(`/issues/${id}/comments`, { comment: commentText });
      setCommentText('');
      // Refresh issue to get the new comment
      await fetchIssue();
    } catch (err) {
      console.error("Failed to add comment:", err);
      alert("Failed to add comment. Please try again.");
    } finally {
      setSubmittingComment(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="animate-pulse flex flex-col items-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-4"></div>
          <p className="text-slate-500 font-medium">Loading issue details...</p>
        </div>
      </div>
    );
  }

  if (error || !issue) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-6 text-center">
        <h2 className="text-2xl font-bold text-slate-800 mb-2">Oops!</h2>
        <p className="text-slate-500 mb-6">{error}</p>
        <button 
          onClick={() => navigate('/issues')}
          className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
        >
          Back to Dashboard
        </button>
      </div>
    );
  }

  // Combine comments and status changes into a single timeline if they are in the same array
  // Assuming issue.status_history contains all updates
  const timeline = [...(issue.status_history || [])].sort((a, b) => new Date(a.created_at) - new Date(b.created_at));

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <nav className="bg-white border-b border-slate-200 px-6 py-4 flex justify-between items-center sticky top-0 z-10 shadow-sm">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/issues')} className="text-slate-500 hover:text-slate-800 transition-colors">
            <ArrowLeft size={24} />
          </button>
          <h1 className="text-xl font-bold text-slate-800">Issue #{issue.id}</h1>
        </div>
      </nav>

      <main className="flex-1 max-w-4xl w-full mx-auto p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Left Column: Details */}
        <div className="md:col-span-2 space-y-6">
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
            <div className="flex justify-between items-start mb-4">
              <span className={`text-xs font-bold px-3 py-1.5 rounded-full uppercase tracking-wide
                ${issue.priority === 'HIGH' ? 'bg-red-100 text-red-700' : 
                  issue.priority === 'MEDIUM' ? 'bg-amber-100 text-amber-700' : 
                  'bg-emerald-100 text-emerald-700'}`
              }>
                {issue.priority || 'UNASSIGNED PRIORITY'}
              </span>
              <span className="text-sm font-semibold text-slate-500 bg-slate-100 px-3 py-1.5 rounded-full uppercase">
                {issue.category}
              </span>
            </div>
            
            <h2 className="text-2xl font-bold text-slate-800 mb-3">{issue.title}</h2>
            <p className="text-slate-600 whitespace-pre-line leading-relaxed mb-6">
              {issue.description}
            </p>
            
            <div className="flex items-center gap-4 text-sm text-slate-500 border-t border-slate-100 pt-4">
              <div className="flex items-center gap-1.5">
                <MapPin size={16} className="text-slate-400" />
                {issue.latitude}, {issue.longitude}
              </div>
              <div className="flex items-center gap-1.5">
                <Clock size={16} className="text-slate-400" />
                {new Date(issue.created_at).toLocaleDateString()}
              </div>
            </div>
          </div>
          
          {/* Images Section */}
          {issue.attachments && issue.attachments.length > 0 && (
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
              <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                <ImageIcon size={20} className="text-slate-400" />
                Attachments
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                {issue.attachments.map(att => (
                  <div key={att.id} className="aspect-square rounded-xl overflow-hidden bg-slate-100 border border-slate-200">
                    <img 
                      src={`http://localhost:5000/api/uploads/${att.file_path}`} 
                      alt="Issue Attachment"
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.target.onerror = null;
                        e.target.src = 'https://via.placeholder.com/300?text=Image+Not+Found';
                      }}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Timeline / Comments Section */}
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
            <h3 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
              <MessageSquare size={20} className="text-slate-400" />
              Activity & Comments
            </h3>
            
            <div className="space-y-6 mb-8">
              {timeline.length === 0 ? (
                <p className="text-slate-500 italic text-center py-4">No activity recorded yet.</p>
              ) : (
                timeline.map(item => (
                  <div key={item.id} className="flex gap-4">
                    <div className="w-10 h-10 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center flex-shrink-0 text-slate-500 font-bold">
                      {item.changed_by_id === issue.reporter_id ? 'Me' : 'S'}
                    </div>
                    <div className="flex-1 bg-slate-50 rounded-xl p-4 border border-slate-100">
                      <div className="flex justify-between items-start mb-1">
                        <span className="font-semibold text-slate-800 text-sm">
                          {item.changed_by_id === issue.reporter_id ? 'Me (Citizen)' : 'Staff'}
                        </span>
                        <span className="text-xs text-slate-400">
                          {new Date(item.created_at).toLocaleString()}
                        </span>
                      </div>
                      
                      {item.previous_status && item.new_status && item.previous_status !== item.new_status && (
                        <div className="text-xs font-medium text-slate-500 mb-2">
                          Changed status from <span className="bg-slate-200 px-1.5 py-0.5 rounded">{item.previous_status}</span> to <span className="bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded">{item.new_status}</span>
                        </div>
                      )}
                      
                      {item.comment && (
                        <p className="text-slate-700 text-sm">{item.comment}</p>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Add Comment Form */}
            <form onSubmit={handleCommentSubmit} className="flex gap-3">
              <input
                type="text"
                className="flex-1 px-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                placeholder="Write a comment..."
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                required
              />
              <button 
                type="submit" 
                disabled={submittingComment || !commentText.trim()}
                className="bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-xl transition-colors shadow-sm disabled:opacity-50 flex items-center justify-center"
              >
                <Send size={20} />
              </button>
            </form>
          </div>
        </div>

        {/* Right Column: Status Sidebar */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 sticky top-24">
            <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4">Current Status</h3>
            <div className="flex items-center gap-3 mb-6">
              <div className={`w-3 h-3 rounded-full 
                ${issue.status === 'OPEN' ? 'bg-blue-500' : 
                  issue.status === 'IN_PROGRESS' ? 'bg-amber-500' : 
                  'bg-emerald-500'}`
              }></div>
              <span className="text-lg font-bold text-slate-800">
                {issue.status.replace('_', ' ')}
              </span>
            </div>
            
            <div className="space-y-4 border-t border-slate-100 pt-4">
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase">Reporter</p>
                <p className="text-sm font-medium text-slate-800 mt-1">Me (Citizen)</p>
              </div>
              
              {issue.department && (
                <div>
                  <p className="text-xs font-semibold text-slate-500 uppercase">Department</p>
                  <p className="text-sm font-medium text-slate-800 mt-1">{issue.department.name}</p>
                </div>
              )}
            </div>
          </div>
          
          <AssignmentManager 
            issueId={issue.id} 
            currentAssignment={issue.current_assignment}
            onAssignmentUpdated={() => fetchIssue()}
          />
        </div>
      </main>
    </div>
  );
};

export default IssueDetail;
