from typing import *
import PySide6.QtCore as _QtCore

TPropName: TypeAlias = str

TSender = Tuple[_QtCore.QObject, TPropName]
TReceptor = Tuple[_QtCore.QObject, TPropName]


class TQSideCore(NamedTuple):
    # `./qml/QSide.qml`
    eval_in_js: Callable
    connect_prop: Callable
