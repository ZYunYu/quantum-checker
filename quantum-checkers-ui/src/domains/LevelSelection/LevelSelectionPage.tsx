import React, {useEffect, useState} from 'react';
import './LevelSelectionPage.css';
import MenuButton from '../../shared/components/MenuButton/MenuButton';
import {apiRequest} from '../../shared/api';

interface GameLevel {id: number; level: number; title: string;}
const LevelSelection: React.FC = () => {
  const [levels, setLevels] = useState<GameLevel[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    apiRequest<GameLevel[]>('/api/gamelevels/').then(setLevels)
      .catch(error => setError(error.message)).finally(() => setLoading(false));
  }, []);
  return <main className="level-selection-container"><div className="level-selection">
    <h1 className="title">Select Level</h1>
    {loading && <p role="status">Loading levels…</p>}
    {error && <p role="alert">{error}</p>}
    {!loading && !error && levels.length === 0 && <p>No levels yet. An administrator can add them in the admin page.</p>}
    <div className="button-container">{levels.map(level =>
      <MenuButton key={level.id} to={`/game/${level.level}`} className="button">
        Level {level.level}{level.title ? `: ${level.title}` : ''}
      </MenuButton>
    )}<MenuButton to="/">Main menu</MenuButton></div>
  </div></main>;
};
export default LevelSelection;
