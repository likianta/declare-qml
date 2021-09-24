from textwrap import dedent
from textwrap import indent

from declare_foundation.components import BaseComponent as OriginBaseComponent
from ..properties import PropertyManager
from ..properties.manager import adapt_key
from ..properties.manager import adapt_value
from ..typehint import *


class BaseComponent(OriginBaseComponent, PropertyManager):
    children: List['BaseComponent']
    name: str
    
    _initialized = False
    _propagating = False
    
    def __init__(self):
        OriginBaseComponent.__init__(self)
        PropertyManager.__init__(self)
        
        self._propagations = set()
        
        # self._init_raw_props()
        # self._init_custom_props()
        
        self._initialized = True
    
    def build(self) -> TComponent:
        pass
    
    def finalize(self, offset=0) -> str:
        """ Convert data structure into qml code. """
        # declare custom properties
        holder1 = []
        for k, v in self.new_props.items():
            k = adapt_key(k)
            v = adapt_value(v)
            # type_ = {
            #     bool: 'bool',
            #     str: 'string',
            #     int: 'int',
            #     float: 'real',
            #     'alias': 'alias',
            # }.get(type(v), 'var')
            holder1.append(f'property {v.qtype} {k}: {v}')
        
        # properties
        holder2 = []
        for k, v in self.raw_props.items():
            k = adapt_key(k)
            v = adapt_value(v)
            holder2.append(f'{k}: {v}')
        
        qml_code = dedent('''
            {component} {{
                id: {id}
                objectName: "{object_name}"
                
                // CUSTOM PROPERTIES
                {custom_properties}
                
                // PROPERTIES
                {properties}
                
                // CHILDREN
                {children}
            }}
        ''').strip().format(
            component=self.name,
            id=self.uid,
            object_name=self.name.lower() + str(self.uid)[3:],
            #   e.g. 'window_0x1_01'
            custom_properties='\n    '.join(holder1) or '// -- NO PROPS --',
            properties='\n    '.join(holder2) or '// -- NO PROPS --',
            children='\n\n    '.join(
                x.finalize(4).lstrip() for x in self.children
            ) if self.children else '// -- NO CHILD --',
        )
        
        return indent(qml_code, ' ' * offset)

    # def _init_raw_props(self):
    #     raise NotImplementedError
    #
    # def _init_custom_props(self):
    #     pass

    # def __getattr__(self, item):
    #     if (
    #             isinstance(item, str) and
    #             item.startswith('on_') and
    #             item.endswith('_changed')
    #     ):
    #         return self.__dict__.get(item, lambda v: v)
    #     else:
    #         return self.__dict__[item]

    # def __setattr__(self, key, value, propagate=True):
    #     # https://www.cnblogs.com/hester/articles/4767152.html
    #     # noinspection PyProtectedMember
    #     from sys import _getframe
    #     caller_name = _getframe(1).f_code.co_name  # type: str
    #
    #     if self._initialized:
    #         ''' 如何避免无限回调?
    #         1. self._propagations 维护一个传播链
    #         2. 当 on_prop_changed 的 prop 第一次触发时, 由于该 prop 不在传播链
    #            上, 所以正常触发
    #            1. 此时 self._propagations 记录该 prop
    #         3. 当 prop 因为某种联动机制再次到来时, 由于不是第一次触发,
    #            self._propagations 有记录, 所以不予触发, 直接返回
    #         4. 什么时候清空传播链? 当外部调用者触发时 (由下面的语句判断是否为外
    #            部调用者), 将传播链清零, 并重复步骤 2 的过程
    #         '''
    #         if (
    #                 caller_name.startswith('on_') and
    #                 caller_name.endswith('_changed')
    #         ):  # the caller is from inner method, so we prevent it if not the
    #             # first time triggered follows step 3
    #             if key in self._propagations:
    #                 return
    #             # else it it the first time occurred, we pass through it follows
    #             # step 2
    #         else:
    #             # else the caller is from outside, so we clear the propagation
    #             # chain and pass through it follows step 2
    #             self._propagations.clear()
    #         self._propagations.add(key)
    #
    #     super().__setattr__(key, value)
    #
    #     if self._initialized is False:
    #         if caller_name == '_init_raw_props':
    #             self._props['raw_props'].append(key)
    #         elif caller_name == '_init_custom_props':
    #             self._props['custom_props'].append(key)
    #     else:
    #         getattr(self, f'on_{key}_changed', lambda v: v)(value)

    # def __enter__(self):
    #     """
    #     with Component() as com:
    #         #   1. update `this` indicates to `com`
    #         #   2. update `context` surrounds `com`
    #         ...
    #     """
    #     # 此时的 this 代表的是上个组件 (上个组件指的可能是父组件, 兄弟组件或兄弟
    #     # 组件的子孙组件)
    #     last_com = this.represents
    #     context.update(self.uid, self.level, self, last_com)
    #     # 经过 context 更新后, this 和 parent 的指向都正常了
    #     return self
    #
    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     this.point_to(id_ref[(pid := self.uid.parent_id)])
    #     parent.point_to(id_ref[pid.parent_id] if pid is not None else None)
