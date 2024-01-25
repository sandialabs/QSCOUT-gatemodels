# Copyright 2020 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.
from numpy import abs, diag, pi, kron

import pygsti

from .jaqal_gates import ALL_GATES
from .jaqal_action import U_R, U_Rz, U_MS, U_XX, U_YY, U_ZZ
from .stretched import jaqal_gates as stretched
from jaqalpaq.emulator.pygsti import AbstractNoisyNativeEmulator


class SNLToy1(AbstractNoisyNativeEmulator):
    """Version 1 error model of the QSCOUT native gates."""

    # This tells AbstractNoisyNativeEmulator what gate set we're modeling:
    jaqal_gates = ALL_GATES.copy()
    jaqal_gates.update(stretched.ALL_GATES)

    def __init__(self, *args, **kwargs):
        """Builds a MyCustomEmulator instance for particular parameters

        :param depolarization float: (default 1e-3) The depolarization during one pi/2
          gate.
        :param rotation_error float: (default 1e-2) The over-rotation angle during one
          pi/2 gate.
        :param phase_error: (default 1e-2) The error in the x-y angle for (non-Z)
          rotation gates.
        """
        # Equivalent to
        # self.depolarization = kwargs.pop('depolarization', 1e-3 )
        # ...
        self.set_defaults(
            kwargs, depolarization=1e-3, rotation_error=1e-2, phase_error=1e-2
        )

        # Pass through the balance of the parameters to AbstractNoisyNativeEmulator
        # In particular: passes the number of qubits to emulated (in args)
        super().__init__(*args, **kwargs)

    # For every gate, we need to specify a superoperator and a duration:

    # GJR
    def gateduration_R(self, q, axis_angle, rotation_angle, stretch=1):
        return stretch * abs(rotation_angle) / (pi / 2)

    def gate_R(self, q, axis_angle, rotation_angle, stretch=1):
        # We model the decoherence and over-rotation as a function of the gate duration:
        duration = self.gateduration_R(q, axis_angle, rotation_angle, stretch)

        # I.e., we scale the rotation and depolarization error by the time
        scaled_rotation_error = self.rotation_error * duration
        depolarization_term = (1 - self.depolarization) ** duration

        # Combine these all, returning a superoperator in the Pauli basis
        return pygsti.unitary_to_pauligate(
            U_R(axis_angle + self.phase_error, rotation_angle + scaled_rotation_error)
        ) @ diag([1, depolarization_term, depolarization_term, depolarization_term])

    # GJRt
    gateduration_Rt = gateduration_R
    gate_Rt = gate_R

    # GJXX
    def gateduration_XX(self, q0, q1, rotation_angle, stretch=1):
        # Assume XX pi/2 gate 10 times longer than Sx, Sy, Sz
        return stretch * 10 * abs(rotation_angle) / (pi / 2)

    def gate_XX(self, q0, q1, rotation_angle, stretch=1):
        duration = self.gateduration_XX(q0, q1, rotation_angle, stretch=stretch)

        scaled_rotation_error = self.rotation_error * duration
        depolarization_term = (1 - self.depolarization) ** duration

        return pygsti.unitary_to_pauligate(
            U_XX(rotation_angle + scaled_rotation_error)
        ) @ kron(
            diag([1] + 3 * [depolarization_term]), diag([1] + 3 * [depolarization_term])
        )

    # GJYY
    def gateduration_YY(self, q0, q1, rotation_angle, stretch=1):
        # Assume YY pi/2 gate 10 times longer than Sx, Sy, Sz
        return stretch * 10 * abs(rotation_angle) / (pi / 2)

    def gate_YY(self, q0, q1, rotation_angle, stretch=1):
        duration = self.gateduration_YY(q0, q1, rotation_angle, stretch=stretch)

        scaled_rotation_error = self.rotation_error * duration
        depolarization_term = (1 - self.depolarization) ** duration

        return pygsti.unitary_to_pauligate(
            U_YY(rotation_angle + scaled_rotation_error)
        ) @ kron(
            diag([1] + 3 * [depolarization_term]), diag([1] + 3 * [depolarization_term])
        )

    # GJZZ
    def gateduration_ZZ(self, q0, q1, rotation_angle, stretch=1):
        # Assume ZZ pi/2 gate 10 times longer than Sx, Sy, Sz
        return stretch * 10 * abs(rotation_angle) / (pi / 2)

    def gate_ZZ(self, q0, q1, rotation_angle, stretch=1):
        duration = self.gateduration_ZZ(q0, q1, rotation_angle, stretch=stretch)

        scaled_rotation_error = self.rotation_error * duration
        depolarization_term = (1 - self.depolarization) ** duration

        return pygsti.unitary_to_pauligate(
            U_ZZ(rotation_angle + scaled_rotation_error)
        ) @ kron(
            diag([1] + 3 * [depolarization_term]), diag([1] + 3 * [depolarization_term])
        )

    # GJMS
    def gateduration_MS(self, q0, q1, axis_angle, rotation_angle, stretch=1):
        # Assume MS pi/2 gate 10 times longer than Sx, Sy, Sz
        return stretch * 10 * abs(rotation_angle) / (pi / 2)

    def gate_MS(self, q0, q1, axis_angle, rotation_angle, stretch=1):
        duration = self.gateduration_MS(
            q0, q1, axis_angle, rotation_angle, stretch=stretch
        )

        scaled_rotation_error = self.rotation_error * duration
        depolarization_term = (1 - self.depolarization) ** duration

        return pygsti.unitary_to_pauligate(
            U_MS(axis_angle + self.phase_error, rotation_angle + scaled_rotation_error)
        ) @ kron(
            diag([1] + 3 * [depolarization_term]), diag([1] + 3 * [depolarization_term])
        )

    # Rz is performed entirely in software.
    # GJRz
    def gateduration_Rz(self, q, angle, stretch=1):
        return 0

    def gate_Rz(self, q, angle, stretch=1):
        return pygsti.unitary_to_pauligate(U_Rz(angle))

    # A process matrix for the idle behavior of a qubit.
    # Gidle
    def idle(self, q, duration):
        depolarization_term = (1 - self.depolarization) ** duration

        return diag(
            [1.0, depolarization_term, depolarization_term, depolarization_term]
        )  # WARNING: array must be of dtype=float

    # Instead of copy-pasting the above definitions, use _curry to create new methods
    # with some arguments.  None is a special argument that means: require an argument
    # in the created function and pass it through.
    C = AbstractNoisyNativeEmulator._curry

    gateduration_Rx, gate_Rx = C((None, 0.0, None), gateduration_R, gate_R)
    gateduration_Ry, gate_Ry = C((None, pi / 2, None), gateduration_R, gate_R)
    gateduration_Px, gate_Px = C((None, 0.0, pi), gateduration_R, gate_R)
    gateduration_Py, gate_Py = C((None, pi / 2, pi), gateduration_R, gate_R)
    gateduration_Pz, gate_Pz = C((None, pi), gateduration_Rz, gate_Rz)
    gateduration_Sx, gate_Sx = C((None, 0.0, pi / 2), gateduration_R, gate_R)
    gateduration_Sy, gate_Sy = C((None, pi / 2, pi / 2), gateduration_R, gate_R)
    gateduration_Sz, gate_Sz = C((None, pi / 2), gateduration_Rz, gate_Rz)
    gateduration_Sxd, gate_Sxd = C((None, 0.0, -pi / 2), gateduration_R, gate_R)
    gateduration_Syd, gate_Syd = C((None, pi / 2, -pi / 2), gateduration_R, gate_R)
    gateduration_Szd, gate_Szd = C((None, -pi / 2), gateduration_Rz, gate_Rz)
    gateduration_Sxx, gate_Sxx = C((None, None, pi / 2), gateduration_XX, gate_XX)
    gateduration_Sxxd, gate_Sxxd = C((None, None, -pi / 2), gateduration_XX, gate_XX)
    gateduration_Syy, gate_Syy = C((None, None, pi / 2), gateduration_YY, gate_YY)
    gateduration_Syyd, gate_Syyd = C((None, None, -pi / 2), gateduration_YY, gate_YY)
    gateduration_Szz, gate_Szz = C((None, None, pi / 2), gateduration_ZZ, gate_ZZ)
    gateduration_Szzd, gate_Szzd = C((None, None, -pi / 2), gateduration_ZZ, gate_ZZ)

    del C
