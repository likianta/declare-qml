from os import PathLike as _PathLike
from typing import *

from PySide6.QtCore import QObject as _QObject
from PySide6.QtQml import QQmlComponent as _QQmlComponent
from PySide6.QtQml import QQmlProperty as _QQmlProperty
from PySide6.QtQuick import QQuickItem as _QQuickItem

TComponent = _QQmlComponent
TQObject = Union[_QObject, _QQuickItem]
TProperty = _QQmlProperty
TPropName: TypeAlias = str

TSender = tuple[TQObject, TPropName]
TReceptor = tuple[TQObject, TPropName]

TQmlFile = Union[_PathLike, str]
TComponentCache = dict[TQmlFile, TComponent]


class TQSideCore:
    # `declare_pyside/qmlside/LKQmlSide/QmlSide.qml`
    
    @staticmethod
    def bind(t_obj: TQObject, s_obj: TQObject, expression: str): pass
    
    @staticmethod
    def connect_prop(*_, **__) -> Any: pass
    
    @staticmethod
    def create_component(_: str) -> TComponent: pass
    
    @staticmethod
    def create_object(component: TComponent, container: TQObject) -> TQObject: pass
    
    @staticmethod
    def eval_js(code: str, locals_: list[TQObject]): pass
