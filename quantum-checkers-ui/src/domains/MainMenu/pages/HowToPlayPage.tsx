import React from 'react';
const HowToPlayPage: React.FC = () => <main style={{maxWidth: 720, margin: 'auto', padding: 24}}>
  <h1>How to Play</h1>
  <p>Match the current board to the target. Select the left or right qubit, then apply an allowed gate. CZ acts on both qubits. You can reset a puzzle and return to it later.</p>
  <h2>Reading the circles</h2>
  <p>Black means the answer is certainly 0; white means it is certainly 1. An outline means either answer is equally likely. The middle circles show whether the two answers agree: black means agreement, white means disagreement. A dashed target circle can have any value.</p>
  <h2>Gates</h2>
  <p>X flips the Z answer. Z flips the X answer. H exchanges the X and Z answers. CZ can create correlations between the qubits.</p>
  <p>Inspired by <a href="https://medium.com/qiskit/hello-quantum-2c1c00fe830c" target="_blank" rel="noreferrer">Hello Quantum by James Wootton</a>. These are original practice puzzles for this web version.</p>
</main>;
export default HowToPlayPage;
