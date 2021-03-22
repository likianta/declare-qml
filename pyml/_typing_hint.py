from typing import *

TComponent = ...
TComponentID = ...
#   see `pyml_pure_python.core.id_gen.IDGenerator`
TComponentNo = int  # int >= 1
#   see `pyml_pure_python.core.id_gen.IDGenerator`
TLayerLevel = int  # int >= 0
TRepresent = ...

if __name__ == '__main__':
    from .widgets.base_component import BaseComponent as _Component
    from .core.uid_system import UID as _UID
    
    TComponentID = Union[_UID, str]
    TComponent = _Component
    TRepresent = Optional[TComponent]
