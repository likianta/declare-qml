from os import PathLike as _PathLike
from typing import *

from . import pyside_pkg
from . import qmlside_pkg

TPath = Union[_PathLike, str, bytes]
