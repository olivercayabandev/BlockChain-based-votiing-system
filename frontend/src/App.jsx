import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { LoginPage } from './components/auth/LoginPage';
import { RegistrationPage } from './components/auth/RegistrationPage';
import { AdminLoginPage } from './components/auth/AdminLoginPage';
import { OfficialLoginPage } from './components/auth/OfficialLoginPage';
import { VoterDashboard } from './components/voter/VoterDashboard';
import { AdminDashboard } from './components/admin/AdminDashboard';
import { OfficialDashboard } from './components/official/OfficialDashboard';
import { BlockchainVisualizer } from './components/shared/BlockchainVisualizer';
import { VerificationTool } from './components/shared/VerificationTool';
import { useAuth } from './context/AuthContext';

const styles = {
  fullHeight: { minHeight: '100vh', backgroundColor: '#f9fafb' },
};

function ProtectedAdminRoute({ children }) {
  const hasToken = localStorage.getItem('admin-token');
  if (!hasToken) {
    return <Navigate to="/admin-login" replace />;
  }
  return children;
}

function ProtectedOfficialRoute({ children }) {
  const hasToken = localStorage.getItem('official-token');
  if (!hasToken) {
    return <Navigate to="/officials-login" replace />;
  }
  return children;
}

function ProtectedVoterRoute({ children }) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  return children;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<LoginPage onSwitchPage={() => {}} />} />
      <Route path="/register" element={<RegistrationPage onSwitchPage={() => {}} />} />
      <Route path="/verify" element={<VerificationTool onSwitchPage={() => {}} />} />
      <Route path="/blockchain" element={<BlockchainVisualizer onSwitchPage={() => {}} />} />
      
      <Route path="/admin-login" element={<AdminLoginPage onSwitchPage={() => {}} />} />
      <Route path="/admin" element={
        <ProtectedAdminRoute>
          <AdminDashboard onNavigate={() => {}} />
        </ProtectedAdminRoute>
      } />
      
      <Route path="/officials-login" element={<OfficialLoginPage onSwitchPage={() => {}} />} />
      <Route path="/officials" element={
        <ProtectedOfficialRoute>
          <OfficialDashboard onNavigate={() => {}} />
        </ProtectedOfficialRoute>
      } />
      
      <Route path="/voter" element={
        <ProtectedVoterRoute>
          <VoterDashboard onNavigate={() => {}} />
        </ProtectedVoterRoute>
      } />
      
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <BrowserRouter>
          <div style={styles.fullHeight}>
            <AppRoutes />
          </div>
        </BrowserRouter>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;