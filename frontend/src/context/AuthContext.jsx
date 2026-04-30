import React, { useState, createContext, useContext } from 'react';
import PropTypes from 'prop-types';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('voting-token') || '');
  const [user, setUser] = useState(() => {
    const u = localStorage.getItem('voting-user');
    return u ? JSON.parse(u) : null;
  });

  const login = (newToken, userData) => {
    localStorage.setItem('voting-token', newToken);
    localStorage.setItem('voting-user', JSON.stringify(userData));
    setToken(newToken);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('voting-token');
    localStorage.removeItem('voting-user');
    setToken('');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ token, user, login, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
}

AuthProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    return { token: '', user: null, login: () => {}, logout: () => {}, isAuthenticated: false };
  }
  return context;
}
