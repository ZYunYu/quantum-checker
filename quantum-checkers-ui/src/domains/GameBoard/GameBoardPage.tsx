import React, {useEffect, useState} from 'react';
import axios from 'axios';
import Circle from './components/Circle';
import './GameBoardPage.css';
import Square from './components/BackgroundSquare';
import {useParams} from "react-router-dom";

interface GameLevelDetails {
    id: number;
    level: number;
    circle11: number | null;
    circle12: number | null;
    circle21: number | null;
    circle22: number | null;
    circle23: number | null;
    circle31: number | null;
    circle32: number | null;
    circle33: number | null;
    // gate_z: boolean;
    // gate_h: boolean;
    // gate_x: boolean;
    // gate_cz: boolean;
}

interface QuantumCheckersProps {
    levelId: number;
}

const GameBoard: React.FC = () => {
    const [gameData, setGameData] = useState<GameLevelDetails | null>(null);
    const { levelId } = useParams();

    useEffect(() => {
        axios.get(`http://localhost:8000/api/gamelevels/${levelId}/`)
            .then(response => {
                console.log("Data fetched:", response.data);
                setGameData(response.data);
            })
            .catch(error => console.error('Error fetching game data:', error));
    }, [levelId]);


    return (
        <div className={"game-board-container"}>
            <div className={"game-board"}>
                {gameData ? (
                    <>
                        <Square row={1} column={1} className="orange-square"/>
                        <Square row={1} column={2} className="orange-square"/>
                        <Square row={2} column={3} className="orange-square"/>
                        <Square row={3} column={3} className="orange-square"/>
                        <Square row={2} column={1} className="dark-orange-square"/>
                        <Square row={2} column={2} className="dark-orange-square"/>
                        <Square row={3} column={1} className="dark-orange-square"/>
                        <Square row={3} column={2} className="dark-orange-square"/>
                        <Circle probability={gameData.circle11} row={1} column={1}/>
                        <Circle probability={gameData.circle12} row={1} column={2}/>
                        <Circle probability={gameData.circle21} row={2} column={1}/>
                        <Circle probability={gameData.circle22} row={2} column={2}/>
                        <Circle probability={gameData.circle23} row={2} column={3}/>
                        <Circle probability={gameData.circle31} row={3} column={1}/>
                        <Circle probability={gameData.circle32} row={3} column={2}/>
                        <Circle probability={gameData.circle33} row={3} column={3}/>
                    </>
                ) : null}
            </div>
        </div>
    );
};

export default GameBoard;

