import React, {useState} from 'react';
import {BrowserRouter, BrowserRouter as Router, Route, Routes} from 'react-router-dom';
import {MainMenu} from './domains/MainMenu'
import AboutPage from './domains/MainMenu/pages/AboutPage';
import HowToPlayPage from './domains/MainMenu/pages/HowToPlayPage';
import {LevelSelection} from './domains/LevelSelection';
import {GameBoard} from './domains/GameBoard';
import './App.css';
import './shared/styles/base.css';


function App() {
    const [selectedLevel, setSelectedLevel] = useState<number | null>(null);


    return (
        <div className="App">
            <Router>
                <Routes>
                    <Route path="/test" element={<MainMenu/>}/>
                    <Route path="/level-selection" element={<LevelSelection setSelectedLevel={setSelectedLevel}/>}/>
                    <Route path="/game/:levelId" element={<GameBoard/>}/>
                    <Route path="/about" element={<AboutPage/>}/>
                    <Route path="/how-to-play" element={<HowToPlayPage/>}/>
                </Routes>
            </Router>
        </div>
    );
}

export default App;
