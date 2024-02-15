import React, {useEffect, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import axios from 'axios';
import './LevelSelectionPage.css';
import MenuButton from "../../shared/components/MenuButton/MenuButton";

interface GameLevel {
    id: number;
    level: number;
}

interface LevelSelectionProps {
    setSelectedLevel: (level: number) => void;
}

const LevelSelection: React.FC<LevelSelectionProps> = ({setSelectedLevel}) => {
    const [levels, setLevels] = useState<GameLevel[]>([]);
    const navigate = useNavigate();

    useEffect(() => {
        axios.get('http://localhost:8000/api/gamelevels/')
            .then(response => {
                setLevels(response.data);
            })
            .catch(error => console.error('Error fetching levels:', error));
    }, []);

    const handleLevelSelect = (levelNumber: number) => {
        navigate(`/game/${levelNumber}`);
    };

    return (
        <div className="level-selection-container">
            <div className="level-selection">
                <h1 className="title">Select Level</h1>
                <div className="button-container">
                    {levels.map((level) => (
                        <MenuButton
                            key={level.id}
                            to={`/game/${level.level}`}
                            className="button"
                            onClick={() => handleLevelSelect(level.level)}
                        >
                            Level {level.level}
                        </MenuButton>
                    ))}
                </div>
            </div>
        </div>

    );
};

export default LevelSelection;


