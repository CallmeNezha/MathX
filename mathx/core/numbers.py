from sympy.core.numbers import Integer, Rational
from .expression import AtomicExpr

import math
import sympy
import mpmath
from typing import Union

from math import log

C = log(10, 2)  # ~ 3.3219280948873626

# Number of bits of machine precision
machine_precision = 53
machine_epsilon = 2 ** (1 - machine_precision)


def dpsx(prec) -> int:
    """
    dps (short for decimal places) is the decimal precision
    """

    return max(1, int(round(int(prec) / C - 1)))


def precx(dps) -> int:
    """
    prec denotes the binary precision (measured in bits)
    """

    return max(1, int(round((int(dps) + 1) * C)))


def precision(number: Union['MachineReal','PrecisionReal']) -> int:
    """
    Get the precision of real number
    """

    if isinstance(number, MachineReal):
        return machine_precision

    elif isinstance(number, PrecisionReal):
        return number._value._prec + 1

    else:
        raise Exception(f'type {type(number)} does\'t have property precision')


def roundx(number, dps=None) -> Union['PrecisionReal','MachineReal']:
    """
    Round to float if dps not provided, or to dps number, it is 
    named with suffix `x` to avoid conflict with python's builtin
    round.

    dps (short for decimal places) is the decimal precision.
    """

    if dps is None:

        if isinstance(number, (Integer, Real, Rational)):
            return MachineReal(float(number))

        elif isinstance(number, Complex):
            real = roundx(number.real)
            imag = roundx(number.imag)
            return Complex(real, imag)

        else:
            raise Exception(f'unsupported type {type(number)}')

    else:

        if isinstance(number, Integer): 
            return PrecisionReal(sympy.Float(int(number), dps))

        elif isinstance(number, Rational):
            return PrecisionReal(number.value.n(dps))

        elif isinstance(number, MachineReal):
            return PrecisionReal(sympy.Float(float(number), dps))

        elif isinstance(number, PrecisionReal):
            dps = min(dpsx(precision(number)), dps)
            return PrecisionReal(number.value.n(dps))

        elif isinstance(number, Complex):
            real = roundx(number.real, dps)
            imag = roundx(number.imag, dps)
            return Complex(real, imag)

        else:
            raise Exception(f'unsupported type {type(number)}')


class Number(AtomicExpr):
    """
    A parent class of all numbers.
    """
    is_number = True


class Integer(Number):
    """
    Integer class, internal saved as int.
    """

    __slots__ = ['_value']

    def __new__(cls, value: int) -> 'Integer':
        obj = super(Integer, cls).__new__(cls)
        obj._value = int(value)
        return obj


class Rational(Number):
    """
    Rational class, internal saved as sympy.Rational
    """

    __slots__ = ['_value']

    def __new__(cls, numerator, denominator=1) -> 'Rational':
        obj = super(Rational, cls).__new__(cls)
        obj._value = sympy.Rational(numerator, denominator)
        return obj



class Real(Number):
    """
    Real number can be MachineReal or PrecisionReal depends
    on that value is passed to it.
    """

    def __new__(cls, value, p=None) -> Union['MachineReal', 'PrecisionReal']:
        if isinstance(value, str):
            value = str(value)

            if p is None:
                import re
                digits = ("".join(re.findall("[0-9]+", value))).lstrip("0")

                if digits == "":  # Handle weird Mathematica zero case
                    p = max(precx(len(value.replace("0.", ""))), machine_precision)

                else:
                    p = precx(len(digits.zfill(dpsx(machine_precision))))

        elif isinstance(value, sympy.Float):

            if p is None:
                p = value._prec + 1

        elif isinstance(value, (Integer, sympy.Number, mpmath.mpf, float, int)):

            if p is not None and p > machine_precision:
                value = str(value)

        else:
            raise TypeError("Unknown number type: %s (type %s)" % (value, type(value)))

        # return either machine precision or arbitrary precision real
        if p is None or p == machine_precision:
            return MachineReal.__new__(MachineReal, value)

        else:
            return PrecisionReal.__new__(PrecisionReal, value)



class MachineReal(Real):
    """
    Machine precision real number, internal saved as float.
    """

    __slots__ = ['_value']

    def __new__(cls, value) -> "MachineReal":
        value = float(value)

        if math.isinf(value) or math.isnan(value):
            raise OverflowError

        obj = super(Number, cls).__new__(cls)
        obj._value = value
        return obj

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self._value}>"


class PrecisionReal(Real):
    """
    Arbitrary precision real number.

    Stored internally as a sympy.Float.

    Note: Plays nicely with the mpmath.mpf (float) type.
    """

    __slots__ = ['_value']

    def __new__(cls, value) -> "PrecisionReal":
        obj = super(Number, cls).__new__(cls)
        obj._value = sympy.Float(value)
        return obj

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self._value}>"


class Complex(Number):
    """
    Complex number of MathX

    If create with all Integer it returns: Integer + I * Integer.
    If imaginary is Integer Zero it returns: Integer
    """

    __slots__ = ['_real', '_imag']

    def __new__(cls, real: Union['Real','Integer'], imag: Union['Real','Integer']) -> Number:
        self = super(Complex, cls).__new__(cls)

        if isinstance(real, Complex) or not isinstance(real, Number):
            raise ValueError("Argument 'real' must be a real number.")

        if isinstance(imag, Complex) or not isinstance(imag, Number):
            raise ValueError("Argument 'imag' must be a real number.")

        # Here to implement explicitly avoiding loop import of compare.
        if isinstance(imag, Integer) and imag._value == Integer0._value:
            return real

        # Round to lower 
        if isinstance(real, MachineReal) and not isinstance(imag, MachineReal):
            imag = roundx(imag)

        if isinstance(imag, MachineReal) and not isinstance(real, MachineReal):
            real = roundx(real)

        self._real = real
        self._imag = imag
        return self

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self._real, self._imag}>"


def to_sympy(number: Number) -> sympy.Number:
    """
    Convert MathX to simpy category.
    """

    if isinstance(number, Integer):
        return sympy.Integer(number._value)

    elif isinstance(number, Rational):
        return number._value

    elif isinstance(number, MachineReal):
        return sympy.Float(number._value)

    elif isinstance(number, PrecisionReal):
        return number._value

    elif isinstance(number, Complex):
        return number._real + sympy.I * number._imag


def to_python(number: Number) -> [float,int,complex]:
    """
    Covert MathX to pure python category.
    """

    if isinstance(number, Integer):
        return number._value

    elif isinstance(number, Rational):
        return float(number._value)

    elif isinstance(number, MachineReal):
        return number._value

    elif isinstance(number, PrecisionReal):
        return float(number._value)

    elif isinstance(number, Complex):
        return complex(to_python(number._real), to_python(number._imag))




# constants
Integer0 = Integer(0)
Integer1 = Integer(1)

__all__ = ['precision', 'roundx', 'Number', 'Integer', 'Real', 'MachineReal', 
           'PrecisionReal', 'Complex', 'Integer0', 'Integer1', 'machine_precision', 'C',
           'Rational'
          ]
