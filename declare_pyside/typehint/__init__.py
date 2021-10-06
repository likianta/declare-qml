from os import PathLike as _PathLike
from typing import *

from . import pyside
from . import qmlside

TPath = Union[_PathLike, str, bytes]
