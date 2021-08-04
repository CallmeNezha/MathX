from mathx.core.expression import AtomicExpr


class String(AtomicExpr):
    """
    String of mathx.
    """

    __slots__ = ['_value']

    def __new__(cls, value):
        obj = super(String, cls).__new__(cls)
        obj._value = str(value)
        return obj

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self._value}>"
