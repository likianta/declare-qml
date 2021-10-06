from PySide6.QtQml import QQmlComponent
from lk_logger import lk

from declare_foundation.context_manager import Context
from ..pyside import app
from ..qmlside import qmlside
from ..typehint.qmlside import *


class BaseItem(Context):
    parent: 'BaseItem'
    qmlfile: TQmlFile
    
    component: TComponent
    qobj: TQObject
    
    def __init__(self):
        super().__init__()
        self.component = QQmlComponent(app.engine, self.qmlfile)
        lk.logt('[D5904]', self.component)
    
    def __enter__(self):
        super().__enter__()
        
        self.qobj = self.create_object()
        lk.logt('[D0131]', self.qobj)
        
        # from ..qmlside import qmlside
        # txt1 = qmlside._core.createObject(self.component, self.parent.qobj)
        # lk.loga(txt1)
        # lk.logp(txt1.property('text'),
        #         txt1.property('width'),
        #         txt1.property('height'),
        #         txt1.parent())
        # txt1.setProperty('text', 'Hello World (TxT1)')
        
        lk.loga(self.qobj.property('text'))
        self.qobj.setProperty('text', 'hello')
        lk.loga(self.qobj.property('text'))
        lk.loga(self.parent)
        lk.loga(self.qobj.parent())
        lk.loga(self.qobj.parent().objectName())
        return self
    
    # def __setattr__(self, key, value):
    #     pass
    
    # def __getattr__(self, item):
    #     if item in self.__dict__:
    #         return self.__dict__[item]
    #     else:
    #         return self.qobj.property(item)
    
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
