# Copyright 2020 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.

from jaqalpaq.core.circuit import normalize_native_gates
from jaqalpaq.core import Parameter, ParamType
from jaqalpaq.core.gatedef import add_idle_gates, GateDefinition, BusyGateDefinition
from ... import v1


ACTIVE_GATES = (
    GateDefinition(
        "ZZ",
        [
            Parameter("q0", ParamType.QUBIT),
            Parameter("q1", ParamType.QUBIT),
            Parameter("rotation-angle", ParamType.FLOAT),
        ],
    ),
)

ACTIVE_GATES = normalize_native_gates(ACTIVE_GATES, origin=v1.zz.__name__)
ALL_GATES = add_idle_gates(ACTIVE_GATES)
