from typing import Callable
from typing import Literal

TArg0 = Literal['', 'self', 'cls']
TNArgs = int  # nargs: 'number of args', int == -1 or >= 0. -1 means uncertain.

_TPyClassName = str
_TPyFuncName = str
_TPyMethName = str
_TRegisteredName = str  # usually this name is same with _TPyFuncName or
#   _TPyMethName, but you can define it with a custom name (something likes
#   alias).

TPyClassHolder = dict[
    _TPyClassName, dict[
        _TPyMethName, tuple[_TRegisteredName, TNArgs]
    ]
]

_TPyFunction = Callable
TPyFuncHolder = dict[_TRegisteredName, tuple[_TPyFunction, TNArgs]]
