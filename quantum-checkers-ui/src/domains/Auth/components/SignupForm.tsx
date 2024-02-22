// src/domains/Auth/SignupForm.tsx
import React, {useState} from 'react';
import './AuthForm.css';
import axios from 'axios';

interface SignupFormProps {
    onSignupSuccess?: () => void;
}

const SignupForm: React.FC<SignupFormProps> = ({onSignupSuccess}) => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        axios.post('http://localhost:8000/api/signup/', {  // 确保URL匹配你的Django服务器地址
            username,
            email,
            password,
        })
            .then(response => {
                console.log(response.data.message);
                // onSignupSuccess();
            })
            .catch(error => {
                if (error.response) {
                    console.log(error.response.data.error);
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
                    <label htmlFor="email">Email</label>
                    <input
                        type="email"
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
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
                <button type="submit" className="submit-button">Sign Up</button>
            </form>
        </div>
    );
};

export default SignupForm;
