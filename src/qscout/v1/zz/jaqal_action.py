from .jaqal_gates import ALL_GATES, ACTIVE_GATES

import numpy as np


def U_ZZ(rotation_angle):
    """
    Generates the unitary matrix that describes the QSCOUT native ZZ gate.

    :param float rotation_angle: The angle by which the gate rotates the state.
    :returns: The unitary gate matrix.
    :rtype: numpy.array
    """

    cr = np.cos(rotation_angle / 2.0)
    sr = np.sin(rotation_angle / 2.0) * 1j
    # fmt: off
    return np.array(
        [
            [ cr-sr,   0  ,   0  ,   0   ],
            [   0  , cr+sr,   0  ,   0   ],
            [   0  ,   0  , cr+sr,   0   ],
            [   0  ,   0  ,   0  , cr-sr ],
        ]
    )
    # fmt: on


IDEAL_ACTION = dict(
    ZZ=U_ZZ,
)

for name in list(ACTIVE_GATES.keys()):
    IDEAL_ACTION[f"I_{name}"] = None
