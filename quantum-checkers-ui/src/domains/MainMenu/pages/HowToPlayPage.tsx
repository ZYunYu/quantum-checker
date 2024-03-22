import React from 'react';
import './AboutPage.css';

const HowToPlayPage: React.FC = () => (
  <div className="howtoplay">
    <h2>How to Play</h2>
    <p>To play this game, you will apply logic gates to the two qubits on the grid. You will do this through the two gate selectors on either side of the main grid. Through these gates, you can change the color of the qubits and their outputs. Your goal is to make the output of your grid match that of the small grid to the left of the main grid. Use the explanations before each level as hints and advice on how to beat the level. We wish you luck!</p>

    <h2>What is a Qubit?</h2>
    <p>A qubit is a tiny particle that is like a computer bit, but it can be more things than just 0 or 1. Unlike regular bits, qubits can be in a state called a “superposition”, a state in between 0 and 1. In this game, a qubit with a value of 0 is represented as a white qubit, a 1 is a black qubit. A grey qubit is a qubit that is in a superposition. We can change the value of a qubit using logic gates!</p>

    <h2>What is a Logic Gate?</h2>
    <p>A logic gate is similar to a math operation. When you apply a logic gate to a qubit, you are able to change the qubit in a predictable way. Just like how you can use addition or subtraction to change the outcome of two numbers, you can use logic gates to change the outcome of one or more qubits! You will encounter five different logic gates in this game, the “X”, “Y”, “Z”, “H”, and “CZ” gates. The specifics of these gates will be explained before the levels you will play.</p>
  </div>
);

export default HowToPlayPage;
