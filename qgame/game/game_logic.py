import copy
import json
from io import BytesIO

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit_aer.backends.aer_simulator import AerSimulator

SUPPORTED_GATES = ['x', 'z', 'h', 'cz']


class QuantumGame():
    def __init__(self,
                 initialize: list[dict] = [],
                 win_condition: dict = None,
                 allowed_gates: list[str] = None,
                 shots: int = 1024,
                 win_threshold: float = 0.1,
                 backend=None):

        self.circuit = self.create_circuit()

        self.allowed_gates = allowed_gates if allowed_gates is not None else ['x', 'z', 'h', 'cz', 'cx']
        self.applied_gates = initialize
        self.win_condition = win_condition if win_condition is not None else {'IZ': 0, 'ZI': 0, 'IX': 0, 'XI': 0,
                                                                              'ZZ': 0, 'ZX': 0, 'XZ': 0, 'XX': 0}
        self.win_threshold = win_threshold

        self.backend = AerSimulator() if backend is None else backend
        self.shots = shots

        self.probabilities = None

        for gate_dict in initialize:
            self.apply_gate(**gate_dict)

    def create_circuit(self):
        qr = QuantumRegister(2, 'q')
        cr = ClassicalRegister(2, 'c')
        circuit = QuantumCircuit(qr, cr)
        return circuit

    def apply_gate(self, qubit_idx: int, gate: str, **params):
        gate = gate.lower()
        assert gate in self.allowed_gates, f"Gate {gate} not supported"
        getattr(self.circuit, gate)(qubit_idx)
        self.applied_gates.append({'qubit_idx': qubit_idx, 'gate': gate, **params})

    def run_circuit(self, **kwargs) -> None:
        self.probabilities = {}

        corr = ['ZZ', 'ZX', 'XZ', 'XX']
        identities = ['ZI', 'XI', 'IZ', 'IX']

        results = {}
        for basis in corr:
            temp_circuit = copy.deepcopy(self.circuit)
            for i in range(2):
                if basis[i] == 'X':
                    temp_circuit.h(i)

            temp_circuit.barrier()
            temp_circuit.measure(self.qr, self.cr)

            job = self.backend.run(temp_circuit, shots=self.shots, **kwargs)
            results[basis] = job.result().get_counts()

            for key, value in results[basis].items():
                results[basis][key] = value / self.shots

        probabilities = {}
        for identity in identities:
            probabilities[identity] = 0
            for basis, counts in results.items():
                if basis[(identity.index('I') + 1) % 2] != identity[(identity.index('I') + 1) % 2]:
                    continue
                for string, count in counts.items():
                    if string[identity.index('I')] == '1':
                        probabilities[identity] += count / 2

        for basis in corr:
            probabilities[basis] = 0
            for string, probability in results[basis].items():
                if string[0] != string[1]:
                    probabilities[basis] += probability

        for basis, probability in probabilities.items():
            self.probabilities[basis] = 1 - 2 * probability

    def check_win(self) -> bool:
        if self.probabilities is None:
            self.run_circuit()

        for pauli, prob in self.probabilities.items():
            if self.win_condition[pauli] == None:
                continue
            win_proximity = abs(prob - self.win_condition[pauli])
            if win_proximity > self.win_threshold:
                return False

    def save(self, filename: str):
        with open(filename, 'w+') as f:
            json.dump(self.applied_gates, f)

