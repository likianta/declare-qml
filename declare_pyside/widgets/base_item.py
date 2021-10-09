from PySide6.QtQml import QQmlComponent

from declare_foundation.context_manager import Context
from .core.authorized_props import AuthorizedProps
from .core.authorized_props import QPROPS
from .core.prop_delegators import PropDelegator
from .core.prop_delegators import adapt_delegator
from ..pyside import app
from ..qmlside import qmlside
from ..typehint.qmlside import *


class BaseItem(Context, AuthorizedProps):
    component: TComponent
    parent: Optional['BaseItem']
    qmlfile: TQmlFile
    qobj: TQObject
    
    def __init__(self):
        Context.__init__(self)
        AuthorizedProps.__init__(self)
        self.component = QQmlComponent(app.engine, self.qmlfile)
    
    def __enter__(self):
        super().__enter__()
        self.qobj = self.create_object()
        return self
    
    def __getprop__(self, name: TPropName):
        type_ = self._qprops[name]
        prop_delegator = adapt_delegator(self.qobj, name, type_)
        return prop_delegator
    
    def __setattr__(self, key, value):
        if key == QPROPS:
            super().__setattr__(key, value)
            return
        
        if key in self._qprops:
            # A
            # self.qobj.setProperty(key, value)
            
            # B
            # prop = QQmlProperty(self.qobj, key)
            # prop.write(value)
            
            # C
            type_ = self._qprops[key]
            prop_delegator = adapt_delegator(self.qobj, key, type_)
            if isinstance(value, PropDelegator):
                prop_delegator.write(value.read())
            else:
                prop_delegator.write(value)
        else:
            super().__setattr__(key, value)
    
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
