import React from 'react';
import {BrowserRouter as Router, Route, Routes, Navigate} from 'react-router-dom';
import {MainMenu} from './domains/MainMenu';
import AboutPage from './domains/MainMenu/pages/AboutPage';
import HowToPlayPage from './domains/MainMenu/pages/HowToPlayPage';
import {LevelSelection} from './domains/LevelSelection';
import {GameBoard} from './domains/GameBoard';
import Login from './domains/Auth/components/Login';
import SignUp from './domains/Auth/components/SignUp';
import {AuthProvider, useAuth} from './domains/Auth/components/AuthContext';
import {UserIdDisplay} from './shared/components/UserIdDisplay';
import './App.css';
import './shared/styles/base.css';

const ProtectedRoute = ({children}: {children: JSX.Element}) => {
  const {isAuthenticated, loading} = useAuth();
  if (loading) return <p role="status">Loading…</p>;
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};
function App() {
  return <AuthProvider><div className="App"><Router><Routes>
    <Route path="/login" element={<Login />} />
    <Route path="/signup" element={<SignUp />} />
    <Route path="/" element={<MainMenu />} />
    <Route path="/test" element={<MainMenu />} />
    <Route path="/level-selection" element={<ProtectedRoute><LevelSelection /></ProtectedRoute>} />
    <Route path="/game/:levelId" element={<ProtectedRoute><GameBoard /></ProtectedRoute>} />
    <Route path="/about" element={<AboutPage />} />
    <Route path="/how-to-play" element={<HowToPlayPage />} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes><UserIdDisplay /></Router></div></AuthProvider>;
}
export default App;
