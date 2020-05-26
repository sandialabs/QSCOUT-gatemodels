from unittest import TestCase
from numbers import Number

from jaqalpaq.core import (
    GateDefinition,
    Register,
    ScheduledCircuit,
    Parameter,
    BlockStatement,
    LoopStatement,
    Macro,
    Constant,
    NamedQubit,
    AnnotatedValue,
)
from qscout.gate_pulse.native_gates import NATIVE_GATES
from jaqalpaq.jaqal.parser import parse_jaqal_string, Option


class ParserTester(TestCase):
    def setUp(self):
        self.gate_definitions = {}
        self.registers = {}

    def test_deduce_native_gates(self):
        """Test that the native gates are properly deduced from the text."""
        # Note: This behavior is possibly not what we want long term
        text = "register r[3]; foo 1 r[0]; bar 3.14"
        exp_native_gates = {
            "foo": self.get_gate_definition(
                "foo",
                [
                    self.make_parameter(index=0, kind="float"),
                    self.make_parameter(index=1, kind="qubit"),
                ],
            ),
            "bar": self.get_gate_definition(
                "bar", [self.make_parameter(index=0, kind="float")]
            ),
        }
        self.run_test(text, exp_native_gates=exp_native_gates)

    def test_use_native_gates(self):
        """Test that we can use the native gates in the QSCOUT native gate set."""
        text = "register r[3]; Rx r[0] 1.5"
        exp_result = self.make_circuit(
            registers={"r": self.make_register("r", 3)},
            gates=[self.make_gate("Rx", ("r", 0), 1.5, native_gates=NATIVE_GATES)],
        )
        self.run_test(text, exp_result, native_gates=NATIVE_GATES)

    def test_fail_on_missing_native_gate(self):
        """Test that we fail when the using qscout native gates and the user uses a gate
        that does not exist."""
        text = "register r[3]; foo r[0] 1.5"
        # Make sure things we aren't doing something stupid and things will parse
        # without native gates on.
        parse_jaqal_string(text)
        with self.assertRaises(Exception):
            parse_jaqal_string(text, native_gates=NATIVE_GATES)

    ##
    # Helper methods
    #

    def run_test(
        self,
        text,
        exp_result=None,
        exp_native_gates=None,
        override_dict=None,
        native_gates=None,
        option=Option.none,
    ):
        act_result = parse_jaqal_string(
            text,
            override_dict=override_dict,
            native_gates=native_gates,
            processing_option=option,
        )
        if exp_result is not None:
            self.assertEqual(exp_result.body, act_result.body)
            self.assertEqual(exp_result.macros, act_result.macros)
            self.assertEqual(exp_result.constants, act_result.constants)
            self.assertEqual(exp_result.registers, act_result.registers)
        if exp_native_gates is not None:
            self.assertEqual(exp_native_gates, act_result.native_gates)

    @staticmethod
    def make_circuit(*, gates, registers=None, macros=None, constants=None, maps=None):
        circuit = ScheduledCircuit()
        for gate in gates:
            circuit.body.append(gate)
        if registers:
            circuit.registers.update(registers)
        if macros:
            circuit.macros.update(macros)
        if constants:
            circuit.constants.update(constants)
        if maps:
            circuit.registers.update(maps)
        return circuit

    def make_gate(self, name, *args, native_gates=None):
        """Make a gate that is either native or not. Don't call directly."""
        arg_objects = [self.make_argument_object(arg) for arg in args]
        if native_gates:
            gate_def = self.get_native_gate_definition(name, native_gates)
        else:
            params = [
                self.make_parameter_from_arg(idx, arg) for idx, arg in enumerate(args)
            ]
            gate_def = self.get_gate_definition(name, params)
        return gate_def(*arg_objects)

    def get_gate_definition(self, name, params):
        """Return an existing or create a new GateDefinition."""
        if name not in self.gate_definitions:
            gate_def = GateDefinition(name, params)
            self.gate_definitions[name] = gate_def
        else:
            gate_def = self.gate_definitions[name]
        return gate_def

    @staticmethod
    def get_native_gate_definition(name, NATIVE_GATES):
        """Return an existing GateDefinition for a native gate or raise an exception."""
        for gate in NATIVE_GATES:
            if gate.name == name:
                return gate
        raise ValueError(f"Native gate {name} not found")

    def make_argument_object(self, arg):
        """Format an argument as the GateStatement constructor expects it."""
        if isinstance(arg, Number):
            return arg
        elif isinstance(arg, tuple):
            return self.make_qubit(*arg)
        elif isinstance(arg, str):
            return Parameter(arg, None)
        elif isinstance(arg, NamedQubit):
            return arg
        elif isinstance(arg, AnnotatedValue):
            return arg
        else:
            raise TypeError(f"Cannot make an argument out of {arg}")

    def make_qubit(self, name, index):
        """Return a NamedQubit object, possibly creating a register object in the process."""
        if name not in self.registers:
            raise ValueError(f"Please define register {name}")
        else:
            return self.registers[name][index]

    def make_parameter_from_arg(self, index, arg):
        """Define a Parameter from the argument to a gate. Used to define a new GateDefinition."""
        param = self.make_parameter(index=index, kind=None)
        return param

    def make_parameter(self, name=None, index=None, kind=None):
        if name is None:
            if index is None:
                raise ValueError("Provide either name or index to Parameter")
            name = str(index)
        return Parameter(name, kind)

    def make_parallel_gate_block(self, *gates):
        return BlockStatement(parallel=True, statements=list(gates))

    def make_sequential_gate_block(self, *gates):
        return BlockStatement(parallel=False, statements=list(gates))

    def make_loop(self, *gates, count):
        return LoopStatement(count, self.make_sequential_gate_block(*gates))

    def make_register(self, name, size):
        reg = Register(name, size)
        if name in self.registers:
            raise ValueError(f"Register {name} already exists")
        self.registers[name] = reg
        return reg

    def make_macro(self, name, parameter_names, *statements):
        """Create a new Macro object for a macro definition."""
        # Note That this only creates macros with sequential gate blocks while those with
        # parallel gate blocks are also possible.
        return Macro(
            name,
            parameters=[self.make_parameter(pname) for pname in parameter_names],
            body=self.make_sequential_gate_block(*statements),
        )

    def make_constant(self, name, value):
        return Constant(name, value)

    def make_map(self, name, reg_name, reg_indexing):
        if reg_name not in self.registers:
            raise ValueError(f"Please create register {reg_name} first")
        if isinstance(reg_indexing, tuple):
            if len(reg_indexing) != 3:
                raise ValueError(
                    f"reg_indexing must have 3 elements, found {len(reg_indexing)}"
                )
            reg_indexing = tuple(self.make_slice_component(arg) for arg in reg_indexing)
            alias_slice = slice(*reg_indexing)
            reg = Register(
                name, alias_from=self.registers[reg_name], alias_slice=alias_slice
            )
            self.registers[name] = reg
            return reg
        elif isinstance(reg_indexing, int):
            nq = NamedQubit(
                name, alias_from=self.registers[reg_name], alias_index=reg_indexing
            )
            self.registers[name] = nq
            return nq
        elif reg_indexing is None:
            reg = Register(name, alias_from=self.registers[reg_name])
            self.registers[name] = reg
            return reg
        else:
            raise ValueError(f"Bad register indexing {reg_indexing}")

    def make_slice_component(self, arg):
        if isinstance(arg, int):
            return arg
        elif isinstance(arg, str):
            return Parameter(arg, None)
        elif arg is None:
            return None
        elif isinstance(arg, AnnotatedValue):
            return arg
        else:
            raise ValueError(f"Cannot make slice component from {arg}")

    def make_named_qubit(self, name):
        """Return a named qubit that is stored as a map in the registers."""
        if name not in self.registers:
            raise ValueError(f"No entity called {name}")
        named_qubit = self.registers[name]
        if not isinstance(named_qubit, NamedQubit):
            raise TypeError(f"Register entry {name} not a named qubit")
        return named_qubit


class TestOption(TestCase):
    """Test the Option and OptionSet classes."""

    def test_contains_self(self):
        """Test that all options contain themselves."""
        for opt in Option:
            self.assertIn(opt, opt)

    def test_contains_bitmask(self):
        """Test that element containment acts like a bitmask."""
        for opt0 in Option:
            for opt1 in Option:
                self.assertEqual(opt0.value & opt1.value == opt1.value, opt1 in opt0)

    def test_in_option_set(self):
        """Test that options are in an option set containing them."""
        for opt0 in Option:
            for opt1 in Option:
                optset = opt0 | opt1
                self.assertIn(opt0, optset)
                self.assertIn(opt1, optset)

    def test_combine_opt_set_with_option(self):
        """Test that an option set combines with an option"""
        for opt0 in Option:
            for opt1 in Option:
                for opt2 in Option:
                    optset = opt0 | opt1
                    self.assertIn(opt2, optset | opt2)
                    self.assertIn(opt2, opt2 | optset)

    def test_let_in_optionset_with_let_map(self):
        """Test that extract_let is in an OptionSet that was created with extract_let_map but not extract_let"""
        optset = Option.expand_macro | Option.expand_let_map
        self.assertIn(Option.expand_let_map, optset)
