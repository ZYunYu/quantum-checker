import React, {useState} from 'react';
import {useNavigate, Link} from 'react-router-dom';
import {apiRequest} from '../../../shared/api';
import './AuthForm.css';

const SignUp: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  const handleSignUp = async (event: React.FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError('');
    try {
      await apiRequest('/api/signup/', {method: 'POST', body: JSON.stringify({username, password, email})});
      navigate('/login');
    } catch (error) {
      setError((error as Error).message);
    } finally {
      setBusy(false);
    }
  };
  return <main className="auth-container">
    <h1>Create an account</h1>
    {error && <p role="alert">{error}</p>}
    <form onSubmit={handleSignUp}>
      <p><label htmlFor="username">Username</label><input id="username" autoComplete="username" maxLength={150} value={username} onChange={e => setUsername(e.target.value)} required /></p>
      <p><label htmlFor="email">Email (optional)</label><input id="email" type="email" autoComplete="email" value={email} onChange={e => setEmail(e.target.value)} /></p>
      <p><label htmlFor="password">Password</label><input id="password" type="password" autoComplete="new-password" minLength={8} value={password} onChange={e => setPassword(e.target.value)} required /></p>
      <button disabled={busy}>{busy ? 'Creating…' : 'Sign up'}</button>
    </form>
    <p><Link to="/login">Back to login</Link></p>
  </main>;
};
export default SignUp;
