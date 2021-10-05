from .._typehint.property import *


class PrimitiveProperty:
    
    def __init__(self, value: TPyVal):
        self.value = self._adapt_type(value)
    
    # noinspection PyMethodMayBeStatic
    def _adapt_type(self, value: TPyVal):
        return value
    
    def __str__(self):
        return str(self.value)


class PrimStr(PrimitiveProperty):
    
    def _adapt_type(self, value: TPyVal):
        assert isinstance(value, str)
        return value
    
    def __str__(self):
        return f'"{self.value}"'


class PrimBool(PrimitiveProperty):
    
    def _adapt_type(self, value: TPyVal):
        assert isinstance(value, bool)
        return value
    
    def __str__(self):
        return 'true' if self.value else 'false'


class PrimNull(PrimitiveProperty):
    
    # noinspection PyMissingConstructor
    def __init__(self):
        self.value = None
    
    def __str__(self):
        return 'null'


def convert_pyval_to_prop(pyval):
    if isinstance(pyval, str):
        return PrimStr(pyval)
    if isinstance(pyval, bool):
        return PrimBool(pyval)
    # if isinstance(pyval, int):
    #     return PI
    if pyval is None:
        return PrimNull()
    # TODO
