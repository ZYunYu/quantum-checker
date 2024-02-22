import React from 'react';
import axios from 'axios';
import './Gate.css';

interface GateProps {
    gateType: 'x' | 'z' | 'h' | 'cz';
    isEnabled: boolean;
    sessionId?: number;
    qubitIdx?: number;
    onUpdate?: () => void;
}

const Gate: React.FC<GateProps> = ({gateType, isEnabled, sessionId, qubitIdx, onUpdate}) => {
    const applyGate = async () => {
        if (!isEnabled) return;

        try {
            const response = await axios.post(`http://localhost:8000/api/applygate/${sessionId}/`, {
                gate_type: gateType,
                qubit_idx: qubitIdx,
            });

            console.log('Gate applied successfully:', response.data);
        } catch (error) {
            console.error('Error applying gate:', error);
        }
    };

    return (
        <button className={`gate-button ${isEnabled ? '' : 'disabled'}`} disabled={!isEnabled} onClick={applyGate}>
            <div className="gate-type">{gateType.toUpperCase()}</div>
            <div className="gate-label">GATE</div>
        </button>
    );
};

export default Gate;
