from typing import *

TComponentID = ...
#   see `pyml_pure_python.core.id_gen.IDGenerator`
TComponentNo = int  # int >= 1
#   see `pyml_pure_python.core.id_gen.IDGenerator`
TLayerLevel = int  # int >= 0
TRepresents = ...

if __name__ == '__main__':
    from .components.base_component import BaseComponent
    from .core.uid_system import UID
    
    TComponentID = UID
    TComponent = BaseComponent
    TRepresents = Optional[TComponent]
