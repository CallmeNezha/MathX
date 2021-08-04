from collections import namedtuple

from .basic import Basic, Atom
from .numbers import Real, MachineReal, PrecisionReal, Integer, Rational, Complex

ContextName = namedtuple('ContextName', 'context name')


class Expr(Basic):
    """
    Expression is the basic thing in here.
    """
    is_expr = True

    __slots__ = ['_head', '_leaves']

    def __new__(cls, head, *leaves):
        obj = super(Expr, cls).__new__(cls)
        obj._head = head
        obj._leaves = tuple(leaves)
        return obj

    @property
    def head(self):
        return self._head

    @property
    def leaves(self):
        return self._leaves

    def __repr__(self):
        return f"<{self._head.__class__.__name__}: {self}>"


class AtomicExpr(Atom, Expr):
    """
    Atomic expression is parent of Symbol, Number.
    """
    def __new__(cls, *args, **kwargs):
        obj = super(AtomicExpr, cls).__new__(cls, Symbol(cls.__name__))
        return obj


class Symbol(AtomicExpr):
    """
    Everything are symbols in some sort of way.
    """
    # Every symbol is unique
    _cache = {}

    __slots__ = ['_ctx_name']

    def __new__(cls, name: str, *, unit=False):
        if "`" in name:
            i = name.rfind("`")
            ctx_name = ContextName(name[:i], name[i:])
        else:
            ctx_name = ContextName("System", name)

        if ctx_name in Symbol._cache:
            return Symbol._cache[ctx_name]
        else:
            if unit:
                obj = super(AtomicExpr, cls).__new__(cls, None)
                obj._head = obj
            else:
                obj = super(AtomicExpr, cls).__new__(cls, Symbol0)
            obj._ctx_name = ctx_name
            Symbol._cache[ctx_name] = obj
            return obj

    @property
    def name(self):
        return self._ctx_name.name

    @property
    def context(self):
        return self._ctx_name.context

    @property
    def fullname(self):
        return self._ctx_name.context + "`" + self._ctx_name.name

    def __str__(self):
        return self.name


Symbol0 = Symbol("Symbol", unit=True)

