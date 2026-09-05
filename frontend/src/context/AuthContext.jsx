import React, { createContext, useState, useEffect, useContext } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      // In a real app, we might want to fetch user profile here.
      // For now, if we have a token, we assume logged in.
      // Let's use the health check just to verify backend is up.
      api.get('/health')
        .then(() => {
          setUser({ token });
        })
        .catch(() => {
          localStorage.removeItem('token');
          setUser(null);
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    try {
      // CivicFIX auth endpoint. Let's assume standard POST /auth/login
      const response = await api.post('/auth/login', { email, password });
      const { access_token } = response.data;
      if (access_token) {
        localStorage.setItem('token', access_token);
        setUser({ token: access_token });
        return true;
      }
      return false;
    } catch (error) {
      console.error("Login failed", error);
      throw error;
    }
  };

  const register = async (fullName, email, password) => {
    try {
      const response = await api.post('/auth/register', { 
        full_name: fullName, 
        email, 
        password,
        role: 'citizen'
      });
      return response.data;
    } catch (error) {
      console.error("Registration failed", error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
