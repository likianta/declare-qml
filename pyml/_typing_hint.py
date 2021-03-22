from typing import *

TComponent = ...
TComponentID = ...
#   see `pyml_pure_python.core.id_gen.IDGenerator`
TComponentNo = int  # int >= 1
#   see `pyml_pure_python.core.id_gen.IDGenerator`
TLayerLevel = int  # int >= 0
TRepresent = ...


class _Constable:
    """ Constable type.
    Constable[X] is equivalent to Union[X, Constable].
    """
    
    def __getitem__(self, item):
        from pyml.keywords import const
        return Union[item, const]


TConstable = _Constable()


if __name__ == '__main__':
    from .widgets.base_component import BaseComponent as _Component
    from .core.uid_system import UID as _UID
    
    TComponentID = Union[_UID, str]
    TComponent = _Component
    TRepresent = Optional[TComponent]
