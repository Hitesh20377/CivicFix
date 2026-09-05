import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Home from './pages/Home';
import Register from './pages/Register';
import Login from './pages/Login';
import IssueDashboard from './pages/IssueDashboard';
import CreateIssue from './pages/CreateIssue';
import IssueDetail from './pages/IssueDetail';

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) return <div className="flex h-screen items-center justify-center bg-slate-950 text-slate-200">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  
  return children;
};

const App = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-slate-950 text-slate-100 font-sans antialiased">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route 
              path="/issues" 
              element={
                <ProtectedRoute>
                  <IssueDashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/issues/new" 
              element={
                <ProtectedRoute>
                  <CreateIssue />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/issues/:id" 
              element={
                <ProtectedRoute>
                  <IssueDetail />
                </ProtectedRoute>
              } 
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
