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

    def __int__(self):
        return self._value

    def __float__(self):
        return float(self._value)


class Rational(Number):
    """
    Rational class, internal saved as sympy.Rational
    """

    __slots__ = ['_value']


    def __new__(cls, numerator, denominator=1) -> 'Rational':
        obj = super(Rational, cls).__new__(cls)
        obj._value = sympy.Rational(numerator, denominator)
        return obj

    def __int__(self):
        return int(self._value)

    def __float__(self):
        return float(self._value)


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

    @property
    def value(self) -> Union[float, sympy.Float]:
        return self._value


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

    def __int__(self):
        return int(self._value)

    def __float__(self):
        return self._value


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

    def __int__(self):
        return int(self._value)
    
    def __float__(self):
        return float(self._value)


class Complex(Number):
    """
    Complex number Hummm.
    """

    __slots__ = ['_real', '_imag']

    def __new__(cls, real, imag):
        self = super(Complex, cls).__new__(cls)

        if isinstance(real, Complex) or not isinstance(real, Number):
            raise ValueError("Argument 'real' must be a real number.")

        if isinstance(imag, Complex) or not isinstance(imag, Number):
            raise ValueError("Argument 'imag' must be a real number.")

        if imag.sameQ(Integer0):
            return real

        # Round to lower 
        if isinstance(real, MachineReal) and not isinstance(imag, MachineReal):
            imag = roundx(imag)

        if isinstance(imag, MachineReal) and not isinstance(real, MachineReal):
            real = roundx(real)

        self.real = real
        self.imag = imag
        return self




# constants
Integer0 = Integer(0)
Integer1 = Integer(1)

__all__ = ['precision', 'roundx', 'Number', 'Integer', 'Real', 'MachineReal', 
           'PrecisionReal', 'Complex', 'Integer0', 'Integer1']