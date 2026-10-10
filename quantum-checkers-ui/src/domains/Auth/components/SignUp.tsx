import React, {useState, useEffect} from 'react';
import {useNavigate, Link} from 'react-router-dom';
import {apiRequest} from '../../../shared/api';
import './AuthForm.css';

const SignUp: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [studentId, setStudentId] = useState('');
  const [classroomId, setClassroomId] = useState('');
  const [classrooms, setClassrooms] = useState<{id: number; name: string}[]>([]);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  useEffect(() => {
    apiRequest<{id: number; name: string}[]>('/api/classrooms/').then(setClassrooms).catch(error => setError(error.message));
  }, []);
  const handleSignUp = async (event: React.FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError('');
    try {
      await apiRequest('/api/signup/', {method: 'POST', body: JSON.stringify({
        username, password, email, student_id: studentId,
        classroom_id: classroomId ? Number(classroomId) : null,
      })});
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
      <p><label htmlFor="student-id">Student ID / 学号</label><input id="student-id" maxLength={64} pattern="[A-Za-z0-9_-]+" value={studentId} onChange={e => setStudentId(e.target.value)} required /></p>
      <p><label htmlFor="classroom">Classroom / 班级 (optional)</label><select id="classroom" value={classroomId} onChange={e => setClassroomId(e.target.value)}>
        <option value="">Unassigned / 未分班</option>
        {classrooms.map(classroom => <option key={classroom.id} value={classroom.id}>{classroom.name}</option>)}
      </select></p>
      <p><label htmlFor="password">Password</label><input id="password" type="password" autoComplete="new-password" minLength={8} value={password} onChange={e => setPassword(e.target.value)} required /></p>
      <button disabled={busy}>{busy ? 'Creating…' : 'Sign up'}</button>
    </form>
    <p><Link to="/login">Back to login</Link></p>
  </main>;
};
export default SignUp;
