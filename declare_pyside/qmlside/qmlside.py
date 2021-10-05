from textwrap import dedent

from PySide6.QtCore import QObject

from ..typehint.qmlside_pkg import *


def setup():
    def register_qmlside(obj):
        global qmlside
        qmlside.init(obj)
    
    from ..pyside import pyside
    pyside.register(register_qmlside)


class QmlSide(QObject):
    _core: TQSideCore
    
    def init(self, qobj):
        self._core = qobj
    
    def connect_prop(self, r: TReceptor, s: TSender):
        pass
    
    def connect_func(self, r: TReceptor, func: Callable,
                     s_group: Iterable[TSender]):
        args = [r[0], [s[0] for s in s_group]]
        self._core.eval_in_js(
            dedent('''
                {r_obj}.{r_prop} = Qt.binding(
                    () => PySide.call({func_id}, {s_group})
                )
            ''').format(
                r_obj='args[0]',
                r_prop=r[1],
                func_id='',
                s_group=[
                    f'args[{i}].{prop}'
                    for i, (_, prop) in enumerate(s_group, 1)
                ]
            ),
            args,
        )


qmlside = QmlSide()
