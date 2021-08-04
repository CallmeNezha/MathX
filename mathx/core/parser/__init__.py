#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .bridge import convert
from ..context import default

from mathics_parser.parser import Parser
from mathics_parser.feed import MathicsSingleLineFeeder


from typing import Tuple, Any

# singleton
parser = Parser()


def parse(definitions, feeder):
    """
    Parse input (from the frontend, -e, input files, ToExpression etc).
    Look up symbols according to the Definitions instance supplied.

    Feeder must implement the feed and empty methods, see core/parser/feed.py.
    """
    return parse_returning_code(definitions, feeder)[0]


def parse_returning_code(definitions, feeder) -> Tuple[Any, str]:
    """
    Parse input (from the frontend, -e, input files, ToExpression etc).
    Look up symbols according to the Definitions instance supplied.

    Feeder must implement the feed and empty methods, see core/parser/feed.py.
    """
    ast = parser.parse(feeder)
    source_code = parser.tokeniser.code if hasattr(parser.tokeniser, "code") else ""
    if ast is not None:
        return convert(ast, definitions), source_code
    else:
        return None, source_code


class DummySystemDefinitions(object):
    """
    Dummy Definitions object that puts every unqualified symbol in
    System`.
    """
    def lookup_symbol_name(self, name):
        assert isinstance(name, str)
        return default(name)
