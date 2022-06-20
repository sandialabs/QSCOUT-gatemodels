# Copyright 2020 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.

from jaqalpaq.core.circuit import normalize_native_gates
from jaqalpaq.core import Parameter, ParamType
from jaqalpaq.core.gatedef import add_idle_gates, GateDefinition, BusyGateDefinition
from .. import std


ACTIVE_GATES = (
    GateDefinition(
        "R",
        [
            Parameter("q", ParamType.QUBIT),
            Parameter("axis-angle", ParamType.FLOAT),
            Parameter("rotation-angle", ParamType.FLOAT),
        ],
    ),
    GateDefinition(
        "Rx",
        [Parameter("q", ParamType.QUBIT), Parameter("angle", ParamType.FLOAT)],
    ),
    GateDefinition(
        "Ry",
        [Parameter("q", ParamType.QUBIT), Parameter("angle", ParamType.FLOAT)],
    ),
    GateDefinition(
        "Rz",
        [Parameter("q", ParamType.QUBIT), Parameter("angle", ParamType.FLOAT)],
    ),
    GateDefinition("Px", [Parameter("q", ParamType.QUBIT)]),
    GateDefinition("Py", [Parameter("q", ParamType.QUBIT)]),
    GateDefinition("Pz", [Parameter("q", ParamType.QUBIT)]),
    GateDefinition("Sx", [Parameter("q", ParamType.QUBIT)]),
    GateDefinition("Sy", [Parameter("q", ParamType.QUBIT)]),
    GateDefinition("Sz", [Parameter("q", ParamType.QUBIT)]),
    GateDefinition("Sxd", [Parameter("q", ParamType.QUBIT)]),
    GateDefinition("Syd", [Parameter("q", ParamType.QUBIT)]),
    GateDefinition("Szd", [Parameter("q", ParamType.QUBIT)]),
    GateDefinition(
        "MS",
        [
            Parameter("q0", ParamType.QUBIT),
            Parameter("q1", ParamType.QUBIT),
            Parameter("axis-angle", ParamType.FLOAT),
            Parameter("rotation-angle", ParamType.FLOAT),
        ],
    ),
    GateDefinition(
        "Sxx",
        [Parameter("q0", ParamType.QUBIT), Parameter("q1", ParamType.QUBIT)],
    ),
)

ACTIVE_GATES = normalize_native_gates(ACTIVE_GATES, origin=std.__name__)
ALL_GATES = add_idle_gates(ACTIVE_GATES)

SUBCIRCUIT_DEFINERS = (
    BusyGateDefinition("prepare_all", unitary=False),
    BusyGateDefinition("measure_all", unitary=False),
)

SUBCIRCUIT_DEFINERS = normalize_native_gates(SUBCIRCUIT_DEFINERS, origin=std.__name__)
ALL_GATES.update(SUBCIRCUIT_DEFINERS)
