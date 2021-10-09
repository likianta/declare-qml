from PySide6.QtCore import QObject
from PySide6.QtGui import QFont
from PySide6.QtQuick import QQuickItem

from .prop_delegators import *
from ...typehint.widgets_support import *

QPROPS = '_qprops'


class AuthorizedProps:
    """
    Notes.zh-CN:
        所有继承本类的子类, 如果该子类属于 Mixin 类型, 则必须将本类放在第一继承
        位置. 否则将导致 [MARK][1] 发生异常, 进而导致 [MARK][2] 引发断言错误.
        
    Notes:
        All subclasses that inherit from this class, if the subclass is a Mixin
        type, it must place AuthorizedProps in its first Mixin position.
        Otherwise [MARK][1] will match a wrong baseclass, then [MARK][2] will
        raise an AssertionError.
        
        [1]: `<child_class>.<classmethod:get_authorized_props>.<while_loop>
             .<var:temp_cls>.<code:'temp_cls = temp_cls.__base__'>`
        [2]: `<child_class>.<classmethod:get_authorized_props>.<while_loop>
             .<code:assert>`
    """
    # this is a special attribute that its name must be prefixed with
    # underscore. otherwise it will puzzle `<globals>._get_authorized_props
    # .<code:'if not k.startswith('_')'>`.
    _qprops: TAuthProps
    
    def __init__(self):
        self._init_authorized_props()
    
    def _init_authorized_props(self):
        """
        References:
            https://stackoverflow.com/questions/2611892/how-to-get-the-parents
                -of-a-python-class
        """
        if self.__class__ is AuthorizedProps:
            raise Exception('This method should be used in subclasses of '
                            '`AuthorizedProps`!')
        # trick: search `self.__class__.__bases__` by reversed sequence. this
        #   can be a little faster to find the target baseclass because usually
        #   we like putting `class:AuthorizedProps` in the end of `self
        #   .__class__.__bases__`.
        for cls in reversed(self.__class__.__bases__):
            # lk.logt('[D5835]', cls.__name__)
            if issubclass(cls, AuthorizedProps):
                self._qprops = cls._get_authorized_props()
                return
    
    @classmethod
    def _get_authorized_props(cls) -> TAuthProps:
        out = {}
        tmp_cls = cls
        # # while tmp_cls is not AuthorizedProps:
        # #     assert issubclass(tmp_cls, AuthorizedProps)
        while issubclass(tmp_cls, AuthorizedProps):  # two steps in one
            out.update(_get_authorized_props(tmp_cls))
            tmp_cls = tmp_cls.__base__
        return out
    
    def __getattr__(self, item):
        if item == QPROPS:
            return getattr(super(), QPROPS, ())
        
        # https://stackoverflow.com/questions/3278077/difference-between-getattr
        # -vs-getattribute
        if item in self._qprops:
            return super().__getattribute__('__getprop__')(item)
        else:
            return super().__getattribute__(item)
    
    def __getprop__(self, name):
        # see typical implementation at `..base_item.BaseItem.__getprop__`.
        raise NotImplemented


def _get_authorized_props(cls) -> Iterable[tuple[TPropName, TConstructor]]:
    for k, v in cls.__annotations__.items():
        if not k.startswith('_'):
            yield k, v


# ------------------------------------------------------------------------------
# TODO: the following can be generated from blueprint

class AnchorsProps(AuthorizedProps):
    fill: Union[str, PrimitivePropDelegator]
    center: Union[str, PrimitivePropDelegator]
    center_in: Union[str, PrimitivePropDelegator]
    
    left: Union[str, PrimitivePropDelegator]
    right: Union[str, PrimitivePropDelegator]
    top: Union[str, PrimitivePropDelegator]
    bottom: Union[str, PrimitivePropDelegator]
    
    margins_left: Union[str, PrimitivePropDelegator]
    margins_right: Union[str, PrimitivePropDelegator]
    margins_top: Union[str, PrimitivePropDelegator]
    margins_bottom: Union[str, PrimitivePropDelegator]


class ItemProps(AuthorizedProps):
    anchors: Union[AnchorsProps, PropDelegatorC]
    height: Union[float, PropDelegatorA]
    width: Union[float, PropDelegatorA]
    x: Union[float, PropDelegatorA]
    y: Union[float, PropDelegatorA]
    z: Union[float, PropDelegatorA]


# ------------------------------------------------------------------------------

class ButtonProps(ItemProps):
    text: Union[str, PropDelegatorA]
    background: Union[object, PropDelegatorA]


class MouseAreaProps(ItemProps):
    drag: Union[object, PropDelegatorB]


class RectangleProps(ItemProps):
    background: Union[QQuickItem, PropDelegatorA]
    border: Union[QObject, PropDelegatorB]
    color: Union[str, PropDelegatorA]


class TextProps(ItemProps):
    font: Union[QFont, PropDelegatorA]
    text: Union[str, PropDelegatorA]


class WindowProps(ItemProps):
    color: Union[str, PropDelegatorA]
    visible: Union[bool, PropDelegatorA]
