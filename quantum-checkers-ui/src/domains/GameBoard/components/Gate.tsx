import React from 'react';
import './Gate.css';
interface GateProps {
  gateType: string;
  isEnabled: boolean;
  onApply: () => void;
}
const Gate: React.FC<GateProps> = ({gateType, isEnabled, onApply}) =>
  <button className="gate-button" disabled={!isEnabled} onClick={onApply} aria-label={`Apply ${gateType.toUpperCase()} gate`}>
    {gateType.toUpperCase()}
  </button>;
export default Gate;
