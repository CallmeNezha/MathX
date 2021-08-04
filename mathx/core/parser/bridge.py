#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sympy

from math import ceil, log10
from typing import Tuple, Union
from mathics_parser.ast import Symbol, String, Number, Filename

import mathx.core.string
from .. import expression as expr
from .. import numbers as nums
from ..numbers import machine_precision, C


def reconstruct_digits(bits) -> int:
    """
    Number of digits needed to reconstruct a number with given bits of precision.

    >>> reconstruct_digits(53)
    17
    """
    return int(ceil(bits / C) + 1)


def string_escape(s: str) -> str:
    s = s.replace("\\\\", "\\").replace('\\"', '"')
    s = s.replace("\\r\\n", "\r\n")
    s = s.replace("\\r", "\r")
    s = s.replace("\\n", "\n")
    s = s.replace("\\t", "\t")
    return s


def convert_Symbol(node: Symbol) -> Tuple[str, str]:
    """
    Convert ast Symbol to expression Symbol
    """

    if node.context is not None:
        return "Symbol", node.context + "`" + node.value

    else:
        return "Lookup", node.value


def convert_String(node: String) -> Tuple[str, str]:
    """
    Convert ast String to expression String
    """

    value = string_escape(node.value)
    return "String", value


def convert_Filename(node: Filename) -> Tuple[str, str]:
    """
    Convert ast Filename to expression Filename
    """

    s = node.value
    if s.startswith('"'):
        assert s.endswith('"')
        s = s[1:-1]

    s = string_escape(s)
    s = s.replace("\\", "\\\\")
    return "String", s


def convert_Number(node: Number) -> Union[Tuple[str, int, int],
                                          Tuple[str, int],
                                          Tuple[str, float],
                                          Tuple[str, str, float],
                                          Tuple[str, Tuple[str, str], int],
                                          Tuple[str, Tuple[str, str], float]]:
    s = node.value
    sign = node.sign
    base = node.base
    suffix = node.suffix
    n = node.exp

    # Look for decimal point
    if "." not in s:

        if suffix is None:

            if n < 0:
                return "Rational", sign * int(s, base), base ** abs(n)

            else:
                return "Integer", sign * int(s, base) * (base ** n)

        else:
            s = s + "."

    if base == 10:
        man = s

        if n != 0:
            s = s + "E" + str(n)

        if suffix is None:
            # MachineReal/PrecisionReal is determined by number of digits
            # in the mantissa
            d = len(man) - 2  # one less for decimal point

            if d < reconstruct_digits(machine_precision):
                return "MachineReal", sign * float(s)

            else:
                return (
                    "PrecisionReal",
                    ("DecimalString", str("-" + s if sign == -1 else s)),
                    d,
                )

        elif suffix == "":
            return "MachineReal", sign * float(s)

        elif suffix.startswith("`"):
            acc = float(suffix[1:])
            x = float(s)

            if x == 0:
                prec10 = acc

            else:
                prec10 = acc + log10(x)

            return (
                "PrecisionReal",
                ("DecimalString", str("-" + s if sign == -1 else s)),
                prec10,
            )

        else:
            return (
                "PrecisionReal",
                ("DecimalString", str("-" + s if sign == -1 else s)),
                float(suffix),
            )

    # Put into standard form mantissa * base ^ n
    s = s.split(".")

    if len(s) == 1:
        man = s[0]

    else:
        n -= len(s[1])
        man = s[0] + s[1]

    man = sign * int(man, base)

    if n >= 0:
        p = man * base ** n
        q = 1

    else:
        p = man
        q = base ** -n

    result = "Rational", p, q
    x = float(sympy.Rational(p, q))

    # determine `prec10` the digits of precision in base 10
    if suffix is None:
        acc = len(s[1])
        acc10 = acc * log10(base)

        if x == 0:
            prec10 = acc10

        else:
            prec10 = acc10 + log10(abs(x))

        if prec10 < reconstruct_digits(machine_precision):
            prec10 = None

    elif suffix == "":
        prec10 = None

    elif suffix.startswith("`"):
        acc = float(suffix[1:])
        acc10 = acc * log10(base)

        if x == 0:
            prec10 = acc10

        else:
            prec10 = acc10 + log10(abs(x))

    else:
        prec = float(suffix)
        prec10 = prec * log10(base)

    if prec10 is None:
        return "MachineReal", x

    else:
        return "PrecisionReal", result, prec10


def make_Symbol(s):
    return expr.Symbol(s)


def make_String(s):
    return mathx.core.string.String(s)


def make_Integer(x):
    return nums.Integer(x)


def make_Rational(x, y):
    return nums.Rational(x, y)


def make_MachineReal(x):
    return nums.MachineReal(x)


def make_PrecisionReal(value, prec):
    if value[0] == "Rational":
        assert len(value) == 3
        x = sympy.Rational(*value[1:])

    elif value[0] == "DecimalString":
        assert len(value) == 2
        x = value[1]

    else:
        assert False

    return nums.PrecisionReal(sympy.Float(x, prec))


def make_Expression(head, children):
    return expr.Expr(head, *children)


def do_convert(node):

    if isinstance(node, Symbol):
        return convert_Symbol(node)

    elif isinstance(node, String):
        return convert_String(node)

    elif isinstance(node, Number):
        return convert_Number(node)

    elif isinstance(node, Filename):
        return convert_Filename(node)

    else:
        head = do_convert(node.head)
        children = [do_convert(child) for child in node.children]
        return "Expression", head, children


def convert(node, definitions):

    assert hasattr(definitions, 'lookup_symbol_name')

    result = do_convert(node)

    if result[0] == "Lookup":
        value = definitions.lookup_symbol_name(*result[1:])
        return expr.Symbol(value)
        
    else:
        return globals()["make_" + result[0]](*result[1:])


# Exported functions or classes, do not use any other function if you
# know what you are doing.

__all__ = ['convert']
