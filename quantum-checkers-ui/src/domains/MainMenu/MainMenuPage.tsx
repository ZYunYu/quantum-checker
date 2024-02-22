import React from 'react';
import './MainMenuPage.css';
import MenuButton from '../../shared/components/MenuButton/MenuButton';

const MainMenuPage: React.FC = () => (


    <div id="container">
        <h1>Main Menu</h1>
        <div className="button-container">
            <MenuButton to="/auth">Login</MenuButton>
            <MenuButton to="/level-selection">Start Game</MenuButton>
            <MenuButton to="/about">About</MenuButton>
            <MenuButton to="/how-to-play">How to Play</MenuButton>
            <MenuButton to="/ranking-list">Ranking List</MenuButton>
        </div>
    </div>

);

export default MainMenuPage;
