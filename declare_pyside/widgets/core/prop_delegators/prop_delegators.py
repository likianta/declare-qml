"""
README:
    docs/everything-about-prop-delegators.zh.md
"""
# noinspection PyUnresolvedReferences,PyProtectedMember
from typing import _UnionGenericAlias as RealUnionType

from PySide6.QtQml import QQmlProperty

from .typehint import *
from ....qmlside import qmlside

_REGISTERED_NAMES = (
    'qobj', 'name', 'prop', 'read', 'write', 'kiss', 'bind'
)


class PropDelegator:
    qobj: TQObject
    name: TPropName
    prop: TProperty
    
    def __init__(self, qobj: TQObject, name: TPropName):
        self.qobj = qobj
        self.name = name
        self.prop = QQmlProperty(qobj, name)
    
    def __getattr__(self, item):
        # notice: subclasses shouldn't override this method.
        if item.startswith('__') or item in _REGISTERED_NAMES:
            return super().__getattribute__(item)
        else:
            return super().__getattribute__('__get_subprop__')(item)
    
    def __setattr__(self, key, value):
        """
        Examples:
            xxx.name = 'xxx'
            xxx.??? = 'xxx'
        """
        if key.startswith('__') or key in _REGISTERED_NAMES:
            super().__setattr__(key, value)
        else:
            self.write(value)
    
    def __get_subprop__(self, name: TPropName):
        raise NotImplementedError
    
    def read(self):
        return self.prop.read()
    
    def write(self, value):
        self.prop.write(value)
    
    def kiss(self, value):
        self.write(value)
    
    def bind(self, abstract_prop_expression: tuple[TQObject, str]):
        """
        Documents:
            See `docs/black-magic-about-binding-mechanism.zh.md`

        Notes:
            Trying hard to complete dynamic binding feature. You cannot use
            this method for now.
            If you want to dynamically bind the others' properties, try the
            following instead:
                # WIP
                <item_A>.<prop>.bind(<item_B>.<prop>)
                # Workaround
                <item_B>.<prop_changed>.connect(
                    lambda: <item_A>.<prop> = <item_B>.<prop>
                )
        """
        # last_frame = currentframe().f_back
        # event, participants = self._extract_frame_info(last_frame)
        raise NotImplemented
    
    # @staticmethod
    # def _extract_frame_info(frame):
    #     """
    #     Learning:
    #         source code of lk-logger
    #
    #     TODO: much work (unittest & optimization) need to be done...
    #     """
    #     filename = frame.f_code.co_filename
    #     lineno = frame.f_lineno
    #     file = open(filename, 'r', encoding='utf-8')
    #     source_line = file.read().splitlines()[lineno - 1]
    #     file.close()
    #
    #     assert (m := re.match(r'^ +(?:\w+\.)+\.bind\(', source_line)), '''
    #         Your binding statement is too complex to analyse!
    #         In current verison (v0.1.x) we can only parse format likes
    #         `<some_qobj>.<property_name>.bind(<expression>)`.
    #         Here's the position error happened FYI:
    #             Filename: {}
    #             Lineno: {}
    #             Source Line: {}
    #     '''.format(filename, lineno, source_line)
    #     source_line_stem = source_line[m.span()[0]:]
    #
    #     from lk_logger.scanner import get_all_blocks
    #     from ...base_item import BaseItem  # FIXME: not a good way
    #
    #     segs = source_line_stem[1:].split(',')
    #     segs[-1] = segs[-1].rstrip(', ')
    #     event = ''
    #     participants = []
    #     locals_ = frame.f_locals()
    #     for match0 in get_all_blocks(source_line_stem):
    #         event = match0.fulltext.strip()
    #         break
    #     for match in get_all_blocks(*segs, end_mark=','):
    #         obj_name, prop_name, *_ = match.fulltext.split('.')
    #         #   e.g. 'btn.x' -> 'btn'
    #         if obj_name in locals_:
    #             obj = locals_[obj_name]
    #             if isinstance(obj, BaseItem) and prop_name in obj.auth_props:
    #                 participants.append(QQmlProperty(obj.qobj, prop_name))
    #
    #     return event, participants


class PropDelegatorA(PropDelegator):
    
    def __get_subprop__(self, name):
        raise AttributeError(
            'This property ({}) doesn\'t support to access a secondary '
            'property from it.'.format(self.name), 
            'Did you mean `PropDelegatorB` or `PropDelegatorC`?', name
        )


class PropDelegatorB(PropDelegator):
    
    def __get_subprop__(self, name) -> PropDelegatorA:
        return PropDelegatorA(self.prop.read(), name)
        # return QQmlProperty(self.prop.read(), name)
        #                   ^^^^^^^^^^^^^^^^ QObject


class PropDelegatorC(PropDelegator):
    sub_name: TPropName
    
    def __getattribute__(self, item):
        if item == 'sub_name':
            return object.__getattribute__(self, item)
        else:
            return super().__getattr__(item)
    
    def __get_subprop__(self, name):
        return self
    
    class PropBroker:
        
        def __init__(self, qobj: TQObject, prop_name: str):
            self.qobj = qobj
            # self.prop_name = prop_name or QQmlProperty(self.qobj).name()
            self.prop_name = prop_name
            
        def __setattr__(self, key: TPropName, value: 'PropDelegatorC.PropBroker'):
            t_obj = self.qobj
            t_prop_name = key
            s_obj = value.qobj
            s_prop_name = value.prop_name
            assert s_prop_name is not None
            qmlside.bind_prop(t_obj, t_prop_name, s_obj, s_prop_name)
    
    def __getattr__(self, item) -> Union[Any, tuple[TQObject, TPropName]]:
        if item == _REGISTERED_NAMES:
            return super().__getattribute__(_REGISTERED_NAMES)
        if item in self._self_registered_attribute_names:
            return super().__getattr__(item)
        else:  # e.g. <anchors>.top
            # # return QQmlProperty(self.prop.read(), item)
            return PropDelegatorC.PropBroker(self.prop.read(), item)
            # return self.prop.read(), item
    
    def __setattr__(self, key, value):
        # if key in dir(self):
        if key.startswith('__') or key in ('qobj', 'name', 'prop'):
            super().__setattr__(key, value)
        else:
            self.write(value)
    
    def write(self, value: tuple[TQObject, TPropName]):
        qmlside.bind_prop(self.prop.read(), self.name, *value)
        
        
def adapt_delegator(qobj: TQObject, name: TPropName,
                    constructor: TConstructor) -> TDelegator:
    if type(constructor) is RealUnionType:
        delegator = constructor.__args__[-1]
        #   e.g. Union[float, PropDelegatorA] -> PropDelegatorA
        #   we had agreement that always put `type:TDelegator` in the last
        #   position of `TConstructor`. see reason at [TODO] and some
        #   implementation code at `..authorized_props.ItemProps`.
    else:
        # noinspection PyTypeChecker
        assert issubclass(constructor, PropDelegator)
        delegator = constructor
    return delegator(qobj, name)
