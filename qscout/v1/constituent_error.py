# Copyright 2020 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.
import numpy as np

import pygsti

from jaqalpaq.core import Parameter, ParamType
from jaqalpaq.core.gatedef import add_idle_gates, GateDefinition, BusyGateDefinition

from jaqalpaq.emulator.pygsti.noisygatedef import (
    curry_op_factory_class,
    NoisyGateDefinition,
)

from .native_gates import U_R, U_Rx, U_Ry, U_Rz, U_MS


depolarization = 1e-3
rotation_error = 1e-2
phase_error = 1e-2


class RadialRotationOpFactory(pygsti.obj.OpFactory):
    def __init__(self):
        pygsti.obj.OpFactory.__init__(self, dim=4, evotype="densitymx")

    def create_object(self, args=None, sslbls=None):
        assert (
            sslbls is None
        )  # don't worry about sslbls for now -- these are for factories that can create gates placed at arbitrary circuit locations
        assert len(args) == 2
        phase = float(args[0])
        rotation = float(args[1])

        duration = rotation / (np.pi / 2)

        scaled_rotation_error = rotation_error * duration
        depolarization_term = (1 - depolarization) ** duration

        super_op = pygsti.unitary_to_pauligate(
            U_R(phase + phase_error, rotation + scaled_rotation_error)
        ) @ np.diag([1, depolarization_term, depolarization_term, depolarization_term])

        return pygsti.obj.StaticDenseOp(super_op)


class MSRotationOpFactory(pygsti.obj.OpFactory):
    def __init__(self):
        pygsti.obj.OpFactory.__init__(self, dim=16, evotype="densitymx")

    def create_object(self, args=None, sslbls=None):
        assert (
            sslbls is None
        )  # don't worry about sslbls for now -- these are for factories that can create gates placed at arbitrary circuit locations
        assert len(args) == 2
        phase = float(args[0])
        rotation = float(args[1])

        duration = (
            10 * rotation / (np.pi / 2)
        )  # Assume MS pi/2 gate 10 times longer than Sx, Sy, Sz

        scaled_rotation_error = rotation_error * duration
        depolarization_term = (1 - depolarization) ** duration

        super_op = pygsti.unitary_to_pauligate(
            U_MS(phase + phase_error, rotation + scaled_rotation_error)
        ) @ np.diag([1] + 15 * [depolarization_term])

        return pygsti.obj.StaticDenseOp(super_op)


class AxialRotationOpFactory(pygsti.obj.OpFactory):
    def __init__(self):
        pygsti.obj.OpFactory.__init__(self, dim=4, evotype="densitymx")

    def create_object(self, args=None, sslbls=None):
        assert (
            sslbls is None
        )  # don't worry about sslbls for now -- these are for factories that can create gates placed at arbitrary circuit locations
        assert len(args) == 1
        rotation = float(args[0])

        duration = rotation / (np.pi / 2)

        scaled_rotation_error = rotation_error * duration
        depolarization_term = (1 - depolarization) ** duration

        super_op = pygsti.unitary_to_pauligate(
            U_Rz(rotation + scaled_rotation_error)
        ) @ np.diag([1, depolarization_term, depolarization_term, depolarization_term])

        return pygsti.obj.StaticDenseOp(super_op)


class IdleOpFactory(pygsti.obj.OpFactory):
    def __init__(self):
        pygsti.obj.OpFactory.__init__(self, dim=4, evotype="densitymx")

    def create_object(self, args=None, sslbls=None):
        assert (
            sslbls is None
        )  # don't worry about sslbls for now -- these are for factories that can create gates placed at arbitrary circuit locations
        assert len(args) == 1
        rotation = float(args[0])

        duration = rotation / (np.pi / 2)

        depolarization_term = (1 - depolarization) ** duration

        super_op = np.diag(
            [1, depolarization_term, depolarization_term, depolarization_term]
        )

        return pygsti.obj.StaticDenseOp(super_op)


class MSIdleOpFactory(pygsti.obj.OpFactory):
    def __init__(self):
        pygsti.obj.OpFactory.__init__(self, dim=16, evotype="densitymx")

    def create_object(self, args=None, sslbls=None):
        assert (
            sslbls is None
        )  # don't worry about sslbls for now -- these are for factories that can create gates placed at arbitrary circuit locations
        assert len(args) == 2
        phase = float(args[0])
        rotation = float(args[1])

        duration = (
            10 * rotation / (np.pi / 2)
        )  # Assume MS pi/2 gate 10 times longer than Sx, Sy, Sz

        depolarization_term = (1 - depolarization) ** duration

        super_op = np.diag([1] + 15 * [depolarization_term])

        return pygsti.obj.StaticDenseOp(super_op)


ACTIVE_NATIVE_GATES = (
    BusyGateDefinition("prepare_all"),
    NoisyGateDefinition(
        "R",
        [
            Parameter("q", ParamType.QUBIT),
            Parameter("axis-angle", ParamType.FLOAT),
            Parameter("rotation-angle", ParamType.FLOAT),
        ],
        ideal_unitary=U_R,
        noisy_operation=RadialRotationOpFactory(),
    ),
    NoisyGateDefinition(
        "Rx",
        [Parameter("q", ParamType.QUBIT), Parameter("angle", ParamType.FLOAT)],
        ideal_unitary=U_Rx,
        noisy_operation=curry_op_factory_class(RadialRotationOpFactory, (0.0, None))(),
    ),
    NoisyGateDefinition(
        "Ry",
        [Parameter("q", ParamType.QUBIT), Parameter("angle", ParamType.FLOAT)],
        ideal_unitary=U_Ry,
        noisy_operation=curry_op_factory_class(
            RadialRotationOpFactory, (np.pi / 2, None)
        )(),
    ),
    NoisyGateDefinition(
        "Rz",
        [Parameter("q", ParamType.QUBIT), Parameter("angle", ParamType.FLOAT)],
        ideal_unitary=U_Rz,
        noisy_operation=AxialRotationOpFactory(),
    ),
    NoisyGateDefinition(
        "Px",
        [Parameter("q", ParamType.QUBIT)],
        ideal_unitary=lambda: U_Rx(np.pi),
        noisy_operation=curry_op_factory_class(RadialRotationOpFactory, (0.0, np.pi))(),
    ),
    NoisyGateDefinition(
        "Py",
        [Parameter("q", ParamType.QUBIT)],
        ideal_unitary=lambda: U_Ry(np.pi),
        noisy_operation=curry_op_factory_class(
            RadialRotationOpFactory, (np.pi / 2, np.pi)
        )(),
    ),
    NoisyGateDefinition(
        "Pz",
        [Parameter("q", ParamType.QUBIT)],
        ideal_unitary=lambda: U_Rz(np.pi),
        noisy_operation=curry_op_factory_class(AxialRotationOpFactory, (np.pi,))(),
    ),
    NoisyGateDefinition(
        "Sx",
        [Parameter("q", ParamType.QUBIT)],
        ideal_unitary=lambda: U_Rx(np.pi / 2),
        noisy_operation=curry_op_factory_class(
            RadialRotationOpFactory, (0.0, np.pi / 2)
        )(),
    ),
    NoisyGateDefinition(
        "Sy",
        [Parameter("q", ParamType.QUBIT)],
        ideal_unitary=lambda: U_Ry(np.pi / 2),
        noisy_operation=curry_op_factory_class(
            RadialRotationOpFactory, (np.pi / 2, np.pi / 2)
        )(),
    ),
    NoisyGateDefinition(
        "Sz",
        [Parameter("q", ParamType.QUBIT)],
        ideal_unitary=lambda: U_Rz(np.pi / 2),
        noisy_operation=curry_op_factory_class(AxialRotationOpFactory, (np.pi / 2,))(),
    ),
    NoisyGateDefinition(
        "Sxd",
        [Parameter("q", ParamType.QUBIT)],
        ideal_unitary=lambda: U_Rx(-np.pi / 2),
        noisy_operation=curry_op_factory_class(
            RadialRotationOpFactory, (0.0, -np.pi / 2)
        )(),
    ),
    NoisyGateDefinition(
        "Syd",
        [Parameter("q", ParamType.QUBIT)],
        ideal_unitary=lambda: U_Ry(-np.pi / 2),
        noisy_operation=curry_op_factory_class(
            RadialRotationOpFactory, (np.pi / 2, -np.pi / 2)
        )(),
    ),
    NoisyGateDefinition(
        "Szd",
        [Parameter("q", ParamType.QUBIT)],
        ideal_unitary=lambda: U_Rz(-np.pi / 2),
        noisy_operation=curry_op_factory_class(AxialRotationOpFactory, (np.pi / 2,))(),
    ),
    NoisyGateDefinition(
        "MS",
        [
            Parameter("q0", ParamType.QUBIT),
            Parameter("q1", ParamType.QUBIT),
            Parameter("axis-angle", ParamType.FLOAT),
            Parameter("rotation-angle", ParamType.FLOAT),
        ],
        ideal_unitary=U_MS,
        noisy_operation=MSRotationOpFactory(),
    ),
    NoisyGateDefinition(
        "Sxx",
        [Parameter("q0", ParamType.QUBIT), Parameter("q1", ParamType.QUBIT)],
        ideal_unitary=lambda: U_MS(0, np.pi / 2),
        noisy_operation=curry_op_factory_class(MSRotationOpFactory, (0.0, np.pi / 2))(),
    ),
    BusyGateDefinition("measure_all"),
)

NATIVE_GATES = add_idle_gates(ACTIVE_NATIVE_GATES)
