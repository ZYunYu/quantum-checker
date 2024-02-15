import React, {useState} from 'react';

interface CircleProps {
    probability: number | null;
    row: number;
    column: number;
}

const Circle: React.FC<CircleProps> = ({probability, row, column}) => {
    const [showProbability, setShowProbability] = useState(false);

    const getGreyScale = (prob: number) => {
        const scaleValue = Math.floor(prob * 255);
        return `rgb(${scaleValue}, ${scaleValue}, ${scaleValue})`;
    };

    const textColor = probability !== null && probability > 0.5 ? 'white' : 'black';
    const backgroundColor = probability === 1 ? 'black' : probability === 0 ? 'white' : probability === null ? 'transparent' : getGreyScale(probability);

    const circleStyle: React.CSSProperties = {
        backgroundColor: probability === null ? 'transparent' : backgroundColor,
        borderColor: probability === null ? 'white' : 'transparent',
        borderWidth: probability === null ? '2px' : '0',
        borderStyle: 'solid',
        color: textColor,
        width: '80%',
        height: '80%',
        margin: 'auto',
        borderRadius: '50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '12px',
        boxSizing: 'border-box',
        gridRow: 4 - row,
        gridColumn: column,
        zIndex: 2,

    };

    return (
        <div
            style={circleStyle}
            onMouseEnter={() => setShowProbability(true)}
            onMouseLeave={() => setShowProbability(false)}
        >
            <div style={{transform: 'rotate(-45deg)'}}>
                {showProbability && probability !== null && probability.toFixed(2)}
            </div>
        </div>
    );
};

export default Circle;
