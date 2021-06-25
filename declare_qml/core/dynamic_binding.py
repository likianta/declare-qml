from ..properties import PyFunc
from ..typehint import *


def bind(coms: Iterable[TComponent], func: Callable) -> PyFunc:
    return PyFunc(coms, func)
