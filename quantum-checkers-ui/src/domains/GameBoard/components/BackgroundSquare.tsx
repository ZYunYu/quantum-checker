import React from 'react';
import './BackgroundSquare.css';

const Square = ({ row, column, className }: { row: number; column: number; className: string }) => {
  const style = {
    gridRow: 4 - row,
    gridColumn: column,
  };

  return <div className={`square ${className}`} style={style}></div>;
};

export default Square;
