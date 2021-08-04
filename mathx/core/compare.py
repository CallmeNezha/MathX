from typing import Union

import sympy

from .basic import Basic, Atom
from .expression import Symbol, Expr
from .string import String
from .numbers import Complex, Integer, Real, Rational, MachineReal, PrecisionReal, to_sympy, to_python


def sameQ(lhs, rhs):
    """
    MathX sameQ.
    """

    if id(lhs) == id(rhs):
        return True

    if type(lhs) == type(rhs) == Symbol:
        return lhs.name == rhs.name #TODO: maybe it will never meet because of singleton cache

    elif type(lhs) == type(rhs) == Expr:

        if not sameQ(lhs.head, rhs.head):
            return False

        if len(lhs.leaves) != len(rhs.leaves):
            return False

        for ll, rl in zip(lhs.leaves, rhs.leaves):
            if not sameQ(ll, rl):
                return False

        return True

    if type(lhs) == type(rhs) == Integer:
        lhs._value: int
        rhs._value: int
        return lhs._value == rhs._value

    elif type(lhs) == type(rhs) == MachineReal:
        lhs._value: float
        rhs._value: float
        return lhs._value == rhs._value

    elif type(lhs) == type(rhs) == String:
        lhs._value: str
        rhs._value: str
        return lhs._value == rhs._value

    elif type(lhs) == type(rhs) == PrecisionReal:
        lhs._value: sympy.Float
        rhs._value: sympy.Float
        return lhs._value == rhs._value

    elif isinstance(lhs, Real) and isinstance(rhs, Real) and type(rhs) != type(lhs):
        lhs: Union['MachineReal', 'PrecisionReal']
        rhs: Union['MachineReal', 'PrecisionReal']
        return to_sympy(lhs) == to_sympy(rhs)

    elif type(lhs) == type(rhs) == Complex:
        lhs._real: Union['Integer', 'MachineReal', 'PrecisionReal']
        rhs._real: Union['Integer', 'MachineReal', 'PrecisionReal']
        lhs._imag: Union['Integer', 'MachineReal', 'PrecisionReal']
        rhs._imag: Union['Integer', 'MachineReal', 'PrecisionReal']
        return sameQ(lhs._real, rhs._real) and sameQ(lhs._imag, rhs._imag)

    elif type(lhs) == type(rhs) == Rational:
        lhs._value: sympy.Rational
        rhs._value: sympy.Rational
        return lhs._value == rhs._value

    else:
        return False
