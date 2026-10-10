"""Exact two-qubit simulation.

Bit 0 is the left qubit. Pauli strings use q1-q0 ordering.
Circles show P(0) or P(equal): 1 black, 0 white, 0.5 outline.
"""
import math

SUPPORTED_GATES = ('x', 'z', 'h', 'cz')
CIRCLE_PAULIS = {
    'circle11': 'IZ', 'circle12': 'IX', 'circle23': 'XI', 'circle33': 'ZI',
    'circle31': 'ZZ', 'circle21': 'ZX', 'circle22': 'XX', 'circle32': 'XZ',
}


def validate_gates(gates):
    if not isinstance(gates, list) or len(gates) > 256:
        raise ValueError('Initial gates must be a list of at most 256 operations.')
    for item in gates:
        if not isinstance(item, dict) or item.get('gate') not in SUPPORTED_GATES:
            raise ValueError('Supported gates are x, z, h and cz.')
        if item['gate'] != 'cz' and (type(item.get('qubit_idx')) is not int or item['qubit_idx'] not in (0, 1)):
            raise ValueError('X, Z and H need qubit_idx 0 or 1.')


class QuantumGame:
    def __init__(self, initialize=None, allowed_gates=None):
        self.allowed_gates = list(SUPPORTED_GATES) if allowed_gates is None else allowed_gates
        self.state = [1.0, 0.0, 0.0, 0.0]
        self.applied_gates = []
        gates = initialize or []
        validate_gates(gates)
        for operation in gates:
            self._apply(operation['gate'], operation.get('qubit_idx', 0))

    def _apply(self, gate, qubit_idx):
        if gate == 'cz':
            self.state[3] *= -1
        else:
            mask = 1 << qubit_idx
            for index in range(4):
                if index & mask:
                    continue
                other = index | mask
                a, b = self.state[index], self.state[other]
                if gate == 'x':
                    self.state[index], self.state[other] = b, a
                elif gate == 'z':
                    self.state[other] = -b
                elif gate == 'h':
                    self.state[index], self.state[other] = (a + b) / math.sqrt(2), (a - b) / math.sqrt(2)
        self.applied_gates.append({'gate': gate, **({'qubit_idx': qubit_idx} if gate != 'cz' else {})})

    def apply_gate(self, qubit_idx, gate):
        if gate not in self.allowed_gates:
            raise ValueError('This gate is not allowed in this level.')
        validate_gates([{'gate': gate, 'qubit_idx': qubit_idx}])
        self._apply(gate, qubit_idx)

    def run_circuit(self):
        self.probabilities = {}
        for field, pauli in CIRCLE_PAULIS.items():
            expectation = 0.0
            for index, amplitude in enumerate(self.state):
                other, sign = index, 1
                for bit, operator in enumerate(reversed(pauli)):
                    if operator == 'X':
                        other ^= 1 << bit
                    elif operator == 'Z' and index & (1 << bit):
                        sign *= -1
                expectation += self.state[other] * amplitude * sign
            self.probabilities[field] = round(max(0, min(1, (1 + expectation) / 2)), 10)
        return self.probabilities

    def check_win(self, level):
        circles = self.run_circuit()
        targets = {field: getattr(level, field) for field in CIRCLE_PAULIS if getattr(level, field) is not None}
        for condition in level.win_conditions:
            field = f"circle{condition['row']}{condition['column']}"
            value = circles[field]
            if 'exact' in condition:
                if abs(value - condition['exact']) > 1e-6:
                    return False
            elif not condition['min'] - 1e-6 <= value <= condition['max'] + 1e-6:
                return False
        return bool(targets or level.win_conditions) and all(abs(circles[field] - target) <= 1e-6 for field, target in targets.items())
