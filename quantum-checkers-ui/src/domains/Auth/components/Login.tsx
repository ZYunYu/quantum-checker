import React, {useState} from 'react';
import {useNavigate, Link} from 'react-router-dom';
import {useAuth} from './AuthContext';
import {apiRequest} from '../../../shared/api';
import './AuthForm.css';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  const {refreshSession} = useAuth();
  const handleLogin = async (event: React.FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError('');
    try {
      await apiRequest('/api/login/', {method: 'POST', body: JSON.stringify({username, password})});
      await refreshSession();
      navigate('/');
    } catch (error) {
      setError((error as Error).message);
    } finally {
      setBusy(false);
    }
  };
  return <main className="auth-container">
    <h1>Log in</h1>
    {error && <p role="alert">{error}</p>}
    <form onSubmit={handleLogin}>
      <p><label htmlFor="username">Username</label><input id="username" autoComplete="username" value={username} onChange={e => setUsername(e.target.value)} required /></p>
      <p><label htmlFor="password">Password</label><input id="password" type="password" autoComplete="current-password" value={password} onChange={e => setPassword(e.target.value)} required /></p>
      <button disabled={busy}>{busy ? 'Logging in…' : 'Log in'}</button>
    </form>
    <p><Link to="/signup">Create an account</Link></p>
  </main>;
};
export default Login;
