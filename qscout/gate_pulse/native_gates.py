import numpy as np

from jaqal.core import GateDefinition, Parameter, QUBIT_TYPE, FLOAT_TYPE


def U_R(theta, phi):
    """
    Generates the unitary matrix that describes the QSCOUT native R gate, which performs
    an arbitrary rotation around an axis in the X-Y plane.

    :param float theta: The angle that sets the planar axis to rotate around.
    :param float phi: The angle by which the gate rotates the state.
    :returns: The unitary gate matrix.
    :rtype: numpy.array
    """
    return np.array(
        [
            [
                np.cos(phi / 2.0),
                (-1j * np.cos(theta) - np.sin(theta)) * np.sin(phi / 2.0),
            ],
            [
                (-1j * np.cos(theta) + np.sin(theta)) * np.sin(phi / 2.0),
                np.cos(phi / 2.0),
            ],
        ]
    )


def U_MS(theta, phi):
    """
    Generates the unitary matrix that describes the QSCOUT native Mølmer-Sørensen gate.
    This matrix is equivalent to ::

        exp(-i theta/2 (cos(phi) XI + sin(phi) YI) (cos(phi) IX + sin(phi) IY))

    :param float theta: The angle by which the gate rotates the state.
    :param float phi: The phase angle determining the mix of XX and YY rotation.
    :returns: The unitary gate matrix.
    :rtype: numpy.array
    """
    return np.array(
        [
            [
                np.cos(theta / 2.0),
                0,
                0,
                -1j
                * (np.cos(phi * 2.0) - 1j * np.sin(phi * 2.0))
                * np.sin(theta / 2.0),
            ],
            [0, np.cos(theta / 2.0), -1j * np.sin(theta / 2.0), 0],
            [0, -1j * np.sin(theta / 2.0), np.cos(theta / 2.0), 0],
            [
                -1j
                * (np.cos(phi * 2.0) - 1j * np.sin(phi * 2.0))
                * np.sin(theta / 2.0),
                0,
                0,
                np.cos(theta / 2.0),
            ],
        ]
    )


def U_Rx(phi):
    return np.array(
        [
            [np.cos(phi / 2), -1j * np.sin(phi / 2)],
            [-1j * np.sin(phi / 2), np.cos(phi / 2)],
        ]
    )


def U_Ry(phi):
    return np.array(
        [[np.cos(phi / 2), -np.sin(phi / 2)], [np.sin(phi / 2), np.cos(phi / 2)]]
    )


def U_Rz(phi):
    return np.array([[1, 0], [0, np.exp(1j * phi)]])


NATIVE_GATES = (
    GateDefinition("prepare_all"),
    GateDefinition(
        "R",
        [
            Parameter("q", QUBIT_TYPE),
            Parameter("axis-angle", FLOAT_TYPE),
            Parameter("rotation-angle", FLOAT_TYPE),
        ],
        ideal_unitary=U_R,
    ),
    GateDefinition(
        "Rx",
        [Parameter("q", QUBIT_TYPE), Parameter("angle", FLOAT_TYPE)],
        ideal_unitary=U_Rx,
    ),
    GateDefinition(
        "Ry",
        [Parameter("q", QUBIT_TYPE), Parameter("angle", FLOAT_TYPE)],
        ideal_unitary=U_Ry,
    ),
    GateDefinition(
        "Rz",
        [Parameter("q", QUBIT_TYPE), Parameter("angle", FLOAT_TYPE)],
        ideal_unitary=U_Rz,
    ),
    GateDefinition(
        "Px", [Parameter("q", QUBIT_TYPE)], ideal_unitary=lambda: U_Rx(np.pi)
    ),
    GateDefinition(
        "Py", [Parameter("q", QUBIT_TYPE)], ideal_unitary=lambda: U_Ry(np.pi)
    ),
    GateDefinition(
        "Pz", [Parameter("q", QUBIT_TYPE)], ideal_unitary=lambda: U_Rz(np.pi)
    ),
    GateDefinition(
        "Sx", [Parameter("q", QUBIT_TYPE)], ideal_unitary=lambda: U_Rx(np.pi / 2)
    ),
    GateDefinition(
        "Sy", [Parameter("q", QUBIT_TYPE)], ideal_unitary=lambda: U_Ry(np.pi / 2)
    ),
    GateDefinition(
        "Sz", [Parameter("q", QUBIT_TYPE)], ideal_unitary=lambda: U_Rz(np.pi / 2)
    ),
    GateDefinition(
        "Sxd", [Parameter("q", QUBIT_TYPE)], ideal_unitary=lambda: U_Rx(-np.pi / 2)
    ),
    GateDefinition(
        "Syd", [Parameter("q", QUBIT_TYPE)], ideal_unitary=lambda: U_Ry(-np.pi / 2)
    ),
    GateDefinition(
        "Szd", [Parameter("q", QUBIT_TYPE)], ideal_unitary=lambda: U_Rz(-np.pi / 2)
    ),
    GateDefinition(
        "MS",
        [
            Parameter("q1", QUBIT_TYPE),
            Parameter("q2", QUBIT_TYPE),
            Parameter("axis-angle", FLOAT_TYPE),
            Parameter("rotation-angle", FLOAT_TYPE),
        ],
        ideal_unitary=U_MS,
    ),
    GateDefinition(
        "Sxx",
        [Parameter("q1", QUBIT_TYPE), Parameter("q2", QUBIT_TYPE)],
        ideal_unitary=lambda: U_MS(np.pi, 0),
    ),
    GateDefinition("measure_all"),
)
