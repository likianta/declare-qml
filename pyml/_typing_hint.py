from typing import *

from .components.base_component import BaseComponent as TComponent

TComponentID = str  # e.g. 'com_0x1_01_01_01'.
#   see `pyml_pure_python.core.id_gen.IDGenerator`
TComponentNo = int  # int >= 1
#   see `pyml_pure_python.core.id_gen.IDGenerator`
TLayerLevel = int  # int >= 0
TRepresents = Optional[TComponent]
