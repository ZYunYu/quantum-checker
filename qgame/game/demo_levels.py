from .game_logic import QuantumGame

def demo_levels():
    specifications = [
        (1, 'Flip the left qubit', 'Select the left qubit and use X to match the target.', [], [{'gate': 'x', 'qubit_idx': 0}], ['x']),
        (2, 'Change the question', 'Use H on the left qubit to exchange its X and Z answers.', [], [{'gate': 'h', 'qubit_idx': 0}], ['x', 'h']),
        (3, 'Flip the X answer', 'The left qubit starts in |+〉. Use Z to make its X answer white.', [{'gate': 'h', 'qubit_idx': 0}], [{'gate': 'z', 'qubit_idx': 0}], ['z', 'h']),
        (4, 'Connect the qubits', 'Both qubits start in |+〉. Use CZ to create the target correlations.', [{'gate': 'h', 'qubit_idx': 0}, {'gate': 'h', 'qubit_idx': 1}], [{'gate': 'cz'}], ['x', 'z', 'h', 'cz']),
    ]
    result = []
    for number, title, instructions, initial, solution, gates in specifications:
        result.append({
            'level': number, 'title': title, 'instructions': instructions,
            'initial_gates': initial, 'win_conditions': [],
            **{f'gate_{gate}': gate in gates for gate in ('x', 'z', 'h', 'cz')},
            **QuantumGame(initial + solution).run_circuit(),
        })
    return result
