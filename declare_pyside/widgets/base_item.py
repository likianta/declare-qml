from PySide6.QtQml import QQmlComponent
from PySide6.QtQml import QQmlProperty

from declare_foundation.context_manager import Context
from .core.authorized_props import AuthorizedProps
from .core.delegators import Delegator
from ..pyside import app
from ..qmlside import qmlside
from ..typehint.qmlside import *
from ..typehint.widgets_support import *


class BaseItem(Context):
    auth_props: TAuthProps
    component: TComponent
    parent: 'BaseItem'
    qmlfile: TQmlFile
    qobj: TQObject
    
    def __init__(self):
        super().__init__()
        self._init_authorized_props()
        self.component = QQmlComponent(app.engine, self.qmlfile)
    
    def _init_authorized_props(self):
        """
        References:
            https://stackoverflow.com/questions/2611892/how-to-get-the-parents
                -of-a-python-class
        """
        # trick: search `self.__class__.__bases__` from end to start. this is a
        #   little faster to find the target baseclass because usually we like
        #   putting `class:AuthorizedProps` in the end of `self.__class__
        #   .__bases__`.
        for cls in reversed(self.__class__.__bases__):
            # lk.logt('[D5835]', cls.__name__)
            if issubclass(cls, AuthorizedProps):
                self.auth_props = cls.get_authorized_props()
                return
        else:
            if (classname := self.__class__.__name__) != 'BaseItem':
                raise Exception('Widget doesn\'t inherit `class:AuthProps`',
                                classname)
    
    def __enter__(self):
        super().__enter__()
        self.qobj = self.create_object()
        return self
    
    def __setattr__(self, key, value):
        if key == 'auth_props':
            super().__setattr__(key, value)
            return
        
        if key in self.auth_props:
            prop = QQmlProperty(self.qobj, key)
            prop.write(value)
            # self.qobj.setProperty(key, value)
        else:
            super().__setattr__(key, value)
    
    def __getattr__(self, item):
        if item == 'auth_props':
            return getattr(super(), 'auth_props', ())
        
        if item in self.auth_props:
            prop = QQmlProperty(self.qobj, item)
            return prop.read()
            # return self.qobj.property(item)
        else:
            # https://stackoverflow.com/questions/3278077/difference-between
            #   -getattr-vs-getattribute
            # return self.__dict__[item]
            return super().__getattribute__(item)
    
    def create_object(self) -> TQObject:
        """
        
        TODO:
            `self.component` (the instance of QQmlComponent) doesn't provide a
            function that can directly create a QObject within defined parent.
            It means, by `qobj = self.component.create(...)` that the `qobj`
            won't be shown in GUI -- we've tried many things to make it work --
            but for now it still totally invalid.
            So we have to create `qobj` by `qmside.create_qobject`. The key
            method is `QML:Component.createObject` (`QML:Component` inherits
            from `PySide6.QtQml.QQmlComponent`, see [link#1][1] and
            [link#2][2]).
                [1]: https://doc.qt.io/qt-5/qqmlcomponent.html
                [2]: https://doc.qt.io/qt-5/qml-qtqml-component.html
                
            Backup Works:
                ctx = app.engine.contextForObject(self.parent.qobj)
                qobj = self.component.create(ctx)
                qobj.setParent(self.parent.qobj)
                return qobj
        """
        qobj = qmlside.create_qobject(self.component, self.parent.qobj)
        return qobj
