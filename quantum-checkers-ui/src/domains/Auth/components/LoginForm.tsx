// src/domains/Auth/LoginForm.tsx
import React, {useState} from 'react';
import './AuthForm.css';
import axios from 'axios';
import {useNavigate} from 'react-router-dom';
import MenuButton from "../../../shared/components/MenuButton/MenuButton";

const LoginForm: React.FC = () => {
    const navigate = useNavigate();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [errorMessage, setErrorMessage] = useState('');


    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        axios.post('http://localhost:8000/api/login/', {
            username,
            password,
        })
            .then(response => {
                console.log('Login successful:', response.data);
                // add logic to save the token to localStorage
                navigate('/test');
            })
            .catch(error => {
                if (error.response) {
                    console.log(error.response.data.error);
                    setErrorMessage(error.response.data.error);
                    if (error.response.status === 401) {
                        const shouldRedirect = window.confirm('Invalid credentials. Do you want to sign up instead?');
                        if (shouldRedirect) {
                            // Add logic to jump to the registration page
                        }
                    }
                } else if (error.request) {
                    console.log(error.request);
                } else {
                    console.log('Error', error.message);
                }
            });
    };

    return (
        <div className="center-container">
            <form onSubmit={handleSubmit} className="auth-form">
                <div className="form-group">
                    <label htmlFor="username">Username</label>
                    <input
                        type="text"
                        id="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="password">Password</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                </div>
                {errorMessage && <div className="error-message">{errorMessage}</div>}
                <button type="submit" className="submit-button">Login</button>
            </form>
        </div>
    );
};

export default LoginForm;