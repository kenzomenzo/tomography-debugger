import numpy as np

from pyquil import Program
from pyquil.gates import *
from pyquil.quil import address_qubits
from pyquil.quilatom import QubitPlaceholder
from pyquil.api import QVMConnection
import random

class QuantumDebugger(object):

    def __init__(self, num_iters):

        #Increase this later
        self.num_iters = num_iters
        self.X = np.array([[0,1],[1,0]])
        self.Y = np.array([[0,-1j],[1j,0]])
        self.Z = np.array([[1,0],[0,-1]])
        self.I = np.array([[1,0],[0,1]])

    def basicTomography(self, p: Program(), q_list):
        #p is the program we are running tomography on
        #q is a list of qubit indices

        #Takes in a program and runs it multiple times in order to figure out the X, Y, Z and I contributions
        #Returns a numpy array representing the density matrix

        #Only generates matrix for qubit 0

        q_num = len(q_list)

        #NOTE: Make sure that the memory registers don't conflict!!!

        #Measure X:

        p_x = Program()
        xo = p.declare('xo', 'BIT', q_num)
        for instruction in p:
            p_x += instruction
        for q in q_list:
            p_x += RY(-np.pi/2, q)
            p_x += MEASURE(q, xo[q])

        outputs_x = np.array(qvm.run(p_x, trials=self.num_iters))
        outputs_x[outputs_x == 0] = -1
        outputs_x[outputs_x == 1] = 1
        c_x = np.mean(outputs_x, axis = 0)


        #Measure Y:

        p_y = Program()
        yo = p.declare('yo', 'BIT', q_num)
        for instruction in p:
            p_y += instruction
        for q in q_list:
            p_y += RX(np.pi/2, q)
            p_y += MEASURE(q, yo[q])

        outputs_y = np.array(qvm.run(p_y, trials=self.num_iters))
        outputs_y[outputs_y == 0] = -1
        outputs_y[outputs_y == 1] == 1
        c_y = np.mean(outputs_y, axis = 0)

        #Measure Z:

        p_z = Program()
        zo = p.declare('zo', 'BIT', q_num)
        for instruction in p:
            p_z += instruction
        for q in q_list:
            p_z += MEASURE(q, zo[q])

        outputs_z = np.array(qvm.run(p_z, trials=self.num_iters))
        outputs_z[outputs_z == 0] = -1
        outputs_z[outputs_z == 1] == 1
        c_z = np.mean(outputs_z, axis = 0)

        #Trace of rho is 1
        rho = 0.5 * (self.I + c_x * self.X + c_y * self.Y + c_z * self.Z)
        print(rho)

qvm = QVMConnection() #GET RID OF THIS LATER!

qd = QuantumDebugger(10)
prog = Program()
prog += H(0)
prog += CNOT(0, 1)

q_list = [0]

qd.basicTomography(prog, q_list)
