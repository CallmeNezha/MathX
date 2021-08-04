
class Basic:
    """
    A parent class for all mathics objects
    """
    # overwrite this in appropriate subclass
    is_atom = False
    is_expr = False
    is_number = False
    is_string = False


class Atom(Basic):
    is_atom = True


__all__ = ['Basic', 'Atom']
