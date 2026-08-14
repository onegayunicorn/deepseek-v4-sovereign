import numpy as np

def ket(a, b):
    return np.array([a, b])

def tensor(a, b):
    return np.kron(a, b)

def hadamard():
    return np.array([[1, 1], [1, -1]]) / np.sqrt(2)

def cnot():
    return np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
