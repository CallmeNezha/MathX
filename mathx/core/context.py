#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class ContextName(object):
    """
    Context name class for storing context and name.
    """

    __slots__ = ['_context', '_name']

    def __new__(cls, context: str, name: str):
        obj = super(ContextName, cls).__new__(cls)
        obj._context = context
        obj._name = name
        return obj

    @property
    def context(self):
        return self._context

    @property
    def name(self):
        return self._name

    def __str__(self):
        return self._context + "`" + self._name

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self}>"


def is_qualified_repr(value: str, initial_backquote=False) -> bool:
    """
    Is qualified represent string of context name.
    """
    return (
        value.endswith("`")
        and "``" not in value
        and (initial_backquote or not value.startswith("`"))
    )


def default(name: str, context="System") -> str:
    """
    Complete name with System context if not presented
    1. If the name's format is -> ({context}`)+{name}
    then function returns same as is.
    2. If the name's format is different with 1.
    then function returns name with {context}{name} prefix.
    """
    assert name != ""

    # Symbol has a context mark -> it came from the parser
    if is_qualified_repr(name):
        return name
    # Symbol came from Python code doing something like
    # Expression('Plus', ...) -> use System` or more generally
    # context + name
    else:
        return str(ContextName(context, name))


__all__ = ['ContextName', 'default', 'is_qualified_repr']
