import numpy as np
from pyquil import get_qc, Program
from pyquil.gates import *
from pyquil.quil import address_qubits
from pyquil.quilatom import QubitPlaceholder
from pyquil.api import QVMConnection
from pyquil.api import QuantumComputer
import random

class QuantumDebugger(object):

    def __init__(self, num_iters, q_num):

        #Increase this later
        self.num_iters = num_iters
        self.q_num = q_num
        self.q_list = [i for i in range(self.q_num)]
        self.X = np.array([[0,1],[1,0]])
        self.Y = np.array([[0,-1j],[1j,0]])
        self.Z = np.array([[1,0],[0,-1]])
        self.I = np.array([[1,0],[0,1]])
        self.QC = get_qc("8q-qvm")

    def basicTomography(self, p: Program()):
        #p is the program we are running tomography on
        #q is a list of qubit indices

        #Takes in a program and runs it multiple times in order to figure out the X, Y, Z and I contributions
        #Returns a numpy array representing the density matrix

        #Measure X:

        p_x = Program()
        xo = p_x.declare('ro', 'BIT', self.q_num)
        for instruction in p:
            p_x += instruction
        for q in self.q_list:
            p_x += RY(-np.pi/2, q)
        for q in self.q_list:
            p_x += MEASURE(q, xo[q])

        p_x.wrap_in_numshots_loop(self.num_iters)

        #print(p_x)
        executable_x = self.QC.compile(p_x)
        outputs_x = np.array(self.QC.run(executable_x))
        #NOTE: Why are we using -1 and 1 as values here?
        outputs_x[outputs_x == 0] = -1
        outputs_x[outputs_x == 1] = 1
        c_x = np.mean(outputs_x, axis = 0)

        #Measure Y:

        p_y = Program()
        yo = p_y.declare('ro', 'BIT', self.q_num)
        for instruction in p:
            p_y += instruction
        for q in self.q_list:
            p_y += RX(np.pi/2, q)
        for q in self.q_list:
            p_y += MEASURE(q, yo[q])

        p_y.wrap_in_numshots_loop(self.num_iters)

        #print(p_x)
        executable_y = self.QC.compile(p_y)
        outputs_y = np.array(self.QC.run(executable_y))
        outputs_y[outputs_y == 0] = -1
        outputs_y[outputs_y == 1] = 1
        c_y = np.mean(outputs_y, axis = 0)

        #Measure Z:

        p_z = Program()
        zo = p_z.declare('ro', 'BIT', self.q_num)
        for instruction in p:
            p_z += instruction
        for q in self.q_list:
            p_z += MEASURE(q, zo[q])

        p_y.wrap_in_numshots_loop(self.num_iters)

        executable_z = self.QC.compile(p_z)
        outputs_z = np.array(self.QC.run(executable_z))
        outputs_z[outputs_z == 0] = -1
        outputs_z[outputs_z == 1] == 1
        c_z = np.mean(outputs_z, axis = 0)

        #Trace of rho is 1
        rho = 0.5 * (self.I + c_x * self.X + c_y * self.Y + c_z * self.Z)
        print(rho)

qd = QuantumDebugger(1000, 1)
prog = Program()
prog += H(0)

qd.basicTomography(prog)
