from secrets import token_hex

from PySide6.QtQml import QQmlProperty

from ...black_magic import gstates
from ...typehint.qmlside import *

""" what-is-prime-delegators-and-subprime-delegators.zh.md

`PrimePropDelegator` 用于代理 qml 中结构较为简单的属性. 例如: width, height, x,
y 等; `SubprimePropDelegator` 用于代理具有次级属性的 qml 属性, 例如 anchors
(anchors.fill, anchors.centerIn, anchors.top, etc.), font (font.pixelSize, font
.family, etc.).
"""


class AbstractDelegatorExpression:
    qobj: TQObject
    expression: str
    
    def __init__(self, qobj):
        self.qobj = qobj
        self.expression = ''
        
    def __add__(self, other):
        expression, qobj = other
        
    def _randomize_placeholders(self, expression: str):
        def _gen_random_slot_name():
            return 'x' + token_hex(8)
    
    def update(self, value: str):
        self.expression += value
        return self.expression


class Delegator:
    
    def __init__(self, qobj: TQObject, name: TPropName):
        self.qobj = qobj
        self.name = name
        self.prop = QQmlProperty(qobj, name)
    
    def __getattr__(self, item):
        if item == 'bind':
            if self.prop.hasNotifySignal():
                gstates.is_binding = True
            else:
                raise Exception(
                    'Property not bindable!',
                    self.qobj, self.name, self.prop.read()
                )
        return super().__getattribute__(item)
    
    def __add__(self, other):
        if gstates.is_binding:
            if isinstance(other, AbstractDelegatorExpression):
                return other.update(' + ')
        
    def bind(self, abstract_prop_expression: tuple[TQObject, str]):
        pass
    
    def kiss(self, value):
        pass
        
    


class PrimePropDelegator(Delegator):
    
    def __getattr__(self, item):
        if item == 'bind':
            if self.prop.hasNotifySignal():
                gstates.is_binding = True
            else:
                raise Exception('Property not bindable!',
                                self.name, self.prop.read())
        return super().__getattribute__(item)
    
    def read(self):
        if gstates.is_binding:
            return self.prop
        return self.prop.read()
    
    def write(self, value):
        self.prop.write(value)
    
    def bind(self, prop: QQmlProperty, func=None):
        assert gstates.is_binding
        
        
        
        x = QQmlProperty()
        x.connectNotifySignal()
        
        gstates.is_binding = False
    
    def kiss(self, value):
        # TODO: check whether `value` type immutable
        self.prop.write(value)


class SubprimePropDelegator(Delegator):
    pass
