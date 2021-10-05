from lk_logger import lk

from .primitive_property import PrimitiveProperty
from .primitive_property import convert_pyval_to_prop
from .._typehint.property import *
from ..black_magic import gstates

__all__ = [
    'Boundable',
    'Property',
    'PropInt',
]


class Boundable:
    _source = None
    _target = None
    
    def __init__(self, source, target):
        self._source = source
        self._target = target


class Property(Boundable):
    _name: TPropName
    _value: TPropValue
    _wid: str
    
    # noinspection PyMissingConstructor
    def __init__(self, name: str, value: TPyVal = None):
        self._name = name
        self._value = value
    
    def __str__(self):
        raise NotImplementedError
    
    def __getattribute__(self, item):
        """
        Critical Warning:
            Do not barely print `self.bind`, it will cause black magic leaks
            and destroy all succeeding properties' handles! I.E. the only way
            to use `self.bind` is `self.bind(...)`.
        """
        if item == 'bind':
            lk.logt('[D2806]', 'enable binding mode')
            gstates.is_binding = True
        return super().__getattribute__(item)
    
    def set_widget_id(self, wid):
        self._wid = wid
    
    @property
    def prop_name(self) -> str:
        if self._wid:
            return f'{self._wid}.{self._name}'
        else:
            return self._name
    
    @property
    def prop_value(self) -> TPropValue:
        return self._value
    
    def bind(self, prop):
        lk.logt('[D2951]', gstates.is_binding)
        try:
            if isinstance(prop, Boundable):
                self._value = prop
            else:
                raise Exception('Target is not boundable', prop)
        finally:
            gstates.is_binding = False
    
    def gain(self, x: Union[TPropValue, TPyVal]):
        if isinstance(x, PrimitiveProperty):
            self._value = x
        elif isinstance(x, Property):
            self._value = PrimitiveProperty(x.prop_value)
        else:
            self._value = convert_pyval_to_prop(x)


class PropInt(Property):
    
    def __init__(self, name: str, value: int = 0):
        assert isinstance(value, int)
        super().__init__(name, value)
    
    def __str__(self):
        return str(self._value)
    
    def __add__(self, other):
        if gstates.is_binding:
            assert self._wid
            return Boundable(self, f'{self.prop_name} + {other}')
        else:
            return self._value + other
    
    def __radd__(self, other):
        if gstates.is_binding:
            assert self._wid
            return Boundable(self, f'{self.prop_name} + {other}')
        else:
            return other + self._value
