

def baz(*a, **kw):
    print(__name__, 'baz', a, kw)
    return a, kw


import operator

def ret_math(*vals, op='add'):
    return getattr(operator, op)(*vals)
