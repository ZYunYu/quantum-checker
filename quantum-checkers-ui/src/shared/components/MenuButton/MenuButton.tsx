import React from 'react';
import {Link} from 'react-router-dom';
import './MenuButton.css';

interface MenuButtonProps {
    to: string;
    className?: string;
    onClick?: () => void;
    children: React.ReactNode;
}

const MenuButton: React.FC<MenuButtonProps> = ({to, children}) => (
    <Link to={to} className="menu-button">
        {children}
    </Link>
);

export default MenuButton;