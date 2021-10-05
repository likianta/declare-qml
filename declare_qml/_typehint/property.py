from typing import *

from lk_lambdex import lambdex

if __name__ == '__main__':
    import declare_qml.property.property as _prop
    import declare_qml.property.primitive_property as _prim_prop
else:
    _fake_type = lambdex('', """
        class AnyType:
            def __getattr__(self, item):
                return Any
        return AnyType()
    """)()
    _prop = _fake_type
    _prim_prop = _fake_type

# ------------------------------------------------------------------------------

TPropName = str
TPropValue = Union[None,
                   _prim_prop.PrimitiveProperty,
                   _prop.Boundable, _prop.Property]
TPyVal = Any
