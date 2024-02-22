import React, {useState} from 'react';
import MenuButton from "../../shared/components/MenuButton/MenuButton";
import LoginForm from "./components/LoginForm";
import SignupForm from "./components/SignupForm";
import './components/AuthForm.css';


const AuthPage: React.FC = () => {
    const [isLogin, setIsLogin] = useState(true);

    const handleSignupSuccess = () => {
        setIsLogin(true); // After successful registration, switch to the login form
    };

    return (
        <div className="center-container">
            <div>
                <h2>{isLogin ? 'Login' : 'Signup'}</h2>
                {isLogin ? <LoginForm/> : <SignupForm onSignupSuccess={handleSignupSuccess}/>}
                <MenuButton
                    to={isLogin ? "/signup" : "/login"}
                    onClick={() => setIsLogin(!isLogin)}
                >
                    {isLogin ? 'Need an account? Sign up' : 'Have an account? Log in'}
                </MenuButton>

            </div>
        </div>
    );
};

export default AuthPage;
