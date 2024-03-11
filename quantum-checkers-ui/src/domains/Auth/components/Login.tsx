import React, {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {useAuth} from './AuthContext';
import Cookies from 'universal-cookie';

const Login: React.FC = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const cookies = new Cookies();
    const navigate = useNavigate();
    const {setIsAuthenticated} = useAuth();

    const handleLogin = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        const csrfToken = cookies.get('csrftoken');

        try {
            const response = await fetch('http://localhost:8000/api/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken || '',
                },
                credentials: 'include',
                body: JSON.stringify({username, password}),
            });

            if (!response.ok) {
                // If the response status code is not 2xx, the login failed
                const errorData = await response.json();
                const errorMessage = errorData.error || 'Login failed. Please try again.';
                setError(errorMessage);
                return;
            }

            const responseData = await response.json();
            setIsAuthenticated(true);
            navigate('/test');
        } catch (error) {
            console.error('Login error:', error);
            setError('An error occurred. Please try again.');
        }
    };


    return (
        <div>
            <h2>Login</h2>
            {error && <div className="error">{error}</div>}
            <form onSubmit={handleLogin}>
                <div>
                    <label htmlFor="username">Username:</label>
                    <input
                        type="text"
                        id="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label htmlFor="password">Password:</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button type="submit">Login</button>
                <button type="button" onClick={() => navigate('/signup')}>Sign Up</button>
            </form>
        </div>
    );
};

export default Login;
