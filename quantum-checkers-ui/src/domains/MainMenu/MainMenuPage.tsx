import React, {useState} from 'react';
import './MainMenuPage.css';
import MenuButton from '../../shared/components/MenuButton/MenuButton';
import {useAuth} from '../Auth/components/AuthContext';
import {apiRequest} from '../../shared/api';

const MainMenuPage: React.FC = () => {
  const {isAuthenticated, isStaff, refreshSession} = useAuth();
  const [error, setError] = useState('');
  const logout = async () => {
    try {
      await apiRequest('/api/logout/', {method: 'POST', body: '{}'});
      await refreshSession();
    } catch (error) {setError((error as Error).message);}
  };
  return <main id="container">
    <h1>Quantum Checkers</h1>
    <div className="button-container">
      <MenuButton to="/level-selection">Start Game</MenuButton>
      <MenuButton to="/about">About</MenuButton>
      <MenuButton to="/how-to-play">How to Play</MenuButton>
      {isStaff && <a href="/admin/">Edit levels</a>}
      {isAuthenticated ? <button onClick={logout}>Log out</button> : <MenuButton to="/login">Log in</MenuButton>}
    </div>
    {error && <p role="alert">{error}</p>}
  </main>;
};
export default MainMenuPage;
