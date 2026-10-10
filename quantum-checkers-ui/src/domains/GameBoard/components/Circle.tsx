import React from 'react';
interface CircleProps {probability: number | null; row: number; column: number;}
const Circle: React.FC<CircleProps> = ({probability, row, column}) => {
  const outline = probability === 0.5;
  const unspecified = probability === null;
  const grey = probability === null ? 0 : Math.round((1 - probability) * 255);
  return <div title={unspecified ? 'Any value' : `P(0 / equal): ${probability}`}
    aria-label={`Circle ${row},${column}: ${unspecified ? 'any value' : probability}`}
    style={{
      backgroundColor: outline || unspecified ? 'transparent' : `rgb(${grey},${grey},${grey})`,
      border: `3px ${unspecified ? 'dashed' : 'solid'} ${outline || unspecified ? 'var(--color-text)' : '#777'}`,
      width: '70%', height: '70%', margin: 'auto', borderRadius: '50%', boxSizing: 'border-box',
      gridRow: 4 - row, gridColumn: column, zIndex: 2,
    }} />;
};
export default Circle;
