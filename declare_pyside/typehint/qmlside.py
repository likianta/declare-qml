from os import PathLike as _PathLike
from typing import *

from PySide6.QtCore import QObject as _QObject
from PySide6.QtQml import QQmlComponent as _QQmlComponent
from PySide6.QtQuick import QQuickItem as _QQuickItem

TComponent = _QQmlComponent
TQObject = Union[_QObject, _QQuickItem]
# TQItem = _QQuickItem

TPropName: TypeAlias = str

TSender = tuple[TQObject, TPropName]
TReceptor = tuple[TQObject, TPropName]

TQmlFile = Union[_PathLike, str]
TComponentCache = dict[TQmlFile, TComponent]


def _eval_js(_: str, __: list[TQObject]): pass


def _create_component(_: str) -> 'TComponent': pass


def _create_object(_: TComponent, __: TQObject) -> TQObject:
    """ (component, container) """


def _somefunc(*_, **__) -> Any: pass


class TQSideCore:
    # `./qml/QSide.qml`
    evalJs = _eval_js
    connectProp = _somefunc
    createComponent = _create_component
    createObject = _create_object
