# Copyright 2020 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.
import numpy as np

import pygsti

from jaqalpaq.emulator.pygsti.noisygatedef import (
    curry_op_factory_class,
    create_NOISY_GATES,
)

from .native_gates import U_R, U_Rx, U_Ry, U_Rz, U_MS, ACTIVE_NATIVE_GATES


depolarization = 1e-3
rotation_error = 1e-2
phase_error = 1e-2


class RadialRotationOpFactory(pygsti.obj.OpFactory):
    def __init__(self):
        pygsti.obj.OpFactory.__init__(self, dim=4, evotype="densitymx")

    def jaqal_duration(self, args=None, sslbls=None):
        rotation = float(args[1])
        return np.abs(rotation) / (np.pi / 2)

    def create_object(self, args=None, sslbls=None):
        # don't worry about sslbls for now -- these are for factories that can create
        # gates placed at arbitrary circuit locations
        assert sslbls is None
        assert len(args) == 2
        phase = float(args[0])
        rotation = float(args[1])

        duration = self.jaqal_duration(args, sslbls)

        scaled_rotation_error = rotation_error * duration
        depolarization_term = (1 - depolarization) ** duration

        super_op = pygsti.unitary_to_pauligate(
            U_R(phase + phase_error, rotation + scaled_rotation_error)
        ) @ np.diag([1, depolarization_term, depolarization_term, depolarization_term])

        return pygsti.obj.StaticDenseOp(super_op)


class MSRotationOpFactory(pygsti.obj.OpFactory):
    def __init__(self):
        pygsti.obj.OpFactory.__init__(self, dim=16, evotype="densitymx")

    def jaqal_duration(self, args=None, sslbls=None):
        # Assume MS pi/2 gate 10 times longer than Sx, Sy, Sz
        rotation = float(args[1])
        return 10 * np.abs(rotation) / (np.pi / 2)

    def create_object(self, args=None, sslbls=None):
        # don't worry about sslbls for now -- these are for factories that can create
        # gates placed at arbitrary circuit locations
        assert sslbls is None
        assert len(args) == 2
        phase = float(args[0])
        rotation = float(args[1])

        duration = self.jaqal_duration(args, sslbls)

        scaled_rotation_error = rotation_error * duration
        depolarization_term = (1 - depolarization) ** duration

        super_op = pygsti.unitary_to_pauligate(
            U_MS(phase + phase_error, rotation + scaled_rotation_error)
        ) @ np.diag([1] + 15 * [depolarization_term])

        return pygsti.obj.StaticDenseOp(super_op)


class AxialRotationOpFactory(pygsti.obj.OpFactory):
    def __init__(self):
        pygsti.obj.OpFactory.__init__(self, dim=4, evotype="densitymx")

    def jaqal_duration(self, args=None, sslbls=None):
        rotation = float(args[0])
        return np.abs(rotation) / (np.pi / 2)

    def create_object(self, args=None, sslbls=None):
        # don't worry about sslbls for now -- these are for factories that can create
        # gates placed at arbitrary circuit locations
        assert sslbls is None
        assert len(args) == 1
        rotation = float(args[0])

        duration = self.jaqal_duration(args, sslbls)

        scaled_rotation_error = rotation_error * duration
        depolarization_term = (1 - depolarization) ** duration

        super_op = pygsti.unitary_to_pauligate(
            U_Rz(rotation + scaled_rotation_error)
        ) @ np.diag([1, depolarization_term, depolarization_term, depolarization_term])

        return pygsti.obj.StaticDenseOp(super_op)


class IdleOpFactory(pygsti.obj.OpFactory):
    def __init__(self):
        pygsti.obj.OpFactory.__init__(self, dim=4, evotype="densitymx")

    def jaqal_duration(self, args=None, sslbls=None):
        rotation = float(args[0])
        return np.abs(rotation) / (np.pi / 2)

    def create_object(self, args=None, sslbls=None):
        # don't worry about sslbls for now -- these are for factories that can create
        # gates placed at arbitrary circuit locations
        assert sslbls is None
        assert len(args) == 1
        rotation = float(args[0])

        duration = self.jaqal_duration(args, sslbls)

        depolarization_term = (1 - depolarization) ** duration

        super_op = np.diag(
            [1, depolarization_term, depolarization_term, depolarization_term]
        )

        return pygsti.obj.StaticDenseOp(super_op)


class MSIdleOpFactory(pygsti.obj.OpFactory):
    def __init__(self):
        pygsti.obj.OpFactory.__init__(self, dim=16, evotype="densitymx")

    def jaqal_duration(self, args=None, sslbls=None):
        # Assume MS pi/2 gate 10 times longer than Sx, Sy, Sz
        rotation = float(args[1])
        return 10 * np.abs(rotation) / (np.pi / 2)

    def create_object(self, args=None, sslbls=None):
        # don't worry about sslbls for now -- these are for factories that can create
        # gates placed at arbitrary circuit locations
        assert sslbls is None
        assert len(args) == 2
        phase = float(args[0])
        rotation = float(args[1])

        duration = self.jaqal_duration(args, sslbls)

        depolarization_term = (1 - depolarization) ** duration

        super_op = np.diag([1] + 15 * [depolarization_term])

        return pygsti.obj.StaticDenseOp(super_op)


idle_operation = IdleOpFactory()


NOISY_GATES = create_NOISY_GATES(
    ACTIVE_NATIVE_GATES,
    R=RadialRotationOpFactory(),
    Rx=curry_op_factory_class(RadialRotationOpFactory, (0.0, None))(),
    Ry=curry_op_factory_class(RadialRotationOpFactory, (np.pi / 2, None))(),
    Rz=AxialRotationOpFactory(),
    Px=curry_op_factory_class(RadialRotationOpFactory, (0.0, np.pi))(),
    Py=curry_op_factory_class(RadialRotationOpFactory, (np.pi / 2, np.pi))(),
    Pz=curry_op_factory_class(AxialRotationOpFactory, (np.pi,))(),
    Sx=curry_op_factory_class(RadialRotationOpFactory, (0.0, np.pi / 2))(),
    Sy=curry_op_factory_class(RadialRotationOpFactory, (np.pi / 2, np.pi / 2))(),
    Sz=curry_op_factory_class(AxialRotationOpFactory, (np.pi / 2,))(),
    Sxd=curry_op_factory_class(RadialRotationOpFactory, (0.0, -np.pi / 2))(),
    Syd=curry_op_factory_class(RadialRotationOpFactory, (np.pi / 2, -np.pi / 2))(),
    Szd=curry_op_factory_class(AxialRotationOpFactory, (np.pi / 2,))(),
    MS=MSRotationOpFactory(),
    Sxx=curry_op_factory_class(MSRotationOpFactory, (0.0, np.pi / 2))(),
)
