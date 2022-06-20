from .jaqal_gates import ALL_GATES, ACTIVE_GATES

import numpy as np


def U_R(axis_angle, rotation_angle):
    """
    Generates the unitary matrix that describes the QSCOUT native R gate, which performs
    an arbitrary rotation around an axis in the X-Y plane.

    :param float axis_angle: The angle that sets the planar axis to rotate around.
    :param float rotation_angle: The angle by which the gate rotates the state.
    :returns: The unitary gate matrix.
    :rtype: numpy.array
    """
    return np.array(
        [
            [
                np.cos(rotation_angle / 2.0),
                (-1j * np.cos(axis_angle) - np.sin(axis_angle))
                * np.sin(rotation_angle / 2.0),
            ],
            [
                (-1j * np.cos(axis_angle) + np.sin(axis_angle))
                * np.sin(rotation_angle / 2.0),
                np.cos(rotation_angle / 2.0),
            ],
        ]
    )


def U_MS(axis_angle, rotation_angle):
    """
    Generates the unitary matrix that describes the QSCOUT native Mølmer-Sørensen gate.
    This matrix is equivalent to ::

        exp(-i rotation_angle/2 (cos(axis_angle) XI + sin(axis_angle) YI) (cos(axis_angle) IX + sin(axis_angle) IY))

    :param float axis_angle: The phase angle determining the mix of XX and YY rotation.
    :param float rotation_angle: The angle by which the gate rotates the state.
    :returns: The unitary gate matrix.
    :rtype: numpy.array
    """
    return np.array(
        [
            [
                np.cos(rotation_angle / 2.0),
                0,
                0,
                -1j
                * (np.cos(axis_angle * 2.0) - 1j * np.sin(axis_angle * 2.0))
                * np.sin(rotation_angle / 2.0),
            ],
            [0, np.cos(rotation_angle / 2.0), -1j * np.sin(rotation_angle / 2.0), 0],
            [0, -1j * np.sin(rotation_angle / 2.0), np.cos(rotation_angle / 2.0), 0],
            [
                -1j
                * (np.cos(axis_angle * 2.0) + 1j * np.sin(axis_angle * 2.0))
                * np.sin(rotation_angle / 2.0),
                0,
                0,
                np.cos(rotation_angle / 2.0),
            ],
        ]
    )


def U_Rx(rotation_angle):
    return np.array(
        [
            [np.cos(rotation_angle / 2), -1j * np.sin(rotation_angle / 2)],
            [-1j * np.sin(rotation_angle / 2), np.cos(rotation_angle / 2)],
        ]
    )


def U_Ry(rotation_angle):
    return np.array(
        [
            [np.cos(rotation_angle / 2), -np.sin(rotation_angle / 2)],
            [np.sin(rotation_angle / 2), np.cos(rotation_angle / 2)],
        ]
    )


def U_Rz(rotation_angle):
    return np.array([[1, 0], [0, np.exp(1j * rotation_angle)]])


IDEAL_ACTION = dict(
    R=U_R,
    Rx=U_Rx,
    Ry=U_Ry,
    Rz=U_Rz,
    Px=lambda: U_Rx(np.pi),
    Py=lambda: U_Ry(np.pi),
    Pz=lambda: U_Rz(np.pi),
    Sx=lambda: U_Rx(np.pi / 2),
    Sy=lambda: U_Ry(np.pi / 2),
    Sz=lambda: U_Rz(np.pi / 2),
    Sxd=lambda: U_Rx(-np.pi / 2),
    Syd=lambda: U_Ry(-np.pi / 2),
    Szd=lambda: U_Rz(-np.pi / 2),
    MS=U_MS,
    Sxx=lambda: U_MS(0, np.pi / 2),
)

for name in list(ACTIVE_GATES.keys()):
    IDEAL_ACTION[f"I_{name}"] = None
