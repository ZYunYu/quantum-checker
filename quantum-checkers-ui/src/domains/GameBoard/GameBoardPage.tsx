import React, {useEffect, useState} from 'react';
import {Link, useParams} from 'react-router-dom';
import Circle from './components/Circle';
import Square from './components/BackgroundSquare';
import Gate from './components/Gate';
import {apiRequest} from '../../shared/api';
import './GameBoardPage.css';

const positions = [[1,1], [1,2], [2,3], [3,3], [3,1], [2,1], [2,2], [3,2]];
type Circles = {[key: string]: number | null};
type CircleName = `circle${number}${number}`;
type Level = {level: number; title: string; instructions: string; allowed_gates: string[]; win_conditions: {row: number; column: number; exact?: number; min?: number; max?: number}[]} & Record<CircleName, number | null>;
interface GameSession {id: number; circles: Circles; moves: number; is_win: boolean;}

const Board = ({circles, label}: {circles: Circles; label: string}) =>
  <div className="board-wrap"><div className="game-board" role="group" aria-label={label}>
    {positions.map(([row, column]) => <React.Fragment key={`${row}${column}`}>
      <Square row={row} column={column} className={row === 1 || column === 3 ? 'orange-square' : 'dark-orange-square'} />
      <Circle probability={circles[`circle${row}${column}`] ?? null} row={row} column={column} />
    </React.Fragment>)}
  </div></div>;

const GameBoard: React.FC = () => {
  const {levelId} = useParams();
  const [level, setLevel] = useState<Level | null>(null);
  const [session, setSession] = useState<GameSession | null>(null);
  const [qubit, setQubit] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    setLevel(null);
    setSession(null);
    setError('');
    Promise.all([
      apiRequest<Level>(`/api/gamelevels/${levelId}/`),
      apiRequest<GameSession>(`/api/gamelevels/${levelId}/session/`, {method: 'POST', body: '{}'}),
    ]).then(([newLevel, newSession]) => {
      if (active) {setLevel(newLevel); setSession(newSession);}
    }).catch(error => {if (active) setError(error.message);});
    return () => {active = false;};
  }, [levelId]);
  const play = async (gate?: string) => {
    if (!session || busy) return;
    setBusy(true);
    setError('');
    try {
      setSession(gate
        ? await apiRequest<GameSession>(`/api/applygate/${session.id}/`, {
          method: 'POST', body: JSON.stringify({gate_type: gate, qubit_idx: qubit}),
        })
        : await apiRequest<GameSession>(`/api/gamelevels/${levelId}/session/`, {method: 'POST', body: '{"reset":true}'}));
    } catch (error) {setError((error as Error).message);} finally {setBusy(false);}
  };
  return <main className="game-board-container">
    <Link to="/level-selection">← All levels</Link>
    {error && <p role="alert">{error}</p>}
    {!level || !session ? (!error && <p role="status">Loading puzzle…</p>) : <>
      <h1>Level {level.level}{level.title ? `: ${level.title}` : ''}</h1>
      <p>{level.instructions}</p>
      <div className="boards">
        <section><h2>Current</h2><Board circles={session.circles} label="Current state" /></section>
        <section><h2>Target</h2><Board circles={Object.fromEntries(positions.map(([row, column]) => [`circle${row}${column}`, level[`circle${row}${column}` as CircleName]]))} label="Target state" /></section>
      </div>
      <p>Black = 1 · White = 0 · Outline = 0.5 · Dashed = any value</p>
      {level.win_conditions.length > 0 && <p>Extra targets: {level.win_conditions.map(item =>
        `circle (${item.row},${item.column}) ${item.exact !== undefined ? '= ' + item.exact : item.min + '–' + item.max}`
      ).join('; ')}</p>}
      <fieldset disabled={busy}><legend>Apply a gate to</legend>
        <label><input type="radio" name="qubit" checked={qubit === 0} onChange={() => setQubit(0)} /> Left qubit</label>
        <label><input type="radio" name="qubit" checked={qubit === 1} onChange={() => setQubit(1)} /> Right qubit</label>
      </fieldset>
      <div className="gate-controls">{['x', 'z', 'h', 'cz'].map(gate =>
        <Gate key={gate} gateType={gate} isEnabled={!busy && level.allowed_gates.includes(gate)} onApply={() => play(gate)} />
      )}</div>
      <p>CZ always acts on both qubits. Moves: {session.moves}</p>
      {session.is_win && <p className="win-message" role="status">Puzzle solved! <Link to="/level-selection">Choose another level</Link></p>}
      <button disabled={busy} onClick={() => play()}>Reset puzzle</button>
    </>}
  </main>;
};
export default GameBoard;
