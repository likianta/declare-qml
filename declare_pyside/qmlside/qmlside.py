from secrets import token_hex
from textwrap import dedent

from PySide6.QtCore import QObject
from PySide6.QtQml import QQmlComponent
from lk_logger import lk

from .. import path_model
from ..pyside import app
from ..pyside import pyside
from ..typehint.qmlside import *


def setup():
    def register_qmlside(obj: TQObject):
        global qmlside
        qmlside.init_core(obj)
        lk.logt('[I0557]', 'registered qmlside object', obj.objectName())
    
    from ..pyside import pyside
    pyside.register(register_qmlside, '__register_qmlside_object')
    #   see `declare_pyside/qmlside/LKQmlSide/QmlSide.qml:Component.onCompleted`


class QmlSide(QObject):
    qmlfile = path_model.lk_qml_side_dir + '/QmlSide.qml'
    _core: TQSideCore
    _component_cache = {}  # type: TComponentCache
    
    def init_core(self, qobj):
        self._core = qobj
    
    def bind(self, target, participants, expression):
        pass
    
    def bind_prop(self,
                  t_obj: TQObject, t_prop_name: TPropName,
                  s_obj: TQObject, s_prop_name: TPropName):
        expression = '{} = Qt.binding(() => {})'.format(
            f't_obj.{convert_name_case(t_prop_name)}',
            f's_obj.{convert_name_case(s_prop_name)}'.rstrip('.'),
        )
        lk.loga(expression)
        self._core.bind(t_obj, s_obj, expression)
    
    def connect_prop(self, r: TReceptor, s: TSender):
        pass
    
    def connect_func(self, r: TReceptor, func: Callable,
                     s_group: Iterable[TSender]):
        
        func_id = func.__name__ + '_' + token_hex(8)
        pyside.register(func, func_id)
        
        args = [r[0], [s[0] for s in s_group]]
        
        self._core.eval_js(
            dedent('''
                {r_obj}.{r_prop} = Qt.binding(
                    () => PySide.call({func_id}, {s_group})
                )
            ''').format(
                r_obj='args[0]',
                r_prop=r[1],
                func_id=func_id,
                s_group=[
                    f'args[{i}].{prop}'
                    for i, (_, prop) in enumerate(s_group, 1)
                ]
            ),
            args,
        )
    
    def create_component(
            self, qmlfile: TQmlFile, save_cache=False
    ) -> TComponent:
        if qmlfile in self._component_cache:
            return self._component_cache[qmlfile]
        else:
            comp = QQmlComponent(app.engine, qmlfile)
            if save_cache:
                self._component_cache[qmlfile] = comp
            return comp
    
    def create_qobject(self,
                       component: TComponent,
                       container: TQObject) -> TQObject:
        qobj = self._core.create_object(component, container)
        #   the component type is TComponent, but when `self._core
        #   .create_object` -- which is defined in `declare_pyside/qmlside
        #   /LKQmlSide/QmlSide.qml:<function:create_object>` -- is called,
        #   TComponent will be implicitly translated to `QML:Component` type.
        return qobj


def convert_name_case(snake_case: str):
    if '_' in snake_case:
        segs = snake_case.split('_')
        camel_case = segs[0] + ''.join(x.title() for x in segs[1:])
    else:
        camel_case = snake_case
    return camel_case


qmlside = QmlSide()
